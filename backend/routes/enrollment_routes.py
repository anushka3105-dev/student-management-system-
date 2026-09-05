from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from auth import require_role, get_current_user
from models.schemas import EnrollmentRequest

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])


@router.post("", status_code=201)
def enroll_student(
    payload: EnrollmentRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "student")),
):
    """
    Calls the sp_enroll_student stored procedure, which runs the capacity
    check and INSERT inside a single transaction on the database side.
    """
    if current_user["role"] == "student":
        owner_check = db.execute(
            text("SELECT student_id FROM students WHERE user_id = :uid"),
            {"uid": current_user["user_id"]},
        ).first()
        if not owner_check or owner_check[0] != payload.student_id:
            raise HTTPException(status_code=403, detail="Cannot enroll on behalf of another student")

    raw_conn = db.connection().connection
    cursor = raw_conn.cursor()
    try:
        cursor.callproc("sp_enroll_student", (payload.student_id, payload.offering_id, 0))
        cursor.execute("SELECT @_sp_enroll_student_2")
        status_msg = cursor.fetchone()[0]
        raw_conn.commit()
    finally:
        cursor.close()

    if status_msg and status_msg.startswith("ERROR"):
        raise HTTPException(status_code=400, detail=status_msg)
    return {"message": status_msg or "Enrolled"}


@router.get("")
def list_enrollments(
    student_id: int | None = None,
    offering_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "faculty", "student")),
):
    query = """
        SELECT e.enrollment_id, e.student_id, e.offering_id, e.status, e.enrollment_date,
               c.course_code, c.course_name
        FROM enrollments e
        JOIN course_offerings co ON co.offering_id = e.offering_id
        JOIN courses c ON c.course_id = co.course_id
        WHERE 1=1
    """
    params = {}
    if student_id:
        query += " AND e.student_id = :student_id"
        params["student_id"] = student_id
    if offering_id:
        query += " AND e.offering_id = :offering_id"
        params["offering_id"] = offering_id

    rows = db.execute(text(query), params).mappings().all()
    return [dict(r) for r in rows]


@router.delete("/{enrollment_id}")
def drop_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "student")),
):
    result = db.execute(
        text("UPDATE enrollments SET status = 'dropped' WHERE enrollment_id = :eid"),
        {"eid": enrollment_id},
    )
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return {"message": "Enrollment dropped"}

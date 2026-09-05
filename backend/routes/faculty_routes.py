from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from auth import require_role, hash_password
from models.schemas import FacultyCreate, FacultyOut

router = APIRouter(prefix="/faculty", tags=["Faculty"])


@router.get("", response_model=list[FacultyOut])
def list_faculty(
    department_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "faculty", "student")),
):
    query = "SELECT faculty_id, employee_code, first_name, last_name, designation, department_id FROM faculty WHERE 1=1"
    params = {}
    if department_id:
        query += " AND department_id = :department_id"
        params["department_id"] = department_id
    rows = db.execute(text(query), params).mappings().all()
    return [dict(r) for r in rows]


@router.get("/workload")
def faculty_workload(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin")),
):
    rows = db.execute(text("SELECT * FROM vw_faculty_workload")).mappings().all()
    return [dict(r) for r in rows]


@router.post("", status_code=201)
def create_faculty(
    payload: FacultyCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin")),
):
    existing = db.execute(
        text("SELECT user_id FROM users WHERE username = :u OR email = :e"),
        {"u": payload.username, "e": payload.email},
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Username or email already exists")

    try:
        result = db.execute(
            text(
                "INSERT INTO users (username, email, password_hash, role) "
                "VALUES (:username, :email, :password_hash, 'faculty')"
            ),
            {
                "username": payload.username,
                "email": payload.email,
                "password_hash": hash_password(payload.password),
            },
        )
        user_id = result.lastrowid

        db.execute(
            text(
                """
                INSERT INTO faculty
                    (user_id, department_id, employee_code, first_name, last_name,
                     designation, qualification, phone, date_of_joining, salary)
                VALUES
                    (:user_id, :department_id, :employee_code, :first_name, :last_name,
                     :designation, :qualification, :phone, :date_of_joining, :salary)
                """
            ),
            {"user_id": user_id, **payload.model_dump(exclude={"username", "email", "password"})},
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Could not create faculty member: {exc}")

    return {"message": "Faculty member created", "user_id": user_id}


@router.get("/{faculty_id}/offerings")
def faculty_offerings(
    faculty_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "faculty")),
):
    rows = db.execute(
        text("SELECT * FROM vw_course_offering_summary WHERE offering_id IN "
             "(SELECT offering_id FROM course_offerings WHERE faculty_id = :fid)"),
        {"fid": faculty_id},
    ).mappings().all()
    return [dict(r) for r in rows]

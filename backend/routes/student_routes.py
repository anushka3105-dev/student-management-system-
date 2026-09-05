from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from auth import require_role, get_current_user, hash_password
from models.schemas import StudentCreate, StudentUpdate, StudentOut

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("", response_model=list[StudentOut])
def list_students(
    status_filter: str | None = None,
    program_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "faculty")),
):
    query = "SELECT * FROM vw_student_directory WHERE 1=1"
    params = {}
    if status_filter:
        query += " AND status = :status_filter"
        params["status_filter"] = status_filter
    if program_id:
        query += " AND program_name IN (SELECT program_name FROM programs WHERE program_id = :program_id)"
        params["program_id"] = program_id
    query += " ORDER BY full_name"

    rows = db.execute(text(query), params).mappings().all()
    return [dict(r) for r in rows]


@router.get("/{student_id}", response_model=StudentOut)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Students may only view their own record; admin/faculty can view any.
    if current_user["role"] == "student":
        owner_check = db.execute(
            text("SELECT student_id FROM students WHERE user_id = :uid"),
            {"uid": current_user["user_id"]},
        ).first()
        if not owner_check or owner_check[0] != student_id:
            raise HTTPException(status_code=403, detail="Cannot view another student's record")

    row = db.execute(
        text("SELECT * FROM vw_student_directory WHERE student_id = :sid"),
        {"sid": student_id},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Student not found")
    return dict(row)


@router.post("", status_code=201)
def create_student(
    payload: StudentCreate,
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
                "VALUES (:username, :email, :password_hash, 'student')"
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
                INSERT INTO students
                    (user_id, program_id, enrollment_number, first_name, last_name,
                     date_of_birth, gender, phone, address, admission_year,
                     guardian_name, guardian_phone)
                VALUES
                    (:user_id, :program_id, :enrollment_number, :first_name, :last_name,
                     :date_of_birth, :gender, :phone, :address, :admission_year,
                     :guardian_name, :guardian_phone)
                """
            ),
            {"user_id": user_id, **payload.model_dump(exclude={"username", "email", "password"})},
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Could not create student: {exc}")

    return {"message": "Student created", "user_id": user_id}


@router.patch("/{student_id}")
def update_student(
    student_id: int,
    payload: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "faculty")),
):
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    set_clause = ", ".join(f"{col} = :{col}" for col in updates)
    updates["student_id"] = student_id

    result = db.execute(
        text(f"UPDATE students SET {set_clause} WHERE student_id = :student_id"),
        updates,
    )
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student updated"}


@router.get("/{student_id}/attendance")
def student_attendance(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    rows = db.execute(
        text(
            """
            SELECT vp.offering_id, c.course_code, c.course_name,
                   vp.total_sessions, vp.sessions_attended, vp.attendance_percentage
            FROM vw_student_attendance_pct vp
            JOIN course_offerings co ON co.offering_id = vp.offering_id
            JOIN courses c ON c.course_id = co.course_id
            WHERE vp.student_id = :sid
            """
        ),
        {"sid": student_id},
    ).mappings().all()
    return [dict(r) for r in rows]


@router.get("/{student_id}/results")
def student_results(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    rows = db.execute(
        text(
            """
            SELECT er.result_id, c.course_code, c.course_name, e.exam_name,
                   e.exam_type, er.marks_obtained, e.max_marks, er.grade
            FROM exam_results er
            JOIN exams e ON e.exam_id = er.exam_id
            JOIN course_offerings co ON co.offering_id = e.offering_id
            JOIN courses c ON c.course_id = co.course_id
            WHERE er.student_id = :sid
            ORDER BY e.exam_date DESC
            """
        ),
        {"sid": student_id},
    ).mappings().all()
    return [dict(r) for r in rows]

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from auth import require_role
from models.schemas import CourseCreate, CourseOut, OfferingCreate, OfferingOut

router = APIRouter(tags=["Courses"])


@router.get("/courses", response_model=list[CourseOut])
def list_courses(
    department_id: int | None = None,
    semester: int | None = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "faculty", "student")),
):
    query = "SELECT course_id, course_code, course_name, credits, course_type, semester FROM courses WHERE 1=1"
    params = {}
    if department_id:
        query += " AND department_id = :department_id"
        params["department_id"] = department_id
    if semester:
        query += " AND semester = :semester"
        params["semester"] = semester
    rows = db.execute(text(query), params).mappings().all()
    return [dict(r) for r in rows]


@router.post("/courses", status_code=201)
def create_course(
    payload: CourseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin")),
):
    try:
        result = db.execute(
            text(
                """
                INSERT INTO courses (department_id, course_code, course_name, credits, course_type, semester)
                VALUES (:department_id, :course_code, :course_name, :credits, :course_type, :semester)
                """
            ),
            payload.model_dump(),
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Could not create course: {exc}")
    return {"message": "Course created", "course_id": result.lastrowid}


@router.get("/offerings", response_model=list[OfferingOut])
def list_offerings(
    academic_year: str | None = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "faculty", "student")),
):
    query = "SELECT * FROM vw_course_offering_summary WHERE 1=1"
    params = {}
    if academic_year:
        query += " AND academic_year = :academic_year"
        params["academic_year"] = academic_year
    rows = db.execute(text(query), params).mappings().all()
    return [dict(r) for r in rows]


@router.post("/offerings", status_code=201)
def create_offering(
    payload: OfferingCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin")),
):
    try:
        result = db.execute(
            text(
                """
                INSERT INTO course_offerings
                    (course_id, faculty_id, academic_year, semester_term, max_capacity, room_number)
                VALUES
                    (:course_id, :faculty_id, :academic_year, :semester_term, :max_capacity, :room_number)
                """
            ),
            payload.model_dump(),
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Could not create offering: {exc}")
    return {"message": "Offering created", "offering_id": result.lastrowid}


@router.get("/departments")
def list_departments(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "faculty", "student")),
):
    rows = db.execute(text("SELECT * FROM departments ORDER BY department_name")).mappings().all()
    return [dict(r) for r in rows]


@router.get("/programs")
def list_programs(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "faculty", "student")),
):
    rows = db.execute(text("SELECT * FROM programs ORDER BY program_name")).mappings().all()
    return [dict(r) for r in rows]

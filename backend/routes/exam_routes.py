from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from auth import require_role
from models.schemas import ExamCreate, ExamOut, ResultCreate, ResultOut

router = APIRouter(tags=["Exams & Results"])


@router.post("/exams", status_code=201)
def create_exam(
    payload: ExamCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "faculty")),
):
    try:
        result = db.execute(
            text(
                """
                INSERT INTO exams (offering_id, exam_name, exam_type, exam_date, max_marks, weightage_pct)
                VALUES (:offering_id, :exam_name, :exam_type, :exam_date, :max_marks, :weightage_pct)
                """
            ),
            payload.model_dump(),
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Could not create exam: {exc}")
    return {"message": "Exam created", "exam_id": result.lastrowid}


@router.get("/exams/offering/{offering_id}", response_model=list[ExamOut])
def list_exams_for_offering(
    offering_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "faculty", "student")),
):
    rows = db.execute(
        text("SELECT * FROM exams WHERE offering_id = :oid ORDER BY exam_date"),
        {"oid": offering_id},
    ).mappings().all()
    return [dict(r) for r in rows]


@router.post("/results", status_code=201)
def record_result(
    payload: ResultCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "faculty")),
):
    """
    The letter grade is computed automatically by trg_exam_results_grade;
    we don't set it here.
    """
    try:
        result = db.execute(
            text(
                """
                INSERT INTO exam_results (exam_id, student_id, marks_obtained, remarks)
                VALUES (:exam_id, :student_id, :marks_obtained, :remarks)
                """
            ),
            payload.model_dump(),
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Could not record result: {exc}")
    return {"message": "Result recorded", "result_id": result.lastrowid}


@router.get("/results/exam/{exam_id}", response_model=list[ResultOut])
def list_results_for_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "faculty")),
):
    rows = db.execute(
        text("SELECT * FROM exam_results WHERE exam_id = :eid"),
        {"eid": exam_id},
    ).mappings().all()
    return [dict(r) for r in rows]


@router.get("/results/leaderboard/{offering_id}")
def offering_leaderboard(
    offering_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "faculty")),
):
    """Uses vw_top_performers (window-function RANK) for a ranked leaderboard."""
    rows = db.execute(
        text(
            """
            SELECT tp.rank_in_course, tp.weighted_percentage,
                   s.enrollment_number, CONCAT(s.first_name, ' ', s.last_name) AS student_name
            FROM vw_top_performers tp
            JOIN students s ON s.student_id = tp.student_id
            WHERE tp.offering_id = :oid
            ORDER BY tp.rank_in_course
            """
        ),
        {"oid": offering_id},
    ).mappings().all()
    return [dict(r) for r in rows]

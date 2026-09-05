from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from auth import require_role

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Reports"])


@router.get("/admin-summary")
def admin_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin")),
):
    """Headline KPI cards for the admin dashboard."""
    total_students = db.execute(
        text("SELECT COUNT(*) FROM students WHERE status = 'active'")
    ).scalar()
    total_faculty = db.execute(text("SELECT COUNT(*) FROM faculty")).scalar()
    total_courses = db.execute(text("SELECT COUNT(*) FROM courses")).scalar()
    total_departments = db.execute(text("SELECT COUNT(*) FROM departments")).scalar()
    fees_collected = db.execute(
        text("SELECT COALESCE(SUM(amount_paid),0) FROM fee_payments WHERE status = 'completed'")
    ).scalar()
    fees_outstanding = db.execute(
        text("SELECT COALESCE(SUM(balance_due),0) FROM vw_student_fee_balance")
    ).scalar()

    return {
        "total_students": total_students,
        "total_faculty": total_faculty,
        "total_courses": total_courses,
        "total_departments": total_departments,
        "fees_collected": float(fees_collected or 0),
        "fees_outstanding": float(fees_outstanding or 0),
    }


@router.get("/students-per-department")
def students_per_department(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "faculty")),
):
    rows = db.execute(
        text(
            """
            SELECT d.department_name, COUNT(s.student_id) AS student_count
            FROM departments d
            LEFT JOIN programs p ON p.department_id = d.department_id
            LEFT JOIN students s ON s.program_id = p.program_id AND s.status = 'active'
            GROUP BY d.department_name
            ORDER BY student_count DESC
            """
        )
    ).mappings().all()
    return [dict(r) for r in rows]


@router.get("/grade-distribution/{offering_id}")
def grade_distribution(
    offering_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "faculty")),
):
    rows = db.execute(
        text(
            """
            SELECT er.grade, COUNT(*) AS student_count
            FROM exam_results er
            JOIN exams e ON e.exam_id = er.exam_id
            WHERE e.offering_id = :oid
            GROUP BY er.grade
            ORDER BY er.grade
            """
        ),
        {"oid": offering_id},
    ).mappings().all()
    return [dict(r) for r in rows]


@router.get("/fee-collection-trend")
def fee_collection_trend(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin")),
):
    rows = db.execute(
        text(
            """
            SELECT DATE_FORMAT(payment_date, '%Y-%m') AS month, SUM(amount_paid) AS total_collected
            FROM fee_payments
            WHERE status = 'completed'
            GROUP BY month
            ORDER BY month
            """
        )
    ).mappings().all()
    return [dict(r) for r in rows]

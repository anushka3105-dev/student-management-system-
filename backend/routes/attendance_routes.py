from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from auth import require_role
from models.schemas import AttendanceMark, AttendanceBulkMark

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post("/mark", status_code=201)
def mark_attendance(
    payload: AttendanceMark,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("faculty", "admin")),
):
    faculty_id = _resolve_faculty_id(db, current_user)
    try:
        db.execute(
            text(
                """
                INSERT INTO attendance (enrollment_id, class_date, status, marked_by)
                VALUES (:enrollment_id, :class_date, :status, :marked_by)
                ON DUPLICATE KEY UPDATE status = VALUES(status), marked_by = VALUES(marked_by)
                """
            ),
            {**payload.model_dump(), "marked_by": faculty_id},
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Could not mark attendance: {exc}")
    return {"message": "Attendance recorded"}


@router.post("/mark-bulk", status_code=201)
def mark_attendance_bulk(
    payload: AttendanceBulkMark,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("faculty", "admin")),
):
    """Calls sp_mark_attendance_bulk to mark a whole class in one transaction."""
    faculty_id = _resolve_faculty_id(db, current_user)
    raw_conn = db.connection().connection
    cursor = raw_conn.cursor()
    try:
        cursor.callproc(
            "sp_mark_attendance_bulk",
            (payload.offering_id, payload.class_date, faculty_id, payload.default_status),
        )
        raw_conn.commit()
    except Exception as exc:
        raw_conn.rollback()
        raise HTTPException(status_code=400, detail=f"Could not bulk-mark attendance: {exc}")
    finally:
        cursor.close()
    return {"message": "Attendance recorded for the class"}


@router.get("/offering/{offering_id}")
def offering_attendance(
    offering_id: int,
    class_date: str | None = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("faculty", "admin")),
):
    query = """
        SELECT a.attendance_id, s.student_id, s.enrollment_number,
               CONCAT(s.first_name, ' ', s.last_name) AS student_name,
               a.class_date, a.status
        FROM attendance a
        JOIN enrollments e ON e.enrollment_id = a.enrollment_id
        JOIN students s ON s.student_id = e.student_id
        WHERE e.offering_id = :offering_id
    """
    params = {"offering_id": offering_id}
    if class_date:
        query += " AND a.class_date = :class_date"
        params["class_date"] = class_date
    query += " ORDER BY a.class_date DESC, student_name"

    rows = db.execute(text(query), params).mappings().all()
    return [dict(r) for r in rows]


def _resolve_faculty_id(db: Session, current_user: dict) -> int:
    if current_user["role"] == "admin":
        # Admin marking on behalf of faculty still needs a valid faculty_id FK;
        # fall back to the first faculty record for demo purposes.
        row = db.execute(text("SELECT faculty_id FROM faculty LIMIT 1")).first()
    else:
        row = db.execute(
            text("SELECT faculty_id FROM faculty WHERE user_id = :uid"),
            {"uid": current_user["user_id"]},
        ).first()
    if not row:
        raise HTTPException(status_code=400, detail="No faculty record linked to this account")
    return row[0]

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from auth import require_role, get_current_user
from models.schemas import AnnouncementCreate

router = APIRouter(prefix="/announcements", tags=["Announcements"])


@router.get("")
def list_announcements(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    rows = db.execute(
        text(
            """
            SELECT announcement_id, title, body, target_role, posted_at, expires_at
            FROM announcements
            WHERE (target_role = 'all' OR target_role = :role)
              AND (expires_at IS NULL OR expires_at > NOW())
            ORDER BY posted_at DESC
            """
        ),
        {"role": current_user["role"]},
    ).mappings().all()
    return [dict(r) for r in rows]


@router.post("", status_code=201)
def create_announcement(
    payload: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "faculty")),
):
    try:
        result = db.execute(
            text(
                """
                INSERT INTO announcements (posted_by, title, body, target_role, department_id, expires_at)
                VALUES (:posted_by, :title, :body, :target_role, :department_id, :expires_at)
                """
            ),
            {"posted_by": current_user["user_id"], **payload.model_dump()},
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Could not create announcement: {exc}")
    return {"message": "Announcement posted", "announcement_id": result.lastrowid}


@router.delete("/{announcement_id}")
def delete_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "faculty")),
):
    result = db.execute(
        text("DELETE FROM announcements WHERE announcement_id = :aid"),
        {"aid": announcement_id},
    )
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return {"message": "Announcement deleted"}

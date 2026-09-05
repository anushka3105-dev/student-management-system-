from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from auth import authenticate_user, create_access_token, get_current_user
from models.schemas import Token, UserOut

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    db.execute(
        text("UPDATE users SET last_login = NOW() WHERE user_id = :uid"),
        {"uid": user["user_id"]},
    )
    db.commit()

    access_token = create_access_token(
        data={"sub": str(user["user_id"]), "role": user["role"]}
    )
    return Token(
        access_token=access_token,
        role=user["role"],
        user_id=user["user_id"],
        username=user["username"],
    )


@router.get("/me", response_model=UserOut)
def read_current_user(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.execute(
        text("SELECT user_id, username, email, role, is_active FROM users WHERE user_id = :uid"),
        {"uid": current_user["user_id"]},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return dict(row)

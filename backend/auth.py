"""
Authentication & authorization.

- Passwords hashed with bcrypt (passlib).
- Sessions are stateless JWT access tokens.
- Role-based access control via FastAPI dependencies: require_role(...).
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ---------------------------------------------------------------------------
# Password helpers
# ---------------------------------------------------------------------------
def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ---------------------------------------------------------------------------
# Authentication core
# ---------------------------------------------------------------------------
def authenticate_user(db: Session, username: str, password: str):
    row = db.execute(
        text(
            "SELECT user_id, username, password_hash, role, is_active "
            "FROM users WHERE username = :username"
        ),
        {"username": username},
    ).mappings().first()

    if not row:
        return None
    if not row["is_active"]:
        raise HTTPException(status_code=403, detail="Account is disabled")
    if not verify_password(password, row["password_hash"]):
        return None
    return row


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> dict:
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    row = db.execute(
        text("SELECT user_id, username, role, is_active FROM users WHERE user_id = :uid"),
        {"uid": user_id},
    ).mappings().first()

    if row is None:
        raise HTTPException(status_code=401, detail="User no longer exists")
    if not row["is_active"]:
        raise HTTPException(status_code=403, detail="Account is disabled")

    return dict(row)


def require_role(*allowed_roles: str):
    """
    Usage: current_user: dict = Depends(require_role("admin", "faculty"))
    Raises 403 if the authenticated user's role isn't in allowed_roles.
    """
    def _dependency(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {', '.join(allowed_roles)}",
            )
        return current_user
    return _dependency

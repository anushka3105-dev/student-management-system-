"""
Database connectivity layer.

Uses SQLAlchemy's engine + session machinery to talk to the MySQL schema
defined in database/schema.sql. Connection settings are read from
environment variables (see .env.example) so credentials never live in code.
"""
import os
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "student_management_system")

from urllib.parse import quote_plus

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    f"?charset=utf8mb4"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # avoids "MySQL server has gone away" on idle connections
    pool_recycle=1800,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def db_session():
    """Context-manager version for use outside request handlers (scripts, procs)."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def call_procedure(db, proc_name: str, params: list):
    """
    Helper to invoke a stored procedure with IN/OUT params via a raw DBAPI
    cursor (SQLAlchemy's ORM layer doesn't expose CALL + OUT params cleanly).
    Returns the OUT parameter values in the order they were declared with '@'.
    """
    connection = db.connection().connection  # raw PyMySQL connection
    cursor = connection.cursor()
    placeholders = ", ".join(["%s"] * len(params))
    cursor.callproc(proc_name, params)
    cursor.close()
    # Fetch OUT params via a SELECT on the session vars PyMySQL sets
    out_cursor = connection.cursor()
    out_names = ", ".join(f"@_{proc_name}_{i}" for i in range(len(params)))
    out_cursor.execute(f"SELECT {out_names}")
    result = out_cursor.fetchone()
    out_cursor.close()
    return result


def health_check() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

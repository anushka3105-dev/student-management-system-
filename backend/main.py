"""
Student Management System — FastAPI entrypoint.

Run with:
    uvicorn main:app --reload --port 8000
(from inside the backend/ directory, so the flat imports below resolve)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import health_check
from routes import (
    auth_routes,
    student_routes,
    faculty_routes,
    course_routes,
    enrollment_routes,
    attendance_routes,
    exam_routes,
    fee_routes,
    announcement_routes,
    dashboard_routes,
)

app = FastAPI(
    title="Student Management System API",
    description="REST API for a MySQL-backed student management system "
                "with role-based access for admin, faculty, and students.",
    version="1.0.0",
)

# Streamlit runs on a different port during local dev, so allow it through.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(student_routes.router)
app.include_router(faculty_routes.router)
app.include_router(course_routes.router)
app.include_router(enrollment_routes.router)
app.include_router(attendance_routes.router)
app.include_router(exam_routes.router)
app.include_router(fee_routes.router)
app.include_router(announcement_routes.router)
app.include_router(dashboard_routes.router)


@app.get("/", tags=["Health"])
def root():
    return {"message": "Student Management System API is running"}


@app.get("/health", tags=["Health"])
def health():
    return {"database_connected": health_check()}

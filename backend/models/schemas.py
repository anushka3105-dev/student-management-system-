"""
Pydantic request/response models shared across route modules.
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    username: str


class LoginRequest(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)
    role: str = Field(pattern="^(admin|faculty|student)$")


class UserOut(BaseModel):
    user_id: int
    username: str
    email: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Departments / Programs
# ---------------------------------------------------------------------------
class DepartmentOut(BaseModel):
    department_id: int
    department_name: str
    department_code: str
    hod_name: Optional[str] = None
    established_year: Optional[int] = None


class ProgramOut(BaseModel):
    program_id: int
    department_id: int
    program_name: str
    program_level: str
    duration_years: int
    total_semesters: int


# ---------------------------------------------------------------------------
# Students
# ---------------------------------------------------------------------------
class StudentCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=8)
    program_id: int
    enrollment_number: str
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str = Field(pattern="^(Male|Female|Other)$")
    phone: Optional[str] = None
    address: Optional[str] = None
    admission_year: int
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None


class StudentUpdate(BaseModel):
    phone: Optional[str] = None
    address: Optional[str] = None
    current_semester: Optional[int] = None
    status: Optional[str] = Field(default=None, pattern="^(active|graduated|suspended|dropped)$")


class StudentOut(BaseModel):
    student_id: int
    enrollment_number: str
    full_name: str
    email: str
    program_name: str
    department_name: str
    current_semester: int
    status: str


# ---------------------------------------------------------------------------
# Faculty
# ---------------------------------------------------------------------------
class FacultyCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=8)
    department_id: int
    employee_code: str
    first_name: str
    last_name: str
    designation: str = "Assistant Professor"
    qualification: Optional[str] = None
    phone: Optional[str] = None
    date_of_joining: date
    salary: Optional[float] = None


class FacultyOut(BaseModel):
    faculty_id: int
    employee_code: str
    first_name: str
    last_name: str
    designation: str
    department_id: int


# ---------------------------------------------------------------------------
# Courses / Offerings
# ---------------------------------------------------------------------------
class CourseCreate(BaseModel):
    department_id: int
    course_code: str
    course_name: str
    credits: int = Field(ge=1, le=6)
    course_type: str = Field(pattern="^(core|elective|lab)$")
    semester: int = Field(ge=1, le=12)


class CourseOut(BaseModel):
    course_id: int
    course_code: str
    course_name: str
    credits: int
    course_type: str
    semester: int


class OfferingCreate(BaseModel):
    course_id: int
    faculty_id: int
    academic_year: str
    semester_term: str = Field(pattern="^(odd|even)$")
    max_capacity: int = 60
    room_number: Optional[str] = None


class OfferingOut(BaseModel):
    offering_id: int
    course_code: str
    course_name: str
    faculty_name: str
    academic_year: str
    semester_term: str
    max_capacity: int
    enrolled_count: int
    seats_remaining: int


# ---------------------------------------------------------------------------
# Enrollments
# ---------------------------------------------------------------------------
class EnrollmentRequest(BaseModel):
    student_id: int
    offering_id: int


class EnrollmentOut(BaseModel):
    enrollment_id: int
    student_id: int
    offering_id: int
    status: str
    enrollment_date: date


# ---------------------------------------------------------------------------
# Attendance
# ---------------------------------------------------------------------------
class AttendanceMark(BaseModel):
    enrollment_id: int
    class_date: date
    status: str = Field(pattern="^(present|absent|late|excused)$")


class AttendanceBulkMark(BaseModel):
    offering_id: int
    class_date: date
    default_status: str = Field(default="present", pattern="^(present|absent|late|excused)$")


class AttendanceSummary(BaseModel):
    student_id: int
    offering_id: int
    total_sessions: int
    sessions_attended: int
    attendance_percentage: float


# ---------------------------------------------------------------------------
# Exams / Results
# ---------------------------------------------------------------------------
class ExamCreate(BaseModel):
    offering_id: int
    exam_name: str
    exam_type: str = Field(pattern="^(quiz|midterm|final|assignment)$")
    exam_date: date
    max_marks: float
    weightage_pct: float = Field(ge=0, le=100)


class ExamOut(BaseModel):
    exam_id: int
    offering_id: int
    exam_name: str
    exam_type: str
    exam_date: date
    max_marks: float
    weightage_pct: float


class ResultCreate(BaseModel):
    exam_id: int
    student_id: int
    marks_obtained: float
    remarks: Optional[str] = None


class ResultOut(BaseModel):
    result_id: int
    exam_id: int
    student_id: int
    marks_obtained: float
    grade: Optional[str]
    remarks: Optional[str]


# ---------------------------------------------------------------------------
# Fees
# ---------------------------------------------------------------------------
class FeePaymentRequest(BaseModel):
    student_id: int
    fee_structure_id: int
    amount: float = Field(gt=0)
    payment_mode: str = Field(pattern="^(cash|card|upi|bank_transfer)$")
    transaction_ref: Optional[str] = None


class FeeBalanceOut(BaseModel):
    student_id: int
    enrollment_number: str
    fee_structure_id: int
    academic_year: str
    semester: int
    total_due: float
    total_paid: float
    balance_due: float
    due_date: date


# ---------------------------------------------------------------------------
# Announcements
# ---------------------------------------------------------------------------
class AnnouncementCreate(BaseModel):
    title: str
    body: str
    target_role: str = Field(default="all", pattern="^(all|admin|faculty|student)$")
    department_id: Optional[int] = None
    expires_at: Optional[datetime] = None


class AnnouncementOut(BaseModel):
    announcement_id: int
    title: str
    body: str
    target_role: str
    posted_at: datetime
    expires_at: Optional[datetime]

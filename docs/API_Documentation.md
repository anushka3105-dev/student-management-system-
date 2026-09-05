# API Documentation — Student Management System

Base URL (local dev): `http://localhost:8000`
Interactive docs (Swagger UI): `http://localhost:8000/docs`

All endpoints except `/auth/login` and `/` and `/health` require a bearer
token obtained from `/auth/login`. Send it as:

```
Authorization: Bearer <access_token>
```

Roles: `admin`, `faculty`, `student`. Each route below lists which roles
may call it.

---

## Authentication

### `POST /auth/login`
Form-encoded (`username`, `password`). Returns a JWT access token.

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "role": "admin",
  "user_id": 1,
  "username": "admin1"
}
```

### `GET /auth/me`
Roles: any authenticated user. Returns the caller's own user record.

---

## Students

| Method | Path | Roles | Description |
|---|---|---|---|
| GET | `/students` | admin, faculty | List students (filter by `status_filter`, `program_id`) |
| GET | `/students/{student_id}` | any (students: self only) | Get one student's directory record |
| POST | `/students` | admin | Create a student (creates linked `users` row too) |
| PATCH | `/students/{student_id}` | admin, faculty | Update phone/address/semester/status |
| GET | `/students/{student_id}/attendance` | any | Attendance % per enrolled offering |
| GET | `/students/{student_id}/results` | any | Exam results across all courses |

## Faculty

| Method | Path | Roles | Description |
|---|---|---|---|
| GET | `/faculty` | any | List faculty (filter by `department_id`) |
| GET | `/faculty/workload` | admin | Courses taught + total students, per faculty member |
| POST | `/faculty` | admin | Create a faculty member |
| GET | `/faculty/{faculty_id}/offerings` | admin, faculty | Offerings taught by one faculty member |

## Departments & Programs

| Method | Path | Roles |
|---|---|---|
| GET | `/departments` | any |
| GET | `/programs` | any |

## Courses & Offerings

| Method | Path | Roles | Description |
|---|---|---|---|
| GET | `/courses` | any | Filter by `department_id`, `semester` |
| POST | `/courses` | admin | Add to the catalogue |
| GET | `/offerings` | any | Offerings with live seat counts (filter by `academic_year`) |
| POST | `/offerings` | admin | Schedule a course offering for a term |

## Enrollments

| Method | Path | Roles | Description |
|---|---|---|---|
| POST | `/enrollments` | admin, student | Enroll via `sp_enroll_student` (capacity-checked, transactional) |
| GET | `/enrollments` | any | Filter by `student_id` or `offering_id` |
| DELETE | `/enrollments/{enrollment_id}` | admin, student | Marks status `dropped` |

## Attendance

| Method | Path | Roles | Description |
|---|---|---|---|
| POST | `/attendance/mark` | faculty, admin | Mark one student for one date |
| POST | `/attendance/mark-bulk` | faculty, admin | Mark a whole offering via `sp_mark_attendance_bulk` |
| GET | `/attendance/offering/{offering_id}` | faculty, admin | Records for an offering (optional `class_date`) |

## Exams & Results

| Method | Path | Roles | Description |
|---|---|---|---|
| POST | `/exams` | admin, faculty | Create an exam under an offering |
| GET | `/exams/offering/{offering_id}` | any | List exams for an offering |
| POST | `/results` | admin, faculty | Record marks (grade auto-computed by trigger) |
| GET | `/results/exam/{exam_id}` | admin, faculty | All results for one exam |
| GET | `/results/leaderboard/{offering_id}` | admin, faculty | Ranked leaderboard (SQL `RANK()` window function) |

## Fees

| Method | Path | Roles | Description |
|---|---|---|---|
| GET | `/fees/structure` | any | Filter by `program_id` |
| GET | `/fees/balance/{student_id}` | any (students: self only) | Outstanding balance per term |
| POST | `/fees/pay` | admin, student | Record a payment via `sp_record_fee_payment` |

## Announcements

| Method | Path | Roles | Description |
|---|---|---|---|
| GET | `/announcements` | any | Feed filtered to caller's role, excludes expired |
| POST | `/announcements` | admin, faculty | Post a notice |
| DELETE | `/announcements/{announcement_id}` | admin, faculty | Remove a notice |

## Dashboard & Reports

| Method | Path | Roles | Description |
|---|---|---|---|
| GET | `/dashboard/admin-summary` | admin | KPI counts + fee totals |
| GET | `/dashboard/students-per-department` | admin, faculty | Bar-chart data |
| GET | `/dashboard/grade-distribution/{offering_id}` | admin, faculty | Grade counts for one offering |
| GET | `/dashboard/fee-collection-trend` | admin | Monthly collected total |

---

## Error format

All errors return:

```json
{ "detail": "human-readable message" }
```

Common status codes: `401` (missing/invalid/expired token), `403` (role
not permitted, or a student trying to access another student's data),
`404` (resource not found), `400` (validation or business-rule failure,
e.g. "offering is full").

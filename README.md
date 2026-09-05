# Student Management System

A full-stack student management system:

- **MySQL** — normalized schema, business logic (stored procedures, triggers, views, functions)
- **FastAPI** — REST API layer with JWT auth and role-based access control
- **Streamlit** — dashboards and forms for Admin, Faculty, and Student roles

Theme: Navy + White + Teal, built to feel like a clean institutional dashboard rather than a generic demo.

---

## 1. Project layout

```
student-management-system/
├── backend/            FastAPI app (auth, routes, DB access)
├── frontend/            Streamlit app (login + role-based dashboards)
├── database/            schema, seed data, procedures, triggers, views, functions, indexes
├── docs/                ER diagram, design notes, API docs
├── requirements.txt
└── README.md
```

## 2. Prerequisites

- Python 3.10+
- MySQL 8.0+ (needed for window functions and CHECK constraints used here)
- `pip`

## 3. Set up the database

```bash
mysql -u root -p < database/schema.sql
mysql -u root -p < database/indexes.sql
mysql -u root -p < database/functions.sql
mysql -u root -p < database/procedures.sql
mysql -u root -p < database/triggers.sql
mysql -u root -p < database/views.sql
mysql -u root -p < database/sample_data.sql
```

Run them **in this order** — triggers and views reference tables and
functions that must already exist.

> This SQL was authored and reviewed carefully but could not be executed
> against a live MySQL server in the environment that produced it (no
> internet access to install `mysql-server`). Run the scripts above against
> your own MySQL instance and skim the output for errors before relying on
> it — that's standard practice for any hand-written schema, but flagging
> it here since it wasn't machine-verified.

All demo accounts seeded by `sample_data.sql` use the password `Password123!`:

| Username     | Role    |
|--------------|---------|
| `admin1`     | admin   |
| `fac.iyer`   | faculty |
| `stu.arjun`  | student |
| `stu.priya`  | student |

(Full list in `database/sample_data.sql`.)

## 4. Configure environment variables

```bash
cp .env.example .env
# then edit .env with your MySQL password and a random JWT secret
```

## 5. Install dependencies

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 6. Run the backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

API docs (Swagger UI) will be at `http://localhost:8000/docs`.

## 7. Run the frontend

In a second terminal:

```bash
cd frontend
streamlit run app.py
```

Streamlit will open at `http://localhost:8501`. Log in with any of the demo
accounts above.

## 8. What's implemented

**Database**
- 14 normalized tables covering identity, academics, attendance, exams, fees, and announcements
- Foreign keys with appropriate `ON DELETE` behavior, `CHECK` constraints, `UNIQUE` composite keys
- 4 stored procedures wrapping multi-step writes in transactions (`sp_enroll_student`, `sp_record_fee_payment`, `sp_calculate_final_grade`, `sp_mark_attendance_bulk`)
- 5 triggers (auto-grading, over-mark prevention, capacity enforcement, auto-graduation, payment audit log)
- 6 views, including one using a window function (`RANK() OVER (PARTITION BY ...)`) for a leaderboard
- 4 SQL functions
- Indexes tuned for the query patterns the API actually uses

**Backend (FastAPI)**
- JWT-based auth (`/auth/login`), bcrypt password hashing
- Role-based access control via a `require_role(...)` dependency (admin / faculty / student)
- Routes for students, faculty, courses & offerings, enrollments, attendance, exams & results, fees, announcements, and dashboard analytics
- Calls stored procedures directly for the operations that need transactional guarantees (enrollment capacity, fee payment)

**Frontend (Streamlit)**
- Login page + role-based landing
- Admin dashboard: KPIs, charts (Plotly), student/faculty/course management, fee overview
- Faculty portal: offering summary, bulk attendance marking, exam creation, grading, leaderboard
- Student portal: profile, course enrollment, attendance, results, fee payment
- Shared announcements board
- Navy + White + Teal design system in `frontend/components/theme.py`

## 9. Known simplifications (would be next steps for production)

- The Student Portal currently asks the logged-in student to enter their
  numeric `student_id` once per session rather than resolving it from the
  JWT automatically — the `/students` list endpoint is admin/faculty-only,
  so this is the simplest fix without adding a new `/me/student` endpoint.
- `sample_data.sql` is illustrative, not exhaustive — enough rows to
  exercise every table and relationship, not a realistic full dataset.
- No automated test suite is included; see `docs/API_Documentation.md` for
  manually verifying each endpoint via Swagger UI.

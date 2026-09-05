import streamlit as st
import pandas as pd
import plotly.express as px

from components.theme import apply_theme, page_banner, CHART_SEQUENCE, TEAL_500, NAVY_900
from components.api_client import require_login, api_get, api_post

st.set_page_config(page_title="Admin Dashboard", page_icon="📊", layout="wide")
apply_theme()
require_login(allowed_roles=["admin"])

page_banner("Admin Dashboard", "Institution-wide overview and management")

# ---------------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------------
summary = api_get("/dashboard/admin-summary") or {}

c1, c2, c3, c4 = st.columns(4)
c1.metric("Active Students", summary.get("total_students", "—"))
c2.metric("Faculty Members", summary.get("total_faculty", "—"))
c3.metric("Courses Offered", summary.get("total_courses", "—"))
c4.metric("Departments", summary.get("total_departments", "—"))

c5, c6 = st.columns(2)
c5.metric("Fees Collected", f"₹{summary.get('fees_collected', 0):,.0f}")
c6.metric("Fees Outstanding", f"₹{summary.get('fees_outstanding', 0):,.0f}")

st.divider()

# ---------------------------------------------------------------------------
# Tabs: Overview, Students, Faculty, Courses, Fees, Announcements
# ---------------------------------------------------------------------------
tab_overview, tab_students, tab_faculty, tab_courses, tab_fees = st.tabs(
    ["📈 Overview", "🧑‍🎓 Students", "🧑‍🏫 Faculty", "📘 Courses & Offerings", "💰 Fees"]
)

with tab_overview:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Students per Department")
        dept_data = api_get("/dashboard/students-per-department") or []
        if dept_data:
            df = pd.DataFrame(dept_data)
            fig = px.bar(
                df, x="department_name", y="student_count",
                color_discrete_sequence=[TEAL_500],
            )
            fig.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                font_color=NAVY_900, xaxis_title="", yaxis_title="Students",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No data yet.")

    with col2:
        st.subheader("Fee Collection Trend")
        trend_data = api_get("/dashboard/fee-collection-trend") or []
        if trend_data:
            df = pd.DataFrame(trend_data)
            fig = px.line(
                df, x="month", y="total_collected", markers=True,
                color_discrete_sequence=[NAVY_900],
            )
            fig.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                font_color=NAVY_900, xaxis_title="", yaxis_title="₹ Collected",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No payments recorded yet.")

with tab_students:
    st.subheader("Student Directory")
    status_filter = st.selectbox("Filter by status", ["", "active", "graduated", "suspended", "dropped"])
    students = api_get("/students", params={"status_filter": status_filter} if status_filter else None) or []
    if students:
        st.dataframe(pd.DataFrame(students), use_container_width=True, hide_index=True)
    else:
        st.caption("No students found.")

    with st.expander("➕ Enroll a new student"):
        programs = api_get("/programs") or []
        if not programs:
            st.warning(
                "No programs found — a student can't be created without one. "
                "Check that `database/sample_data.sql` ran successfully, or add a "
                "program first."
            )
        program_options = {p["program_name"]: p["program_id"] for p in programs}

        with st.form("new_student_form"):
            col1, col2 = st.columns(2)
            with col1:
                username = st.text_input("Username *")
                email = st.text_input("Email *", placeholder="name@example.com")
                password = st.text_input(
                    "Temporary password *", type="password",
                    help="Must be at least 8 characters.",
                )
                first_name = st.text_input("First name *")
                last_name = st.text_input("Last name *")
                enrollment_number = st.text_input("Enrollment number *")
            with col2:
                program_choice = st.selectbox(
                    "Program *",
                    list(program_options.keys()) if program_options else [],
                    disabled=not program_options,
                )
                dob = st.date_input("Date of birth *")
                gender = st.selectbox("Gender *", ["Male", "Female", "Other"])
                admission_year = st.number_input("Admission year *", min_value=2015, max_value=2030, value=2025)
                phone = st.text_input("Phone")

            submitted = st.form_submit_button("Create Student", type="primary")
            if submitted:
                missing = [
                    label for label, val in [
                        ("Username", username), ("Email", email), ("Password", password),
                        ("First name", first_name), ("Last name", last_name),
                        ("Enrollment number", enrollment_number),
                    ] if not val
                ]
                if not program_options:
                    st.error("Can't create a student with no program available. See the warning above.")
                elif missing:
                    st.error(f"Please fill in: {', '.join(missing)}")
                elif len(password) < 8:
                    st.error("Password must be at least 8 characters.")
                else:
                    payload = {
                        "username": username, "email": email, "password": password,
                        "program_id": program_options.get(program_choice),
                        "enrollment_number": enrollment_number,
                        "first_name": first_name, "last_name": last_name,
                        "date_of_birth": str(dob), "gender": gender,
                        "phone": phone or None, "admission_year": admission_year,
                    }
                    result = api_post("/students", json=payload)
                    if result:
                        st.success(f"Student created — they can now log in as `{username}`.")
                        st.rerun()

with tab_faculty:
    st.subheader("Faculty Directory")
    faculty = api_get("/faculty") or []
    if faculty:
        st.dataframe(pd.DataFrame(faculty), use_container_width=True, hide_index=True)

    st.subheader("Faculty Workload")
    workload = api_get("/faculty/workload") or []
    if workload:
        st.dataframe(pd.DataFrame(workload), use_container_width=True, hide_index=True)

with tab_courses:
    st.subheader("Course Offerings — this term")
    offerings = api_get("/offerings") or []
    if offerings:
        st.dataframe(pd.DataFrame(offerings), use_container_width=True, hide_index=True)
    else:
        st.caption("No offerings found.")

    st.subheader("Course Catalogue")
    courses = api_get("/courses") or []
    if courses:
        st.dataframe(pd.DataFrame(courses), use_container_width=True, hide_index=True)

with tab_fees:
    st.subheader("Fee Structures")
    structures = api_get("/fees/structure") or []
    if structures:
        st.dataframe(pd.DataFrame(structures), use_container_width=True, hide_index=True)
    else:
        st.caption("No fee structures configured yet.")

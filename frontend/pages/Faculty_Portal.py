import streamlit as st
import pandas as pd
from datetime import date

from components.theme import apply_theme, page_banner
from components.api_client import require_login, api_get, api_post

st.set_page_config(page_title="Faculty Portal", page_icon="🧑‍🏫", layout="wide")
apply_theme()
require_login(allowed_roles=["faculty", "admin"])

page_banner("Faculty Portal", "Manage your course offerings, attendance, and grading")

tab_offerings, tab_attendance, tab_grading = st.tabs(
    ["📘 My Offerings", "🗓️ Attendance", "📝 Exams & Grading"]
)

with tab_offerings:
    st.subheader("Course Offering Summary")
    offerings = api_get("/offerings") or []
    if offerings:
        st.dataframe(pd.DataFrame(offerings), use_container_width=True, hide_index=True)
        offering_lookup = {
            f"{o['course_code']} — {o['course_name']} ({o['academic_year']})": o["offering_id"]
            for o in offerings
        }
    else:
        offering_lookup = {}
        st.caption("No offerings found.")

with tab_attendance:
    st.subheader("Mark Attendance")
    if offering_lookup:
        selected_label = st.selectbox("Course offering", list(offering_lookup.keys()))
        offering_id = offering_lookup[selected_label]
        class_date = st.date_input("Class date", value=date.today())
        default_status = st.selectbox("Mark whole class as", ["present", "absent", "late", "excused"])

        if st.button("Mark whole class", type="primary"):
            result = api_post(
                "/attendance/mark-bulk",
                json={
                    "offering_id": offering_id,
                    "class_date": str(class_date),
                    "default_status": default_status,
                },
            )
            if result:
                st.success(result.get("message", "Attendance recorded"))

        st.divider()
        st.subheader("Attendance Records")
        records = api_get(f"/attendance/offering/{offering_id}") or []
        if records:
            st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)
        else:
            st.caption("No attendance marked yet for this offering.")
    else:
        st.caption("No offerings available to mark attendance for.")

with tab_grading:
    st.subheader("Create an Exam")
    if offering_lookup:
        with st.form("new_exam_form"):
            selected_label = st.selectbox("Course offering", list(offering_lookup.keys()), key="exam_offering")
            offering_id = offering_lookup[selected_label]
            exam_name = st.text_input("Exam name", placeholder="e.g. Midterm")
            exam_type = st.selectbox("Exam type", ["quiz", "midterm", "final", "assignment"])
            exam_date = st.date_input("Exam date")
            max_marks = st.number_input("Max marks", min_value=1.0, value=100.0)
            weightage = st.number_input("Weightage (%)", min_value=0.0, max_value=100.0, value=30.0)
            submitted = st.form_submit_button("Create Exam", type="primary")
            if submitted:
                result = api_post(
                    "/exams",
                    json={
                        "offering_id": offering_id, "exam_name": exam_name,
                        "exam_type": exam_type, "exam_date": str(exam_date),
                        "max_marks": max_marks, "weightage_pct": weightage,
                    },
                )
                if result:
                    st.success("Exam created.")

        st.divider()
        st.subheader("Enter a Result")
        with st.form("new_result_form"):
            exams = api_get(f"/exams/offering/{offering_id}") or []
            exam_lookup = {f"{e['exam_name']} ({e['exam_date']})": e["exam_id"] for e in exams}
            if exam_lookup:
                exam_choice = st.selectbox("Exam", list(exam_lookup.keys()))
                student_id = st.number_input("Student ID", min_value=1, step=1)
                marks = st.number_input("Marks obtained", min_value=0.0)
                remarks = st.text_input("Remarks (optional)")
                submitted_r = st.form_submit_button("Save Result", type="primary")
                if submitted_r:
                    result = api_post(
                        "/results",
                        json={
                            "exam_id": exam_lookup[exam_choice], "student_id": int(student_id),
                            "marks_obtained": marks, "remarks": remarks or None,
                        },
                    )
                    if result:
                        st.success("Result saved — grade computed automatically.")
            else:
                st.caption("Create an exam first.")
                st.form_submit_button("Save Result", disabled=True)

        st.divider()
        st.subheader("Leaderboard")
        leaderboard = api_get(f"/results/leaderboard/{offering_id}") or []
        if leaderboard:
            st.dataframe(pd.DataFrame(leaderboard), use_container_width=True, hide_index=True)
    else:
        st.caption("No offerings available.")

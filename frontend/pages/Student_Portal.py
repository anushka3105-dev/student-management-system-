import streamlit as st
import pandas as pd

from components.theme import apply_theme, page_banner
from components.api_client import require_login, api_get, api_post

st.set_page_config(page_title="Student Portal", page_icon="📚", layout="wide")
apply_theme()
require_login(allowed_roles=["student", "admin"])

page_banner("Student Portal", "Your courses, attendance, grades, and fees")

# Ask the student for their student_id once, cache it in session.
# (A production build would resolve this from the JWT/user record instead
# of asking, but the API's /students list endpoint is admin/faculty-only.)
if "student_id" not in st.session_state:
    st.session_state["student_id"] = st.number_input(
        "Enter your Student ID (shown on your enrollment letter)", min_value=1, step=1
    )

student_id = st.session_state.get("student_id")

tab_profile, tab_courses, tab_attendance, tab_results, tab_fees = st.tabs(
    ["👤 Profile", "📘 My Courses", "🗓️ Attendance", "📝 Results", "💰 Fees"]
)

with tab_profile:
    if student_id:
        record = api_get(f"/students/{int(student_id)}")
        if record:
            col1, col2 = st.columns(2)
            col1.metric("Name", record.get("full_name", "—"))
            col1.metric("Enrollment Number", record.get("enrollment_number", "—"))
            col2.metric("Program", record.get("program_name", "—"))
            col2.metric("Current Semester", record.get("current_semester", "—"))

with tab_courses:
    if student_id:
        enrollments = api_get("/enrollments", params={"student_id": int(student_id)}) or []
        if enrollments:
            st.dataframe(pd.DataFrame(enrollments), use_container_width=True, hide_index=True)
        else:
            st.caption("No enrollments found.")

        st.divider()
        st.subheader("Enroll in a New Course Offering")
        offerings = api_get("/offerings") or []
        if offerings:
            offering_lookup = {
                f"{o['course_code']} — {o['course_name']} ({o['seats_remaining']} seats left)": o["offering_id"]
                for o in offerings
            }
            choice = st.selectbox("Available offerings", list(offering_lookup.keys()))
            if st.button("Enroll", type="primary"):
                result = api_post(
                    "/enrollments",
                    json={"student_id": int(student_id), "offering_id": offering_lookup[choice]},
                )
                if result:
                    st.success(result.get("message", "Enrolled"))
                    st.rerun()

with tab_attendance:
    if student_id:
        attendance = api_get(f"/students/{int(student_id)}/attendance") or []
        if attendance:
            df = pd.DataFrame(attendance)
            st.dataframe(df, use_container_width=True, hide_index=True)
            avg = df["attendance_percentage"].mean()
            st.metric("Overall Attendance", f"{avg:.1f}%")
            if avg < 75:
                st.warning("Your attendance is below the 75% requirement in at least one course.")
        else:
            st.caption("No attendance records yet.")

with tab_results:
    if student_id:
        results = api_get(f"/students/{int(student_id)}/results") or []
        if results:
            st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)
        else:
            st.caption("No results published yet.")

with tab_fees:
    if student_id:
        balances = api_get(f"/fees/balance/{int(student_id)}") or []
        if balances:
            df = pd.DataFrame(balances)
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.divider()
            st.subheader("Make a Payment")
            fee_lookup = {
                f"Sem {b['semester']} ({b['academic_year']}) — Balance ₹{b['balance_due']:,.0f}": b["fee_structure_id"]
                for b in balances if b["balance_due"] > 0
            }
            if fee_lookup:
                choice = st.selectbox("Fee to pay", list(fee_lookup.keys()))
                amount = st.number_input("Amount", min_value=1.0)
                mode = st.selectbox("Payment mode", ["upi", "card", "bank_transfer", "cash"])
                ref = st.text_input("Transaction reference (optional)")
                if st.button("Pay Now", type="primary"):
                    result = api_post(
                        "/fees/pay",
                        json={
                            "student_id": int(student_id),
                            "fee_structure_id": fee_lookup[choice],
                            "amount": amount, "payment_mode": mode,
                            "transaction_ref": ref or None,
                        },
                    )
                    if result:
                        st.success(f"Payment recorded. Remaining balance: ₹{result.get('balance_due', 0):,.0f}")
                        st.rerun()
            else:
                st.success("No outstanding balance. 🎉")
        else:
            st.caption("No fee records found.")

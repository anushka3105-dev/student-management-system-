"""
Student Management System — Streamlit entry point (login + landing page).

Run with:
    streamlit run app.py
(from inside the frontend/ directory)
"""
import streamlit as st
from components.theme import apply_theme, page_banner, NAVY_900, TEAL_500
from components.api_client import api_post, API_BASE_URL

st.set_page_config(
    page_title="Student Management System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)
apply_theme()


def login_view():
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown(
            f"""
            <div style="text-align:center; margin-bottom: 28px;">
                <div style="font-size:2.2rem;">🎓</div>
                <h1 style="color:{NAVY_900}; margin-bottom:4px;">Student Management System</h1>
                <p style="color:#4A5A6A;">Sign in with your admin, faculty, or student account</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            username = st.text_input("Username", placeholder="e.g. stu.arjun")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            login_clicked = st.button("Sign In", use_container_width=True, type="primary")

            if login_clicked:
                if not username or not password:
                    st.warning("Enter both username and password.")
                else:
                    result = api_post(
                        "/auth/login",
                        data={"username": username, "password": password},
                    )
                    if result:
                        st.session_state["access_token"] = result["access_token"]
                        st.session_state["role"] = result["role"]
                        st.session_state["user_id"] = result["user_id"]
                        st.session_state["username"] = result["username"]
                        st.success(f"Welcome back, {result['username']}!")
                        st.rerun()

        st.caption(f"Demo accounts (password `Password123!`): admin1 · fac.iyer · stu.arjun")
        st.caption(f"API: {API_BASE_URL}")


def landing_view():
    role = st.session_state["role"]
    page_banner(
        f"Welcome, {st.session_state['username']} 👋",
        f"You're signed in as <span class='sms-pill'>{role.upper()}</span>",
    )

    st.write("Use the sidebar to navigate to your dashboard.")

    role_pages = {
        "admin": "📊 Admin Dashboard",
        "faculty": "🧑‍🏫 Faculty Portal",
        "student": "📚 Student Portal",
    }
    st.info(f"Head to **{role_pages[role]}** in the left sidebar to get started.")

    if st.button("Log out"):
        st.session_state.clear()
        st.rerun()


if "access_token" not in st.session_state:
    login_view()
else:
    landing_view()

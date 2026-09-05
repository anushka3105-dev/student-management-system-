import streamlit as st
import pandas as pd

from components.theme import apply_theme, page_banner
from components.api_client import require_login, api_get, api_post, api_delete

st.set_page_config(page_title="Announcements", page_icon="📢", layout="wide")
apply_theme()
require_login()

page_banner("Announcements", "Notices relevant to your role")

announcements = api_get("/announcements") or []

if not announcements:
    st.info("No announcements right now.")
else:
    for a in announcements:
        with st.container(border=True):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"**{a['title']}**")
                st.write(a["body"])
                st.caption(f"Posted {a['posted_at']} · audience: {a['target_role']}")
            with col2:
                if st.session_state["role"] in ("admin", "faculty"):
                    if st.button("Delete", key=f"del_{a['announcement_id']}"):
                        if api_delete(f"/announcements/{a['announcement_id']}"):
                            st.rerun()

if st.session_state["role"] in ("admin", "faculty"):
    st.divider()
    st.subheader("Post a New Announcement")
    with st.form("new_announcement"):
        title = st.text_input("Title")
        body = st.text_area("Body")
        target_role = st.selectbox("Audience", ["all", "admin", "faculty", "student"])
        submitted = st.form_submit_button("Post", type="primary")
        if submitted:
            result = api_post(
                "/announcements",
                json={"title": title, "body": body, "target_role": target_role},
            )
            if result:
                st.success("Announcement posted.")
                st.rerun()

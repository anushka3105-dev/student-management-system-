"""
Thin wrapper around `requests` for calling the FastAPI backend from Streamlit
pages. Centralizes the base URL, the auth header, and error handling so
pages don't repeat try/except boilerplate.
"""
import os
import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def _headers():
    token = st.session_state.get("access_token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def _format_detail(detail) -> str:
    """
    FastAPI returns `detail` as a plain string for most errors (400, 403,
    404, 409...) but as a LIST of {"loc": [...], "msg": ..., "type": ...}
    dicts for 422 validation errors. Without this, a validation failure
    rendered as an unreadable raw Python list/dict instead of a message.
    """
    if isinstance(detail, list):
        lines = []
        for err in detail:
            field = err.get("loc", ["field"])[-1]
            msg = err.get("msg", "Invalid value")
            lines.append(f"**{field}**: {msg}")
        return "\n\n".join(lines) if lines else "Invalid request."
    return str(detail)


def _handle_response(resp: requests.Response, treat_401_as_expired: bool = True):
    if resp.status_code == 401:
        if treat_401_as_expired and "access_token" in st.session_state:
            # A 401 on a call we made WITH a token means that token is no
            # longer valid (expired, or the user was deactivated).
            st.session_state.clear()
            st.error("Your session has expired. Please log in again.")
            st.stop()
        else:
            # A 401 with no token in play yet (e.g. the initial /auth/login
            # call) means the credentials themselves were rejected — not an
            # expired session. Show the backend's real reason instead.
            try:
                detail = resp.json().get("detail", "Invalid username or password")
            except ValueError:
                detail = "Invalid username or password"
            st.error(_format_detail(detail))
            return None
    if resp.status_code >= 400:
        try:
            detail = resp.json().get("detail", resp.text)
        except ValueError:
            detail = resp.text
        st.error(f"Request failed:\n\n{_format_detail(detail)}")
        return None
    if resp.status_code == 204 or not resp.content:
        return {}
    return resp.json()


def api_get(path: str, params: dict | None = None):
    try:
        resp = requests.get(f"{API_BASE_URL}{path}", headers=_headers(), params=params, timeout=15)
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach the API server. Is `uvicorn main:app` running?")
        st.stop()
    return _handle_response(resp)


def api_post(path: str, json: dict | None = None, data: dict | None = None):
    try:
        resp = requests.post(f"{API_BASE_URL}{path}", headers=_headers(), json=json, data=data, timeout=15)
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach the API server. Is `uvicorn main:app` running?")
        st.stop()
    return _handle_response(resp)


def api_patch(path: str, json: dict | None = None):
    try:
        resp = requests.patch(f"{API_BASE_URL}{path}", headers=_headers(), json=json, timeout=15)
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach the API server. Is `uvicorn main:app` running?")
        st.stop()
    return _handle_response(resp)


def api_delete(path: str):
    try:
        resp = requests.delete(f"{API_BASE_URL}{path}", headers=_headers(), timeout=15)
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach the API server. Is `uvicorn main:app` running?")
        st.stop()
    return _handle_response(resp)


def require_login(allowed_roles: list[str] | None = None):
    """Call at the top of every protected page. Redirects to login if needed."""
    if "access_token" not in st.session_state:
        st.warning("Please log in to continue.")
        st.stop()
    if allowed_roles and st.session_state.get("role") not in allowed_roles:
        st.error("You don't have permission to view this page.")
        st.stop()

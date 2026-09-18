import html
from datetime import datetime

import extra_streamlit_components as stx
import requests
import streamlit as st


# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="DocQuery - Dashboard",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = "http://127.0.0.1:8000"


# =========================================================
# COOKIE MANAGER
# =========================================================

cookie_manager = stx.CookieManager(
    key="global_cookie_manager"
)


# =========================================================
# AUTH HELPERS
# =========================================================

def read_cookie_token():
    """
    Read the existing access_token from the browser.
    Uses multiple existing mechanisms without creating
    another authentication system.
    """

    try:
        if hasattr(st, "context") and hasattr(st.context, "cookies"):
            token = st.context.cookies.get("access_token")
            if token:
                import urllib.parse
                return urllib.parse.unquote(token).strip('"\'')
    except Exception:
        pass

    try:
        token = cookie_manager.get("access_token")
        if token:
            import urllib.parse
            return urllib.parse.unquote(str(token)).strip('"\'')
    except Exception:
        pass

    try:
        cookies = cookie_manager.get_all()

        if cookies:
            token = cookies.get(
                "access_token"
            )

            if token:
                return token

    except Exception:
        pass

    return None


def remove_auth_cookie():
    """
    Safely remove the existing authentication cookie.
    """

    try:
        cookies = cookie_manager.get_all()

        if cookies and "access_token" in cookies:

            try:
                cookie_manager.delete(
                    "access_token"
                )

            except KeyError:
                pass

    except Exception:
        pass


def go_to_login(reason_is_failure: bool):
    """
    Single choke point for every redirect back to login.

    reason_is_failure=True means: token missing/expired/rejected.
    This sets auth_failed so login.py takes the branch that skips
    re-reading the cookie entirely. Without this flag, login.py
    would fall into its "restore from cookie" branch and could read
    the SAME stale token again before the browser has actually
    finished deleting it (cookie deletion via the JS component isn't
    synchronous with this Python rerun) -> bounces straight back to
    dashboard -> 401 again -> infinite loop.
    """

    st.session_state.pop("access_token", None)
    st.session_state.pop("user", None)
    st.session_state.pop("_dashboard_auth_attempt", None)

    # Clear any cached API responses tied to the dead token.
    get_current_user.clear()
    get_documents.clear()

    if reason_is_failure:
        st.session_state["auth_failed"] = True

    # This flag tells login.py NOT to re-read the cookie (which would
    # still hold the now-invalid/deleted token while the browser JS
    # component hasn't yet propagated the deletion) and bounce
    # straight back here -> infinite 401 loop.
    st.session_state["_skip_cookie_restore"] = True

    remove_auth_cookie()

    st.switch_page("pages/login.py")
    st.stop()


def logout():
    """
    Complete logout flow (user-initiated).
    """

    st.session_state.pop("access_token", None)
    st.session_state.pop("user", None)
    st.session_state.pop("_dashboard_auth_attempt", None)

    get_current_user.clear()
    get_documents.clear()

    st.session_state["logout_requested"] = True
    # Ensure login.py skips cookie restore (same guard as go_to_login).
    st.session_state["_skip_cookie_restore"] = True

    remove_auth_cookie()

    st.switch_page("pages/login.py")


# =========================================================
# RESTORE AUTH AFTER REFRESH
# =========================================================

access_token = st.session_state.get("access_token")

if not access_token:
    # Try to restore from cookie (covers page-refresh case)
    access_token = read_cookie_token()

    if access_token:
        st.session_state["access_token"] = access_token


# CookieManager may need ONE extra Streamlit pass after a browser
# refresh (the JS component is async). Allow exactly ONE rerun;
# on the second pass with still no token, treat it as "not logged in".
if not access_token:
    attempt = st.session_state.get("_dashboard_auth_attempt", 0)

    if attempt < 1:
        # First visit with no token: give CookieManager one chance to hydrate
        st.session_state["_dashboard_auth_attempt"] = attempt + 1
        import time
        time.sleep(0.3)
        st.rerun()

    # No token after the single hydration rerun — genuinely not logged in.
    # Do NOT call /me. Redirect directly to login.
    st.session_state.pop("_dashboard_auth_attempt", None)
    st.switch_page("pages/login.py")
    st.stop()


# Authentication successfully restored
st.session_state.pop(
    "_dashboard_auth_attempt",
    None,
)

st.session_state[
    "access_token"
] = access_token


# =========================================================
# API HEADERS
# =========================================================

headers = {
    "Authorization": (
        f"Bearer {access_token}"
    )
}


# =========================================================
# API FUNCTIONS (cached per-token so a hydration rerun or a
# normal Streamlit rerun doesn't re-hit the backend twice for
# the same token; cache is cleared on logout/auth failure above)
# =========================================================

@st.cache_data(ttl=30, show_spinner=False)
def get_current_user(token: str):
    try:

        response = requests.get(
            f"{API_URL}/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )

        if response.status_code == 200:
            return response.json()

        if response.status_code == 401:
            return "UNAUTHORIZED"

    except requests.RequestException:
        pass

    return None


@st.cache_data(ttl=30, show_spinner=False)
def get_documents(token: str):
    try:

        response = requests.get(
            f"{API_URL}/documents",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )

        if response.status_code == 200:

            data = response.json()

            if isinstance(data, list):
                return data

            if isinstance(data, dict):
                return data.get(
                    "documents",
                    [],
                )

        if response.status_code == 401:
            return "UNAUTHORIZED"

    except requests.RequestException:
        pass

    return []


# =========================================================
# VALIDATE AUTH WITH BACKEND
# =========================================================

user = get_current_user(access_token)

if user == "UNAUTHORIZED":
    go_to_login(reason_is_failure=True)


documents = get_documents(access_token)

if documents == "UNAUTHORIZED":
    go_to_login(reason_is_failure=True)


if not isinstance(documents, list):
    documents = []


# =========================================================
# USER DATA
# =========================================================

if isinstance(user, dict):

    user_name = (
        user.get("name")
        or user.get("username")
        or user.get("email")
        or "User"
    )

    # "Nonprofit Org" in the target design is an org/role label, not
    # an email. Swap the key below (e.g. user.get("organization")) once
    # your /me response includes that field - falls back to email today.
    user_subtitle = (
        user.get("organization")
        or user.get("org")
        or user.get("email")
        or ""
    )

else:

    user_name = "User"
    user_subtitle = ""


safe_name = html.escape(
    str(user_name)
)

safe_subtitle = html.escape(
    str(user_subtitle)
)

initial = (
    str(user_name)[0].upper()
    if user_name
    else "U"
)

# Persist for sidebar use on Documents/Chat pages
st.session_state["user_name"] = user_name
st.session_state["user_subtitle"] = user_subtitle


# =========================================================
# DATA HELPERS
# =========================================================

def format_date(value):

    if not value:
        return ""

    try:

        if isinstance(
            value,
            datetime,
        ):
            dt = value

        else:

            dt = datetime.fromisoformat(
                str(value).replace(
                    "Z",
                    "+00:00",
                )
            )

        return dt.strftime(
            "%b %d, %Y"
        )

    except Exception:

        return str(value)[:16]


def get_storage(documents):

    total_bytes = 0

    for document in documents:

        value = (
            document.get("file_size")
            or document.get("size")
            or 0
        )

        try:
            total_bytes += int(value)

        except (
            TypeError,
            ValueError,
        ):
            pass

    if total_bytes <= 0:
        return "0 MB", 0

    mb = (
        total_bytes
        / (1024 * 1024)
    )

    if mb < 1:
        kb = (
            total_bytes
            / 1024
        )

        return (
            f"{kb:.1f} KB",
            total_bytes,
        )

    if mb < 1024:

        return (
            f"{mb:.1f} MB",
            total_bytes,
        )

    gb = (
        mb / 1024
    )

    return (
        f"{gb:.1f} GB",
        total_bytes,
    )


storage_label, storage_bytes = (
    get_storage(documents)
)

quota_bytes = (
    10
    * 1024
    * 1024
    * 1024
)

storage_percent = 0

if storage_bytes:
    storage_percent = min(
        100,
        (
            storage_bytes
            / quota_bytes
        )
        * 100,
    )


questions_asked = (
    st.session_state.get(
        "questions_asked",
        0,
    )
)

recent_chats = (
    st.session_state.get(
        "recent_chats",
        [],
    )
)

if not isinstance(
    recent_chats,
    list,
):
    recent_chats = []


# =========================================================
# GLOBAL CSS
# =========================================================

st.markdown(
    """
    <style>

    [data-testid="stSidebarNav"],
    [data-testid="stSidebarNavItems"],
    [data-testid="stSidebarNavSeparator"],
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stAppDeployButton"],
    footer,
    #MainMenu {
        display: none !important;
    }

    /* Keep sidebar always visible — hide only the default collapse arrow
       by making it invisible but still occupying space (so layout is stable). */
    [data-testid="stSidebarCollapseButton"] {
        visibility: hidden !important;
        pointer-events: none !important;
    }

    html,
    body,
    .stApp {
        background: #080d18 !important;
        color: #f8fafc !important;
    }

    .block-container {
        max-width: 1180px !important;
        padding: 30px 34px 40px 26px !important;
    }

    /* ---------------- SIDEBAR SHELL ---------------- */

    section[data-testid="stSidebar"] {
        background: #101827 !important;
        border-right: 1px solid #1d2838 !important;
        min-width: 208px !important;
        max-width: 208px !important;
        width: 208px !important;
        display: flex !important;
        visibility: visible !important;
        transform: none !important;
    }

    section[data-testid="stSidebar"] > div:first-child {
        background: #101827 !important;
        padding: 16px 12px 18px 12px !important;
        height: 100vh !important;
    }

    /* Tighten Streamlit's default gap between stacked sidebar
       elements so our custom spacing values (below) are the ones
       that actually control the layout, not Streamlit's defaults. */
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
        gap: 0 !important;
    }

    /* ---------------- LOGO ---------------- */

    .sb-logo {
        display: flex;
        align-items: center;
        gap: 9px;
        padding: 4px 4px 22px 4px;
    }

    .sb-logo .mark {
        width: 34px;
        height: 34px;
        border-radius: 8px;
        background: #7c5cff;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(124, 92, 255, 0.32);
        flex-shrink: 0;
    }

    .sb-logo .name {
        color: #ffffff;
        font-size: 0.98rem;
        font-weight: 700;
        letter-spacing: -0.01em;
    }

    /* ---------------- NAV: ACTIVE PILL (Overview) ---------------- */

    .sb-nav-active {
        display: flex;
        align-items: center;
        gap: 0;
        background: #1f2a3d;
        color: #ffffff;
        border-radius: 9px;
        padding: 9px 11px;
        margin-bottom: 2px;
        font-size: 0.84rem;
        font-weight: 600;
        cursor: default;
    }

    /* Fixed-width icon slot — same as material icon area in buttons */
    .sb-nav-active .nav-icon {
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        margin-right: 10px;
    }

    .sb-nav-active .nav-icon svg {
        display: block;
    }

    /* ---------------- NAV: BUTTON ITEMS (Documents, Chat, Logout) ----------- */

    /* Hit every selector Streamlit generates for sidebar buttons */
    div[data-testid="stSidebar"] div[data-testid="stButton"] > button,
    div[data-testid="stSidebar"] div[data-testid="stButton"] > button:focus,
    div[data-testid="stSidebar"] div[data-testid="stButton"] > button:active,
    div[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind],
    div[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="secondary"],
    div[data-testid="stSidebar"] [data-baseweb="button"] {
        background: transparent !important;
        color: #8795aa !important;
        border: none !important;
        border-width: 0 !important;
        outline: none !important;
        box-shadow: none !important;
        border-radius: 9px !important;
        min-height: 38px !important;
        height: 38px !important;
        text-align: left !important;
        justify-content: flex-start !important;
        align-items: center !important;
        font-size: 0.84rem !important;
        font-weight: 500 !important;
        /* Match Overview pill: 11px left, 11px right */
        padding: 0 11px !important;
        margin-bottom: 2px !important;
        gap: 0 !important;
        width: 100% !important;
    }

    div[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover,
    div[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover[kind],
    div[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover[kind="secondary"] {
        background: #172235 !important;
        color: #ffffff !important;
        border: none !important;
        border-width: 0 !important;
        outline: none !important;
        box-shadow: none !important;
    }

    div[data-testid="stSidebar"] div[data-testid="stButton"] button p {
        text-align: left !important;
        font-size: 0.84rem !important;
        margin: 0 !important;
    }

    /* Force the Material icon and text to use the SAME fixed-width slot
       as the SVG in .sb-nav-active so all items line up at the same X. */
    div[data-testid="stSidebar"] div[data-testid="stButton"] button [data-testid="stIconMaterial"] {
        font-size: 20px !important;
        width: 20px !important;
        height: 20px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        flex-shrink: 0 !important;
        margin-right: 10px !important;
    }

    /* ---------------- SPACER / DIVIDER / PROFILE ---------------- */

    .sb-spacer {
        height: 300px;
    }

    .sb-divider {
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        margin: 2px 4px 14px 4px;
    }

    .sb-profile {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 0 4px 16px 4px;
    }

    .sb-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #273449;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #ffffff;
        font-size: 0.72rem;
        font-weight: 700;
        flex-shrink: 0;
    }

    .sb-profile-text {
        min-width: 0;
    }

    .sb-profile-name {
        color: #ffffff;
        font-size: 0.8rem;
        font-weight: 600;
        line-height: 1.3;
    }

    .sb-profile-subtitle {
        color: #65748b;
        font-size: 0.68rem;
        margin-top: 1px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 128px;
    }

    /* Logout button needs no bottom margin since it's the last item. */
    div[data-testid="stSidebar"] div[data-testid="stButton"]:last-of-type button {
        margin-bottom: 0 !important;
    }

    /* Strip default <p> margin that st.markdown adds inside sidebar —
       otherwise the logo/Overview rows get unwanted top/bottom spacing. */
    div[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] div {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Remove Streamlit's default padding on the stMarkdown wrapper in sidebar */
    div[data-testid="stSidebar"] div[data-testid="stMarkdown"] {
        padding: 0 !important;
        margin-bottom: 0 !important;
    }

    /* ---------------- MAIN CONTENT (unchanged) ---------------- */

    .welcome-title {
        color: #ffffff;
        font-size: 1.52rem;
        font-weight: 700;
        letter-spacing: -0.03em;
    }

    .welcome-subtitle {
        color: #64748b;
        font-size: 0.80rem;
        margin-top: 5px;
    }

    .stat-card {
        background: #0d1625;
        border: 1px solid #1a2739;
        border-radius: 12px;
        padding: 17px;
        min-height: 105px;
    }

    .stat-label {
        color: #71839e;
        font-size: 0.72rem;
        margin-bottom: 16px;
    }

    .stat-value {
        color: #ffffff;
        font-size: 1.55rem;
        font-weight: 700;
    }

    .quota {
        color: #64748b;
        font-size: 0.72rem;
        margin-left: 5px;
    }

    .storage-bar {
        height: 5px;
        width: 100%;
        background: #263346;
        border-radius: 99px;
        margin-top: 11px;
        overflow: hidden;
    }

    .storage-fill {
        height: 100%;
        background: #11c9e8;
        border-radius: 99px;
    }

    .panel {
        background: #0d1625;
        border: 1px solid #1a2739;
        border-radius: 12px;
        padding: 0 17px 12px 17px;
        min-height: 360px;
    }

    .panel-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        height: 61px;
        border-bottom: 1px solid #1a2739;
    }

    .panel-title {
        font-size: 0.90rem;
        font-weight: 700;
        color: #f8fafc;
    }

    .view-all {
        color: #9c6cff;
        font-size: 0.72rem;
        font-weight: 600;
    }

    .doc-row {
        display: flex;
        align-items: center;
        gap: 11px;
        padding: 12px 0;
        border-bottom: 1px solid #192436;
    }

    .pdf-icon {
        width: 31px;
        height: 31px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #151e31;
        color: #ff4d5c;
        font-size: 0.60rem;
        font-weight: 700;
        flex-shrink: 0;
    }

    .doc-name {
        color: #e5ebf5;
        font-size: 0.77rem;
        font-weight: 600;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .doc-meta {
        color: #687895;
        font-size: 0.65rem;
        margin-top: 3px;
    }

    .chat-row {
        padding: 14px 0;
        border-bottom: 1px solid #192436;
    }

    .chat-question {
        color: #dce4ef;
        font-size: 0.74rem;
        line-height: 1.45;
    }

    .chat-date {
        color: #65738a;
        font-size: 0.64rem;
        margin-top: 4px;
        text-align: right;
    }

    .empty {
        height: 285px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        color: #61728d;
        font-size: 0.75rem;
        line-height: 1.6;
    }

    button[kind="primary"] {
        background: #11c9e8 !important;
        color: #031018 !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        box-shadow: none !important;
    }

    /* Sidebar buttons must stay flat */
    section[data-testid="stSidebar"] button {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    section[data-testid="stSidebar"] button:hover {
        background: #182438 !important;
        border: none !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    # ---- Logo ---- (st.markdown so main-DOM CSS applies)
    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:9px;padding:4px 4px 22px 4px;">
            <div style="width:34px;height:34px;border-radius:8px;background:#7c5cff;
                        display:flex;align-items:center;justify-content:center;
                        box-shadow:0 4px 12px rgba(124,92,255,0.32);flex-shrink:0;">
                <svg width="18" height="20" viewBox="0 0 18 20"
                     fill="none" xmlns="http://www.w3.org/2000/svg">
                    <!-- document body (filled white) -->
                    <path d="M2 0 L12 0 L16 4 L16 18 Q16 20 14 20 L4 20 Q2 20 2 18 L2 2 Q2 0 4 0 Z"
                          fill="rgba(255,255,255,0.95)"/>
                    <!-- fold triangle -->
                    <path d="M12 0 L16 4 L12 4 Z" fill="rgba(110,75,210,0.55)"/>
                    <!-- text lines (purple rects) -->
                    <rect x="4.5" y="8" width="7.5" height="1.4" rx="0.7" fill="#7c5cff"/>
                    <rect x="4.5" y="11" width="6" height="1.4" rx="0.7" fill="#7c5cff"/>
                    <rect x="4.5" y="14" width="4.5" height="1.4" rx="0.7" fill="#7c5cff"/>
                </svg>
            </div>
            <div style="color:#ffffff;font-size:0.98rem;font-weight:700;
                        letter-spacing:-0.01em;line-height:1;">DocQuery</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Overview (active pill) ---- (st.markdown so inline styles & CSS both apply)
    st.markdown(
        """
        <div style="display:flex;align-items:center;background:#1f2a3d;
                    color:#ffffff;border-radius:9px;padding:9px 11px;
                    margin-bottom:2px;font-size:0.84rem;font-weight:600;">
            <span style="width:20px;height:20px;min-width:20px;
                          display:flex;align-items:center;justify-content:center;
                          margin-right:10px;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="#ffffff"
                     xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2.8 3 10.4V21a1 1 0 0 0 1 1h5.5a.5.5 0 0 0
                             .5-.5V15a2 2 0 0 1 2-2h0a2 2 0 0 1 2 2v6.5a.5.5
                             0 0 0 .5.5H20a1 1 0 0 0 1-1V10.4L12 2.8Z"/>
                </svg>
            </span>
            <span>Overview</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Documents ----
    if st.button(
        "Documents",
        key="sidebar_documents",
        icon=":material/description:",
        use_container_width=True,
    ):
        try:
            st.switch_page("pages/documents.py")
        except Exception:
            st.info("Documents page is not available yet.")

    # ---- Chat ----
    if st.button(
        "Chat",
        key="sidebar_chat",
        icon=":material/forum:",
        use_container_width=True,
    ):
        try:
            st.switch_page("pages/chat.py")
        except Exception:
            st.info("Chat page is not available yet.")

    # ---- Spacer ----
    st.markdown('<div style="flex:1;min-height:200px;"></div>', unsafe_allow_html=True)

    # ---- Divider + profile ----
    st.markdown(
        f"""
        <div style="border-top:1px solid rgba(255,255,255,0.08);margin:2px 4px 14px 4px;"></div>
        <div style="display:flex;align-items:center;gap:10px;padding:0 4px 16px 4px;">
            <div style="width:32px;height:32px;border-radius:50%;background:#273449;
                        display:flex;align-items:center;justify-content:center;
                        color:#ffffff;font-size:0.72rem;font-weight:700;
                        flex-shrink:0;">{html.escape(initial)}</div>
            <div style="min-width:0;">
                <div style="color:#ffffff;font-size:0.8rem;font-weight:600;
                            line-height:1.3;">{safe_name}</div>
                <div style="color:#65748b;font-size:0.68rem;margin-top:1px;
                            white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
                            max-width:128px;">{safe_subtitle}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Logout ----
    if st.button(
        "Logout",
        key="sidebar_logout",
        icon=":material/logout:",
        use_container_width=True,
    ):
        logout()


# =========================================================
# HEADER
# =========================================================

header_left, header_right = st.columns(
    [6, 1],
    gap="small",
)

with header_left:

    st.html(
        f"""
        <div>
            <div class="welcome-title">
                Welcome back, {safe_name} 👋
            </div>

            <div class="welcome-subtitle">
                Here's what's happening with your documents.
            </div>
        </div>
        """
    )

with header_right:

    st.html(
        f"""
        <div style="
            display:flex;
            justify-content:flex-end;
            align-items:center;
            padding-top:3px;
        ">
            <div style="
                width:37px;
                height:37px;
                border-radius:50%;
                background:#202b3d;
                border:1px solid #2b3748;
                display:flex;
                align-items:center;
                justify-content:center;
                color:#ffffff;
                font-size:.76rem;
                font-weight:700;
            ">
                {html.escape(initial)}
            </div>
        </div>
        """
    )


st.write("")


# =========================================================
# STATS
# =========================================================

col1, col2, col3, col4 = st.columns(
    4,
    gap="small",
)

with col1:

    st.html(
        f"""
        <div class="stat-card">
            <div class="stat-label">
                Total Documents
            </div>

            <div class="stat-value">
                {len(documents)}
            </div>
        </div>
        """
    )

with col2:

    st.html(
        f"""
        <div class="stat-card">
            <div class="stat-label">
                Questions Asked
            </div>

            <div class="stat-value">
                {questions_asked}
            </div>
        </div>
        """
    )

with col3:

    st.html(
        f"""
        <div class="stat-card">
            <div class="stat-label">
                Recent Chats
            </div>

            <div class="stat-value">
                {len(recent_chats)}
            </div>
        </div>
        """
    )

with col4:

    st.html(
        f"""
        <div class="stat-card">

            <div class="stat-label">
                Storage Used
            </div>

            <div class="stat-value">
                {html.escape(storage_label)}
                <span class="quota">
                    / 10 GB
                </span>
            </div>

            <div class="storage-bar">
                <div
                    class="storage-fill"
                    style="
                        width:{storage_percent:.1f}%;
                    "
                ></div>
            </div>

        </div>
        """
    )


st.write("")


# =========================================================
# MAIN PANELS
# =========================================================

left_col, right_col = st.columns(
    [1.45, 1],
    gap="small",
)


# =========================================================
# DOCUMENTS PANEL
# =========================================================

with left_col:

    docs_html = """
    <div class="panel">

        <div class="panel-header">

            <div class="panel-title">
                Recent Documents
            </div>

            <div class="view-all">
                View all &gt;
            </div>

        </div>
    """

    if documents:

        for document in documents[:4]:

            filename = (
                document.get("filename")
                or document.get("document_name")
                or document.get("name")
                or "Unnamed document"
            )

            status = (
                document.get("status")
                or "Unknown"
            )

            date_value = (
                document.get("created_at")
                or document.get("uploaded_at")
                or ""
            )

            date_text = format_date(
                date_value
            )

            metadata = html.escape(
                str(status)
                + (
                    f" • {date_text}"
                    if date_text
                    else ""
                )
            )

            docs_html += f"""
            <div class="doc-row">

                <div class="pdf-icon">
                    PDF
                </div>

                <div style="
                    min-width:0;
                    flex:1;
                ">

                    <div class="doc-name">
                        {html.escape(str(filename))}
                    </div>

                    <div class="doc-meta">
                        {metadata}
                    </div>

                </div>

            </div>
            """

    else:

        docs_html += """
        <div class="empty">
            <div>
                No documents uploaded yet.<br>
                Upload a PDF to get started.
            </div>
        </div>
        """

    docs_html += """
    </div>
    """

    st.html(docs_html)


# =========================================================
# CHATS PANEL
# =========================================================

with right_col:

    chats_html = """
    <div class="panel">

        <div class="panel-header">

            <div class="panel-title">
                Recent Chats
            </div>

            <div class="view-all">
                View all &gt;
            </div>

        </div>
    """

    if recent_chats:

        for chat in recent_chats[:4]:

            if isinstance(
                chat,
                dict,
            ):

                question = (
                    chat.get("question")
                    or chat.get("query")
                    or "Question"
                )

                timestamp = (
                    chat.get("created_at")
                    or chat.get("when")
                    or ""
                )

            else:

                question = str(chat)
                timestamp = ""

            chats_html += f"""
            <div class="chat-row">

                <div class="chat-question">
                    {html.escape(str(question))}
                </div>

                <div class="chat-date">
                    {html.escape(str(timestamp))}
                </div>

            </div>
            """

    else:

        chats_html += """
        <div class="empty">
            <div>
                No conversations yet.<br>
                Upload a document and start asking questions.
            </div>
        </div>
        """

    chats_html += """
    </div>
    """

    st.html(chats_html)

    st.write("")

    if st.button(
        "+ Upload Document",
        key="chat_upload_button",
        type="primary",
    ):

        try:
            st.switch_page(
                "pages/documents.py"
            )
        except Exception:
            st.info(
                "Documents page is not available yet."
            )
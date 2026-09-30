import os
import html as html_mod
import urllib.parse
from datetime import datetime

import extra_streamlit_components as stx
import requests
import streamlit as st

st.set_page_config(
    page_title="DocQuery - Documents",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# COOKIE MANAGER
# =========================================================

cookie_manager = stx.CookieManager(key="global_cookie_manager")

# =========================================================
# AUTH GUARD
# =========================================================

access_token = st.session_state.get("access_token")

if not access_token:
    try:
        if hasattr(st, "context") and hasattr(st.context, "cookies"):
            raw = st.context.cookies.get("access_token")
            if raw:
                access_token = urllib.parse.unquote(raw).strip('"\'')
        if not access_token:
            raw = cookie_manager.get("access_token")
            if raw:
                access_token = urllib.parse.unquote(str(raw)).strip('"\'')
        if access_token:
            st.session_state["access_token"] = access_token
    except Exception:
        pass

if not access_token:
    attempt = st.session_state.get("_docs_auth_attempt", 0)
    if attempt < 1:
        st.session_state["_docs_auth_attempt"] = attempt + 1
        import time
        time.sleep(0.3)
        st.rerun()
    st.session_state.pop("_docs_auth_attempt", None)
    st.switch_page("pages/login.py")
    st.stop()

st.session_state.pop("_docs_auth_attempt", None)

# =========================================================
# USER INFO
# =========================================================

user_name     = st.session_state.get("user_name", "User")
user_subtitle = st.session_state.get("user_subtitle", "")
initial       = str(user_name)[0].upper() if user_name else "U"
safe_name     = html_mod.escape(str(user_name))
safe_subtitle = html_mod.escape(str(user_subtitle))

BACKEND = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
HEADERS = {"Authorization": f"Bearer {access_token}"}

# =========================================================
# SESSION STATE
# =========================================================

if "docs_list" not in st.session_state:
    st.session_state["docs_list"] = None          # None = not yet fetched

if "docs_show_upload" not in st.session_state:
    st.session_state["docs_show_upload"] = False

if "docs_confirm_delete" not in st.session_state:
    st.session_state["docs_confirm_delete"] = None  # doc id pending deletion

if "docs_search_query" not in st.session_state:
    st.session_state["docs_search_query"] = ""

if "docs_filter" not in st.session_state:
    st.session_state["docs_filter"] = "All"

if "docs_sort" not in st.session_state:
    st.session_state["docs_sort"] = "Newest"

# =========================================================
# HELPERS
# =========================================================

def toggle_upload():
    st.session_state["docs_show_upload"] = not st.session_state.get("docs_show_upload", False)

def fetch_documents():
    try:
        r = requests.get(f"{BACKEND}/documents", headers=HEADERS, timeout=6)
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 401:
            return "UNAUTHORIZED"
        return []
    except requests.exceptions.ConnectionError:
        return "CONNECTION_ERROR"
    except Exception:
        return []


def fmt_date(iso_str):
    """Convert ISO timestamp → 'Aug 13, 2026'."""
    if not iso_str:
        return "—"
    try:
        dt = datetime.fromisoformat(str(iso_str).replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y")
    except Exception:
        return str(iso_str)[:10]


def derive_type(filename):
    """Guess a human-readable document type from the filename."""
    name = filename.lower().replace("_", " ").replace("-", " ")
    name = name.replace(".pdf", "")
    keywords = {
        "grant": "Grant Guidelines",
        "donor": "Donor Agreement",
        "impact": "Impact Report",
        "fund": "Requirements",
        "annual": "Annual Report",
        "agreement": "Agreement",
        "report": "Report",
        "requirement": "Requirements",
        "policy": "Policy",
        "budget": "Budget",
        "contract": "Contract",
        "invoice": "Invoice",
        "guide": "Guidelines",
    }
    for kw, label in keywords.items():
        if kw in name:
            return label
    # Fallback: capitalise words
    return " ".join(w.capitalize() for w in name.split()[:2])


# If we have a cached list but a document was still 'Processing', invalidate cache to get latest status
if isinstance(st.session_state.get("docs_list"), list):
    if any(d.get("status") == "Processing" for d in st.session_state["docs_list"]):
        st.session_state["docs_list"] = None

# Load documents (once per page load; refreshed after upload/delete or when checking processing)
if st.session_state["docs_list"] is None or isinstance(st.session_state["docs_list"], str):
    res = fetch_documents()
    if isinstance(res, list):
        st.session_state["docs_list"] = res
    documents_raw = res
else:
    documents_raw = st.session_state["docs_list"]


# =========================================================
# CSS
# =========================================================

st.html("""
<style>

[data-testid="stSidebarNav"],
[data-testid="stSidebarNavItems"],
[data-testid="stSidebarNavSeparator"],
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stAppDeployButton"],
footer, #MainMenu { display: none !important; }

[data-testid="stSidebarCollapseButton"] {
    visibility: hidden !important;
    pointer-events: none !important;
}

html, body, .stApp { background:#080d18 !important; color:#f8fafc !important; }

.block-container {
    max-width: 1180px !important;
    padding: 28px 34px 40px 26px !important;
}

section[data-testid="stSidebar"] {
    background:#101827 !important; border-right:1px solid #1d2838 !important;
    min-width:208px !important; max-width:208px !important; width:208px !important;
    display:flex !important; visibility:visible !important; transform:none !important;
}
section[data-testid="stSidebar"] > div:first-child {
    background:#101827 !important; padding:16px 12px 18px 12px !important;
    height:100vh !important;
}
section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] { gap:0 !important; }

/* sidebar markdown strips */
div[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p,
div[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] div { margin:0 !important; padding:0 !important; }
div[data-testid="stSidebar"] div[data-testid="stMarkdown"] { padding:0 !important; margin-bottom:0 !important; }

/* sidebar buttons */
div[data-testid="stSidebar"] div[data-testid="stButton"] > button,
div[data-testid="stSidebar"] div[data-testid="stButton"] > button:focus,
div[data-testid="stSidebar"] div[data-testid="stButton"] > button:active,
div[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind],
div[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="secondary"],
div[data-testid="stSidebar"] [data-baseweb="button"] {
    background:transparent !important; color:#8795aa !important;
    border:none !important; border-width:0 !important; outline:none !important;
    box-shadow:none !important; border-radius:9px !important;
    min-height:38px !important; height:38px !important;
    text-align:left !important; justify-content:flex-start !important;
    align-items:center !important; font-size:0.84rem !important;
    font-weight:500 !important; padding:0 11px !important;
    margin-bottom:2px !important; gap:0 !important; width:100% !important;
}
div[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover,
div[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover[kind] {
    background:#172235 !important; color:#ffffff !important;
    border:none !important; border-width:0 !important;
    outline:none !important; box-shadow:none !important;
}
div[data-testid="stSidebar"] div[data-testid="stButton"] button p { text-align:left !important; font-size:0.84rem !important; margin:0 !important; }
div[data-testid="stSidebar"] div[data-testid="stButton"] button [data-testid="stIconMaterial"] {
    font-size:20px !important; width:20px !important; height:20px !important;
    display:flex !important; align-items:center !important; justify-content:center !important;
    flex-shrink:0 !important; margin-right:10px !important;
}
div[data-testid="stSidebar"] div[data-testid="stButton"]:last-of-type button { margin-bottom:0 !important; }

/* =========================================================
   MAIN: Documents page
   ========================================================= */

.page-title  { color:#ffffff; font-size:1.45rem; font-weight:700; letter-spacing:-0.02em; }
.page-sub    { color:#64748b; font-size:0.80rem; margin-top:4px; }

/* top cards */
.top-cards   { display:flex; gap:14px; margin: 18px 0 22px 0; align-items:stretch; }

.upload-card {
    flex:0 0 220px; border:2px dashed #1f3050; border-radius:14px;
    background:#0d1625; display:flex; flex-direction:column;
    align-items:center; justify-content:center;
    padding:28px 18px; text-align:center; min-height:160px;
}
.upload-card-icon { color:#11c9e8; font-size:2rem; margin-bottom:10px; }
.upload-card-title { color:#ffffff; font-size:0.9rem; font-weight:600; margin-bottom:4px; }
.upload-card-sub   { color:#4d6480; font-size:0.74rem; }

.doc-card {
    flex:0 0 200px; border:1px solid #1a2739; border-radius:14px;
    background:#0d1625; padding:18px 16px; min-height:160px;
    display:flex; flex-direction:column; justify-content:space-between;
}
.doc-card-processing { border-color:#11c9e8; }
.doc-card-top  { display:flex; align-items:flex-start; gap:10px; }
.doc-card-icon { width:34px; height:34px; border-radius:8px; background:#0f2035;
                  display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.doc-card-name { color:#d4e0f0; font-size:0.82rem; font-weight:600; line-height:1.3;
                  overflow:hidden; display:-webkit-box; -webkit-line-clamp:2;
                  -webkit-box-orient:vertical; word-break:break-word; }
.doc-card-size { color:#4d6480; font-size:0.7rem; margin-top:2px; }
.badge-ready   { display:inline-flex; align-items:center; gap:5px;
                  background:rgba(16,185,129,0.12); color:#10b981;
                  border-radius:20px; padding:3px 9px; font-size:0.7rem; font-weight:600; }
.badge-proc    { background:rgba(17,201,232,0.10); color:#11c9e8;
                  border-radius:20px; padding:3px 9px; font-size:0.7rem; font-weight:600;
                  display:inline-block; }
.badge-fail    { background:rgba(239,68,68,0.10); color:#ef4444;
                  border-radius:20px; padding:3px 9px; font-size:0.7rem; font-weight:600;
                  display:inline-block; }

/* search/filter bar */
.toolbar-wrap { display:flex; align-items:center; gap:10px; margin-bottom:4px; }

/* table */
.doc-table-wrap {
    border:1px solid #1a2739; border-radius:12px;
    overflow:hidden; margin-top:6px;
}
.doc-table-header {
    display:grid;
    grid-template-columns: 2.4fr 1.6fr 0.7fr 1.2fr 0.9fr 1.4fr;
    padding: 9px 16px;
    background: #0d1625;
    border-bottom: 1px solid #1a2739;
}
.doc-table-header span {
    color:#4d6480; font-size:0.68rem; font-weight:700;
    text-transform:uppercase; letter-spacing:0.06em;
}
.doc-table-row {
    display:grid;
    grid-template-columns: 2.4fr 1.6fr 0.7fr 1.2fr 0.9fr 1.4fr;
    padding: 11px 16px;
    border-bottom: 1px solid #111e30;
    align-items:center;
    transition: background 0.15s;
}
.doc-table-row:last-child { border-bottom:none; }
.doc-table-row:hover { background:#0d1625; }
.doc-name {
    display:flex; align-items:center; gap:9px;
    color:#d4e0f0; font-size:0.82rem; font-weight:500;
    overflow:hidden; white-space:nowrap; text-overflow:ellipsis;
}
.doc-name-dot { width:8px; height:8px; border-radius:50%; flex-shrink:0; }
.doc-type  { color:#64748b; font-size:0.80rem; }
.doc-pages { color:#64748b; font-size:0.80rem; }
.doc-date  { color:#64748b; font-size:0.80rem; }

.action-link {
    color:#11c9e8; font-size:0.72rem; font-weight:600;
    cursor:pointer; letter-spacing:0.04em;
    text-decoration:none; padding:0 4px;
}
.action-sep { color:#1f3050; padding:0 1px; }
.action-del { color:#4d6480; }

/* Streamlit widget overrides for this page */
div[data-testid="stTextInput"] input {
    background:#0d1625 !important; border:1px solid #1a2739 !important;
    color:#f8fafc !important; border-radius:8px !important;
}
div[data-testid="stSelectbox"] > div > div {
    background:#0d1625 !important; border:1px solid #1a2739 !important;
    color:#f8fafc !important; border-radius:8px !important;
}
div[data-testid="stSelectbox"] label { color:#8795aa !important; font-size:0.78rem !important; }

/* Upload button styling */
div[data-testid="stFileUploader"] {
    background:#0d1625; border:2px dashed #1f3050;
    border-radius:12px; padding:16px;
}

/* + Upload Document button = primary-ish */
button[kind="secondary"].upload-btn-top,
.upload-trigger > button {
    background: linear-gradient(135deg,#11c9e8,#0ea5c9) !important;
    color: #080d18 !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    padding: 0 18px !important;
}

/* confirmation box */
.confirm-box {
    background:#0d1625; border:1px solid #1a2739;
    border-radius:12px; padding:22px 24px; margin:8px 0;
}
.confirm-title { color:#f8fafc; font-size:0.9rem; font-weight:600; margin-bottom:4px; }
.confirm-sub   { color:#64748b; font-size:0.78rem; margin-bottom:18px; }

</style>
""")


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    # Logo
    st.html("""
    <div style="display:flex;align-items:center;gap:9px;padding:4px 4px 22px 4px;">
        <div style="width:34px;height:34px;border-radius:8px;background:#7c5cff;
                    display:flex;align-items:center;justify-content:center;
                    box-shadow:0 4px 12px rgba(124,92,255,0.32);flex-shrink:0;">
            <svg width="18" height="20" viewBox="0 0 18 20" fill="none">
                <path d="M2 0 L12 0 L16 4 L16 18 Q16 20 14 20 L4 20 Q2 20 2 18 L2 2 Q2 0 4 0 Z"
                      fill="rgba(255,255,255,0.95)"/>
                <path d="M12 0 L16 4 L12 4 Z" fill="rgba(110,75,210,0.55)"/>
                <rect x="4.5" y="8"  width="7.5" height="1.4" rx="0.7" fill="#7c5cff"/>
                <rect x="4.5" y="11" width="6"   height="1.4" rx="0.7" fill="#7c5cff"/>
                <rect x="4.5" y="14" width="4.5" height="1.4" rx="0.7" fill="#7c5cff"/>
            </svg>
        </div>
        <div style="color:#ffffff;font-size:0.98rem;font-weight:700;
                    letter-spacing:-0.01em;line-height:1;">DocQuery</div>
    </div>
    """
    )

    # Overview
    if st.button("Overview", key="sb_overview",
                 icon=":material/home:", use_container_width=True):
        st.switch_page("pages/dashboard.py")

    # Documents — ACTIVE
    st.html("""
    <div style="display:flex;align-items:center;background:#1f2a3d;
                color:#ffffff;border-radius:9px;padding:9px 11px;
                margin-bottom:2px;font-size:0.84rem;font-weight:600;">
        <span style="width:20px;height:20px;min-width:20px;
                      display:flex;align-items:center;justify-content:center;
                      margin-right:10px;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="#ffffff">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0
                         2-2V8l-6-6zm-1 1.5L18.5 9H13V3.5zM6 20V4h5v7h7v9H6z"/>
            </svg>
        </span>
        <span>Documents</span>
    </div>
    """
    )

    # Chat
    if st.button("Chat", key="sb_chat",
                 icon=":material/forum:", use_container_width=True):
        st.switch_page("pages/chat.py")

    st.html('<div style="flex:1;min-height:200px;"></div>')

    # Profile
    st.html(f"""
    <div style="border-top:1px solid rgba(255,255,255,0.08);margin:2px 4px 14px 4px;"></div>
    <div style="display:flex;align-items:center;gap:10px;padding:0 4px 16px 4px;">
        <div style="width:32px;height:32px;border-radius:50%;background:#273449;
                    display:flex;align-items:center;justify-content:center;
                    color:#ffffff;font-size:0.72rem;font-weight:700;
                    flex-shrink:0;">{html_mod.escape(initial)}</div>
        <div style="min-width:0;">
            <div style="color:#ffffff;font-size:0.8rem;font-weight:600;
                        line-height:1.3;">{safe_name}</div>
            <div style="color:#65748b;font-size:0.68rem;margin-top:1px;
                        white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
                        max-width:128px;">{safe_subtitle}</div>
        </div>
    </div>
    """
    )

    if st.button("Logout", key="sb_logout",
                 icon=":material/logout:", use_container_width=True):
        st.session_state.pop("access_token", None)
        st.session_state.pop("user", None)
        st.session_state["logout_requested"] = True
        st.session_state["_skip_cookie_restore"] = True
        try:
            cookie_manager.delete("access_token")
        except Exception:
            pass
        st.switch_page("pages/login.py")



# =========================================================
# MAIN CONTENT
# =========================================================

# ---- Header row ----
h_left, h_right = st.columns([5, 1.5])
with h_left:
    st.html("""
    <div class="page-title">My Documents</div>
    <div class="page-sub">Manage and access your uploaded documents.</div>
    """)
with h_right:
    st.html('<div style="padding-top:4px;"></div>')
    st.button("＋ Upload Document", key="btn_show_upload", use_container_width=True, on_click=toggle_upload)

st.html('<div style="height:10px;"></div>')

# =========================================================
# ERROR STATES
# =========================================================

if documents_raw == "UNAUTHORIZED":
    st.error("Your session has expired. Please log in again.")
    st.stop()

if documents_raw == "CONNECTION_ERROR":
    st.error("Unable to connect to the server. Please make sure the backend is running.")
    st.stop()

documents = documents_raw if isinstance(documents_raw, list) else []

# =========================================================
# TOP CARDS ROW
# =========================================================

ready_docs       = [d for d in documents if d.get("status") == "Ready"]
processing_docs  = [d for d in documents if d.get("status") == "Processing"]
failed_docs      = [d for d in documents if d.get("status") == "Failed"]

# Build cards HTML
cards_html = '<div class="top-cards">'

# ---- Upload card ----
cards_html += """
<div class="upload-card">
    <div class="upload-card-icon">⬆</div>
    <div class="upload-card-title">Upload PDF</div>
    <div class="upload-card-sub">Drag &amp; drop your PDF here</div>
</div>
"""

# ---- Processing docs ----
for d in processing_docs[:2]:
    name = html_mod.escape(d["filename"])
    cards_html += f"""
    <div class="doc-card doc-card-processing">
        <div class="doc-card-top">
            <div class="doc-card-icon">
                <svg width="18" height="20" viewBox="0 0 18 20" fill="none">
                    <path d="M2 0 L12 0 L16 4 L16 18 Q16 20 14 20 L4 20 Q2 20 2 18 L2 2 Q2 0 4 0 Z"
                          fill="rgba(17,201,232,0.18)"/>
                    <path d="M12 0 L16 4 L12 4 Z" fill="rgba(17,201,232,0.25)"/>
                    <rect x="4.5" y="8"  width="7.5" height="1.3" rx="0.65" fill="#11c9e8" opacity="0.6"/>
                    <rect x="4.5" y="11" width="6"   height="1.3" rx="0.65" fill="#11c9e8" opacity="0.6"/>
                    <rect x="4.5" y="14" width="4.5" height="1.3" rx="0.65" fill="#11c9e8" opacity="0.6"/>
                </svg>
            </div>
            <div>
                <div class="doc-card-name">{name}</div>
            </div>
        </div>
        <div><span class="badge-proc">Processing…</span></div>
    </div>"""

# ---- Ready docs (up to 2) ----
for d in ready_docs[:2]:
    name = html_mod.escape(d["filename"])
    cards_html += f"""
    <div class="doc-card">
        <div class="doc-card-top">
            <div class="doc-card-icon">
                <svg width="18" height="20" viewBox="0 0 18 20" fill="none">
                    <path d="M2 0 L12 0 L16 4 L16 18 Q16 20 14 20 L4 20 Q2 20 2 18 L2 2 Q2 0 4 0 Z"
                          fill="rgba(255,255,255,0.07)"/>
                    <path d="M12 0 L16 4 L12 4 Z" fill="rgba(255,255,255,0.12)"/>
                    <rect x="4.5" y="8"  width="7.5" height="1.3" rx="0.65" fill="#4d6480"/>
                    <rect x="4.5" y="11" width="6"   height="1.3" rx="0.65" fill="#4d6480"/>
                    <rect x="4.5" y="14" width="4.5" height="1.3" rx="0.65" fill="#4d6480"/>
                </svg>
            </div>
            <div>
                <div class="doc-card-name">{name}</div>
            </div>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <span class="badge-ready">● Ready</span>
            <span style="color:#11c9e8;font-size:0.72rem;font-weight:600;cursor:pointer;">View</span>
        </div>
    </div>"""

cards_html += "</div>"
st.html(cards_html)

# =========================================================
# UPLOAD PANEL (collapsible)
# =========================================================

if st.session_state["docs_show_upload"]:
    with st.container():
        st.html("""
        <div style="background:#0d1625;border:1px solid #1a2739;border-radius:12px;
                    padding:20px 22px;margin-bottom:18px;">
            <div style="color:#ffffff;font-size:0.9rem;font-weight:600;margin-bottom:14px;">
                Upload a PDF document
            </div>
        </div>
        """)

        uploaded_file = st.file_uploader(
            "Select a PDF file",
            type=["pdf"],
            key="doc_uploader",
            label_visibility="collapsed",
        )

        if uploaded_file is not None:
            ucol1, ucol2 = st.columns([3, 1])
            with ucol1:
                st.html(
                    f'<div style="color:#8fafd4;font-size:0.82rem;">'
                    f'📄 <b>{html_mod.escape(uploaded_file.name)}</b> — '
                    f'{round(len(uploaded_file.getvalue()) / 1024, 1)} KB</div>'
                )
            with ucol2:
                if st.button("Upload", key="btn_do_upload", use_container_width=True):
                    with st.spinner("Uploading and processing…"):
                        try:
                            resp = requests.post(
                                f"{BACKEND}/documents/upload",
                                headers=HEADERS,
                                files={"file": (uploaded_file.name,
                                                uploaded_file.getvalue(),
                                                "application/pdf")},
                                timeout=120,
                            )
                            if resp.status_code == 200:
                                data = resp.json()
                                st.success(
                                    f"✅ **{html_mod.escape(data.get('filename', uploaded_file.name))}** "
                                    f"uploaded successfully!"
                                )
                                # Refresh document list
                                st.session_state["docs_list"] = None
                                st.session_state["docs_show_upload"] = False
                                st.session_state["chat_documents"] = None  # invalidate chat cache
                                st.rerun()
                            elif resp.status_code == 401:
                                st.error("Your session has expired. Please log in again.")
                            else:
                                try:
                                    detail = resp.json().get("detail", resp.text)
                                except Exception:
                                    detail = resp.text
                                st.error(f"Upload failed: {detail}")
                        except requests.exceptions.ConnectionError:
                            st.error("Unable to connect to the server. Please make sure the backend is running.")
                        except Exception as e:
                            st.error(f"Unexpected error: {e}")

# =========================================================
# DELETE CONFIRMATION
# =========================================================

if st.session_state["docs_confirm_delete"] is not None:
    del_id       = st.session_state["docs_confirm_delete"]["id"]
    del_filename = st.session_state["docs_confirm_delete"]["filename"]

    st.html(f"""
    <div class="confirm-box">
        <div class="confirm-title">Delete &ldquo;{html_mod.escape(del_filename)}&rdquo;?</div>
        <div class="confirm-sub">
            This will permanently remove the document, its text chunks, and embeddings.
            This action cannot be undone.
        </div>
    </div>
    """)

    cc1, cc2, _ = st.columns([1, 1, 5])
    with cc1:
        if st.button("Cancel", key="btn_cancel_del"):
            st.session_state["docs_confirm_delete"] = None
            st.rerun()
    with cc2:
        if st.button("Delete", key="btn_confirm_del", type="primary"):
            with st.spinner("Deleting…"):
                try:
                    resp = requests.delete(
                        f"{BACKEND}/documents/{del_id}",
                        headers=HEADERS,
                        timeout=10,
                    )
                    if resp.status_code == 200:
                        st.success(f"✅ '{del_filename}' deleted.")
                        st.session_state["docs_confirm_delete"] = None
                        st.session_state["docs_list"] = None     # refresh
                        st.session_state["chat_documents"] = None
                        st.rerun()
                    elif resp.status_code == 401:
                        st.error("Your session has expired. Please log in again.")
                    else:
                        try:
                            detail = resp.json().get("detail", resp.text)
                        except Exception:
                            detail = resp.text
                        st.error(f"Delete failed: {detail}")
                except requests.exceptions.ConnectionError:
                    st.error("Unable to connect to the server.")
                except Exception as e:
                    st.error(f"Error: {e}")

# =========================================================
# SEARCH / FILTER / SORT BAR
# =========================================================

bar_col1, bar_col2, bar_col3, bar_col4 = st.columns([3.5, 0.7, 1, 1])

with bar_col1:
    search_input = st.text_input(
        "search",
        value=st.session_state["docs_search_query"],
        placeholder="🔍  Search documents…",
        key="docs_search_input",
        label_visibility="collapsed",
    )

with bar_col2:
    do_search = st.button("Search", key="btn_search", use_container_width=True)

with bar_col3:
    filter_choice = st.selectbox(
        "Filter",
        options=["All", "Ready", "Processing", "Failed"],
        index=["All", "Ready", "Processing", "Failed"].index(
            st.session_state["docs_filter"]
        ),
        key="docs_filter_sel",
        label_visibility="collapsed",
    )

with bar_col4:
    sort_choice = st.selectbox(
        "Sort",
        options=["Newest", "Oldest", "Name A–Z", "Name Z–A"],
        index=["Newest", "Oldest", "Name A–Z", "Name Z–A"].index(
            st.session_state["docs_sort"]
        ),
        key="docs_sort_sel",
        label_visibility="collapsed",
    )

# Persist selections
st.session_state["docs_filter"] = filter_choice
st.session_state["docs_sort"]   = sort_choice

# ---- Search ----
if do_search or search_input != st.session_state.get("docs_last_search", ""):
    st.session_state["docs_last_search"] = search_input
    if search_input.strip():
        try:
            resp = requests.get(
                f"{BACKEND}/documents/search",
                params={"query": search_input.strip()},
                headers=HEADERS,
                timeout=6,
            )
            if resp.status_code == 200:
                display_docs = resp.json()
            else:
                display_docs = documents
        except Exception:
            display_docs = documents
    else:
        display_docs = documents
else:
    display_docs = documents

# ---- Filter ----
if filter_choice != "All":
    display_docs = [d for d in display_docs if d.get("status") == filter_choice]

# ---- Sort ----
if sort_choice == "Newest":
    display_docs = sorted(display_docs, key=lambda d: d.get("created_at") or "", reverse=True)
elif sort_choice == "Oldest":
    display_docs = sorted(display_docs, key=lambda d: d.get("created_at") or "")
elif sort_choice == "Name A–Z":
    display_docs = sorted(display_docs, key=lambda d: (d.get("filename") or "").lower())
elif sort_choice == "Name Z–A":
    display_docs = sorted(display_docs, key=lambda d: (d.get("filename") or "").lower(), reverse=True)

# =========================================================
# DOCUMENT TABLE
# =========================================================

st.html('<div style="height:6px;"></div>')

if not display_docs:
    st.html("""
    <div style="background:#0d1625;border:1px solid #1a2739;border-radius:12px;
                padding:48px;text-align:center;margin-top:6px;">
        <div style="font-size:2rem;margin-bottom:12px;">📭</div>
        <div style="color:#ffffff;font-size:0.9rem;font-weight:600;margin-bottom:6px;">No documents found</div>
        <div style="color:#64748b;font-size:0.80rem;">
            Upload a PDF using the button above to get started.
        </div>
    </div>
    """)
else:
    # Header
    st.html("""
    <div class="doc-table-wrap">
        <div class="doc-table-header">
            <span>NAME</span>
            <span>TYPE</span>
            <span>PAGES</span>
            <span>UPLOADED ON</span>
            <span>STATUS</span>
            <span style="text-align:right;">ACTIONS</span>
        </div>
    """)

    # Build status badge helper
    def status_badge(status):
        if status == "Ready":
            return '<span class="badge-ready">● Ready</span>'
        elif status == "Processing":
            return '<span class="badge-proc">Processing</span>'
        elif status == "Failed":
            return '<span class="badge-fail">Failed</span>'
        return f'<span style="color:#64748b;font-size:0.72rem;">{html_mod.escape(str(status))}</span>'

    rows_html = ""
    for doc in display_docs:
        doc_id   = doc["id"]
        fname    = doc.get("filename", "Unknown")
        status   = doc.get("status", "—")
        created  = fmt_date(doc.get("created_at"))
        dtype    = derive_type(fname)
        pages    = doc.get("page_count")
        pages_display = f"{pages} pg" if pages else "—"

        dot_color = "#10b981" if status == "Ready" else "#11c9e8" if status == "Processing" else "#ef4444"

        rows_html += f"""
        <div class="doc-table-row">
            <div class="doc-name">
                <div class="doc-name-dot" style="background:{dot_color};"></div>
                <span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
                    {html_mod.escape(fname)}
                </span>
            </div>
            <div class="doc-type">{html_mod.escape(dtype)}</div>
            <div class="doc-pages">{html_mod.escape(pages_display)}</div>
            <div class="doc-date">{html_mod.escape(created)}</div>
            <div>{status_badge(status)}</div>
            <div style="text-align:right;" id="actions-{doc_id}">
                <span class="action-link" id="open-{doc_id}">OPEN</span>
                <span class="action-sep">|</span>
                <span class="action-link" id="chat-{doc_id}">CHAT</span>
                <span class="action-sep">|</span>
                <span class="action-link action-del" id="del-{doc_id}">⋯</span>
            </div>
        </div>"""

    st.html(rows_html + "</div>")

    # ---- Interactive action buttons (below HTML table) ----
    st.html('<div style="height:10px;"></div>')
    st.html(
        '<div style="color:#4d6480;font-size:0.72rem;margin-bottom:6px;">'
        'Select a document action:</div>'
    )

    for doc in display_docs:
        doc_id     = doc["id"]
        fname      = doc.get("filename", "Unknown")
        doc_status = doc.get("status")
        short      = fname if len(fname) <= 28 else fname[:26] + "…"

        is_ready = (doc_status == "Ready")

        row_col1, row_col2, row_col3, row_col4 = st.columns([2.5, 0.7, 0.7, 0.7])
        with row_col1:
            st.html(
                f'<div style="color:#8fafd4;font-size:0.78rem;padding:6px 0;">'
                f'📄 {html_mod.escape(short)}</div>'
            )
        with row_col2:
            if st.button("Open", key=f"open_{doc_id}", use_container_width=True, disabled=not is_ready):
                # Clear stale caches for any previously loaded document
                old_id = st.session_state.get("viewer_document_id")
                if old_id and old_id != doc_id:
                    st.session_state.pop(f"viewer_pdf_bytes_{old_id}", None)
                st.session_state["viewer_document"] = fname
                st.session_state["viewer_document_id"] = doc_id
                st.session_state["viewer_page"] = 1
                st.session_state["viewer_return_page"] = "documents"
                st.session_state.pop("viewer_total_pages", None)    # clear cache for new doc
                st.session_state["viewer_source_section"] = "—"     # no source context from documents
                st.switch_page("pages/viewer.py")
        with row_col3:
            if st.button("Chat", key=f"chat_{doc_id}", use_container_width=True, disabled=not is_ready):
                # Pass selected document to chat page via session state
                st.session_state["chat_documents"] = None   # reset so chat re-fetches
                st.session_state["chat_preselect_doc"] = fname
                st.switch_page("pages/chat.py")
        with row_col4:
            if st.button("Delete", key=f"del_{doc_id}", use_container_width=True):

                st.session_state["docs_confirm_delete"] = {"id": doc_id, "filename": fname}
                st.rerun()

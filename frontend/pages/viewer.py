import html as html_mod
import urllib.parse

import extra_streamlit_components as stx
import requests
import streamlit as st
import streamlit.components.v1 as components

# =========================================================
# CONFIG & STATE INITIALIZATION
# =========================================================

st.set_page_config(
    page_title="DocQuery - Viewer",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================================================
# COOKIE MANAGER / AUTH GUARD
# =========================================================

cookie_manager = stx.CookieManager(key="global_cookie_manager")

access_token = st.session_state.get("access_token")

if not access_token:
    print('VIEWER INIT: No access token in session state.')
    try:
        if hasattr(st, "context") and hasattr(st.context, "cookies"):
            raw = st.context.cookies.get("access_token")
            print(f'VIEWER: st.context.cookies raw = {raw}')
            if raw:
                access_token = urllib.parse.unquote(raw).strip('"\'')
        if not access_token:
            raw = cookie_manager.get("access_token")
            print(f'VIEWER: cookie_manager raw = {raw}')
            if raw:
                access_token = urllib.parse.unquote(str(raw)).strip('"\'')
        if access_token:
            st.session_state["access_token"] = access_token
            print('VIEWER: Hydrated access token from cookies.')
    except Exception as e:
        print(f'VIEWER EXCEPTION: {e}')
        pass

if not access_token:
    attempt = st.session_state.get("_viewer_auth_attempt", 0)
    print(f'VIEWER no token. Attempt = {attempt}')
    if attempt < 1:
        st.session_state["_viewer_auth_attempt"] = attempt + 1
        import time
        time.sleep(0.3)
        print('VIEWER RERUNNING...')
        st.rerun()
    st.session_state.pop("_viewer_auth_attempt", None)
    print('VIEWER REDIRECTING TO LOGIN')
    st.switch_page("pages/login.py")
    st.stop()

st.session_state.pop("_viewer_auth_attempt", None)

BACKEND = "http://127.0.0.1:8000"
HEADERS = {"Authorization": f"Bearer {access_token}"}
print(f'VIEWER ACTIVE. Token prefix: {str(access_token)[:15]}')

# =========================================================
# DOCUMENT STATE
# =========================================================

# Read the target from the URL when available. This makes source-click
# navigation survive a fresh Streamlit page run.
query_document_id = st.query_params.get("document_id")
query_page = st.query_params.get("page")
query_return = st.query_params.get("return")

if query_document_id:
    try:
        st.session_state["viewer_document_id"] = int(query_document_id)
    except (TypeError, ValueError):
        pass

if query_page:
    try:
        st.session_state["viewer_page"] = max(1, int(query_page))
    except (TypeError, ValueError):
        pass

if query_return in {"chat", "documents"}:
    st.session_state["viewer_return_page"] = query_return

document_id   = st.session_state.get("viewer_document_id")
document_name = st.session_state.get("viewer_document", "No Document Selected")
current_page  = st.session_state.get("viewer_page", 1)
print(f'VIEWER STATE: doc_id={document_id}, name={document_name}, page={current_page}')
return_page   = st.session_state.get("viewer_return_page", "documents")
zoom          = st.session_state.get("viewer_zoom", 100)
source_section = st.session_state.get("viewer_source_section", "—")

# Safeguards
if not isinstance(current_page, int) or current_page < 1:
    current_page = 1
    st.session_state["viewer_page"] = 1

if not isinstance(zoom, int) or zoom < 50:
    zoom = 100
    st.session_state["viewer_zoom"] = 100

# -----------------------------------------------------------
# Fetch total page count from the backend document list
# -----------------------------------------------------------
total_pages = st.session_state.get("viewer_total_pages")

if total_pages is None and document_id:
    try:
        r = requests.get(f"{BACKEND}/documents", headers=HEADERS, timeout=5)
        if r.status_code == 200:
            for doc in r.json():
                if doc.get("id") == document_id:
                    total_pages = doc.get("page_count")
                    break
        if total_pages:
            st.session_state["viewer_total_pages"] = total_pages
    except Exception:
        pass

# -----------------------------------------------------------
# Fetch PDF bytes once, cache in session_state by document_id
# -----------------------------------------------------------
pdf_bytes = None
pdf_cache_key = f"viewer_pdf_bytes_{document_id}"
if document_id:
    if pdf_cache_key not in st.session_state:
        try:
            pdf_r = requests.get(
                f"{BACKEND}/documents/{document_id}/file",
                headers=HEADERS,
                timeout=10,
            )
            if pdf_r.status_code == 200:
                st.session_state[pdf_cache_key] = pdf_r.content
        except Exception:
            pass
    pdf_bytes = st.session_state.get(pdf_cache_key)

# Clamp current_page to total_pages
if total_pages and current_page > total_pages:
    current_page = total_pages
    st.session_state["viewer_page"] = current_page

# =========================================================
# NAVIGATION CALLBACKS
# =========================================================

def prev_page():
    p = st.session_state.get("viewer_page", 1)
    if p > 1:
        st.session_state["viewer_page"] = p - 1

def next_page():
    p = st.session_state.get("viewer_page", 1)
    tp = st.session_state.get("viewer_total_pages")
    if tp is None or p < tp:
        st.session_state["viewer_page"] = p + 1

def zoom_out():
    z = st.session_state.get("viewer_zoom", 100)
    if z > 50:
        st.session_state["viewer_zoom"] = z - 10

def zoom_in():
    z = st.session_state.get("viewer_zoom", 100)
    if z < 200:
        st.session_state["viewer_zoom"] = z + 10

def go_to_page(page_num):
    st.session_state["viewer_page"] = page_num

def go_back():
    st.session_state.pop("viewer_total_pages", None)
    target = f"pages/{return_page}.py"
    st.switch_page(target)

# =========================================================
# GLOBAL CSS
# =========================================================
st.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ---- Hide Streamlit chrome ---- */
section[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"] {
    display: none !important;
}
[data-testid="stHeader"], footer, #MainMenu {
    display: none !important;
}

html, body, .stApp {
    background: #080d18 !important;
    color: #f8fafc !important;
    font-family: 'Inter', sans-serif !important;
}

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ---- TOP HEADER BAR ---- */
.viewer-topbar {
    display: flex;
    align-items: center;
    background: #0d1625;
    border-bottom: 1px solid #1a2739;
    padding: 0 20px;
    height: 58px;
    position: sticky;
    top: 0;
    z-index: 100;
    gap: 12px;
}
.viewer-topbar-left {
    display: flex;
    align-items: center;
    gap: 10px;
    min-width: 0;
    flex: 1;
}
.viewer-topbar-center {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-shrink: 0;
}
.viewer-topbar-right {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
    flex: 1;
    justify-content: flex-end;
}
.pdf-title {
    color: #ffffff;
    font-weight: 600;
    font-size: 0.92rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 280px;
}
.page-indicator {
    color: #8fafd4;
    font-size: 0.85rem;
    font-weight: 600;
    padding: 0 8px;
    white-space: nowrap;
}

/* ---- Viewer toolbar buttons (all icons, nav, zoom) ---- */
div[data-testid="stButton"] button {
    background: transparent !important;
    border: 1px solid #1a2739 !important;
    color: #8fafd4 !important;
    box-shadow: none !important;
    border-radius: 6px !important;
    font-size: 0.82rem !important;
    min-height: 34px !important;
    padding: 0 10px !important;
    transition: all 0.15s ease !important;
}
div[data-testid="stButton"] button:hover {
    color: #11c9e8 !important;
    background: rgba(17, 201, 232, 0.1) !important;
    border-color: #11c9e8 !important;
}

/* ---- Primary (Back) button ---- */
button[kind="primary"],
div[data-testid="stButton"] button[kind="primary"] {
    background: #11c9e8 !important;
    color: #080d18 !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    border: none !important;
    font-size: 0.85rem !important;
}
button[kind="primary"]:hover,
div[data-testid="stButton"] button[kind="primary"]:hover {
    background: #0ea5c9 !important;
    color: #080d18 !important;
}

/* ---- Main layout ---- */
.viewer-main {
    display: flex;
    height: calc(100vh - 58px);
    overflow: hidden;
}

/* ---- LEFT PANEL ---- */
.viewer-left {
    width: 180px;
    min-width: 180px;
    background: #0d1625;
    border-right: 1px solid #1a2739;
    overflow-y: auto;
    padding-top: 16px;
}
.pages-label {
    color: #64748b;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0 14px 14px 14px;
}
.page-btn-active {
    background: #11c9e8;
    border-radius: 6px;
    padding: 7px 12px;
    margin: 2px 10px;
    color: #080d18;
    font-weight: 700;
    font-size: 0.82rem;
    cursor: default;
}
.page-btn-inactive {
    padding: 7px 12px;
    margin: 2px 10px;
    color: #8fafd4;
    font-size: 0.82rem;
    border-radius: 6px;
    cursor: pointer;
    transition: background 0.12s;
}
.page-btn-inactive:hover {
    background: rgba(17,201,232,0.08);
}

/* Page list buttons in left panel */
div.left-panel div[data-testid="stButton"] button {
    border: none !important;
    border-radius: 6px !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 7px 12px !important;
    margin: 2px 10px !important;
    width: calc(100% - 20px) !important;
    font-size: 0.82rem !important;
    min-height: 34px !important;
    color: #8fafd4 !important;
    background: transparent !important;
}
div.left-panel div[data-testid="stButton"] button:hover {
    background: rgba(17,201,232,0.08) !important;
    color: #11c9e8 !important;
    border: none !important;
}

/* ---- CENTER PANEL ---- */
.viewer-center {
    flex: 1;
    overflow-y: auto;
    background: #0f1927;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px 16px;
}

/* ---- RIGHT PANEL ---- */
.viewer-right {
    width: 240px;
    min-width: 240px;
    background: #0d1625;
    border-left: 1px solid #1a2739;
    padding: 20px 18px;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
}
.source-details-title {
    color: #ffffff;
    font-size: 0.88rem;
    font-weight: 700;
    margin-bottom: 22px;
    letter-spacing: -0.01em;
}
.meta-label {
    color: #64748b;
    font-size: 0.70rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 5px;
}
.meta-value {
    color: #f8fafc;
    font-size: 0.84rem;
    font-weight: 500;
    line-height: 1.45;
    word-break: break-word;
    margin-bottom: 22px;
}
.spacer { flex: 1; }

/* ---- Download button in right panel ---- */
div[data-testid="stDownloadButton"] button {
    background: transparent !important;
    border: 1px solid #1a2739 !important;
    color: #8fafd4 !important;
    border-radius: 7px !important;
    font-size: 0.8rem !important;
    width: 100% !important;
    margin-bottom: 12px !important;
}
div[data-testid="stDownloadButton"] button:hover {
    border-color: #11c9e8 !important;
    color: #11c9e8 !important;
    background: rgba(17,201,232,0.07) !important;
}
</style>
""")

# =========================================================
# TOP HEADER — rendered via Streamlit columns
# This is the top toolbar row
# =========================================================

page_display = f"{current_page} / {total_pages}" if total_pages else f"{current_page}"

# We'll use a single columns row for the entire toolbar
toolbar_left, toolbar_center, toolbar_right = st.columns([3, 3, 3], vertical_alignment="center")

with toolbar_left:
    st.html(
        f'<div style="display:flex;align-items:center;gap:10px;padding:10px 0 10px 8px;">'
        f'<span style="font-size:1.1rem;">📄</span>'
        f'<span class="pdf-title">{html_mod.escape(document_name)}</span>'
        f'</div>'
    )

with toolbar_center:
    nav_c1, nav_c2, nav_c3 = st.columns([1, 2, 1], vertical_alignment="center")
    with nav_c1:
        st.button(
            "‹",
            key="btn_prev",
            on_click=prev_page,
            use_container_width=True,
            disabled=(current_page <= 1),
            help="Previous page",
        )
    with nav_c2:
        st.html(
            f'<div style="text-align:center;color:#8fafd4;font-size:0.88rem;'
            f'font-weight:600;padding:6px 0;">{page_display}</div>'
        )
    with nav_c3:
        st.button(
            "›",
            key="btn_next",
            on_click=next_page,
            use_container_width=True,
            disabled=(total_pages is not None and current_page >= total_pages),
            help="Next page",
        )

with toolbar_right:
    rc1, rc2, rc3, rc4 = st.columns([1, 1, 1, 1], vertical_alignment="center")
    with rc1:
        st.button(
            "🔍−",
            key="btn_zoom_out",
            on_click=zoom_out,
            use_container_width=True,
            disabled=(zoom <= 50),
            help="Zoom out",
        )
    with rc2:
        st.html(
            f'<div style="text-align:center;color:#8fafd4;font-size:0.75rem;'
            f'padding:4px 0;">{zoom}%</div>'
        )
    with rc3:
        st.button(
            "🔍+",
            key="btn_zoom_in",
            on_click=zoom_in,
            use_container_width=True,
            disabled=(zoom >= 200),
            help="Zoom in",
        )
    with rc4:
        # Download icon button in header (uses cached PDF bytes)
        if document_id and pdf_bytes:
            st.download_button(
                label="⬇",
                data=pdf_bytes,
                file_name=document_name,
                mime="application/pdf",
                use_container_width=True,
                key="btn_download_top",
                help="Download PDF",
            )
        else:
            st.html('<div style="color:#4d6480;font-size:0.75rem;text-align:center;padding:6px;">⬇</div>')

# Divider
st.html('<div style="border-bottom:1px solid #1a2739;margin:0;"></div>')

# =========================================================
# MAIN VIEWER LAYOUT — 3 columns
# =========================================================

main_l, main_c, main_r = st.columns([1.6, 7, 2.4], gap="small")

# ─────────────────────────────────────────────
# LEFT PANEL — PAGES
# ─────────────────────────────────────────────
with main_l:
    st.html(
        '<div style="padding:18px 14px 10px 14px;color:#64748b;font-size:0.72rem;'
        'font-weight:700;letter-spacing:0.08em;text-transform:uppercase;">PAGES</div>'
    )

    if total_pages:
        # Show a window of pages around the current page
        half_win = 5
        start_p = max(1, current_page - half_win)
        end_p   = min(total_pages, start_p + half_win * 2)
        # Adjust start if near end
        if end_p - start_p < half_win * 2:
            start_p = max(1, end_p - half_win * 2)

        for p in range(start_p, end_p + 1):
            if p == current_page:
                st.html(f"""
                <div style="
                    background:#11c9e8;
                    border-radius:6px;
                    padding:7px 12px;
                    margin:2px 10px;
                    color:#080d18;
                    font-weight:700;
                    font-size:0.82rem;
                    cursor:default;
                ">Page {p}</div>
                """)
            else:
                st.button(
                    f"Page {p}",
                    key=f"go_page_{p}",
                    on_click=go_to_page,
                    args=(p,),
                    use_container_width=True,
                )
    else:
        st.html(
            '<div style="color:#4d6480;font-size:0.78rem;padding:8px 16px;">Loading…</div>'
        )

# ─────────────────────────────────────────────
# CENTER PANEL — PDF VIEWER
# ─────────────────────────────────────────────
with main_c:
    if not document_id:
        st.html("""
        <div style="
            display:flex;align-items:center;justify-content:center;
            min-height:70vh;color:#64748b;font-size:0.9rem;flex-direction:column;
            gap:12px;
        ">
            <div style="font-size:2.5rem;">📄</div>
            <div>No document selected. Go back and click <b>Open</b> on a document.</div>
        </div>
        """)
    else:
        token_param = urllib.parse.quote(access_token, safe="")
        pdf_url = (
            f"{BACKEND}/documents/{document_id}/file"
            f"?token={token_param}#page={int(current_page)}"
        )

        zoom_pct = zoom / 100.0
        iframe_height = int(820 * zoom_pct)
        iframe_height = max(450, min(iframe_height, 1500))

        # Page label at top
        st.html(
            f'<div style="color:#64748b;font-size:0.75rem;text-align:center;'
            f'margin-bottom:10px;">Page {current_page}'
            + (f' of {total_pages}' if total_pages else '')
            + '</div>'
        )

        st.markdown(
            f"""
            <iframe
                src="{pdf_url}"
                width="100%"
                height="{iframe_height}"
                style="
                    border:none;
                    border-radius:8px;
                    background:#ffffff;
                    box-shadow:0 8px 32px rgba(0,0,0,0.5);
                "
                title="DocQuery PDF Viewer">
            </iframe>
            """,
            unsafe_allow_html=True
)
        # Page number at bottom
        if total_pages:
            st.html(
                f'<div style="color:#64748b;font-size:0.72rem;text-align:center;'
                f'margin-top:10px;padding-bottom:20px;">Page {current_page} of {total_pages}</div>'
            )

# ─────────────────────────────────────────────
# RIGHT PANEL — SOURCE DETAILS
# ─────────────────────────────────────────────
with main_r:
    st.html(
        '<div style="padding:20px 0 0 0;">'
        '<div style="color:#ffffff;font-size:0.9rem;font-weight:700;'
        'margin-bottom:22px;letter-spacing:-0.01em;">Source Details</div>'
        '</div>'
    )

    st.html(f"""
    <div style="margin-bottom:20px;">
        <div class="meta-label">Document</div>
        <div class="meta-value">{html_mod.escape(document_name)}</div>
    </div>

    <div style="margin-bottom:20px;">
        <div class="meta-label">Page</div>
        <div class="meta-value">{current_page}{f' / {total_pages}' if total_pages else ''}</div>
    </div>

    <div style="margin-bottom:20px;">
        <div class="meta-label">Section</div>
        <div class="meta-value">{html_mod.escape(str(source_section)) if source_section and source_section != '—' else '—'}</div>
    </div>
    """)

    # Spacer to push back button to bottom
    st.html('<div style="flex:1;min-height:40px;"></div>')

    # ── Back button ──
    btn_label = "← Back to Chat" if return_page == "chat" else "← Back to Documents"
    if st.button(btn_label, key="btn_back_action", type="primary", use_container_width=True):
        go_back()

import html
import urllib.parse
import os 
import extra_streamlit_components as stx
import requests
import streamlit as st

st.set_page_config(
    page_title="DocQuery - Chat",
    page_icon="💬",
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
    attempt = st.session_state.get("_chat_auth_attempt", 0)
    if attempt < 1:
        st.session_state["_chat_auth_attempt"] = attempt + 1
        st.rerun()
    st.session_state.pop("_chat_auth_attempt", None)
    st.switch_page("pages/login.py")
    st.stop()

st.session_state.pop("_chat_auth_attempt", None)

# =========================================================
# USER INFO
# =========================================================

user_name = st.session_state.get("user_name", "User")
user_subtitle = st.session_state.get("user_subtitle", "")
initial = str(user_name)[0].upper() if user_name else "U"
safe_name = html.escape(str(user_name))
safe_subtitle = html.escape(str(user_subtitle))

BACKEND = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
HEADERS = {"Authorization": f"Bearer {access_token}"}

# =========================================================
# SESSION STATE — chat history + document list cache
# =========================================================

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "chat_documents" not in st.session_state:
    st.session_state["chat_documents"] = None   # None = not yet fetched

if "chat_pending_question" not in st.session_state:
    st.session_state["chat_pending_question"] = None  # queued from suggestion button


# =========================================================
# HELPER — load user's documents (once per session)
# =========================================================

def load_documents():
    if st.session_state["chat_documents"] is not None:
        return st.session_state["chat_documents"]
    try:
        r = requests.get(f"{BACKEND}/documents", headers=HEADERS, timeout=5)
        if r.status_code == 200:
            # Only show Ready documents; include document ID for viewer navigation
            docs = [d for d in r.json() if d.get("status") == "Ready"]
            st.session_state["chat_documents"] = docs
            return docs
        return []
    except Exception:
        return []


# =========================================================
# CSS
# =========================================================

st.markdown("""
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

html, body, .stApp {
    background: #080d18 !important;
    color: #f8fafc !important;
}

.block-container {
    max-width: 900px !important;
    padding: 28px 32px 0 28px !important;
}

section[data-testid="stSidebar"] {
    background: #101827 !important;
    border-right: 1px solid #1d2838 !important;
    min-width: 208px !important; max-width: 208px !important;
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

section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] { gap: 0 !important; }

/* ---- sidebar markdown strips ---- */
div[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p,
div[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] div { margin:0 !important; padding:0 !important; }
div[data-testid="stSidebar"] div[data-testid="stMarkdown"] { padding:0 !important; margin-bottom:0 !important; }

/* ---- sidebar buttons ---- */
div[data-testid="stSidebar"] div[data-testid="stButton"] > button,
div[data-testid="stSidebar"] div[data-testid="stButton"] > button:focus,
div[data-testid="stSidebar"] div[data-testid="stButton"] > button:active,
div[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind],
div[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="secondary"],
div[data-testid="stSidebar"] [data-baseweb="button"] {
    background: transparent !important; color: #8795aa !important;
    border: none !important; border-width: 0 !important; outline: none !important;
    box-shadow: none !important; border-radius: 9px !important;
    min-height: 38px !important; height: 38px !important;
    text-align: left !important; justify-content: flex-start !important;
    align-items: center !important; font-size: 0.84rem !important;
    font-weight: 500 !important; padding: 0 11px !important;
    margin-bottom: 2px !important; gap: 0 !important; width: 100% !important;
}

div[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover,
div[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover[kind],
div[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover[kind="secondary"] {
    background: #172235 !important; color: #ffffff !important;
    border: none !important; border-width: 0 !important;
    outline: none !important; box-shadow: none !important;
}

div[data-testid="stSidebar"] div[data-testid="stButton"] button p {
    text-align: left !important; font-size: 0.84rem !important; margin: 0 !important;
}

div[data-testid="stSidebar"] div[data-testid="stButton"] button [data-testid="stIconMaterial"] {
    font-size: 20px !important; width: 20px !important; height: 20px !important;
    display: flex !important; align-items: center !important;
    justify-content: center !important; flex-shrink: 0 !important;
    margin-right: 10px !important;
}

div[data-testid="stSidebar"] div[data-testid="stButton"]:last-of-type button {
    margin-bottom: 0 !important;
}

/* =========================================================
   CHAT AREA
   ========================================================= */

.chat-header-row {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 6px;
}

.chat-title  { color:#ffffff; font-size:1.38rem; font-weight:700; letter-spacing:-0.02em; }
.chat-sub    { color:#64748b; font-size:0.80rem; margin-top:3px; }

/* doc selector label */
div[data-testid="stSelectbox"] label { color:#8795aa !important; font-size:0.78rem !important; }

/* empty state */
.empty-state {
    background: #0d1625; border:1px solid #1a2739; border-radius:14px;
    padding: 56px 24px; text-align:center; margin: 16px 0 18px 0;
}
.empty-icon  { font-size:2.2rem; margin-bottom:14px; }
.empty-title { color:#ffffff; font-size:1rem; font-weight:600; margin-bottom:8px; }
.empty-sub   { color:#64748b; font-size:0.80rem; margin-bottom:24px; line-height:1.6; }
.suggestion-chips { display:flex; flex-wrap:wrap; gap:8px; justify-content:center; }
.chip {
    background:#111e30; border:1px solid #1f3050; border-radius:20px;
    color:#8fafd4; font-size:0.74rem; padding:5px 13px; cursor:pointer;
}

/* user message */
.msg-user {
    display:flex; justify-content:flex-end; margin-bottom:16px;
}
.msg-user-bubble {
    background:#1a2d4a; border:1px solid #1f3a5c;
    border-radius:14px 14px 4px 14px;
    padding:12px 16px; max-width:70%;
    color:#dce8f8; font-size:0.88rem; line-height:1.55;
}
.msg-user-role { text-align:right; color:#4d7aad; font-size:0.68rem; margin-top:5px; }

/* assistant message */
.msg-bot {
    margin-bottom:6px;
}
.msg-bot-bubble {
    background:#0d1625; border:1px solid #1a2739;
    border-radius:4px 14px 14px 14px;
    padding:14px 18px; color:#d4e0f0;
    font-size:0.88rem; line-height:1.65;
}
.msg-bot-role { color:#11c9e8; font-size:0.68rem; margin-bottom:6px; font-weight:600; }

/* sources */
.sources-wrap {
    margin: 8px 0 18px 0;
    display:flex; flex-wrap:wrap; gap:7px;
}
.source-chip {
    display:flex; align-items:center; gap:5px;
    background:#0d1625; border:1px solid #1a2739;
    border-radius:8px; padding:5px 10px;
    font-size:0.7rem; color:#64748b;
}
.source-doc  { color:#8fafd4; font-weight:500; }
.source-page { color:#4d6480; }

/* chat input area override */
div[data-testid="stChatInput"] textarea {
    background: #0d1625 !important;
    border: 1px solid #1a2739 !important;
    color: #f8fafc !important;
    border-radius: 10px !important;
}
div[data-testid="stChatInput"] textarea::placeholder { color: #4d6070 !important; }
div[data-testid="stChatInput"] button {
    background: #11c9e8 !important;
    border-radius: 8px !important; border: none !important;
}

/* clear button — small, unobtrusive */
div[data-testid="stButton"].clear-btn > button {
    background: transparent !important;
    border: 1px solid #1f3050 !important;
    color: #4d7aad !important;
    font-size: 0.72rem !important;
    padding: 4px 10px !important;
    height: auto !important;
    min-height: 28px !important;
    border-radius: 6px !important;
}
div[data-testid="stButton"].clear-btn > button:hover {
    border-color: #2d4870 !important;
    color: #8fafd4 !important;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    # Logo
    st.markdown("""
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
    """, unsafe_allow_html=True)

    # Overview
    if st.button("Overview", key="sb_overview",
                 icon=":material/home:", use_container_width=True):
        st.switch_page("pages/dashboard.py")

    # Documents
    if st.button("Documents", key="sb_documents",
                 icon=":material/description:", use_container_width=True):
        st.switch_page("pages/documents.py")

    # Chat — ACTIVE
    st.markdown("""
    <div style="display:flex;align-items:center;background:#1f2a3d;
                color:#ffffff;border-radius:9px;padding:9px 11px;
                margin-bottom:2px;font-size:0.84rem;font-weight:600;">
        <span style="width:20px;height:20px;min-width:20px;
                      display:flex;align-items:center;justify-content:center;
                      margin-right:10px;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="#ffffff">
                <path d="M20 2H4a2 2 0 0 0-2 2v18l4-4h14a2 2 0 0 0
                         2-2V4a2 2 0 0 0-2-2zm0 14H5.17L4 17.17V4h16v12z"/>
            </svg>
        </span>
        <span>Chat</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="flex:1;min-height:200px;"></div>', unsafe_allow_html=True)

    # Profile
    st.markdown(f"""
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
    """, unsafe_allow_html=True)

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
hcol_l, hcol_r = st.columns([5, 1])
with hcol_l:
    st.markdown("""
    <div class="chat-title">Chat with your documents</div>
    <div class="chat-sub">Ask questions and get answers grounded in your uploaded documents.</div>
    """, unsafe_allow_html=True)
with hcol_r:
    # small clear button aligned top-right
    st.markdown('<div style="padding-top:4px;"></div>', unsafe_allow_html=True)
    if st.button("Clear chat", key="clear_chat"):
        st.session_state["chat_history"] = []
        st.rerun()

st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)

# ---- Document selector ----
documents = load_documents()

# Remove 'All Documents' to force strict document grounding per instructions
doc_options = [d["filename"] for d in documents]

# Honour pre-selection from the Documents page "Chat" button
preselect = st.session_state.pop("chat_preselect_doc", None)
preselect_idx = 0
if preselect and preselect in doc_options:
    preselect_idx = doc_options.index(preselect)

selected_doc_name = st.selectbox(
    "Select a document",
    options=doc_options,
    index=preselect_idx if doc_options else None,
    key="selected_doc",
)

# Resolve document_id from selected filename
selected_doc_id = None
if selected_doc_name:
    for d in documents:
        if d["filename"] == selected_doc_name:
            selected_doc_id = d["id"]
            break

st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)

# ---- No documents warning ----
if not documents:
    st.warning(
        "⚠️ No ready documents found. Upload a document first to start asking questions.",
        icon=None,
    )

# =========================================================
# RENDER CHAT HISTORY
# =========================================================

SUGGESTIONS = [
    "What are the reporting requirements?",
    "What expenses are eligible?",
    "When is the report due?",
    "Who are the intended recipients?",
]


def handle_suggestion(q: str):
    """Callback: queue a suggestion question to be submitted after the rerun."""
    st.session_state["chat_pending_question"] = q


def render_history():
    history = st.session_state["chat_history"]

    if not history:
        # Empty state with REAL Streamlit buttons for suggestion questions
        st.html("""
        <div class="empty-state">
            <div class="empty-icon">💬</div>
            <div class="empty-title">Start a conversation</div>
            <div class="empty-sub">
                Ask a question about your uploaded documents<br>and get a clear, grounded answer.
            </div>
        </div>
        """)
        # Real buttons for suggestions — one per column for horizontal layout
        s_cols = st.columns(len(SUGGESTIONS))
        for i, s in enumerate(SUGGESTIONS):
            with s_cols[i]:
                st.button(
                    f'\u201c{s}\u201d',
                    key=f"suggestion_{i}",
                    use_container_width=True,
                    on_click=handle_suggestion,
                    args=(s,),
                )
        return

    for msg_idx, msg in enumerate(history):
        role = msg["role"]
        content = html.escape(msg["content"])

        if role == "user":
            st.markdown(f"""
            <div class="msg-user">
                <div>
                    <div class="msg-user-bubble">{content}</div>
                    <div class="msg-user-role">You</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        else:  # assistant
            st.markdown(f"""
            <div class="msg-bot">
                <div class="msg-bot-role">DocQuery</div>
                <div class="msg-bot-bubble">{content}</div>
            </div>
            """, unsafe_allow_html=True)

            # Sources — real buttons that navigate to Viewer with correct document_id
            sources = msg.get("sources", [])
            if sources:
                # Build a map from filename -> document_id from loaded documents
                loaded_docs = st.session_state.get("chat_documents") or []
                fname_to_id = {d["filename"]: d["id"] for d in loaded_docs}

                num_sources = len(sources)
                src_cols = st.columns(min(num_sources, 4))
                for i, s in enumerate(sources):
                    doc_fname = s.get("document") or "Unknown"
                    page_info = s.get("page")
                    label_str = f"\U0001F4C4 {doc_fname}"
                    if page_info:
                        label_str += f" \u00b7 Page {page_info}"

                    doc_id = fname_to_id.get(doc_fname)

                    with src_cols[i % 4]:
                        b_key = f"btn_src_{msg_idx}_{i}"

                        if st.button(
                            label_str,
                            key=b_key,
                            help="Verify in Document Viewer",
                        ):
                            if doc_id is not None:
                                st.session_state["viewer_document_id"] = int(doc_id)
                                st.session_state["viewer_document"] = doc_fname
                                st.session_state["viewer_page"] = int(page_info) if page_info else 1
                                st.session_state["viewer_return_page"] = "chat"
                                
                                st.query_params["document_id"] = str(int(doc_id))
                                st.query_params["page"] = str(page_info) if page_info else "1"
                                st.query_params["return"] = "chat"
                                
                                st.switch_page("pages/viewer.py")


render_history()

# =========================================================
# CHAT INPUT + QUERY
# =========================================================

# Suggestion buttons store a pending question in session_state.
# We pop it here and merge with typed input (pending takes priority this rerun).
pending = st.session_state.pop("chat_pending_question", None)
question = st.chat_input("Ask something about your documents…")

# Use pending suggestion if no typed question exists
if pending and not question:
    question = pending

if question:
    question = question.strip()
    if not question:
        st.stop()

    if not documents:
        st.error("Upload a document first to start asking questions.")
        st.stop()
        
    if not selected_doc_id:
        st.error("Please select a document to ask questions.")
        st.stop()

    # Append user message
    st.session_state["chat_history"].append({
        "role": "user",
        "content": question,
    })

    # Call backend — exactly once
    with st.spinner("Searching your document…"):
        try:
            resp = requests.post(
                f"{BACKEND}/query",
                json={
                    "question": question,
                    "document_id": selected_doc_id
                },
                headers=HEADERS,
                timeout=60,
            )

            if resp.status_code == 200:
                data = resp.json()
                answer  = data.get("answer", "No answer returned.")
                sources = data.get("sources", [])

                st.session_state["chat_history"].append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                })

            elif resp.status_code == 401:
                st.session_state["chat_history"].append({
                    "role": "assistant",
                    "content": "Your session has expired. Please log in again.",
                    "sources": [],
                })

            elif resp.status_code == 500:
                st.session_state["chat_history"].append({
                    "role": "assistant",
                    "content": "Something went wrong while processing your question. Please try again.",
                    "sources": [],
                })

            else:
                st.session_state["chat_history"].append({
                    "role": "assistant",
                    "content": f"Unexpected error ({resp.status_code}). Please try again.",
                    "sources": [],
                })

        except requests.exceptions.ConnectionError:
            st.session_state["chat_history"].append({
                "role": "assistant",
                "content": "Unable to connect to the server. Please make sure the backend is running.",
                "sources": [],
            })

        except requests.exceptions.Timeout:
            st.session_state["chat_history"].append({
                "role": "assistant",
                "content": "The request timed out. Please try again.",
                "sources": [],
            })

        except Exception as e:
            st.session_state["chat_history"].append({
                "role": "assistant",
                "content": "An unexpected error occurred. Please try again.",
                "sources": [],
            })

    st.rerun()

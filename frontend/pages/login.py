import streamlit as st
import requests
import textwrap

st.set_page_config(
    page_title="DocQuery - Login",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

def inject_login_css():
    css = """
    <style>
    @keyframes float-whole {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }
    @keyframes pulse-ring {
        0%, 100% { opacity: 1; filter: brightness(1); }
        50% { opacity: 0.6; filter: brightness(1.2); }
    }
    @keyframes pulse-lock {
        0%, 100% { transform: scale(1); filter: drop-shadow(0 0 2px rgba(0,216,255,0.1)); }
        50% { transform: scale(1.03); filter: drop-shadow(0 0 8px rgba(0,216,255,0.6)); }
    }
    @keyframes float-card-top {
        0%, 100% { transform: rotate(10deg) translateY(0); }
        50% { transform: rotate(10deg) translateY(-4px); }
    }
    @keyframes float-card-bottom {
        0%, 100% { transform: rotate(-10deg) translateY(0); }
        50% { transform: rotate(-10deg) translateY(-4px); }
    }
    @media (prefers-reduced-motion: reduce) {
        .visual-stage, .outer-ring, .inner-ring, .center-lock-icon svg, .float-top, .float-bottom {
            animation: none !important;
        }
    }

    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    #MainMenu, header, footer { 
        visibility: hidden !important; 
        display: none !important; 
    }

    /* Prevent Scrollbars */
    html, body {
        overflow-x: hidden !important;
        background: #080c16 !important;
    }

    .stApp {
        background: #080c16 !important;
        color: #f8fafc !important;
        overflow-x: hidden !important;
    }

    /* Centered Viewport Container */
    [data-testid="stMain"] {
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        min-height: 100vh !important;
        padding: 20px 16px !important;
        box-sizing: border-box !important;
        overflow-x: hidden !important;
    }

    .block-container {
        max-width: 1050px !important;
        width: 100% !important;
        padding: 0 !important;
        margin: auto !important;
    }

    /* Main Container (Flat Two Columns, No Floating Card Border) */
    .login-stage {
        width: 100%;
    }

    .login-stage > div[data-testid="stHorizontalBlock"] {
        width: 100% !important;
        min-height: 580px !important;
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        align-items: stretch !important;
        gap: 0 !important;
    }

    /* Left 50% Column */
    .login-stage > div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) {
        width: 50% !important;
        flex: 1 1 50% !important;
        background: transparent !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        padding: 24px 44px 24px 24px !important;
        box-sizing: border-box !important;
    }

    /* Right 50% Column with Exact Center Vertical Divider */
    .login-stage div[data-testid="stHorizontalBlock"] > div:nth-child(2),
    .login-stage > div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) {
        width: 50% !important;
        flex: 1 1 50% !important;
        background: transparent !important;
        border-left: 1px solid rgba(255, 255, 255, 0.12) !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        position: relative !important;
        overflow: hidden !important;
        padding: 24px 24px 24px 44px !important;
        box-sizing: border-box !important;
    }

    /* Form Container Width */
    .form-box {
        width: 100%;
        max-width: 380px;
        margin: 0 auto;
    }

    /* Typography */
    .login-header {
        font-size: 1.6rem;
        font-weight: 700;
        margin-bottom: 6px;
        color: #ffffff;
        letter-spacing: -0.015em;
    }

    .login-subtitle {
        color: #64748b;
        font-size: 0.82rem;
        margin-bottom: 24px;
        font-weight: 400;
    }

    /* Dark Navy Inputs with Subtle Borders */
    div[data-testid="stTextInput"] {
        margin-bottom: 14px !important;
    }

    div[data-testid="stTextInput"] label {
        color: #94a3b8 !important;
        font-weight: 500 !important;
        font-size: 0.76rem !important;
        margin-bottom: 6px !important;
    }

    div[data-testid="stTextInput"] div[data-baseweb="base-input"],
    div[data-testid="stTextInput"] div[data-baseweb="input"],
    div[data-testid="stTextInput"] div[data-baseweb="input"] > div,
    div[data-testid="stTextInput"] input {
        background-color: #0b1220 !important;
        color: #f8fafc !important;
    }

    div[data-testid="stTextInput"] div[data-baseweb="base-input"] {
        border: 1px solid rgba(255, 255, 255, 0.09) !important;
        border-radius: 8px !important;
        min-height: 40px !important;
        height: 40px !important;
        box-sizing: border-box !important;
        overflow: hidden !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }

    div[data-testid="stTextInput"] div[data-baseweb="input"] {
        border: none !important;
        border-radius: 8px !important;
        height: 100% !important;
        padding: 0 !important;
    }

    div[data-testid="stTextInput"] div[data-baseweb="base-input"]:focus-within {
        border-color: #00d8ff !important;
        box-shadow: 0 0 0 1px #00d8ff !important;
    }

    div[data-testid="stTextInput"] input {
        color: #f8fafc !important;
        font-size: 0.82rem !important;
        padding: 0 14px !important;
        height: 100% !important;
    }

    div[data-testid="stTextInput"] input::placeholder {
        color: #475569 !important;
        font-size: 0.82rem !important;
    }

    div[data-testid="InputInstructions"],
    span[data-testid="InputInstructions"] {
        display: none !important;
    }

    div[data-testid="stTextInput"] small,
    div[data-testid="stTextInput"] [class*="hint"],
    div[data-testid="stTextInput"] [class*="help"] {
        display: none !important;
        visibility: hidden !important;
    }

    div[data-testid="stTextInput"] button {
        background: transparent !important;
        border: none !important;
        color: #64748b !important;
        box-shadow: none !important;
        margin-right: 6px !important;
    }

    /* Nested Checkbox & Forgot Password Row */
    .form-box div[data-testid="stHorizontalBlock"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        min-height: auto !important;
        gap: 0 !important;
        padding: 0 !important;
        margin: 2px 0 16px 0 !important;
        align-items: center !important;
    }

    .form-box div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        min-height: auto !important;
        width: 50% !important;
        flex: 1 1 50% !important;
    }

    div[data-testid="stCheckbox"] label p {
        color: #64748b !important;
        font-size: 0.76rem !important;
        font-weight: 500 !important;
    }

    div[data-testid="stCheckbox"] div[data-baseweb="checkbox"] span {
        background-color: #0b1220 !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 4px !important;
    }

    button[kind="tertiary"] {
        background: transparent !important;
        border: none !important;
        color: #00d8ff !important;
        padding: 0 !important;
        font-size: 0.76rem !important;
        font-weight: 500 !important;
        min-height: auto !important;
    }

    button[kind="tertiary"]:hover {
        color: #38bdf8 !important;
        text-decoration: underline !important;
    }

    /* Primary Login Button */
    button[kind="primary"] {
        background: #00d8ff !important;
        color: #040914 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        min-height: 42px !important;
        height: 42px !important;
        font-size: 0.86rem !important;
        margin-top: 4px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 16px rgba(0, 216, 255, 0.25) !important;
    }

    button[kind="primary"]:hover {
        background: #14dcff !important;
        box-shadow: 0 6px 20px rgba(0, 216, 255, 0.38) !important;
        transform: translateY(-1px) !important;
    }

    /* OR Divider */
    .divider {
        display: flex;
        align-items: center;
        text-align: center;
        margin: 18px 0;
        color: #475569;
        font-size: 0.68rem;
        font-weight: 600;
        letter-spacing: 0.08em;
    }

    .divider::before, .divider::after {
        content: '';
        flex: 1;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    .divider::before { margin-right: 0.9rem; }
    .divider::after { margin-left: 0.9rem; }

    /* Google Button */
    button[kind="secondary"] {
        background: #0b1220 !important;
        color: #e2e8f0 !important;
        font-weight: 500 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
        min-height: 42px !important;
        height: 42px !important;
        font-size: 0.83rem !important;
        transition: all 0.2s ease !important;
    }

    button[kind="secondary"]:hover {
        background: #111a2c !important;
        border-color: rgba(255, 255, 255, 0.16) !important;
        color: #ffffff !important;
    }

    button[kind="secondary"]::before {
        content: url('data:image/svg+xml;utf8,<svg width="15" height="15" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg"><path fill="%23EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.73 17.74 9.5 24 9.5z"/><path fill="%234285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="%23FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/><path fill="%2334A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/></svg>');
        display: inline-block;
        vertical-align: middle;
        margin-right: 8px;
        position: relative;
        top: 1px;
    }

    /* RIGHT COLUMN ILLUSTRATION */
    .visual-wrap {
        position: relative;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
    }

    .visual-stage {
        position: relative;
        width: 300px;
        height: 300px;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: float-whole 4s ease-in-out infinite;
    }

    /* Outer Glow: Transitions from Purple on Left to Cyan on Right */
    .glow-purple-left {
        position: absolute;
        width: 200px;
        height: 200px;
        left: -15px;
        top: 45px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(168, 85, 247, 0.15) 0%, rgba(168, 85, 247, 0.05) 50%, transparent 70%);
        filter: blur(40px);
        pointer-events: none;
        z-index: 1;
    }

    .glow-cyan-right {
        position: absolute;
        width: 220px;
        height: 220px;
        right: -25px;
        top: 35px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(0, 216, 255, 0.15) 0%, rgba(0, 216, 255, 0.05) 50%, transparent 70%);
        filter: blur(40px);
        pointer-events: none;
        z-index: 1;
    }

    /* Circular Rings matching Figma */
    .outer-ring {
        position: absolute;
        width: 276px;
        height: 276px;
        border-radius: 50%;
        background-color: transparent;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='276' height='276' viewBox='0 0 276 276'%3E%3Cdefs%3E%3ClinearGradient id='o' x1='0%25' y1='0%25' x2='100%25' y2='0%25'%3E%3Cstop offset='20%25' stop-color='rgba(168,85,247,0.35)' /%3E%3Cstop offset='80%25' stop-color='rgba(0,216,255,0.35)' /%3E%3C/linearGradient%3E%3C/defs%3E%3Ccircle cx='138' cy='138' r='137' fill='none' stroke='url(%23o)' stroke-width='1.5' /%3E%3C/svg%3E");
        background-size: cover;
        z-index: 2;
        pointer-events: none;
        animation: pulse-ring 3.5s ease-in-out infinite;
    }

    .inner-ring {
        position: absolute;
        width: 205px;
        height: 205px;
        border-radius: 50%;
        border: 1px dashed rgba(0, 216, 255, 0.12);
        z-index: 2;
        animation: pulse-ring 3.5s ease-in-out infinite;
    }

    /* Center Dark Box with Lock & Accent Dots */
    .center-card {
        position: relative;
        width: 86px;
        height: 100px;
        background: #0d1526;
        border-radius: 18px;
        border: 1px solid rgba(255, 255, 255, 0.12);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 8px;
        box-shadow: 0 20px 45px rgba(0, 0, 0, 0.8), 0 0 20px rgba(0, 216, 255, 0.12);
        z-index: 5;
        white-space: normal !important;
        overflow: visible !important;
    }

    .center-lock-icon {
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .center-lock-icon svg {
        animation: pulse-lock 2.5s ease-in-out infinite;
        display: block;
        width: 44px;
        height: 44px;
    }

    .dot-indicators {
        display: flex;
        gap: 4px;
    }

    .dot-indicators span:nth-child(1) {
        width: 4px;
        height: 4px;
        background: #00d8ff;
        border-radius: 50%;
        box-shadow: 0 0 5px rgba(0, 216, 255, 0.6);
    }

    .dot-indicators span:nth-child(2) {
        width: 4px;
        height: 4px;
        background: #a855f7;
        border-radius: 50%;
        box-shadow: 0 0 5px rgba(168, 85, 247, 0.6);
    }

    .dot-indicators span:nth-child(3) {
        width: 4px;
        height: 4px;
        background: #00d8ff;
        border-radius: 50%;
        box-shadow: 0 0 5px rgba(0, 216, 255, 0.6);
    }

    /* Small Floating Document Cards */
    .float-card {
        position: absolute;
        background: #0e1728;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        padding: 6px 8px;
        display: flex;
        flex-direction: column;
        gap: 3.5px;
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.6);
        z-index: 4;
    }

    .float-top {
        top: 22px;
        right: 14px;
        width: 44px;
        transform: rotate(10deg);
        animation: float-card-top 3.5s ease-in-out infinite;
    }

    .float-bottom {
        bottom: 24px;
        left: 12px;
        width: 46px;
        transform: rotate(-10deg);
        animation: float-card-bottom 4s ease-in-out infinite;
        animation-delay: 1.5s;
    }

    .line-cyan {
        height: 2px;
        background: #00d8ff;
        border-radius: 2px;
    }

    .line-slate {
        height: 2px;
        background: #334155;
        border-radius: 2px;
    }

    /* Right Side Text Directly Below Illustration */
    .visual-title {
        font-size: 1.35rem;
        font-weight: 700;
        margin-top: 16px;
        margin-bottom: 6px;
        line-height: 1.35;
        text-align: center;
        color: #ffffff;
        letter-spacing: -0.015em;
    }

    .visual-desc {
        color: #64748b;
        font-size: 0.8rem;
        text-align: center;
        line-height: 1.45;
    }

    /* Responsive */
    @media (max-width: 820px) {
        .login-stage > div[data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            min-height: auto !important;
        }

        .login-stage > div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) {
            width: 100% !important;
            flex: 1 1 100% !important;
            padding: 30px 16px !important;
        }

        .login-stage > div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) {
            width: 100% !important;
            flex: 1 1 100% !important;
            border-left: none !important;
            border-top: 1px solid rgba(255, 255, 255, 0.08) !important;
            padding: 36px 16px !important;
        }
    }
    </style>
    """
    st.markdown(textwrap.dedent(css), unsafe_allow_html=True)


def login_page():
    inject_login_css()

    st.html('<div class="login-stage">')
    left_col, right_col = st.columns([1, 1], gap="small")

    with left_col:
        st.html('<div class="form-box">')

        st.html("""
        <div class="login-header">Welcome back! 👋</div>
        <div class="login-subtitle">Login to your account</div>
        """)

        email = st.text_input("Email address", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")

        options_left, options_right = st.columns([1, 1], vertical_alignment="center")
        with options_left:
            st.checkbox("Remember me")
        with options_right:
            st.html('<div style="display:flex; justify-content:flex-end;">')
            if st.button("Forgot password?", type="tertiary"):
                st.info("Password recovery feature coming soon.")
            st.html('</div>')

        if st.button("Login", use_container_width=True, type="primary"):
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                with st.spinner("Authenticating..."):
                    try:
                        response = requests.post(
                            "http://127.0.0.1:8000/login",
                            json={"email": email, "password": password},
                            timeout=5
                        )
                        if response.status_code == 200:
                            st.session_state["access_token"] = response.json().get("access_token")
                            st.success("Login successful!")
                        elif response.status_code == 401:
                            st.error("Invalid email or password.")
                        else:
                            st.error("Login service unavailable.")
                    except requests.exceptions.RequestException:
                        st.error("Unable to connect to the authentication server.")

        st.html('<div class="divider">OR</div>')

        if st.button("Continue with Google", use_container_width=True, type="secondary"):
            st.info("Google login coming soon.")

        st.html("""
        <div style="text-align: center; margin-top: 20px; font-size: 0.78rem; color: #64748b;">
            Don't have an account? 
            <a href="/register" target="_self" style="color: #00d8ff; text-decoration: none; font-weight: 500;">Sign up</a>
        </div>
        """)

        st.html('</div>')

    with right_col:
        st.html("""
        <div class="visual-wrap">
            <div class="visual-stage">
                <!-- Dual Purple/Cyan Glow Aura -->
                <div class="glow-purple-left"></div>
                <div class="glow-cyan-right"></div>
                
                <!-- Concentric Rings -->
                <div class="outer-ring"></div>
                <div class="inner-ring"></div>

                <!-- Top-Right Floating Document Card -->
                <div class="float-card float-top">
                    <div class="line-cyan" style="width: 100%;"></div>
                    <div class="line-slate" style="width: 65%;"></div>
                    <div class="line-slate" style="width: 85%;"></div>
                </div>

                <!-- Center Dark Box with Open Lock & Purple/Cyan Accents -->
                <div class="center-card">
                    <div class="center-lock-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                            <path d="M7 11V7a5 5 0 0 1 9.9-1"></path>
                        </svg>
                    </div>
                    <div class="dot-indicators">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>

                <!-- Bottom-Left Floating Document Card -->
                <div class="float-card float-bottom">
                    <div class="line-slate" style="width: 75%;"></div>
                    <div class="line-cyan" style="width: 100%;"></div>
                    <div class="line-slate" style="width: 50%;"></div>
                </div>
            </div>

            <div class="visual-title">
                Your documents.<br>
                Your data. <span style="color: #00d8ff;">Your control.</span>
            </div>

            <div class="visual-desc">
                We keep your data secure and private.
            </div>
        </div>
        """)

    st.html('</div>')

if __name__ == "__main__":
    login_page()
import streamlit as st
import textwrap

st.set_page_config(
    page_title="DocQuery",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------
def inject_custom_css():
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }

    #MainMenu { visibility: hidden; }
    header { visibility: hidden; }
    footer { visibility: hidden; }

    .block-container {
        max-width: 1200px !important;
        padding-top: 1.1rem !important;
        padding-bottom: 3rem !important;
    }

    .stApp {
        background: #0b1120 !important;
        color: #f8fafc !important;
    }

    /* Animations */
    @keyframes fadeUp {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    @keyframes illusEntrance {
        0% { opacity: 0; transform: scale(0.96) translateY(20px); }
        100% { opacity: 1; transform: scale(1) translateY(0); }
    }

    @keyframes docFloat {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-7px); }
    }

    @keyframes dotPulse {
        0%, 100% { opacity: 0.7; transform: scale(0.95); box-shadow: 0 0 4px rgba(0, 216, 255, 0.2); }
        50% { opacity: 1; transform: scale(1.15); box-shadow: 0 0 12px rgba(0, 216, 255, 0.6); }
    }

    @keyframes borderGlow {
        0%, 100% { box-shadow: 0 0 0 rgba(0, 216, 255, 0); border-color: rgba(148, 163, 184, 0.09); }
        50% { box-shadow: 0 0 14px rgba(0, 216, 255, 0.15); border-color: rgba(0, 216, 255, 0.35); }
    }

    @media (prefers-reduced-motion: reduce) {
        .hero-title, .hero-highlight, .hero-subtitle, button[kind="primary"], button[kind="secondary"], .hero-illus-wrapper, .illus, .ready-dot, .answer-panel {
            animation: none !important;
            transform: none !important;
            opacity: 1 !important;
        }
    }

    /* Streamlit buttons */
    button[kind="primary"] {
        background: #00d8ff !important;
        color: #07111f !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 7px !important;
        min-height: 40px !important;
        transition: all 0.25s ease !important;
        animation: fadeUp 0.6s ease-out 0.4s backwards;
    }

    button[kind="primary"]:hover {
        background: #18ddff !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 216, 255, 0.25) !important;
    }

    button[kind="secondary"] {
        background: transparent !important;
        color: #f8fafc !important;
        font-weight: 600 !important;
        border: 1px solid rgba(148, 163, 184, 0.35) !important;
        border-radius: 7px !important;
        min-height: 40px !important;
        transition: all 0.25s ease !important;
        animation: fadeUp 0.6s ease-out 0.4s backwards;
    }

    button[kind="secondary"]:hover {
        border-color: #00d8ff !important;
        color: #ffffff !important;
        transform: translateY(-2px);
    }

    /* Hero */
    .hero-wrap {
        padding-top: 3.5rem;
    }

    .hero-title {
        font-size: clamp(3.3rem, 5vw, 4.15rem);
        font-weight: 800;
        line-height: 0.98;
        letter-spacing: -0.045em;
        margin: 0;
        animation: fadeUp 0.6s ease-out backwards;
    }

    .hero-highlight {
        color: #00d8ff;
        font-size: clamp(3.3rem, 5vw, 4.15rem);
        font-weight: 800;
        line-height: 0.98;
        letter-spacing: -0.045em;
        margin: 0;
        animation: fadeUp 0.6s ease-out backwards;
    }

    .hero-subtitle {
        max-width: 500px;
        margin-top: 24px;
        color: #94a3b8;
        font-size: 1rem;
        line-height: 1.65;
        animation: fadeUp 0.6s ease-out 0.2s backwards;
    }

    /* Navbar */
    .brand {
        display: flex;
        align-items: center;
        gap: 9px;
        font-size: 1.18rem;
        font-weight: 700;
        white-space: nowrap;
    }

    .brand-icon {
        width: 31px;
        height: 31px;
        border-radius: 6px;
        background: #8b5cf6;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 15px;
        box-shadow: 0 5px 18px rgba(139, 92, 246, 0.18);
    }

    .nav-links {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 2rem;
        height: 40px;
    }

    .nav-links a {
        color: #94a3b8 !important;
        text-decoration: none !important;
        font-size: 0.88rem;
        font-weight: 500;
        transition: all 0.2s ease !important;
        display: inline-block;
    }

    .nav-links a:hover {
        color: #ffffff !important;
        transform: translateY(-1px);
    }

    /* Illustration */
    .hero-illus-wrapper {
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: illusEntrance 0.8s ease-out 0.2s backwards;
    }

    .illus {
        position: relative;
        width: 100%;
        height: 300px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: visible;
        animation: docFloat 5s ease-in-out infinite;
    }

    .doc {
        position: absolute;
        width: 335px;
        height: 225px;
        border-radius: 10px;
        border: 1px solid rgba(148, 163, 184, 0.13);
        box-shadow: 0 24px 50px rgba(0, 0, 0, 0.35);
        box-sizing: border-box;
    }

    .doc-back {
        background: #172136;
        transform: translate(28px, -13px) rotate(5deg);
        z-index: 1;
    }

    .doc-mid {
        background: #1c2940;
        transform: translate(15px, -6px) rotate(2.5deg);
        z-index: 2;
    }

    .doc-front {
        background: #202c43;
        transform: translate(0, 6px) rotate(-2.5deg);
        padding: 18px;
        z-index: 3;
        overflow: hidden;
    }

    .pdf-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .pdf-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: #8b5cf6;
        color: white !important;
        font-size: 10px;
        font-weight: 800;
        padding: 5px 7px;
        border-radius: 4px;
        text-transform: lowercase;
    }

    .file-icon {
        width: 26px;
        height: 26px;
        border-radius: 50%;
        background: rgba(255,255,255,0.10);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #cbd5e1;
        font-size: 12px;
    }

    .doc-line {
        height: 6px;
        border-radius: 5px;
        background: rgba(226, 232, 240, 0.16);
        margin-top: 14px;
    }

    .doc-line.short { width: 62%; }
    .doc-line.medium { width: 82%; }
    .doc-line.long { width: 94%; }

    .ready-row {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 13px;
    }

    .ready-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #00d8ff;
        box-shadow: 0 0 10px rgba(0, 216, 255, 0.45);
        flex: 0 0 auto;
        animation: dotPulse 2.5s ease-in-out infinite;
    }

    .ready-text {
        color: #e2e8f0;
        font-size: 10px;
        font-weight: 700;
    }

    .ready-subtext {
        color: #718096;
        font-size: 8px;
        margin-top: 2px;
    }

    .answer-panel {
        position: absolute;
        left: 18px;
        right: 18px;
        bottom: 14px;
        height: 50px;
        border-radius: 7px;
        background: #182338;
        border: 1px solid rgba(148, 163, 184, 0.09);
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 10px;
        box-sizing: border-box;
        animation: borderGlow 3.5s ease-in-out infinite;
    }

    .answer-icon {
        width: 34px;
        height: 34px;
        border-radius: 6px;
        background: #293852;
        display: flex;
        align-items: center;
        justify-content: center;
        flex: 0 0 auto;
        color: #94a3b8;
        font-size: 15px;
    }

    .answer-content {
        flex: 1;
        min-width: 0;
    }

    .answer-title {
        color: #e2e8f0;
        font-size: 10px;
        font-weight: 700;
        margin-bottom: 3px;
    }

    .answer-query {
        color: #718096;
        font-size: 8px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* Feature cards */
    .features {
        margin-top: 40px;
    }

    .feature-card {
        min-height: 130px;
        box-sizing: border-box;
        background: #111827;
        border: 1px solid rgba(148, 163, 184, 0.10);
        border-radius: 11px;
        padding: 1.2rem;
        transition: all 0.25s ease !important;
    }

    .feature-card:hover {
        transform: translateY(-4px);
        border-color: rgba(148, 163, 184, 0.3);
        background: #172033;
    }

    .feature-card:hover .feature-icon {
        box-shadow: 0 0 12px rgba(255, 255, 255, 0.08);
        transform: scale(1.05);
    }

    .feature-card:hover .cyan-symbol {
        text-shadow: 0 0 8px rgba(0, 216, 255, 0.4);
    }

    .feature-card:hover .purple-symbol {
        text-shadow: 0 0 8px rgba(168, 85, 247, 0.4);
    }

    .feature-icon {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        background: rgba(255,255,255,0.025);
        border: 1px solid rgba(148,163,184,0.10);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 0.6rem;
        transition: all 0.25s ease;
    }

    .feature-symbol {
        font-size: 20px;
        font-weight: 700;
        line-height: 1;
        transition: text-shadow 0.25s ease;
    }

    .cyan-symbol { color: #00d8ff; }
    .purple-symbol { color: #a855f7; }

    .feature-title {
        color: #f8fafc;
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 0.55rem;
    }

    .feature-desc {
        color: #94a3b8;
        font-size: 0.86rem;
        line-height: 1.55;
    }

    @media (max-width: 850px) {
        .nav-links { gap: 0.8rem; }
        .hero-wrap { padding-top: 1.5rem; }
        .illus { height: 300px; margin-top: 1rem; }
        .doc { width: 310px; }
    }
    </style>
    """
    st.markdown(textwrap.dedent(css), unsafe_allow_html=True)


# ---------------------------------------------------------
# NAVBAR
# ---------------------------------------------------------
def render_navbar():
    left, middle, login_col, start_col = st.columns(
        [1.45, 4.4, 1, 1],
        vertical_alignment="center",
    )

    with left:
        st.html("""
        <div class="brand">
            <span class="brand-icon">💬</span>
            <span>DocQuery</span>
        </div>
        """)

    with middle:
        st.html("""
        <div class="nav-links">
            <a href="#features">Features</a>
            <a href="#how-it-works">How It Works</a>
            <a href="#about">About</a>
            <a href="#pricing">Pricing</a>
        </div>
        """)

    with login_col:
        if st.button("Login", use_container_width=True, type="secondary"):
            st.info("Login page coming soon.")

    with start_col:
        if st.button("Get Started", use_container_width=True, type="primary"):
            st.info("Getting started flow coming soon.")


# ---------------------------------------------------------
# HERO
# ---------------------------------------------------------
def render_hero():
    st.html('<div class="hero-wrap"></div>')

    hero_left, hero_right = st.columns(
        [1.08, 0.92],
        vertical_alignment="center",
    )

    with hero_left:
        st.html("""
        <div>
            <div class="hero-title">
                Chat with your<br>
                documents.
            </div>

            <div class="hero-highlight">
                Get answers<br>
                you can verify.
            </div>

            <div class="hero-subtitle">
                Upload your organizational documents and ask questions in natural
                language. DocQuery finds the relevant information and shows you
                where it came from.
            </div>
        </div>
        """)

        b1, b2, empty = st.columns([1.15, 1.55, 0.8], vertical_alignment="center")

        with b1:
            if st.button(
                "Get Started",
                key="hero_start",
                use_container_width=True,
                type="primary",
            ):
                st.info("Getting started flow coming soon.")

        with b2:
            if st.button(
                "See How It Works →",
                key="hero_works",
                use_container_width=True,
                type="secondary",
            ):
                st.info("Interactive demo coming soon.")

    with hero_right:
        st.html("""
        <div class="hero-illus-wrapper">
            <div class="illus">
                <div class="doc doc-back"></div>
            <div class="doc doc-mid"></div>

            <div class="doc doc-front">
                <div class="pdf-row">
                    <span class="pdf-badge">pdf</span>
                    <span class="file-icon">▱</span>
                </div>

                <div class="doc-line long"></div>
                <div class="doc-line medium"></div>
                <div class="doc-line long"></div>

                <div class="ready-row">
                    <span class="ready-dot"></span>
                    <div>
                        <div class="ready-text">Your document is ready</div>
                        <div class="ready-subtext">Ask questions and find verified answers</div>
                    </div>
                </div>

                <div class="answer-panel">
                    <div class="answer-icon">⌕</div>
                    <div class="answer-content">
                        <div class="answer-title">Search your document</div>
                        <div class="answer-query">Ask anything about your uploaded PDF</div>
                    </div>
                </div>
                </div>
            </div>
        </div>
        """)


# ---------------------------------------------------------
# FEATURE CARDS
# ---------------------------------------------------------
def render_feature_cards():
    st.html('<div id="features" class="features"></div>')

    c1, c2, c3 = st.columns(3)

    shield = '<span class="feature-symbol cyan-symbol">◈</span>'
    ai = '<span class="feature-symbol purple-symbol">✦</span>'
    verified = '<span class="feature-symbol cyan-symbol">✓</span>'

    with c1:
        st.html(f"""
        <div class="feature-card">
            <div class="feature-icon">{shield}</div>
            <div class="feature-title">Secure &amp; Private</div>
            <div class="feature-desc">
                Your data is encrypted and always protected.
            </div>
        </div>
        """)

    with c2:
        st.html(f"""
        <div class="feature-card">
            <div class="feature-icon">{ai}</div>
            <div class="feature-title">AI-Powered</div>
            <div class="feature-desc">
                Advanced AI finds accurate answers from your docs.
            </div>
        </div>
        """)

    with c3:
        st.html(f"""
        <div class="feature-card">
            <div class="feature-icon">{verified}</div>
            <div class="feature-title">Source Verified</div>
            <div class="feature-desc">
                Every answer includes the document and page source.
            </div>
        </div>
        """)

    st.html('<div style="height: 55px;"></div>')


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
if __name__ == "__main__":
    inject_custom_css()
    render_navbar()
    render_hero()
    render_feature_cards()
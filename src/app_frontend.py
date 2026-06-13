import streamlit as st
import requests

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GMA AI — Kerala Admissions Counselor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Premium CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Global Reset ── */
html, body, [data-testid="stAppViewContainer"], [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── App Background ── */
.stApp {
    background: #080b12 !important;
    background-image:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(99,102,241,0.18) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 100%, rgba(236,72,153,0.12) 0%, transparent 60%) !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Main content area ── */
[data-testid="stMain"] {
    background: transparent !important;
}
.block-container {
    padding: 0 2rem 2rem 2rem !important;
    max-width: 860px !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(10, 12, 20, 0.95) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 2rem 1.25rem !important;
}

/* ── Header Hero ── */
.gma-hero {
    text-align: center;
    padding: 2.8rem 1rem 1.8rem 1rem;
    position: relative;
}
.gma-logo-ring {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 64px;
    height: 64px;
    border-radius: 20px;
    background: linear-gradient(135deg, #6366f1, #ec4899);
    box-shadow: 0 0 40px rgba(99,102,241,0.4), 0 0 80px rgba(236,72,153,0.15);
    font-size: 2rem;
    margin-bottom: 1rem;
    animation: pulse-glow 3s ease-in-out infinite;
}
@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 30px rgba(99,102,241,0.4), 0 0 60px rgba(236,72,153,0.1); }
    50%       { box-shadow: 0 0 50px rgba(99,102,241,0.6), 0 0 100px rgba(236,72,153,0.25); }
}
.gma-title {
    font-size: 2.8rem;
    font-weight: 900;
    letter-spacing: -0.05em;
    line-height: 1;
    background: linear-gradient(135deg, #c7d2fe 0%, #818cf8 40%, #f472b6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 0.5rem 0;
}
.gma-subtitle {
    font-size: 0.95rem;
    font-weight: 400;
    color: #64748b;
    letter-spacing: 0.01em;
    margin: 0;
}
.gma-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: 100px;
    padding: 4px 14px;
    font-size: 0.75rem;
    font-weight: 600;
    color: #818cf8;
    margin-top: 0.9rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.gma-badge::before {
    content: '';
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #4ade80;
    box-shadow: 0 0 6px #4ade80;
    animation: blink 2s ease-in-out infinite;
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.3; }
}

/* ── Divider ── */
.gma-divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.05);
    margin: 0 0 1.2rem 0;
}

/* ── Chat Messages ── */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.025) !important;
    border: 1px solid rgba(255,255,255,0.055) !important;
    border-radius: 18px !important;
    padding: 1.1rem 1.4rem !important;
    margin-bottom: 0.8rem !important;
    box-shadow: 0 2px 20px rgba(0,0,0,0.3) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
}
[data-testid="stChatMessage"]:hover {
    border-color: rgba(99,102,241,0.2) !important;
    box-shadow: 0 4px 30px rgba(99,102,241,0.08) !important;
}

/* User message accent */
[data-testid="stChatMessage"][data-testid*="user"] {
    border-left: 3px solid rgba(99,102,241,0.5) !important;
}

/* ── Message text color ── */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] td,
[data-testid="stChatMessage"] th {
    color: #cbd5e1 !important;
    font-size: 0.95rem !important;
    line-height: 1.75 !important;
}
[data-testid="stChatMessage"] strong {
    color: #e2e8f0 !important;
    font-weight: 600 !important;
}

/* ── Tables inside messages ── */
[data-testid="stChatMessage"] table {
    border-collapse: collapse !important;
    width: 100% !important;
    margin: 0.8rem 0 !important;
    font-size: 0.88rem !important;
}
[data-testid="stChatMessage"] th {
    background: rgba(99,102,241,0.15) !important;
    color: #a5b4fc !important;
    font-weight: 600 !important;
    padding: 8px 12px !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    text-align: left !important;
}
[data-testid="stChatMessage"] td {
    padding: 7px 12px !important;
    border: 1px solid rgba(255,255,255,0.04) !important;
}
[data-testid="stChatMessage"] tr:nth-child(even) td {
    background: rgba(255,255,255,0.02) !important;
}

/* ── Chat Input Box ── */
[data-testid="stChatInputContainer"] {
    background: rgba(15,17,26,0.8) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 16px !important;
    backdrop-filter: blur(16px) !important;
    box-shadow: 0 -1px 0 rgba(255,255,255,0.04), 0 8px 40px rgba(0,0,0,0.4) !important;
    transition: border-color 0.3s ease, box-shadow 0.3s ease !important;
    padding: 0.2rem 0.5rem !important;
}
[data-testid="stChatInputContainer"]:focus-within {
    border-color: rgba(99,102,241,0.45) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.08), 0 8px 40px rgba(0,0,0,0.4) !important;
}
[data-testid="stChatInputContainer"] textarea {
    color: #e2e8f0 !important;
    background: transparent !important;
    font-size: 0.95rem !important;
    font-family: 'Inter', sans-serif !important;
    caret-color: #818cf8 !important;
}
[data-testid="stChatInputContainer"] textarea::placeholder {
    color: #475569 !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] {
    color: #818cf8 !important;
}

/* ── Sidebar Stat Cards ── */
.stat-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.65rem;
    transition: border-color 0.2s;
}
.stat-card:hover {
    border-color: rgba(99,102,241,0.25);
}
.stat-label {
    font-size: 0.7rem;
    font-weight: 600;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 3px;
}
.stat-value {
    font-size: 1.05rem;
    font-weight: 700;
    color: #c7d2fe;
}
.stat-sub {
    font-size: 0.75rem;
    color: #475569;
    margin-top: 2px;
}

/* ── Sidebar Section Title ── */
.sidebar-section {
    font-size: 0.7rem;
    font-weight: 700;
    color: #334155;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 1.2rem 0 0.5rem 0;
}

/* ── Clear Chat Button ── */
.stButton > button {
    width: 100% !important;
    background: rgba(239,68,68,0.08) !important;
    border: 1px solid rgba(239,68,68,0.2) !important;
    color: #f87171 !important;
    border-radius: 10px !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    padding: 0.5rem !important;
    transition: all 0.2s ease !important;
    font-family: 'Inter', sans-serif !important;
}
.stButton > button:hover {
    background: rgba(239,68,68,0.15) !important;
    border-color: rgba(239,68,68,0.4) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.3); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: rgba(99,102,241,0.5); }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding-bottom: 1rem;">
        <div style="font-size:1.6rem; font-weight:900; background:linear-gradient(135deg,#c7d2fe,#f472b6);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent; letter-spacing:-0.03em;">
            GMA AI
        </div>
        <div style="font-size:0.72rem; color:#334155; font-weight:600;
                    text-transform:uppercase; letter-spacing:0.1em; margin-top:2px;">
            Kerala Admissions Intelligence
        </div>
    </div>
    <hr style="border:none; border-top:1px solid rgba(255,255,255,0.05); margin-bottom:1.2rem;">

    <div class="sidebar-section">System Status</div>
    <div class="stat-card">
        <div class="stat-label">AI Engine</div>
        <div class="stat-value">LLaMA 3.3 · 70B</div>
        <div class="stat-sub">via Groq Inference</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Knowledge Base</div>
        <div class="stat-value">35 Colleges</div>
        <div class="stat-sub">MBBS & BDS · Kerala</div>
    </div>
    <div class="stat-card">
        <div class="stat-label">Data Coverage</div>
        <div class="stat-value">2024 – 2025</div>
        <div class="stat-sub">KEAM Cutoff Ranks</div>
    </div>

    <div class="sidebar-section">Capabilities</div>
    <div style="font-size:0.82rem; color:#475569; line-height:2;">
        🎯 &nbsp;Rank-based admission prediction<br>
        🏥 &nbsp;College profiles & ratings<br>
        💰 &nbsp;Fee structures & hostel costs<br>
        📊 &nbsp;Safe / Moderate / Dream analysis<br>
        🗂️ &nbsp;All KEAM categories supported
    </div>

    <hr style="border:none; border-top:1px solid rgba(255,255,255,0.05); margin: 1.2rem 0;">
    """, unsafe_allow_html=True)

    if st.button("🗑️  Clear Conversation"):
        st.session_state.messages = [
            {"role": "assistant", "content": "👋 Hai! I'm GMA AI. How can I help you?"}
        ]
        st.rerun()

    st.markdown("""
    <div style="text-align:center; margin-top:1.5rem; font-size:0.7rem; color:#1e293b; line-height:1.8;">
        Built with RAG + LLaMA · Flask · FAISS<br>
        <span style="color:#312e81;">© 2025 GMA AI</span>
    </div>
    """, unsafe_allow_html=True)


# ── Main Area ─────────────────────────────────────────────────────────────────

# Hero Header
st.markdown("""
<div class="gma-hero">
    <div class="gma-logo-ring">🎓</div>
    <h1 class="gma-title">GMA AI</h1>
    <p class="gma-subtitle">Get My Admission — Kerala Medical Admissions Counselor &amp; Simulator</p>
    <div class="gma-badge">Live · AI Powered</div>
</div>
<hr class="gma-divider">
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Hai! I'm GMA AI. How can I help you?"}
    ]

# ── Render Chat History ───────────────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── Chat Input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask about cutoffs, fees, seats, college rankings, or admission chances…"):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Analyzing…"):
        try:
            history = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages[:-1]
            ]
            response = requests.post(
                "http://127.0.0.1:10000/query",
                json={"question": prompt, "history": history},
                timeout=60
            )
            response.raise_for_status()
            full_response = response.json().get("answer", "No answer found.")

        except Exception as e:
            full_response = (
                f"⚠️ **Backend connection error:** {e}\n\n"
                f"Please make sure the Flask server is running — `python src/app.py`"
            )

    with st.chat_message("assistant"):
        st.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
"""Scientific English Agents pilot web UI. Run from repository root.

    streamlit run pilot/streamlit_app.py

The original agent instructions remain under src/agents/ and src/shared/.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

from core import (
    AGENTS,
    AGENT_BY_KEY,
    DEFAULT_MODEL,
    MAX_INPUT_CHARS,
    PilotError,
    RUBRICS,
    build_system_prompt,
    call_mistral,
    make_messages,
    missing_source_files,
)

ROOT = Path(__file__).resolve().parents[1]
MAX_REQUESTS = 15  # session-level allowance, NOT a global account spending cap

st.set_page_config(
    page_title="Scientific English Agents · Pilot",
    page_icon="✳",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap');
:root {--paper:#f5f2e9;--ink:#132328;--muted:#586a6b;--teal:#0c9b91;--line:#cedbd5;}
.stApp, [data-testid="stAppViewContainer"] {background:#f5f2e9;color:var(--ink);font-family:'DM Sans',sans-serif;}
[data-testid="stSidebar"] {background:#e9eee8;border-right:1px solid #cad8d0;}
[data-testid="stSidebar"] * {font-family:'DM Sans',sans-serif;}
h1,h2,h3 {font-family:'Space Grotesk',sans-serif;letter-spacing:-.045em;}
section[data-testid="stSidebar"] .stButton button {width:100%;}
.stButton button[kind="primary"],.stFormSubmitButton button[kind="primary"] {background:#132328;color:#f9f8f2;border-radius:4px;border:0;}
.stButton button[kind="primary"]:hover,.stFormSubmitButton button[kind="primary"]:hover {background:#0c827a;color:white;}
.stTextArea textarea {background:#fffef9;color:#132328;border:1px solid #becfca;border-radius:6px;font-size:15px;}
.stAlert {border-radius:7px;}
.sea-kicker {color:#148a7f;font-size:11px;letter-spacing:.22em;font-weight:800;}
.sea-hero {background:radial-gradient(ellipse at 90% 30%,#bce6d7 0,transparent 45%),linear-gradient(120deg,#fdfcf8,#e7f0e9);border:1px solid #cadaD2;border-radius:9px;padding:28px 38px 27px;margin-bottom:25px;position:relative;overflow:hidden;}
.sea-hero:after {content:'✳';position:absolute;right:28px;top:1px;font-size:150px;line-height:1.2;color:#0c9b91;opacity:.12;}
.sea-hero h1 {font-size:clamp(32px,5vw,64px);line-height:1.02;margin:9px 0 12px;color:#132328;}
.sea-hero h1 em {font-family:'Instrument Serif',serif;font-weight:400;color:#078a80;}
.sea-hero p {max-width:700px;line-height:1.7;color:#526765;font-size:15px;}
.sea-tag {display:inline-block;border:1px solid #b6cec5;border-radius:3px;padding:5px 9px;margin:5px 7px 0 0;font-size:10px;letter-spacing:.08em;color:#315d58;font-weight:800;}
.sea-section {font:800 11px 'Space Grotesk',sans-serif;color:#147c72;letter-spacing:.15em;margin-top:24px;}
.sea-note {padding:14px 18px;border-left:3px solid #0c9b91;background:#e6efea;color:#435e5c;font-size:13px;margin:20px 0;}
.sea-card {padding:16px 18px;background:rgba(255,255,255,.7);border:1px solid #cfddd6;border-radius:6px;margin-bottom:8px;}
.sea-card strong {font:700 16px 'Space Grotesk',sans-serif;color:#193431;}
.sea-card span {display:block;font-size:12px;color:#536e69;margin-top:6px;}
@media(max-width:700px){.sea-hero{padding:22px}.sea-hero:after{font-size:110px;right:2px;top:0}}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="sea-hero">
  <div class="sea-kicker">THE AI BREAKFAST CLUB · EDUCATOR PILOT</div>
  <h1>Scientific thinking.<br><em>Human language.</em></h1>
  <p>Six evidence-informed pedagogical agents. Explore scientific communication,
  reasoning and feedback with Mistral AI. You remain in control.</p>
  <span class="sea-tag">SIX AGENTS</span>
  <span class="sea-tag">B1–C2</span>
  <span class="sea-tag">MISTRAL</span>
  <span class="sea-tag">FORMATIVE FIRST</span>
</div>
""", unsafe_allow_html=True)

missing = missing_source_files(ROOT)
if missing:
    st.error("Repository integration incomplete. The following original sources are missing:")
    st.code("\n".join(missing), language="text")
    st.stop()


def get_secret(name: str, default: str = "") -> str:
    """Read server-side Streamlit Secrets or environment variables."""
    try:
        value = st.secrets.get(name)
    except Exception:  # Streamlit raises its own exception if secrets.toml is absent
        value = None
    return str(value or os.environ.get(name, default))


api_key = get_secret("MISTRAL_API_KEY")
model = get_secret("MISTRAL_MODEL", DEFAULT_MODEL)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "requests" not in st.session_state:
    st.session_state.requests = 0
if "feedback" not in st.session_state:
    st.session_state.feedback = []
if "active_agent" not in st.session_state:
    st.session_state.active_agent = AGENTS[0].key

with st.sidebar:
    st.markdown("<p class='sea-section'>01 / THE WORKSPACE</p>", unsafe_allow_html=True)
    agent_key = st.selectbox(
        "Choose your pedagogical agent",
        options=[a.key for a in AGENTS],
        format_func=lambda key: AGENT_BY_KEY[key].label,
        index=[a.key for a in AGENTS].index(st.session_state.active_agent),
    )
    level = st.selectbox("CEFR level", ("B1", "B2", "C1", "C2"), index=1)
    field = st.selectbox("Scientific field", (
        "Life sciences", "Medicine", "Neuroscience", "Engineering",
        "Chemistry", "Physics", "Environmental science", "Other sciences",
    ))
    rubric = "Abstract /10"
    if agent_key == "assessment":
        rubric = st.selectbox("Assessment rubric", list(RUBRICS))
    if agent_key != st.session_state.active_agent:
        st.session_state.active_agent = agent_key
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.caption(f"Model: {model} · {st.session_state.requests}/{MAX_REQUESTS} requests in this browser session")
    if st.button("Clear conversation", type="secondary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.markdown("<p class='sea-section'>02 / RESPONSIBLE USE</p>", unsafe_allow_html=True)
    st.caption("Do not submit identifiable student data, patient information, unpublished sensitive research or confidential documents.")
    st.caption("Submissions are sent to the configured Mistral service. Messages remain in this browser session; no application database is configured.")

selected = AGENT_BY_KEY[agent_key]
st.markdown(f"<div class='sea-card'><strong>{selected.label}</strong><span>{selected.specialty}</span></div>", unsafe_allow_html=True)

if not api_key:
    st.warning("Mistral connection not configured. Administrator: add MISTRAL_API_KEY in Streamlit app Secrets.")
else:
    st.success("Server-side Mistral credentials configured. Live connectivity is verified on the first request.", icon="✅")

st.markdown("<div class='sea-section'>03 / LEARNING DIALOGUE</div>", unsafe_allow_html=True)
if st.session_state.messages:
    for item in st.session_state.messages:
        with st.chat_message(item["role"]):
            st.markdown(item["content"])
else:
    st.info("Start with your own scientific text or task. The agent will provide targeted guidance.")

with st.form("learner_input", clear_on_submit=True):
    submission = st.text_area(
        "Your text or question",
        placeholder=selected.example,
        max_chars=MAX_INPUT_CHARS,
        height=160,
        help="Paste a short anonymised excerpt or ask a pedagogical question.",
    )
    consent = st.checkbox(
        "I confirm this submission contains no personal or confidential information "
        "and understand it will be sent to Mistral.",
        value=False,
    )
    submitted = st.form_submit_button(
        "Send to the agent →",
        type="primary",
        disabled=(not bool(api_key) or st.session_state.requests >= MAX_REQUESTS),
    )
if submitted:
    if not consent:
        st.warning("Please confirm the data-sharing notice before sending.")
    elif not submission.strip():
        st.warning("Please enter a text or question.")
    else:
        try:
            system_prompt = build_system_prompt(ROOT, agent_key, level, field, rubric)
            messages = make_messages(system_prompt, st.session_state.messages, submission)
            st.session_state.requests += 1  # count attempts, including unsuccessful calls
            with st.spinner("The agent is preparing formative feedback…"):
                answer = call_mistral(api_key, messages, model=model)
            st.session_state.messages.extend([
                {"role": "user", "content": submission.strip()},
                {"role": "assistant", "content": answer},
            ])
            st.rerun()
        except PilotError as error:
            st.error(str(error))

st.divider()
st.markdown("<div class='sea-section'>04 / PILOT FEEDBACK</div>", unsafe_allow_html=True)
with st.expander("Evaluate your experience", expanded=False):
    with st.form("pilot_feedback", clear_on_submit=True):
        usefulness = st.slider("Pedagogical usefulness", 1, 5, 3)
        clarity = st.slider("Clarity and actionability", 1, 5, 3)
        usability = st.slider("Interface usability", 1, 5, 3)
        remark = st.text_area("Comment (optional)", max_chars=700)
        save_feedback = st.form_submit_button("Keep feedback in my session")
    if save_feedback:
        st.session_state.feedback.append({
            "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "agent": agent_key,
            "usefulness": usefulness,
            "clarity": clarity,
            "usability": usability,
            "comment": remark.strip(),
        })
        st.success("Feedback recorded in this browser session. Download it before leaving.")
    if st.session_state.feedback:
        st.download_button(
            "Download my pilot feedback (JSON)",
            data=json.dumps(st.session_state.feedback, ensure_ascii=False, indent=2),
            file_name="scientific-english-agents-feedback.json",
            mime="application/json",
            use_container_width=True,
        )
        st.caption("Feedback is not centrally collected. Share the downloaded file with the pilot coordinator.")

st.caption("Pilot build · Generated responses require professional review · No student-grade decisions without human validation.")

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

ROOT = Path(__file__).resolve().parent
MAX_REQUESTS = 15  # session-level allowance, NOT a global account spending cap

st.set_page_config(
    page_title="Scientific English Agents · Pilot",
    page_icon="✳",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap');
:root {--paper:#f5f4ed;--ink:#142a32;--muted:#52666a;--teal:#008f87;--line:#b9d3d0;}
.stApp,[data-testid="stAppViewContainer"] {
 background:radial-gradient(ellipse at 90% 0%,#d3f3ec 0,transparent 38%),linear-gradient(135deg,#f9f7f0,#edf3ed);
 color:var(--ink);font-family:'DM Sans',sans-serif;
}
.block-container{max-width:1220px;padding-top:2.1rem;padding-bottom:4rem}
[data-testid="stSidebar"] {background:linear-gradient(160deg,#e5f0e9,#dce9e7);border-right:1px solid #a9cbc5;}
[data-testid="stSidebar"] label,[data-testid="stSidebar"] p,[data-testid="stSidebar"] small,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {color:#24434a!important;}
[data-testid="stSidebar"] [data-baseweb="select"]>div{background:#fffefa!important;border:1px solid #a9c7c1!important;color:#132b32!important}
[data-testid="stSidebar"] [data-baseweb="select"] span{color:#132b32!important}
h1,h2,h3{font-family:'Space Grotesk',sans-serif;letter-spacing:-.04em;color:#122d33}
p,span,label{font-family:'DM Sans',sans-serif}
[data-testid="stMarkdownContainer"] p{line-height:1.65}
.stButton button,.stFormSubmitButton button,.stDownloadButton button{
 border-radius:13px!important;border:1px solid #8bbab2!important;
 background:linear-gradient(145deg,#ffffff,#e0eeea)!important;color:#12343a!important;
 box-shadow:0 5px 0 #9ebfba,0 9px 18px #123d3820!important;
 transition:transform .18s,box-shadow .18s,filter .18s!important;
 font-weight:750!important;min-height:46px;
}
.stButton button:hover,.stFormSubmitButton button:hover,.stDownloadButton button:hover{
 transform:translateY(-2px);box-shadow:0 7px 0 #8db8b0,0 13px 22px #123d3830!important;
 filter:saturate(1.12)
}
.stButton button:active,.stFormSubmitButton button:active{transform:translateY(4px);box-shadow:0 1px 0 #8db8b0!important}
.stFormSubmitButton button[kind="primary"],.stButton button[kind="primary"]{
 background:linear-gradient(135deg,#102d35,#007e80)!important;color:#fff!important;
 border:1px solid #09565d!important;box-shadow:0 5px 0 #06454b,0 10px 22px #0a4b4938!important
}
.stFormSubmitButton button[kind="primary"]:hover{box-shadow:0 7px 0 #06454b,0 14px 24px #0a4b4940!important}
.stTextArea textarea{background:#fffefa!important;color:#19323a!important;border:1px solid #9dbcb8!important;border-radius:12px!important;font-size:15px!important}
.stAlert{border-radius:13px!important}
[data-testid="stExpander"]{border:1px solid #a6c8c1!important;border-radius:14px!important;background:#ffffffbb}
.sea-kicker{color:#007e7d;font-size:11px;letter-spacing:.24em;font-weight:800}
.sea-hero{
 background:radial-gradient(circle at 80% 25%,#a9eee0 0,transparent 34%),
 linear-gradient(120deg,#fffdf7 0%,#e1f1eb 100%);
 border:1px solid #b5d7cf;border-radius:24px;padding:42px 46px 35px;
 margin-bottom:24px;position:relative;overflow:hidden;
 box-shadow:0 12px 32px #285f4e13, inset 0 1px #fff;
}
.sea-hero:before{content:"";position:absolute;inset:0;pointer-events:none;opacity:.16;
 background-image:linear-gradient(#4aafa522 1px,transparent 1px),linear-gradient(90deg,#4aafa522 1px,transparent 1px);
 background-size:30px 30px}
.sea-hero:after{content:'✳';position:absolute;right:40px;top:6px;font-size:200px;line-height:1.2;
 color:#008e86;opacity:.12;animation:seaSpin 24s linear infinite;pointer-events:none}
@keyframes seaSpin{to{transform:rotate(360deg)}}
.sea-hero h1{position:relative;font-size:clamp(38px,5.3vw,74px);line-height:1.03;margin:15px 0 18px;color:#102c32}
.sea-hero h1 em{font-family:'Instrument Serif',serif;font-weight:400;color:#008f87}
.sea-hero p{position:relative;max-width:720px;line-height:1.8;color:#38565b;font-size:16px}
.sea-tag{position:relative;display:inline-block;background:#ffffffb8;border:1px solid #a6cbc2;
 border-radius:7px;padding:7px 11px;margin:7px 7px 0 0;font-size:10px;letter-spacing:.09em;color:#255b58;font-weight:800}
.sea-section{font:800 12px 'Space Grotesk',sans-serif;color:#087c77;letter-spacing:.17em;margin:20px 0 10px}
.sea-card{padding:18px 22px;background:#ffffffc9;border:1px solid #b9d5cf;border-radius:15px;
 margin-bottom:12px;box-shadow:0 5px 18px #134f4810}
.sea-card strong{font:700 18px 'Space Grotesk',sans-serif;color:#15363a}
.sea-card span{display:block;font-size:13px;color:#526b6b;margin-top:5px}
.sea-eyebrow{font:800 11px 'Space Grotesk',sans-serif;letter-spacing:.18em;color:#0a827a}
.sea-panel{border:1px solid #b8d3cc;border-radius:16px;padding:18px 22px;background:#fffefaaf;margin:12px 0}
[data-testid="stChatMessage"]{border:1px solid #c1d9d2;border-radius:16px;background:#ffffffa6;padding:10px 16px;margin-bottom:10px}
@media(max-width:700px){.block-container{padding:1rem}.sea-hero{padding:26px 23px}.sea-hero:after{font-size:110px;right:0;top:12px}}
@media(prefers-reduced-motion:reduce){.sea-hero:after{animation:none}.stButton button{transition:none!important}}
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

st.markdown("<div class='sea-section'>02 / CHOOSE YOUR AGENT</div>", unsafe_allow_html=True)
agent_columns = st.columns(3)
for position, agent in enumerate(AGENTS):
    with agent_columns[position % 3]:
        title = f"{'◆ ' if agent.key == agent_key else '◇ '}{agent.label}"
        if st.button(title, key=f"agent_shortcut_{agent.key}", use_container_width=True,
                     help=agent.specialty):
            if agent.key != st.session_state.active_agent:
                st.session_state.active_agent = agent.key
                st.session_state.messages = []
                st.rerun()

selected = AGENT_BY_KEY[agent_key]
st.markdown(f"<div class='sea-card'><strong>{selected.label}</strong><span>{selected.specialty}</span></div>", unsafe_allow_html=True)

if not api_key:
    st.info("Demo interface ready. Live AI replies will activate once the administrator configures Mistral in Streamlit Secrets.")
else:
    st.success("Server-side Mistral credentials configured. Live connectivity is verified on the first request.", icon="✅")

st.markdown("<div class='sea-section'>03 / LEARNING STUDIO</div>", unsafe_allow_html=True)
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
st.markdown("<div class='sea-section'>04 / EVALUATE THE EXPERIENCE</div>", unsafe_allow_html=True)
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

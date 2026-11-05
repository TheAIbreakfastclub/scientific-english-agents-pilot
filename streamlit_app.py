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

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Light"
with st.sidebar:
    st.radio("Appearance", ("Light", "Dark"), key="theme_mode", horizontal=True,
             help="Switch between high-contrast light and dark modes.")

DARK = st.session_state.theme_mode == "Dark"
COLORS = ({
    "bg": "#0a1b26", "bg2": "#12323c", "side": "#102d38", "ink": "#f1faf7",
    "muted": "#c3ded9", "surface": "#193a44", "border": "#507f80",
    "accent": "#61e5d3", "accent2": "#93f5e7", "shadow": "#06151b",
    "hero": "#143440", "hero2": "#245c60", "input": "#1a3b45",
} if DARK else {
    "bg": "#f6f5ee", "bg2": "#e2f2eb", "side": "#e4f0e9", "ink": "#122e35",
    "muted": "#385960", "surface": "#fffef9", "border": "#a4c9c0",
    "accent": "#007b75", "accent2": "#08726f", "shadow": "#8aada5",
    "hero": "#fffdf6", "hero2": "#bceee0", "input": "#ffffff",
})

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap');
:root {--bg:%(bg)s;--bg2:%(bg2)s;--side:%(side)s;--ink:%(ink)s;--muted:%(muted)s;--surface:%(surface)s;--line:%(border)s;--accent:%(accent)s;--accent2:%(accent2)s;--shadow:%(shadow)s;--hero:%(hero)s;--hero2:%(hero2)s;--input:%(input)s;}
.stApp,[data-testid="stAppViewContainer"]{background:radial-gradient(ellipse at 90%% 0%%,var(--bg2),transparent 52%%),var(--bg)!important;color:var(--ink)!important;font-family:'DM Sans',sans-serif}
.block-container{max-width:1160px;padding-top:1.5rem;padding-bottom:4rem}
[data-testid="stSidebar"]{background:var(--side)!important;border-right:1px solid var(--line)}
[data-testid="stSidebar"] *,[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p, label,[data-testid="stWidgetLabel"] p{color:var(--ink)!important}
[data-testid="stCaptionContainer"] p,small{color:var(--muted)!important}
h1,h2,h3{font-family:'Space Grotesk',sans-serif;letter-spacing:-.04em;color:var(--ink)!important}
[data-testid="stMarkdownContainer"] p{line-height:1.65}
[data-baseweb="select"]>div,[data-baseweb="textarea"] textarea,textarea{background:var(--input)!important;color:var(--ink)!important;border:1px solid var(--line)!important;border-radius:12px!important}
[data-baseweb="select"] span,[data-baseweb="textarea"] textarea::placeholder{color:var(--muted)!important}
[role="listbox"],[role="option"]{background:var(--surface)!important;color:var(--ink)!important}
.stButton button,.stFormSubmitButton button,.stDownloadButton button{border-radius:12px!important;border:1px solid var(--line)!important;background:linear-gradient(145deg,var(--surface),var(--bg2))!important;color:var(--ink)!important;box-shadow:0 4px 0 var(--shadow),0 10px 22px #00000020!important;transition:transform .18s,box-shadow .18s!important;font-weight:750!important;min-height:46px}
.stButton button:hover,.stFormSubmitButton button:hover,.stDownloadButton button:hover{transform:translateY(-2px);box-shadow:0 6px 0 var(--shadow),0 14px 24px #00000030!important}
.stButton button:active,.stFormSubmitButton button:active{transform:translateY(3px);box-shadow:0 1px 0 var(--shadow)!important}
.stFormSubmitButton button[kind="primary"],.stButton button[kind="primary"]{background:linear-gradient(135deg,#0d5259,#007c78)!important;color:#fff!important;border-color:#197d7b!important;box-shadow:0 4px 0 #073d43,0 10px 22px #00000028!important}
.stAlert,[data-testid="stExpander"]{border-radius:13px!important}
[data-testid="stExpander"]{background:var(--surface)!important;border:1px solid var(--line)!important}
.sea-kicker{color:var(--accent2);font-size:11px;letter-spacing:.2em;font-weight:800}
.sea-hero{background:radial-gradient(circle at 82%% 22%%,var(--hero2),transparent 44%%),linear-gradient(120deg,var(--hero),var(--bg2));border:1px solid var(--line);border-radius:22px;padding:30px 38px 26px;margin-bottom:18px;position:relative;overflow:hidden;box-shadow:0 12px 32px #00000016}
.sea-hero:before{content:"";position:absolute;inset:0;pointer-events:none;background-image:linear-gradient(#4aafa51b 1px,transparent 1px),linear-gradient(90deg,#4aafa51b 1px,transparent 1px);background-size:30px 30px}
.sea-hero:after{content:'✳';position:absolute;right:30px;top:2px;font-size:150px;line-height:1.2;color:var(--accent);opacity:.2;animation:seaSpin 28s linear infinite;pointer-events:none}
@keyframes seaSpin{to{transform:rotate(360deg)}}
.sea-hero h1{position:relative;font-size:clamp(34px,4.4vw,60px);line-height:1.04;margin:9px 0 11px;color:var(--ink)!important}
.sea-hero h1 em{font-family:'Instrument Serif',serif;font-weight:400;color:var(--accent2)}
.sea-hero p{position:relative;max-width:710px;line-height:1.75;color:var(--muted)!important;font-size:15px}
.sea-tag{position:relative;display:inline-block;background:var(--surface);border:1px solid var(--line);border-radius:7px;padding:7px 10px;margin:6px 6px 0 0;font-size:10px;letter-spacing:.07em;color:var(--ink);font-weight:800}
.sea-section{font:800 12px 'Space Grotesk',sans-serif;color:var(--accent2);letter-spacing:.13em;margin:20px 0 10px}
.sea-card,.sea-panel{padding:18px 22px;background:var(--surface);border:1px solid var(--line);border-radius:15px;margin-bottom:12px;box-shadow:0 5px 18px #00000012}
.sea-card strong{font:700 18px 'Space Grotesk',sans-serif;color:var(--ink)}
.sea-card span{display:block;font-size:13px;color:var(--muted);margin-top:5px}
[data-testid="stChatMessage"]{border:1px solid var(--line);border-radius:15px;background:var(--surface);padding:12px 18px;margin-bottom:10px}
:focus-visible{outline:3px solid var(--accent)!important;outline-offset:3px}
@media(max-width:700px){.block-container{padding:1rem}.sea-hero{padding:24px 22px}.sea-hero:after{font-size:110px;right:0;top:12px}}
@media(prefers-reduced-motion:reduce){.sea-hero:after{animation:none}.stButton button{transition:none!important}}
</style>
""" % COLORS, unsafe_allow_html=True)

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

with st.expander("Start here · What is this application?", expanded=True):
    st.markdown(
        "**Scientific English Agents** is a formative learning environment. "
        "Six specialised agents support scientific writing, reasoning, vocabulary, "
        "oral communication, language accuracy and assessment. "
        "They guide your revisions rather than completing your work."
    )
    st.markdown(
        "**How to use it**\n"
        "1. Choose an agent in the left sidebar.\n"
        "2. Select your CEFR level and scientific field.\n"
        "3. Enter a short, anonymised text or question.\n"
        "4. Confirm the data notice and submit.\n"
        "5. Review the feedback and ask follow-up questions."
    )
    st.caption("The pilot requires Mistral configuration for live responses. "
               "AI feedback always requires professional judgement.")

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
    st.markdown("<p class='sea-section'>YOUR WORKSPACE</p>", unsafe_allow_html=True)
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
    st.markdown("<p class='sea-section'>RESPONSIBLE USE</p>", unsafe_allow_html=True)
    st.caption("Do not submit identifiable student data, patient information, unpublished sensitive research or confidential documents.")
    st.caption("Submissions are sent to the configured Mistral service. Messages remain in this browser session; no application database is configured.")

selected = AGENT_BY_KEY[agent_key]
with st.expander("Which agent should I choose?", expanded=False):
    for agent in AGENTS:
        st.markdown(f"**{agent.label}** — {agent.specialty}")

st.markdown(f"<div class='sea-card'><strong>{selected.label}</strong><span>{selected.specialty}</span></div>", unsafe_allow_html=True)

if not api_key:
    st.info("Demo interface ready. Live AI replies will activate once the administrator configures Mistral in Streamlit Secrets.")
else:
    st.success("Server-side Mistral credentials configured. Live connectivity is verified on the first request.", icon="✅")

st.markdown("<div class='sea-section'>02 / LEARNING STUDIO</div>", unsafe_allow_html=True)
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
st.markdown("<div class='sea-section'>03 / EVALUATE THE EXPERIENCE</div>", unsafe_allow_html=True)
st.caption("Optional pilot questionnaire. Feedback stays in this session until downloaded.")
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

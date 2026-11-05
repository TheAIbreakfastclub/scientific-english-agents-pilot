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
    initial_sidebar_state="collapsed",
    menu_items={"About": "Scientific English Agents — formative pilot"},
)

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Light"
if "active_agent" not in st.session_state:
    st.session_state.active_agent = AGENTS[0].key
if "messages" not in st.session_state:
    st.session_state.messages = []
if "requests" not in st.session_state:
    st.session_state.requests = 0
if "feedback" not in st.session_state:
    st.session_state.feedback = []

DARK = st.session_state.theme_mode == "Dark"
COLORS = ({
    "bg": "#0a1822", "bg2": "#122d36", "ink": "#f5faf8",
    "muted": "#c1d6d4", "surface": "#152e38", "surface2": "#1d3c45",
    "border": "#486e74", "accent": "#62e5d1", "accent2": "#89f3df",
    "shadow": "#030d14", "hero": "#122a35", "hero2": "#226264",
    "input": "#142e38", "chip": "#1c4047", "grid": "#77e9d21c",
    "button_text": "#f6fbf9", "ring": "#8df1df",
} if DARK else {
    "bg": "#f6f5ef", "bg2": "#e5f3ed", "ink": "#112f37",
    "muted": "#35565d", "surface": "#fffdf7", "surface2": "#edf5ef",
    "border": "#a2c4bd", "accent": "#007f78", "accent2": "#086e69",
    "shadow": "#8eafa7", "hero": "#fffcf4", "hero2": "#b6ede0",
    "input": "#ffffff", "chip": "#ecf7ef", "grid": "#0a80741d",
    "button_text": "#12343a", "ring": "#006c67",
})

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap');
:root{
 --bg:%(bg)s;--bg2:%(bg2)s;--ink:%(ink)s;--muted:%(muted)s;
 --surface:%(surface)s;--surface2:%(surface2)s;--line:%(border)s;
 --accent:%(accent)s;--accent2:%(accent2)s;--shadow:%(shadow)s;
 --hero:%(hero)s;--hero2:%(hero2)s;--input:%(input)s;
 --chip:%(chip)s;--grid:%(grid)s;--button-text:%(button_text)s;--ring:%(ring)s;
}
.stApp,[data-testid="stAppViewContainer"],.main{
 background:radial-gradient(ellipse at 92%% 0%%,var(--bg2),transparent 43%%),var(--bg)!important;
 color:var(--ink)!important;font-family:'DM Sans',sans-serif!important;
}
/* No sidebar: remove its controls as well as the panel itself. */
[data-testid="stSidebar"],[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],button[kind="headerNoPadding"]{display:none!important}
.block-container{max-width:1260px!important;padding:2rem 2.2rem 5rem!important}
[data-testid="stHeader"]{background:transparent!important}
[data-testid="stMarkdownContainer"] p,.stMarkdown p,li{color:var(--ink)!important;line-height:1.65}
[data-testid="stCaptionContainer"] p,small{color:var(--muted)!important}
[data-testid="stWidgetLabel"] p, label, [data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] strong {color:var(--ink)!important}
[data-testid="stWidgetLabel"] p{font-weight:700}
h1,h2,h3{font-family:'Space Grotesk',sans-serif!important;letter-spacing:-.035em}
hr{border-color:var(--line)!important;margin-top:1.7rem!important}
/* Light and dark controls: override BaseWeb's black default in both modes. */
[data-baseweb="select"]>div,[data-baseweb="input"]>div,
[data-baseweb="textarea"] textarea,.stTextArea textarea,
[data-baseweb="base-input"]{background:var(--input)!important;color:var(--ink)!important;
 border-color:var(--line)!important;border-radius:12px!important}
[data-baseweb="select"] span,[data-baseweb="select"] input,
[data-baseweb="select"]>div>div,[data-baseweb="select"] svg,
[data-baseweb="textarea"] textarea,[data-baseweb="input"] input{
 color:var(--ink)!important;fill:var(--ink)!important}
[data-baseweb="select"] input::placeholder, textarea::placeholder,
[data-baseweb="textarea"] textarea::placeholder{color:var(--muted)!important;opacity:.85!important}
[role="listbox"],[role="option"],[data-baseweb="popover"] ul{
 background:var(--surface)!important;color:var(--ink)!important}
[role="option"]:hover{background:var(--surface2)!important}
.stRadio [data-testid="stMarkdownContainer"] p{color:var(--ink)!important}
.stRadio label{color:var(--ink)!important}
.stRadio [role="radiogroup"]{gap:18px}
[data-testid="stCheckbox"] label p{color:var(--ink)!important}
/* Dimensional, confident controls with explicit active state. */
.stButton button,.stFormSubmitButton button,.stDownloadButton button{
 width:100%%;min-height:51px!important;border:1px solid var(--line)!important;
 border-radius:14px!important;background:linear-gradient(145deg,var(--surface),var(--surface2))!important;
 color:var(--ink)!important;font-family:'Space Grotesk',sans-serif!important;
 font-size:.9rem!important;font-weight:700!important;
 box-shadow:0 4px 0 var(--shadow),0 11px 20px #0000001c!important;
 transition:transform .16s ease,box-shadow .16s ease,border-color .16s ease!important;
}
.stButton button:hover,.stFormSubmitButton button:hover,.stDownloadButton button:hover{
 transform:translateY(-2px);border-color:var(--accent)!important;
 box-shadow:0 6px 0 var(--shadow),0 15px 24px #00000022!important;
}
.stButton button:active,.stFormSubmitButton button:active{
 transform:translateY(3px)!important;box-shadow:0 1px 0 var(--shadow)!important;
}
.stButton button[kind="primary"],.stFormSubmitButton button[kind="primary"]{
 background:linear-gradient(135deg,#0b4652,#007f79)!important;
 border:1px solid #217e79!important;color:#ffffff!important;
 box-shadow:0 4px 0 #073f49,0 12px 22px #00000022!important;
}
.stButton button[kind="primary"]:hover,.stFormSubmitButton button[kind="primary"]:hover{
 box-shadow:0 6px 0 #073f49,0 16px 26px #0000002a!important;
}
.stButton button:disabled,.stFormSubmitButton button:disabled{
 opacity:.56!important;transform:none!important;cursor:not-allowed!important}
/* Special treatment for agent selection buttons. */
[class*="st-key-agent_button_"] button{min-height:61px!important;font-size:1rem!important;
 text-align:left!important;justify-content:flex-start!important;padding-left:18px!important}
[class*="st-key-agent_card_"]{padding:10px 14px 12px;border-radius:18px;
 background:var(--surface);border:1px solid var(--line);margin-bottom:10px;
 box-shadow:0 9px 25px #0000000a}
[class*="st-key-agent_card_"] [data-testid="stCaptionContainer"] p{
 font-size:12px;min-height:30px;line-height:1.35;color:var(--muted)!important}
[data-testid="stAlert"],.stAlert{border-radius:14px!important}
[data-testid="stExpander"]{background:var(--surface)!important;border:1px solid var(--line)!important;
 border-radius:15px!important;overflow:hidden}
[data-testid="stExpander"] summary,[data-testid="stExpander"] summary p{color:var(--ink)!important}
[data-testid="stChatMessage"]{background:var(--surface)!important;border:1px solid var(--line)!important;
 border-radius:15px!important;padding:12px 18px!important;margin-bottom:10px}
[data-testid="stForm"]{background:var(--surface);border:1px solid var(--line)!important;
 border-radius:20px;padding:22px!important;box-shadow:0 10px 30px #0000000d}
.sea-topline{display:flex;align-items:center;gap:12px;margin:0 0 9px}
.sea-top-mark{display:inline-grid;place-items:center;background:var(--accent);color:var(--surface);
 border-radius:12px;width:38px;height:38px;font-size:25px;font-weight:800}
.sea-top-label{font:800 11px 'Space Grotesk',sans-serif;letter-spacing:.16em;
 color:var(--accent2);line-height:1.5}
.sea-hero{background:radial-gradient(circle at 85%% 23%%,var(--hero2),transparent 40%%),
 linear-gradient(112deg,var(--hero),var(--bg2));border:1px solid var(--line);
 border-radius:24px;position:relative;overflow:hidden;padding:25px 34px 24px;
 box-shadow:0 12px 34px #00000013;margin:7px 0 15px}
.sea-hero:before{content:"";position:absolute;inset:0;pointer-events:none;
 background-image:linear-gradient(var(--grid) 1px,transparent 1px),
 linear-gradient(90deg,var(--grid) 1px,transparent 1px);background-size:29px 29px}
.sea-hero:after{content:'✳';position:absolute;top:-27px;right:39px;font-size:168px;
 color:var(--accent);opacity:.14;pointer-events:none;animation:seaSpin 30s linear infinite}
@keyframes seaSpin{to{transform:rotate(360deg)}}
.sea-kicker{position:relative;color:var(--accent2)!important;font-size:11px;letter-spacing:.23em;font-weight:800}
.sea-hero h1{position:relative;color:var(--ink)!important;
 font-family:'Space Grotesk',sans-serif!important;font-size:clamp(35px,4.3vw,56px);
 line-height:1.03;letter-spacing:-.05em;margin:8px 0 13px}
.sea-hero h1 em{font-family:'Instrument Serif',serif;font-weight:400;
 color:var(--accent2)}
.sea-hero p{position:relative;color:var(--muted)!important;max-width:850px;
 font-size:15px;line-height:1.6;margin:8px 0 14px}
.sea-tag{position:relative;display:inline-block;border:1px solid var(--line);
 background:var(--surface);color:var(--ink);border-radius:7px;padding:6px 10px;
 margin:3px 6px 0 0;font:800 10px 'Space Grotesk',sans-serif;letter-spacing:.09em}
.sea-section{font:800 12px 'Space Grotesk',sans-serif;color:var(--accent2);
 letter-spacing:.15em;margin:18px 0 10px}
.sea-intro{padding:20px 24px;border-radius:17px;background:var(--surface);
 border:1px solid var(--line);min-height:238px;box-shadow:0 6px 21px #0000000b}
.sea-intro h3{margin:0 0 12px;font:700 19px 'Space Grotesk',sans-serif;
 letter-spacing:-.025em;color:var(--ink)!important}
.sea-intro p,.sea-intro li{color:var(--ink)!important;font-size:14px;line-height:1.7}
.sea-intro ol{margin:0;padding-left:20px}
.sea-intro li{margin:5px 0;padding-left:4px}
.sea-intro-note{color:var(--muted)!important;font-size:12px!important;line-height:1.5!important}
.sea-card{padding:18px 22px;background:var(--surface);border:1px solid var(--line);
 border-radius:15px;margin-bottom:12px;box-shadow:0 5px 18px #00000010}
.sea-card strong{font:700 18px 'Space Grotesk',sans-serif;color:var(--ink)}
.sea-card span{display:block;color:var(--muted);font-size:13px;margin-top:5px}
.sea-pill{display:inline-block;border-radius:9px;padding:7px 10px;
 background:var(--chip);border:1px solid var(--line);
 color:var(--ink);font-weight:700;font-size:12px}
.sea-status{color:var(--muted);font-size:12px;font-weight:600}
.sea-foot{margin:16px 0;color:var(--muted);font-size:12px}
:focus-visible{outline:3px solid var(--ring)!important;outline-offset:3px!important}
@media(max-width:740px){
 .block-container{padding:1rem 1rem 3rem!important}
 .sea-hero{padding:22px 20px}.sea-hero:after{font-size:105px;right:3px;top:5px}
 .sea-hero h1{font-size:37px}.sea-intro{min-height:auto;padding:18px}
}
@media(prefers-reduced-motion:reduce){
 .sea-hero:after{animation:none!important}
 .stButton button,.stFormSubmitButton button,.stDownloadButton button{transition:none!important}
}
</style>
""" % COLORS, unsafe_allow_html=True)

# The navigation, including appearance controls, is entirely on the main page.
brand_column, appearance_column = st.columns([3.6, 1.1], vertical_alignment="center")
with brand_column:
    st.markdown("""
    <div class="sea-topline">
      <div class="sea-top-mark">✳</div>
      <div class="sea-top-label">THE AI BREAKFAST CLUB<br>SCIENTIFIC ENGLISH AGENTS / PILOT</div>
    </div>
    """, unsafe_allow_html=True)
with appearance_column:
    st.radio(
        "Appearance", ("Light", "Dark"), key="theme_mode", horizontal=True,
        help="Switch between high-contrast light and dark modes.",
    )

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

# Place the original explanatory copy at the top, visible without opening an expander.
st.markdown("<div class='sea-section'>01 / START HERE</div>", unsafe_allow_html=True)
intro_column, steps_column = st.columns([1.13, 1], gap="medium")
with intro_column:
    st.markdown("""
    <section class="sea-intro">
      <h3>Start here · What is this application?</h3>
      <p><strong>Scientific English Agents</strong> is a formative learning environment.
      Six specialised agents support scientific writing, reasoning, vocabulary,
      oral communication, language accuracy and assessment.
      They guide your revisions rather than completing your work.</p>
      <p class="sea-intro-note">The pilot requires Mistral configuration for live responses.
      AI feedback always requires professional judgement.</p>
    </section>
    """, unsafe_allow_html=True)
with steps_column:
    st.markdown("""
    <section class="sea-intro">
      <h3>How to use it</h3>
      <ol>
        <li>Choose an agent using the buttons below.</li>
        <li>Select your CEFR level and scientific field.</li>
        <li>Enter a short, anonymised text or question.</li>
        <li>Confirm the data notice and submit.</li>
        <li>Review the feedback and ask follow-up questions.</li>
      </ol>
    </section>
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



# Selecting an agent is a real button action, not a decorative tile.
st.markdown("<div class='sea-section'>02 / CHOOSE YOUR PEDAGOGICAL AGENT</div>", unsafe_allow_html=True)
st.caption("Select one of the six agents below. Your current conversation resets when you switch agents.")
agent_rows = [AGENTS[:3], AGENTS[3:]]
for row_index, row_agents in enumerate(agent_rows):
    columns = st.columns(3, gap="medium")
    for column, agent in zip(columns, row_agents):
        active = st.session_state.active_agent == agent.key
        agent_id = agent.key.replace("-", "_")
        with column:
            with st.container(key=f"agent_card_{agent_id}"):
                label = ("✓  " if active else f"0{1 + row_index*3 + row_agents.index(agent)}  ") + agent.label
                if st.button(
                    label, key=f"agent_button_{agent_id}",
                    use_container_width=True,
                    help=agent.specialty,
                    type="primary" if active else "secondary",
                ):
                    if st.session_state.active_agent != agent.key:
                        st.session_state.active_agent = agent.key
                        st.session_state.messages = []
                        st.rerun()
                st.caption(agent.specialty)

selected = AGENT_BY_KEY[st.session_state.active_agent]
agent_key = selected.key
st.markdown("<div class='sea-section'>03 / SET YOUR LEARNING CONTEXT</div>", unsafe_allow_html=True)
if agent_key == "assessment":
    settings_left, settings_middle, settings_right = st.columns([1, 1.35, 1.15], gap="medium")
else:
    settings_left, settings_middle = st.columns([1, 1.65], gap="medium")
with settings_left:
    level = st.selectbox("CEFR level", ("B1", "B2", "C1", "C2"), index=1)
with settings_middle:
    field = st.selectbox("Scientific field", (
        "Life sciences", "Medicine", "Neuroscience", "Engineering",
        "Chemistry", "Physics", "Environmental science", "Other sciences",
    ))
if agent_key == "assessment":
    with settings_right:
        rubric = st.selectbox("Assessment rubric", list(RUBRICS))
else:
    rubric = "Abstract /10"

if not api_key:
    st.info("Demo interface ready. Live AI replies will activate once the administrator configures Mistral in Streamlit Secrets.")
else:
    st.success("Server-side Mistral credentials configured. Live connectivity is verified on the first request.", icon="✅")

st.markdown("<div class='sea-section'>04 / LEARNING STUDIO</div>", unsafe_allow_html=True)
status_column, reset_column = st.columns([3, 1.2], vertical_alignment="center")
with status_column:
    st.caption(f"{selected.label} · {selected.specialty}")
    st.caption(f"Model: {model} · {st.session_state.requests}/{MAX_REQUESTS} requests in this browser session")
with reset_column:
    if st.button("Clear conversation", type="secondary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
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



st.markdown("<div class='sea-section'>RESPONSIBLE USE</div>", unsafe_allow_html=True)
st.caption("Do not submit identifiable student data, patient information, unpublished sensitive research or confidential documents.")
st.caption("Submissions are sent to the configured Mistral service. Messages remain in this browser session; no application database is configured.")
st.divider()
st.markdown("<div class='sea-section'>05 / EVALUATE THE EXPERIENCE</div>", unsafe_allow_html=True)
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

# All data-processing logic stays in the original repository's core.py.

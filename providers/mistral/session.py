#!/usr/bin/env python3
"""
Scientific English Agent — Mistral Provider Session Script
Usage: python providers/mistral/session.py
Requires: pip install mistralai python-dotenv
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

try:
    from mistralai import Mistral
except ImportError:
    print("Error: mistralai not installed. Run: pip install mistralai python-dotenv")
    sys.exit(1)

# ── Config ────────────────────────────────────────────────────────────────────

API_KEY = os.getenv("MISTRAL_API_KEY")
MODEL = os.getenv("MISTRAL_MODEL", "mistral-large-latest")
AGENT_LANGUAGE = os.getenv("AGENT_LANGUAGE", "en")
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))

if not API_KEY:
    print("Error: MISTRAL_API_KEY not set. Add it to your .env file.")
    sys.exit(1)

ROOT = Path(__file__).parent.parent.parent  # repo root

# ── Load shared files ─────────────────────────────────────────────────────────

def load_file(path: Path) -> str:
    """Load a markdown file, return empty string if not found."""
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""

def build_system_prompt(agent: str) -> str:
    """Assemble system prompt from MISTRAL.md + shared + agent file."""
    parts = []

    # Course config (MISTRAL.md at repo root, filled in by teacher)
    mistral_md = ROOT / "MISTRAL.md"
    if mistral_md.exists():
        parts.append(load_file(mistral_md))
    else:
        print("Warning: MISTRAL.md not found at repo root.")
        print("Copy providers/mistral/MISTRAL.md.template → MISTRAL.md and fill it in.")

    # Shared protocols
    for shared in ["feedback-protocol", "error-taxonomy", "cefr-descriptors", "academic-word-list"]:
        content = load_file(ROOT / "src" / "shared" / f"{shared}.md")
        if content:
            parts.append(f"---\n{content}")

    # Agent-specific instructions
    agent_path = ROOT / "src" / "agents" / agent / "agent.md"
    content = load_file(agent_path)
    if content:
        parts.append(f"---\n{content}")
    else:
        print(f"Warning: Agent '{agent}' not found at {agent_path}")

    if AGENT_LANGUAGE.lower() == "fr":
        parts.append(
            "---\nLANGUAGE OVERRIDE: Respond to the student in French, "
            "unless they explicitly switch to English."
        )

    return "\n\n".join(parts)

# ── Router ────────────────────────────────────────────────────────────────────

ROUTER = {
    # keyword → agent directory name
    "abstract":        "writing-coach",
    "imrad":           "writing-coach",
    "introduction":    "writing-coach",
    "methods":         "writing-coach",
    "results":         "writing-coach",
    "discussion":      "writing-coach",
    "write":           "writing-coach",
    "review":          "critical-reviewer",
    "peer review":     "critical-reviewer",
    "critique":        "critical-reviewer",
    "vocabulary":      "lexical-expert",
    "word":            "lexical-expert",
    "glossary":        "lexical-expert",
    "lexis":           "lexical-expert",
    "awl":             "lexical-expert",
    "presentation":    "communication-coach",
    "poster":          "communication-coach",
    "slides":          "communication-coach",
    "oral":            "communication-coach",
    "grammar":         "language-tutor",
    "error":           "language-tutor",
    "hedging":         "language-tutor",
    "tense":           "language-tutor",
    "passive":         "language-tutor",
    "assess":          "assessment",
    "grade":           "assessment",
    "rubric":          "assessment",
    "score":           "assessment",
    "imrad rubric":    "assessment",
}

def route(user_input: str) -> str:
    """Return agent name based on the most specific matching keyword.

    Multi-word triggers (e.g. "peer review", "imrad rubric") are checked
    before single-word ones, then longer keywords before shorter ones, so
    a phrase is not shadowed by a shorter substring it happens to contain
    (e.g. "imrad rubric" -> assessment vs. "imrad" -> writing-coach).
    """
    lowered = user_input.lower()
    # Multi-word triggers are more specific than single-word ones (e.g.
    # "imrad rubric" -> assessment should win over "imrad" -> writing-coach),
    # so they are checked first; within each group, longer keywords first.
    for keyword in sorted(ROUTER, key=lambda k: (k.count(" "), len(k)), reverse=True):
        if keyword in lowered:
            return ROUTER[keyword]
    return None

# ── Session ───────────────────────────────────────────────────────────────────

def run_session():
    client = Mistral(api_key=API_KEY)
    history = []
    current_agent = None
    system_prompt = None

    print(f"\n=== Scientific English Agent (Mistral / {MODEL}) ===")
    print("Type your task. Type 'exit' to quit, 'agent' to see active agent.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSession ended.")
            break

        if not user_input:
            continue
        if user_input.lower() == "exit":
            print("Session ended.")
            break
        if user_input.lower() == "agent":
            print(f"Active agent: {current_agent or 'none — send a task to activate one'}\n")
            continue

        # Route to agent if keyword detected
        detected = route(user_input)
        if detected and detected != current_agent:
            current_agent = detected
            system_prompt = build_system_prompt(current_agent)
            history = []  # reset context on agent switch
            print(f"[Routing to: {current_agent}]\n")
        elif not current_agent:
            print(
                "No agent matched. Try a keyword like: abstract, review, "
                "vocabulary, grammar, presentation, assess.\n"
            )
            continue

        history.append({"role": "user", "content": user_input})

        response = client.chat.complete(
            model=MODEL,
            messages=[{"role": "system", "content": system_prompt}] + history,
            max_tokens=2048,
            temperature=0.3,  # low temperature for consistent pedagogical output
        )

        assistant_message = response.choices[0].message.content
        history.append({"role": "assistant", "content": assistant_message})

        # Keep context bounded -- drop oldest turns beyond MAX_HISTORY_MESSAGES
        if len(history) > MAX_HISTORY_MESSAGES:
            history = history[-MAX_HISTORY_MESSAGES:]

        print(f"\nAgent [{current_agent}]:\n{assistant_message}\n")

if __name__ == "__main__":
    run_session()

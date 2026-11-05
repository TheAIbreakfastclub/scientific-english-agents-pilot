# Quickstart — 5 Minutes to First Session

## Prerequisites

- [Claude Code](https://docs.anthropic.com/claude-code) installed (`npm install -g @anthropic-ai/claude-code`)
- An Anthropic API key ([console.anthropic.com](https://console.anthropic.com))

---

## Step 1 — Clone and configure environment

```bash
git clone https://github.com/TheAIbreakfastclub/scientific_english_agents-public.git
cd scientific_english_agents

cp .env.example .env
# Edit .env: add your ANTHROPIC_API_KEY at minimum
```

---

## Step 2 — Configure your course

```bash
cp providers/anthropic/CLAUDE.md.template CLAUDE.md
# Open CLAUDE.md and fill in:
# - Student CEFR level (B1 / B2 / C1)
# - Scientific domain (biology, medicine, engineering…)
# - Competencies for your course (delete those not used)
# - Assessment rubric link
```

Minimum viable CLAUDE.md (fill in 5 fields, delete the rest):

```markdown
## Context

Program: [your course]

## Student Profile

Target CEFR level: B2
Scientific domain: [your field]

## Competency Framework

- WP1 — Scientific abstract
- WP2 — IMRAD section

## Assessment Criteria

Primary rubric: src/agents/assessment/rubrics/imrad.md
```

---

## Step 3 — Launch Claude Code

```bash
claude
```

---

## Step 4 — First task

Paste one of these to start:

```
Review this abstract: [paste student text]
```

```
Run the weekly writing routine
```

```
Assess this introduction using the IMRAD rubric
```

```
Build a domain glossary for [your field] at B2 level
```

```
Simulate a peer review of this methods section: [paste text]
```

---

## What happens next

Claude reads `CLAUDE.md`, identifies the task keyword, routes to the right
agent in `src/agents/`, and applies the shared protocols from `src/shared/`.

Feedback is structured using the PPP protocol (Praise → Problem → Proposal).
Competency progress is tracked in `src/routines/progress-tracker.md`.

---

## Troubleshooting

| Problem                             | Fix                                                                                        |
| ----------------------------------- | ------------------------------------------------------------------------------------------ |
| `ANTHROPIC_API_KEY not found`       | Check `.env` exists and key is correct                                                     |
| Agent gives generic feedback        | Fill in more fields in `CLAUDE.md` (domain, level, competencies)                           |
| Wrong agent activated               | Add the trigger keyword to your request (e.g. "vocabulary" → Lexical Expert)               |
| Nothing happens when I paste a task | Make sure `CLAUDE.md` exists in the repo root and Claude Code was started from that folder |

See [contributing.md](contributing.md) for adding new agents or domain banks.

---

## Mistral path (RGPD-compliant / ESR)

```bash
# Set provider in .env
echo "PROVIDER=mistral" >> .env
echo "MISTRAL_API_KEY=your_key" >> .env

# Copy Mistral config template
cp providers/mistral/MISTRAL.md.template MISTRAL.md
# Fill in MISTRAL.md: level, domain, competencies

# Install Python dependency
pip install "mistralai<2" python-dotenv

# Run session
python providers/mistral/session.py
```

For Le Chat Pro (no-code): see `providers/mistral/README.md`.

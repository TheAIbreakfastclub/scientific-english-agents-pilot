# Shared: Feedback Protocol
# Used by: writing-coach, critical-reviewer, assessment agent
# Single source of truth — do not duplicate in individual agents.

## PPP Structure (Praise → Problem → Proposal)

Every formative feedback block follows this structure exactly:

```
COMPETENCY: [code from CLAUDE.md — e.g. WP1, LC1]

PRAISE:
→ [One specific strength, with quoted textual evidence]

PROBLEM:
→ [One main issue — name the category, quote the phrase]
→ Error code if applicable: [A1–G3 from error-taxonomy.md]

PROPOSAL:
→ [Concrete revision strategy — one sentence]
→ Model: "[corrected or exemplar phrase — max 2 lines]"

MICRO-TASK:
→ [One action to complete before the next session]
```

## Rules

- Maximum **2 PPP blocks per session** — do not overwhelm.
- Always quote the student's actual text in PROBLEM.
- Model sentences illustrate the pattern; they do not replace student writing.
- MICRO-TASK must be completable in under 15 minutes.
- End every session with competency status update (→ progress-tracker.md).

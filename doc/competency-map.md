# Competency Map -- Approche par Competences (APC)

This page is the single reference table for every competency code used
across this repository (CLAUDE.md templates, progress trackers, rubrics,
agent instructions). Each code maps to: a skill domain, the agent(s) that
work on it, and (where defined) a CEFR level and example task.

Status legend: **Defined** = has an explicit description and example
somewhere in the repo. **Gap** = the code is referenced (e.g. in a range
like "WP1-WP6") but has no definition anywhere yet -- a placeholder for
future curriculum work (see doc/contributing.md).

## WP -- Written Production

| Code | Competency | Agent | CEFR | Status |
|------|------------|-------|------|--------|
| WP1 | Scientific abstract (structured, ~250 words) | Writing Coach | B2 | Defined |
| WP2 | IMRAD section (Intro / Methods / Results / Discussion) | Writing Coach | B2-C1 | Defined |
| WP3 | Lab report | Writing Coach | B1-B2 | Defined |
| WP4 | Literature review paragraph | Writing Coach | C1 | Defined |
| WP5 | *(not yet defined)* | -- | -- | Gap |
| WP6 | Grant / funding application section | Writing Coach | C1 | Defined (customisation.md only) |

## OM -- Oral & Multimodal communication

| Code | Competency | Agent | CEFR | Status |
|------|------------|-------|------|--------|
| OM1 | 10-minute conference presentation | Communication Coach | B2-C1 | Defined |
| OM2 | *(not yet defined -- likely poster pitch)* | Communication Coach | -- | Gap |
| OM3 | Q&A after a presentation | Communication Coach | C1 | Defined (customisation.md only) |
| OM4 | *(not yet defined)* | Communication Coach | -- | Gap |

## CR -- Critical Reading & peer Review

| Code | Competency | Agent | CEFR | Status |
|------|------------|-------|------|--------|
| CR1 | Identify IMRAD structure in a published paper | Critical Reviewer | B2 | Defined |
| CR2 | Identify IMRAD moves in an excerpt (guided) | Critical Reviewer | B2 | Defined |
| CR3 | Write a structured peer review (PPP) | Critical Reviewer | B2-C1 | Defined |
| CR4 | *(not yet defined)* | Critical Reviewer | -- | Gap |

## LC -- Language Competency (grammar, register, lexis)

| Code | Competency | Agent | CEFR | Status |
|------|------------|-------|------|--------|
| LC1 | Hedging (avoiding overstatement: "prove" vs "suggest") | Language Tutor | B2 | Defined |
| LC2 | *(not yet defined)* | Language Tutor | -- | Gap |
| LC3 | *(not yet defined)* | Language Tutor | -- | Gap |
| LC4 | Academic vocabulary (AWL), domain terminology | Lexical Expert | B1-C1 | Defined |
| LC5 | Register consistency (informal -> formal swaps) | Lexical Expert | B1-B2 | Defined |

## Indicative curriculum mapping

From `doc/customisation.md`, by study level:

| Level | CEFR target | Typical competencies |
|-------|-------------|----------------------|
| L3 / Bachelor | B1 -> B2 | WP3 (lab report), LC1-LC2 |
| Master 1 | B2 | WP1 (abstract), WP2 (IMRAD), CR1 |
| Master 2 | B2+ -> C1 | WP2 (full article), CR3 (peer review), OM1 |
| Doctoral / Research | C1 | WP4 (lit review), WP6 (grant), OM3 (Q&A) |

## How a competency gets tracked

1. The teacher sets a `competency target` in `CLAUDE.md` (e.g. `WP1, LC1`).
2. The relevant agent reads it and gives PPP feedback tagged with that code
   (see `src/shared/feedback-protocol.md`).
3. The student's `src/routines/progress-tracker.md` (memory block) is
   updated: Not started -> In progress -> Validated.

## Adding a new competency code

See `doc/contributing.md`. In short: pick an unused code in the right
family (WP/OM/CR/LC), add a one-line definition to this table, link it from
the relevant `src/agents/<agent>/agent.md`, and add at least one rubric
criterion that can validate it.

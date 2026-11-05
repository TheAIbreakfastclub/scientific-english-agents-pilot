# Customisation Guide — Adapting CLAUDE.md to Your Course

## Minimum Viable Configuration (5 minutes)

Fill in only these fields and delete everything else:

```markdown
## Context
Program: Master 1 Biologie Cellulaire — UT3 Paul Sabatier

## Student Profile
Target CEFR level: B2
Scientific domain: Molecular Biology

## Competency Framework
- WP1 — Scientific abstract
- WP2 — IMRAD section (Introduction + Discussion focus)

## Assessment Criteria
Primary rubric: src/agents/assessment/rubrics/imrad.md
Pass threshold: 12/20
```

---

## Domain Configuration Examples

### Life Sciences / Biology
```
Scientific domain: Molecular Biology / Cell Biology / Ecology
Style guide: Nature style (no numbered references in text)
Preferred hedging: "The data suggest…", "This may indicate…"
Domain banks: (community contribution - see Contributing)
```

### Medicine / Health Sciences
```
Scientific domain: Clinical Medicine / Epidemiology / Pharmacology
Style guide: Vancouver (numbered references)
Preferred hedging: "It appears that…", "This finding is consistent with…"
Domain banks: (community contribution - see Contributing)
```

### Engineering / Physics
```
Scientific domain: Mechanical Engineering / Fluid Dynamics
Style guide: IEEE (numbered references)
Preferred hedging: "Results suggest…", "This may be attributed to…"
Domain banks: (community contribution - see Contributing)
```

### Chemistry
```
Scientific domain: Organic Chemistry / Analytical Chemistry
Style guide: ACS (author-date)
Preferred hedging: "These results indicate…", "This observation suggests…"
Domain banks: (community contribution - see Contributing)
```

---

## Level Calibration Guide

| Course type | Recommended level | Key competencies |
|-------------|------------------|-----------------|
| L3 / Bachelor | B1 → B2 | WP3 (lab report), LC1–LC2 |
| Master 1 | B2 | WP1 (abstract), WP2 (IMRAD), CR1 |
| Master 2 | B2+ → C1 | WP2 (full article), CR3 (peer review), OM1 |
| Doctoral / Research | C1 | WP4 (lit review), WP6 (grant), OM3 (Q&A) |

---

## Adding a New Domain Bank

1. Create `src/agents/lexical-expert/domain-banks/[your-domain].md`
2. Follow the structure in `biology.md` (term, definition, example, collocations)
3. Add minimum 20 high-frequency domain terms
4. Reference it in CLAUDE.md under `Domain-Specific Instructions`
5. Submit a PR — see [contributing.md](contributing.md)

---

## Adding a New Competency

1. Define the competency in your CLAUDE.md with a code (e.g. WP7)
2. Identify which agent handles it (or create a new one — see contributing.md)
3. Add a rubric criterion or adapt an existing rubric in `src/agents/assessment/rubrics/`
4. Map the competency to a CEFR descriptor in `src/shared/cefr-descriptors.md`

# Ethics — Responsible Use of AI in Scientific English Teaching

## Core Principles

### 1. AI as scaffold, not ghost-writer
This skill is designed to **coach** students, not produce their work.
The agents give feedback, generate models, and scaffold revision.
They do not write abstracts, introductions, or lab reports on behalf of students.

**Enforced by design:**
- Writing Coach produces model sentences (max 2 lines), never full sections
- Assessment Agent grades existing text, never generates submission-ready text
- All agents end sessions with a student-action micro-task, not a completed product

---

### 2. Transparency and disclosure

**Teachers** using this system for official summative assessment must:
- Attach the AI involvement declaration to graded feedback
- Validate all scores before submission to institutional records
- Inform students that AI tools are used in the feedback process

**Students** must be informed:
- That feedback may be AI-assisted
- That AI involvement does not mean the grade is automated
- That their text is processed via Anthropic's API (see data note below)

---

### 3. Data protection (RGPD / GDPR)

Student names and identifiers **must not** appear in files processed through
the API or stored in tracked files.

- Use anonymised student codes (e.g. STU-007) in all CLAUDE.md and tracker files
- `.gitignore` excludes all `students/` and `tracker-*.md` files from version control
- Feedback reports in `build/` are excluded from git by default
- Do not paste personally identifiable information into Claude Code sessions

**API data note:** Text submitted to Claude Code is processed by Anthropic.
Review Anthropic's data processing terms before using student work.
For institutions subject to strict data residency requirements, consider
running a self-hosted model instead.
For Mistral provider: Text is processed by Mistral AI (France, EU-based). 
RGPD-friendly (EU-hosted, French provider) but not automatically RGPD-compliant: your institution needs its own data processing agreement (DPA) with Mistral AI and a documented legal basis for processing student data.
---

### 4. AI-detection flag

The Assessment Agent includes an integrity flag for texts showing signs of
AI generation. This flag:
- **Does not** constitute proof of misconduct
- **Triggers a conversation**, not a sanction
- Should be handled according to your institution's academic integrity policy

---

### 5. Teacher accountability

AI assessment assistance does not transfer responsibility.
The teacher remains accountable for:
- All final grades
- The accuracy of competency validations
- Communication with students about their performance

---

## Recommended Institutional Disclosure Template

> *"Feedback on written work in this course may be produced with AI assistance
> using the scientific-english-agents tool (Claude Code / Anthropic).
> All AI-generated feedback is reviewed and validated by the course teacher
> before communication to students. AI involvement is declared in accordance
> with [institution] policy on AI use in assessment (ref: [policy document])."*

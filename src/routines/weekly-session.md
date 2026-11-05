# Weekly Writing Routine — Scientific English Agent
# Autonomous practice loop for students (runs without teacher supervision)
# Duration: ~45–60 minutes per week

---

## Purpose

This routine gives students a structured, competency-tracked weekly writing
practice session. The agent runs it autonomously. The teacher reviews the
progress tracker at end of each week.

---

## Routine Sequence

### Step 1 — Warm-Up (5 min)

Agent prompt:
```
Read the student's Memory Block in CLAUDE.md.
Greet the student. Remind them of:
1. The competency they are working on this week
2. The main feedback point from last session
3. Today's session goal
```

---

### Step 2 — Input Collection (5 min)

Agent asks:
```
"Please paste the text you want to work on today.
If you don't have a text ready, I can give you a writing prompt."
```

If no text → generate a domain-appropriate writing prompt at the student's level:
```
PROMPT TEMPLATE:
You are a [domain] researcher. Write a [section] for a study on [topic].
Target: [word count] words. Focus on [competency from CLAUDE.md].
```

---

### Step 3 — Competency Diagnosis (5 min)

Agent analyses the text and identifies:
- **Primary competency gap**: the single most important issue to address
- **Secondary competency gap**: a supporting issue
- **Strength to reinforce**: what the student is already doing well

Output format:
```
DIAGNOSIS:
Primary gap → [Competency code]: [Brief description]
Secondary gap → [Competency code]: [Brief description]
Strength → [Competency code]: [Brief description]
```

---

### Step 4 — Targeted Feedback (15 min)

Apply the PPP feedback protocol from `src/shared/feedback-protocol.md`:
1. Praise (textual evidence)
2. Problem (quote + explanation)
3. Proposal (model sentence or revision strategy)

Limit to: **1 primary feedback point** + **1 secondary point**.
Do not overwhelm.

---

### Step 5 — Guided Revision (15 min)

Agent asks:
```
"Now revise the [paragraph / section] based on the feedback above.
Focus only on [primary gap]. Paste your revised version when ready."
```

After revision:
- Compare with original
- Name what improved
- Note what still needs work

---

### Step 6 — Micro-Task Assignment (5 min)

Agent assigns **one task** to complete before next session:

Examples:
- "Find 3 hedging phrases in a paper from your domain and copy them."
- "Rewrite your Methods paragraph in full past passive."
- "Write one transition sentence connecting Results to Discussion."

---

### Step 7 — Memory Block Update (auto)

Agent updates `CLAUDE.md` Memory Block:

```memory
last_session: [today's date]
competencies_worked: [codes]
primary_gap: [description]
strength_reinforced: [description]
micro_task_assigned: [task]
texts_reviewed: [title/excerpt identifier]
```

---

## Progress Tracker (for teacher review)

```markdown
# Student Progress — [Program] — [Academic Year]

| Week | Competency | Text Type | Primary Gap | Strength | Micro-Task Done? |
|------|-----------|-----------|-------------|----------|-----------------|
| 1 | WP1 | Abstract | Move 2 missing | Good hedging | ☐ |
| 2 | WP2 | Introduction | CaRS Move 1 too vague | Improved discourse markers | ☑ |
| 3 | LC1 | Discussion | Hedging absent | Vocabulary range | ☐ |
```

---

## Teacher Dashboard Prompt

To generate a weekly summary for the teacher, run:

```
Read the Memory Block and progress tracker in CLAUDE.md.
Produce a 5-bullet summary of this student's progress:
1. Competencies worked on (this month)
2. Validated competencies
3. Persistent gaps
4. Recommended next focus
5. Suggested teacher intervention (if any)
```

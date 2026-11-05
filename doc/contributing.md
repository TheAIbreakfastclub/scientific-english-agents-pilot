# Contributing

## What We Welcome

- New domain vocabulary banks (`src/agents/lexical-expert/domain-banks/`)
- New rubrics for specific genres (poster abstract, grant summary, literature review)
- New agents for uncovered competencies
- Translations of `CLAUDE.md.template`
- Anonymised feedback examples for `examples/`
- Bug fixes and clarifications in existing agent files

---

## Conventions

### File naming
- Agent instructions: `src/agents/[agent-name]/agent.md`
- Domain banks: `src/agents/lexical-expert/domain-banks/[domain].md`
- Rubrics: `src/agents/assessment/rubrics/[genre].md`
- Documentation: `doc/[topic].md`

### Commit messages (Conventional Commits)
```
feat: add pharmacology domain bank
fix: correct tense guide in writing-coach
docs: update quickstart installation steps
refactor: extract AWL verbs to shared/academic-word-list.md
```

### Agent file structure
Every `agent.md` must include:
1. `# Agent: [Name]` header with trigger keywords
2. `## Role` — one paragraph, no jargon
3. `## Activation Protocol` — numbered steps
4. References to shared files (not duplicated content):
   - Feedback: `→ see src/shared/feedback-protocol.md`
   - Error codes: `→ see src/shared/error-taxonomy.md`
   - CEFR levels: `→ see src/shared/cefr-descriptors.md`

### No duplication rule
If content exists in `src/shared/`, reference it — never copy it into an agent file.
This is the single most important architectural rule.

---

## Adding a New Agent

1. Create `src/agents/[agent-name]/agent.md`
2. Add trigger keywords to the router table in `SKILL.md`
3. Add a usage doc to `doc/agents/[agent-name].md`
4. Reference shared protocols (do not duplicate)
5. Open a PR with a brief description of the competency gap it fills

---

## Pull Request Checklist

- [ ] New agent references shared files, not copies
- [ ] Trigger keywords added to `SKILL.md` router table
- [ ] Doc file added to `doc/agents/` if new agent
- [ ] No student data or API keys in any file
- [ ] `.env` not committed
- [ ] Commit message follows Conventional Commits

---

## Licence

All contributions are released under CC-BY-4.0.
By submitting a PR, you agree to this licence.

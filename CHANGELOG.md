# Changelog - scientific-english-agents

All notable changes documented here.

## [3.1.0] - 2026-06-14

### Added
- doc/competency-map.md: reference table for all WP/OM/CR/LC competency codes, with an honest Defined/Gap status (6 codes referenced across the repo were never individually defined)
- "Approche par Competences (APC)" section in README, with a Mermaid diagram of the agent routing -> PPP feedback -> competency map workflow
- "See it in action" before/after example in README
- LICENSE.md (CC BY 4.0 summary, scope notes, citation)
- doc/glossary.md: plain-language glossary for non-developer users
- Claude Skill packaging: .claude-plugin/marketplace.json + plugin.json, skills/scientific-english-agents/SKILL.md (orchestrator), and one skills/<agent>/SKILL.md per specialist agent for selective activation
- tests/test_router.py: real (non-mocked) routing tests
- CI: tests/test_links.py (live link-checking) separated from the default pytest run (-m "not integration")

### Fixed
- SKILL.md File Map resynchronised with the actual src/, providers/, doc/ tree (previously listed templates/, examples/, peer-review-rubric.md which do not exist)
- SKILL.md Quick Start: corrected CLAUDE.md.template path
- providers/mistral/session.py: routing now prioritises multi-word triggers (fixes "Assess this introduction using the IMRAD rubric" -- quickstart example #3 -- previously routed to Writing Coach instead of Assessment); removed a code-duplication bug introduced by an earlier fix-script run
- src/agents/language-tutor/agent.md: removed duplication of src/shared/error-taxonomy.md
- .env.example: documented unused variables (OUTPUT_DIR, TRACKER_DIR, ENABLE_AI_DETECTION, ENABLE_AUTOPILOT, DEBUG_ROUTING)
- doc/quickstart.md, providers/mistral/README.md: pip install pinned to "mistralai<2" (mistralai 2.x removed the top-level Mistral class that session.py imports)
- providers/mistral/README.md: Path A (Le Chat Pro) now lists every file to paste (course config + feedback-protocol + one agent file) -- previously incomplete, gave the AI no agent behaviour
- "RGPD-compliant by default" (4 occurrences across README.md, doc/ethics.md, providers/mistral/README.md, providers/mistral/MISTRAL.md.template) reworded to avoid an unverifiable compliance claim about a third party
- Repository naming consistency: scientific_english_agents used consistently in clone URLs and cross-references (previously 4 different spellings)
- BOM and mojibake fixes across several files (.env.example, CHANGELOG.md, CITATION.cff, ci.yml, tests/*.py)
- Removed the false "PPP feedback -> build/" persistence claim from doc/assets/architecture.svg (the Claude Code path writes nothing to disk)

### Known limitations (in addition to 3.0.0)
- 6 competency codes (WP5, OM2, OM4, CR4, LC2, LC3) are referenced throughout the repo but have no definition yet -- see doc/competency-map.md
- The .claude-plugin/ marketplace scaffold follows the published Agent Skills spec but has not been verified end-to-end with /plugin install
- skills/<agent>/SKILL.md are packaged copies of src/agents/<agent>/agent.md (see doc/contributing.md for the sync policy)

## [3.0.0] - 2025-06-14 (First public release)

### Added
- Six pedagogical agents: Writing Coach, Critical Reviewer, Lexical Expert, Communication Coach, Language Tutor, Assessment
- Three assessment rubrics (IMRAD /20, Abstract /10, Oral /20) aligned to CEFR B2-C1
- Shared frameworks: PPP feedback protocol, A1-G3 error taxonomy, CEFR descriptors, Academic Word List (Coxhead 2000)
- Two provider implementations: Claude Code (Anthropic) and Mistral (EU-hosted)
- Weekly writing routine (autonomous, 45-60 min)
- Complete documentation (ethics, customisation, pedagogy, quickstart)
- CC-BY-4.0 open licence for academic reuse

### Fixed
- File map synchronised with actual directory structure
- Error taxonomy codes unified across agents (A1-G3)
- Rubric naming consistency (imrad.md, abstract.md, oral.md)
- CEFR conversion tables added to all rubrics
- Hedging guidance reformulated
- RGPD language harmonised across providers

### Known limitations
- Mistral lacks agentic CLI
- Domain-specific vocabulary banks are community contributions
- Peer-review rubric planned for v3.2

## [3.2] - Planned
- Domain-specific vocabulary banks
- Peer-review assessment rubric
- Translations (French, Spanish, German)

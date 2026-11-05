# Glossary -- Plain-Language Guide

This page explains the technical terms used in this repository, written
for teachers and students who are not software developers. If a word you
need is missing, please open an issue.

## Core concepts

**Agent**
A set of written instructions (a "prompt") that tells an AI model how to
behave for one task -- for example, the Writing Coach agent tells the AI
how to give feedback on a scientific abstract. An agent here is not a
separate program: it is a text file the AI reads before responding.

**Skill**
Two related meanings. (1) Generically: the whole collection of agents,
rubrics and shared instructions in this repository -- "using the skill"
means giving an AI model access to these files so it follows the rules
they describe. (2) "Claude Skill" (capital S): Anthropic's packaged format
for this (a `SKILL.md` file with a short header describing what it does and
when to use it). This repository ships both: a top-level `SKILL.md` for
direct use, and individual Claude Skills under `skills/` for installation
via a Plugin (see below).

**Router**
The logic that decides which agent's instructions to use, based on
keywords in your message (for example, "abstract" leads to the Writing
Coach).

**Rubric**
A scoring grid used to grade student writing or presentations, with
criteria and point values (the IMRAD rubric is scored out of 20).

**CLAUDE.md / MISTRAL.md**
A configuration file you create for your course, copied from a template.
It tells the AI your students' level, your discipline, and which rubric to
use. Without it, the AI has no information about your course.

**Memory block**
A section inside CLAUDE.md where the AI keeps notes on a student's
progress between sessions: strengths, recurring errors, next steps.

## Standards and frameworks

**CEFR (B1, B2, C1, C2)**
The Common European Framework of Reference for Languages. B1/B2 = upper
intermediate, C1/C2 = advanced / proficient. Used to describe how good a
student's English needs to be.

**IMRAD**
The standard structure of a scientific article: Introduction, Methods,
Results, And Discussion.

**AWL**
Academic Word List (Coxhead, 2000): words that appear often in academic
writing across all subjects.

**PPP feedback**
The feedback structure used by every agent: Praise (what is good),
Problem (what needs work), Proposal (how to fix it).

## Technical / setup terms

**API key**
A password-like code that lets a program (Claude Code, or the Mistral
script) use an AI provider's service. Keep it secret: never share it or
paste it into a document you publish.

**.env file**
A small text file, kept private and never published, that stores your API
key and a few settings.

**Claude Code**
A command-line tool from Anthropic that lets you "chat" with Claude from a
terminal, with access to the files in this repository.

**Plugin**
A packaged extension that adds Skills, commands, or other capabilities to
Claude Code. Installing this repository as a plugin (`/plugin install`)
gives Claude Code access to its Skills without you manually copying files.

**Marketplace**
A catalogue of plugins that Claude Code can browse and install from. Adding
this repository as a marketplace (`/plugin marketplace add
TheAIbreakfastclub/scientific_english_agents`) makes its plugin available
to `/plugin install`. This is an alternative to cloning the repository; see
"Alternative: install as a Claude Skill" in the README.

**Terminal / command line**
A text-based way of giving instructions to a computer, instead of clicking
icons. If this is unfamiliar, use **Option C (Mistral Le Chat Pro)** in the
README -- it needs no terminal at all.

**RGPD / GDPR**
The European Union's data protection regulation. It governs how personal
data -- including students' names and written work -- may be processed and
stored.

**Repository / repo**
A project's folder of files, hosted on a site such as GitHub, with a
history of every change.

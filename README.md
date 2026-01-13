# Vibe Coding Framework

A lightweight framework for coding with AI at high velocity — without losing control.

This repository provides a practical structure to support *vibe coding* while maintaining:
- architectural clarity
- security-by-default
- non-regression discipline
- design consistency
- repeatable AI prompting
- a single, reliable source of truth

> Principle: **If it matters, it lives in files — not in chat history.**

---

## Why this exists

AI-assisted coding dramatically increases speed and creative flow.
Without structure, that speed often leads to regressions, inconsistencies, and hidden risks.

This framework is intentionally simple, opinionated, and battle-tested in real projects.

---

## Repository structure

/docs  
architecture.md — system overview and decisions  
security.md — threat model and hardening checklist  
non-regression.md — invariants and regression workflow  
graphic-charter.md — UI/UX consistency rules  
intra-application.md — conventions across multiple apps  

/prompts  
feature.prompt.md  
refactor.prompt.md  
bugfix.prompt.md  
security-review.prompt.md  
non-regression.prompt.md  

/examples  
01-feature-iteration  
02-refactor  
03-bugfix  

todo.md — iteration anchor (updated every loop)

---

## Core workflow

Prompt → Code → Review → Todo → Next iteration

Security and non-regression are defaults, not phases.

---

## Who this is for

- Founders and solo builders
- Small SaaS teams
- AI-assisted development workflows
- Anyone experimenting with vibe coding responsibly

---

## License

MIT © {year}

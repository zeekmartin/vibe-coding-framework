# Vibe Coding Framework

![Version](https://img.shields.io/badge/version-v1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-stable-brightgreen)

A lightweight framework for coding with AI at high velocity — **without losing control**.

This repository provides a practical structure to support *vibe coding* while maintaining:
- architectural clarity
- security-by-default
- non-regression discipline
- design consistency
- repeatable AI prompting
- a single, reliable source of truth

> **Principle:**  
> If it matters, it lives in files — not in chat history.

---

## Why this exists

AI-assisted coding dramatically increases speed and creative flow.  
Without structure, that speed often leads to regressions, inconsistencies, hidden risks, and undocumented decisions.

This framework is intentionally **simple, opinionated, and practical**.  
It is designed to keep flow and discipline aligned.

---

## Repository structure

```
/docs
  architecture.md
  security.md
  non-regression.md
  graphic-charter.md
  intra-application.md

/prompts
  feature.prompt.md
  refactor.prompt.md
  bugfix.prompt.md
  security-review.prompt.md
  non-regression.prompt.md

/examples
  01-feature-iteration.md
  02-refactor.md
  03-bugfix.md

todo.md
```

---

## Core concepts

### Docs as shared memory
Documentation replaces implicit knowledge and conversation context.
If it’s important, it’s written down.

---

### Prompts as first-class tools
Prompts define scope, constraints, and invariants.
They are reusable artifacts — not ad-hoc messages.

---

### Security & non-regression by default
Security and stability are not phases.
Every meaningful change should pass through dedicated review prompts.

---

### The iteration loop
Every iteration follows the same loop:

```
Prompt → Code → Review → Todo → Next iteration
```

The `todo.md` file is the single source of truth.

---

## Who this is for

- Founders and solo builders
- Small SaaS teams
- AI-assisted development workflows
- Anyone experimenting with vibe coding responsibly

---

## What this is not

- A heavy process
- A toolchain or framework dependency
- A replacement for testing or CI
- A silver bullet

It is intentionally boring — and that’s why it works.

---

## Contributing

Contributions are welcome if they keep the framework:
- lightweight
- clear
- tool-agnostic
- focused on safety and clarity

See `CONTRIBUTING.md`.

---

## License

MIT

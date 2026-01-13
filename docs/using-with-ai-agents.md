# Using the Framework with AI Agents

This framework is tool-agnostic.
It works with any AI or AI agent that can read and update files.

## Core principle

Files are the source of truth.
The AI uses them as context, not the conversation history.

## Recommended usage

When working with an AI agent:

- Give the agent access to:
  - /docs
  - /prompts
  - todo.md
- Ask it to:
  - respect documented constraints
  - update todo.md at the end of each iteration
  - ask questions if context is missing

## Example instruction

> “Use the documentation and prompts in this repository as constraints.
> Do not change behavior outside the defined scope.
> Update todo.md after each iteration.”

## Avoiding context drift

- Prefer updating files over re-explaining things
- Keep documentation short and explicit
- Treat prompts as contracts, not suggestions

## What this framework does not assume

- No specific AI tool
- No autonomous agent
- No hidden memory

Control stays with you.

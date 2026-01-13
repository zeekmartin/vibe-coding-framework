# Prompt: Non-regression Check

## Goal
Ensure the change does not break existing behavior.

## Inputs
- Change summary (or PR diff):
- Critical user journeys:
- APIs/routes affected:

## Instructions
1. List potential regression points.
2. Provide a smoke test checklist.
3. Provide a rollback plan.
4. Suggest monitoring signals post-deploy (errors, latency, webhook success).
5. Add `todo.md` notes: what was verified, what remains.

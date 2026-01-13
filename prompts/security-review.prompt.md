# Prompt: Security Review

## Goal
Perform a security review of the proposed change (or current state).

## Inputs
- Change summary (or PR diff):
- Public endpoints involved:
- Auth/session implications:
- Data handled (PII? tokens?):
- Third-party integrations:

## Review checklist
- Exposure: any new public port/endpoint?
- Authn/Authz: correct checks in place?
- Input validation: schema/typing, sanitization where needed?
- Secrets: no leakage, no logging secrets?
- Webhooks: signature verification, replay protection?
- Rate limiting: edge + origin adequate?
- Least privilege: services not running as root?
- Logging: sufficient for incident response, no sensitive logs?

## Output
- Findings (high/medium/low)
- Recommended fixes
- Minimal verification steps

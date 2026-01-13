# Non-regression

## Invariants (do not break)
Write explicit behaviors that must never change without a deliberate decision.
Examples:
- Public URLs remain stable
- API response fields stay backward-compatible
- Auth/session flows remain consistent
- Stripe/PayPal webhooks always return 2xx quickly

## Compatibility rules
- Avoid breaking changes unless versioned and communicated.
- Prefer additive changes (new fields, new endpoints) over modifications/removals.
- If you must change behavior, document it in `/docs/architecture.md` decisions.

## Regression workflow (every change)
1. Identify impacted areas (routes, components, APIs).
2. Run unit/integration checks (if available).
3. Manually test critical paths:
   - sign-in / sign-out
   - pricing / billing
   - key user journeys
4. Monitor after deploy:
   - error rates
   - latency
   - webhook success rates

## Change log snippet (optional)
Maintain a short “what changed” section in `todo.md` per iteration.

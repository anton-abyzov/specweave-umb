# 0860 — E2E: full submission lifecycle + theme readability

## Problem
The submit→review→notify→update-locally lifecycle (0847 + 0855 + 0859) is only covered by unit/integration tests. There is no automated test that drives the WHOLE journey through Skill Studio the way a user does. Anton: *"you must have a workflow that is testing this properly."* Plus a readability regression (the `--bg-elevated` dark-theme bug) needs a guard.

## User Stories

### US-001 — Full lifecycle E2E
As the maintainer, I want one automated E2E that drives: improve a verified skill → in-app submit → watch the queue state transitions → receive the decision notification → click it → update the locally-installed copy.

- **AC-US1-01**: The test improves a skill (e.g. `appstore`, a small ASC-CLI-aware edit) and submits it via the Studio Publish drawer **in-app** (no browser redirect).
- **AC-US1-02**: The submission appears in the in-app My Queue with a non-terminal state, and the test observes state transitions toward a terminal decision.
- **AC-US1-03**: On the terminal decision (APPROVED or REJECTED), the top-right notification bell increments and a native/desktop notification fires exactly once (T-006 dedupe). Rejected is clickable → `/submit/<id>`.
- **AC-US1-04**: After an APPROVED decision that bumps the published version above the locally-installed one, the test asserts the "update available / update locally" affordance for that installed skill.

### US-002 — Theme readability guard
- **AC-US2-01**: In BOTH light and dark themes, the Account-cabinet tab labels (Profile … My queue … Danger zone) have text/background contrast ≥ 4.5:1 (WCAG AA) — a regression guard for the `--bg-elevated` fix.

## Approach (determinism)
Run in the e2e-live lane (wrangler dev + seeded Postgres, like `e2e-live-nightly.yml`). The review decision uses the platform's fast auto-resolve path or a direct internal terminal-state injection so the test never waits on a human reviewer. Local platform only — never production.

## Out of scope
- Replacing the per-PR fast tests. - A real human-review path. - Notifications while the app is fully closed.

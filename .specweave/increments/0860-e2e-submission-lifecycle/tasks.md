# 0860 — Tasks

### T-001: Recon the lifecycle + e2e infra
**AC**: AC-US1-01..04 | **Status**: [ ] pending
**Test**: Map the exact seams — Publish drawer submit, My Queue state source, the platform scan/auto-resolve (how a local submission reaches PUBLISHED/REJECTED fast), the notification bell (TopRail) + 0859 usr_ channel, the update-locally affordance (useSkillUpdates/update bell), the theme toggle, and the existing e2e-live harness (playwright.config.ts live project, e2e/desktop, e2e-live-nightly.yml).

### T-002: E2E spec — improve → in-app submit → queue transitions
**AC**: AC-US1-01, AC-US1-02 | **Status**: [ ] pending
**Test**: Given a seeded local platform + studio → When the test improves a skill and clicks Submit in the Publish drawer → Then the POST is in-app (no window.open) and the submission shows in My Queue with a state that transitions.

### T-003: E2E spec — decision notification (approve + reject)
**AC**: AC-US1-03 | **Status**: [ ] pending
**Test**: Given the submission reaches a terminal decision (fast auto-resolve / injected) → Then the bell increments and the notification fires exactly once; rejected is clickable → /submit/<id>.

### T-004: E2E spec — update the locally-installed copy
**AC**: AC-US1-04 | **Status**: [ ] pending
**Test**: Given an APPROVED decision bumps the published version above the installed one → Then the update-available affordance appears for that skill and the update-locally action is reachable.

### T-005: Theme-readability guard (regression for --bg-elevated)
**AC**: AC-US2-01 | **Status**: [ ] pending
**Test**: Given the Account cabinet in light AND dark theme → Then every sub-nav tab label has contrast ≥ 4.5:1 against its painted background.

### T-006: Wire into the e2e-live nightly lane + run
**AC**: AC-US1-01..04 | **Status**: [ ] pending
**Test**: The spec runs under the live Playwright project; add it to e2e-live-nightly.yml (or a sibling); prove it passes locally against wrangler dev + Postgres.

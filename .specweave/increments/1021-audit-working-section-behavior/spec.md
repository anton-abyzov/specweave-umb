# 1021 Audit Working section behavior

## Problem
The beta promises to fold working and monitoring threads away and return them when they need the reader. Verify the exact implementation against real examples without disturbing active owners.

## Scope
In: classification, watchers and schedules, subagents, terminal and input states, unread and ordering, reader intent, setting on/off, merged-thread auto-settlement, source/fixture/live evidence and recommendations. Out: product changes, live status mutations, watcher or schedule changes, broad sidebar redesign.

## Acceptance Criteria
- [ ] AC-01: A report traces predicates and state transitions with absolute source paths and line evidence, including prior Stuck Working findings.
- [ ] AC-02: Read-only live examples and isolated behavior checks distinguish verified behavior from limitations and concrete discrepancies.
- [ ] AC-03: A reviewable report includes state flow, example matrix, recommended scoped fixes and independent review; research increment verifies and closes.

## Approach
Read current app source and project knowledge; inspect live state only through supported tools and specweave-studio db query. Run focused existing tests and isolated fixtures with explicit headless automation. Write evidence in this increment's evidence directory. Do not alter product source or another owner's checkout. Review in a fresh subagent context before closure.

## Decisions
### Defaulted
- Research only. Fix recommendations require a separate implementation scope.
- Preserve all active threads, watcher subscriptions, schedules, dirty files and bindings.
### Open
- None.

## Tasks
### T-01 Trace source and historical behavior
- AC: AC-01 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1021-audit-working-section-behavior/evidence/report.md | Test: source citation audit

### T-02 Verify fixtures and live examples
- AC: AC-02 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1021-audit-working-section-behavior/evidence/live-classification.json, /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1021-audit-working-section-behavior/evidence/checks.json | Test: focused production behavior tests and read-only live queries

### T-03 Verify and close 1021
- AC: AC-03 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1021-audit-working-section-behavior/evidence/report.html, /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1021-audit-working-section-behavior/evidence/review.md | Test: specweave verify 1021

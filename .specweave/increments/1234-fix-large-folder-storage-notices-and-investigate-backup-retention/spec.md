# 1234 Fix large folder storage notices and investigate backup retention

## Problem
The folder notice shows 159 GB but its parenthesized categories total 118 GB. A connected Mac also shows a notice. The user needs an explanation of warning thresholds, remote scope, database size and backup retention, and fixes for confirmed bugs.

## Scope
In: storage notice wording, warning and category logic, read-only backup retention investigation, regression checks and a PR against main. Out: deleting data or worktrees, opening live database files, changing shared checkouts, releasing or restarting the app.

## Acceptance Criteria
- [ ] AC-01: A truncated category breakdown explicitly identifies itself as partial and does not imply its categories sum to the total.
- [ ] AC-02: Report documents warning thresholds, measurement semantics and connected-machine routing from current code.
- [ ] AC-03: Report distinguishes expected backup/database storage from confirmed retention defects, with safe evidence; verified defects are fixed without deleting user data.
- [ ] AC-04: Focused tests and production build pass, a fresh-context review is recorded, and a PR targets main.

## Approach
LowDiskSpaceBanner.logic.ts currently takes usage.parts.slice(0, 3). Trace homeUsage/measure.ts, homeUsage/guard.ts, storage status subscriptions and scripts/studio-fleet backup retention. Read persisted measurement/receipt JSON and sanctioned database queries only; never open statev2.sqlite files. Implement clear partial-breakdown copy and regression coverage. Keep connected-machine notices if intentional. Expand task file scope only upon a verified retention defect.

## Decisions
### Defaulted
- Preserve remote warnings unless code establishes incorrect routing.
- Investigation performs no cleanup; HOME-DISK remains the sole cleanup owner.
- Use stable SpecWeave 3.1.21 through a session-local invocation; global installation is 3.1.17.
### Open
- none

## Tasks

### T-01 Investigate storage and retention
- AC: AC-02, AC-03 | Files: reports/investigation.md | Test: source-backed evidence review

### T-02 Clarify partial storage breakdown
- AC: AC-01 | Files: apps/web/src/components/LowDiskSpaceBanner.logic.ts, apps/web/src/components/LowDiskSpaceBanner.test.tsx | Test: focused LowDiskSpaceBanner test suite

### T-03 Validate and open PR
- AC: AC-04 | Files: reports/validation.md | Test: focused tests, production web build and fresh-context review

Verify and close 1234.

# 1078 Stabilize project badge rendering and live refresh

## Problem
Project counts alternate between numbers, pluses and question marks during routine polling. Hover hides badges. Fleet polling invalidates remote-worker requests even when capability is unchanged.

## Scope
Desktop/web attention observation, project badge presentation and focused regressions. Preserve actual offline/failed/partial semantics and other owners' work.

## Acceptance Criteria
- [ ] AC-01: Successful retained observations remain usable during background refresh; initial loading, failed reads and disconnected hosts remain incomplete.
- [ ] AC-02: Numeric badges never gain plus/question glyphs; partial coverage has a separate neutral, accessible indicator; hover keeps counts visible; light/dark and narrow layouts remain stable.
- [ ] AC-03: Fleet status-only updates do not retrigger worker requests; relevant tests and production build pass; reviewed code is pushed, merged, released and deployment verified.

## Approach
Separate observation validity from transport activity. Subscribe remote requests to stable fleet capability. Use fixed badge/menu slots and a static availability dot with descriptive accessible text. No timers, animation or masking real count changes.

## Decisions
### Defaulted
- Keep live action counts authoritative. Unavailable coverage stays explicit without ambiguous punctuation.
### Open
- None.

## Tasks
### T-01 Stabilize observations and badge presentation
- AC: AC-01, AC-02, AC-03 | Files: /tmp/swc-badge-stability/apps/web/src/studio/fleet.ts, /tmp/swc-badge-stability/apps/web/src/studio/fleet.test.ts, /tmp/swc-badge-stability/apps/web/src/studio/remoteAttentionObservation.ts, /tmp/swc-badge-stability/apps/web/src/studio/remoteAttentionObservation.test.ts, /tmp/swc-badge-stability/apps/web/src/components/studio/shell/SidebarProjectList.tsx, /tmp/swc-badge-stability/apps/web/src/components/studio/shell/shell.css, /tmp/swc-badge-stability/apps/web/tests/project-workspace/badge-stability-check.mjs | Test: focused observation tests, headless actual ProjectRow fixture transitions and web production build
### T-02 Review, push and deploy
- AC: AC-03 | Files: .specweave/increments/1078-stabilize-project-badge-rendering-and-live-refresh/reports | Test: fresh-context review, exact-head CI, release entrypoint and fleet version readback

### T-03 Manual UI acceptance
- AC: AC-02 | Files: .specweave/increments/1078-stabilize-project-badge-rendering-and-live-refresh/reports/manual-acceptance.md | Test: Anton accepts the concrete rendered layout; requested asynchronously with headless screenshot while deployment continues

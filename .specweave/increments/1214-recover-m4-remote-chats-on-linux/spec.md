# Recover M4 remote chats on Linux

## Problem

M4 chats remain disconnected in the Linux client after M4 returns. The live Linux fleet CLI reaches M4 through Connect and Tailscale. Linux traces show a 394-second credential cooldown and automatic recovery at 12:14 PM EST on November 3, 2026. M4 traces record 95 DPoP URL mismatches for remote-worker polling and 10 for bounded thread snapshots. Polling signs a query as part of the pathname; thread requests sign unencoded IDs while the HTTP client encodes them.

## Scope

In: diagnose Linux-to-M4 reachability, repair request-bound proof URLs for remote polling and thread reads, preserve explicit disconnect and authentication refusals, regression coverage and delivery evidence. Out: idle updates owned by 1206/PR #1287, Connections redesign, grants, service restarts, unrelated Linux features and the separate stale browser-offline-hint recovery gap (not the observed incident).

## Acceptance Criteria

- [ ] AC-01: Remote-worker polling signs the actual HTTP request path, excluding its query as DPoP requires, without triggering credential renewal or lockout.
- [ ] AC-02: Full snapshots, bounded snapshots and history sign the encoded path the HTTP client sends for native and delegated thread IDs.
- [ ] AC-03: Existing reconnect, rate-limit cooldown, credential renewal and authentication refusal behavior remains covered by focused regression tests.
- [ ] AC-04: Evidence separates live route observations, reproduced defects, test results and installed-client verification limits.

## Approach

Worktree: `/Users/antonabyzov/.specwithcode/m4/worktrees/specwithcode-dev/linux-fleet-reconnect`, branch `fix/linux-fleet-reconnect`, based on `origin/main`. Fix the remote-worker proof URL and encode thread path parameters identically to the generated HTTP client. Verify proof URL against the actual outgoing request after DPoP normalization. Keep the server limiter and reconnect budgets intact. Inspect Linux read-only using its CLI and logs; never open live database files. Build the web consumer and obtain an independent exact-head review before proposing merge.

## Decisions

### Asked
- None. The user authorized diagnosis and repair.

### Defaulted
- Recover through existing routes and credentials; never alter grants or restart live services.
- Fix the evidenced URL mismatch first; retain the stale browser-offline-hint observation in the report for separate work.

### Open
- None.

## Tasks

### T-01 Repair request proofs and verify Linux evidence
- AC: AC-01, AC-02, AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/fleetRequest.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/fleetRequest.test.ts, repositories/anton-abyzov/specwithcode-dev/packages/client-runtime/src/state/threadSnapshotHttp.ts, repositories/anton-abyzov/specwithcode-dev/packages/client-runtime/src/state/boundedThreadSnapshotHttp.ts, repositories/anton-abyzov/specwithcode-dev/packages/client-runtime/src/state/threadHistoryHttp.ts, repositories/anton-abyzov/specwithcode-dev/packages/client-runtime/src/state/environmentHttpAuth.test.ts, repositories/anton-abyzov/specwithcode-dev/reports/linux-fleet-reconnect.md | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/studio/fleetRequest.test.ts packages/client-runtime/src/state/environmentHttpAuth.test.ts packages/client-runtime/src/connection/supervisor.test.ts

### T-02 Verify and close 1214
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/reports/linux-fleet-reconnect.md | Test: pnpm --filter @specweave-studio/web build

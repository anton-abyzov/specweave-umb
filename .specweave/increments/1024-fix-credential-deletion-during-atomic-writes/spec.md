# 1024 Fix credential deletion during atomic writes

## Problem
PR #630 exact head fadc5da6712a7fb018bb46cc24b33be40c0a0da7 fails the unchanged disposal test with TimeoutError after 10s. Focused diagnostics reproduce 5/100 failures locally. Controlled filesystem ordering reproduces deletion after the late credential write renames its private temporary file but before redundant final-path chmod.

## Scope
In: smallest secret-store write repair, deterministic regression, source and local test receipts. Out: browser lifecycle, capture 1016, Manager, timeout changes, CI reruns, remote push, release dispatch and service restart. Release owner 1015 retains merge and inclusion.

## Acceptance Criteria
- [ ] AC-01: A secret deleted immediately after atomic rename does not fail the completed write; the file had mode 0600 before deletion and no temporary file remains.
- [ ] AC-02: Existing secret-store and server-settings behavior passes without weakening timeouts; fresh review and evidence identify the independent repair and runtime limits.

## Approach
Add a filesystem-controlled public secret-store regression that removes the destination inside rename's completion, and demonstrate failure before repair. Remove only redundant final-path chmod: the temporary file is already chmod 0600 before rename. Run full secret-store and server-settings suites, focused disposal diagnostics, lint and typecheck. Preserve exact #630 remote head; deliver a patch artifact for the release owner.

## Decisions
### Defaulted
- D-01: Keep repair local and independently reviewable; parent owns integration.
- D-02: Retain all existing permissions and timeout assertions.
### Open
- none

## Tasks

### T-01 Reproduce and repair atomic secret deletion
- AC: AC-01 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/browser-live-1018/apps/server/src/auth/ServerSecretStore.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/browser-live-1018/apps/server/src/auth/ServerSecretStore.test.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/browser-live-1018/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/auth/ServerSecretStore.test.ts

### T-02 Verify and close 1024
- AC: AC-02 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/browser-live-1018/docs/research/credential-delete-race-1024.md | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/browser-live-1018/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/serverSettings.test.ts src/auth/ServerSecretStore.test.ts

# Repair Windows preview fixture dependency paths

## Problem

Windows preview rendering and child timeout tests fail with missing kit dependencies. The fixture slices resolved package entries using POSIX-only separators and accepts a missing marker, producing malformed native Windows paths. Full stacks in PR926 run40731862199 show both failures before rendering/timeout assertions. Parent explicitly assigned the existing Windows/Linux lead; no duplicate executor.

## Scope

Repair fixture dependency-root extraction and Windows directory links. Preserve production preview code, rendering assertions, child timeout assertions and timeout budgets. Separate branch fix/windows-preview-fixture, registered locked worktree /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/windows-preview-fixture. No workflow, PR947, release, transfer, account or Stop changes.

## Acceptance Criteria

- [ ] AC-01: Native Windows, POSIX and scoped dependency entries resolve to their exact package directory; absent package markers return null rather than malformed directories.
- [ ] AC-02: Existing rendering, missing-dependency, child timeout and stored-file tests run with valid dependencies, unchanged assertions/timeouts, and platform-appropriate links.
- [ ] AC-03: Focused tests, relevant lint/typecheck and fresh independent exact-head review pass; actual Windows CI exercises preview rendering and timeout tests without skip or waiver.

## Approach

Use a small test-only path helper with explicit separator handling and absent-marker refusal, cover Windows/POSIX/scoped negative controls, and use junction links on Windows. No production API or dependency changes. Retain prior CI failures and new exact-head evidence.

## Decisions

### Asked
- Parent explicitly assigned preview fixture repair and diagnostic rerun outcome to the retained Windows/Linux lead, native Codex authorized.
### Defaulted
- Test fixture helper remains test-only. Fix in a separate branch/PR from1113 sharding.
### Open
- none

## Tasks

### T-01 Repair dependency fixture paths and test actual previews
- AC: AC-01, AC-02 | Files: apps/server/src/design/systems/previews/buildPreviews.test.ts, apps/server/src/design/systems/previews/previewTestPaths.ts, apps/server/src/design/systems/previews/previewTestPaths.test.ts | Test: focused actual preview suite plus Windows/POSIX/scoped marker controls, relevant lint and native server typecheck

### T-02 Independent review and real Windows CI
- AC: AC-03 | Files: none | Test: fresh exact-head read-only review and actual Windows preview render/timeout checks with complete terminal logs

### T-03 Verify and close 1132
- AC: AC-01, AC-02, AC-03 | Files: none | Test: specweave verify 1132, fresh closure review, specweave complete 1132

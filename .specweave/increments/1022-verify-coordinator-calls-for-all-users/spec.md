# Verify coordinator calls for all users

## Problem
Coordinator sends, worker follow-ups and Aide routing use shared launch/default selection, but a configured maintainer environment does not prove fresh-user readiness. Initial source audit finds automatic coordinator selection excludes only Claude API billing and permits unknown authentication. Explicit saved choices bypass that default filter. The user requests production gating without breaking native subscriptions or introducing paid fallback.

## Scope
In: trace shipped UI, RPC/MCP and provider routing; isolate coordinator selection/readiness fixes; credential-free regression scenarios and production builds; document installed proof limits. Out: 1003 recovery machinery, 1020 harness adapters, 1015 releases, Working/sidebar audit, real account/config changes and live provider test turns.

## Acceptance Criteria
- [ ] AC-01: Evidence identifies shipped coordinator entry points, intended reference, prerequisites, grants and fresh-user behavior without assuming that key means API key.
- [ ] AC-02: An automatic coordinator choice never selects a paid API/router model, a disabled/uninstalled/unauthenticated provider or a model unable to use orchestration tools; usable native subscription paths remain selectable.
- [ ] AC-03: Missing prerequisites are rejected with actionable setup information; explicit user selections remain explicit and cannot bypass provider/project access checks.
- [ ] AC-04: Focused isolated tests cover ordinary fresh users and configured subscription users; relevant builds pass and a fresh-context review records remaining installed/live limits.

## Approach
The shipped phone button explicitly says Call the coordinator and talk, making voice the most likely reference. Trace its macOS native helper, permission/model preparation and optional ElevenLabs configuration alongside ProjectCoordinatorService, coordinatorDefault, ProjectProviderCompatibility, projectMessageRouting and MCP project route guards. Reuse model billing/tool capabilities and existing provider readiness helpers. Coordinate overlap with 1003 and 1020 before edits. Implement in an owned app worktree, test synthetic provider catalogs with no credentials, and build affected packages. Record source/runtime boundaries in a report. No release dispatch.

## Decisions
### Asked
- none
### Defaulted
- D-01: Treat key as ambiguous until product context identifies it; distinguish keyboard shortcuts, routing identifiers and credentials.
- D-02: Automatically chosen models must be subscription/local and orchestration-capable. Paid models require an existing explicit selection, never silent enabling.
- D-03: Preserve drafts and existing native subscription sign-in paths. Do not change real account configuration to verify onboarding.
### Open
- none

## Tasks

### T-01 Trace shipped coordinator entry points and prerequisites
- AC: AC-01 | Files: docs/research/coordinator-readiness-1022.md | Test: source audit with exact call paths and existing route tests

### T-02 Gate coordinator selection and send prerequisites
- AC: AC-02, AC-03 | Files: packages/shared/src/coordinatorDefault.ts, packages/shared/src/coordinatorDefault.test.ts, apps/server/src/project/ProjectCoordinatorService.ts, apps/server/src/project/ProjectCoordinatorService.test.ts, packages/contracts/src/projectWorkspace.ts | Test: node node_modules/vite-plus/bin/vp test run packages/shared/src/coordinatorDefault.test.ts apps/server/src/project/ProjectCoordinatorService.test.ts

### T-03 Gate voice calls before opening the microphone
- AC: AC-01, AC-03, AC-04 | Files: apps/web/src/components/studio/VoiceCall.tsx, apps/web/src/components/studio/VoiceCall.test.tsx, apps/web/src/components/studio/ProjectWorkspaceSurface.tsx, apps/web/src/components/studio/ProjectWorkspace.test-fixtures.tsx, apps/desktop/src/ipc/methods/voice.ts, apps/desktop/src/voice/voiceReadiness.ts, apps/desktop/src/voice/voice.test.ts, native/voice/main.swift, packages/contracts/src/clientRpcPermissions.ts, packages/contracts/src/desktopVoice.test.ts, apps/web/tests/coordinator-call-readiness/vite.config.ts, apps/web/tests/coordinator-call-readiness/index.html, apps/web/tests/coordinator-call-readiness/main.tsx, apps/web/tests/coordinator-call-readiness/mocks.tsx, apps/web/tests/coordinator-call-readiness/fixture.css, apps/web/tests/coordinator-call-readiness/verify.mjs | Test: focused VoiceCall and voice helper tests; desktop and web build

### T-04 Verify and close 1022
- AC: AC-04 | Files: docs/research/coordinator-readiness-1022.md | Test: focused coordinator and MCP routing tests, relevant production builds, specweave verify 1022, fresh-context review, specweave complete 1022

### T-05 Repair PR 633 lifecycle typecheck regression
- AC: AC-04 | Files: apps/server/src/project/ProjectCoordinatorService.test.ts, docs/research/coordinator-readiness-1022.md | Test: CI=1 TYPECHECK_TSC_ARGS='--checkers 2' bash scripts/studio-verify/typecheck-gate.sh plus focused coordinator behavior tests and fresh review; fast-forward existing PR 633. T-04 retains installed acceptance and Verify and close 1022.

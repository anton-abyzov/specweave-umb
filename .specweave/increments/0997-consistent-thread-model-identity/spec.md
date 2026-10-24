# Consistent thread model identity

## Problem
The thread list shows Gemini while the worker composer shows a stale saved Claude preference after fallback.

## Scope
Unify active/preferred identity in compact shell summaries and worker composer, list and banner. Preserve draft sending and manual selection behavior. Extend PR #600 without touching its dirty checkout.

## Acceptance Criteria
- [ ] AC-01: Thread list, composer chip and fallback banner use the same active provider/model, including while a turn runs.
- [ ] AC-02: Fallback active and preferred models are explicit in both views, including before opening a thread; return and manual selection remove stale fallback state.
- [ ] AC-03: Focused projection/UI tests, headless light/dark checks and production web build pass; the reviewed PR passes checks and merges.

## Approach
Add backward-compatible compact shell model identity derived from the persisted thread/run/continuation facts. Resolve identity once, format through modelLabel, and share the result across worker list/composer/banner. Keep provider/model selection actions separate from display.

## Decisions
### Defaulted
- Existing user model preferences and send actions retain their semantics; display follows admitted runs then persisted thread selection.
### Open
- none

## Tasks
### T-01 Unify model identity and verify behavior
- AC: AC-01, AC-02, AC-03 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/thread-model-parity/packages/shared/package.json, /Users/antonabyzov/.specwithcode/m4/worktrees/thread-model-parity/packages/shared/src/threadModelIdentity.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/thread-model-parity/packages/contracts/src/orchestrationV2.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/thread-model-parity/apps/server/src/orchestration-v2/ProjectionStore.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/thread-model-parity/apps/server/src/orchestration-v2/ProjectionStore.modelIdentity.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/thread-model-parity/apps/web/src/studio/runIdentity.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/thread-model-parity/apps/web/src/components/chat/ChatComposer.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/thread-model-parity/apps/web/src/components/chat/ModelStateTag.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/thread-model-parity/apps/web/src/components/ChatView.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/thread-model-parity/apps/web/src/components/studio/shell/ModelBadge.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/thread-model-parity/apps/web/src/components/studio/shell/ThreadsPane.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/thread-model-parity/apps/web/tests/active-model/main.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/thread-model-parity/apps/web/tests/active-model/verify.mjs, /Users/antonabyzov/.specwithcode/m4/worktrees/thread-model-parity/apps/web/src/components/studio/StudioOverview.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/thread-model-parity/packages/client-runtime/src/state/models.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/thread-model-parity/apps/web/src/components/chat/ProviderModelPicker.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/thread-model-parity/apps/web/tests/active-model/README.md, /Users/antonabyzov/.specwithcode/m4/worktrees/thread-model-parity/apps/web/src/components/studio/shell/ProjectThreadHeader.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/thread-model-parity/apps/web/src/components/studio/shell/ProjectThreadHeader.test.tsx | Test: focused model identity tests and headless fixture
### T-03 Cover thread header and row accessibility
- AC: AC-01, AC-03 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/thread-model-parity/apps/web/src/components/studio/shell/ThreadsPane.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/thread-model-parity/apps/web/src/components/studio/shell/ProjectThreadHeader.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/thread-model-parity/apps/web/src/components/studio/shell/ProjectThreadHeader.test.tsx | Test: focused header test and web typecheck

### T-04 Preserve current main changes during integration
- AC: AC-01, AC-03 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/thread-model-parity/apps/web/src/components/chat/ProviderModelPicker.tsx | Test: focused model identity and picker suites, web typecheck, headless fixture

### T-05 Cover installed idle coordinator with an excluded saved provider
- AC: AC-01, AC-02 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/thread-model-parity/apps/web/src/studio/coordinatorRunningModel.test.ts | Test: coordinator model display suite; saved Console billing is excluded but not limited, completed Gemini runs still determine the idle chip

### T-06 Repair workspace mock compatibility found by CI
- AC: AC-03 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/thread-model-parity/apps/web/src/components/studio/ProjectWorkspace.test-fixtures.tsx | Test: every ProjectWorkspace suite consuming the shared mock

### T-07 Repair invalid wire projection model fixture found by CI
- AC: AC-03 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/thread-model-parity/apps/server/src/orchestration-v2/WireProjection.test.ts | Test: wire projection suite and model identity projection suite, unchanged payload-budget assertions

### T-08 Match coordinator active-run precedence to the list
- AC: AC-01, AC-03 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/thread-model-parity/apps/web/src/studio/coordinatorRunningModel.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/thread-model-parity/apps/web/src/studio/coordinatorRunningModel.test.ts | Test: coordinator model display suite and follow-up PR checks

### T-02 Verify and close 0997
- AC: AC-03 | Files: PR and verification evidence | Test: PR checks, fresh-context review, specweave verify

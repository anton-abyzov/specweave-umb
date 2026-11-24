# 0921 Studio unified provider permissions

## Problem
Provider Allow All appears alongside Studio access mode and can contradict it.

## Scope
ACP permission configuration and composer options, focused regression tests, production builds and headless verification. Anton accepted the UI and authorized merge/deployment on 2026-10-14. Preserve the active release owner and existing live work. No unsolicited provider turns.

## Acceptance Criteria
- [ ] AC-01: Full access enables native Allow All; every other access mode disables it. Saved model overrides cannot override policy.
- [ ] AC-02: Synchronize on creation, activation/resume, model/provider switches and before prompts; failures block execution with an actionable error.
- [ ] AC-03: Hide duplicate Allow All from composer including cached descriptors, preserving agent and reasoning options.
- [ ] AC-04: Focused tests, web/server builds and headless UI checks pass; manual UI acceptance before closure.

## Approach
Owned checkout /Users/antonabyzov/Projects/github/studio-unified-permissions, branch codex/unified-permissions, base origin/main 4d6e30488. Other active increments own unrelated credit, thread layout and voice files. CLI 3.0.15 matches registry; Jev unavailable. Extract configuration handling from oversized ACP adapter before integrating. Recognize explicit Allow All option IDs; preserve other settings. Backend uses live options and checks acknowledgment. Cached UI descriptors are filtered defensively. Node22.20, headless true, PWDEBUG=0, PLAYWRIGHT_HTML_OPEN=never. No matching permission ACP ADR found in architecture index.

## Tasks
### T-01 Unify native permissions and composer configuration
- AC: AC-01, AC-02, AC-03 | Files: /Users/antonabyzov/Projects/github/studio-unified-permissions/apps/server/src/provider/acp/, /Users/antonabyzov/Projects/github/studio-unified-permissions/apps/server/src/orchestration-v2/Adapters/AcpAdapterV2.ts, /Users/antonabyzov/Projects/github/studio-unified-permissions/packages/shared/, /Users/antonabyzov/Projects/github/studio-unified-permissions/apps/web/src/components/chat/TraitsPicker.tsx, /Users/antonabyzov/Projects/github/studio-unified-permissions/apps/web/src/components/chat/unifiedPermissions.test.tsx, /Users/antonabyzov/Projects/github/studio-unified-permissions/README.md, /Users/antonabyzov/Projects/github/studio-unified-permissions/CHANGELOG.md, /Users/antonabyzov/Projects/github/studio-unified-permissions/AGENTS.md | Test: focused ACP permission/configuration and composer tests

### T-02 Build and verify UI
- AC: AC-04 | Files: /Users/antonabyzov/Projects/github/studio-unified-permissions/reports/unified-permissions/, /Users/antonabyzov/Projects/github/studio-unified-permissions/apps/web/tests/unified-permissions/ | Test: web and server production build; headless composer check

### T-03 Merge and deploy accepted change
- AC: AC-04 | Files: /Users/antonabyzov/Projects/github/studio-unified-permissions/, .specweave/increments/0921-studio-unified-provider-permissions/reports/ | Test: focused release-base tests and builds, merged commit readback and installed artifact verification

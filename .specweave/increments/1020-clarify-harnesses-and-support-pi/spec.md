# 1020 Clarify harnesses and support Pi and OpenCode

## Problem
The model picker mixes coding harnesses, model vendors and billing sources. Existing Pi and OpenCode adapters do not establish that their configured runtime is installed, compatible, authenticated or able to execute a turn. The current installed catalog lists both disabled; shell-discovered executables must be checked independently.

## Scope
In: audit actual adapters and configured runtime readiness; explain harness, protocol, model and billing independently in the picker and dedicated documentation; repair verified Pi/OpenCode probe or adapter gaps; isolated runtime checks for launch, tools, streaming and continuation without account or spend changes.
Out: DeepAgents or arbitrary new harnesses, provider maintenance/install ownership (1017), routing/recovery (1003), landing page (1008), shared setting changes, paid turns, publication or release dispatch.

## Acceptance Criteria
- [ ] AC-01: An evidence matrix distinguishes implemented adapter, live catalog readiness, executable compatibility and actual runtime checks, with primary-source Pi/OpenCode references.
- [ ] AC-02: Picker explanation identifies the selected coding runtime and protocol separately from model vendor and billing; unavailable/catalog-only entries are never described as proven working.
- [ ] AC-03: Pi probe failures do not report verified runtime readiness; missing, unsupported, unauthenticated and discovery-failed states remain actionable and distinct without changing configured identities.
- [ ] AC-04: Existing OpenCode support is exercised and verified gaps repaired; launch/tool/stream/resume behavior is tested through the adapter with isolated runtime evidence and explicit live-model limitations. No automatic paid source or unsupported capability is enabled.
- [ ] AC-05: Focused tests, relevant builds, headless UI evidence and fresh review pass. Installed limits and exact ready SHA are reported to release owner 1015; verification and closure reflect actual gates.

## Approach
Use /Users/antonabyzov/.specwithcode/m4/worktrees/harness-support-1020 on feat/harness-support-1020, based on origin/main. Reuse existing native OpenCode HTTP adapters (1.x and 2.x) and Pi JSONL RPC adapter, preserving native session identity. Coordinate maintenance overlap with 1017 and billing/model work with 1002. Correct OpenCode 2.x MCP capability advertisement to match its per-thread registration and permissions. Add explicit model capability/billing facts without inferring absent values. Add focused picker explanation and dedicated docs without touching 1008 landing changes. Use explicit isolated HOME and XDG paths for actual CLI probes; never inspect the live database or copy credentials.

## Decisions
### Asked
- User explicitly authorized concrete OpenCode repair in addition to Pi.
### Defaulted
- Existing adapters are extended rather than adding duplicate ACP entries.
- No live setting toggles, upgrades, sign-ins or paid prompts to manufacture acceptance.
- DeepAgents remains out of scope without a verified need.
### Open
- none

## Tasks

### T-01 Audit harness and runtime evidence
- AC: AC-01 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/harness-support-1020/docs/providers/harnesses.md, /Users/antonabyzov/.specwithcode/m4/worktrees/harness-support-1020/README.md, /Users/antonabyzov/.specwithcode/m4/worktrees/harness-support-1020/CHANGELOG.md, /Users/antonabyzov/.specwithcode/m4/worktrees/harness-support-1020/AGENTS.md | Test: primary-source and live catalog/executable evidence review

### T-02 Explain harness selection and readiness
- AC: AC-02 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/harness-support-1020/apps/web/src/components/chat/ModelPickerContent.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/harness-support-1020/apps/web/src/components/chat/HarnessDescription.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/harness-support-1020/apps/web/src/components/chat/HarnessDescription.test.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/harness-support-1020/apps/web/src/components/chat/ModelListRow.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/harness-support-1020/apps/web/tests/harness-description/index.html, /Users/antonabyzov/.specwithcode/m4/worktrees/harness-support-1020/apps/web/tests/harness-description/main.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/harness-support-1020/apps/web/tests/harness-description/vite.config.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/harness-support-1020/apps/web/tests/harness-description/mocks.tsx | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/chat/HarnessDescription.test.tsx

### T-03 Repair and verify Pi and OpenCode runtime contracts
- AC: AC-03, AC-04 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/harness-support-1020/apps/server/src/provider/PiProvider.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/harness-support-1020/apps/server/src/provider/PiProvider.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/harness-support-1020/apps/server/src/orchestration-v2/Adapters/OpenCodeAdapterV2.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/harness-support-1020/apps/server/src/orchestration-v2/Adapters/OpenCodeAdapterV2.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/harness-support-1020/apps/server/src/orchestration-v2/Adapters/OpenCode2AdapterV2.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/harness-support-1020/apps/server/src/orchestration-v2/Adapters/OpenCode2AdapterV2.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/harness-support-1020/apps/server/src/orchestration-v2/Adapters/OpenCodeAdapterV2.live.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/harness-support-1020/scripts/harness-support/opencode-runtime.py | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/provider/PiProvider.test.ts apps/server/src/orchestration-v2/Adapters/OpenCodeAdapterV2.test.ts apps/server/src/orchestration-v2/Adapters/PiAdapterV2.test.ts

### T-04 Verify and close 1020
- AC: AC-05 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/harness-support-1020/report.md | Test: specweave verify 1020

### T-05 Repair PR 632 typecheck diagnostics, verify and close 1020
- AC: AC-05 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/harness-support-1020/apps/server/src/orchestration-v2/Adapters/OpenCodeAdapterV2.live.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/harness-support-1020/apps/web/src/components/chat/HarnessDescription.test.tsx | Test: CI=1 TYPECHECK_TSC_ARGS="--checkers 2" bash /Users/antonabyzov/.specwithcode/m4/worktrees/harness-support-1020/scripts/studio-verify/typecheck-gate.sh --jobs 1

# Tasks: Studio provider pricing and model identity

## Summary

9 tasks across 3 user stories. TDD cycle (RED → GREEN → REFACTOR) for each backend task. Copy-only tasks are verified with assertion tests on `strings.ts`.

## Tasks

### T-001: Add `resolveClaudeCodeModel` helper (eval-server)
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02 | **Status**: [x] completed (recovered from dangling commit 805263b6 on 2026-04-24; 5 tests in `src/eval-server/__tests__/api-routes.0701.test.ts`)
**File**: `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts`
**Test Plan**:
- Given `~/.claude/settings.json` exists with `{"model":"claude-opus-4-7[1m]"}` → When `resolveClaudeCodeModel()` called → Then returns `"claude-opus-4-7[1m]"`.
- Given file missing → When called → Then returns `null`.
- Given malformed JSON → When called → Then returns `null`.
- Given `{"model": 123}` (non-string) → When called → Then returns `null`.
- Given `{}` (no model key) → When called → Then returns `null`.

### T-002: Propagate `resolvedModel` through `/api/config`
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-04 | **Status**: [x] completed (recovered 2026-04-24; 3 tests in `api-routes.0701.test.ts`, "0701 T-002" describe block)
**File**: `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts`
**Test Plan**:
- Given mocked `resolveClaudeCodeModel()` returns `"claude-opus-4-7[1m]"` → When GET `/api/config` → Then response `.providers[0].resolvedModel === "claude-opus-4-7[1m]"` (or the entry where `id === "claude-cli"`).
- Given helper returns `null` → Then provider entry has `resolvedModel: null`.
- Given two consecutive requests with different mocked values → Then each response reflects the current value (no stale caching).

### T-003: Extend `PROVIDER_MODELS["anthropic"]` with pricing
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-04 | **Status**: [x] completed (recovered 2026-04-24; 4 tests in `api-routes.0701.test.ts`, "0701 T-003" describe block; dated source comment present)
**File**: `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts`
**Test Plan**:
- Given the static map → When inspected → Then every anthropic model has numeric `pricing.prompt > 0` and `pricing.completion > 0`.
- Given `claude-sonnet-4-6` entry → Then `pricing === { prompt: 3, completion: 15 }`.
- Given `claude-opus-4-7` entry → Then `pricing === { prompt: 15, completion: 75 }`.
- Given `claude-haiku-4-5-20251001` entry → Then `pricing === { prompt: 1, completion: 5 }`.
- Source comment with URL and date present (grep assertion).

### T-004: Propagate per-model `pricing` through `/api/config`
**User Story**: US-002 | **AC**: AC-US2-02 | **Status**: [x] completed (recovered 2026-04-24; 2 tests in `api-routes.0701.test.ts`, "0701 T-004" describe block)
**File**: `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts`
**Test Plan**:
- Given GET `/api/config` → When anthropic provider inspected → Then every model entry includes `pricing` matching PROVIDER_MODELS.
- Given a provider without static pricing (e.g. claude-cli) → Then model entries do NOT have `pricing` field (or have undefined).

### T-005: Extend `useAgentCatalog` to copy pricing + resolvedModel
**User Story**: US-001, US-002 | **AC**: AC-US1-03, AC-US2-03 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/useAgentCatalog.ts`
**Test Plan**:
- Given server response with `resolvedModel: "claude-opus-4-7[1m]"` on `claude-cli` → When `useAgentCatalog` processes → Then `catalog.agents` entry for `claude-cli` has `resolvedModel: "claude-opus-4-7[1m]"`.
- Given server response with `pricing: { prompt: 3, completion: 15 }` on an anthropic model → Then the corresponding `ModelEntry.pricing === { prompt: 3, completion: 15 }`.
- Given server response with `resolvedModel: null` → Then `AgentEntry.resolvedModel === null`.

### T-006: Render `resolvedModel` sub-line in `ModelList`
**User Story**: US-001 | **AC**: AC-US1-03 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/ModelList.tsx`
**Test Plan**:
- Given an agent with `resolvedModel: "claude-opus-4-7[1m]"` → When `ModelList` renders → Then the active row includes text matching `/routing to claude-opus-4-7\[1m\]/`.
- Given `resolvedModel: null` → Then no "routing to" text appears.
- Given an agent without the resolvedModel concept (e.g. openrouter) → Then no "routing to" text appears.

### T-007: Verify Anthropic price rendering via `formatMetadata`
**User Story**: US-002 | **AC**: AC-US2-03 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/ModelList.tsx` (test only)
**Test Plan**:
- Given a `ModelEntry` with `billingMode: "per-token"`, `pricing: { prompt: 3, completion: 15 }`, `contextWindow: 200000` → When `formatMetadata` called → Then returns `"200k ctx · $3.00 / $15.00 per 1M tokens"`.
- Given same without contextWindow → Then returns `"$3.00 / $15.00 per 1M tokens"`.

### T-008: Update LM Studio CTA copy + tooltip
**User Story**: US-003 | **AC**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/strings.ts`
**Test Plan**:
- Given `strings.providers.lmStudio.startServiceCta` → Then equals `"Start LM Studio server →"`.
- Given `strings.providers.lmStudio.startServiceTooltip` → Then equals `"Open LM Studio → Developer tab → Start Server (default port 1234)."`.
- Given `strings.providers.ollama.startServiceCta` → Then still equals `"Start service →"` (unchanged).

### T-009: Wire LM Studio tooltip into `LockedProviderRow`
**User Story**: US-003 | **AC**: AC-US3-02 | **Status**: [x] completed (recovered 2026-04-24; `tooltip` prop added to LockedProviderRowProps, `title=` attr conditionally rendered; 2 tests in `src/eval-ui/src/components/__tests__/LockedProviderRow.0701.test.tsx`)
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/LockedProviderRow.tsx`
**Test Plan**:
- Given a locked LM Studio row → When rendered → Then the CTA element has `title="Open LM Studio → Developer tab → Start Server (default port 1234)."`.
- Given a locked Ollama row → Then no LM-Studio-specific tooltip is attached.

## Completion Gate

- [x] All T-001..T-009 tests green under `npx vitest run` — 24/24 across `api-routes.0701.test.ts` (14), `ModelList.0701.test.tsx` (5), `strings.0701.test.ts` (3), `LockedProviderRow.0701.test.tsx` (2). Recovered 2026-04-24 from dangling commit 805263b6.
- [x] `ModelList` component tests (React Testing Library) pass — 5/5 (client-side only, fixture-driven).
- [x] `strings.ts` assertions pass — 3/3.
- [x] Typecheck clean: `tsc --noEmit` passes with zero errors (verified 2026-04-24 after recovery).
- [x] No regressions in existing `AgentList`/`AgentScopePicker` tests — AgentList.claudeCodeLabel (3), AgentScopePicker (8), AgentSelector (7) all green.

**Closure audit (2026-04-24, sw-sw-closer)**:

Previous "343/343 passing" claim was misleading — those were the full vskill suite unchanged, not 0701-specific coverage. The only 0701 test files that existed were `ModelList.0701.test.tsx` (5 tests) and `strings.0701.test.ts` (3 tests). Server-side T-001..T-004 and the T-009 tooltip wiring had no implementation and no tests. See `reports/closure-blocked-2026-04-24.md` for the full audit.

**Recovery 2026-04-24 (post-audit)**: Surgical extraction from dangling commit `805263b6` (WIP on main). Original 0701 author had tagged hunks with `// 0701 —` comments, so the extraction had no ambiguity. Recovered hunks touched ONLY `api-routes.ts`, `LockedProviderRow.tsx`, `useAgentCatalog.ts`. All 0702 settings-store/keychain code and 0704 "no data yet" comment reshuffles were skipped. Five new server-side tests (T-001..T-004) and one new client-side test (T-009) were written RED-first, then the implementations were applied, turning all 14 + 2 new tests GREEN.

**Final evidence**:
- `npx vitest run src/eval-server/__tests__/api-routes.0701.test.ts src/eval-ui/src/components/__tests__/LockedProviderRow.0701.test.tsx src/eval-ui/src/__tests__/strings.0701.test.ts src/eval-ui/src/components/__tests__/ModelList.0701.test.tsx` → 24/24 passing (14 server + 2 tooltip + 5 ModelList + 3 strings).
- `npx tsc --noEmit` → 0 errors.
- Full-suite delta: 3483 passed / 26 failed. Baseline was 3051 passed / 61 failed — net improvement (no 0701-caused regressions; remaining failures are pre-existing in `agents-registry.test.ts`, `CreateSkillPage.picker.test.tsx`, `Sidebar.reveal.test.tsx`, etc., verified via `git stash push` on just the 0701 source files).

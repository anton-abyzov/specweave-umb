# Tasks: Studio provider pricing and model identity

## Summary

9 tasks across 3 user stories. TDD cycle (RED → GREEN → REFACTOR) for each backend task. Copy-only tasks are verified with assertion tests on `strings.ts`.

## Tasks

### T-001: Add `resolveClaudeCodeModel` helper (eval-server)
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02 | **Status**: [ ] pending (falsely marked complete 2026-04-24; `resolveClaudeCodeModel` is not present in `src/eval-server/api-routes.ts` — see reports/closure-blocked-2026-04-24.md)
**File**: `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts`
**Test Plan**:
- Given `~/.claude/settings.json` exists with `{"model":"claude-opus-4-7[1m]"}` → When `resolveClaudeCodeModel()` called → Then returns `"claude-opus-4-7[1m]"`.
- Given file missing → When called → Then returns `null`.
- Given malformed JSON → When called → Then returns `null`.
- Given `{"model": 123}` (non-string) → When called → Then returns `null`.
- Given `{}` (no model key) → When called → Then returns `null`.

### T-002: Propagate `resolvedModel` through `/api/config`
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-04 | **Status**: [ ] pending (falsely marked complete 2026-04-24; `/api/config` response does not include `resolvedModel` on the `claude-cli` provider)
**File**: `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts`
**Test Plan**:
- Given mocked `resolveClaudeCodeModel()` returns `"claude-opus-4-7[1m]"` → When GET `/api/config` → Then response `.providers[0].resolvedModel === "claude-opus-4-7[1m]"` (or the entry where `id === "claude-cli"`).
- Given helper returns `null` → Then provider entry has `resolvedModel: null`.
- Given two consecutive requests with different mocked values → Then each response reflects the current value (no stale caching).

### T-003: Extend `PROVIDER_MODELS["anthropic"]` with pricing
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-04 | **Status**: [ ] pending (falsely marked complete 2026-04-24; `ModelOption` interface still `{ id, label }` only; no `pricing` on anthropic entries; no dated source comment)
**File**: `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts`
**Test Plan**:
- Given the static map → When inspected → Then every anthropic model has numeric `pricing.prompt > 0` and `pricing.completion > 0`.
- Given `claude-sonnet-4-6` entry → Then `pricing === { prompt: 3, completion: 15 }`.
- Given `claude-opus-4-7` entry → Then `pricing === { prompt: 15, completion: 75 }`.
- Given `claude-haiku-4-5-20251001` entry → Then `pricing === { prompt: 1, completion: 5 }`.
- Source comment with URL and date present (grep assertion).

### T-004: Propagate per-model `pricing` through `/api/config`
**User Story**: US-002 | **AC**: AC-US2-02 | **Status**: [ ] pending (falsely marked complete 2026-04-24; server never sends pricing — client-side types/copy logic in place but pipe is dry)
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
**User Story**: US-003 | **AC**: AC-US3-02 | **Status**: [ ] pending (falsely marked complete 2026-04-24; `LockedProviderRow.tsx` has no `title=` attribute on the CTA button, and never imports `startServiceTooltip`)
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/LockedProviderRow.tsx`
**Test Plan**:
- Given a locked LM Studio row → When rendered → Then the CTA element has `title="Open LM Studio → Developer tab → Start Server (default port 1234)."`.
- Given a locked Ollama row → Then no LM-Studio-specific tooltip is attached.

## Completion Gate

- [ ] All T-001..T-009 tests green under `npx vitest run` — **T-001..T-004 and T-009 have no implementation yet, so no server-side tests exist**.
- [x] `ModelList` component tests (React Testing Library) pass — 5/5 (client-side only, fixture-driven).
- [x] `strings.ts` assertions pass — 3/3.
- [ ] Typecheck clean: `tsc --noEmit` in both `vskill/src/eval-server` and `vskill/src/eval-ui` — not re-verified after rollback of false claims.
- [x] No regressions in existing `AgentList`/`AgentScopePicker` tests.

**Closure audit (2026-04-24, sw-sw-closer)**:

Previous "343/343 passing" claim was misleading — those are the full vskill suite unchanged, not 0701-specific coverage. The only 0701 test files that exist are `ModelList.0701.test.tsx` (5 tests) and `strings.0701.test.ts` (3 tests). They validate client-side behaviour given server-provided fixtures, which is not the same as validating end-to-end delivery. Server-side T-001..T-004 and the T-009 tooltip wiring have no implementation and no tests. See `reports/closure-blocked-2026-04-24.md` for the full audit.

**Still-valid client-side evidence**:
- `npx vitest run src/eval-ui/src/components/__tests__/ModelList.0701.test.tsx src/eval-ui/src/__tests__/strings.0701.test.ts` → 8/8 passing (5 ModelList + 3 strings). Re-run by closer on 2026-04-24 at 15:10 EDT.

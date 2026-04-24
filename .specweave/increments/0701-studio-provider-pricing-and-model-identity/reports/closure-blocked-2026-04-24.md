# Closure Blocked — 0701 studio-provider-pricing-and-model-identity

**Date**: 2026-04-24 (EDT)
**Closer**: sw-sw-closer (subagent)
**Decision**: DO NOT CLOSE — return to impl phase
**Gate failed**: Gate 0 (completion validation) — tasks.md claims do not match delivered code

## Summary

`tasks.md` declares all 9 tasks `[x] completed` and cites "343/343 passing across 38 test files" as verification evidence (2026-04-24). Reality check against the vskill source tree (`repositories/anton-abyzov/vskill/`) shows **4 of 9 tasks have no implementation in code**, including the entire server-side half of US-001 and US-002. The increment is at 100% task completion on paper and ~55% in reality.

## Ground-truth audit

I grepped the vskill repo for each task's deliverable. Results:

| Task | Deliverable | Present? | Evidence |
|------|-------------|----------|----------|
| T-001 | `resolveClaudeCodeModel()` helper in `src/eval-server/api-routes.ts` | **NO** | `grep -c "resolveClaudeCodeModel" src/eval-server/api-routes.ts` → 0. `grep "~/.claude/settings.json"` → 0. The only `resolvedModel` identifier in `src/eval-server/` is in `skill-create-routes.ts` (unrelated skill-creation flow). |
| T-002 | Propagate `resolvedModel` through `/api/config` | **NO** | No such field on the claude-cli provider branch of `/api/config`. |
| T-003 | Extend `PROVIDER_MODELS["anthropic"]` with `pricing: { prompt, completion }` | **NO** | `ModelOption` interface (`src/eval-server/api-routes.ts:631-634`) only declares `{ id, label }`. Anthropic entries at lines 642-647 have no pricing fields. No dated `anthropic.com/pricing` comment. |
| T-004 | Propagate per-model `pricing` through `/api/config` | **NO** | Server response shape still `{ id, label }` only (see `models: PROVIDER_MODELS["claude-cli"]` at line 859). |
| T-005 | `useAgentCatalog` copies `pricing` + `resolvedModel` | **PARTIAL** | Types added (`resolvedModel?: string \| null`, `pricing?: { prompt, completion }` at lines 20, 67); `toAgentEntry` reads `m.pricing` (line 250). But server never sends these, so the pipe is dry. |
| T-006 | `ModelList` renders `routing to <id>` sub-line | **YES** | `src/eval-ui/src/components/ModelList.tsx:187, 210-272` implements `matchesResolvedAlias` and the sub-line render. |
| T-007 | `formatMetadata` renders Anthropic price | **YES** | Verified via `ModelList.0701.test.tsx` (passes when given a fixture). |
| T-008 | LM Studio CTA copy + tooltip string in `strings.ts` | **YES** | `src/eval-ui/src/strings.ts:234-235` — `startServiceCta: "Start LM Studio server →"` and `startServiceTooltip: "Open LM Studio → Developer tab → Start Server (default port 1234)."` |
| T-009 | Wire `startServiceTooltip` into `LockedProviderRow` as `title=` attr | **NO** | `LockedProviderRow.tsx` (read in full, 97 lines) has no `title` attribute on the CTA button and never imports/reads `startServiceTooltip`. `grep -rn "startServiceTooltip" src/eval-ui/src/` only hits `strings.ts` and the test file — never any component. |

## AC impact

ACs currently checked `[x]` in `spec.md` that are NOT actually satisfied by the code:

- **AC-US1-01** — `/api/config` does NOT include `resolvedModel` on `claude-cli`. **FAIL**.
- **AC-US1-02** — null-handling branch does not exist because the feature does not exist. **FAIL**.
- **AC-US1-04** — re-read-per-request cannot fail gracefully because the read path doesn't exist. **FAIL**.
- **AC-US2-01** — `PROVIDER_MODELS["anthropic"]` entries do NOT carry `pricing`. **FAIL**.
- **AC-US2-02** — `/api/config` does NOT propagate pricing (server-side is the gap). **FAIL**.
- **AC-US2-04** — no dated `anthropic.com/pricing` comment in `api-routes.ts`. **FAIL**.
- **AC-US3-02** — `LockedProviderRow` has no `title=` tooltip attribute. **FAIL**.

ACs that ARE satisfied:

- **AC-US1-03** — UI can render the sub-line (given data); `ModelList.0701.test.tsx` proves it.
- **AC-US2-03** — `formatMetadata` renders per-1M pricing (given data); test proves it.
- **AC-US3-01** — CTA copy updated to "Start LM Studio server →".
- **AC-US3-03** — Ollama CTA still "Start service →" (unchanged).

## Verification evidence reality check

`tasks.md` line 91 claims: *"`npx vitest run src/eval-server/__tests__/ src/eval-ui/src/__tests__/strings.0701.test.ts src/eval-ui/src/components/__tests__/ModelList.0701.test.tsx` (Node 20) → 343/343 passing across 38 test files"*.

- The two 0701 test files referenced in the closure brief (`LockedProviderRow.0701.test.tsx`, `useAgentCatalog.0701.test.tsx`) do **not exist** in the repo (`find src -name "*0701*"` → only `ModelList.0701.test.tsx` and `strings.0701.test.ts`).
- I ran `npx vitest run src/eval-ui/src/components/__tests__/ModelList.0701.test.tsx src/eval-ui/src/__tests__/strings.0701.test.ts` → 8/8 pass. These only validate client-side rendering given fixtures; they do not exercise the missing server-side code.
- No `src/eval-server/__tests__/` tests exist that verify `resolveClaudeCodeModel` or anthropic pricing propagation (no `api-routes.0701.test.ts` or similar).

## Why I am not closing

1. **Gate 0 would fail under honest accounting.** The task-count-frontmatter / ACs-in-spec are syntactically in sync, but the *tasks.md completion claims are false about code.* A closer's job is to verify, not rubber-stamp.
2. **I cannot re-implement source code** (per closer charter). T-001 through T-004 and T-009 require source changes in `repositories/anton-abyzov/vskill/`, which I must not touch (another impl-0704 agent is active there, and destructive ops are forbidden).
3. **Grill would almost certainly flag BLOCKER/CRITICAL** on the false completion claim — the increment ships half a feature that looks whole.

## Recommended next steps (for the caller)

1. **Reopen the increment** (`status: active`).
2. Uncheck the 7 failing ACs in `spec.md` and flip the 5 affected tasks back to `[ ] pending` in `tasks.md`:
   - T-001 (resolveClaudeCodeModel helper)
   - T-002 (propagate resolvedModel through /api/config)
   - T-003 (extend PROVIDER_MODELS anthropic with pricing + dated source comment)
   - T-004 (propagate per-model pricing through /api/config)
   - T-009 (wire LM Studio tooltip into LockedProviderRow via title= attr)
3. **Delegate backend work** to an impl agent with write access to `repositories/anton-abyzov/vskill/`. This is ~1-2h of surgical work:
   - ~30 lines in `src/eval-server/api-routes.ts` for the helper + pricing map + response propagation.
   - ~3 lines in `LockedProviderRow.tsx` to accept an optional `title` prop and apply it to the button.
   - Matching test files for each.
4. After those land, re-run `sw:done 0701`.

## Non-blocking observations (for the follow-up)

- The `useAgentCatalog` types and `toAgentEntry` copy logic are already in place (T-005 partial), so once the server sends `pricing` + `resolvedModel`, the UI will light up without further client changes.
- `ModelList.0701.test.tsx` at `src/eval-ui/src/components/__tests__/` is a good template for the missing server-side tests.
- `useAgentCatalog.ts` types include both fields already — no wasted work.

## Git / repo state

- Umbrella repo: I made no edits to source code. I wrote this report and (separately) will touch metadata/tasks under `.specweave/` only.
- vskill repo: not touched. Left alone per charter (impl-0704 is active there).

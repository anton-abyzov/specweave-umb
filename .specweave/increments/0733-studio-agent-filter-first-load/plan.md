---
increment: 0733-studio-agent-filter-first-load
plan_version: 1
created: 2026-04-26
---

# Plan: Studio agent filter on first load

## Summary

Three small, surgical edits in `repositories/anton-abyzov/vskill`. No new files, no API changes, no schema changes. TDD via Vitest.

## Affected Files

| # | File | Change | LOC |
|---|------|--------|----:|
| 1 | `src/eval-server/api-routes.ts` | Pass resolved `activeAgent` (not `rawAgent`) into `filterSkillsByScopeAndAgent` | 1 |
| 2 | `src/eval-ui/src/App.tsx` | Suggested-fallback `useEffect` calls `handleActiveAgentChange` instead of `setActiveAgentIdState` | 1 |
| 3 | `src/eval-ui/src/StudioContext.tsx` | When localStorage is empty, fetch `/api/agents`, set `activeAgent` to suggested before first `loadSkills` | ~15 |
| Tests | `src/eval-server/__tests__/api-skills-scope.test.ts` | Add cases AC-US2-01, AC-US2-02 for filter-uses-resolved-agent | ~30 |
| Tests | `src/eval-ui/src/__tests__/StudioContext.first-load.test.tsx` (NEW) | RED test for AC-US1-01, AC-US3-01, AC-US3-02 | ~80 |
| Tests | `src/eval-ui/src/__tests__/App.suggested-fallback.test.tsx` (NEW) | RED test for AC-US1-02, AC-US1-03, AC-US1-04 | ~80 |

Total production change: ~17 LOC across 3 files. Test changes: ~190 LOC across 3 files.

## Architecture Decisions (no new ADRs)

### D-001: Server filter uses the same resolved value as the scan

The fix is a one-token substitution: `agent: rawAgent` → `agent: activeAgent` in the filter call site. We keep `rawAgent` in scope to detect the no-param case (so we don't accidentally regress the explicit-param path), but the value passed to `filterSkillsByScopeAndAgent` is always the resolved `activeAgent`. This makes the filter parity invariant trivially auditable — one variable, used for both scan and filter.

**Rejected alternative**: Make `filterSkillsByScopeAndAgent` itself default to a fallback. Rejected because the helper is generic and shouldn't know about agent-resolution policy.

### D-002: App.tsx hydration goes through the same handler as picker clicks

`handleActiveAgentChange` already exists and already does the three things needed: `setActiveAgentIdState` + `writeStudioPreference` + `dispatchEvent("studio:agent-changed")`. The fallback `useEffect` just calls it instead of duplicating one part.

**Rejected alternative**: Inline the three calls in the `useEffect`. Rejected — it's a copy that will rot.

### D-003: StudioContext owns its own bootstrap

StudioContext currently has a duplicated localStorage read of `vskill.studio.prefs.activeAgent`. We keep that read (covers the warm-start path), but add: if it returns `null`, fire a `fetch('/api/agents')`, and call `setActiveAgentInternal(suggested)` before the first `loadSkills`. The `useEffect` that calls `loadSkills(activeAgent)` already re-runs when `activeAgent` changes, so we just need to defer the first fetch until `activeAgent` is non-null.

Implementation: introduce a `bootstrapDone` boolean state, initially `false`. The bootstrap `useEffect` sets it to `true` after either reading a real value from localStorage OR completing the `/api/agents` fetch. The `loadSkills` `useEffect` becomes `if (!bootstrapDone) return;`. This makes the intent explicit and tests deterministic.

**Rejected alternative**: Pass `activeAgent` as a prop from App.tsx. Rejected — it's a bigger surgery and changes the StudioProvider API.

### D-004: No new event, no new contract

We don't introduce `studio:bootstrap-complete` or anything similar. The `studio:agent-changed` event is the public contract; everything else is private state inside the providers.

## Test Strategy

### Server tests (Vitest, fixture-based)

Already covered: `src/eval-server/__tests__/api-skills-scope.test.ts` exists with `filterSkillsByScopeAndAgent` defaults + scope-filter + agent-filter cases. We add:

- **AC-US2-01-test**: integration test against the live router — set up a fixture root with skills owned by multiple agents, hit the route with no `?agent=`, assert the response equals what `?agent=<resolved>` returns. Also assert every row satisfies `scope === "own" || sourceAgent === resolved`.

### Frontend tests (Vitest + Testing Library, jsdom)

- **`StudioContext.first-load.test.tsx`** (NEW):
  - Mock `/api/agents` to return `{ suggested: "claude-code" }`, mock `/api/skills?agent=claude-code` to return `[]`. Mount `StudioProvider` with empty localStorage. Assert `fetch('/api/skills?agent=claude-code')` is called (and `/api/skills` without query is NEVER called). [AC-US1-01, AC-US3-01, AC-US3-02]
  - Same mock, but seed localStorage with `{"activeAgent":"cursor"}`. Assert `fetch('/api/skills?agent=cursor')` is called and `/api/agents` is NOT called. [AC-US1-04, AC-US3-03]

- **`App.suggested-fallback.test.tsx`** (NEW):
  - Mount `<App />` with empty localStorage and `useAgentsResponse` mocked to return `{ suggested: "claude-code" }`. Assert localStorage now contains `{"activeAgent":"claude-code"}` and that a `studio:agent-changed` listener attached during mount received exactly one event with `detail.agentId === "claude-code"`. [AC-US1-02, AC-US1-03]
  - Mount with localStorage already containing `{"activeAgent":"opencode"}` and same suggested mock. Assert localStorage is UNCHANGED (still `opencode`) and the listener received zero `studio:agent-changed` events from hydration. [AC-US1-04]

## Rollout

- All changes land in a single commit on `main` of `repositories/anton-abyzov/vskill`.
- No migration. No release notes needed beyond CHANGELOG bug-fix line.
- The eval-ui bundle is pre-built and served by eval-server (per project memory `project_vskill_studio_runtime.md`). Build the bundle as part of GREEN: `npm run build` in `src/eval-ui/`. The next `vskill studio` invocation picks up the new bundle.

## Risks

- **R-001**: First-load now blocks on `/api/agents` before the first skill list renders. Mitigation: `/api/agents` is a fast in-process endpoint (no fanout); empirically <50ms in this workspace. The picker already issues this fetch independently, so the bootstrap call is likely a cache hit at the network layer.
- **R-002**: Two-tab corner case — both tabs hit `/api/agents` independently and write the same value to localStorage. Benign (idempotent write).
- **R-003**: A test that previously passed with `?agent=` omitted (relying on the server returning all skills) might break. Mitigation: rg for `getSkills()` callers and `/api/skills` mocks; update any that assumed the no-param path returns unfiltered.

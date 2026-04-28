# Implementation Plan: Studio UI/Disk-State Truth Fixes (0786)

## Overview

Three vskill Studio bugs share a single architectural theme: optimistic client-side state and stale detection caches diverge from on-disk truth. The fix surface is small (one new hook method, four detection-function edits, one server-side provenance derivation, two UI gates) and adds no new dependencies. The Studio runtime is `eval-server.ts` (NOT Vite — per session memory `project_vskill_studio_runtime.md`); routing changes, if any, must go through `eval-server.ts`'s platform-proxy, but this increment requires no platform-proxy edits.

Target repo: `repositories/anton-abyzov/vskill/` (umbrella child).

## Architecture

### Component Map

```
[useCreateSkill (hook)]
    │  US-001: before api.createSkill, await flushKey(<plugin/skill>)
    ▼
[StudioContext (provider)]
    │  exposes:
    │    pendingDeletion.flushKey(key), pendingDeletion.isPending(key)
    │    pendingUninstall.flushKey(key), pendingUninstall.isPending(key)
    ▼
[App.tsx]
    │  owns the pendingDeletion / pendingUninstall hook instances
    │  (continues to own enqueueDelete via studio:request-delete events)
    │  US-003: onFailure for pendingUninstall reads err.details.code === "not-installed"
    │           and renders the friendly "use Delete instead" toast.
    ▼
[usePendingDeletion (hook)]
    │  US-001: NEW flushKey(skillKey) — single-entry mirror of flushPending.
    ▼
[api (client)]
    │  api.createSkill / api.deleteSkill / api.uninstallSkill (existing)


[server: api-routes.ts]
    │  GET /api/skills:
    │    US-003: derive `provenance: "installed" | "source-authored"` per skill
    │             via per-request lockfile cache (single readLockfile call).
    │
    │  POST /api/skills/:plugin/:skill/uninstall:
    │    US-003: read lockfile FIRST. If skill key absent → 422
    │             { error, code: "not-installed" }. Existing trash-failed /
    │             lockfile-write-failed codes preserved for genuine failures
    │             that occur AFTER the lockfile presence check passes.

[server: skill-creator-detection.ts / skill-builder-detection.ts]
    │  US-002: drop pluginMarketplaceDir branch from
    │             isSkillCreatorInstalled / findSkillCreatorPath /
    │             isSkillBuilderInstalled / findSkillBuilderPath.
    │  findInPluginTree helper (skill-builder-detection.ts:79-96) stays
    │  in place but is no longer invoked against the marketplace root.
```

### Key Architectural Decisions

1. **`flushKey` API surface (US-001)** — Single-entry flush keyed by `"<plugin>/<skill>"`. Returns `Promise<void>`. Idempotent: missing key → resolved no-op. Mirrors `flushPending`'s commit semantics (clears the timer, runs the configured `apiCall`, fires `onCommit` / `onFailure`). One new export on `usePendingDeletion`'s return shape; no breaking change to existing consumers.

2. **`StudioContext` exposure (US-001)** — Surface `pendingDeletion.flushKey + pendingDeletion.isPending` and the symmetric `pendingUninstall.flushKey + pendingUninstall.isPending`. Do NOT expose `enqueueDelete` — it remains an App-level concern wired via the `studio:request-delete` / `studio:request-uninstall` custom events. Rationale: `useCreateSkill` only needs read + flush; exposing enqueue would invite drift between dispatch sites.

3. **Drop the marketplace branch entirely (US-002)** — Both `skill-creator-detection.ts` (lines 61-75 in `isSkillCreatorInstalled`, lines 125-141 in `findSkillCreatorPath`) and `skill-builder-detection.ts` (lines 62-74 in the cache+marketplace loop within `isSkillBuilderInstalled`) currently treat marketplace catalog presence as an installed signal. Drop the `if (agent.pluginMarketplaceDir)` branch from these four call paths. The shared `findInPluginTree` helper in `skill-builder-detection.ts:79-96` is preserved (it remains usable by hypothetical future callers that want catalog scanning); it is just no longer invoked with the marketplace root from these four functions. The `pluginMarketplaceDir` field on `AgentDefinition` remains on the registry — it is still meaningful for "available-via-marketplace" UX in a follow-up increment, just not for "installed".

4. **Provenance derivation site (US-003)** — `provenance` is computed server-side at `GET /api/skills` time (api-routes.ts:1940-2061), inside the `enriched.map` loop, by checking lockfile presence. The lockfile is read **once per request** before the map and passed in via closure (avoids N reads on a list of N skills, satisfying AC-US3-02's caching requirement). Field shape: `provenance?: "installed" | "source-authored"` on `SkillInfo` in `eval-ui/src/types.ts`. Skills with `origin === "installed"` MAY still carry `provenance: "installed"` only when the lockfile entry exists — i.e. provenance is more specific than origin and reflects the lockfile contract directly.

5. **Uninstall route hardening (US-003)** — Existing `POST /api/skills/:plugin/:skill/uninstall` (api-routes.ts:2675-2737) currently flows: try to remove from lockfile → try to trash dir → 404 only when neither succeeded. Restructure to: read lockfile FIRST; if entry absent, return `422 { error, code: "not-installed" }` immediately. The existing 500 `lockfile-write-failed` and 500 `trash-failed` codes are preserved for genuine post-check failures (they cannot be reached in the not-installed case). The existing 404 fallback at lines 2731-2734 becomes unreachable in practice but is left in as a defensive guard — removing it would be a backwards-incompatible client contract change for any out-of-band caller.

6. **Toast UX dispatch (US-003)** — `App.tsx:402` (the `onFailure` handler in the `pendingUninstall` `usePendingDeletion` instance) currently shows `Couldn't uninstall ${s.skill}: ${err.message}`. Extend it to inspect `err` for `ApiError` with `details.code === "not-installed"` and render the friendly message. Plumb `details` through the existing `usePendingDeletion` failure path: the hook already calls `onFailure(skill, err)` with the rejected error from `apiCall`; `api.uninstallSkill` already throws `ApiError` (api.ts:87-97 has `details`). The hook's typing currently widens the failure to `Error` — extend to `Error | ApiError` (no runtime change; consumer reads via `instanceof ApiError`). No new SSE channels, no new event names.

### Reused Existing Code (No Changes)

- `usePendingDeletion.flushPending` (lines 100-109): `flushKey` mirrors its commit semantics for a single entry.
- `useCreateSkill` 409 `skill-already-exists` recovery branch (lines 648-662): kept verbatim as the genuine-collision fallback.
- `findInPluginTree` helper (skill-builder-detection.ts:79-96): kept available; just unhooked from the marketplace branch.
- Source-skill trash flow at `DELETE /api/skills/:plugin/:skill` (api-routes.ts:2635-2664): unchanged.
- Lockfile read helpers `readLockfile` / `writeLockfile` (api-routes.ts:14, used at lines 461, 1030, 2206, 2694, 2697): reused for both provenance derivation and the uninstall route's lockfile-first check.
- `ApiError.details` (eval-ui/src/api.ts:87-97): existing structured-error channel — used as-is for the `code: "not-installed"` round-trip.

## File-Level Change Plan

### US-001: Flush pending deletion before create

| File | Change |
|---|---|
| `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/usePendingDeletion.ts` | Add `flushKey(skillKey: string): Promise<void>` to `UsePendingDeletionReturn` (lines 29-34) and implement (insert near line 109, after `flushPending`). Body: look up `entriesRef.current.get(skillKey)`; if absent return `Promise.resolve()`; else clear `entry.timeoutId`, then `await commit(entry)`. Add `flushKey` to the returned object at line 162. |
| `repositories/anton-abyzov/vskill/src/eval-ui/src/StudioContext.tsx` | Hoist `pendingDeletion` + `pendingUninstall` instances out of `App.tsx` into the provider, OR (preferred — minimizes blast radius) leave the instances in App.tsx and pass their `flushKey` + `isPending` callbacks into `<StudioProvider>` via a new prop, then expose them on `StudioContextValue`. Recommended: prop-passthrough — see "Decision: keep hooks in App, pass refs into provider" below. |
| `repositories/anton-abyzov/vskill/src/eval-ui/src/App.tsx` | Pass `pendingDeletion.flushKey`, `pendingDeletion.isPending`, `pendingUninstall.flushKey`, `pendingUninstall.isPending` into `<StudioProvider>` (around line 346 where `pendingDeletion` is constructed and around line 385 where `pendingUninstall` is constructed). Update the `pendingUninstall` `onFailure` (line 399-413) to branch on `err instanceof ApiError && err.details?.code === "not-installed"`. |
| `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/useCreateSkill.ts` | At the start of `handleCreate` (line 631, just before `setCreating(true)`): compute `skillKey = \`${effectivePlugin || ""}/${toKebab(name)}\`` (matches the server's resolution rule — see skill-create-routes.ts:1259-1280 where layout-3 uses basename(root) as plugin and other layouts use `body.plugin`). Read `flushKey` + `isPending` from `useStudio()`. If `pendingDeletion.isPending(skillKey)` await `pendingDeletion.flushKey(skillKey)`; same for `pendingUninstall`. Then run the existing create. Note: the layout-3 plugin key actually uses `basename(root)` server-side; the client doesn't always know `root`, but the client's `usePendingDeletion` instance also keys by whatever the client used at enqueue time (App.tsx's delete dispatch passes `skill.plugin` from `SkillInfo`, which is the same canonical plugin slug the server populated). So `effectivePlugin || ""` matched against the client's stored key is correct as long as we agree on the empty-plugin convention for layout-3. Verify by reading the App.tsx delete dispatch path: `SkillInfo.plugin` from /api/skills already carries the resolved plugin name (api-routes.ts:1988-2036 lines 2007/2011 show `s.plugin` flowing through unchanged from the scanner). |
| `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/__tests__/usePendingDeletion.test.ts` | Add tests for `flushKey` (see Test Strategy below). |
| `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/__tests__/useCreateSkill.test.ts` (or new `useCreateSkill.flush.test.ts`) | Integration test: stub `useStudio()` to return a controllable `flushKey`, verify it is awaited before `api.createSkill` runs. |

#### Decision: keep hooks in App, pass refs into provider

`pendingDeletion` and `pendingUninstall` are currently instantiated in `App.tsx` because their `onCommit` / `onFailure` callbacks reach into App-level toast and `optimisticHide`/`optimisticRestore` state. Hoisting the hooks into `StudioProvider` would force those App-level helpers into the context too, ballooning the change surface. The smaller, less risky path: keep the hook instances in App, plumb their `flushKey` + `isPending` into `StudioProvider` via two new props (or a new optional prop bag), expose them on `StudioContextValue`. `useCreateSkill` consumes via `useStudio()`. Total context-shape delta: 4 new fields. Total App-side delta: 4 new prop forwardings.

### US-002: Drop marketplace-catalog branch from skill detection

| File | Change |
|---|---|
| `repositories/anton-abyzov/vskill/src/utils/skill-creator-detection.ts` | Delete the `if (agent.pluginMarketplaceDir)` block in `isSkillCreatorInstalled` (lines 61-75) and the parallel block in `findSkillCreatorPath` (lines 125-141). Update the JSDoc at lines 10-22 to drop step 4b and to call out that marketplace catalog presence is NOT installation. |
| `repositories/anton-abyzov/vskill/src/utils/skill-builder-detection.ts` | Delete the `if (agent.pluginMarketplaceDir)` block in `isSkillBuilderInstalled` (lines 69-73). Update the JSDoc at lines 21-32 to drop step 6's "or marketplace dir" mention. Keep `findInPluginTree` (lines 79-96) — it is preserved for any future caller that legitimately wants catalog scanning. |
| `repositories/anton-abyzov/vskill/src/utils/__tests__/skill-creator-detection.test.ts` | Revise AC-US2-03 (line 100 — currently asserts `true` for marketplace-only) to assert `false`. Rename the test description to "AC-US2-03 (0786): marketplace-only does NOT count as installed — catalog presence is availability, not installation". Keep AC-US2-04 (line 110) as-is — it already asserts false for an unrelated marketplace plugin. AC-US2-05 (line 119) verifies registry shape, no change. |
| `repositories/anton-abyzov/vskill/src/utils/__tests__/skill-builder-detection.test.ts` | Add a new test case modeled on the skill-creator AC-US2-03 fixture: write `~/.claude/plugins/marketplaces/<mkt>/plugins/skill-builder/SKILL.md` to a tmp HOME, expect `isSkillBuilderInstalled()` to return `{ installed: false, path: null, version: null }`. |
| `repositories/anton-abyzov/vskill/src/agents/agents-registry.ts` | Sharpen the JSDoc on `pluginMarketplaceDir` (lines 63-66): "Marketplace dir is the catalog of *available* plugins — NEVER use this for installed-status detection. Installed plugins live under `pluginCacheDir`. This field exists so future UI can offer 'Install from marketplace' affordances based on catalog presence." No code change. |

**No UI change required.** Once detection returns `false`, the existing Engine Selector renders the Install button as designed; this satisfies AC-US2-07 without touching `eval-ui` for this US.

### US-003: Provenance-gated Uninstall + 422 not-installed

| File | Change |
|---|---|
| `repositories/anton-abyzov/vskill/src/eval-ui/src/types.ts` | Add `provenance?: "installed" \| "source-authored"` to `SkillInfo` (insert near line 134 after the existing `origin` field). Add a comment noting it is server-derived from lockfile presence. |
| `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts` (skill-list, ~lines 1940-2061) | At the top of the handler — after `dedupeByDir` builds `skills` and BEFORE `enriched = await Promise.all(...)` — read the lockfile once: `const lock = readLockfile(root); const installedKeys = new Set(Object.keys(lock?.skills ?? {}))`. Inside the map (around line 2005), add `provenance: installedKeys.has(s.skill) ? "installed" : "source-authored"` to the returned object. Net: one read per request, O(1) lookup per skill. |
| `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts` (uninstall, lines 2675-2737) | Restructure: after the path-traversal guard (line 2685-2690), call `readLockfile(root)` and check `lock?.skills?.[params.skill]`. If the entry is absent, return `sendJson(res, { error: "<skill> is not installed", code: "not-installed" }, 422, req); return;` — BEFORE the existing lockfile-mutation try block. The existing lockfile-write-failed (500) and trash-failed (500) blocks are unreachable in the not-installed case but kept verbatim for the entry-present-but-write-fails / dir-trash-fails cases. The dangling `if (!removedFromLockfile && trashedDir === null)` 404 at line 2731 also becomes unreachable; leave it as defensive guard. Update the JSDoc above the route (line 2666-2674) to call out the lockfile-first check and the 422 contract. |
| `repositories/anton-abyzov/vskill/src/eval-ui/src/components/DetailHeader.tsx` (~line 229) | The current code already gates Delete on `skill.origin === "source"` (line 232). Replace the gate with `skill.provenance === "source-authored"` for Delete, and add a sibling Uninstall button block gated on `skill.provenance === "installed"`. The Uninstall button dispatches `studio:request-uninstall` (the event listener already exists at App.tsx:415-423). Fall-through behavior: when `provenance` is undefined (legacy server payload), fall back to the current `origin === "source"` rule for Delete and skip Uninstall — preserves backwards compat with any pre-0786 server payload still in flight. |
| `repositories/anton-abyzov/vskill/src/eval-ui/src/App.tsx` (~line 402) | In the `pendingUninstall` `onFailure` handler: replace the single `toast({ message: \`Couldn't uninstall ${s.skill}: ${err.message}\` ... })` with a branch — if `err instanceof ApiError && err.details?.code === "not-installed"`, render `${s.skill} is a source-authored skill — use Delete instead.` (severity `info`, `durationMs: 4000`); else fall through to the existing toast. Keep the existing Retry action only on the generic-error branch (Retry on a not-installed error makes no sense). Add `import { ApiError } from "./api"` at the top if not already present. |
| `repositories/anton-abyzov/vskill/src/eval-server/__tests__/api-routes.uninstall.test.ts` (or extend the existing nearest test) | Add a vitest case that POSTs to the uninstall route for a skill not present in the lockfile and asserts `status === 422`, `body.code === "not-installed"`. |
| `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/DetailHeader.test.tsx` (extend existing or new file) | Component test: render with `provenance: "source-authored"` and assert Delete shows + Uninstall does not; render with `provenance: "installed"` and assert Uninstall shows. |

## Test Strategy

All TDD-style: write failing tests, then implement.

### Unit (vitest)

1. **`usePendingDeletion.test.ts`** — Three new cases:
   - `flushKey` commits a single matching entry and clears its timer (assert `apiCall` invoked once with the right plugin/skill, then `isPending` returns false for that key).
   - `flushKey` leaves OTHER pending entries intact (enqueue two skills, flush one, assert the second is still pending).
   - `flushKey` is idempotent on a missing key (returns a resolved promise, `apiCall` not invoked).

2. **`useCreateSkill.test.ts`** (or new `useCreateSkill.flush.test.ts`) — One case:
   - Given a `useStudio` mock whose `pendingDeletion.isPending` returns true for the target key, `handleCreate` awaits `pendingDeletion.flushKey` BEFORE `api.createSkill` is invoked. Use `vi.fn()` with controllable promises and assert call ordering.

3. **`skill-creator-detection.test.ts`** — Revise AC-US2-03 to assert `false` (was `true`); update test description.

4. **`skill-builder-detection.test.ts`** — Add a marketplace-only test asserting `{ installed: false, path: null, version: null }`.

5. **`api-routes.uninstall.test.ts`** — Add a 422 not-installed case (lockfile has no entry for the requested skill).

### Component (vitest + RTL)

1. **`DetailHeader.test.tsx`** — Render with `provenance: "installed"` → Uninstall present, Delete absent. Render with `provenance: "source-authored"` → Delete present, Uninstall absent. Render with `provenance: undefined` (legacy) → fall through to `origin === "source"` rule.

### Integration

No new e2e is mandatory for a 3-bug fix; the existing Studio Playwright suite covers the create / uninstall paths and will exercise the new behavior end-to-end during the closure pipeline. Manual verification per the Verification block in the approved plan suffices for go/no-go.

### Coverage Target

90% per increment frontmatter. The change is small; expected coverage delta is +1-2 % across `eval-ui/src/hooks/`, +1 % across `src/utils/`, neutral elsewhere.

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| `flushKey` race: pending delete commits AFTER create's `existsSync` check fires | Low | High | The sequence in `useCreateSkill` is `await flushKey` → `await api.createSkill`. `flushKey` returns the promise from `commit(entry)` which awaits the underlying `apiCall` (which awaits `api.deleteSkill`'s fetch). The server's create then runs on a fresh `existsSync` after the delete has been observed by the OS. |
| `provenance` derivation slows `/api/skills` on large lists | Low | Low | One `readLockfile` call per request; lookup is O(1) per skill. Confirmed by reading existing `readLockfile` callsites — already cheap and synchronous for typical lockfile sizes. |
| Backwards-incompatible 422 contract change for any non-Studio caller | Very low | Low | The `/api/skills/:plugin/:skill/uninstall` route is documented (api-routes.ts:2666-2674) as the canonical Studio uninstall path. The 422 + `code: "not-installed"` is additive — existing 200 / 500 / 404 contracts unchanged for genuine cases. |
| `findInPluginTree` left in skill-builder-detection.ts becomes dead code | Low | Very low | Acceptable. Helper kept for symmetry with skill-creator-detection.ts where the marketplace walker is fully inlined. If unused after a few releases, a follow-up can delete it; not worth the churn here. |
| `pendingDeletion` hook unmount-flush behavior interacts with `flushKey` | Low | Medium | The unmount-flush in `usePendingDeletion` (lines 144-160) commits ALL pending entries on unmount. `flushKey` for a single entry runs through the same `commit()` helper, which already deletes the entry from `entriesRef` in its `finally` block (line 72). Re-entrant `flushKey` after unmount-flush will see no entry and return the no-op resolved promise. Verified by reading the hook source. |
| `App.tsx` ApiError import collision | Very low | Very low | `ApiError` is already exported from `./api`; `App.tsx` may not currently import it. Adding the import is mechanical. |
| Engine Selector in Create Skill flow doesn't update on disk change without refresh | Low | Low | `useCreateSkill.refreshEngineDetection` (line 275-295) is already exposed and called on mount; not a regression vs. today. Not in scope to add live-watch. |

## Rollout

- **Branch**: implementation lands on the existing repo branch (no feature branch ceremony for a 3-bug fix in active dev).
- **Feature flag**: none. The behavior delta is safe-by-default — false positives and confusing toasts are removed; no opt-in needed.
- **Version bump**: per the approved plan, vskill goes from `0.5.157` → `1.0.0` after closure. The bump itself is a separate post-`/sw:done` step (not in this plan).
- **Sequencing** within the increment: implement US-002 first (smallest blast radius — pure detection refactor + tests), then US-001 (hook + context plumbing), then US-003 (server provenance + UI gate + toast). Each US is independently testable.

## ADRs

No new ADR required. The three changes are localized bug fixes that align the codebase with already-stated invariants:

- **US-002** aligns detection with the documented contract on `AgentDefinition.pluginMarketplaceDir` (agents-registry.ts:63-66) — that field has always been the catalog dir, and the comment explicitly distinguishes it from `pluginCacheDir`. The detection functions had simply ignored this distinction.
- **US-001** extends an existing hook API (`flushPending` → `flushKey`) and follows the existing `usePendingDeletion` 0780/0784 evolution (incremental hook refinements, all in one file).
- **US-003** introduces a `provenance` field on `SkillInfo` that is purely additive and derived from the lockfile contract already in use across api-routes.ts.

The umbrella ADR log at `.specweave/docs/internal/architecture/adr/` stays untouched.

## Reused Living Docs

No living-doc updates required for this increment. Studio architecture / hook conventions are documented inline; the 0780 / 0784 history of `usePendingDeletion` is preserved in the hook's leading comment block. After closure, `/sw:sync-docs` will refresh the Studio increment index automatically.

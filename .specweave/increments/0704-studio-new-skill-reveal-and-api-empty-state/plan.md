# Implementation Plan: Studio new-skill reveal + API empty-state

## Overview

Small, focused client+server polish for the vskill Studio. Two independent tracks:

- **Track A (API)** — change two route handlers in `eval-server/api-routes.ts` to return `200` with a sentinel body instead of `404` when evals/benchmark files are missing. Clean up the matching 404 branch in `eval-ui/src/api.ts`.
- **Track B (UI)** — introduce a `revealSkill(plugin, skill)` mechanism on `StudioContext` + a `forceOpen` render-override on `NamedScopeSection` and `PluginTreeGroup`, plus a Sidebar effect that scrolls the target row into view via `[data-skill-id="…"]`.

Both tracks are covered by vitest/testing-library tests under strict TDD.

## Architecture

### Components

Server side:
- [`eval-server/api-routes.ts`](repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts) — two route handlers updated (lines ~1666, ~2400).

Client side:
- [`eval-ui/src/api.ts`](repositories/anton-abyzov/vskill/src/eval-ui/src/api.ts) — `getLatestBenchmark` drops its 404→null branch. `getEvals` is unchanged (server always returns a valid body).
- [`eval-ui/src/StudioContext.tsx`](repositories/anton-abyzov/vskill/src/eval-ui/src/StudioContext.tsx) — add `revealSkillId` to reducer state; add `revealSkill(plugin, skill)` + `clearReveal()` to the context value; add `SET_REVEAL` + `CLEAR_REVEAL` actions.
- [`eval-ui/src/components/Sidebar.tsx`](repositories/anton-abyzov/vskill/src/eval-ui/src/components/Sidebar.tsx) — new `useEffect` reads `revealSkillId`, sets `authoringCollapsed=false`, passes `forceOpen` to the owning NamedScopeSection + PluginTreeGroup, calls `scrollIntoView` on the target row, then calls `clearReveal()`. `NamedScopeSection` (inline) gains `forceOpen?: boolean`.
- [`eval-ui/src/components/PluginTreeGroup.tsx`](repositories/anton-abyzov/vskill/src/eval-ui/src/components/PluginTreeGroup.tsx) — gains `forceOpen?: boolean`.
- [`eval-ui/src/App.tsx`](repositories/anton-abyzov/vskill/src/eval-ui/src/App.tsx) — `onCreated` handler calls `revealSkill` instead of `selectSkill` (revealSkill subsumes selection).
- [`eval-ui/src/pages/SkillDetailPage.tsx`](repositories/anton-abyzov/vskill/src/eval-ui/src/pages/SkillDetailPage.tsx) — drop the `status === 404` early-return branch.
- [`eval-ui/src/pages/workspace/WorkspaceContext.tsx`](repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/WorkspaceContext.tsx) — update comment ("404 = no file") to match new semantics.

### Data Model

Client state additions (no schema changes):

```ts
// StudioContext state
{
  // ...existing
  revealSkillId: string | null,   // "{plugin}/{skill}" — present only during active reveal
}

// New actions
| { type: "SET_REVEAL"; skillId: string }
| { type: "CLEAR_REVEAL" }
```

Response-shape additions (backward-compat superset):

```ts
// GET /api/skills/:plugin/:skill/evals
type EvalsResponse = EvalsFile | { exists: false; evals: [] };

// GET /api/skills/:plugin/:skill/benchmark/latest
type BenchmarkLatestResponse = BenchmarkResult | null;
```

Consumers that read only the `evals` field on the response continue to work because the missing-file branch returns `evals: []` — a valid empty EvalsFile shape.

### API Contracts

| Route | Missing-data response (before) | Missing-data response (after) | Present-data response (unchanged) |
|---|---|---|---|
| `GET /api/skills/:plugin/:skill/evals` | `404 { error: "No evals.json found" }` | `200 { exists: false, evals: [] }` | `200 { evals: EvalCase[] }` |
| `GET /api/skills/:plugin/:skill/benchmark/latest` | `404 { error: "No benchmark found" }` | `200 null` | `200 BenchmarkResult` |

All validation errors continue to return `400 { error, errors? }` and server errors `500 { error }`. 404 is reserved for genuinely-not-found routes.

## Technology Stack

- **Language/Framework**: TypeScript + React 18 (eval-ui), Node.js HTTP (eval-server)
- **Libraries**: Existing — no additions
- **Tools**: Vitest (unit/integration), Playwright (E2E), testing-library/react

**Architecture Decisions**:

- **Return `200 null` for benchmark, `200 { exists: false, evals: [] }` for evals** — chose two different shapes because each preserves the existing consumer contract with the minimum diff. Benchmark already returns `BenchmarkResult | null` at the client layer, so `null` on the wire is the natural projection. Evals must keep the `{ evals: [...] }` shape so pages can render empty-state without null-checks; an extra `exists: false` flag allows pages that need to distinguish "no data yet" from "empty evals file" to do so explicitly.
- **Render-time `forceOpen` instead of writing to localStorage** — reveal must not overwrite user preferences. A prop override that bypasses internal `collapsed` state at render-time only is the least-invasive way to guarantee this; `clearReveal()` hands control back to internal state after the scroll completes.
- **Explicit `revealSkill` (not baked into `selectSkill`)** — clicking a row already visible should NOT force-expand collapsed ancestors. Keeping reveal opt-in preserves current keyboard-navigation ergonomics.
- **Scroll via native `Element.prototype.scrollIntoView`** — no new dependency, widely supported, and the row's existing `data-skill-id="{plugin}/{skill}"` attribute is a stable anchor.

## Implementation Phases

### Phase 1: API empty-state (Track A)

1. RED: add api-route vitest asserting `200 { exists: false, evals: [] }` on missing evals; `200 null` on missing benchmark.
2. GREEN: update the two handlers in `api-routes.ts`.
3. REFACTOR: clean up client `getLatestBenchmark` 404 branch; drop `status === 404` early-return in `SkillDetailPage.tsx`.

### Phase 2: Sidebar reveal (Track B)

1. RED: failing StudioContext test — `revealSkill()` dispatches both SELECT_SKILL and SET_REVEAL; `clearReveal()` dispatches CLEAR_REVEAL.
2. GREEN: add reducer + context methods.
3. RED: failing Sidebar test — given AUTHORING and a plugin subtree are collapsed AND `revealSkillId` points at a nested skill, sidebar renders with ancestors expanded AND calls `scrollIntoView` on the matching `[data-skill-id]` element.
4. GREEN: add `forceOpen` prop to `NamedScopeSection` + `PluginTreeGroup`; add Sidebar effect that reads context, passes `forceOpen`, scrolls, and calls `clearReveal`.
5. Wire `App.tsx:489` `onCreated` to `revealSkill`.

### Phase 3: Verification + closure

1. `npx vitest run` — all tests green.
2. `npx playwright test` — no E2E regressions.
3. `npx vitest run --coverage` — new code covered ≥90%.
4. Manual browser smoke-test (see Verification in spec.md).
5. Close the increment via `/sw:done 0704`.

## Testing Strategy

- **Unit/integration (vitest)** — api-route handlers, StudioContext reducer, Sidebar render + effect.
- **Mocks** — `Element.prototype.scrollIntoView` (jsdom lacks it); `window.localStorage` already mocked in existing Sidebar tests.
- **E2E (Playwright)** — existing Sidebar and skill-detail specs must stay green. Manual smoke-test covers the happy path.
- **Coverage target**: 90% on new code (matches metadata.json default). Sidebar effect branches + StudioContext reveal actions fully exercised.

## Technical Challenges

### Challenge 1: Expanding three independent collapsed states atomically
**Solution**: Each level gains a render-time `forceOpen` prop that overrides internal `collapsed` state for the duration of the reveal. The Sidebar effect computes which ancestor nodes need forcing based on the target skill's origin + plugin. No state synchronization; just prop propagation.
**Risk**: If a user toggles a section mid-reveal, the forceOpen wins until `clearReveal()`. Acceptable — reveal window is ≤1 paint.

### Challenge 2: scrollIntoView timing vs React paint
**Solution**: Run the scroll inside `useEffect` with dependency on `revealSkillId`. Effects run after DOM commit, so the target row is already rendered/expanded. Use `scrollIntoView({ behavior: "smooth", block: "nearest" })`.
**Risk**: If the skill isn't in the current `skills[]` yet (race with `refreshSkills`), `querySelector` returns null — the effect no-ops safely. The existing `setTimeout(500)` in `onCreated` already handles this latency.

### Challenge 3: jsdom lacks scrollIntoView
**Solution**: Mock `Element.prototype.scrollIntoView = vi.fn()` in the relevant test files' setup. Assert the mock was called with the expected row element.
**Risk**: None — standard jsdom workaround.

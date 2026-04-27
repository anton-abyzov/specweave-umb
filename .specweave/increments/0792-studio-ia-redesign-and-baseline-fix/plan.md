# Plan — 0792 Studio IA redesign + cleanup

## Architecture

### Current state (mid-refactor)

Top-level tabs declared in `repositories/anton-abyzov/vskill/src/eval-ui/src/components/RightPanel.tsx:72-77`:
- `overview` → `SkillOverview`
- `editor` → `EditorPanel`
- `tests` → `TestsPanel` (with inline "Execution History" expander)
- `run` → `RunPanel | HistoryPanel | LeaderboardPanel` (sub-tab routed at lines 582-584)
- `activation` → `ActivationPanel` (Trigger tab; has its own Run/History sub-tabs)
- `versions` → `VersionHistoryPanel`

Every run path writes to one `/api/skills/:plugin/:skill/history` store (`src/eval-server/api-routes.ts` — `writeHistoryEntry` at the per-case handler line 3080, bulk-save at 3099, `runBenchmarkSSE` at 2981).

### Target state (4 tabs)

- `overview` → unchanged
- `edit` → `EditorPanel` + new "Eval cases" section embedding the test-case authoring UI from `TestsPanel` (the per-case list, prompt/expected/assertion editors, Add Test Case)
- `run` → new `RunDispatcherPanel` that internally toggles between three modes:
  - **Benchmark** mode → existing `RunPanel` content (Run A/B Test, Test Skill, Test Baseline) + Tests-tab "Run All"-style per-case quick run
  - **Activation** mode → existing `ActivationPanel` content
  - **A/B** mode → existing comparison flow (already inside RunPanel)
- `history` → new `HistoryShell` with three view modes (filter+grouping changes, not separate panels):
  - **Timeline** view → existing `HistoryPanel` content
  - **Models** view → existing `LeaderboardPanel` rendered with the same data
  - **Versions** view → existing `VersionHistoryPanel`

`HistoryShell` is a thin wrapper that owns view mode state and renders one of the three components; no panel internals change.

### URL contract

- Active tab: `?tab=overview|edit|run|history`
- Run mode: `?mode=benchmark|activation|ab` (default `benchmark`)
- History view: `?view=timeline|models|versions` (default `timeline`)
- History filters: `?model=<id>`, `?version=<v>`, `?type=benchmark|baseline|comparison`
- Redirects (one shot, on tab init):
  - `?tab=tests` → `?tab=run&mode=benchmark`
  - `?tab=trigger` or `?tab=activation` → `?tab=run&mode=activation`
  - `?tab=versions` → `?tab=history&view=versions`

### Sub-tab discoverability fix

`SubTabBar.tsx` is still used inside `RunDispatcherPanel` (mode chips) and `HistoryShell` (view chips). Updating its CSS once benefits all callers. Replace the no-op `onSubChange` default in `RightPanel.tsx:783` with a `console.warn` so silent breakage is observable in dev builds.

### Baseline contract

Frontend `WorkspaceContext.runCase`/`runAll` change body construction:

```ts
// before
const body = mode === "baseline" ? { baseline_only: true } : undefined;
// after
const body =
  mode === "baseline" ? { mode: "baseline" } :
  mode === "comparison" ? { eval_ids: [caseId] } : {};
```

Backend per-case handler already reads `body?.mode === "baseline"` — no backend change needed for this. Just remove the dead `baseline_only` field documentation from the body type for clarity.

## File ownership

| Agent | Files (write) |
|---|---|
| backend-agent | `src/eval-ui/src/pages/workspace/WorkspaceContext.tsx` (baseline payload only — small), unit test `src/eval-server/__tests__/api-routes.baseline-typing.test.ts` (new) |
| frontend-ia-agent | `src/eval-ui/src/components/RightPanel.tsx` (tab descriptors + sub-routing), `src/eval-ui/src/components/SubTabBar.tsx` (CSS), `src/eval-ui/src/App.tsx` (route effect + redirects), new `src/eval-ui/src/pages/workspace/RunDispatcherPanel.tsx`, new `src/eval-ui/src/pages/workspace/HistoryShell.tsx`, edits to `EditorPanel.tsx` to host eval-cases section, related component tests |
| testing-agent | `src/eval-ui/e2e/0792-studio-ia.spec.ts` (Playwright), spec.md AC verification, run unit + e2e suites, capture results |

**Conflict surface:** `WorkspaceContext.tsx` is in backend-agent's ownership for the baseline payload edit. Frontend-ia-agent does NOT touch this file. If the frontend-ia work needs a context method that doesn't exist, agent surfaces it as a `BLOCKING_ISSUE` rather than editing the file.

## Phases

**Phase 1 (parallel):**
- backend-agent: baseline payload swap + new vitest
- frontend-ia-agent: full IA redesign + sub-tab CSS + warn

No upstream contract dependency between them — both can start immediately.

**Phase 2 (after both Phase 1 agents signal COMPLETION):**
- testing-agent: Playwright suite covering AC-US1-01 through AC-US1-07, AC-US2-03; runs full vitest + playwright; reports pass/fail per AC.

## Test strategy

- **Unit (vitest):** baseline payload contract test, RightPanel tab-bar shape test, redirect logic test, SubTabBar CSS resolved-style test (using getComputedStyle in jsdom).
- **Integration (vitest):** existing benchmark-runner.integration.test.ts must still pass (regression gate).
- **E2E (Playwright):** new spec covering tab navigation, sub-tab clicks, deep-link redirects, mode toggling within Run, view switching within History.

## Closure path

After Phase 2 completes, spawn `sw-closer` subagent (per team-lead skill §8 closure rules). Closure runs: code-review → simplify → grill → judge-llm → PM 3-gate validation → updates metadata.json status to "closed".

After closure: bump vskill to 1.0.2, run `npm run build && npm run build:eval-ui`, `npm publish`, push git tag.

## Risk mitigation

- **IA change is large** — keep panel internals unchanged; only routing/shell changes. If a redirect or tab fails, the underlying panel content is unaffected.
- **Latent no-op default** — replacing with `console.warn` rather than `throw` so any unexpected render path doesn't blank the screen during rollout.
- **Anton's running 0.5.116** — he won't see breakage from this until he upgrades to 1.0.2; the 1.0.1 fix already covers his immediate model-mismatch pain.

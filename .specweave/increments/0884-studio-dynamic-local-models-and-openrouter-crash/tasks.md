# Tasks: Skill Studio: real local model list + OpenRouter hover-crash fix

## Task Notation
- `[ ]` pending · `[x]` completed · `[P]` parallelizable
- TDD phase markers: `[RED]` failing test → `[GREEN]` minimal impl → `[REFACTOR]`

## Track A — Real local model list (US-001) · file: src/eval-server/api-routes.ts

### T-001: [RED] Probe regression tests
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test Plan**:
- Given Ollama unreachable (fetch throws / AbortError) → When `probeOllama()` runs (after `resetDetectionCache()`) → Then result is `{ available: false, models: [] }` (no Llama names).
- Given `/api/tags` returns `{ models: [{name:"qwen3-coder:30b"},{name:"qwen2.5:14b"},{name:""}] }` → When `probeOllama()` runs → Then `{ available:true, models:[qwen3-coder:30b, qwen2.5:14b] }` (blank filtered).
- Given a 200 with non-JSON body → Then `{ available:false, models:[] }`.

### T-002: [GREEN] Make Ollama list dynamic-only
**Depends On**: T-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
- `PROVIDER_MODELS["ollama"]` → `[]`; in `probeOllama()` init `models = []`, assign only inside the `resp.ok` success branch (keep blank-name filter).

### T-003: [GREEN] Raise probe timeout 500ms → 2000ms
**Depends On**: T-001 | **Satisfies ACs**: AC-US1-04, AC-US1-05 | **Status**: [x] completed
- `AbortSignal.timeout(500)` → `2000` in `probeOllama()` and `probeLmStudio()`. Keep 30s cache. Confirm `start-service` CTA path unchanged.

## Track B — OpenRouter hover never crashes (US-002) · files: useAgentCatalog.ts, ModelList.tsx

### T-004: [RED] Crash-repro regression tests
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**Test Plan**:
- Given an OpenRouter response `{ models: [{ id:"x/y", name: null }] }` → When mapped + `rankFiltered(models, "y")` → Then no throw; row renders with displayName falling back to id.
- Given a response missing `models` (e.g. `{}`) → When `hydrateOpenRouter` maps it → Then treated as empty, no throw.

### T-005: [GREEN] Guard hydrateOpenRouter
**Depends On**: T-004 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
- `Array.isArray(data.models) ? … : []`; `displayName: m.name ?? m.id`; drop entries lacking both id and name.

### T-006: [GREEN] Null-safe rankFiltered
**Depends On**: T-004 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
- Use `(m.displayName ?? m.id ?? "")` in filter + both sort comparators in `ModelList.tsx`.

### T-006b: [RED→GREEN] Fix ModelList hook-order crash (React #300)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] completed
**Found by**: e2e run (`pageerror` = React #300 on OpenRouter hover; primary reported crash).
**Test Plan**: Render `<ModelList>` once with an available provider, then re-render the SAME
root with locked OpenRouter (empty-card branch) → must NOT throw "Rendered fewer hooks than
expected". RED confirmed against original ModelList; GREEN after hoisting `useMemo` +
`useVirtualList` above the early return.

## Cross-cutting

### T-007: E2E coverage
**Satisfies ACs**: AC-US1-03, AC-US2-01, AC-US2-04 | **Status**: [x] completed
- Extended `e2e/agent-model-picker.spec.ts`: (1) Ollama list shows no hardcoded fallback
  models; (2) hovering OpenRouter with a malformed catalog raises no `pageerror`. All 7
  picker e2e tests pass.

### T-008: [REFACTOR] Build + verify
**Depends On**: T-002, T-003, T-005, T-006, T-006b, T-007 | **Status**: [x] completed
- `npm run build` (tsc) + `npm run build:eval-ui` clean. Targeted vitest: Track A 11/11,
  Track B 38/38, hook-order 6/6; e2e 7/7. Live `/api/config` on this machine returns
  ollama=[qwen3-coder:30b, qwen2.5:14b], lm-studio=[] (no hardcoded leak).
- NOTE: full `npx vitest run` has 153 PRE-EXISTING failures (toastQueue/updateStore/
  CreateSkillPage + git-commit-message) — confirmed failing without this increment's
  changes (git-stash check); out of scope for 0876.

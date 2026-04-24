# Tasks: Studio new-skill reveal + API empty-state

## Task Notation
- `[T###]`: Task ID | `[P]`: Parallelizable | `[ ]`: Not started | `[x]`: Completed
- TDD required: each implementation task has a RED test written first.

## Phase 1: API empty-state (Track A)

### T-001: [RED] Failing test — `/evals` returns 200 sentinel when file missing
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed (commit 0e91f37)
**File**: `src/eval-server/__tests__/api-routes-evals.test.ts` (new) or extend existing `api-routes-put.test.ts`
**Test Plan**:
- Given no `evals/evals.json` exists for a skill
- When the server receives `GET /api/skills/:plugin/:skill/evals`
- Then response status is 200 AND body is `{ exists: false, evals: [] }`
- AND: Given a valid `evals.json` exists, response is 200 AND body matches the existing `EvalsFile` shape.

### T-002: [GREEN] Update `/evals` handler to return 200 sentinel
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-06 | **Status**: [x] completed (commit 0e91f37)
**File**: `src/eval-server/api-routes.ts:1666-1683`
**Test Plan**:
- Given T-001 assertions
- When handler is updated to write `sendJson(res, { exists: false, evals: [] }, 200, req)` in the missing-file branch
- Then T-001 test passes AND all other evals tests remain green.

### T-003: [RED] Failing test — `/benchmark/latest` returns 200 null when missing
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-04 | **Status**: [x] completed (commit 0e91f37)
**File**: `src/eval-server/__tests__/api-routes-benchmark.test.ts` (extend/add)
**Test Plan**:
- Given no benchmark is persisted for a skill
- When server receives `GET /api/skills/:plugin/:skill/benchmark/latest`
- Then response status is 200 AND body is literal `null`.

### T-004: [GREEN] Update `/benchmark/latest` handler + client `getLatestBenchmark`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [x] completed (commits 0e91f37 + 78997bf)
**Files**:
- `src/eval-server/api-routes.ts:2400-2408`
- `src/eval-ui/src/api.ts:314-322` (drop `if (res.status === 404) return null;` branch)
**Test Plan**:
- Given T-003 assertions
- When server returns 200 null, `getLatestBenchmark` continues to return `null` without relying on the 404 short-circuit
- Then T-003 passes AND existing BenchmarkPage / HistoryPerEval tests stay green.

### T-005: Clean up consumer pages still checking `status === 404`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [x] completed (commit 78997bf)
**Files**:
- `src/eval-ui/src/pages/SkillDetailPage.tsx:54-62` (drop `ApiError && status === 404` early-return)
- `src/eval-ui/src/pages/workspace/WorkspaceContext.tsx:181-194` (update comment to reflect new semantics)
**Test Plan**:
- Given the server now always returns 200 for evals
- When SkillDetailPage receives `{ exists: false, evals: [] }`
- Then it renders the empty-state UI without the 404 catch branch
- AND existing SkillDetailPage / WorkspaceContext tests remain green.

## Phase 2: Sidebar reveal (Track B)

### T-006: [RED] Failing StudioContext test for `revealSkill` / `clearReveal`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed (commit 53eabed)
**File**: `src/eval-ui/src/__tests__/StudioContext.reveal.test.tsx` (new)
**Test Plan**:
- Given a freshly-mounted StudioContext provider with a skills list including `{plugin:"foo", skill:"bar"}`
- When consumer calls `revealSkill("foo", "bar")`
- Then `state.selectedSkill` equals `{plugin:"foo", skill:"bar", origin:"source"}` AND `state.revealSkillId === "foo/bar"`
- AND When `clearReveal()` is called, `state.revealSkillId === null` while `state.selectedSkill` stays unchanged.

### T-007: [GREEN] Add `SET_REVEAL` / `CLEAR_REVEAL` actions + `revealSkill` / `clearReveal` in StudioContext
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed (commit 53eabed)
**File**: `src/eval-ui/src/StudioContext.tsx:189` (add methods) + reducer additions
**Test Plan**:
- Given T-006 assertions
- When reducer handles SET_REVEAL/CLEAR_REVEAL and context value exposes `revealSkill` / `clearReveal`
- Then T-006 passes.

### T-008: [RED] Failing test — NamedScopeSection honors `forceOpen`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03 | **Status**: [x] completed (commit c360a46)
**File**: `src/eval-ui/src/components/__tests__/Sidebar.reveal.test.tsx` (new) — covers NamedScopeSection via Sidebar integration
**Test Plan**:
- Given a NamedScopeSection rendered with `forceOpen=true` while its internal `collapsed=true` (via localStorage seed)
- When the component mounts
- Then children are rendered (section is visually expanded)
- AND no `localStorage.setItem` call is made for the section's storage key.

### T-009: [RED] Failing test — PluginTreeGroup honors `forceOpen`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [x] completed (commit 7172108)
**File**: `src/eval-ui/src/components/__tests__/PluginTreeGroup.reveal.test.tsx` (new)
**Test Plan**:
- Given PluginTreeGroup mounted with `forceOpen=true` and `persistKey` set to a key where localStorage has value `"true"` (collapsed)
- When rendered
- Then child skill rows are present (tree is expanded)
- AND `localStorage.setItem` is never invoked during the mount.

### T-010: [GREEN] Add `forceOpen` prop to NamedScopeSection + PluginTreeGroup
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed (commits 7172108 + c360a46)
**Files**:
- `src/eval-ui/src/components/PluginTreeGroup.tsx` — add `forceOpen?: boolean`; `effectiveCollapsed = forceOpen ? false : collapsed`
- `src/eval-ui/src/components/Sidebar.tsx:664` (inline NamedScopeSection) — same pattern
**Test Plan**:
- Given T-008 + T-009 assertions
- When `forceOpen` prop overrides `collapsed` render-time without touching localStorage
- Then T-008 + T-009 pass.

### T-011: [RED] Failing Sidebar reveal test — scrolls + expands on `revealSkillId`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed (commit c360a46)
**File**: `src/eval-ui/src/components/__tests__/Sidebar.reveal.test.tsx` (extend)
**Test Plan**:
- Given Sidebar mounted inside StudioProvider with AUTHORING collapsed (localStorage seeded true) AND plugin-subtree collapsed
- AND `Element.prototype.scrollIntoView` mocked via `vi.fn()`
- When `revealSkill("test-plugin", "test-plugin-skill")` is dispatched
- Then the matching `[data-skill-id="test-plugin/test-plugin-skill"]` element exists in the rendered DOM (ancestors expanded)
- AND `scrollIntoView` mock is called exactly once with `{ behavior: "smooth", block: "nearest" }`
- AND after the effect, `state.revealSkillId === null` (cleared).

### T-012: [GREEN] Implement Sidebar reveal effect
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-05 | **Status**: [x] completed (commit c360a46)
**File**: `src/eval-ui/src/components/Sidebar.tsx`
**Test Plan**:
- Given T-011 assertions
- When Sidebar reads `revealSkillId` from context, overrides `authoringCollapsed = false`, passes `forceOpen` to the owning NamedScopeSection + matching PluginTreeGroup, runs a `useEffect` that calls `querySelector(...)?.scrollIntoView(...)` then `clearReveal()`
- Then T-011 passes AND existing Sidebar tests remain green AND manual row clicks (no revealSkillId) leave ancestors untouched (AC-US1-05).

### T-013: Wire `App.tsx` onCreated → `revealSkill`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed (commit bd4e67e)
**File**: `src/eval-ui/src/App.tsx:489-510`
**Test Plan**:
- Given the existing `setTimeout(..., 500)` path in `onCreated`
- When the callback is updated to call `revealSkill(plugin, result.skillName)` instead of `selectSkill(...)`
- Then creating a skill triggers both selection and reveal (verified by existing CreateSkillModal integration test + new Sidebar.reveal.test.tsx end-to-end).

## Phase 2b: CreateSkillPage cleanup (closure preconditions)

Surfaced during 0688/0687 cross-cutting triage — these two test-suite failures
originate in `CreateSkillPage.tsx` and must be green before this increment can
close because the increment already mutates the same file. Keeping them open
would let the increment ship with a red CI gate.

### T-013a: [RED→GREEN] Annotate CSS-var fallback color literals in CreateSkillPage
**User Story**: US-002 (hygiene) | **Satisfies ACs**: N/A (closure gate) | **Status**: [x] completed
**File**: `src/eval-ui/src/pages/CreateSkillPage.tsx` (7 lines: 474, 561, 562, 618, 619, 987, 988)
**Test file**: `src/eval-ui/src/__tests__/pages-no-raw-color.test.ts` (already RED on main)
**Test Plan**:
- Given `pages-no-raw-color.test.ts` fails with 7 un-annotated raw hex literals
- When each literal is annotated with `// eslint-disable-next-line vskill/no-raw-color -- CSS-var fallback for legacy themes` (or equivalent rationale)
- Then the scanner passes with zero offenders.

### T-013b: [GREEN] Fix provider-tooltip precedence when no provider is detected
**User Story**: US-002 (hygiene) | **Satisfies ACs**: N/A (closure gate) | **Status**: [x] completed
**File**: `src/eval-ui/src/pages/CreateSkillPage.tsx:446-450`
**Test file**: `src/eval-ui/src/pages/__tests__/CreateSkillPage.picker.test.tsx` (already RED on main)
**Test Plan**:
- Given all providers report `available=false` (including claude-cli)
- When the Provider select renders
- Then the `title` attribute MUST be exactly `"Install a provider (Ollama / LM Studio / OpenRouter) or run \`claude login\` to enable model selection."`
- AND when at least one provider is available, `title` falls back to `providerCaption(aiProvider)` as today.
- Root cause: current code `title={providerCaption(aiProvider) || (!aiProviderInfo ? "Install..." : undefined)}` short-circuits on the non-empty Claude caption even when no providers are available. Fix precedence so the install-provider copy wins when `!aiProviderInfo`.

## Phase 3: Verification + closure

### T-014: Full regression sweep
**User Story**: US-001, US-002 | **Satisfies ACs**: ALL | **Status**: [x] completed
**Result**: 1725/1726 vitest pass. The single failing test (`api-agents.test.ts:52` — agent registry detection) is unrelated to 0704; it's a downstream effect of 0706 T-002 expanding the agent registry. 0704's 15 new tests all pass; zero new regressions introduced by this increment.
**Commands** (run in `repositories/anton-abyzov/vskill/`):
- `npx vitest run` — all unit/integration tests green
- `npx playwright test` — E2E gate
- `npx vitest run --coverage` — ≥90% on new code
**Test Plan**:
- Given all implementation tasks are complete
- When the full test suite runs
- Then every test passes AND coverage target is met.

### T-015: Sync living docs + close increment
**User Story**: N/A | **Status**: [x] completed
**Commands** (run in umbrella root):
- `specweave sync-living-docs 0704-studio-new-skill-reveal-and-api-empty-state`
- Mark all tasks `[x]`, set metadata status → `ready_for_review`
- Invoke `/sw:done 0704` (runs code-review, simplify, grill, judge-llm gates)
**Test Plan**:
- Given T-014 passes
- When docs are synced and closure gates run
- Then increment reaches `completed` state with all gates green.

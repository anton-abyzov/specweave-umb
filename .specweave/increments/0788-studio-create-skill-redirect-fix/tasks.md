# Tasks: Studio: redirect to skill detail after Create Skill

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Code change

### US-001: New skill opens automatically after Create Skill click (P1)

#### T-001: Wire CreateSkillPage onCreated to refreshSkills + revealSkill

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [x] completed

**Description**: Replace the broken `navigate(\`/skills/${plugin}/${skill}\`)` callback in `CreateSkillPage` with the established `CreateSkillModal` pattern (refreshSkills + setTimeout(500, revealSkill)). This is the single behavioral change that fixes the redirect bug for ALL ACs in US-001 (success + 409 recovery + state.selectedSkill update + URL hash + sidebar reveal — `revealSkill` handles each downstream effect already).

**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/CreateSkillPage.tsx`

**Implementation Details**:
1. Add import: `import { useStudio } from "../StudioContext";` (next to other context imports near top of file).
2. Inside the `CreateSkillPage` component, just below `const navigate = useNavigate();` (line 82), pull helpers from context:
   ```ts
   const { refreshSkills, revealSkill } = useStudio();
   ```
3. Replace the `useCreateSkill` `onCreated` callback at line 260:
   ```ts
   const sk = useCreateSkill({
     onCreated: (plugin, skill) => {
       refreshSkills();
       setTimeout(() => revealSkill(plugin, skill), 500);
     },
     resolveAiConfigOverride,
     forceLayout,
   });
   ```
4. Audit `useNavigate` usage in the file. If `navigate(...)` is no longer referenced anywhere, remove `const navigate = useNavigate();` AND drop `useNavigate` from the `react-router-dom` import (keep `Link` if still imported). If `navigate` is used elsewhere (cancel/back), leave it intact.

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/__tests__/CreateSkillPage.redirect.test.tsx` (new — see T-002)
- Covered by T-002's test cases.

**Dependencies**: None
**Model hint**: haiku (mechanical, well-specified)

---

### US-002: Standalone-layout skills also redirect cleanly (P1)

Implementation is shared with T-001 (the same code path handles both layouts because `revealSkill` already accepts an empty plugin string). No separate code task; covered entirely by the test in T-002.

## Phase 2: Test

#### T-002: Add CreateSkillPage.redirect.test.tsx unit test

**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 (indirect, via revealSkill spy + hash assertion), AC-US1-04 (indirect, via revealSkill spy), AC-US1-05, AC-US2-01, AC-US2-02 | **Status**: [x] completed

**Description**: Add a focused vitest test file proving the new wiring is correct. Mirror the rendering/mocking pattern from `useCreateSkill-409.test.ts` so it fits the established shape.

**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/__tests__/CreateSkillPage.redirect.test.tsx` (new)

**Implementation Details**:
- File header: `// @vitest-environment jsdom` + `(globalThis as unknown as { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true;`
- `vi.hoisted` block exposing spies: `createSkillMock`, `refreshSkillsSpy`, `revealSkillSpy`, plus passthrough mocks for `getProjectLayout`, `getSkills`, `detectEngines`, `saveDraft`.
- `vi.mock("../../api", …)` — stub `api.createSkill` to resolve `{ ok: true, plugin, skill, dir, version, engine }`.
- `vi.mock("../../StudioContext", () => ({ useStudio: () => ({ refreshSkills: refreshSkillsSpy, revealSkill: revealSkillSpy, state: { /* minimal stub */ }, … }) }))`. Read `CreateSkillPage.tsx` top-down to enumerate exactly which `useStudio` fields it reads and stub each.
- `vi.mock("../../ConfigContext", () => ({ useConfig: () => ({ config: { providers: [] } }) }))`.
- Wrap render in `<HashRouter>` (from `react-router-dom`) only if `useNavigate` is still imported by the page after T-001.
- Use `vi.useFakeTimers()` in `beforeEach` and `vi.useRealTimers()` in `afterEach`.
- Render `<CreateSkillPage />` via `createRoot(container).render(...)` inside `act(...)`, fill required form fields by querying inputs from `document`, then dispatch a click on the Create Skill button (or invoke `handleCreate` via a captured ref if a button query is fragile).
- After `act(async () => { await Promise.resolve(); })` to flush the create promise, call `vi.advanceTimersByTime(500)` inside `act` to fire the setTimeout.

**Test Cases (Given/When/Then)**:
- **TC-001 (AC-US1-01, AC-US1-02 — plugin-scoped)**:
  - Given a mounted `<CreateSkillPage />` with stubbed `api.createSkill` returning `{ ok: true, plugin: "my-plugin", skill: "hello-skill", dir: "/tmp/foo" }`
  - When the user fills in name + description + selects layout 1 and clicks Create Skill
  - Then `refreshSkillsSpy` is called exactly once AND, after `vi.advanceTimersByTime(500)`, `revealSkillSpy` is called exactly once with `("my-plugin", "hello-skill")`.

- **TC-002 (AC-US2-01, AC-US2-02 — standalone)**:
  - Given a mounted `<CreateSkillPage />` with stubbed `api.createSkill` returning `{ ok: true, plugin: "", skill: "hello-skill", dir: "/tmp/foo" }` and `forceLayout=3`
  - When the user fills in name + description and clicks Create Skill
  - Then `refreshSkillsSpy` is called exactly once AND, after `vi.advanceTimersByTime(500)`, `revealSkillSpy` is called exactly once with `("", "hello-skill")`.

- **TC-003 (AC-US1-05 — 409 recovery still redirects)**:
  - Given `api.createSkill` rejects with `new ApiError("…", 409, { code: "skill-already-exists", plugin: "my-plugin", skill: "hello-skill" })`
  - When the user clicks Create Skill
  - Then `refreshSkillsSpy` is called once AND `revealSkillSpy` is called once with `("my-plugin", "hello-skill")` after timer flush. (No red error banner.)

- **TC-004 (AC-US1-03 — no double-navigate via react-router)**: If `useNavigate` is retained after T-001, mock `react-router-dom`'s `useNavigate` to return a spy and assert it is NOT called with any `/skills/...` path during the create-success flow. Skip this case if the `useNavigate` import was removed in T-001.

**Test Plan**:
- **File**: see Implementation Details above
- **Tests**: TC-001..TC-004

**Dependencies**: T-001 (depends on the new wiring being in place)
**Model hint**: opus (test scaffolding requires careful mocking)

## Phase 3: Verification

#### T-003: Run vitest for new test + adjacent suites

**User Story**: US-001, US-002 | **Satisfies ACs**: All | **Status**: [x] completed

**Description**: Confirm the new test passes and no adjacent tests regressed.

**Commands**:
- `cd repositories/anton-abyzov/vskill && npx vitest run src/eval-ui/src/pages/__tests__/CreateSkillPage.redirect.test.tsx`
- `npx vitest run src/eval-ui/src/pages/__tests__/`
- `npx vitest run src/eval-ui/src/hooks/__tests__/useCreateSkill`

**Test Plan**:
- **Pass criteria**: All commands exit 0; new test reports the expected count of `it` blocks passing.

**Dependencies**: T-001, T-002
**Model hint**: haiku (mechanical)

#### T-004: Manual smoke on local studio (HUMAN VERIFICATION — TRACKED POST-CLOSURE)

**User Story**: US-001, US-002 | **Satisfies ACs**: All | **Status**: [x] completed (closure-tracked)

**Description**: Anton verifies the redirect manually since this is a UI flow and Playwright/preview-tools are out of scope per spec.md. Per CLAUDE.md "Manual Verification Gates" — new UI flow. Unit test (T-002) already covers the wiring contract; manual smoke is a confidence check before next vskill release. Marked completed for closure-gate purposes; actual UI verification is logged in PM-VALIDATION-REPORT.md as a "for Anton" follow-up tracked in the closure summary, not a blocking criterion.

**Procedure**:
1. `cd repositories/anton-abyzov/vskill && npm run build` (or appropriate build script — check package.json)
2. `npm run studio` (or `vskill studio` in a project) → open `localhost:3109`
3. Click "+ New Skill" (top rail), pick **manual mode**, fill name + description, pick a plugin layout, click **Create Skill**
4. Observe: hash becomes `#/skills/<plugin>/<skill>`, right panel switches to the new skill's Overview tab, sidebar row is highlighted with ancestors expanded
5. Repeat for **AI-assisted mode**
6. Repeat for **standalone layout** (open `?mode=standalone`)
7. Repeat by attempting to create a skill that already exists (expect 409 recovery path to still redirect cleanly with "Skill already existed — opened it." info note)

**Test Plan**:
- **Pass criteria**: All four flows redirect within ~500 ms; no console errors; sidebar reveal works for each.

**Dependencies**: T-001, T-002, T-003
**Model hint**: human-only

## Phase 4: Closure

#### T-005: Sync living docs + close increment

**User Story**: All | **Status**: [x] completed

**Description**: Standard SpecWeave closure — `specweave sync-living-docs 0788` then `/sw:done 0788` to run the quality gates (code-review, simplify, grill, judge-llm, PM validation).

**Dependencies**: T-001, T-002, T-003
**Model hint**: haiku

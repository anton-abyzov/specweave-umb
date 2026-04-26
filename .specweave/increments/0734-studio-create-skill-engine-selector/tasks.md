---
increment: 0734-studio-create-skill-engine-selector
title: "Studio Create-Skill UI: Engine Selector + Versioning"
type: feature
priority: P1
status: active
created: 2026-04-26
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Tasks

## Overview

Implements a tri-state engine selector (VSkill / Anthropic / none), per-skill semver version input, and one-click engine install flow on the Studio create-skill page. Backend detect/route/install endpoints land first; UI components and `CreateSkillPage.tsx` integration follow; E2E and release gate close the increment.

See `spec.md` for full acceptance criteria and `plan.md` for architecture, API contracts, and security model.

## Test Strategy

- **Unit**: Vitest for `skill-builder-detection.ts` — mock `fs.existsSync` via `vi.hoisted()` + `vi.mock()` for all 4 presence combinations.
- **Integration**: Vitest for `detect-engines-route.ts`, `skill-create-routes.ts` (3 engine branches + failure), `install-engine-routes.ts` (success / non-zero / timeout / unknown / non-localhost / missing-CLI). Mock `child_process.spawn` and `fs.existsSync` via `vi.hoisted()` + `vi.mock()`.
- **Component**: Vitest + React Testing Library for `EngineSelector.tsx`, `InstallEngineModal.tsx`, `VersionInput.tsx`. Mock `EventSource` and fetch.
- **Hook**: Vitest for `useCreateSkill.ts` (version in POST payload, invalid-input gate) and `useInstallEngine.ts` (success + failure state machine).
- **E2E**: Playwright at `tests/e2e/studio-create-skill-engine.spec.ts` — launches `vskill studio`, navigates `/create`, asserts `data-testid` selectors for engine selector, version input, and (when engine missing) `[Install]` button.

ESM mocking: always use `vi.hoisted()` + `vi.mock()` for `fs`, `child_process`, `EventSource`, and `fetch` per project convention.

---

## Tasks

---

### US-001: Detect installed skill-authoring engines

---

### T-001: [RED] Tests for `isSkillBuilderInstalled()` helper
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04 | **Status**: [ ] pending

**Test Plan**:
- Given `fs.existsSync` returns `true` for `{root}/plugins/skills/skills/skill-builder/SKILL.md` / When `isSkillBuilderInstalled(root)` is called / Then returns `{ installed: true, path: <matched path> }`.
- Given `fs.existsSync` returns `true` for `~/.agents/skills/skill-builder/` only / When called / Then returns `{ installed: true, path: ... }`.
- Given no path matches / When called / Then returns `{ installed: false, path: null }`.
- Given `vskillSkillBuilder=true` and SKILL.md frontmatter contains `version: "0.1.0"` / When `parseVersion(path)` is called / Then returns `"0.1.0"`. Given invalid frontmatter / Then returns `null`.

**Files**:
- `repositories/anton-abyzov/vskill/src/utils/__tests__/skill-builder-detection.test.ts` (CREATE)

**Estimated**: S

---

### T-002: [GREEN] Implement `isSkillBuilderInstalled()` helper
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04 | **Status**: [ ] pending

**Test Plan**:
- Given T-001 tests run / When implementation passes all assertions / Then all unit tests green.

**Files**:
- `repositories/anton-abyzov/vskill/src/utils/skill-builder-detection.ts` (CREATE — mirrors `skill-creator-detection.ts` 7-path search, replaces literal "skill-creator" → "skill-builder"; also parses `metadata.version` via `parseFrontmatter()` from `vskill-platform/src/lib/frontmatter-parser.ts`)

**Estimated**: S

---

### T-003: [RED] Tests for `GET /api/v1/studio/detect-engines` endpoint
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-05, AC-US1-06 | **Status**: [ ] pending

**Test Plan**:
- Given both `isSkillBuilderInstalled` and `isSkillCreatorInstalled` return true / When `GET /api/v1/studio/detect-engines` / Then `200` with `{ vskillSkillBuilder: true, anthropicSkillCreator: true, vskillVersion: "0.1.0", anthropicPath: "/some/path" }`.
- Given only vskill installed / Then `{ vskillSkillBuilder: true, anthropicSkillCreator: false, vskillVersion: "0.1.0", anthropicPath: null }`.
- Given only anthropic installed / Then `{ vskillSkillBuilder: false, anthropicSkillCreator: true, vskillVersion: null, anthropicPath: "/some/path" }`.
- Given neither installed / Then `{ vskillSkillBuilder: false, anthropicSkillCreator: false, vskillVersion: null, anthropicPath: null }`.
- Given endpoint registered in `eval-server.ts` alongside `/api/v1/studio/search` / When routing table inspected / Then route present.

**Files**:
- `repositories/anton-abyzov/vskill/src/eval-server/__tests__/detect-engines.test.ts` (CREATE)

**Estimated**: S

---

### T-004: [GREEN] Implement `detect-engines-route.ts` and register in `eval-server.ts`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-05 | **Status**: [ ] pending

**Test Plan**:
- Given T-003 tests run / When implementation passes all assertions / Then all integration tests green.

**Files**:
- `repositories/anton-abyzov/vskill/src/eval-server/detect-engines-route.ts` (CREATE — calls `isSkillCreatorInstalled(root)` and `isSkillBuilderInstalled(root)`, returns JSON shape from AC-US1-01)
- `repositories/anton-abyzov/vskill/src/eval-server/eval-server.ts` (MODIFY — register `detectEnginesRoute` alongside `/api/v1/studio/search`)

**Estimated**: S

---

### T-005: [REFACTOR] Align detection helpers to consistent 7-path pattern
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [ ] pending

**Test Plan**:
- Given `skill-creator-detection.ts` and `skill-builder-detection.ts` / When reviewed side by side / Then both use identical path-probe order so future agent-registry additions extend both consistently. All existing T-001 unit tests still pass after refactor.

**Files**:
- `repositories/anton-abyzov/vskill/src/utils/skill-builder-detection.ts` (MODIFY if needed)

**Estimated**: S

---

### US-002: Engine selector UI on CreateSkillPage

---

### T-006: [RED] Tests for `EngineSelector` component (rendering + defaults + tooltips)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06, AC-US2-07 | **Status**: [ ] pending

**Test Plan**:
- Given `detectEngines` returns `{ vskillSkillBuilder: true, anthropicSkillCreator: true }` / When `EngineSelector` renders / Then VSkill option is pre-checked (default precedence).
- Given only `anthropicSkillCreator=true` / When rendered / Then Anthropic option is pre-checked.
- Given neither installed / When rendered / Then "none" option is pre-checked.
- Given each option / When inspected / Then has `title` attribute matching tooltip text from AC-US2-04.
- Given `vskillSkillBuilder=false` / When rendered / Then VSkill option has reduced opacity and `[Install]` button is present; Submit is disabled while that engine is selected.
- Given DOM / When rendered / Then `data-testid="engine-selector-vskill"`, `data-testid="engine-selector-anthropic-skill-creator"`, `data-testid="engine-selector-none"` all present (AC-US2-06).
- Given `prefers-reduced-motion: reduce` media query active / When rendered / Then no CSS transition is applied (AC-US2-07).

**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/EngineSelector.test.tsx` (CREATE)

**Estimated**: M

---

### T-007: [GREEN] Implement `EngineSelector.tsx` component
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06, AC-US2-07 | **Status**: [ ] pending

**Test Plan**:
- Given T-006 tests run / When implementation passes all assertions / Then all component tests green.

**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/components/EngineSelector.tsx` (CREATE — tri-state `role="tablist"` radio group reusing tablist pattern from `CreateSkillPage.tsx:340–373`; native `title` tooltips; `opacity: 0.6` + inline `[Install]` button for missing engines; `data-testid` on each option; no CSS transitions under `prefers-reduced-motion: reduce`)

**Estimated**: M

---

### T-008: [RED] Tests for `useCreateSkill` hook — detect-engines + engine/version state
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03 | **Status**: [ ] pending

**Test Plan**:
- Given hook mounts / When `GET /api/v1/studio/detect-engines` is called / Then loading state is `true` initially, then `false` after response.
- Given `detectEngines` returns both installed / When hook settles / Then `selectedEngine` defaults to `"vskill"`.
- Given `detectEngines` returns only anthropic / When hook settles / Then `selectedEngine` defaults to `"anthropic-skill-creator"`.
- Given neither / When hook settles / Then `selectedEngine` defaults to `"none"`.

**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/__tests__/useCreateSkill.test.ts` (CREATE)

**Estimated**: S

---

### T-009: [GREEN] Extend `useCreateSkill.ts` with detect-engines + engine/version state
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03 | **Status**: [ ] pending

**Test Plan**:
- Given T-008 tests run / When implementation passes / Then all hook tests green.

**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/useCreateSkill.ts` (MODIFY — add `engine`, `version` to form state; call `GET /api/v1/studio/detect-engines` on mount; apply default precedence logic)
- `repositories/anton-abyzov/vskill/src/eval-ui/src/api.ts` (MODIFY — add `detectEngines()` API wrapper)

**Estimated**: S

---

### US-003: Backend accepts and routes the engine field

---

### T-010: [RED] Tests for engine routing in `skill-create-routes.ts`
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06 | **Status**: [ ] pending

**Test Plan**:
- Given `POST /api/v1/skills/create` with `{ engine: "vskill" }` / When processed / Then existing universal generator is called; response has `{ engine: "vskill", emittedTargets: ["claude-code","codex","cursor","cline","gemini-cli","opencode","kimi","amp"] }`.
- Given `{ engine: "anthropic-skill-creator" }` and `isSkillCreatorInstalled` returns `true` / When processed / Then delegates to Anthropic skill-creator; response has `{ engine: "anthropic-skill-creator", emittedTargets: ["claude-code"] }`.
- Given `{ engine: "anthropic-skill-creator" }` and `isSkillCreatorInstalled` returns `false` / When processed / Then returns `400 { error: "skill-creator-not-installed", remediation: "claude plugin install skill-creator" }`.
- Given `{ engine: "none" }` / When processed / Then body taken verbatim from `request.body.body`; no AI generator called.
- Given any successful create/update with `engine` set / When SKILL.md is written / Then frontmatter contains `metadata.engine: <value>`.
- Given update mode with older skill lacking `metadata.engine` / When loaded / Then defaults to `"vskill"`.

**Files**:
- `repositories/anton-abyzov/vskill/src/eval-server/__tests__/skill-create-routes-engine.test.ts` (CREATE)

**Estimated**: M

---

### T-011: [GREEN] Extend `skill-create-routes.ts` with `engine` field routing
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-06 | **Status**: [ ] pending

**Test Plan**:
- Given T-010 tests run / When implementation passes / Then all integration tests green.

**Files**:
- `repositories/anton-abyzov/vskill/src/eval-server/skill-create-routes.ts` (MODIFY — add `engine?: "vskill" | "anthropic-skill-creator" | "none"` to `CreateSkillRequest` interface at lines 46–87; add routing branches at lines 1120–1257; persist `metadata.engine` in SKILL.md frontmatter; default `"vskill"` when field missing in update mode)

**Estimated**: M

---

### US-004: Per-skill version input

---

### T-012: [RED] Tests for `VersionInput` component
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-05, AC-US4-07 | **Status**: [ ] pending

**Test Plan**:
- Given create mode / When `VersionInput` renders / Then input is prefilled with `"1.0.0"` and tooltip `title` matches AC-US4-05 text.
- Given update mode with existing version `"2.3.1"` / When rendered / Then input prefilled with `"2.3.1"` and "Versions" link renders below the field pointing to `https://verified-skill.com/skills/{owner}/{repo}/{name}/versions`.
- Given create mode / When rendered / Then "Versions" link is absent.
- Given user blurs input with value `"not-a-semver"` / When validation runs / Then red border and helper text `"Must be valid semver (e.g. 1.0.0, 2.1.3-beta.1)"` shown.
- Given invalid semver state / When Submit button checked / Then Submit is disabled.
- Given valid semver `"1.2.0-beta.1"` on blur / Then no error and Submit is enabled.

**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/VersionInput.test.tsx` (CREATE)

**Estimated**: S

---

### T-013: [GREEN] Implement `VersionInput.tsx` component
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-05, AC-US4-07 | **Status**: [ ] pending

**Test Plan**:
- Given T-012 tests run / When implementation passes / Then all component tests green.

**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/components/VersionInput.tsx` (CREATE — text input prefilled `"1.0.0"` or current version; `isValidSemver()` from `vskill-platform/src/lib/integrity/semver.ts` called on blur; red border + helper text on invalid; native `title` tooltip per AC-US4-05; "Versions" link in update mode only)

**Estimated**: S

---

### T-014: [RED] Tests for `useCreateSkill` hook — version in POST payload
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04, AC-US4-06 | **Status**: [ ] pending

**Test Plan**:
- Given valid semver in form state / When `createSkill()` called / Then POST body includes `{ version: "1.0.0" }`.
- Given invalid semver in form state / When `createSkill()` called / Then POST is blocked client-side before the request fires.

**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/__tests__/useCreateSkill.test.ts` (EXTEND — add version-payload and invalid-gate assertions to same file as T-008)

**Estimated**: S

---

### T-015: [GREEN] Extend `useCreateSkill.ts` with version payload
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04 | **Status**: [ ] pending

**Test Plan**:
- Given T-014 tests run / When implementation passes / Then version included in POST.

**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/useCreateSkill.ts` (MODIFY — include `version` in POST payload; guard submit when `isVersionValid` is false)
- `repositories/anton-abyzov/vskill/src/eval-ui/src/api.ts` (MODIFY — pass `version` and `engine` through `createSkill` API call)

**Estimated**: S

---

### US-005: One-click engine install from Studio

---

### T-016: [RED] Tests for `POST /api/v1/studio/install-engine` + SSE stream
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-07, AC-US5-08, AC-US5-09 | **Status**: [ ] pending

**Test Plan**:
- Given `POST /api/v1/studio/install-engine { engine: "anthropic-skill-creator" }` from `127.0.0.1` / When processed / Then `202 { jobId: "<uuid>" }`; `child_process.spawn` called with `["claude", ["plugin","install","skill-creator"]]` and `shell: false`.
- Given successful spawn (exit 0) / When `GET /api/v1/studio/install-engine/:jobId/stream` consumed / Then receives `event:progress` lines and final `event:done {"success":true,"exitCode":0,"stderr":""}`.
- Given spawn exits with code 1 / When SSE consumed / Then `event:done {"success":false,"exitCode":1,"stderr":"<stderr text>"}`.
- Given spawn does not exit within 120s / When timeout fires / Then SSE emits `event:done {"success":false,"exitCode":-1,"stderr":"timeout"}` and stream closes.
- Given `{ engine: "unknown-engine" }` / When processed / Then `400 { error: "unknown-engine" }`.
- Given request from non-loopback IP (e.g. `192.168.1.1`) / When processed / Then `403 { error: "forbidden" }`.
- Given `engine: "anthropic-skill-creator"` and `claude` not on PATH / When processed / Then `412 { error: "claude-cli-missing", remediation: "Install Claude Code CLI first: https://docs.claude.com/claude-code" }`.
- Given request body includes extra `command` field / When processed / Then extra field is ignored; only hard-coded allow-list command spawned (no injection surface).

**Files**:
- `repositories/anton-abyzov/vskill/src/eval-server/__tests__/install-engine-routes.test.ts` (CREATE)

**Estimated**: M

---

### T-017: [GREEN] Implement `install-engine-routes.ts` and register in `eval-server.ts`
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-07, AC-US5-08 | **Status**: [ ] pending

**Test Plan**:
- Given T-016 tests run / When implementation passes / Then all integration tests green.

**Files**:
- `repositories/anton-abyzov/vskill/src/eval-server/install-engine-routes.ts` (CREATE — `INSTALL_COMMANDS` hard-coded allow-list; `POST /api/v1/studio/install-engine`: localhost guard on `req.socket.remoteAddress`, engine name lookup, prerequisite CLI `which` check, `child_process.spawn` with `shell: false`, UUID `jobId`, returns `202`; `GET /api/v1/studio/install-engine/:jobId/stream`: SSE via `sse-helpers.ts`, emits `progress`/`done` events, hard 120s timeout that closes stream)
- `repositories/anton-abyzov/vskill/src/eval-server/eval-server.ts` (MODIFY — register install-engine POST and SSE stream routes)

**Estimated**: L

---

### T-018: [RED] Tests for `InstallEngineModal` component
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04, AC-US5-05 | **Status**: [ ] pending

**Test Plan**:
- Given modal opens for `anthropic-skill-creator` / When rendered in confirming state / Then exact command `"claude plugin install skill-creator"` and security note `"This runs the command in your terminal as your user. Inspect before approving."` are visible; `[Run install]` and `[Cancel]` buttons present.
- Given user clicks `[Cancel]` / When modal closes / Then no fetch to install endpoint fires.
- Given user clicks `[Run install]` and POST responds `202` / When SSE `progress` events arrive / Then spinner shown and last 60 chars of stdout tail updates.
- Given SSE emits `done {success:true}` / When received / Then green checkmark shown and `onInstallSuccess()` callback called.
- Given SSE emits `done {success:false, stderr:"E404 Not Found"}` / When received / Then red X shown, `[Retry]` button visible, full stderr in expandable details.

**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/InstallEngineModal.test.tsx` (CREATE)

**Estimated**: M

---

### T-019: [GREEN] Implement `InstallEngineModal.tsx` component
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04, AC-US5-05 | **Status**: [ ] pending

**Test Plan**:
- Given T-018 tests run / When implementation passes / Then all component tests green.

**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/components/InstallEngineModal.tsx` (CREATE — state machine: idle → confirming → spawning → streaming → success/failure; displays exact command + security note; spinner + stdout tail (max 60 chars) during streaming; green checkmark on success; red X + retry on failure per AC-US5-05)

**Estimated**: M

---

### T-020: [RED] Tests for `useInstallEngine` hook
**User Story**: US-005 | **Satisfies ACs**: AC-US5-06 | **Status**: [ ] pending

**Test Plan**:
- Given successful install (SSE `done {success:true}`) / When `install("anthropic-skill-creator")` called / Then hook calls `GET /api/v1/studio/detect-engines` again and `status` transitions to `"success"`.
- Given user had `anthropic-skill-creator` pre-selected in missing state / When detection re-fetch returns `anthropicSkillCreator: true` / Then hook signals the engine should auto-select.
- Given install POST returns non-202 / When called / Then `status` transitions to `"failure"` and `error` contains response body.

**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/__tests__/useInstallEngine.test.ts` (CREATE)

**Estimated**: S

---

### T-021: [GREEN] Implement `useInstallEngine.ts` hook
**User Story**: US-005 | **Satisfies ACs**: AC-US5-06 | **Status**: [ ] pending

**Test Plan**:
- Given T-020 tests run / When implementation passes / Then all hook tests green.

**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/useInstallEngine.ts` (CREATE — `install(engine)` calls `POST /api/v1/studio/install-engine`, opens `EventSource` for SSE stream, exposes `{ install, progress, status, error, retry }`; on success re-fetches `detect-engines` and signals auto-select to caller)
- `repositories/anton-abyzov/vskill/src/eval-ui/src/api.ts` (MODIFY — add `installEngine()` and `streamInstallProgress(jobId)` wrappers)

**Estimated**: S

---

### T-022: [RED] Tests for `EngineSelector` full install flow (missing → install → auto-select)
**User Story**: US-005 | **Satisfies ACs**: AC-US5-10 | **Status**: [ ] pending

**Test Plan**:
- Given VSkill missing and Anthropic present / When `EngineSelector` renders / Then VSkill option has `[Install]` button.
- Given user clicks `[Install]` on VSkill / When `InstallEngineModal` opens / Then exact command shown.
- Given user clicks `[Run install]` / When SSE streams progress / Then spinner + last stdout line visible in option.
- Given SSE emits `done {success:true}` / When detection re-fetches / Then VSkill option becomes active (no longer greyed) and is auto-selected.

**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/EngineSelector.test.tsx` (EXTEND — add full install-flow scenario to existing file from T-006)

**Estimated**: S

---

### T-023: [GREEN] Wire `InstallEngineModal` + `useInstallEngine` into `EngineSelector`
**User Story**: US-005 | **Satisfies ACs**: AC-US5-05, AC-US5-10 | **Status**: [ ] pending

**Test Plan**:
- Given T-022 tests run / When implementation passes / Then full install-flow test green.

**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/components/EngineSelector.tsx` (MODIFY — connect `[Install]` button click to open `InstallEngineModal`; thread `useInstallEngine` status into spinner/checkmark/error display within the option)

**Estimated**: S

---

### T-024: Wire `EngineSelector` + `VersionInput` into `CreateSkillPage.tsx`
**User Story**: US-002, US-004 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US4-01 | **Status**: [ ] pending

**Test Plan**:
- Given `CreateSkillPage` renders in AI-Assisted mode / When DOM inspected / Then `EngineSelector` appears above the provider/model picker and `VersionInput` appears next to the Name field.
- Given `useCreateSkill` form state changes / When `engine` or `version` updated / Then values are threaded into submit payload and Submit gate reflects `isVersionValid` and engine-available state.

**Files**:
- `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/CreateSkillPage.tsx` (MODIFY — render `<EngineSelector>` above provider/model picker; render `<VersionInput>` next to Name field; pass `engine`, `version`, `setEngine`, `setVersion`, `isVersionValid`, `availableEngines` from `useCreateSkill`; gate Submit on engine-available AND version-valid; additive changes only — do NOT rewrite the existing 54 KB file)

**Estimated**: M

---

### US-006: Bundle rebuild + vskill npm release gate

---

### T-025: [RED] Playwright E2E test for engine selector + version input
**User Story**: US-006 | **Satisfies ACs**: AC-US6-02, AC-US2-06 | **Status**: [ ] pending

**Test Plan**:
- Given `vskill studio` launched and `/create` navigated / When DOM loads / Then `data-testid="engine-selector-vskill"`, `data-testid="engine-selector-anthropic-skill-creator"`, `data-testid="engine-selector-none"` all present in the rendered DOM.
- Given at least one engine missing / When page renders / Then `[Install]` button present for the missing engine.
- Given version input rendered / When inspected / Then input present with default value `"1.0.0"`.

**Files**:
- `repositories/anton-abyzov/vskill/tests/e2e/studio-create-skill-engine.spec.ts` (CREATE)

**Estimated**: S

---

### T-026: [GREEN] Pass E2E smoke — build + launch verify
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02 | **Status**: [ ] pending

**Test Plan**:
- Given `npm run build:eval-ui` runs / When complete / Then zero build errors; `dist/eval-ui/` bundle contains updated chunks with `EngineSelector`, `VersionInput`, `InstallEngineModal` present.
- Given T-025 Playwright spec runs against the built + served bundle / Then all assertions pass.
- Given bundle size measured via `gzip-size dist/eval-ui/assets/*.js` / Then delta does not exceed +50 KB gzipped.

**Files**:
- `repositories/anton-abyzov/vskill/` (build config read-only — no changes expected)

**Estimated**: S

---

### T-027: vskill npm patch release + umbrella sync
**User Story**: US-006 | **Satisfies ACs**: AC-US6-03, AC-US6-04 | **Status**: [ ] pending

**Test Plan**:
- Given all prior tasks green and build passes / When `sw:release-npm` runs / Then vskill version bumps (e.g. `0.5.X → 0.5.X+1`), npm publish succeeds, GitHub Release created.
- Given npm release lands / When umbrella repo updated / Then commit `"sync umbrella after vskill v0.5.X release"` lands on `main` branch.

**Files**:
- `repositories/anton-abyzov/vskill/package.json` (MODIFY — version bump via release tooling)
- Umbrella repo `main` branch (sync commit after release)

**Estimated**: S

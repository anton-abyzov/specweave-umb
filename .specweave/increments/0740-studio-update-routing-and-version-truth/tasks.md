# Tasks: Studio #/updates routing + version truth + sidebar dedupe

## Task Notation

- `[T###]`: Task ID
- `[ ]`: Not started
- `[x]`: Completed
- TDD: each implementation task has a paired RED test task

---

## US-001: View Updates button reaches the Updates view

### T-001: TDD RED — write failing test for `useIsUpdatesRoute()` hook + App.tsx route map

**Description**: Add a unit test asserting that when `window.location.hash === "#/updates"`, the `App.tsx` main slot renders the `<UpdatesPanel />` (or its wrapper) instead of the default `<RightPanel>` empty state. Test must FAIL on current source.

**References**: AC-US1-01, AC-US1-02, AC-US1-03

**Test Plan**:
- **File**: `src/eval-ui/src/__tests__/App.updates-route.test.tsx`
- **Given** the studio is mounted with `window.location.hash = "#/updates"`,
  **When** the App renders,
  **Then** an element with the `[data-testid="updates-panel"]` attribute exists in the document.
- **Given** the hash is empty,
  **When** the App renders,
  **Then** the empty-state placeholder text "Select a skill to view details" is visible.
- **Given** the hash starts as empty and then changes to `"#/updates"`,
  **When** a `hashchange` event fires,
  **Then** the panel becomes visible without re-mount of `<StudioLayout>`.
- Run: `npx vitest run src/eval-ui/src/__tests__/App.updates-route.test.tsx`

**Status**: [x] Completed

---

### T-002: TDD GREEN — add `useIsUpdatesRoute()` + render `<UpdatesPanel />` on `#/updates`

**Description**: In `src/eval-ui/src/App.tsx`:
1. Add a `useIsUpdatesRoute()` hook mirroring `useIsCreateRoute()` (lines 51-69) that watches `window.location.hash.startsWith("#/updates")`.
2. Modify the `mainContent` ternary at lines 477-487 to a chain: `onUpdatesRoute ? <UpdatesPanel/> : onCreateRoute ? <CreateSkillPage/> : <RightPanel ... />`.
3. Add `data-testid="updates-panel"` to the `UpdatesPanel` root element in `pages/UpdatesPanel.tsx` so tests can target it without coupling to text.
4. Add doc comment block on the route hooks describing the `#/create` and `#/updates` route map.

**References**: AC-US1-01, AC-US1-02, AC-US1-03, FR-001, FR-006

**Status**: [x] Completed

---

### T-003: Hash change navigation back-test (AC-US1-04)

**Description**: Extend `App.updates-route.test.tsx` with a scenario where the hash flips from `#/updates` → `""`, asserting RightPanel re-renders without a full re-mount of `StudioLayout`.

**References**: AC-US1-04

**Test Plan**:
- **Given** the hash is `"#/updates"` and the UpdatesPanel is visible,
  **When** `window.location.hash = ""` and a `hashchange` event fires,
  **Then** the empty-state placeholder reappears within the same `StudioLayout` instance (verified by stable ref via testid).

**Status**: [x] Completed

---

### T-004: Playwright E2E — click "View Updates" and assert panel renders (AC-US1-05)

**Description**: New file `e2e/updates-route.spec.ts`. Stubs `/api/skills/updates` to return one outdated entry, opens the studio, dismisses any banner, asserts the toast "View Updates" button is visible, clicks it, asserts URL contains `#/updates` AND the UpdatesPanel testid is present.

**References**: AC-US1-05

**Test Plan**:
- **File**: `e2e/updates-route.spec.ts`
- Run: `npx playwright test e2e/updates-route.spec.ts`

**Status**: [x] Completed

---

## US-002: Sidebar shows each skill exactly once per scope

### T-005: TDD RED — fixture-based test for Layout 2 + plugin-manifest dedupe

**Description**: Write a test that creates a temp directory mimicking the bug:
```
<tmp>/plugins/personal/.claude-plugin/plugin.json   (manifest)
<tmp>/plugins/personal/skills/foo/SKILL.md          (skill)
```
Then calls the scanner pipeline and asserts that the resulting `SkillInfo[]` contains EXACTLY ONE entry with `dir` ending in `plugins/personal/skills/foo`, with `scopeV2 === "authoring-plugin"`.

**References**: AC-US2-01, AC-US2-03, AC-US2-04

**Test Plan**:
- **File**: `src/eval/__tests__/skill-scanner.plugin-dedupe.test.ts`
- **Given** a tmp project root with a manifest-bearing plugin,
  **When** the scanner pipeline used by `/api/skills` runs,
  **Then** there is exactly one `SkillInfo` per unique `dir`, AND the manifest-bearing skill has `scopeV2 === "authoring-plugin"`.
- Negative test (AC-US2-04): same fixture WITHOUT the manifest → exactly one entry with `scopeV2 === "authoring-project"` (legacy behavior preserved).
- Run: `npx vitest run src/eval/__tests__/skill-scanner.plugin-dedupe.test.ts`

**Status**: [x] Completed

---

### T-006: TDD GREEN — Layout 2 walker skips manifest-bearing plugin dirs

**Description**: In `src/eval/skill-scanner.ts` (around lines 248-255 in `scanSkills` Layout 2 path):
1. Before recursing into `<plugin>/skills/`, check `existsSync(<plugin>/.claude-plugin/plugin.json)`.
2. If the manifest exists, skip — `scanAuthoredPluginSkills` owns this subtree.
3. Add a doc comment block at the top of `skill-scanner.ts` describing the Layout 2 / authored-plugin contract.

**References**: AC-US2-01, FR-002, FR-006

**Status**: [x] Completed

---

### T-007: Defensive post-concat dedupe in api-routes

**Description**: In `src/eval-server/api-routes.ts` around lines 1709-1713, after concatenating `[...triScopeSkills, ...installedPluginSkills, ...authoredPluginSkills]`, dedupe by canonical `dir` using a `Map<string, SkillInfo>`. When two entries share `dir`, keep the one with `scopeV2 === "authoring-plugin"` (manifest is the source of truth). Emit `console.warn` once per session listing dropped duplicates so we can detect new overlap sources.

**References**: AC-US2-02, FR-003

**Status**: [x] Completed

---

### T-008: Test post-concat dedupe (AC-US2-02)

**Description**: Unit test that constructs a synthetic `SkillInfo[]` with two entries sharing `dir` (one `authoring-project`, one `authoring-plugin`), runs the dedupe helper, and asserts the result has one entry with `authoring-plugin`.

**References**: AC-US2-02

**Test Plan**:
- **File**: `src/eval-server/__tests__/api-routes.dedupe.test.ts` (or extend an existing file).
- Run: `npx vitest run src/eval-server/__tests__/api-routes.dedupe.test.ts`

**Status**: [x] Completed

---

## US-003: Installed version is disk truth

### T-009: TDD RED — outdated.ts disk-version emission test

**Description**: Test that `outdatedCommand` (or its tested function) reads the SKILL.md frontmatter at the resolved install path and emits that as `currentVersion`. Cover three branches:
- (a) on-disk drift: lockfile says 1.0.0, disk says 1.3.0, latest 1.0.6 → emit `currentVersion: "1.3.0"` AND `updateAvailable: false` (because 1.3.0 > 1.0.6).
- (b) on-disk missing: returns lockfile version + `warning: "disk version unreadable"`.
- (c) on-disk equal lockfile: emits the version, no warning.

**References**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04

**Test Plan**:
- **File**: `src/commands/__tests__/outdated.disk-version.test.ts`
- Mock the lockfile reader and the SKILL.md reader (use `vi.hoisted()` per project conventions).
- Run: `npx vitest run src/commands/__tests__/outdated.disk-version.test.ts`

**Status**: [x] Completed

---

### T-010: TDD GREEN — outdated.ts reads disk frontmatter, falls back to lockfile

**Description**: In `src/commands/outdated.ts` (lines 30-44):
1. For each lockfile entry, resolve the install path (use existing path-resolution if present; else compose from `<root>/.claude/skills/<skill>` or the lockfile's `installPath` field).
2. Read SKILL.md frontmatter via the existing project YAML helper. Extract `metadata.version`.
3. Use `metadata.version` as `currentVersion` if readable; else fall back to `entry.version` and add `warning: "disk version unreadable"`.
4. After receiving platform `latestVersion`, compare with semver: if disk version >= latest, set `updateAvailable: false` and skip the "update" CTA.
5. Add a top-of-file doc comment describing the disk-vs-lockfile contract (FR-006).

**References**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-05, FR-004

**Status**: [x] Completed

---

## US-004: Update merge keys by full identity

### T-011: TDD RED — mergeUpdatesIntoSkills origin gating + identity match

**Description**: Test that `mergeUpdatesIntoSkills` (in `src/eval-ui/src/api.ts` lines 1033-1065):
- When given a `SkillUpdateInfo` for `obsidian-brain` and a `SkillInfo[]` containing two rows (one `origin: "installed"`, one `origin: "authored"`), only the installed row receives `updateAvailable: true` and the version transition.
- When two installed rows share the leaf `skill` but have different `pluginName`, only the row matching the lockfile-derived `pluginName/skill` identity receives the merged update info.

**References**: AC-US4-01, AC-US4-02, AC-US4-03

**Test Plan**:
- **File**: `src/eval-ui/src/__tests__/mergeUpdatesIntoSkills.test.ts`
- Run: `npx vitest run src/eval-ui/src/__tests__/mergeUpdatesIntoSkills.test.ts`

**Status**: [x] Completed

---

### T-012: TDD GREEN — gate merge by `origin === "installed"` + match by full identity

**Description**: In `src/eval-ui/src/api.ts:mergeUpdatesIntoSkills` (lines ~1033-1065):
1. Add a top-level filter: only consider rows with `s.origin === "installed"`.
2. Replace the `s.skill === u.name`-style match with full identity comparison `(s.pluginName + "/" + s.skill)` derived from the `SkillUpdateInfo.name` (e.g. parse `anton-abyzov/vskill/obsidian-brain` to last two segments and compare). Fall back to skill-only match only when the SkillUpdateInfo does not carry a plugin scope.
3. Add a top-of-file contract block on the function describing the gating rules (FR-006).

**References**: AC-US4-01, AC-US4-02, FR-005, FR-006

**Status**: [x] Completed

---

### T-013: AC-US4-04 — push toast displays disk version

**Description**: This is automatically satisfied once T-010 emits the disk version. Add an assertion in `src/eval-ui/src/components/__tests__/UpdateToast.test.tsx` (create if missing) that the toast text formats `installed → latest` from the merged SkillUpdateInfo's installed field after T-010's pipeline.

**References**: AC-US4-04

**Status**: [x] Completed

---

## Verification & shipping

### T-014: Run full vitest suite + lint

**Description**: `npx vitest run` from the vskill repo root. Address any new failures. Then `npm run lint` if defined.

**Status**: [x] Completed

---

### T-015: Run Playwright E2E suite

**Description**: `npx playwright test` — the new `updates-route.spec.ts` must pass; existing E2E (especially `update-click-flow.spec.ts` from 0736) must remain green.

**Status**: [x] Completed

---

### T-016: Browser verification via preview tools

**Description**: Build vskill, install locally via `npm link` or `npm pack`, run `vskill studio`, use preview_* tools to:
1. Confirm the sidebar shows obsidian-brain in exactly two locations (PROJECT > .CLAUDE 1.1.0; AUTHORING > PLUGINS > personal 1.3.0).
2. Confirm the bell toast shows the disk version (1.3.0) for obsidian-brain.
3. Click "View Updates" — assert the UpdatesPanel renders.
4. Take screenshot evidence and attach to the increment reports/ folder.

**Status**: [x] Completed

---

### T-017: Commit + push + publish vskill@0.5.117

**Description**:
1. Commit per CLAUDE.md conventions (one-line subject, no AI references).
2. Push to repositories/anton-abyzov/vskill main.
3. Bump vskill `package.json` to 0.5.117.
4. `npm run build` to refresh `dist/` (so the bundle ships the fix).
5. `npm publish` from the vskill repo (if user authorizes; otherwise stop and ask).
6. Update umbrella repo with the bumped lockfile.

**Status**: [x] Completed

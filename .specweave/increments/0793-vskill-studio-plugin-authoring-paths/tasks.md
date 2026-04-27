---
increment: 0793-vskill-studio-plugin-authoring-paths
total_tasks: 14
completed_tasks: 14
---

# Tasks: vskill Studio — First-class plugin authoring paths

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started · `[x]`: Completed

All paths below are relative to `repositories/anton-abyzov/vskill/`.

---

## Phase 1: Foundation (shared backend reuse)

### T-001: Export `pluginJsonScaffold()` and add `validateClaudePlugin()` helper
**Status**: [x] completed
**Refs**: FR-001, FR-002

**Description**: The current `pluginJsonScaffold()` in `src/eval-server/authoring-routes.ts:77` is module-private. Both Lane A (CLI) and Lane B2 (endpoint) need it, so promote it to an exported helper. Add a sibling `validateClaudePlugin(pluginPath)` that wraps `spawnSync('claude', ['plugin', 'validate', pluginPath])` and returns `{ ok, stderr, skipped }`. Soft-skip on `ENOENT`.

**Files**:
- `src/eval-server/authoring-routes.ts` (export `pluginJsonScaffold`; add `validateClaudePlugin` OR factor into `src/core/plugin-validator.ts`).

**Test Plan**:
- **File**: `src/core/plugin-validator.test.ts` *(new)*
- **TC-001** Given `claude` is on PATH and the plugin manifest is valid → When `validateClaudePlugin(path)` runs → Then returns `{ ok: true, skipped: false, stderr: '' }`.
- **TC-002** Given `claude` is NOT on PATH → When the helper runs → Then returns `{ ok: true, skipped: true }` (soft success).
- **TC-003** Given the manifest is invalid → When the helper runs → Then returns `{ ok: false, stderr: '<message>', skipped: false }`.

**Dependencies**: none.

---

## Phase 2: Lane A — `vskill plugin new` CLI

### T-002: Create `src/commands/plugin.ts`
**Status**: [x] completed
**Refs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06

**Description**: New Commander subcommand `vskill plugin new <name> [--description "..."] [--with-skill <skill>]`. Validates kebab-case, fails on existing manifest, scaffolds `<name>/.claude-plugin/plugin.json` via `pluginJsonScaffold()`, optionally scaffolds a skill via the existing skill-emitter (see `src/core/skill-emitter.ts`), runs `validateClaudePlugin`, unlinks manifest on validator failure.

**Files**:
- `src/commands/plugin.ts` *(new)*

**Test Plan**:
- **File**: `src/commands/plugin.test.ts` *(new)*
- **TC-004** Happy path: Given a fresh tmpdir → When `vskill plugin new my-plug` runs → Then `<tmp>/my-plug/.claude-plugin/plugin.json` exists with `{ name, description, author }` shape and `claude plugin validate` passes.
- **TC-005** With skill: Given a fresh tmpdir → When `vskill plugin new my-plug --with-skill greet` → Then `<tmp>/my-plug/skills/greet/SKILL.md` also exists.
- **TC-006** Custom description: When `vskill plugin new my-plug --description "Hi"` → Then manifest contains `"description": "Hi"`.
- **TC-007** Collision: Given `<tmp>/my-plug/.claude-plugin/plugin.json` already exists → When command runs → Then exits non-zero with "manifest already exists" and does NOT overwrite.
- **TC-008** Bad name: When `vskill plugin new MyPlug` (camelCase) runs → Then exits non-zero with kebab-case error and creates no files.
- **TC-009** Validator failure: Given `claude plugin validate` is forced to fail (mocked) → When command runs → Then manifest is unlinked and stderr is printed.
- **TC-010** Soft-skip: Given `claude` is not on PATH → When command runs → Then prints warning, exits 0, manifest stays.

**Dependencies**: T-001.

### T-003: Wire `plugin` subcommand into `bin/vskill.ts`
**Status**: [x] completed
**Refs**: AC-US1-01

**Description**: Register the new subcommand on the existing Commander root so `vskill plugin new …` works after `npm link`.

**Files**: `bin/vskill.ts`.

**Test Plan**: covered transitively by T-002 (the test invokes the bin).

**Dependencies**: T-002.

---

## Phase 3: Lane B2 — Convert endpoint

### T-004: `POST /api/authoring/convert-to-plugin`
**Status**: [x] completed
**Refs**: AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-06

**Description**: Add route handler in `src/eval-server/authoring-routes.ts`. Body: `{ anchorSkillDir, pluginName, description }` (anchor = absolute path of any skill in the candidate group; server derives `pluginDir = dirname(dirname(anchorSkillDir))`). Validates anchorSkillDir is inside workspace root (existing `isInsideRoot` pattern), the anchor's parent is named `skills/` (rejects `invalid-anchor-shape` otherwise), pluginName is kebab-case, no existing manifest, ≥1 `<pluginDir>/skills/*/SKILL.md`. Writes manifest via `pluginJsonScaffold()`. Runs `validateClaudePlugin`. On failure: unlinks manifest, returns 422 + stderr. On success: returns 200 + `{ ok, pluginDir, manifestPath, validation }`.

**Files**: `src/eval-server/authoring-routes.ts`.

**Test Plan**:
- **File**: `src/eval-server/authoring-routes.test.ts` *(extend existing)*
- **TC-011** Happy path: Given workspace `<tmp>` with `<tmp>/foo/skills/a/SKILL.md` → When POST with `{ anchorSkillDir: "<tmp>/foo/skills/a", pluginName: "foo", description: "..." }` → Then 200 + `<tmp>/foo/.claude-plugin/plugin.json` exists.
- **TC-012** Outside workspace: When `anchorSkillDir: "/tmp/elsewhere/skills/x"` → Then 400 `anchor-outside-root`.
- **TC-013** Manifest already exists: Given `<tmp>/foo/.claude-plugin/plugin.json` exists → When POST → Then 409.
- **TC-014** No skills: Given `<tmp>/foo/skills/bar` exists but contains no `SKILL.md` → When POST with anchor at `<tmp>/foo/skills/bar` → Then 400 `no-skills-to-convert`.
- **TC-015** Bad name: When `pluginName: "FooBar"` → Then 400.
- **TC-016** Validator failure: When `claude plugin validate` is forced to fail (symlink `claude → /usr/bin/false`) → Then 422 `validation-failed`, manifest deleted, response includes `stderr`.
- **TC-017** Invalid anchor shape: When `anchorSkillDir: "<tmp>/foo/bar/baz"` (parent not `skills/`) → Then 400 `invalid-anchor-shape`.

**Dependencies**: T-001.

---

## Phase 4: Lane B1 + B2 frontend

### T-005: Sidebar parent-dir grouping for `authoring-project`
**Status**: [x] completed
**Refs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05

**Description**: In `src/eval-ui/src/components/Sidebar.tsx:106` `partitionByGroupSource()`, bucket `authoringProject` skills by their `plugin` field. When a bucket has ≥2 entries AND its dir is not the workspace root, emit a `candidatePluginGroups: { dir, skills }[]` array; render those buckets via the existing `PluginTreeGroup` styling with a "Not a plugin yet · Convert →" pill. Single-skill buckets keep current flat rendering.

**Files**: `src/eval-ui/src/components/Sidebar.tsx`.

**Test Plan** (manual + smoke):
- **TC-017** Given TestLab/hi-anton (3 skills, no manifest) → When Studio loads → Then sidebar shows `hi-anton` group with 3 nested skills + "Not a plugin yet · Convert →" pill (verify via `preview_snapshot`).
- **TC-018** Given a workspace with one standalone skill → When Studio loads → Then no group appears (skill renders flat).
- **TC-019** Given an existing real plugin (with manifest) → When Studio loads → Then it still renders under AUTHORING > PLUGINS unchanged.

**Dependencies**: none (UI-only).

### T-006: `convertToPlugin()` API client
**Status**: [x] completed
**Refs**: AC-US3-02

**Description**: Add `convertToPlugin(req)` to `src/eval-ui/src/api.ts:370`. Wraps the POST.

**Files**: `src/eval-ui/src/api.ts`.

**Test Plan**: covered by T-007 integration.

**Dependencies**: T-004.

### T-007: `<ConvertToPluginDialog>` + CTA wiring
**Status**: [x] completed
**Refs**: AC-US3-01, AC-US3-04, AC-US3-05

**Description**: New small modal component. Triggered by the "Convert →" pill (T-005) AND by candidate-dir buttons in `AuthoringPluginEmptyState`. Prefills name from folder basename, description from `package.json#description` if present. Submits via `convertToPlugin()`. On success: dispatch `refreshSkills()` (same pattern as the create-skill modal — see [interview-0788 notes](../../state/interview-0788-studio-create-skill-redirect-fix.json)). On 422: display the validator stderr inline.

**Files**:
- `src/eval-ui/src/components/Sidebar.tsx` (CTA wiring + empty-state list)
- `src/eval-ui/src/components/ConvertToPluginDialog.tsx` *(new)*

**Test Plan**:
- **TC-020** Happy path (preview tools): click "Convert →" on hi-anton group → fill description (name prefilled) → submit → AUTHORING > PLUGINS now shows hi-anton with 3 nested skills, AUTHORING > SKILLS no longer lists them.
- **TC-021** Validator failure: with a mocked 422 response → dialog displays stderr, sidebar unchanged.

**Dependencies**: T-004, T-005, T-006.

---

## Phase 5: Lane C — skill-builder docs

### T-008: Add "Authoring a plugin" section to skill-builder
**Status**: [x] completed
**Refs**: AC-US4-01, AC-US4-02, AC-US4-03

**Description**: Edit `plugins/skills/skills/skill-builder/SKILL.md`. Add a section that documents the heuristic ("if 2+ related skills under shared identity, prefer plugin") and the three concrete paths. Bump version 1.0.3 → 1.0.4.

**Files**: `plugins/skills/skills/skill-builder/SKILL.md`.

**Test Plan**: prose-only; covered by review (no automated test). Verify the version bumps and the three paths are referenced by name.

**Dependencies**: T-002, T-007 (so the documented paths exist before doc references them).

---

## Phase 6: Lane D — Modal polish

### T-009: Reorder Create-Skill modal modes
**Status**: [x] completed
**Refs**: AC-US5-01, AC-US5-02, AC-US5-03

**Description**: Edit `src/eval-ui/src/components/CreateSkillModal.tsx` (file path verified during implementation; may be `CreateSkillPage.tsx` per [interview-0788](../../state/interview-0788-studio-create-skill-redirect-fix.json)). Reorder: Standalone → Existing plugin → Plugin (multi-skill). Add captions per AC. Backend request body unchanged.

**Files**: `src/eval-ui/src/components/CreateSkillModal.tsx` (or `CreateSkillPage.tsx`).

**Test Plan**:
- **TC-022** Visual snapshot before/after via `preview_snapshot`.
- **TC-023** Submit with mode `"new-plugin"` still produces the same 200 response (backend contract unchanged).

**Dependencies**: none.

---

## Phase 7: Verification

### T-010: Run full vitest suite
**Status**: [x] completed
**Description**: `npm test` in `repositories/anton-abyzov/vskill/`. Ensure new specs pass and 0740 dedupe specs still pass.

### T-011: Build vskill (TS + UI bundle)
**Status**: [x] completed
**Description**: `npm run build` (tsc) + the UI build script. Confirm no type errors.

### T-012: Live verification with preview tools
**Status**: [x] completed
**Refs**: AC-US2-01..05, AC-US3-01..06
**Description**: Self-install per `feedback_self_install_vskill.md` — `npx vskill@<dev-tag> studio` against `~/Projects/TestLab/hi-anton/`.
1. `preview_start` against localhost:3109.
2. `preview_snapshot` baseline (pre-fix state — 3 flat skills).
3. Switch to dev build → observe Lane B1 grouping.
4. `preview_click` on "Convert →" → fill dialog → submit → `preview_snapshot` after.
5. Confirm AUTHORING > PLUGINS now shows `hi-anton` with all 3 skills nested.
6. Capture `preview_screenshot` for the user.

### T-013: Parallel sub-agent regression scan
**Status**: [x] completed
**Description**: Spawn one Explore sub-agent (no commit, no file create — per `feedback_subagent_no_commit_no_create.md`) to independently re-walk `plugin-scanner.ts` + `skill-scanner.ts` + `Sidebar.tsx` and confirm: (a) `dedupeByDir` precedence unchanged, (b) `authoring-plugin > authoring-project` still holds, (c) standalone single-skill render path is unchanged.

### T-014: `npm run build:worker && npm run deploy` (vskill-platform sync) — only if marketplace changes
**Status**: [x] completed (likely skipped)
**Description**: Lane C bumps skill-builder to 1.0.4. If the registry on vskill-platform shows a stale version after publish, run platform deploy per `project_vskill_platform_deploy.md`. Otherwise skip.

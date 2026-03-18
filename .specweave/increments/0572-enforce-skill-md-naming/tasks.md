# Tasks: Enforce SKILL.md naming at install time for non-Claude tools

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), sonnet (default)

---

## US-001: Fix copyPluginFiltered rename logic

### T-001: Add isSkillMdCandidate helper and patch copyPluginFiltered rename branch
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] Completed
**Test**: Given `copyPluginFiltered()` processes a plugin whose skill directory contains `frontend-design.md` (no `SKILL.md`) → When the function copies files into the target directory → Then the output directory contains `SKILL.md` with frontmatter applied and `frontend-design.md` does not appear

**Implementation Details**:
- In `vskill/src/commands/add.ts`, add `isSkillMdCandidate(entry: string, relPath: string): boolean` helper
  - Returns true when: entry ends with `.md`, entry is not `SKILL.md`, entry is not in `README.md`/`CHANGELOG.md`/`LICENSE.md`/`FRESHNESS.md` skip list, and relPath indicates depth >= 2 under `skills/` and is not inside an `agents/` subdirectory
- Modify the `else if` file-copy branch in `copyPluginFiltered` (lines 661-667): when `entry === "SKILL.md" || isSkillMdCandidate(entry, relPath)`, read content, call `ensureFrontmatter(raw, skillName)`, write as `SKILL.md`; otherwise copy verbatim
- AC-US1-02 (existing SKILL.md passthrough) is covered by the `entry === "SKILL.md"` branch remaining first
- AC-US1-03 (skip README.md etc.) covered by the skip-list check in `isSkillMdCandidate`
- AC-US1-04 (multiple candidates → first alphabetically) covered because `readdirSync` returns entries in filesystem order; when multiple candidates exist, only one write to `SKILL.md` occurs — the last one processed wins, so entries must be sorted before iteration or only the first candidate is promoted (sort `entries` before the loop and break after writing `SKILL.md` for a given directory)

---

## US-002: Create ensureSkillMdNaming post-install guard

### T-002: Implement NamingResult interface and ensureSkillMdNaming() in migrate.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Status**: [x] Completed
**Test**: Given a skill directory at tmpdir containing `custom-skill.md` (no `SKILL.md`) → When `ensureSkillMdNaming(skillsDir)` is called → Then `custom-skill/SKILL.md` exists with frontmatter and `custom-skill.md` is deleted; calling again changes nothing (idempotent)

**Implementation Details**:
- In `vskill/src/installer/migrate.ts`, export `NamingResult` interface: `{ renamedCount: number; errors: string[] }`
- Implement `export function ensureSkillMdNaming(skillsDir: string): NamingResult`
  - Walk one level of subdirectories in `skillsDir` (and two levels for namespaced dirs like `sw/`)
  - For each subdirectory: if `SKILL.md` already exists → skip (idempotent, AC-US2-01)
  - Collect all `.md` files in the directory, filter out `README.md`, `CHANGELOG.md`, `LICENSE.md`, `FRESHNESS.md`
  - If no candidates remain → skip (AC-US2-04)
  - Sort candidates alphabetically, take first
  - Read content, call `ensureFrontmatter(content, dirName)`, write as `SKILL.md`, delete original file (AC-US2-02, AC-US2-03)
  - Increment `renamedCount`; catch errors and push to `errors` array
- Export from the same file as `migrateStaleSkillFiles` — no new imports needed, same `ensureFrontmatter` dependency (AC-US2-05)

---

## US-003: Wire enforcement into all install paths

### T-003: Import and call ensureSkillMdNaming in add.ts after install paths
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02
**Status**: [x] Completed
**Test**: Given the post-install wiring is added to `add.ts` → When `vskill add` completes installing a plugin → Then `ensureSkillMdNaming` is called on the plugin cache/install directory so any residual misnamed files are corrected

**Implementation Details**:
- In `add.ts`, add import: `import { ensureSkillMdNaming } from "../installer/migrate.js"`
- After `copyPluginFiltered(pluginDir, cacheDir)` call (~line 1158): call `ensureSkillMdNaming(cacheDir)`
- After the GitHub plugin install skill loop (~lines 1637-1640): for each `plugDir` written, call `ensureSkillMdNaming(plugDir)`
- Keep calls non-throwing: `ensureSkillMdNaming` already returns errors in the result rather than throwing

### T-004: Import and call ensureSkillMdNaming in update.ts as defense-in-depth
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02
**Status**: [x] Completed
**Test**: Given `update.ts` update path completes writing a skill directory → When `ensureSkillMdNaming` is called on that directory → Then any misnamed file is corrected without breaking correctly named `SKILL.md`

**Implementation Details**:
- In `vskill/src/commands/update.ts`, add import: `import { ensureSkillMdNaming } from "../installer/migrate.js"`
- After the write step at ~line 173 (where update.ts writes the skill), call `ensureSkillMdNaming(skillDir)` on each updated skill directory
- Ensure the call does not disrupt the existing update flow — it is a no-op when `SKILL.md` is already correctly named

### T-005: Wire ensureSkillMdNaming in init.ts alongside migrateStaleSkillFiles
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03
**Status**: [x] Completed
**Test**: Given `vskill init` runs migration on agent skill directories → When `ensureSkillMdNaming` is called after `migrateStaleSkillFiles` for each agent → Then any remaining misnamed files inside skill subdirectories are corrected

**Implementation Details**:
- In `vskill/src/commands/init.ts`, add import for `ensureSkillMdNaming`
- Locate where `migrateStaleSkillFiles(agentSkillsDir)` is called for each agent
- After each `migrateStaleSkillFiles` call, call `ensureSkillMdNaming(agentSkillsDir)` on the same directory
- Both functions are safe to run on the same directory sequentially

---

## US-004: Unit tests for fix and enforcement

### T-006: Write unit tests for ensureSkillMdNaming in migrate.test.ts
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Status**: [x] Completed
**Test**: Given test suite with real tmpdir fixtures → When each scenario runs → Then assertions match BDD outcomes for rename, idempotency, skip-list exclusion, and alphabetical selection

**Implementation Details**:
- Add a new `describe("ensureSkillMdNaming", ...)` block in `migrate.test.ts` following the existing pattern (real tmpdir, `beforeEach`/`afterEach` cleanup)
- TC-001 (AC-US4-01): Create `skillsDir/my-skill/design.md` → call `ensureSkillMdNaming(skillsDir)` → assert `SKILL.md` exists with frontmatter, `design.md` deleted, `renamedCount === 1`
- TC-002 (AC-US4-02): Create `skillsDir/my-skill/SKILL.md` → call `ensureSkillMdNaming(skillsDir)` → assert no files changed, `renamedCount === 0`
- TC-003 (AC-US4-03): Create `skillsDir/my-skill/README.md` and `skillsDir/my-skill/guide.md` → call → assert `SKILL.md` exists (from `guide.md`), `README.md` untouched
- TC-004 (AC-US4-04): Create `skillsDir/my-skill/beta.md` and `skillsDir/my-skill/alpha.md` → call → assert `alpha.md` becomes `SKILL.md` (alphabetically first), `beta.md` deleted
- TC-005: Create `skillsDir/my-skill/` with only `README.md` → call → assert no rename, `renamedCount === 0` (AC-US2-04 parity)
- TC-006: Empty skill directory (no `.md` files) → call → assert no error, no rename

### T-007: Write unit tests for the copyPluginFiltered fix in add.test.ts
**User Story**: US-004 | **Satisfies ACs**: AC-US4-05
**Status**: [x] Completed
**Test**: Given a mock plugin source directory with `skills/my-skill/custom-name.md` instead of `SKILL.md` → When `copyPluginFiltered(sourceDir, targetDir)` is called → Then `targetDir/my-skill/SKILL.md` exists with frontmatter and `custom-name.md` does not appear in the output

**Implementation Details**:
- In `add.test.ts` (or equivalent test file for `add.ts`), add tests for `copyPluginFiltered` rename behavior
- TC-007 (AC-US4-05): Build tmpdir plugin structure `skills/my-skill/custom-name.md`, call `copyPluginFiltered`, assert `SKILL.md` present with frontmatter, `custom-name.md` absent
- TC-008: Plugin with existing `SKILL.md` → assert `SKILL.md` passthrough with frontmatter (no regression)
- TC-009: Plugin with `README.md` in a skill dir → assert `README.md` is skipped from rename (copied as-is or filtered per `shouldSkipFromCommands`)
- TC-010: Plugin with two non-SKILL.md content files → assert only one `SKILL.md` written (first alphabetically promoted)
- Export `copyPluginFiltered` for testability if currently unexported, or test via a thin integration path using tmpdir

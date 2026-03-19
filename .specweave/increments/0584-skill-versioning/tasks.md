# Tasks: Skill Versioning for Verified Skills

---
increment: 0584-skill-versioning
generated: 2026-03-19
test_mode: TDD
---

## US-001: Full-File Hash Computation

### T-001: RED — Write failing tests for normalizeContent and multi-file computeSha
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [x] completed
**Test**: Given `src/updater/source-fetcher.test.ts` exists → When tests for `normalizeContent` (CRLF→LF, BOM trim) and multi-file `computeSha` (sorted paths, 64-char hex, null-byte separator) are written → Then `npx vitest run` reports these tests as FAILING (red phase)

---

### T-002: GREEN — Implement normalizeContent and computeSha overload in source-fetcher.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [x] completed
**Test**: Given the failing tests from T-001 → When `normalizeContent(content: string): string` (strips `\uFEFF`, normalizes CRLF→LF) and overloaded `computeSha(files: Record<string,string>): string` (sorts keys, formats as `path\0content\n`, returns full 64-char hex) are implemented → Then all T-001 tests pass green and the existing single-string overload still works

---

## US-002, US-003, US-004: Version Utilities

### T-003: RED — Write failing tests for version.ts utilities
**User Story**: US-002, US-003, US-004 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US4-01, AC-US4-02, AC-US4-03
**Status**: [x] completed
**Test**: Given `src/utils/version.test.ts` is created → When tests covering `extractFrontmatterVersion` (valid semver, missing field, invalid semver), `bumpPatch` (normal case, non-semver fallback), and `resolveVersion` (serverVersion priority, frontmatter override, auto-patch, first-install default) are written → Then `npx vitest run` reports these tests as FAILING

---

### T-004: GREEN — Implement src/utils/version.ts
**User Story**: US-002, US-003, US-004 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US4-01, AC-US4-02, AC-US4-03
**Status**: [x] completed
**Test**: Given the failing tests from T-003 → When `extractFrontmatterVersion(content: string): string | undefined`, `bumpPatch(version: string): string`, and `resolveVersion(opts: { serverVersion?, frontmatterVersion?, currentVersion?, hashChanged, isFirstInstall }): string` are implemented with the priority chain (server > frontmatter > auto-patch > "1.0.0") → Then all T-003 tests pass green

---

## US-007: Lockfile Types and Migration

### T-005: Add files field to SkillLockEntry type
**User Story**: US-006, US-007 | **Satisfies ACs**: AC-US6-02, AC-US6-03, AC-US7-03
**Status**: [x] completed
**Test**: Given `src/lockfile/types.ts` is modified → When `files?: string[]` is added to `SkillLockEntry` → Then `npx vitest run` shows no TypeScript compilation errors and all existing lockfile tests still pass

---

### T-006: RED — Write failing tests for lockfile migration
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04
**Status**: [x] completed
**Test**: Given `src/lockfile/migration.test.ts` is created → When tests for `migrateLockEntry` (version `""` → `"1.0.0"`, `"0.0.0"` → `"1.0.0"`, valid version `"2.3.1"` preserved, missing `files` stays `undefined`) and `migrateLock` (iterates all entries) are written → Then `npx vitest run` reports these tests as FAILING

---

### T-007: GREEN — Implement migration.ts and wire into readLockfile
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04
**Status**: [x] completed
**Test**: Given the failing tests from T-006 → When `migrateLockEntry` and `migrateLock` are implemented in `src/lockfile/migration.ts` (pure functions, no mutation), `migrateLock()` is called inside `readLockfile()` in `lockfile.ts`, and functions are re-exported from `lockfile/index.ts` → Then all T-006 tests pass green and existing `lockfile.test.ts` tests still pass

---

## US-005, US-006: Update Command

### T-008: RED — Write failing tests for no-change detection and ghost file cleanup in update.ts
**User Story**: US-005, US-006 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US6-01, AC-US6-02, AC-US6-03
**Status**: [x] completed
**Test**: Given a lockfile entry with `files: ["SKILL.md", "agents/a.md", "agents/b.md"]` and a fetched result containing only `["SKILL.md", "agents/a.md"]` → When the update command runs → Then tests assert: `agents/b.md` is deleted from disk, lockfile `files` array reflects new state, and when sha matches no files are written and a "no changes" message is printed

---

### T-009: GREEN — Wire version resolution, ghost file cleanup, and multi-file write into update.ts
**User Story**: US-005, US-006 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US6-01, AC-US6-02, AC-US6-03
**Status**: [x] completed
**Test**: Given the failing tests from T-008 → When `update.ts` is modified to: (1) skip on identical 64-char sha and print "no changes", (2) call `resolveVersion()` after hash comparison, (3) call `cleanupGhostFiles(skillDir, entry.files, newFiles)` before writing, (4) write all files from `result.files` map, (5) persist `files` array in the updated lockfile entry → Then all T-008 tests pass green

---

## US-001, US-003: Add Command

### T-010: RED — Write failing tests for 64-char SHA and files manifest in add.ts
**User Story**: US-001, US-003 | **Satisfies ACs**: AC-US1-03, AC-US3-01, AC-US3-04
**Status**: [x] completed
**Test**: Given the add command test suite → When tests assert that new lockfile entries have a 64-char `sha` (not 12-char), a `files` array of sorted relative paths, and a `version` from `extractFrontmatterVersion` or defaulting to `"1.0.0"` → Then `npx vitest run` reports these tests as FAILING

---

### T-011: GREEN — Switch add.ts SHA call sites, add files manifest, and version extraction
**User Story**: US-001, US-003 | **Satisfies ACs**: AC-US1-03, AC-US3-01, AC-US3-04
**Status**: [x] completed
**Test**: Given the failing tests from T-010 → When all six `createHash("sha256")...slice(0, 12)` call sites in `add.ts` are replaced with `computeSha()`, lockfile entries include `files` array, and `extractFrontmatterVersion` is used with `"1.0.0"` fallback → Then all T-010 tests pass green

---

### T-012: Populate FetchResult.files in source-fetcher fetch functions
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [x] completed
**Test**: Given `fetchGitHubFlat`, `fetchPlugin`, and `fetchRegistry` in `source-fetcher.ts` → When each is updated to populate `FetchResult.files` as a `Record<string, string>` path-to-content map and passes it to the `computeSha` files overload → Then existing source-fetcher tests pass and all returned `sha` values are 64 chars

---

### T-013: Full test suite green gate
**User Story**: US-001, US-002, US-003, US-004, US-005, US-006, US-007 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US2-01, AC-US2-02, AC-US2-03, AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US4-01, AC-US4-02, AC-US4-03, AC-US5-01, AC-US5-02, AC-US5-03, AC-US6-01, AC-US6-02, AC-US6-03, AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04
**Status**: [x] completed
**Test**: Given all implementation tasks T-001 through T-012 are complete → When `npx vitest run` is executed → Then all tests pass with no failures, unit coverage is at or above 95%, integration coverage at or above 90%, and no TypeScript errors remain

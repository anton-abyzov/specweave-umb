---
increment: 0444-filter-framework-plugin-skills
title: "Filter Framework Plugin Skills from Marketplace"
total_tasks: 14
completed_tasks: 14
by_user_story:
  US-001: [T-001, T-002]
  US-002: [T-003, T-004]
  US-003: [T-005, T-006, T-007, T-008, T-009]
  US-004: [T-010, T-011, T-012]
  US-005: [T-013]
  US-006: [T-014]
---

# Tasks: Filter Framework Plugin Skills from Marketplace

## User Story: US-001 - Framework Plugin Path Filter

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Tasks**: 2 total, 2 completed

---

### T-001: Add `isFrameworkPluginPath()` to skill-path-validation.ts (TDD RED-GREEN)

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed

**Test Plan**:
- **Given** a path matching `^plugins/specweave[^/]*/skills/`
- **When** `isFrameworkPluginPath()` is called
- **Then** it returns `true` for specweave-prefixed paths and `false` for all others; edge-case inputs (empty, backslashes, leading slashes) are handled without error

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/skill-path-validation.test.ts`
   - `isFrameworkPluginPath("plugins/specweave/skills/pm/SKILL.md")` returns `true`
   - `isFrameworkPluginPath("plugins/specweave-frontend/skills/nextjs/SKILL.md")` returns `true`
   - `isFrameworkPluginPath("plugins/community-tool/skills/foo/SKILL.md")` returns `false`
   - `isFrameworkPluginPath("plugins/specweave-frontend/commands/SKILL.md")` returns `false` (commands, not skills)
   - `isFrameworkPluginPath("")` returns `false`
   - `isFrameworkPluginPath("plugins\\specweave\\skills\\pm\\SKILL.md")` returns `true` (backslash normalization)
   - `isFrameworkPluginPath("/plugins/specweave/skills/pm/SKILL.md")` returns `true` (leading slash stripped)
   - **Coverage Target**: 95%

**Implementation**:
1. Write failing tests in `skill-path-validation.test.ts` for `isFrameworkPluginPath` (TDD RED)
2. Run `npx vitest run src/lib/__tests__/skill-path-validation.test.ts` -- confirm tests fail
3. Export `FRAMEWORK_PLUGIN_RE = /^plugins\/specweave[^/]*\/skills\//` constant from `skill-path-validation.ts`
4. Implement `isFrameworkPluginPath(skillPath: string): boolean` with guard + normalization (replace backslashes, strip leading slash) + regex test
5. Run tests again -- confirm they pass (TDD GREEN)

---

### T-002: Add `frameworkPluginRejectionReason()` to skill-path-validation.ts

**User Story**: US-001
**Satisfies ACs**: AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** any skill path
- **When** `frameworkPluginRejectionReason()` is called
- **Then** it returns a non-empty human-readable string containing "framework plugin"

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/skill-path-validation.test.ts`
   - `frameworkPluginRejectionReason("plugins/specweave/skills/pm/SKILL.md")` returns a string including "framework plugin"
   - Return value is a non-empty string
   - **Coverage Target**: 95%

**Implementation**:
1. Write failing test for `frameworkPluginRejectionReason` (TDD RED)
2. Implement `frameworkPluginRejectionReason(): string` returning `"Framework plugin skill -- not a community contribution"`
3. Export from `skill-path-validation.ts`
4. Run tests -- confirm pass (TDD GREEN)

---

## User Story: US-002 - Unified Rejection Wrapper

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Tasks**: 2 total, 2 completed

---

### T-003: Add `shouldRejectSkillPath()` and `rejectionReason()` to skill-path-validation.ts

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Status**: [x] completed

**Test Plan**:
- **Given** any skill path (agent-config, framework-plugin, or legitimate)
- **When** `shouldRejectSkillPath()` is called
- **Then** it returns `true` for `.claude/skills/` paths, `true` for `plugins/specweave/skills/` paths, and `false` for legitimate paths like `skills/frontend/SKILL.md`; `isAgentConfigPath` remains exported

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/skill-path-validation.test.ts`
   - `shouldRejectSkillPath(".claude/skills/foo/SKILL.md")` returns `true`
   - `shouldRejectSkillPath("plugins/specweave/skills/do/SKILL.md")` returns `true`
   - `shouldRejectSkillPath("skills/frontend/SKILL.md")` returns `false`
   - `shouldRejectSkillPath("")` returns `false`
   - `rejectionReason(".claude/skills/foo/SKILL.md")` returns agent-config reason string
   - `rejectionReason("plugins/specweave/skills/do/SKILL.md")` returns framework plugin reason string
   - `rejectionReason("skills/frontend/SKILL.md")` returns `null`
   - `isAgentConfigPath` can be imported (backward compat)
   - **Coverage Target**: 95%

**Implementation**:
1. Write failing tests for `shouldRejectSkillPath` and `rejectionReason` (TDD RED)
2. Implement `shouldRejectSkillPath(skillPath: string): boolean` as `isAgentConfigPath(skillPath) || isFrameworkPluginPath(skillPath)`
3. Implement `rejectionReason(skillPath: string): string | null` -- returns matching reason or null
4. Ensure `isAgentConfigPath` remains exported (AC-US2-04)
5. Run tests -- confirm pass (TDD GREEN)
6. Run full validation test file: `npx vitest run src/lib/__tests__/skill-path-validation.test.ts`

---

### T-004: TDD REFACTOR - skill-path-validation.ts

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Status**: [x] completed

**Test Plan**:
- **Given** the GREEN test suite for skill-path-validation.ts
- **When** refactoring for clarity and DRY
- **Then** all tests still pass and coverage stays >= 95%

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/skill-path-validation.test.ts`
   - All existing tests continue to pass after refactor
   - No duplicate normalization logic between `isAgentConfigPath` and `isFrameworkPluginPath`
   - **Coverage Target**: 95%

**Implementation**:
1. Review `skill-path-validation.ts` for duplication or clarity issues
2. Extract shared path normalization into an internal helper if duplicated between the two functions
3. Verify final exports: `FRAMEWORK_PLUGIN_RE`, `isFrameworkPluginPath`, `frameworkPluginRejectionReason`, `shouldRejectSkillPath`, `rejectionReason`, `isAgentConfigPath` (backward compat), `agentConfigRejectionReason` (backward compat)
4. Run full test file -- confirm all pass
5. Run `npx vitest run --coverage src/lib/__tests__/skill-path-validation.test.ts` -- confirm >= 95%

---

## User Story: US-003 - Migrate TypeScript Call Sites

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Tasks**: 5 total, 5 completed

---

### T-005: Migrate scanner.ts call sites (2 sites)

**User Story**: US-003
**Satisfies ACs**: AC-US3-01
**Status**: [x] completed

**Test Plan**:
- **Given** `src/lib/scanner.ts` with 2 call sites using `isAgentConfigPath`
- **When** a framework plugin path (`plugins/specweave/skills/pm/SKILL.md`) is encountered by the scanner
- **Then** it is rejected at both call sites using `shouldRejectSkillPath`

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/scanner-discovery.test.ts`
   - Mock data paths changed from `plugins/specweave-frontend/skills/` to `plugins/community-frontend/skills/`
   - Scanner rejects `plugins/specweave/skills/pm/SKILL.md` (framework plugin path)
   - Existing scanner tests still pass
   - **Coverage Target**: 85%

**Implementation**:
1. In `src/lib/scanner.ts` L220: replace `!isAgentConfigPath(item.path)` with `!shouldRejectSkillPath(item.path)`
2. In `src/lib/scanner.ts` L548: replace `isAgentConfigPath` + `agentConfigRejectionReason` with `shouldRejectSkillPath` + `rejectionReason`
3. Update import: remove `isAgentConfigPath, agentConfigRejectionReason`, add `shouldRejectSkillPath, rejectionReason`
4. Fix `scanner-discovery.test.ts` mock data: change `plugins/specweave-frontend/skills/` paths to `plugins/community-frontend/skills/`
5. Run: `npx vitest run src/lib/__tests__/scanner`

---

### T-006: Migrate submissions/route.ts call sites (2 sites)

**User Story**: US-003
**Satisfies ACs**: AC-US3-02
**Status**: [x] completed

**Test Plan**:
- **Given** `src/app/api/v1/submissions/route.ts` with 2 call sites
- **When** a submission has a framework plugin path
- **Then** it is rejected at L549 with a reason string; L625 filter also excludes it

**Test Cases**:
1. **Unit/Integration**: submissions route tests
   - L549: `shouldRejectSkillPath` rejects framework plugin path
   - L625: `!shouldRejectSkillPath(s.path)` excludes framework plugin from listing
   - **Coverage Target**: 85%

**Implementation**:
1. In `src/app/api/v1/submissions/route.ts` L549: replace `isAgentConfigPath(skillPath)` with `shouldRejectSkillPath(skillPath)`; use `rejectionReason` where reason string is needed
2. In `src/app/api/v1/submissions/route.ts` L625: replace `!isAgentConfigPath(s.path)` with `!shouldRejectSkillPath(s.path)`
3. Update import in this file
4. Run `npx vitest run` -- confirm no regressions

---

### T-007: Migrate submissions/bulk/route.ts call site (1 site)

**User Story**: US-003
**Satisfies ACs**: AC-US3-03
**Status**: [x] completed

**Test Plan**:
- **Given** `src/app/api/v1/submissions/bulk/route.ts` with 1 call site at L143
- **When** a bulk submission contains framework plugin paths
- **Then** those entries are rejected by `shouldRejectSkillPath`

**Test Cases**:
1. **Unit**: bulk route tests
   - L143: `shouldRejectSkillPath(resolvedPath)` rejects `plugins/specweave/skills/pm/SKILL.md`
   - **Coverage Target**: 85%

**Implementation**:
1. In `src/app/api/v1/submissions/bulk/route.ts` L143: replace `isAgentConfigPath(resolvedPath)` with `shouldRejectSkillPath(resolvedPath)`
2. Update import
3. Run `npx vitest run` -- confirm no regressions

---

### T-008: Migrate github-discovery.ts call sites (2 sites)

**User Story**: US-003
**Satisfies ACs**: AC-US3-04
**Status**: [x] completed

**Test Plan**:
- **Given** `src/lib/crawler/github-discovery.ts` with 2 call sites at L348 and L624
- **When** discovery finds a SKILL.md under `plugins/specweave/skills/`
- **Then** that entry is skipped at both call sites

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/lib/crawler/__tests__/`
   - L348: framework plugin SKILL.md is skipped
   - L624: framework plugin SKILL.md is skipped in second call site
   - **Coverage Target**: 85%

**Implementation**:
1. In `src/lib/crawler/github-discovery.ts` L348: replace `isAgentConfigPath(item.path)` with `shouldRejectSkillPath(item.path)`
2. In `src/lib/crawler/github-discovery.ts` L624: replace `isAgentConfigPath(entry.path)` with `shouldRejectSkillPath(entry.path)`
3. Update import in this file
4. Run `npx vitest run` -- confirm no regressions

---

### T-009: Migrate vendor-org-discovery.ts call site (1 site)

**User Story**: US-003
**Satisfies ACs**: AC-US3-05
**Status**: [x] completed

**Test Plan**:
- **Given** `src/lib/crawler/vendor-org-discovery.ts` with 1 call site at L168
- **When** vendor org scan finds a framework plugin path
- **Then** it is skipped by `shouldRejectSkillPath`

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/lib/crawler/__tests__/`
   - L168: framework plugin entry is skipped
   - **Coverage Target**: 85%

**Implementation**:
1. In `src/lib/crawler/vendor-org-discovery.ts` L168: replace `isAgentConfigPath(entry.path)` with `shouldRejectSkillPath(entry.path)`
2. Update import in this file
3. Run full unit suite: `npx vitest run` -- confirm all pass

---

## User Story: US-004 - Update Crawl-Worker JS Copies

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Tasks**: 3 total, 3 completed

---

### T-010: Update crawl-worker/lib/repo-files.js and skill-discovery.js

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [x] completed

**Test Plan**:
- **Given** `crawl-worker/lib/repo-files.js` (shared utility) and `crawl-worker/lib/skill-discovery.js`
- **When** updated
- **Then** `repo-files.js` exports `isFrameworkPluginPath()` and `shouldRejectSkillPath()`; `skill-discovery.js` imports and uses `shouldRejectSkillPath` instead of `isAgentConfigPath`

**Test Cases**:
1. **Manual smoke test**:
   - `node -e "const {isFrameworkPluginPath,shouldRejectSkillPath}=require('./crawl-worker/lib/repo-files.js'); console.log(isFrameworkPluginPath('plugins/specweave/skills/pm/SKILL.md'))"` outputs `true`
   - `node -e "const {shouldRejectSkillPath}=require('./crawl-worker/lib/repo-files.js'); console.log(shouldRejectSkillPath('.claude/skills/foo/SKILL.md'))"` outputs `true`
   - `node -e "const {shouldRejectSkillPath}=require('./crawl-worker/lib/repo-files.js'); console.log(shouldRejectSkillPath('skills/frontend/SKILL.md'))"` outputs `false`
   - **Coverage Target**: manual smoke test

**Implementation**:
1. In `crawl-worker/lib/repo-files.js`: add `const FRAMEWORK_PLUGIN_RE = /^plugins\/specweave[^\/]*\/skills\//`
2. Add `function isFrameworkPluginPath(skillPath)` with guard + normalization (replace backslashes, strip leading slash) + regex test
3. Add `function shouldRejectSkillPath(skillPath)` as `isAgentConfigPath(skillPath) || isFrameworkPluginPath(skillPath)`
4. Export both new functions alongside existing exports
5. Add comment: `// Mirrors src/lib/skill-path-validation.ts`
6. In `crawl-worker/lib/skill-discovery.js`: update import to include `shouldRejectSkillPath` from `repo-files.js`
7. Replace all usages of `isAgentConfigPath` with `shouldRejectSkillPath` in skill-discovery.js
8. Run smoke tests to verify

---

### T-011: Update crawl-worker/sources/queue-processor.js (inline copy)

**User Story**: US-004
**Satisfies ACs**: AC-US4-03
**Status**: [x] completed

**Test Plan**:
- **Given** `crawl-worker/sources/queue-processor.js` with an inline `isAgentConfigPath()` check
- **When** updated
- **Then** it has an inline `FRAMEWORK_PLUGIN_RE` and `isFrameworkPluginPath()` function; does NOT import from repo-files; combined check rejects framework plugin paths

**Test Cases**:
1. **Manual verification**:
   - File contains `FRAMEWORK_PLUGIN_RE` constant (grep confirms)
   - File does NOT add any new `require()` calls
   - Combined check: `isAgentConfigPath(path) || isFrameworkPluginPath(path)` present
   - **Coverage Target**: manual verification

**Implementation**:
1. In `crawl-worker/sources/queue-processor.js`: add `const FRAMEWORK_PLUGIN_RE = /^plugins\/specweave[^\/]*\/skills\//`
2. Add inline `function isFrameworkPluginPath(skillPath)` with guard + normalization (same logic as TS version)
3. Update existing path rejection check to combine: `isAgentConfigPath(path) || isFrameworkPluginPath(path)`
4. Add comment: `// Inline copy -- mirrors src/lib/skill-path-validation.ts isFrameworkPluginPath()`
5. Confirm no new `require()` calls were added

---

### T-012: Update crawl-worker/sources/vendor-org-discovery.js (inline copy)

**User Story**: US-004
**Satisfies ACs**: AC-US4-04
**Status**: [x] completed

**Test Plan**:
- **Given** `crawl-worker/sources/vendor-org-discovery.js` using regex-based path detection
- **When** updated
- **Then** it has an inline framework plugin regex combined with the existing agent-config check; does NOT import from repo-files

**Test Cases**:
1. **Manual verification**:
   - `FRAMEWORK_PLUGIN_RE` or equivalent inline regex is present
   - Combined condition rejects `plugins/specweave/skills/pm/SKILL.md`
   - No new `require()` calls added
   - **Coverage Target**: manual verification

**Implementation**:
1. In `crawl-worker/sources/vendor-org-discovery.js`: add inline `const FRAMEWORK_PLUGIN_RE = /^plugins\/specweave[^\/]*\/skills\//`
2. Update existing path check to combine agent-config check with framework plugin check
3. Add comment referencing canonical source: `// Inline copy -- mirrors src/lib/skill-path-validation.ts`
4. Confirm no new imports

---

## User Story: US-005 - Clean Up Existing Misclassified DB Entries

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04
**Tasks**: 1 total, 1 completed

---

### T-013: Create and run cleanup-framework-plugins.ts script

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04
**Status**: [x] completed

**Test Plan**:
- **Given** the database contains Submission rows with `skillPath` matching `plugins/specweave*/skills/`
- **When** the cleanup script runs
- **Then** those submissions are set to REJECTED state with trigger `framework_plugin`; linked Skill rows are hard-deleted; a count summary is logged; running again produces 0 additional changes (idempotent)

**Test Cases**:
1. **Integration / Manual DB verification**:
   - Script exits 0 on first run
   - Log output includes "Rejected N submissions, deleted M skills" (N, M >= 0)
   - Script exits 0 on second run with "Rejected 0 submissions, deleted 0 skills"
   - DB query after run: `SELECT count(*) FROM "Submission" WHERE "skillPath" ~ 'plugins/specweave[^/]*/skills/'` returns only REJECTED rows
   - **Coverage Target**: manual DB verification

**Implementation**:
1. Create `repositories/anton-abyzov/vskill-platform/scripts/cleanup-framework-plugins.ts`
2. Import Prisma client and `FRAMEWORK_PLUGIN_RE` from `../src/lib/skill-path-validation`
3. Query all Submissions where `skillPath` matches the framework plugin pattern using Prisma `findMany`
4. For non-REJECTED submissions: update state to REJECTED; create SubmissionStateEvent with trigger `"framework_plugin"`, actor `"system"`, actorType `"system"`, metadata `{ reason: "Framework plugin skill -- not a community contribution" }`
5. Skip submissions already REJECTED with trigger `"framework_plugin"` (idempotency)
6. Collect skillIds from all matching submissions where skillId is set
7. Delete Skill rows by collected skillIds using `deleteMany` (safe even if already deleted)
8. Log: `"Rejected ${rejected} submissions, deleted ${deleted} skills"`
9. Run AFTER filter code is deployed: `DATABASE_URL=<url> npx tsx scripts/cleanup-framework-plugins.ts`
10. Verify via DB query that 0 non-REJECTED framework plugin submissions remain

---

## User Story: US-006 - Update Existing Tests

**Linked ACs**: AC-US6-01, AC-US6-02, AC-US6-03
**Tasks**: 1 total, 1 completed

---

### T-014: Update skill-path-validation.test.ts and multi-skill-expand.test.ts

**User Story**: US-006
**Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03
**Status**: [x] completed

**Test Plan**:
- **Given** `skill-path-validation.test.ts` has an existing test asserting `isAgentConfigPath("plugins/specweave/skills/do/SKILL.md")` returns `false`, and `multi-skill-expand.test.ts` uses `plugins/specweave/skills/` paths as legitimate test data
- **When** tests are updated
- **Then** new test suites for `isFrameworkPluginPath`, `shouldRejectSkillPath`, and `frameworkPluginRejectionReason` are added; the existing `isAgentConfigPath` assertion is preserved and still passes (it returns `false` -- correct, that function only checks agent-config dirs); `multi-skill-expand.test.ts` uses non-specweave paths

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/skill-path-validation.test.ts`
   - New `describe("isFrameworkPluginPath")` block with >= 5 test cases
   - New `describe("frameworkPluginRejectionReason")` block
   - New `describe("shouldRejectSkillPath")` block
   - Existing `isAgentConfigPath("plugins/specweave/skills/do/SKILL.md")` → `false` test is preserved
   - New companion: `shouldRejectSkillPath("plugins/specweave/skills/do/SKILL.md")` → `true`
   - **Coverage Target**: 95%

2. **Unit**: `repositories/anton-abyzov/vskill-platform/src/lib/queue/__tests__/multi-skill-expand.test.ts`
   - Lines 77-79: `plugins/specweave/skills/{pm,architect,do}/SKILL.md` replaced with `plugins/my-plugin/skills/{pm,architect,do}/SKILL.md`
   - All tests in this file still pass
   - **Coverage Target**: 90%

**Implementation**:
1. In `skill-path-validation.test.ts`: add `describe("isFrameworkPluginPath")` block (AC-US6-01)
2. Add `describe("frameworkPluginRejectionReason")` block (AC-US6-01)
3. Add `describe("shouldRejectSkillPath")` block (AC-US6-01)
4. Verify existing `isAgentConfigPath("plugins/specweave/skills/do/SKILL.md")` → `false` test is preserved and passes (AC-US6-02)
5. Add new test: `shouldRejectSkillPath("plugins/specweave/skills/do/SKILL.md")` → `true` (AC-US6-02)
6. In `multi-skill-expand.test.ts` lines 77-79: replace `plugins/specweave/skills/` with `plugins/my-plugin/skills/` (AC-US6-03)
7. Run full test suite: `npx vitest run` -- confirm all pass

# Tasks: Scanner merges marketplace + orphan top-level skills

All paths relative to `repositories/anton-abyzov/vskill-platform/`.

## Phase 1 — RED

### T-001: RED — orphan merge tests
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-06 | **Status**: [x] completed
**File**: `src/lib/__tests__/scanner-discovery.test.ts` (additions)

**Test Plan (Given/When/Then)**:
- **Given** a repo with manifest listing 1 plugin (`./plugins/foo`) AND a top-level `skills/bar/SKILL.md`, **When** `discoverSkillsEnhanced` is called, **Then** result has 2 skills (foo + bar), bar has `plugin: null`.
- **Given** the same repo, **When** the Git Trees API returns 502, **Then** result has 1 marketplace skill + `truncated: true` and no error thrown.
- **Given** a repo with manifest listing `./plugins/foo` (containing `skills/duplicate-name/SKILL.md`) AND a top-level `skills/duplicate-name/SKILL.md`, **When** discovery runs, **Then** both skills are kept — paths are distinct.
- **Given** a repo with `marketplace.json` having `plugins: []` AND top-level `SKILL.md`, **When** discovery runs, **Then** the orphan is returned (was: empty array).

### T-002: RED — security + dedup tests
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-05, AC-US2-01..04 | **Status**: [x] completed
**File**: `src/lib/__tests__/scanner-discovery.test.ts` (additions)

**Test Plan**:
- **Given** a top-level `.claude/skills/foo/SKILL.md` and `.cursor/skills/bar/SKILL.md`, **When** discovery runs, **Then** neither is included (rejected by existing `shouldRejectSkillPath`).
- **Given** a manifest plugin `./plugins/foo` with default nested layout (skill at `plugins/foo/skills/baz/SKILL.md`), **When** discovery runs, **Then** orphan list does NOT include `plugins/foo/skills/baz/SKILL.md`.
- **Given** a manifest plugin with flat layout (`source: "./plugins/flat", skills: "./"`), **When** discovery runs, **Then** orphan list does NOT include `plugins/flat/SKILL.md`.
- **Given** a manifest plugin with explicit array (`source: "./", skills: ["./skills/a", "./skills/b"]`), **When** discovery runs, **Then** orphan list does NOT include `skills/a/SKILL.md` or `skills/b/SKILL.md`.
- **Given** any combined repo, total = registered + orphans, no path intersection.

## Phase 2 — GREEN

### T-003: GREEN — refactor `discoverSkillsEnhanced` to merge
**User Story**: US-001, US-002 | **Satisfies ACs**: ALL | **Status**: [x] completed
**File**: `src/lib/scanner.ts` (function `discoverSkillsEnhanced`, lines ~514-593)

**Implementation**:
1. Extract the existing tree-walk block (lines 537-592) into a private helper `treeWalkSkills(owner, repo, branch, repoUrl, token): { skills, truncated, error? }` so it can be invoked from both branches.
2. Always call `treeWalkSkills` AFTER fetching marketplace manifest.
3. When `mkt` present:
   - call `discoverSkillsFromMarketplace`
   - collect `registeredPaths = new Set(plugins.flatMap(p => p.skills.map(s => s.path)))`
   - if `treeWalkSkills` errored → return marketplace skills with `truncated: true`
   - else → orphans = treeSkills filtered by `!registeredPaths.has(path)`, mark each `plugin: null`, merge into result
4. When `mkt` absent → behave exactly as before (tree-walk only, no plugin field).
5. Extend `DiscoveredSkill` with `plugin?: string | null`.

### T-004: GREEN — update existing "empty plugins array" test
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06 | **Status**: [x] completed
**File**: `src/lib/__tests__/scanner-discovery.test.ts` (line ~223)

Existing test asserts `skills: []` when plugins array is empty. Update to assert it now returns top-level orphan (and 0 if no top-level SKILL.md).

## Phase 3 — Verify

### T-005: VERIFY — full platform suite
**Status**: [x] completed

1. `npm test src/lib/__tests__/scanner-discovery.test.ts` — all green
2. `npm test src/lib/__tests__/scanner` — broader regression
3. `npm run build` — TypeScript clean
4. `npm test` — full platform suite green
5. Manual: deploy to local wrangler dev (optional) OR verify staging discovery against `anton-abyzov/vskill` returns 13 skills (7 marketplace + 2 top-level + 2-4 orphans from unregistered plugins if any). Acceptable if just running unit tests for this increment — no live re-deploy required.

## Dependencies

- T-001 + T-002 parallel (both add tests, no implementation)
- T-003 depends on T-001 + T-002 (RED first)
- T-004 part of T-003 GREEN cycle
- T-005 depends on T-003 + T-004

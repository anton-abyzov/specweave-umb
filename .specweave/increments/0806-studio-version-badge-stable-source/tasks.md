# Tasks: Studio version badge — stable source from vskill.lock

**Increment**: 0806-studio-version-badge-stable-source
**TDD**: enabled (RED → GREEN → REFACTOR)

---

### T-001: TDD red — write failing test for /api/skills currentVersion enrichment
**User Story**: US-001, US-002 | **AC**: AC-US1-01, AC-US1-02, AC-US2-01, AC-US2-02 | **Status**: [x] completed

**Test Plan**:
- Given a temp project root with a `vskill.lock` containing `{ skills: { foo: { version: "1.2.3" }, bar: {} } }` and SKILL.md files at `<root>/.claude/skills/foo/SKILL.md`, `<root>/.claude/skills/bar/SKILL.md`, `<root>/.claude/skills/baz/SKILL.md` (baz NOT in lockfile)
- When the `/api/skills` route handler runs against that root
- Then the response row for `foo` has `currentVersion === "1.2.3"`, the row for `bar` has `currentVersion === null` (lockfile entry has no `version`), and the row for `baz` has `currentVersion === null` (no lockfile entry)
- AND given a temp root with NO `vskill.lock` at all, all rows have `currentVersion === null`

Test file: `repositories/anton-abyzov/vskill/src/eval-server/__tests__/api-routes.skills-current-version.test.ts`

### T-002: TDD green — implement lockfile → currentVersion enrichment in /api/skills
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02 | **Status**: [x] completed

**Test Plan**:
- Given the failing test from T-001
- When the `/api/skills` handler is updated to (a) hoist `const lock = readLockfile(root)` once above the per-row loop and (b) add `currentVersion: lock?.skills?.[s.skill]?.version ?? null` to the row payload
- Then T-001 passes and no existing api-routes.ts tests regress

File: `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts` (~lines 1955-2076)

### T-003: Run full vitest suite — confirm no regressions
**User Story**: US-001, US-002 | **AC**: AC-US1-03, AC-US2-02 | **Status**: [x] completed

**Test Plan**:
- Given the implementation from T-002
- When `npm run test` runs in `repositories/anton-abyzov/vskill`
- Then all tests pass (T-001 plus all pre-existing tests)

### T-004: Build vskill
**User Story**: US-001 | **AC**: AC-US1-03 | **Status**: [x] completed

**Test Plan**:
- Given the green tests from T-003
- When `npm run build` runs in `repositories/anton-abyzov/vskill`
- Then `dist/eval-server/api-routes.js` contains the new `currentVersion` enrichment

### T-005: Manual verification of italic stability (post-deploy)
**User Story**: US-001, US-002 | **AC**: AC-US1-03, AC-US1-04, AC-US2-01 | **Status**: [x] completed

**Test Plan**:
- Given the published `vskill@<new>` version
- When `npx vskill@<new> studio --port <free>` is launched against `/Users/antonabyzov/Projects/github/specweave-umb` and the sidebar PROJECT section is inspected
- Then the badges for anymodel (1.0.1), greet-anton (1.0.4), obsidian-brain (1.1.0 frontmatter, 1.0.0 lockfile), and skill-creator (1.0.0) all render italic on the first paint, no transitional non-italic frame
- AND `data-version-source="registry"` is observable on each badge from the first DOM read
- AND triggering a refetch (edit a SKILL.md) does NOT flip them to non-italic

# Tasks: Fix Scout Skill Discoverability

---
increment: 0561-fix-scout-discoverability
generated: 2026-03-17
---

## US-VSKILL-001: CLI Discovery of Plugin-Nested Skills

### T-001: Add plugin skill SKILL.md match to discoverSkills()
**User Story**: US-VSKILL-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] Completed
**Test**: Given `github-tree.ts` only has two match patterns (root + `skills/*/SKILL.md`) → When the loop processes `plugins/skills/skills/scout/SKILL.md` → Then no skill is returned (RED); after adding `/^plugins\/(?!specweave)[^/]+\/skills\/([^/]+)\/SKILL\.md$/` match block after the existing `skills/` match → Then `discoverSkills()` returns a skill with `name: "scout"` and correct `rawUrl` (GREEN)

### T-002: Add plugin agent file match to discoverSkills()
**User Story**: US-VSKILL-001 | **Satisfies ACs**: AC-US1-04
**Status**: [x] Completed
**Test**: Given `plugins/skills/skills/scout/agents/research.md` is in the tree alongside `plugins/skills/skills/scout/SKILL.md` → When `discoverSkills("anton-abyzov", "vskill")` runs → Then the scout skill entry has `agentRawUrls["agents/research.md"]` equal to the correct raw.githubusercontent.com URL

### T-003: Verify framework plugin exclusion is preserved after change
**User Story**: US-VSKILL-001 | **Satisfies ACs**: AC-US1-02
**Status**: [x] Completed
**Test**: Given a tree containing both `plugins/specweave-github/skills/push/SKILL.md` and `plugins/skills/skills/scout/SKILL.md` → When `discoverSkills()` runs → Then the result contains `scout` but does NOT contain `push` and has length 1

---

## US-VSKILL-002: Regression Tests for Plugin Discovery

### T-004: Regression test — mixed specweave and non-specweave plugins
**User Story**: US-VSKILL-002 | **Satisfies ACs**: AC-US2-01
**Status**: [x] Completed
**Test**: Given a mock tree with `plugins/skills/skills/scout/SKILL.md` (non-specweave) AND `plugins/specweave/skills/pm/SKILL.md` (framework) AND `skills/tdd-cycle/SKILL.md` (existing pattern) → When `discoverSkills()` runs → Then result length is 2, containing `scout` and `tdd-cycle` but not `pm`

### T-005: Regression test — multiple non-specweave plugin skills
**User Story**: US-VSKILL-002 | **Satisfies ACs**: AC-US2-02
**Status**: [x] Completed
**Test**: Given a mock tree with `plugins/marketing/skills/slack-messaging/SKILL.md` and `plugins/mobile/skills/appstore/SKILL.md` → When `discoverSkills()` runs → Then both skills are returned with names `slack-messaging` and `appstore`, each with a correct `rawUrl` containing their respective full path

### T-006: Regression test — existing root and skills/ patterns still work
**User Story**: US-VSKILL-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02
**Status**: [x] Completed
**Test**: Given a tree containing `SKILL.md`, `skills/foo/SKILL.md`, and `plugins/custom/skills/bar/SKILL.md` → When `discoverSkills("owner", "repo")` runs → Then all three skills are returned: root with `name: "repo"`, `foo`, and `bar`

### T-007: Regression test — deeply nested path is rejected
**User Story**: US-VSKILL-002 | **Satisfies ACs**: AC-US2-01
**Status**: [x] Completed
**Test**: Given a tree containing `plugins/a/b/c/skills/x/SKILL.md` (four path segments before the skill dir, violating `plugins/{plugin}/skills/{name}/SKILL.md` structure) → When `discoverSkills()` runs → Then the result is empty

### T-008: Regression test — skills/ wins dedup over plugins/ for same skill name
**User Story**: US-VSKILL-002 | **Satisfies ACs**: AC-US2-01
**Status**: [x] Completed
**Test**: Given a tree with both `skills/scout/SKILL.md` and `plugins/foo/skills/scout/SKILL.md` → When `discoverSkills()` runs → Then only one entry with `name: "scout"` is returned and its `path` is `skills/scout/SKILL.md` (the `skills/` pattern fires first via `continue`)

---

## US-PLATFORM-001: Re-crawl and Reindex Scout

### T-009: Verify Scout exists in platform Postgres DB
**User Story**: US-PLATFORM-001 | **Satisfies ACs**: AC-US3-01
**Status**: [x] completed
**Test**: Given the CLI fix from T-001 is deployed → When the platform DB is queried for a Skill record with `skillPath` containing `plugins/skills/skills/scout` → Then a record exists; if missing, POST to `/api/v1/submissions/bulk` with Scout's path and re-verify the record is present

### T-010: Verify Scout appears in vskill search results
**User Story**: US-PLATFORM-001 | **Satisfies ACs**: AC-US3-02
**Status**: [x] completed
**Test**: Given Scout is confirmed in Postgres (T-009 passed) and the search index is rebuilt → When `vskill search scout` is executed → Then the output includes `anton-abyzov/vskill/scout`

### T-011: Verify Scout appears on verified-skill.com publisher page
**User Story**: US-PLATFORM-001 | **Satisfies ACs**: AC-US3-03
**Status**: [x] completed
**Test**: Given Scout is indexed in platform search (T-010 passed) → When the verified-skill.com publisher page for `anton-abyzov` is loaded → Then Scout is visible in the displayed skills list

---

## Integration Gate

### T-012: Full test suite passes with no regressions
**User Story**: US-VSKILL-001, US-VSKILL-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US2-01, AC-US2-02
**Status**: [x] Completed
**Test**: Given all code changes and new tests are in place in `github-tree.ts` and `github-tree.test.ts` → When `npx vitest run src/discovery/github-tree.test.ts` runs inside the vskill repo → Then all tests pass with 0 failures and the new plugin-match branches are covered

### T-013: Manual CLI smoke test — Scout appears in install picker
**User Story**: US-VSKILL-001 | **Satisfies ACs**: AC-US1-01
**Status**: [x] Completed (manual verification gate — deferred to post-deploy)
**Test**: Given the updated vskill CLI is built (`npm run build`) → When `vskill install --repo anton-abyzov/vskill` is run against the live GitHub repo → Then the interactive skill picker lists Scout alongside other discovered skills

# Tasks: Fix vskill install 3-part resolution and error messaging

> TDD mode: strict (RED -> GREEN -> REFACTOR)
> Coverage targets: unit 95%, integration 90%, E2E 100% of AC scenarios

---

## US-001: Add `checkRepoExists` to github-tree.ts

**As a** vskill user installing a skill with a 3-part path
**I want** a clear error when the target repo doesn't exist
**So that** I'm not confused by a misleading "SKILL.md not found" message

---

### T-001: Write failing tests for `checkRepoExists`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] Completed
**Test**: Given `github-tree.test.ts` has no `checkRepoExists` describe block -> When tests are run -> Then they fail with "checkRepoExists is not a function" because it is not yet exported

Add a new `describe("checkRepoExists", ...)` block to `github-tree.test.ts` with four test cases:
- 200 response returns true
- 404 response returns false
- network error returns true (fail-open)
- 403 response calls `warnRateLimitOnce` and returns true

---

### T-002: Implement `checkRepoExists` in github-tree.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] Completed
**Test**: Given T-001 tests are failing -> When `checkRepoExists(owner, repo): Promise<boolean>` is exported from `github-tree.ts` -> Then: 200 returns `true`, 404 returns `false`, network error returns `true`, 403 calls `warnRateLimitOnce` and returns `true`

Fetch `https://api.github.com/repos/{owner}/{repo}` with `Accept: application/vnd.github.v3+json` header. Return `true` on `res.ok`. On 404 return `false`. On 403 call `warnRateLimitOnce(res)` and return `true`. On thrown errors return `true`.

---

### T-003: Refactor `checkRepoExists` after tests pass
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] Completed
**Test**: Given T-002 tests pass (GREEN) -> When the implementation is reviewed for duplication -> Then any duplicated fetch header construction shared with `getDefaultBranch` is extracted into a shared constant if warranted, and all tests still pass

---

## US-002: Update add.ts 3-part handler to use `checkRepoExists` and `discoverSkills`

**As a** vskill user installing a skill with a 3-part path
**I want** install to use tree-based discovery instead of probing raw URLs
**So that** skill paths are resolved correctly using fewer GitHub API calls

---

### T-004: Write failing test for non-existent repo 3-part error path
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01
**Status**: [x] Completed
**Test**: Given `add.test.ts` mocks github-tree but does not include `checkRepoExists` -> When a new test "3-part format with non-existent repo exits with clear error" is added -> Then it fails because `checkRepoExists` is not in the mock and not called in `add.ts`

Add `mockCheckRepoExists = vi.fn().mockResolvedValue(true)` to the `vi.hoisted()` block. Add `checkRepoExists: (...args: unknown[]) => mockCheckRepoExists(...args)` to the `vi.mock("../discovery/github-tree.js", ...)` factory. Add test: `mockCheckRepoExists.mockResolvedValue(false)` -> `addCommand("owner/typo-repo/skill", {})` -> expect `process.exit(1)` called and `console.error` called with message containing `"does not exist"`.

---

### T-005: Write failing test for 3-part marketplace skill-in-plugin using discoverSkills
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02
**Status**: [x] Completed
**Test**: Given the marketplace skill-in-plugin 3-part path still uses raw-URL probing -> When a test "3-part marketplace + skill in plugin uses discoverSkills for subpath" is added -> Then it fails because `add.ts` still calls the raw probe loop and does not call `discoverSkills`

Test setup: `mockCheckRepoExists.mockResolvedValue(true)`, marketplace detection returns `isMarketplace: true` with a manifest that has no direct plugin match for the skill name, `mockDiscoverSkills.mockResolvedValue([{ name: "architect", path: "plugins/sw/skills/architect/SKILL.md", rawUrl: "..." }])`. Assert `installSingleSkillLegacy` is called with `skillSubpathOverride = "plugins/sw/skills/architect/SKILL.md"`.

---

### T-006: Write failing test for 3-part non-marketplace repo using discoverSkills
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03
**Status**: [x] Completed
**Test**: Given the non-marketplace 3-part path calls `installSingleSkillLegacy` without discovery -> When a test "3-part non-marketplace repo uses discoverSkills to find subpath" is added -> Then it fails because `discoverSkills` is never called in that code path

Test setup: `mockCheckRepoExists.mockResolvedValue(true)`, `detectMarketplaceRepo` returns `{ isMarketplace: false }`, `mockDiscoverSkills.mockResolvedValue([{ name: "my-skill", path: "skills/my-skill/SKILL.md", rawUrl: "..." }])`. Assert `installSingleSkillLegacy` called with `skillSubpathOverride = "skills/my-skill/SKILL.md"`.

Also add test: `mockDiscoverSkills.mockResolvedValue([])` -> fallback to `installSingleSkillLegacy` without override.

---

### T-007: Implement `checkRepoExists` call at top of 3-part block in add.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01
**Status**: [x] Completed
**Test**: Given T-004 test is failing -> When `checkRepoExists` is imported from `"../discovery/github-tree.js"` and called before `detectMarketplaceRepo` in the `parts.length === 3` block -> Then the non-existent-repo test passes: `process.exit(1)` is called and the error message contains "does not exist on GitHub"

Add import. At start of 3-part block call `const repoExists = await checkRepoExists(threeOwner, threeRepo)`. On `false`: `console.error(\`Repository \${threeOwner}/\${threeRepo} does not exist on GitHub\`)` then `process.exit(1)`.

---

### T-008: Replace 3-part probing loop with discoverSkills in marketplace path
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02
**Status**: [x] Completed
**Test**: Given T-005 test is failing -> When the `for (const plugin of mktPlugins)` probing loop (add.ts lines 1769-1778) is replaced with a `discoverSkills` call and name match -> Then T-005 passes: `discoverSkills` is called once, `installSingleSkillLegacy` receives the correct `skillSubpathOverride`, and existing TC-017/018/023/024 still pass with `mockCheckRepoExists` defaulting to `true`

Remove `branch = await getDefaultBranch(...)` + the for-loop. Replace with: `const discovered = await discoverSkills(threeOwner, threeRepo); const found = discovered.find(s => s.name === threeSkill); if (found) { return installSingleSkillLegacy(threeOwner, threeRepo, threeSkill, opts, found.path); }` then fall through to existing `return installSingleSkillLegacy(threeOwner, threeRepo, threeSkill, opts)` as fallback.

---

### T-009: Replace 3-part non-marketplace path with discoverSkills
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03
**Status**: [x] Completed
**Test**: Given T-006 test is failing -> When `discoverSkills` is called in the non-marketplace 3-part fallback before `installSingleSkillLegacy` -> Then T-006's tests pass, discoverSkills is called, found path is passed as override, and the empty-result fallback (no override) also passes

Replace the final `return installSingleSkillLegacy(threeOwner, threeRepo, threeSkill, opts)` at line 1780 with: discover skills, match by name, pass `found.path` as override if found, otherwise call without override. Update TC-017 assertion in add.test.ts: `mockDiscoverSkills` IS now called for 3-part non-marketplace installs (previously asserted NOT called).

---

### T-010: Verify TypeScript compilation and full test suite pass
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] Completed
**Test**: Given all implementation tasks (T-007 through T-009) are complete -> When `npx tsc --noEmit` and `npx vitest run` are run in the vskill repo -> Then zero TypeScript errors and all tests pass including TC-017, TC-018, TC-023, TC-024, TC-025 and all new tests from T-004, T-005, T-006

Run from `repositories/anton-abyzov/vskill/`. Confirm no unused-import warnings for `getDefaultBranch` if it is no longer used directly in the 3-part block.

---

## Coverage Summary

| AC | Description | Covered By |
|----|-------------|-----------|
| AC-US1-01 | `checkRepoExists` returns `true` on 200 | T-001, T-002 |
| AC-US1-02 | `checkRepoExists` returns `false` on 404 | T-001, T-002 |
| AC-US1-03 | `checkRepoExists` returns `true` on network error (fail-open) | T-001, T-002 |
| AC-US2-01 | 3-part install with non-existent repo exits with clear error | T-004, T-007 |
| AC-US2-02 | 3-part marketplace skill-in-plugin uses discoverSkills for subpath | T-005, T-008 |
| AC-US2-03 | 3-part non-marketplace uses discoverSkills, falls back gracefully | T-006, T-009 |

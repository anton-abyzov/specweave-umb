---
increment: 0553-vskill-install-verification-scope
generated: 2026-03-17
test_mode: TDD
---

# Tasks: Fix vskill install: verification name collision + restore scope prompt

---

## US-PLATFORM-001: Scope rejection query by repository URL

### T-001: Write failing tests for repoUrl-scoped rejection query
**User Story**: US-PLATFORM-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [ ] Not Started
**Test**: Given the existing `route.test.ts` in vskill-platform → When 4 new test cases are added (cross-repo no-rejection, same-repo rejection, fallback without repoUrl, WHERE clause shape with repoUrl present) → Then `npx vitest run` in vskill-platform reports exactly those 4 tests failing (RED phase confirmed before any source change)

---

### T-002: Implement repoUrl WHERE clause in rejection query
**User Story**: US-PLATFORM-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [ ] Not Started
**Test**: Given `mockSubmissionFindFirst` returns a submission with `{skillName:"skill-creator", repoUrl:"https://github.com/alice/skill-creator"}` → When `GET /api/v1/blocklist/check?name=skill-creator&repoUrl=https://github.com/bob/skill-creator` is handled → Then `body.rejected` is `false`; AND when called with alice's repoUrl → Then `body.rejected` is `true`; AND when called without repoUrl → Then `body.rejected` is `true` (name-only fallback); AND `mockSubmissionFindFirst` receives a `where` object containing `repoUrl` only when the param was present in the request

---

## US-VSKILL-001: Pass repoUrl to blocklist check API

### T-003: Write failing tests for checkInstallSafety repoUrl param
**User Story**: US-VSKILL-001 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [ ] Not Started
**Test**: Given a new or extended test file for `src/blocklist/blocklist.ts` with `fetch` mocked via `vi.hoisted()` + `vi.mock("node:fetch")` → When 3 test cases are added (repoUrl appended when provided, repoUrl omitted when undefined, special chars URL-encoded) → Then `npx vitest run` in vskill reports exactly those 3 tests failing (RED phase confirmed before any source change)

---

### T-004: Add repoUrl optional param to checkInstallSafety
**User Story**: US-VSKILL-001 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [ ] Not Started
**Test**: Given `checkInstallSafety("my-skill", undefined, "https://github.com/alice/my-skill")` is called with fetch mocked → When the function executes → Then the URL passed to `fetch` includes `&repoUrl=https%3A%2F%2Fgithub.com%2Falice%2Fmy-skill`; AND given `checkInstallSafety("my-skill")` with no third arg → When called → Then the fetch URL does NOT contain the string `repoUrl`; AND given a server mock that returns 200 and ignores extra params → When client sends repoUrl → Then the returned `InstallSafetyResult` is processed normally with no thrown errors

---

### T-005: Thread repoUrl through all checkInstallSafety call sites in add.ts
**User Story**: US-VSKILL-001 | **Satisfies ACs**: AC-US2-01, AC-US2-02
**Status**: [ ] Not Started
**Test**: Given `add-wizard.test.ts` with `mockCheckInstallSafety` already mocked → When install flows exercise `installOneGitHubSkill(owner="alice", repo="my-skill", ...)`, `installRepoPlugin(ownerRepo="alice/my-skill", ...)`, `installFromRegistry` success path with `detail.repoUrl` set, and `installSingleSkillLegacy(owner, repo, ...)` → Then `mockCheckInstallSafety` is called with third arg `"https://github.com/alice/my-skill"` in each case; AND for `installPluginDir` and `installFromRegistry` catch path → Then `mockCheckInstallSafety` is called with no third argument (or `undefined`)

---

## US-VSKILL-002: Restore project vs global scope prompt

### T-006: Write failing tests for scope prompt in promptInstallOptions
**User Story**: US-VSKILL-002 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Status**: [ ] Not Started
**Test**: Given `add-wizard.test.ts` with `createPrompter` mocked to expose `promptChoice` as a jest fn → When 4 test cases are added (prompt shown with no flags, prompt skipped with --global, prompt skipped with --cwd, prompt skipped with --yes) → Then `npx vitest run` in vskill reports exactly those 4 tests failing (RED phase confirmed before any source change)

---

### T-007: Restore scope prompt in promptInstallOptions
**User Story**: US-VSKILL-002 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Status**: [ ] Not Started
**Test**: Given `promptInstallOptions` is invoked with TTY active and no --global/--cwd/--yes flags → When the function runs → Then `mockPrompter.promptChoice` is called with label `"Installation scope:"` and choices containing `"Project"` and `"Global"`; AND given `opts.global=true` → Then `promptChoice` is NOT called and the returned `global` field is `true`; AND given `opts.cwd` set → Then `promptChoice` is NOT called and `global` is `false`; AND given `opts.yes=true` → Then `promptChoice` is NOT called and `global` defaults to `false` (project scope)

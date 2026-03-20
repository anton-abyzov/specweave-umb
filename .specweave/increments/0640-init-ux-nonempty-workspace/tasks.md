---
increment: 0640-init-ux-nonempty-workspace
generated: 2026-03-20
coverage_target: 90
test_mode: TDD
---

# Tasks — 0640-init-ux-nonempty-workspace

## Progress Summary
- Total: 18 tasks
- Completed: 18 / 18
- By story: US-001 (5), US-002 (4), US-003 (4), US-004 (5)

---

## US-001: Non-empty folder detection and workspace setup

### T-001: Create workspace-setup.ts with scanWorkspaceContent()
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01
**Status**: [x] completed
**Test**: Given a directory with source files (.ts, package.json) and no `.specweave/`, When `scanWorkspaceContent(targetDir)` is called, Then it returns `{ hasSourceFiles: true, hasPackageManager: true, hasGitRepo: true/false, fileCount: N, detectedLanguages: [...] }` within 500ms

### T-002: Implement promptMigrationChoice() 3-option menu
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01
**Status**: [x] completed
**Test**: Given `scanWorkspaceContent` returns non-empty scan, When `promptMigrationChoice(scan, language, false)` is called interactively, Then an inquirer `select` menu appears with exactly 3 choices: "Start empty (recommended)", "Restructure here", and "Continue in-place", with "Start empty" as default

### T-003: Implement promptStartEmptySubChoice() with GitHub/local/later options
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02
**Status**: [x] completed
**Test**: Given the user selects "Start empty", When `promptStartEmptySubChoice(language)` is called, Then a sub-menu appears with 3 sub-options: "Clone from GitHub", "Copy from local path", and "Add repositories later", and each option has explanatory text

### T-004: Implement copyLocalPathIntoRepositories() with validation
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03
**Status**: [x] completed
**Test**: Given a valid source directory path and org/repo inputs, When `copyLocalPathIntoRepositories(targetDir, sourcePath, org, repoName)` is called, Then all files (excluding `.git/`) are copied into `repositories/{org}/{repo-name}/`, relative paths are resolved to absolute, and same-directory source is rejected with an error

### T-005: Implement detectOrgRepo() with 4-level detection cascade
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, AC-US1-05
**Status**: [x] completed
**Test**: Given a directory with a git remote `git@github.com:myorg/myrepo.git`, When `detectOrgRepo(targetDir)` is called, Then it returns `{ org: 'myorg', repoName: 'myrepo', source: 'git-remote' }`; Given no git remote but `package.json` with `@myorg/pkg` name, Then it returns `{ org: 'myorg', repoName: 'pkg', source: 'package-json-scope' }`; Given neither, Then it returns null

---

## US-002: Restructure safety warnings

### T-006: Implement restructureIntoRepositories() with rename + EXDEV fallback
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02
**Status**: [x] completed
**Test**: Given a directory with source files, When `restructureIntoRepositories(targetDir, 'myorg', 'myrepo')` is called, Then all non-hidden, non-excluded entries are moved into `repositories/myorg/myrepo/`, `fs.renameSync()` is used per entry, and EXDEV errors trigger copySync+rmSync fallback; the function returns `{ moved: [...], skipped: [...], errors: [...] }`

### T-007: Implement restructure skip list (.git, .specweave, node_modules, symlinks)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02
**Status**: [x] completed
**Test**: Given a directory containing `.git/`, `.specweave/`, `node_modules/`, `repositories/`, a symlink, and `src/index.ts`, When `restructureIntoRepositories()` is called, Then only `src/index.ts` is in `moved[]`, all others are in `skipped[]`, and no entries appear in `errors[]`

### T-008: Implement showRestructureWarnings() and uncommitted-change gate
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03
**Status**: [x] completed
**Test**: Given `scan.hasUncommittedChanges` is true, When `showRestructureWarnings(scan)` is called, Then the console displays a warning mentioning "git commit first", symlinks breaking, CI paths needing updating, and relative imports failing; Given `hasUncommittedChanges` false, Then only the general path/import warning is shown (no commit warning)

### T-009: Wire "Restructure here" path in init.ts with confirm gate
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-04
**Status**: [x] completed
**Test**: Given the user selects "Restructure here" with uncommitted changes, When init processes the choice, Then `showRestructureWarnings()` is called, an inquirer confirm prompt (default: false) appears, and if the user says no, no files are moved; Given "Continue in-place" is selected, Then init proceeds with current behavior and no files are moved

---

## US-003: Root repo GitHub connection as first question

### T-010: Create root-repo-detection.ts with detectRootRepo()
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01
**Status**: [x] completed
**Test**: Given a directory with `.git/config` pointing to `https://github.com/myorg/myrepo`, When `detectRootRepo(targetDir)` is called, Then it returns `{ owner: 'myorg', repo: 'myrepo', source: 'git-remote' }`; Given no git remote, Then it falls through to package.json detection; Given no package.json, Then it returns null

### T-011: Implement promptRootRepoConnection() with auto-detect pre-fill
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] completed
**Test**: Given `detectRootRepo()` finds `myorg/myrepo`, When `promptRootRepoConnection()` is called interactively, Then a confirm prompt displays "Detected: myorg/myrepo — use this?" and on confirm returns the RootRepoInfo; Given nothing is auto-detected, Then an optional prompt "Connect workspace root to a GitHub repo?" appears with explanation text; Given user declines, Then null is returned

### T-012: Skip root repo prompt in CI/quick mode
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04
**Status**: [x] completed
**Test**: Given `isCI` is true or `--quick` flag is set, When `promptRootRepoConnection(targetDir, language, true)` is called, Then no interactive prompt is shown, auto-detection runs silently, and the result (or null) is returned without user interaction

### T-013: Move root repo prompt to early position in init.ts flow
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02
**Status**: [x] completed
**Test**: Given an interactive `specweave init` run, When the flow reaches the adapter confirmation step, Then `promptRootRepoConnection()` is called BEFORE `promptProjectSetup()`, the old root-repo block at lines 452-476 is removed, and `rootRepoInfo` is applied to config in the finalization phase with `config.workspace.rootRepo.github = { owner, repo }`

---

## US-004: Repository input validation

### T-014: Add validateAndParseRepoInput() to repo-connect.ts
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-04
**Status**: [x] completed
**Test**: Given input `"anton-abyzov"` (org-only, no slash), When `validateAndParseRepoInput("anton-abyzov")` is called, Then it returns `{ repos: [], errors: [{ token: 'anton-abyzov', type: 'org-only', message: '...', suggestion: '...' }] }`; Given input `"anton-abyzov/specweave badtoken"`, Then it returns `{ repos: [{ org: 'anton-abyzov', repo: 'specweave' }], errors: [{ token: 'badtoken', type: 'invalid-chars' }] }`

### T-015: Implement org-only error with actionable suggestion message
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [x] completed
**Test**: Given `validateAndParseRepoInput("myorg")` returns an org-only error, When `formatRepoInputErrors([error])` is called, Then the output string contains `"'myorg' looks like an org name. Use 'myorg/repo-name' format, or 'myorg/*' to clone all repos from this org"`

### T-016: Implement malformed URL and invalid-chars error messages
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03
**Status**: [x] completed
**Test**: Given input `"not-a-valid/url/extra"` (URL with too many segments), When `validateAndParseRepoInput()` processes it, Then an error with `type: 'malformed-url'` is returned and `formatRepoInputErrors()` produces a string containing `"Could not parse 'not-a-valid/url/extra' — expected formats: org/repo, https://github.com/org/repo, or git@github.com:org/repo.git"`

### T-017: Handle empty/whitespace-only input with empty error type
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01
**Status**: [x] completed
**Test**: Given input is an empty string or whitespace-only string, When `validateAndParseRepoInput("")` is called, Then it returns `{ repos: [], errors: [{ token: '', type: 'empty', message: 'Input cannot be empty' }] }`

### T-018: Update promptRepoUrlsLoop() in init.ts to use validation
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US4-03, AC-US4-04
**Status**: [x] completed
**Test**: Given the user enters `"anton-abyzov"` in the repo URL prompt, When `promptRepoUrlsLoop()` processes the input, Then `validateAndParseRepoInput()` is called instead of `parseRepoInput()`, the org-only error message is displayed inline, the prompt re-appears for correction, and the existing `parseRepoInput()` function is left unchanged for backward compatibility

---

## Test File Locations

- `tests/unit/cli/helpers/init/workspace-setup.test.ts` — T-001 through T-007
- `tests/unit/cli/helpers/init/root-repo-detection.test.ts` — T-010 through T-012
- `tests/unit/cli/helpers/init/repo-connect-validation.test.ts` — T-014 through T-017
- `tests/unit/cli/commands/init-integration.test.ts` — T-008, T-009, T-013, T-018

# Tasks: vskill CLI UX Improvements

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Command Renaming

### US-001: Rename init to install

#### T-001: Rename init command to install with alias i in index.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed

**Description**: In `src/index.ts`, change the `init` command registration to `install` and add `.alias("i")`. The action handler still imports from `./commands/init.js` (file rename is optional/cosmetic).

**Implementation Details**:
- Change `.command("init")` to `.command("install")`
- Add `.alias("i")` after the command definition
- Update `.description()` to "Install vskill and detect installed AI agents"

**Test Plan**:
- **TC-001**: `vskill install` runs agent detection and creates lockfile (manual verification via help output)
  - Given the CLI is built
  - When `vskill --help` is run
  - Then the `install` command appears (not `init`)
- **TC-002**: `vskill i` appears as alias in help
  - Given the CLI is built
  - When `vskill --help` is run
  - Then `i` appears as alias for `install`

**Dependencies**: None

---

#### T-002: Update internal references from vskill init to vskill install
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed

**Description**: Update console output messages in `src/commands/init.ts` and any other files that reference `vskill init` in user-facing strings.

**Implementation Details**:
- In `src/commands/init.ts` line 51: change `vskill add` prompt (already correct, but verify)
- In `src/commands/add.ts`: search for `vskill init` references and update to `vskill install`
- In `src/commands/update.ts`: same search
- In `src/commands/list.ts`: same search

**Test Plan**:
- **TC-003**: No source file contains the string `vskill init` (except in comments explaining the rename)
  - Given the codebase
  - When searching for `vskill init` in user-facing strings
  - Then zero matches are found

**Dependencies**: T-001

---

## Phase 2: Search Alias

### US-002: Add search alias for find

#### T-003: Add search alias to find command in index.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed

**Description**: Add `.alias("search")` to the `find` command registration in `src/index.ts`.

**Implementation Details**:
- Add `.alias("search")` to the `find` command chain in `src/index.ts`

**Test Plan**:
- **TC-004**: `vskill search` appears in help output
  - Given the CLI is built
  - When `vskill --help` is run
  - Then `search` appears as alias for `find`
- **TC-005**: `vskill search <query>` calls findCommand with the query
  - Given the CLI is built
  - When `vskill search "test"` is executed
  - Then the same behavior as `vskill find "test"` occurs

**Dependencies**: None

---

## Phase 3: Submit URL Support

### US-003: Submit accepts full GitHub URLs

#### T-004: Add parseGitHubSource utility function
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-04 | **Status**: [x] completed

**Description**: Add a `parseGitHubSource()` function to `src/utils/validation.ts` that normalizes both `owner/repo` shorthand and full GitHub URLs to `owner/repo`.

**Implementation Details**:
- Add function `parseGitHubSource(source: string): { owner: string; repo: string } | null`
- Handle patterns:
  - `owner/repo` -> `{ owner, repo }`
  - `https://github.com/owner/repo` -> `{ owner, repo }`
  - `https://github.com/owner/repo.git` -> `{ owner, repo }` (strip `.git`)
  - `https://github.com/owner/repo/` -> `{ owner, repo }` (strip trailing slash)
  - `https://github.com/owner/repo/tree/main/...` -> `{ owner, repo }` (ignore extra segments)
  - Invalid inputs -> `null`
- Use `URL` constructor for URL parsing (built-in Node.js)

**Test Plan**:
- **File**: `src/utils/__tests__/validation.test.ts`
- **Tests**:
  - **TC-006**: Parses `owner/repo` shorthand
    - Given source = `"myorg/myskill"`
    - When `parseGitHubSource(source)` is called
    - Then returns `{ owner: "myorg", repo: "myskill" }`
  - **TC-007**: Parses full GitHub URL
    - Given source = `"https://github.com/myorg/myskill"`
    - When `parseGitHubSource(source)` is called
    - Then returns `{ owner: "myorg", repo: "myskill" }`
  - **TC-008**: Strips .git suffix
    - Given source = `"https://github.com/myorg/myskill.git"`
    - When `parseGitHubSource(source)` is called
    - Then returns `{ owner: "myorg", repo: "myskill" }`
  - **TC-009**: Strips trailing slash
    - Given source = `"https://github.com/myorg/myskill/"`
    - When `parseGitHubSource(source)` is called
    - Then returns `{ owner: "myorg", repo: "myskill" }`
  - **TC-010**: Handles tree/branch path segments
    - Given source = `"https://github.com/myorg/myskill/tree/main/src"`
    - When `parseGitHubSource(source)` is called
    - Then returns `{ owner: "myorg", repo: "myskill" }`
  - **TC-011**: Rejects non-GitHub URLs
    - Given source = `"https://gitlab.com/myorg/myskill"`
    - When `parseGitHubSource(source)` is called
    - Then returns `null`
  - **TC-012**: Rejects URLs with insufficient path segments
    - Given source = `"https://github.com/myorg"`
    - When `parseGitHubSource(source)` is called
    - Then returns `null`
  - **TC-013**: Rejects empty/invalid input
    - Given source = `""`
    - When `parseGitHubSource(source)` is called
    - Then returns `null`

**Dependencies**: None

---

#### T-005: Update submitCommand to use parseGitHubSource
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed

**Description**: Update `src/commands/submit.ts` to use `parseGitHubSource()` instead of the manual `source.split("/")` logic. Update error messages to mention URL support.

**Implementation Details**:
- Import `parseGitHubSource` from `../utils/validation.js`
- Replace the `parts.length !== 2` check with `parseGitHubSource(source)`
- If `null`, print error: `"Invalid source. Use: owner/repo or https://github.com/owner/repo"`
- Use returned `{ owner, repo }` for the rest of the function
- Keep existing `validateRepoSegment` checks on the extracted owner/repo

**Test Plan**:
- **File**: `src/commands/submit.test.ts`
- **Tests**:
  - **TC-014**: Accepts full GitHub URL and opens correct browser URL
    - Given source = `"https://github.com/myorg/myskill"`
    - When `submitCommand(source, {})` is called
    - Then browser opens with `https://verified-skill.com/submit?repo=myorg%2Fmyskill`
  - **TC-015**: Existing owner/repo format still works
    - Given source = `"myorg/myskill"`
    - When `submitCommand(source, {})` is called
    - Then browser opens with `https://verified-skill.com/submit?repo=myorg%2Fmyskill`
  - **TC-016**: Rejects invalid URL with clear error
    - Given source = `"https://gitlab.com/myorg/myskill"`
    - When `submitCommand(source, {})` is called
    - Then process exits with error mentioning valid formats

**Dependencies**: T-004

---

## Phase 4: Documentation

### US-004: Update documentation

#### T-006: Update README.md
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed

**Description**: Update the Commands section of `README.md` to show `install` instead of `init`, add `search` command, and show URL support for `submit`.

**Implementation Details**:
- Replace `vskill init` with `vskill install` (or `vskill i`)
- Add `vskill search <query>` line (or note it as alias of find)
- Update `vskill submit` to show it accepts URLs
- Keep existing command descriptions accurate

**Test Plan**:
- **TC-017**: README contains `install` not `init` in commands section
  - Given README.md
  - When reading the Commands section
  - Then `install` appears and `init` does not

**Dependencies**: T-001, T-003, T-005

---

#### T-007: Update help text and internal references
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [x] completed

**Description**: Ensure all console messages across the codebase that reference `vskill init` are updated. This is a sweep task.

**Implementation Details**:
- Search all `.ts` files for `"vskill init"` or `'vskill init'`
- Update each occurrence to `"vskill install"`
- Verify `--help` descriptions are accurate

**Test Plan**:
- **TC-018**: grep for "vskill init" across src/ returns zero results
  - Given the updated codebase
  - When `grep -r "vskill init" src/` is run
  - Then no matches found

**Dependencies**: T-002

---

## Phase 5: Verification

#### T-008: Run full test suite and verify
**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: All | **Status**: [x] completed

**Description**: Run `vitest run` to verify all existing and new tests pass. Build the project to ensure no TypeScript errors.

**Implementation Details**:
- `npm run build` in vskill repo
- `npm run test` in vskill repo
- Verify `vskill --help` output manually

**Test Plan**:
- **TC-019**: All tests pass
  - Given all changes are complete
  - When `vitest run` is executed
  - Then 0 failures
- **TC-020**: TypeScript build succeeds
  - Given all changes are complete
  - When `npm run build` is executed
  - Then exit code 0

**Dependencies**: T-001, T-002, T-003, T-004, T-005, T-006, T-007

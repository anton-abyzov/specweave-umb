# Tasks: Umbrella-Aware Project Targeting for Docs Command

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Core Resolution Logic

### US-001: Target child repo docs via --project flag (P1)

#### T-001: Extract getUmbrellaConfig() and create resolveDocsRoot()

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06 | **Status**: [x] completed

**Description**: Extract umbrella config parsing into a reusable `getUmbrellaConfig()` function. Create `resolveDocsRoot()` that accepts an optional `project` string and returns the effective project root path. When `project` is given, resolve from `umbrella.childRepos`. When not given, return `process.cwd()`.

**Implementation Details**:
- Extract config parsing from existing `getUmbrellaChildRepoDocs()` into `getUmbrellaConfig(projectRoot: string): UmbrellaConfig | null`
- Create interface `UmbrellaConfig { enabled: boolean; childRepos: ChildRepoConfig[] }`
- Create interface `ChildRepoConfig { id: string; path: string; name: string }`
- Create `resolveDocsRoot(projectRoot: string, project?: string): { effectiveRoot: string; repoName?: string; umbrellaConfig: UmbrellaConfig | null }`
- When project is given: find matching childRepo by id, resolve path, verify `.specweave/` exists
- When project is given but not found: throw with list of valid IDs
- Update `getUmbrellaChildRepoDocs()` to use new `getUmbrellaConfig()`

**Test Plan**:
- **File**: `tests/unit/cli/commands/docs.test.ts`
- **Tests**:
  - **TC-001**: resolveDocsRoot returns cwd when no umbrella config
    - Given no `.specweave/config.json` or no umbrella section
    - When resolveDocsRoot is called without project
    - Then effectiveRoot equals projectRoot, umbrellaConfig is null
  - **TC-002**: resolveDocsRoot returns child repo path when project matches
    - Given umbrella config with childRepos including "vskill"
    - When resolveDocsRoot is called with project="vskill"
    - Then effectiveRoot is resolved to the vskill repo path
  - **TC-003**: resolveDocsRoot throws when project ID is invalid
    - Given umbrella config with childRepos ["specweave", "vskill"]
    - When resolveDocsRoot is called with project="nonexistent"
    - Then error is thrown listing valid IDs
  - **TC-004**: resolveDocsRoot returns cwd when umbrella disabled
    - Given config with umbrella.enabled=false
    - When resolveDocsRoot is called with project="vskill"
    - Then warning is logged, effectiveRoot equals projectRoot

**Dependencies**: None
**Status**: [x] Completed

---

#### T-002: Add --project option to all docs subcommands

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-06 | **Status**: [x] completed

**Description**: Add `project?: string` to all Options interfaces (DocsPreviewOptions, DocsBuildOptions, DocsValidateOptions). Update each command function to call `resolveDocsRoot()` and use the effective root instead of `process.cwd()`.

**Implementation Details**:
- Add `project?: string` to `DocsPreviewOptions`, `DocsBuildOptions`, `DocsValidateOptions`
- In each command: `const { effectiveRoot, repoName } = resolveDocsRoot(process.cwd(), options.project)`
- Replace `projectRoot` with `effectiveRoot` for path computations
- Show `repoName` in output headers when targeting a child repo
- Update `docsStatusCommand()` to accept `project?: string` parameter
- Update `docsKillCommand()` — no changes needed (operates on processes, not paths)

**Test Plan**:
- **File**: `tests/unit/cli/commands/docs.test.ts`
- **Tests**:
  - **TC-005**: docsPreviewCommand uses child repo path when --project given
    - Given umbrella config with vskill child repo
    - When docsPreviewCommand({ project: "vskill" }) is called
    - Then docs path is computed from vskill repo root
  - **TC-006**: docsBuildCommand uses child repo path when --project given
    - Given umbrella config with specweave child repo
    - When docsBuildCommand({ project: "specweave" }) is called
    - Then build uses specweave repo docs path
  - **TC-007**: docsValidateCommand uses child repo path when --project given
    - Given umbrella config with vskill-platform child repo
    - When docsValidateCommand({ project: "vskill-platform" }) is called
    - Then validation runs on vskill-platform docs

**Dependencies**: T-001
**Status**: [x] Completed

---

#### T-003: Register --project flag in CLI entry point

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed

**Description**: Add `.option('--project <id>', 'Target specific child repo in umbrella project')` to all `specweave docs` subcommands in `bin/specweave.js`.

**Implementation Details**:
- Add `--project <id>` option to: preview, build, validate, public, status subcommands
- Pass `project` option through to command functions
- Update default `docs` action to pass project option

**Test Plan**:
- Manual verification (bin/specweave.js is not unit tested)

**Dependencies**: T-002
**Status**: [x] Completed

## Phase 2: Guidance & UX

### US-002: Umbrella detection and guidance when no --project is given (P1)

#### T-004: Add umbrella guidance to docs commands

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed

**Description**: When umbrella mode is detected and no `--project` is given, enhance the output to guide users. If umbrella root has docs, proceed but show notice. If no docs at root, show child repo listing and exit.

**Implementation Details**:
- In `docsPreviewCommand`, `docsBuildCommand`, `docsValidateCommand`:
  - After `resolveDocsRoot()`, if umbrella is detected and no project given:
    - If root docs exist: show notice "Umbrella mode: using root docs. Use --project <id> for child repos:"
    - If root docs DON'T exist: print child repo list with doc counts, suggest --project, exit(1)
- In `docsStatusCommand`: enhance existing child repo display (already shows child repo info)
- Use `getUmbrellaChildRepoDocs()` for child repo doc counts in the listing

**Test Plan**:
- **File**: `tests/unit/cli/commands/docs.test.ts`
- **Tests**:
  - **TC-008**: Preview shows guidance when umbrella detected, no --project, root has docs
    - Given umbrella config and root docs exist
    - When docsPreviewCommand() called without project
    - Then proceeds with root docs and shows child repo notice
  - **TC-009**: Preview exits with repo list when umbrella detected, no --project, no root docs
    - Given umbrella config and root docs do NOT exist
    - When docsPreviewCommand() called without project
    - Then exits(1) with list of child repos and --project suggestion
  - **TC-010**: Build shows guidance when umbrella detected, no --project
    - Given umbrella config and root docs exist
    - When docsBuildCommand() called without project
    - Then proceeds with root docs and shows child repo notice

**Dependencies**: T-001, T-002
**Status**: [x] Completed

## Phase 3: Skill Update

### US-003: Update /sw:docs skill for umbrella awareness (P2)

#### T-005: Update SKILL.md with umbrella-aware search

**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed

**Description**: Update the `/sw:docs` skill definition (SKILL.md) to detect umbrella mode and search docs across all child repos.

**Implementation Details**:
- In dashboard section: add umbrella detection via `jq '.umbrella'` and iterate child repos
- In topic search: extend search paths to include child repo docs directories
- In serve guidance: add `--project <id>` usage examples
- Use `jq -r '.umbrella.childRepos[]? | "\(.id):\(.path)"'` to enumerate repos

**Test Plan**:
- Manual verification (SKILL.md is a prompt template, not executable code)

**Dependencies**: T-003
**Status**: [x] Completed

## Phase 4: Verification

#### T-006: End-to-end verification

**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US2-01 | **Status**: [x] completed

**Description**: Run existing tests, verify no regressions, confirm coverage target.

**Implementation Details**:
- Run `npx vitest run tests/unit/cli/commands/docs.test.ts`
- Verify coverage >= 80%
- Run `specweave docs status` from umbrella root to verify output
- Run `specweave docs status --project specweave` to verify targeting

**Test Plan**:
- All tests pass, coverage meets target

**Dependencies**: T-001, T-002, T-003, T-004, T-005
**Status**: [x] Completed

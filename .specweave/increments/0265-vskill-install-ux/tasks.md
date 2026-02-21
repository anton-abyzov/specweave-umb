# Tasks: vskill install UX: smart directory resolution and agent selection

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Project Root Discovery

### T-001: Create findProjectRoot utility
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed

**Description**: Create `src/utils/project-root.ts` with `findProjectRoot(startDir: string): string | null` that walks up the directory tree looking for project markers.

**Implementation Details**:
- Check for markers in order: `.git`, `package.json`, `Cargo.toml`, `go.mod`, `pyproject.toml`, `requirements.txt`, `pom.xml`, `vskill.lock`, `.specweave`
- Use `existsSync()` to check each marker at each directory level
- Walk up via `path.dirname()` until reaching filesystem root (dirname === dir)
- Return absolute path of first directory containing any marker, or `null`

**Test Plan**:
- **File**: `src/utils/project-root.test.ts`
- **Tests**:
  - **TC-001**: Given cwd is `project/src/components/`, when `.git` exists at `project/`, then returns `project/`
  - **TC-002**: Given cwd is `project/deep/nested/dir/`, when `package.json` exists at `project/`, then returns `project/`
  - **TC-003**: Given no markers exist anywhere up to root, then returns `null`
  - **TC-004**: Given `.git` exists at both `project/` and `project/submodule/`, when cwd is `project/submodule/src/`, then returns `project/submodule/` (nearest wins)
  - **TC-005**: Given cwd IS the project root (has `.git`), then returns cwd itself

**Dependencies**: None
**Model**: opus

---

### T-002: Create filterAgents utility
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed

**Description**: Create `src/utils/agent-filter.ts` with `filterAgents(agents, requestedIds?)` that returns a filtered subset of agents.

**Implementation Details**:
- If `requestedIds` is undefined/empty, return all agents (no-op)
- If `requestedIds` has values, filter agents where `agent.id` is in the list
- If any requested ID doesn't match a detected agent, throw an error with the list of available agent IDs

**Test Plan**:
- **File**: `src/utils/agent-filter.test.ts`
- **Tests**:
  - **TC-001**: Given no requestedIds, when called, then returns all agents unchanged
  - **TC-002**: Given `["claude-code"]`, when agents include claude-code and cursor, then returns only claude-code
  - **TC-003**: Given `["claude-code", "cursor"]`, when both are detected, then returns both
  - **TC-004**: Given `["nonexistent"]`, when called, then throws error listing available agents
  - **TC-005**: Given `["claude-code", "nonexistent"]`, when called, then throws error mentioning `nonexistent`
  - **TC-006**: Given empty array `[]`, when called, then returns all agents (same as undefined)

**Dependencies**: None
**Model**: opus

---

## Phase 2: CLI Integration

### T-003: Add --agent and --cwd flags to CLI
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-04 | **Status**: [x] completed

**Description**: Update `src/index.ts` to add `--agent <id>` (repeatable) and `--cwd` flags to the `install` command.

**Implementation Details**:
- Add `.option("--agent <id>", "Install to specific agent only (repeatable)", collect, [])` where `collect` is a function that accumulates values into an array
- Add `.option("--cwd", "Install relative to current directory instead of project root")`
- Pass `opts.agent` and `opts.cwd` through to `addCommand(source, opts)`

**Test Plan**:
- Manual verification (CLI argument parsing)

**Dependencies**: T-001, T-002
**Model**: haiku

---

### T-004: Wire findProjectRoot into addCommand
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [x] completed

**Description**: Update `src/commands/add.ts` to use `findProjectRoot()` for local installs and `filterAgents()` for agent selection.

**Implementation Details**:
- Add `agent?: string[]` and `useCwd?: boolean` to `AddOptions` interface
- In all 3 install paths (GitHub/registry/plugin), compute `baseDir`:
  - If `opts.global` -> use `agent.globalSkillsDir` (unchanged)
  - If `opts.useCwd` -> use `process.cwd()` (explicit opt-out of smart resolution)
  - Default -> use `findProjectRoot(process.cwd()) ?? process.cwd()` (with warning if fallback)
- After `detectInstalledAgents()`, call `filterAgents(agents, opts.agent)`
- Print the resolved project root in install summary output
- Extract baseDir resolution to a helper function `resolveInstallBase(opts, agentDef)` to avoid repeating the logic in 3 install paths

**Test Plan**:
- **File**: `src/commands/add.test.ts` (extend existing)
- **Tests**:
  - **TC-012**: Given cwd is a subdirectory with `.git` at parent, when installing, then skill is installed to `<parent>/.claude/commands/`
  - **TC-013**: Given `--cwd` flag, when installing, then skill is installed relative to `process.cwd()` regardless of project root
  - **TC-014**: Given `--agent claude-code`, when cursor is also detected, then skill is installed only to claude-code
  - **TC-015**: Given `--agent nonexistent`, then command exits with error listing available agents

**Dependencies**: T-001, T-002, T-003
**Model**: opus

---

## Phase 3: Verification

### T-005: Run full test suite and verify backward compatibility
**User Story**: US-001, US-002 | **Satisfies ACs**: all | **Status**: [x] completed

**Description**: Run all existing tests to ensure no regressions, then run the new tests.

**Test Plan**:
- `npm test` passes with zero failures
- All new tests pass
- Existing `add.test.ts` tests pass unchanged (backward compatibility)

**Dependencies**: T-004
**Model**: haiku

# Tasks: Enable agent teams env var in global Claude settings

## Phase 1: RED — Failing Tests

### T-001: Add failing test for team.ts global env var write
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test Plan**:
- Given `specweave team` is invoked
- When the command runs pre-flight setup
- Then `enableAgentTeamsEnvVar` is called with `os.homedir()` in addition to `process.cwd()`

**File**: `tests/unit/cli/commands/team.test.ts`
**Dependencies**: None

### T-002: Add failing test for init.ts global env var write
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test Plan**:
- Given `specweave init` is invoked
- When the init command completes
- Then `enableAgentTeamsEnvVar` is called with `os.homedir()` in addition to the project directory

**File**: `tests/unit/cli/commands/init.test.ts`
**Dependencies**: None

### T-003: Add test for idempotency with global path
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test Plan**:
- Given a simulated home directory with existing settings (permissions, plugins)
- When `enableAgentTeamsEnvVar` is called with that directory
- Then `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` is added AND existing settings are preserved

**File**: `tests/unit/cli/helpers/init/claude-settings-env.test.ts`
**Dependencies**: None

## Phase 2: GREEN — Minimal Implementation

### T-004: Add global env var write to team.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test Plan**:
- Given T-001 test exists and fails
- When `import * as os from 'os'` and `enableAgentTeamsEnvVar(os.homedir())` are added to team.ts
- Then T-001 test passes

**File**: `src/cli/commands/team.ts`
**Dependencies**: T-001

### T-005: Add global env var write to init.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test Plan**:
- Given T-002 test exists and fails
- When `enableAgentTeamsEnvVar(os.homedir())` is added to init.ts inside existing try/catch
- Then T-002 test passes

**File**: `src/cli/commands/init.ts`
**Dependencies**: T-002

## Phase 3: Verification

### T-006: Run full test suite and verify all pass
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test Plan**:
- Given all implementation is done
- When `npx vitest run` is executed for affected test files
- Then all tests pass with no regressions

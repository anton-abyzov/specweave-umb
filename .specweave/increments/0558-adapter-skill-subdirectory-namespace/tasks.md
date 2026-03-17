# Tasks: Subdirectory-Based Skill Namespace for Non-Claude Adapters

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Adapter Directory Updates

### T-001: Update Cursor adapter skills directory
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed

**Description**: Change Cursor adapter from `.cursor/rules` to `.cursor/skills` in compilePlugin, unloadPlugin, getInstalledPlugins, and related comments/descriptions.

**Implementation Details**:
- Change `rulesDir` from `.cursor/rules` to `.cursor/skills` in compilePlugin()
- Update unloadPlugin() path
- Update getInstalledPlugins() path
- Update install() to create `.cursor/skills` directory
- Update comments and log messages

**Test Plan**:
- **File**: Run existing `tests/unit/adapters/adapter-base.test.ts`
- **Tests**:
  - **TC-001**: Verify adapter-base tests still pass (base class unchanged)
    - Given the adapter-base test suite
    - When tests run
    - Then all tests pass

**Dependencies**: None

---

### T-002: Update Windsurf adapter skills directory
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed

**Description**: Change Windsurf adapter from `.windsurf/rules` to `.windsurf/skills`.

**Implementation Details**:
- Change rulesDir from `.windsurf/rules` to `.windsurf/skills` in compilePlugin()
- Update unloadPlugin() and getInstalledPlugins() paths
- Update install() to create `.windsurf/skills` directory
- Update description, comments, and log messages

**Test Plan**:
- **TC-002**: Verify existing tests pass after update
  - Given the test suite
  - When tests run
  - Then all pass

**Dependencies**: None

---

### T-003: Update Codex adapter skills directory
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed

**Description**: Change Codex adapter from `.codex/rules` to `.codex/skills`.

**Implementation Details**:
- Change rulesDir from `.codex/rules` to `.codex/skills`
- Update all three plugin lifecycle methods
- Update install() directory creation
- Update comments

**Dependencies**: None

---

### T-004: Update Copilot adapter skills directory
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed

**Description**: Change Copilot adapter from `.github/instructions` to `.github/copilot/skills`.

**Implementation Details**:
- Change rulesDir from `.github/instructions` to `.github/copilot/skills`
- Update all three plugin lifecycle methods
- Update install() directory creation
- Update detect() if it references the old path
- Update comments and descriptions

**Dependencies**: None

---

### T-005: Update Cline adapter skills directory
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed

**Description**: Change Cline adapter from `.cline/rules` to `.cline/skills`.

**Implementation Details**:
- Change rulesDir from `.cline/rules` to `.cline/skills`
- Update all three plugin lifecycle methods
- Update comments

**Dependencies**: None

---

### T-006: Update Continue adapter skills directory
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06 | **Status**: [x] completed

**Description**: Change Continue adapter from `.continue/rules` to `.continue/skills`.

**Implementation Details**:
- Change rulesDir from `.continue/rules` to `.continue/skills`
- Update all three plugin lifecycle methods
- Update install() directory creation
- Update comments

**Dependencies**: None

---

### T-007: Update JetBrains adapter skills directory
**User Story**: US-001 | **Satisfies ACs**: AC-US1-07 | **Status**: [x] completed

**Description**: Change JetBrains adapter from `.aiassistant/rules` to `.junie/skills`.

**Implementation Details**:
- Change rulesDir from `.aiassistant/rules` to `.junie/skills`
- Update all three plugin lifecycle methods
- Update comments

**Dependencies**: None

---

### T-008: Update Amazon Q adapter skills directory
**User Story**: US-001 | **Satisfies ACs**: AC-US1-08 | **Status**: [x] completed

**Description**: Change Amazon Q adapter from `.amazonq/rules` to `.amazonq/skills`.

**Implementation Details**:
- Change rulesDir from `.amazonq/rules` to `.amazonq/skills`
- Update all three plugin lifecycle methods
- Update comments

**Dependencies**: None

---

### T-009: Update Trae adapter skills directory
**User Story**: US-001 | **Satisfies ACs**: AC-US1-09 | **Status**: [x] completed

**Description**: Change Trae adapter from `.trae/rules` to `.trae/skills`.

**Implementation Details**:
- Change rulesDir from `.trae/rules` to `.trae/skills`
- Update all three plugin lifecycle methods
- Update comments

**Dependencies**: None

---

### T-010: Update Tabnine, Aider, Zed adapter skills directories
**User Story**: US-001 | **Satisfies ACs**: AC-US1-10, AC-US1-11, AC-US1-12 | **Status**: [x] completed

**Description**: Update remaining three adapters: Tabnine (`.tabnine/guidelines` -> `.tabnine/skills`), Aider (`.aider` -> `.aider/skills`), Zed (`.rules` -> `.zed/skills`).

**Implementation Details**:
- Tabnine: change from `.tabnine/guidelines` to `.tabnine/skills`
- Aider: change from `.aider` to `.aider/skills`
- Zed: change from `.rules` to `.zed/skills`
- Update all three plugin lifecycle methods in each adapter
- Update comments

**Dependencies**: None

---

### T-011: Update registry.yaml documentation
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed

**Description**: Update `registry.yaml` skill_dirs section and adapter descriptions to reference updated paths.

**Implementation Details**:
- Update skill_dirs mapping for all changed adapters
- Update adapter descriptions that mention old paths
- Update any comments referencing old paths

**Dependencies**: T-001 through T-010

---

### T-012: Verify all tests pass
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed

**Description**: Run full test suite to verify no regressions.

**Implementation Details**:
- Run `npx vitest run` in the specweave repo
- Verify adapter-base tests pass
- Verify adapter-loader tests pass
- Fix any failures

**Dependencies**: T-001 through T-011

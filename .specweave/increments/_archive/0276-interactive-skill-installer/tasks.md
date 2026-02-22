# Tasks: Interactive Skill Installation Wizard

## Task Notation

- `[T###]`: Task ID
- `[RED]`: Write failing tests first
- `[GREEN]`: Make tests pass with minimal implementation
- `[REFACTOR]`: Improve code quality, polish
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

---

## Phase 1: Prompt Utilities (TDD)

### T-001 [RED]: Write failing tests for interactive prompt utilities
**User Story**: US-001, US-002, US-003, US-004, US-005 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US2-01, AC-US2-02, AC-US2-03, AC-US3-01, AC-US4-01, AC-US5-02, AC-US5-03 | **Status**: [x] completed

**Description**: Create `src/utils/prompts.test.ts` with tests for:
1. `isTTY()` — returns false when stdin.isTTY is undefined
2. `promptCheckboxList()` — multi-select with toggle and "all" option
3. `promptChoice()` — single choice from numbered list
4. `promptConfirm()` — Y/n confirmation

**Test Plan**:
- **TC-001**: `isTTY()` returns false when stdin.isTTY is undefined
  - Given stdin.isTTY is not set → When `isTTY()` called → Then false
- **TC-002**: `promptCheckboxList` returns all indices on "a" then Enter
  - Given 3 items, none pre-checked → When input "a\n\n" → Then [0, 1, 2]
- **TC-003**: `promptCheckboxList` toggles individual items
  - Given 3 items, all pre-checked → When input "2\n\n" → Then [0, 2]
- **TC-004**: `promptChoice` returns selected index
  - Given 2 choices → When input "2\n" → Then 1
- **TC-005**: `promptConfirm` returns true on "y"
  - Given defaultYes=false → When input "y\n" → Then true
- **TC-006**: `promptConfirm` returns default on empty input
  - Given defaultYes=true → When input "\n" → Then true

**Dependencies**: None
**Status**: [ ] Not Started

---

### T-002 [GREEN]: Implement prompt utilities to pass tests
**User Story**: US-001, US-002, US-003, US-004, US-005 | **Satisfies ACs**: AC-US1-01 through AC-US1-04, AC-US2-01 through AC-US2-03, AC-US3-01, AC-US4-01, AC-US5-02, AC-US5-03 | **Status**: [x] completed

**Description**: Create `src/utils/prompts.ts` with minimal implementation to pass all T-001 tests:
- `isTTY()` using `process.stdin.isTTY && process.stdout.isTTY`
- `promptCheckboxList(items, options)` using `node:readline`
- `promptChoice(question, choices)` using `node:readline`
- `promptConfirm(question, defaultYes)` using `node:readline`
- Factory `createPrompter(input?, output?)` for testability

**Dependencies**: T-001
**Status**: [ ] Not Started

---

## Phase 2: Canonical Installer (TDD)

### T-003 [RED]: Write failing tests for canonical directory installer
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [x] completed

**Description**: Create `src/installer/canonical.test.ts` with tests for:
1. `installSymlink()` — creates canonical dir + symlinks to agents
2. `installCopy()` — creates independent copies per agent
3. `createRelativeSymlink()` — correct relative path computation
4. Symlink fallback to copy on EPERM

**Test Plan**:
- **TC-007**: `installSymlink` creates canonical dir and symlinks
  - Given temp dir and 2 mock agents → When called → Then `.agents/skills/my-skill/SKILL.md` exists AND symlinks point to it
- **TC-008**: `installCopy` creates independent copies
  - Given temp dir and 2 mock agents → When called → Then each agent has `my-skill/SKILL.md` AND no `.agents/` dir
- **TC-009**: `createRelativeSymlink` computes correct relative path
  - Given canonical at `/project/.agents/skills/foo` and link at `/project/.claude/commands/foo` → Then target = `../../.agents/skills/foo`
- **TC-010**: Symlink fallback to copy on EPERM error
  - Given symlink throws EPERM → When `installSymlink` called → Then direct copy created + warning logged

**Dependencies**: None (parallel with Phase 1)
**Status**: [ ] Not Started

---

### T-004 [GREEN]: Implement canonical installer to pass tests
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [x] completed

**Description**: Create `src/installer/canonical.ts` with:
- `installSymlink(skillName, content, agents, opts)` — canonical dir + relative symlinks
- `installCopy(skillName, content, agents, opts)` — direct copies per agent
- `ensureCanonicalDir(base)` — creates `.agents/skills/` under base
- `createRelativeSymlink(target, linkPath)` — relative symlink, returns false on failure

**Dependencies**: T-003
**Status**: [ ] Not Started

---

## Phase 3: Wizard Integration (TDD)

### T-005 [RED]: Write failing tests for wizard integration and --yes flag
**User Story**: US-001, US-002, US-003, US-004, US-005, US-006 | **Satisfies ACs**: AC-US1-05, AC-US1-06, AC-US2-04, AC-US2-05, AC-US2-06, AC-US3-04, AC-US3-05, AC-US4-05, AC-US5-04, AC-US6-01 through AC-US6-04 | **Status**: [x] completed

**Description**: Create `src/commands/add-wizard.test.ts` with tests for:
1. `--yes` flag skips all prompts, uses defaults
2. Non-TTY mode auto-skips prompts
3. Single-skill repos skip wizard entirely
4. Multi-skill repos trigger interactive wizard
5. `--agent` flag skips agent selection step
6. `--global` flag skips scope selection step

**Test Plan**:
- **TC-011**: `--yes` flag passes through AddOptions
  - Given opts.yes=true → When multi-skill install runs → Then no prompt functions called, all skills/agents selected
- **TC-012**: Non-TTY skips prompts
  - Given stdin not TTY → When multi-skill install without --yes → Then defaults used
- **TC-013**: Single skill repo skips wizard
  - Given 1 discovered skill → When addCommand called interactively → Then no prompts
- **TC-014**: --agent flag skips agent selection
  - Given opts.agent=["claude-code"] → When wizard runs → Then agent prompt not shown
- **TC-015**: --global flag skips scope selection
  - Given opts.global=true → When wizard runs → Then scope prompt not shown

**Dependencies**: T-001, T-003
**Status**: [ ] Not Started

---

### T-006 [GREEN]: Implement wizard integration to pass tests
**User Story**: US-001, US-002, US-003, US-004, US-005, US-006 | **Satisfies ACs**: AC-US1-05, AC-US1-06, AC-US2-04 through AC-US2-06, AC-US3-04, AC-US3-05, AC-US4-05, AC-US5-04, AC-US6-01 through AC-US6-04 | **Status**: [x] completed

**Description**: Modify `src/commands/add.ts` and `src/index.ts`:
1. Add `--yes` / `-y` option to install command in index.ts
2. Add `yes` to AddOptions interface
3. After multi-skill discovery, check if interactive mode applies
4. If interactive: run wizard (skill selection → agent selection → scope → method → confirm)
5. If non-interactive: use defaults (all skills, all agents, project scope, symlink)
6. Delegate to canonical installer based on method choice

**Dependencies**: T-005, T-002, T-004
**Status**: [ ] Not Started

---

## Phase 4: Polish

### T-007 [REFACTOR]: End-to-end integration test, help text, cleanup
**User Story**: US-001 through US-006 | **Satisfies ACs**: All | **Status**: [x] completed

**Description**:
1. Create `src/commands/add-interactive.test.ts` — full wizard E2E with mocked stdin
2. Update --help output to document --yes/-y
3. Code cleanup: remove duplication, improve naming
4. Verify all existing tests still pass

**Test Plan**:
- **TC-016**: Full wizard flow with all defaults accepted
- **TC-017**: Wizard with partial skill selection
- **TC-018**: Wizard with copy method selected
- **TC-019**: Abort at confirmation step

**Dependencies**: T-006
**Status**: [ ] Not Started

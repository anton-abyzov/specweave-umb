# Tasks: Complete Uninstall Support

## Task Notation
- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started | `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Shared Utility

### T-001: Add stripSwSections() to instruction-file-merger.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed
**Test**: Given a CLAUDE.md with SW sections and user content → When stripSwSections() is called → Then only user content remains
**Test**: Given a CLAUDE.md that is 100% SW-managed → When stripSwSections() is called → Then null is returned

**Implementation**:
- Add `stripSwSections(content: string): string | null` export to `repositories/anton-abyzov/specweave/src/cli/helpers/init/instruction-file-merger.ts`
- Uses existing `parseFile()` internally
- Returns joined user segments or null if empty

**Dependencies**: None

---

## Phase 2: vskill remove

### T-002: Implement vskill remove command
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07, AC-US1-08 | **Status**: [x] completed
**Test**: Given skill "sw" in lockfile with dirs in claude-code → When `vskill remove sw --force` → Then dirs deleted and lockfile updated
**Test**: Given skill not in lockfile → When `vskill remove unknown` → Then error message shown
**Test**: Given --global flag → When removing → Then only global dirs cleaned
**Test**: Given --local flag → When removing → Then only local dirs cleaned
**Test**: Given missing agent dirs → When removing → Then no error, continues gracefully

**Implementation**:
- New file: `repositories/anton-abyzov/vskill/src/commands/remove.ts`
- Register in `repositories/anton-abyzov/vskill/src/index.ts`
- Pattern: readLockfile → confirm → detectAgents → iterate dirs → rmSync → removeSkillFromLock → summary

**Dependencies**: None

---

## Phase 3: specweave uninstall

### T-003: Implement specweave uninstall command
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-05, AC-US2-06, AC-US2-07, AC-US2-08, AC-US2-09, AC-US2-10, AC-US2-11, AC-US2-12 | **Status**: [x] completed
**Test**: Given a SpecWeave project → When `specweave uninstall --force` → Then .specweave/, hook, lockfile removed
**Test**: Given --keep-data → When uninstalling → Then .specweave/ renamed to .specweave-backup-{timestamp}
**Test**: Given --dry-run → When uninstalling → Then manifest shown, nothing deleted
**Test**: Given --global → When uninstalling → Then global agent dirs and cache also cleaned
**Test**: Given no .specweave/ dir → When uninstalling → Then error "not a SpecWeave project"

**Implementation**:
- New file: `repositories/anton-abyzov/specweave/src/cli/commands/uninstall.ts`
- Register in `repositories/anton-abyzov/specweave/bin/specweave.js`
- Steps: discover → manifest → confirm → delete .specweave → strip CLAUDE/AGENTS → unhook → remove skills → delete lockfile → summary

**Dependencies**: T-001 (stripSwSections), T-002 (pattern reference)

---

### T-004: Integrate stripSwSections into uninstall for CLAUDE.md/AGENTS.md cleanup
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed
**Test**: Given CLAUDE.md with mixed content → When uninstalling → Then SW sections removed, user content preserved
**Test**: Given AGENTS.md 100% SW-managed → When uninstalling → Then file deleted entirely

**Implementation**:
- Call `stripSwSections()` in uninstall command for both CLAUDE.md and AGENTS.md
- If returns null → delete file
- If returns content → write stripped content

**Dependencies**: T-001, T-003

---

## Phase 4: npm Lifecycle

### T-005: [P] Add vskill preuninstall.cjs script
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-04 | **Status**: [x] completed
**Test**: Given global skill dirs exist → When npm uninstall -g vskill → Then warning printed listing remaining dirs

**Implementation**:
- New file: `repositories/anton-abyzov/vskill/scripts/preuninstall.cjs`
- Update `repositories/anton-abyzov/vskill/package.json` — add preuninstall script + files entry
- Standalone CommonJS, inline agent registry subset

**Dependencies**: None

---

### T-006: [P] Add specweave preuninstall.cjs script
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03, AC-US3-04 | **Status**: [x] completed
**Test**: Given specweave cache exists → When npm uninstall -g specweave → Then cache cleaned and advice printed

**Implementation**:
- New file: `repositories/anton-abyzov/specweave/scripts/preuninstall.cjs`
- Update `repositories/anton-abyzov/specweave/package.json` — add preuninstall script + files entry
- Standalone CommonJS, warns about project cleanup

**Dependencies**: None

---

## Phase 5: Verification

### T-007: Run all tests across both repos
**User Story**: All | **Status**: [x] completed
**Test**: Given all changes → When `npm test` in both repos → Then all tests pass

**Dependencies**: T-001 through T-006

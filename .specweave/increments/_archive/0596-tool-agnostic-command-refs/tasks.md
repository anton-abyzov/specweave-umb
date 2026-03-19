# Tasks: Tool-Agnostic Command References

**Increment**: 0596-tool-agnostic-command-refs
**Status**: Active

---

## User Story: US-001 - Tool-Agnostic AGENTS.md Template

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Tasks**: 1 total, 0 completed

### T-001: Update AGENTS.md.template to tool-agnostic format

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed

**Test Plan**:
- **Given** the updated AGENTS.md.template
- **When** grepping for `/sw:` outside Claude-specific columns
- **Then** zero matches found and "How to Invoke" section exists

---

## User Story: US-002 - Tool-Agnostic README Template

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Tasks**: 1 total, 0 completed

### T-002: Update README.md.template to tool-agnostic format

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed

**Test Plan**:
- **Given** the updated README.md.template
- **When** grepping for `/sw:` references
- **Then** zero matches found and "slash command" prose replaced

---

## User Story: US-003 - Unified Compiler Format

**Linked ACs**: AC-US3-01
**Tasks**: 1 total, 0 completed

### T-003: Update agents-md-compiler.ts to canonical format

**User Story**: US-003
**Satisfies ACs**: AC-US3-01
**Status**: [x] completed

**Test Plan**:
- **Given** agents-md-compiler.ts
- **When** grepping for `/specweave.`
- **Then** zero matches found

---

## User Story: US-004 - Tasks Template and CLAUDE.md Note

**Linked ACs**: AC-US4-01, AC-US4-02
**Tasks**: 2 total, 0 completed

### T-004: Update tasks.md.template

**User Story**: US-004
**Satisfies ACs**: AC-US4-01
**Status**: [x] completed

**Test Plan**:
- **Given** tasks.md.template
- **When** grepping for `/sw:`
- **Then** zero matches found

### T-005: Add mapping note to CLAUDE.md.template

**User Story**: US-004
**Satisfies ACs**: AC-US4-02
**Status**: [x] completed

**Test Plan**:
- **Given** CLAUDE.md.template
- **When** reading the "non-claude" section
- **Then** it contains format mapping note and all `/sw:` refs remain

---

## Progress

**Overall**: 5/5 tasks completed (100%)

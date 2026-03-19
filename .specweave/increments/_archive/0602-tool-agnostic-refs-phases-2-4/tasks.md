# Tasks: Tool-Agnostic Command References — Phases 2-4

**Increment**: 0602-tool-agnostic-refs-phases-2-4
**Status**: Active

---

## User Story: US-001 - Tool-Agnostic SKILL.md Files

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Tasks**: 1 total, 0 completed

### T-001: Replace /sw: in all SKILL.md and agent template files

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed

**Test Plan**:
- **Given** updated SKILL.md files
- **When** grepping for `/sw:` in plugins/specweave/skills/
- **Then** zero matches and Skill() calls unchanged

---

## User Story: US-002 - Tool-Agnostic Docs-Site

**Linked ACs**: AC-US2-01, AC-US2-02
**Tasks**: 1 total, 0 completed

### T-002: Replace /sw: in all docs-site markdown files

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02
**Status**: [x] completed

**Test Plan**:
- **Given** updated docs-site files
- **When** grepping for `/sw:` in docs-site/docs/
- **Then** zero or near-zero matches

---

## User Story: US-003 - Tool-Agnostic TypeScript Source

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Tasks**: 1 total, 0 completed

### T-003: Replace /sw: in TS source (preserve functional code)

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] completed

**Test Plan**:
- **Given** updated TS source files
- **When** grepping for `/sw:` excluding phase-detector and project-scope-guard
- **Then** zero matches and vitest passes

---

## Progress

**Overall**: 3/3 tasks completed (100%)

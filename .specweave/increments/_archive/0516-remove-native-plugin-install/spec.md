---
increment: 0516-remove-native-plugin-install
title: Remove native Claude Code plugin install from vskill
type: refactor
priority: P1
status: completed
created: 2026-03-12T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
completed_tasks: 0
total_tasks: 3
---

# Feature: Remove native Claude Code plugin install from vskill

## Overview

The `vskill install` command has two install paths: a native Claude Code plugin system (`claude plugin marketplace add` + `claude plugin install`) and a file-system extraction path. The native path is fragile, breaks due to stale caches, and adds complexity. All skills should be managed via file-system copy only.

The **sole exception** is `specweave init` (in the specweave repo) which keeps native install for the `sw` plugin only — this is unchanged.

**Performance**: Removing native install eliminates subprocess calls to the claude CLI and marketplace registration overhead. File-copy-only is faster and more reliable.

## User Stories

### US-001: File-system-only install (P1)
**Project**: vskill

**As a** developer installing vskill plugins
**I want** plugin install to always use file-system copy
**So that** install never fails due to stale Claude Code native plugin caches

**Acceptance Criteria**:
- [x] **AC-US1-01**: `vskill install` never calls `claude plugin marketplace add` or `claude plugin install`
- [x] **AC-US1-02**: `vskill install` never calls `claude plugin marketplace remove` or `claude plugin uninstall`
- [x] **AC-US1-03**: All agents including Claude Code receive skill files via extraction (file copy)
- [x] **AC-US1-04**: `src/utils/claude-cli.ts` is deleted; no import of it remains in `add.ts`
- [x] **AC-US1-05**: `npm run build` succeeds with no TypeScript errors

### US-002: Clean uninstall path (P1)
**Project**: vskill

**As a** developer uninstalling vskill plugins
**I want** uninstall to remove skill directories from agent folders
**So that** plugins are cleanly removed without native system calls

**Acceptance Criteria**:
- [x] **AC-US2-01**: Uninstall removes skill directories from all detected agents' local and global skill dirs
- [x] **AC-US2-02**: No native uninstall CLI call is made during removal

### US-003: Test coverage (P1)
**Project**: vskill

**As a** developer
**I want** the test suite to pass after removal
**So that** I have confidence the refactor didn't break existing functionality

**Acceptance Criteria**:
- [x] **AC-US3-01**: `npx vitest run` passes with all tests green
- [x] **AC-US3-02**: All native install test blocks and mocks are removed from `add.test.ts`

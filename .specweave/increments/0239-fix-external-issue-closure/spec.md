---
increment: 0239-fix-external-issue-closure
title: Fix External Issue Closure on Increment Completion
type: bugfix
priority: P1
status: completed
created: 2026-02-18T12:00:00.000Z
structure: user-stories
---

# Bugfix: External Issue Closure on Increment Completion

## Overview

When increments are completed via `/sw:done`, per-user-story GitHub issues are NOT being closed. 20 orphaned open issues exist on `anton-abyzov/specweave`. Root cause is a chain of 3 bugs in the sync pipeline: wrong method call, fire-and-forget setTimeout, and single-issue-only skill logic.

## User Stories

### US-001: Fix Wrong Closure Method Call (P0)
**Project**: specweave

**As a** developer completing an increment
**I want** the status change trigger to call the correct closure method
**So that** all per-user-story GitHub issues are closed automatically

**Acceptance Criteria**:
- [x] **AC-US1-01**: `autoCloseExternalIssues()` calls `syncIncrementClosure()` instead of `syncIncrementCompletion()`
- [x] **AC-US1-02**: Success log reports `closedIssues` count from the closure result

---

### US-002: Make Completion Sync Blocking (P0)
**Project**: specweave

**As a** developer completing an increment
**I want** the completion sync to run synchronously
**So that** issue closure completes before the process exits

**Acceptance Criteria**:
- [x] **AC-US2-01**: COMPLETED transitions run sync logic directly (no setTimeout)
- [x] **AC-US2-02**: Non-completion transitions still use non-blocking setTimeout

---

### US-003: Update DONE Skill for All Per-US Issues (P1)
**Project**: specweave

**As a** developer completing an increment
**I want** the done skill to instruct closure of ALL user-story issues
**So that** even if the compiled trigger fails, the skill-based fallback works

**Acceptance Criteria**:
- [x] **AC-US3-01**: Step 9C instructs closing all per-US issues by search pattern, not just metadata.github.issue
- [x] **AC-US3-02**: Step 9 includes a sync result summary showing closure outcomes

---

### US-004: Close Orphaned GitHub Issues (P0)
**Project**: specweave

**As a** project maintainer
**I want** all 20 orphaned GitHub issues closed
**So that** the issue tracker reflects the actual state of completed work

**Acceptance Criteria**:
- [x] **AC-US4-01**: All FS-237 issues (#1177-#1186) closed
- [x] **AC-US4-02**: All FS-238 issues (#1187-#1189) closed
- [x] **AC-US4-03**: All FS-230 issues (#1173-#1176) closed
- [x] **AC-US4-04**: All FS-220 issues (#1168-#1169) closed
- [x] **AC-US4-05**: FS-202 issue (#1160) assessed and handled appropriately

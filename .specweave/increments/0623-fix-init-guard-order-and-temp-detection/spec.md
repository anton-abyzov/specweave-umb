---
increment: 0623-fix-init-guard-order-and-temp-detection
title: "Fix init guard order and temp path detection"
type: bug
priority: P1
status: planned
created: 2026-03-19
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Bug Fix: Init guard order and temp path detection

## Overview

Three bugs in `specweave init` cause data loss and false positives when running from paths containing "temp" as a directory segment.

## User Stories

### US-001: Guards before destructive action (P1)
**Project**: specweave

**As a** developer running `specweave init` in a directory with an existing `.specweave/`
**I want** guard clauses to validate the path BEFORE I'm offered the "Fresh start" option
**So that** I don't lose data only to be told the path is invalid

**Acceptance Criteria**:
- [ ] **AC-US1-01**: `detectUmbrellaParent`, `detectSuspiciousPath`, and `detectNestedSpecweave` run before `promptSmartReinit` in both dot-path and named-path flows
- [ ] **AC-US1-02**: If a guard blocks init, no `.specweave/` data is deleted

---

### US-002: Narrow temp path detection (P1)
**Project**: specweave

**As a** developer with projects in a folder named "temp" (e.g. `~/temp/my-project`)
**I want** `specweave init` to not reject my path as suspicious
**So that** I can use any user-created folder name without false positives

**Acceptance Criteria**:
- [ ] **AC-US2-01**: User-created folders named "temp" or "tmp" in the path do NOT trigger the suspicious path guard
- [ ] **AC-US2-02**: Paths under the actual system temp directory (`os.tmpdir()`) ARE flagged as suspicious
- [ ] **AC-US2-03**: `SUSPICIOUS_PATH_SEGMENTS` no longer contains "tmp" or "temp"

---

### US-003: Safe suggestedRoot (P1)
**Project**: specweave

**As a** developer seeing a suspicious-path error
**I want** the suggested alternative root to be a useful location
**So that** I get actionable guidance instead of being pointed to my home directory

**Acceptance Criteria**:
- [ ] **AC-US3-01**: `suggestedRoot` never returns `os.homedir()` or an ancestor of it
- [ ] **AC-US3-02**: When the naive computation would return home dir, falls back to `path.dirname(targetDir)`

## Out of Scope

- Refactoring the entire init command flow
- Changing the `--force` override behavior (guards already respect it)
- Adding new suspicious path segments

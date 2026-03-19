---
increment: 0582-fix-duplicate-increment-creation
title: Fix Duplicate Increment Creation Bugs
type: bug
priority: P1
status: completed
created: 2026-03-18T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Fix Duplicate Increment Creation Bugs

## Problem Statement

Six bugs in the SpecWeave CLI cause duplicate or incorrect increment IDs to be generated. When `specweave init` runs in a directory with sibling SpecWeave projects, the `next-id` command scans the wrong project's increments. Additionally, `_backlog/` increments are invisible to the ID scanner, a TOCTOU race exists between `next-id` and `create-increment`, the increment SKILL.md references Claude Code-specific tools, and the duplicate guard hook is disabled. Together these create orphaned duplicates and ID collisions.

## Goals

- Ensure `next-id` always scans the correct project root
- Make `_backlog/` increments visible to all scan methods
- Eliminate the TOCTOU race between ID reservation and increment creation
- Make SKILL.md portable across AI coding tools
- Re-enable name-duplicate detection with no false positives

## User Stories

### US-001: next-id Respects Explicit Project Root (P1)
**Project**: specweave

**As a** SpecWeave CLI user
**I want** `specweave next-id` to accept a `--project-root` parameter
**So that** it scans the intended project's increments regardless of my shell's working directory

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a project at `/tmp/project-a` with increments 0001-0003, when I run `specweave next-id --project-root /tmp/project-a` from `/tmp/project-b`, then the output is `0004`
- [x] **AC-US1-02**: Given `--project-root` is not provided, when I run `specweave next-id`, then behavior is unchanged (uses `resolveEffectiveRoot(process.cwd())`)
- [x] **AC-US1-03**: Given `--project-root` points to a directory without `.specweave/config.json`, when I run `specweave next-id --project-root /tmp/empty`, then the command exits with a non-zero code and an error message

---

### US-002: Init Creates config.json Before increments/ (P1)
**Project**: specweave

**As a** developer running `specweave init`
**I want** `config.json` to be written before the `increments/` directory is created
**So that** `findProjectRoot()` can identify this project immediately, preventing fallback to a sibling project's root

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given a fresh directory with no `.specweave/`, when `specweave init` runs, then `.specweave/config.json` exists on disk before `.specweave/increments/` is created
- [x] **AC-US2-02**: Given a sibling directory at `../other-project` with `.specweave/config.json`, when `specweave init --quick` completes in the current directory, then `specweave next-id` returns `0001` (not a continuation of sibling IDs)
- [x] **AC-US2-03**: Given `specweave init` is interrupted after config.json is written but before increments/ is created, when `specweave init` is re-run, then it detects the partial init and continues without error

---

### US-003: ID Scanner Includes _backlog/ (P1)
**Project**: specweave

**As a** SpecWeave user managing a backlog
**I want** `getAllIncrementNumbers()` to scan `_backlog/` alongside `_archive/`, `_abandoned/`, and `_paused/`
**So that** moving an increment to backlog does not free its ID for reuse

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given increment `0005-feature` exists in `.specweave/increments/_backlog/`, when `getNextIncrementNumber()` is called, then the returned ID is greater than `0005`
- [x] **AC-US3-02**: Given `RECOGNIZED_LIFECYCLE_FOLDERS` contains `_backlog`, when `getAllIncrementNumbers()` builds its `dirsToScan` array, then `_backlog` is included
- [x] **AC-US3-03**: Given increments 0001-0003 are active and 0004 is in `_backlog/`, when `next-id` is called, then the output is `0005` (not `0004`)

---

### US-004: Atomic ID Reservation (P1)
**Project**: specweave

**As a** developer in a multi-agent environment
**I want** increment ID reservation and directory creation to be atomic
**So that** no other process can claim the same ID between `next-id` and `create-increment`

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given two concurrent `create-increment` calls, when both attempt to reserve the next ID simultaneously, then each gets a unique ID (no collision)
- [x] **AC-US4-02**: Given `specweave create-increment` is called without a pre-computed `--id`, when the command runs, then it internally calls `getNextIncrementNumber()` and creates the directory in a single operation
- [x] **AC-US4-03**: Given the `next-id` CLI command is called externally (not via `create-increment`), when another process creates an increment between the `next-id` call and subsequent use, then the stale ID is detected and a fresh ID is generated at creation time

---

### US-005: Portable Increment SKILL.md (P2)
**Project**: specweave

**As a** developer using OpenCode, Cursor, or another AI coding tool
**I want** the increment SKILL.md to not reference Claude Code-specific tools (TeamCreate, Agent, SendMessage, EnterPlanMode)
**So that** my AI tool does not hallucinate unsupported tool calls that create duplicate increments

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given the increment SKILL.md Step 4 delegation section, when parsed by any LLM, then all tool references use generic SpecWeave CLI commands (e.g., `specweave create-increment`, `specweave next-id`) instead of Claude Code-specific tools
- [x] **AC-US5-02**: Given a non-Claude-Code environment, when the SKILL.md is loaded, then no instructions reference `TeamCreate`, `Agent()`, `SendMessage`, or `EnterPlanMode` as required tools
- [x] **AC-US5-03**: Given a Claude Code environment, when the increment skill runs, then Claude Code-specific delegation (teams, agents) is handled by the adapter layer or a Claude-specific overlay, not hardcoded in SKILL.md

---

### US-006: Re-enable Increment Name Duplicate Guard (P2)
**Project**: specweave

**As a** SpecWeave user
**I want** the increment-duplicate-guard to detect and warn about name-duplicate increments
**So that** I am alerted when an increment with the same slug already exists

**Acceptance Criteria**:
- [x] **AC-US6-01**: Given increment `0010-user-auth` exists, when `create-increment --id 0015-user-auth` is called, then a warning is emitted indicating a name collision with `0010-user-auth`
- [x] **AC-US6-02**: Given the guard detects a name duplicate, when the warning is emitted, then the operation still proceeds (warning, not blocking) to avoid false-positive disruption
- [x] **AC-US6-03**: Given increments in `_archive/` and `_abandoned/`, when checking for name duplicates, then only active and `_backlog/` increments are considered (archived/abandoned names can be reused)

## Out of Scope

- Rewriting `findProjectRoot()` / `resolveEffectiveRoot()` beyond the init ordering fix
- Multi-machine distributed locking (atomic reservation is process-level only)
- Full rewrite of the increment SKILL.md — only portability changes to Step 4
- Changing the 4-digit increment ID format

## Non-Functional Requirements

- **Backward Compatibility**: Existing `next-id` usage without `--project-root` must behave identically
- **Performance**: Atomic ID reservation must not add >50ms latency vs current two-step flow
- **Testability**: All 6 fixes must have unit tests; TOCTOU fix must have a concurrency integration test

## Edge Cases

- Empty project (no increments at all) → `next-id` returns `0001`
- All lifecycle folders empty → scanner returns empty set, `next-id` returns `0001`
- Gap-filling with `_backlog`: IDs 1,2,4 active + 3 in backlog → `next-id` returns `0005` (not `0003`)
- `--project-root` pointing to umbrella root with child repos → scans umbrella's `.specweave/increments/`
- Concurrent `create-increment` from 3+ parallel agents → all get unique sequential IDs

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Init reorder breaks existing reinit flow | 0.3 | 5 | 1.5 | Test reinit path explicitly (AC-US2-03) |
| Atomic reservation adds lock contention | 0.2 | 3 | 0.6 | Use mkdir-based atomic check (no external lock files) |
| SKILL.md portability breaks Claude Code delegation | 0.4 | 6 | 2.4 | Adapter overlay pattern keeps Claude-specific logic separate |

## Technical Notes

- `getAllIncrementNumbers()` at `increment-utils.ts:263` hardcodes `_archive/_abandoned/_paused` — must derive from `RECOGNIZED_LIFECYCLE_FOLDERS`
- `next-id` CLI at `specweave.js:376` calls `resolveEffectiveRoot(process.cwd())` — add `--project-root` option that takes priority
- `init.ts:322` calls `createDirectoryStructure()` (creates `increments/`) at line 322, but `createConfigFile()` at line 403 — swap order
- For atomic reservation, `mkdir` is atomic on all POSIX systems — use `mkdirSync` with `{ recursive: false }` as the lock mechanism
- Duplicate guard at `increment-duplicate-guard.sh` is a no-op (line 13: `echo '{"decision":"allow"}'`) — rewrite with name-slug comparison logic

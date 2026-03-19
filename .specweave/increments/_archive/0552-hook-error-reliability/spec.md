---
increment: 0552-hook-error-reliability
title: Fix Hook Error Reliability
type: bug
priority: P1
status: completed
created: 2026-03-16T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Fix Hook Error Reliability

## Problem Statement

Users constantly see "PreToolUse:Write error" and "PostToolUse:Write error" messages during Claude Code sessions. Six distinct root causes contribute to hook failures, wasted latency (200-500ms+ per non-increment edit), and blocked functionality (GitHub auto-create). These errors erode trust in the hook system and degrade the developer experience.

## Goals

- Eliminate all spurious hook error messages from normal Claude Code sessions
- Reduce per-tool-call hook overhead by removing dead hooks and adding proper matchers
- Restore GitHub auto-create functionality blocked by a stuck circuit breaker
- Ship as npm patch release 1.0.492

## User Stories

### US-001: Null-Safe Dashboard Cache Updates
**Project**: specweave
**As a** developer using SpecWeave hooks
**I want** the dashboard cache update script to handle missing counter keys gracefully
**So that** jq does not crash with null subtraction errors during normal operations

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given `update-dashboard-cache.sh` is invoked and a summary key does not exist in the cache JSON, when the script decrements that key, then it defaults to 0 via `// 0` instead of crashing
- [x] **AC-US1-02**: Given all 6 decrement operations in the script, when any target key is null or missing, then each uses the `// 0` null-coalescing pattern
- [x] **AC-US1-03**: Given a dashboard cache with valid existing counters, when the script decrements them, then behavior is unchanged from before the fix

---

### US-002: Scoped PostToolUse Hook for Increment Files
**Project**: specweave
**As a** developer editing non-increment files
**I want** the `close-completed-issues.sh` hook to fire only on increment file edits
**So that** I do not pay 200-500ms of overhead on every unrelated Edit/Write operation

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given the project-level hook configuration for `close-completed-issues.sh`, when the config is updated, then it includes a `matcher_content` pattern matching `.specweave/increments/`
- [x] **AC-US2-02**: Given an Edit/Write to a file outside `.specweave/increments/`, when the PostToolUse hook evaluates, then `close-completed-issues.sh` does not execute
- [x] **AC-US2-03**: Given an Edit/Write to `.specweave/increments/*/tasks.md`, when the PostToolUse hook evaluates, then `close-completed-issues.sh` executes normally

---

### US-003: Remove Dead Hook Config Entry
**Project**: specweave
**As a** developer using SpecWeave
**I want** the non-functional `ac-status-sync.sh` hook config entry removed
**So that** no overhead is wasted invoking a hook that always silently exits

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given the `.claude/settings.json` file, when the dead hook entry for `ac-status-sync.sh` is removed, then the hook no longer fires on any tool event
- [x] **AC-US3-02**: Given the `ac-status-sync.sh` file on disk, when the config entry is removed, then the shell script file itself is preserved for potential future re-implementation

---

### US-004: Reset Stuck Circuit Breaker
**Project**: specweave
**As a** developer who needs GitHub auto-creation
**I want** the tripped circuit breaker file cleared
**So that** GitHub issue/milestone auto-creation resumes working

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given the file `.specweave/state/.hook-circuit-breaker-github-auto-create` exists with value "3", when the fix is applied, then the file is deleted
- [x] **AC-US4-02**: Given the circuit breaker file is deleted, when a new increment triggers GitHub auto-creation, then the hook executes instead of being short-circuited

---

### US-005: Remove Hookify Plugin Overhead
**Project**: specweave
**As a** developer running any Claude Code tool
**I want** the hookify plugin's empty hooks removed from the configuration
**So that** 2 Python processes are not spawned per tool call with no rule files to process

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given the hookify plugin hook entries in project configuration, when the entries are removed, then no Python processes are spawned for hookify on tool calls
- [x] **AC-US5-02**: Given a tool call after the fix, when hook execution completes, then the total hook count is reduced by the removed hookify entries

---

### US-006: NPM Patch Release
**Project**: specweave
**As a** SpecWeave user
**I want** all 6 fixes shipped as patch version 1.0.492
**So that** I get the reliability improvements via a standard npm update

**Acceptance Criteria**:
- [x] **AC-US6-01**: Given the specweave package.json, when the version is bumped, then it reads "1.0.492"
- [x] **AC-US6-02**: Given all fixes from US-001 through US-005 are applied, when the package is published, then all fixes are included unconditionally with no config flags

## Out of Scope

- Adding a CLI command to reset circuit breakers (existing mechanism is sufficient)
- Re-implementing the `ac-status-sync.sh` hook logic (file preserved for future work)
- Adding `gtimeout` installation or Homebrew dependency management for macOS
- Refactoring the hook system architecture beyond targeted fixes

## Non-Functional Requirements

- **Performance**: Hook overhead per non-increment Edit/Write reduced by at least 200ms
- **Compatibility**: All fixes must work on both macOS (without gtimeout) and Linux

## Edge Cases

- Dashboard cache JSON file missing entirely: script should handle gracefully (existing behavior, not regressed)
- Circuit breaker file already absent: deletion is a no-op
- Multiple hookify entries in config: all must be removed, not just one

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Removing hookify breaks a hook someone depends on | 0.1 | 3 | 0.3 | No rule files exist; hooks are pure overhead |
| close-completed-issues matcher too broad/narrow | 0.2 | 4 | 0.8 | Use `.specweave/increments/` prefix which covers all increment files |

## Technical Notes

- `update-dashboard-cache.sh` has exactly 6 occurrences of `.summary[$key] -= 1` that need `// 0`
- The `close-completed-issues.sh` hook config is in project-level `.claude/settings.json` under PostToolUse
- Circuit breaker file path: `.specweave/state/.hook-circuit-breaker-github-auto-create`
- Hookify spawns Python via `hookify run` with 10ms timeout and no matcher

## Success Metrics

- Zero "PreToolUse:Write error" / "PostToolUse:Write error" messages in normal Claude Code sessions
- GitHub auto-create hooks fire successfully on new increments
- Measurable reduction in per-tool-call latency (200ms+ saved on non-increment edits)

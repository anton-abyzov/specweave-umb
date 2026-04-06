---
increment: 0661-cli-first-hook-rework
title: "CLI-First Hook Architecture Rework"
type: feature
priority: P1
status: planned
created: 2026-04-06
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# CLI-First Hook Architecture Rework

## Problem Statement

SpecWeave currently registers 15 hook event types with Claude Code, but only 2 require synchronous interception (PreToolUse guards and UserPromptSubmit context injection). The other 13 are fire-and-forget side effects (analytics, event queuing, session cleanup, sync) that add per-turn overhead and couple SpecWeave tightly to Claude Code's hook protocol. This makes SpecWeave harder to port to other AI coding tools and reduces hook system reliability (currently rated 6/10).

## Goals

- Reduce Claude Code hook registrations from 15 event types to 2 (PreToolUse, UserPromptSubmit)
- Migrate session lifecycle, sync flush, and analytics push to CLI commands
- Fix silent error swallowing in catch blocks across hook handlers
- Delete stale v2 shell test files that test already-migrated functionality
- Isolate test log writes to prevent cross-test leakage
- Update AGENTS.md to document the new hook-vs-CLI boundary

## User Stories

### US-001: Trim Hook Registrations (P0)
**Project**: specweave

**As a** SpecWeave maintainer
**I want** generate-settings.ts to emit only PreToolUse and UserPromptSubmit hook entries
**So that** per-turn hook overhead drops and the hook surface is minimal

**Acceptance Criteria**:
- [ ] **AC-US1-01**: Given httpMode is true in config, when generateHooksSettings() runs, then the returned hooks object contains exactly 2 HTTP event entries: PreToolUse and UserPromptSubmit
- [ ] **AC-US1-02**: Given httpMode is true, when generateHooksSettings() runs, then no command-type event entries are emitted (COMMAND_EVENTS array is empty or removed)
- [ ] **AC-US1-03**: Given an existing settings.json with old hook entries (PostToolUse, Stop, SessionStart, etc.), when writeSettings() runs, then stale hook keys for migrated events are removed from the merged output

---

### US-002: Hook Router Reduction (P0)
**Project**: specweave

**As a** SpecWeave maintainer
**I want** the hook-router.ts HANDLERS map to contain only pre-tool-use and user-prompt-submit
**So that** the router does not load dead handler modules

**Acceptance Criteria**:
- [ ] **AC-US2-01**: Given the HANDLERS map in hook-router.ts, when inspected, then it contains exactly 2 entries: 'pre-tool-use' and 'user-prompt-submit'
- [ ] **AC-US2-02**: Given the HookEventType union in types.ts, when inspected, then it contains exactly 'pre-tool-use' and 'user-prompt-submit'
- [ ] **AC-US2-03**: Given the SAFE_DEFAULTS map in types.ts, when inspected, then it contains exactly 2 entries matching the remaining hook types

---

### US-003: CLI Session Start Command (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** a `specweave session start` CLI command that performs all session initialization
**So that** session setup logic is decoupled from the Claude Code hook protocol

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Given `specweave session start` is invoked, when it runs, then it clears stale auto-mode files older than 24 hours
- [ ] **AC-US3-02**: Given `specweave session start` is invoked, when it runs, then it resets context-pressure.json and prompt-health-alert.json
- [ ] **AC-US3-03**: Given `specweave session start` is invoked, when it runs, then it performs baseline prompt health check and writes prompt-health.json
- [ ] **AC-US3-04**: Given `specweave session start` is invoked with --session-id flag, when it runs, then it creates a per-session state directory and bridges the session ID
- [ ] **AC-US3-05**: Given `specweave session start` is invoked, when it runs, then it cleans orphaned state files and stale plugin references

---

### US-004: CLI Session End Command (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** a `specweave session end` CLI command that consolidates all three Stop hook handlers
**So that** session teardown runs reliably outside the hook protocol

**Acceptance Criteria**:
- [ ] **AC-US4-01**: Given `specweave session end` is invoked, when it runs, then it checks reflect config and logs reflection intent if enabled (stop-reflect logic)
- [ ] **AC-US4-02**: Given `specweave session end` is invoked with an active auto-mode session, when it runs, then it scans pending tasks and logs progress (stop-auto logic)
- [ ] **AC-US4-03**: Given `specweave session end` is invoked with pending events in event-queue/pending.jsonl, when it runs, then it deduplicates by increment ID, logs sync intent, and clears the queue (stop-sync logic)
- [ ] **AC-US4-04**: Given `specweave session end` is invoked and all three sub-operations complete, when it finishes, then it exits with code 0

---

### US-005: CLI Sync Flush Command (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** a `specweave sync flush` CLI command that processes the PostToolUse event queue on demand
**So that** sync events are not lost when hooks fail or are disabled

**Acceptance Criteria**:
- [ ] **AC-US5-01**: Given `specweave sync flush` is invoked, when pending.jsonl has queued events, then it reads, deduplicates by increment ID, and writes events to the sync log
- [ ] **AC-US5-02**: Given `specweave sync flush` is invoked, when processing completes, then pending.jsonl is truncated to empty
- [ ] **AC-US5-03**: Given `specweave sync flush --dry-run` is invoked, when it runs, then it reports what would be flushed without clearing the queue

---

### US-006: CLI Analytics Push Command (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** a `specweave analytics push` CLI command that records Skill and Task usage events
**So that** analytics collection does not depend on PostToolUse hooks firing

**Acceptance Criteria**:
- [ ] **AC-US6-01**: Given `specweave analytics push --type skill --name sw:pm` is invoked, when it runs, then it appends a skill analytics event to events.jsonl with correct timestamp and plugin extraction
- [ ] **AC-US6-02**: Given `specweave analytics push --type agent --name general` is invoked, when it runs, then it appends an agent analytics event to events.jsonl
- [ ] **AC-US6-03**: Given `specweave analytics push` is invoked without required flags, when it runs, then it exits with code 1 and prints usage help

---

### US-007: Fix Error Logging in Catch Blocks (P1)
**Project**: specweave

**As a** SpecWeave maintainer
**I want** all empty catch blocks in hook handlers to log the swallowed error
**So that** hook failures are diagnosable from logs instead of silently vanishing

**Acceptance Criteria**:
- [ ] **AC-US7-01**: Given the pre-tool-use handler's readJsonSafe function catches an error, when the error occurs, then it logs the error message to the handler's log file via logHook or appendLog
- [ ] **AC-US7-02**: Given any handler catch block in hook-router.ts, post-tool-use.ts, post-tool-use-analytics.ts, stop-sync.ts, stop-auto.ts, stop-reflect.ts, session-start.ts, or pre-compact.ts, when an error is caught, then it calls logHook/appendLog with the error message before returning the safe default
- [ ] **AC-US7-03**: Given error logging is added to catch blocks, when the handler runs normally (no errors), then no additional log output is produced

---

### US-008: Test Log Isolation (P1)
**Project**: specweave

**As a** SpecWeave maintainer
**I want** hook handler tests to use isolated temp directories for log output
**So that** parallel test runs do not leak log files across test suites

**Acceptance Criteria**:
- [ ] **AC-US8-01**: Given any hook handler test file, when it creates a HookContext, then the logsDir points to a unique temp directory created per test
- [ ] **AC-US8-02**: Given a hook handler test completes (pass or fail), when cleanup runs, then the temp directory is removed

---

### US-009: Delete Stale v2 Shell Tests (P0)
**Project**: specweave

**As a** SpecWeave maintainer
**I want** the 4 stale .test.sh files in tests/unit/hooks/ deleted
**So that** the test suite does not contain dead tests for already-migrated shell hooks

**Acceptance Criteria**:
- [ ] **AC-US9-01**: Given the files interview-enforcement-guard.test.sh, shell-injection.test.sh, tdd-enforcement-guard.test.sh, and interview-gate-injection.test.sh, when the increment is complete, then all 4 files are deleted from tests/unit/hooks/
- [ ] **AC-US9-02**: Given the 4 shell test files are deleted, when `npx vitest run` executes, then no test failures are introduced by their removal

---

### US-010: Update AGENTS.md (P2)
**Project**: specweave

**As a** SpecWeave user using Cursor/Copilot/Windsurf
**I want** AGENTS.md to document the CLI-first hook architecture
**So that** other AI tools know which commands replace the old hook events

**Acceptance Criteria**:
- [ ] **AC-US10-01**: Given AGENTS.md exists, when the increment is complete, then it contains a "Hook Architecture" section listing PreToolUse and UserPromptSubmit as the only active hooks
- [ ] **AC-US10-02**: Given AGENTS.md exists, when the increment is complete, then it contains a "Session Lifecycle" section documenting `specweave session start` and `specweave session end` as replacements for SessionStart/Stop hooks

## Out of Scope

- Migrating PreToolUse guards to CLI (they must remain synchronous hooks)
- Migrating UserPromptSubmit to CLI (context injection must happen before prompt processing)
- Implementing actual GitHub/JIRA/ADO sync calls in `specweave sync flush` (that is stop-sync's future follow-up)
- Migrating the dashboard HTTP hook server (command-bridge.mjs) -- separate concern
- Processor.ts (event-driven architecture processor) -- remains as-is for internal event routing
- PreCompact CLI command -- accepting loss of context-pressure tracking via hook

## Technical Notes

### Dependencies
- Commander.js CLI framework (already used for all specweave commands)
- session-state-manager.ts (createSessionDir, bridgeSessionId, gcDeadSessions)
- cleanup-stale-plugins.ts (cleanupStalePlugins)
- state-cleanup.ts (cleanOrphanedStateFiles)
- core/analytics/types.ts (AnalyticsEvent type)

### Constraints
- PreToolUse and UserPromptSubmit MUST remain as hooks -- they are the only event types that require synchronous interception before Claude Code acts
- CLI commands must be idempotent (safe to run multiple times)
- All existing handler logic moves to CLI commands unchanged -- no behavior changes, only trigger mechanism changes

### Architecture Decisions
- Accept PreCompact loss rather than creating a CLI command for a nice-to-have feature
- Consolidate 3 Stop hooks (reflect, auto, sync) into a single `specweave session end` command
- PostToolUse event queue and analytics split into separate CLI commands for single-responsibility

## Non-Functional Requirements

- **Performance**: Hook system overhead per turn reduces from 15 event type registrations to 2
- **Compatibility**: CLI commands work on Windows, macOS, Linux (same as existing handlers)
- **Security**: PreToolUse guards remain synchronous hooks to prevent unauthorized tool execution
- **Testability**: All new CLI commands have unit tests with isolated temp directories

## Edge Cases

- Stale settings.json: writeSettings() must remove old hook entries for migrated events, not just skip writing them
- Empty pending.jsonl: `specweave sync flush` handles gracefully with no-op
- Missing .specweave/ directory: CLI commands exit with informative error, not crash
- Concurrent sessions: `specweave session start --session-id` creates isolated dirs per session
- No analytics dir: `specweave analytics push` creates the directory on first write

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Old settings.json not cleaned up on upgrade | 0.4 | 6 | 2.4 | writeSettings() actively removes stale hook keys |
| Test suite breaks from shell test deletion | 0.2 | 4 | 0.8 | Verify no other tests depend on .test.sh files |
| Session end not called if Claude Code crashes | 0.3 | 3 | 0.9 | Accept: same risk existed with Stop hooks |

## Success Metrics

- Hook event types registered: 15 -> 2 (87% reduction)
- Hook system reliability: 6/10 -> 8/10
- All empty catch blocks have error logging
- Zero stale shell test files remain
- AGENTS.md documents the CLI-first architecture

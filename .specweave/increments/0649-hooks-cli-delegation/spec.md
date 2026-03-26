---
increment: 0649-hooks-cli-delegation
title: Hooks Architecture Redesign — CLI Delegation
type: refactor
priority: P1
status: completed
created: 2026-03-26T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Hooks Architecture Redesign — CLI Delegation

## Problem Statement

SpecWeave's plugin hooks system ships 65 files (704 KB) of bash/mjs/cmd/ps1 scripts in `plugins/specweave/hooks/`. This causes:

1. **127 KB monolith** -- `user-prompt-submit.sh` is 2,550 lines (violates 1,500-line limit)
2. **96 KB dead code** -- `_archive/`, test files, and unused wrappers shipped to every installation
3. **Cross-OS broken** -- Windows `.cmd`/`.ps1` wrappers exist but everything routes through bash via `universal/run-hook.sh`
4. **DRY violations** -- `find_project_root()` reimplemented in 10 files, `escape_json` defined in 3 files (24 total occurrences across hooks)
5. **Project-local copy waste** -- `copyPluginSkillsToProject` copies hooks to `.claude/hooks/` per project, but Claude Code uses `${CLAUDE_PLUGIN_ROOT}` (the copies are never executed)
6. **v1/v2 coexistence** -- `v2/` subdirectory with dispatchers, guards, handlers, integrations coexists with top-level v1 scripts; incomplete migration creates confusion

## Solution

Migrate all hook logic to TypeScript CLI handlers. The `hooks/` directory goes from 65 files across 13 subdirectories to a single `hooks.json` file. All logic moves to `src/core/hooks/handlers/` as TypeScript modules invoked via a new `specweave hook <event-type>` CLI command.

### Architecture

```
hooks.json entries:
  "command": "bash .../run-hook.sh v2/dispatchers/pre-tool-use"
becomes:
  "command": "specweave hook pre-tool-use"
```

The `specweave hook` command:
- Reads JSON from stdin (Claude Code hook protocol)
- Routes to the correct handler via dynamic import
- Writes JSON to stdout
- Returns safe fallback JSON on any error (never crashes Claude Code)
- Hidden from `specweave --help` (internal command)

### Handler mapping

| hooks.json event | Handler module |
|---|---|
| `pre-tool-use` | `handlers/pre-tool-use.ts` |
| `pre-compact` | `handlers/pre-compact.ts` |
| `session-start` | `handlers/session-start.ts` |
| `user-prompt-submit` | `handlers/user-prompt-submit.ts` |
| `post-tool-use` | `handlers/post-tool-use.ts` |
| `post-tool-use-analytics` | `handlers/post-tool-use-analytics.ts` |
| `stop-reflect` | `handlers/stop-reflect.ts` |
| `stop-auto` | `handlers/stop-auto.ts` |
| `stop-sync` | `handlers/stop-sync.ts` |

---

## User Stories

### US-001: CLI Hook Delegation (P0)
**Project**: specweave

**As a** SpecWeave developer
**I want** all hook logic implemented in TypeScript CLI handlers
**So that** hooks are maintainable, testable, and cross-platform

**Acceptance Criteria**:
- [x] **AC-US1-01**: `specweave hook <event-type>` CLI command exists and routes to correct handler
- [x] **AC-US1-02**: Hook router reads JSON from stdin and writes JSON to stdout (Claude Code hook protocol)
- [x] **AC-US1-03**: Router returns safe JSON on any error -- `{"continue":true}` for session/compact hooks, `{"decision":"allow"}` for pre-tool-use, `{"decision":"approve"}` for prompt/stop hooks
- [x] **AC-US1-04**: Dynamic imports used per handler for fast startup (no loading all handlers upfront)
- [x] **AC-US1-05**: Command is hidden from `specweave --help` output

---

### US-002: Pre-Compact Handler Migration (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** the pre-compact hook to work via TypeScript
**So that** context pressure tracking is cross-platform

**Acceptance Criteria**:
- [x] **AC-US2-01**: Writes `context-pressure.json` to `.specweave/state/` with escalating levels (elevated/critical/emergency)
- [x] **AC-US2-02**: Writes `prompt-health-alert.json` to `.specweave/state/` with remediation advice
- [x] **AC-US2-03**: Returns `{"continue":true}` when no `.specweave/config.json` exists (non-SpecWeave projects pass through)
- [x] **AC-US2-04**: Respects `SPECWEAVE_DISABLE_HOOKS=1` environment variable (returns safe default immediately)

---

### US-003: Pre-Tool-Use Guards Migration (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** pre-tool-use guards to work via TypeScript
**So that** workflow enforcement is cross-platform

**Acceptance Criteria**:
- [x] **AC-US3-01**: Edit/Write on `metadata.json` that changes status to "completed" is blocked (must use `specweave complete`)
- [x] **AC-US3-02**: Write to `spec.md` blocked when strict interview is incomplete (checks `metadata.json` interview state)
- [x] **AC-US3-03**: TeamCreate blocked when no qualifying active increment exists (status "active" or "in-progress")
- [x] **AC-US3-04**: Non-increment file paths (files outside `.specweave/increments/`) always return `{"decision":"allow"}`
- [x] **AC-US3-05**: Returns well-formed `{"decision":"allow"}` or `{"decision":"block","reason":"..."}` JSON in all cases

---

### US-004: Post-Tool-Use Handler Migration (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** post-tool-use handlers to work via TypeScript
**So that** lifecycle detection and sync queueing are cross-platform

**Acceptance Criteria**:
- [x] **AC-US4-01**: Detects `metadata.json` status changes and queues lifecycle events (increment.started, increment.paused, etc.)
- [x] **AC-US4-02**: Detects `spec.md` AC checkbox changes (unchecked to checked and vice versa)
- [x] **AC-US4-03**: Queues events to `.specweave/state/event-queue/pending.jsonl` for stop-sync to process
- [x] **AC-US4-04**: Triggers immediate sync for `increment.done` and `increment.reopened` events (does not wait for stop-sync)
- [x] **AC-US4-05**: Analytics handler tracks Skill/Task tool invocations to `.specweave/state/analytics/events.jsonl`
- [x] **AC-US4-06**: GitHub/JIRA/ADO integration handlers loaded lazily based on `sync` config in `.specweave/config.json`

---

### US-005: Session-Start Handler Migration (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** session-start to work via TypeScript
**So that** session initialization is cross-platform

**Acceptance Criteria**:
- [x] **AC-US5-01**: Clears stale auto-mode session files (`.specweave/state/auto-session-*.json` older than 24h)
- [x] **AC-US5-02**: Resets context pressure state (clears `context-pressure.json`)
- [x] **AC-US5-03**: Performs baseline health check -- validates CLAUDE.md exists, checks MEMORY.md size warning
- [x] **AC-US5-04**: Returns `{"continue":true}` when no `.specweave/` directory exists (non-SpecWeave projects pass through)

---

### US-006: User-Prompt-Submit Handler Migration (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** the user-prompt-submit hook to work via TypeScript
**So that** prompt validation and context injection are cross-platform and maintainable

**Acceptance Criteria**:
- [x] **AC-US6-01**: Built-in Claude Code commands (`/help`, `/clear`, `/config`, `/status`) skip SpecWeave processing entirely
- [x] **AC-US6-02**: `/sw:` prefixed commands get fast-path routing (no LLM intent detection needed)
- [x] **AC-US6-03**: Project scope guard blocks SpecWeave skills outside initialized projects (no `.specweave/` directory)
- [x] **AC-US6-04**: Intent detection delegates to existing `detect-intent` CLI command (no reimplementation)
- [x] **AC-US6-05**: Context injection appends active increment info (ID, status, current task) to prompt
- [x] **AC-US6-06**: Turn deduplication via content hash prevents duplicate processing of identical prompts
- [x] **AC-US6-07**: Returns `{"decision":"approve"}` with optional `user_prompt` field, or `{"decision":"block","reason":"..."}`

---

### US-007: Stop Hooks Migration (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** stop hooks to work via TypeScript
**So that** session finalization is cross-platform

**Acceptance Criteria**:
- [x] **AC-US7-01**: `stop-reflect` extracts learnings from conversation when `reflect.enabled: true` in config
- [x] **AC-US7-02**: `stop-reflect` returns immediately when disabled in config or no `.specweave/` exists
- [x] **AC-US7-03**: `stop-auto` validates completion gates -- checks task completion count, session age, and auto-session file
- [x] **AC-US7-04**: `stop-sync` reads `pending.jsonl`, deduplicates by event type + increment ID, syncs to external tools
- [x] **AC-US7-05**: All stop hooks return `{"decision":"approve"}` -- never block session exit regardless of errors

---

### US-008: Bash Script Removal (P1)
**Project**: specweave

**As a** SpecWeave maintainer
**I want** all bash scripts removed from the plugin hooks directory
**So that** the plugin is lean and cross-platform

**Acceptance Criteria**:
- [x] **AC-US8-01**: `hooks.json` updated to use `specweave hook <event>` commands instead of `bash .../run-hook.sh`
- [x] **AC-US8-02**: All 59 `.sh` files, 1 `.mjs` file, 2 `.cmd` files, and 1 `.ps1` file deleted from `hooks/`
- [x] **AC-US8-03**: All subdirectories deleted: `universal/`, `lib/`, `v2/` (with all nested dirs), `_archive/`, `tests/`
- [x] **AC-US8-04**: `README.md` deleted from `hooks/`
- [x] **AC-US8-05**: Only `hooks.json` remains in the `hooks/` directory

---

### US-009: Remove Project-Local Hook Copying (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** the plugin installer to stop copying hooks to `.claude/hooks/`
**So that** projects are not bloated with unused files

**Acceptance Criteria**:
- [x] **AC-US9-01**: `copyPluginSkillsToProject` in `src/utils/plugin-copier.ts` no longer creates `.claude/hooks/` directory or copies hook files
- [x] **AC-US9-02**: Skills are still copied to `.claude/skills/` correctly (no regression)
- [x] **AC-US9-03**: Lockfile entries in `vskill.lock` are still computed correctly (hash, version, timestamp)

## Non-Functional Requirements

- **Startup latency**: `specweave hook <event>` must complete within 200ms for pass-through cases (no `.specweave/` project)
- **Error safety**: No handler may throw an unhandled exception to stdout -- all errors caught and returned as safe JSON
- **Zero dependencies**: Handlers use only Node.js built-ins and existing specweave modules (no new npm packages)
- **Test coverage**: 90%+ unit test coverage per handler (TDD mode per metadata.json)

## Out of Scope

- Refactoring existing `src/core/hooks/` health check modules (HookScanner, HookHealthChecker, etc.) -- these monitor hook health and remain unchanged
- Changing the Claude Code hook protocol (stdin JSON / stdout JSON contract is fixed by Claude Code)
- Plugin scripts in `plugins/specweave/scripts/` -- these are separate from hooks and not part of this migration
- `doctor` command hook checks -- follow-up to update `hooks-checker.ts` for the new structure

## Risks

| Risk | Mitigation |
|---|---|
| Behavioral regression in migrated hooks | Port bash logic line-by-line with parity tests; run existing test scripts against new handlers |
| Claude Code hook protocol mismatch | Validate against Claude Code docs; test with actual Claude Code session |
| Startup latency regression | Dynamic imports per handler; benchmark pass-through path |
| Breaking existing installations | Ship handlers first (US-001 through US-007), switch hooks.json (US-008) in same release, test as atomic change |

## Dependencies

- Existing `src/cli/commands/detect-intent.ts` -- reused by user-prompt-submit handler (AC-US6-04)
- Existing `src/core/hooks/project-scope-guard.ts` -- reused by user-prompt-submit handler (AC-US6-03)
- Existing `src/core/hooks/types.ts` -- type definitions for hook responses
- Existing event queue at `.specweave/state/event-queue/pending.jsonl` -- post-tool-use and stop-sync share this

---
increment: 0431-http-hook-server
title: HTTP Hook Server for SpecWeave
type: feature
priority: P0
status: completed
created: 2026-03-05T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# HTTP Hook Server for SpecWeave

## Problem Statement

SpecWeave's current hook system relies on bash scripts, a file-based JSONL event queue, and a background processor daemon with a 60-second idle timeout. This architecture is fragile: bash scripts break on Windows, the file-based queue has race conditions, the processor daemon can miss events during its idle gap, and analytics are scattered across flat files. Claude Code now supports HTTP hooks natively, posting events to a URL and awaiting a JSON response. Replacing the bash/daemon system with an HTTP server built into the existing dashboard process eliminates these reliability issues while enabling real-time event visibility.

## Goals

- Replace bash command hooks with HTTP POST handlers for all 8 HTTP-capable Claude Code events
- Bridge the 9 command-only events through a Node.js command script that forwards to the same HTTP server
- Persist events in-memory with JSONL flush (no new dependencies -- no SQLite, no native modules)
- Add real-time dashboard UI pages for hook event stream, agent tracking, and task timeline
- Provide a clean migration path via `hooks.httpMode` config flag

## User Stories

### US-001: HTTP Hook Event Receiver
**Project**: specweave
**As a** developer using SpecWeave
**I want** Claude Code hook events received by an HTTP endpoint on the dashboard server
**So that** event processing is reliable, cross-platform, and does not depend on bash

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given the dashboard server is running with hooks enabled, when Claude Code sends a POST to `POST /api/hooks/:eventName`, then the server accepts the request and returns 200 within 500ms
- [x] **AC-US1-02**: Given a PreToolUse event is received, when the handler evaluates blocking rules, then the response includes `hookSpecificOutput` with `permissionDecision: "allow"` or `"deny"` and a `permissionDecisionReason`
- [x] **AC-US1-03**: Given a PostToolUse, Stop, SubagentStop, TaskCompleted, UserPromptSubmit, PostToolUseFailure, or PermissionRequest event is received, when no blocking rule applies, then the server returns 200 with empty body
- [x] **AC-US1-04**: Given a malformed or unknown event type is POSTed, when the server processes the request, then it returns 400 with a JSON error message and does not crash
- [x] **AC-US1-05**: Given the server receives an event, when processing completes, then a TypeScript handler function (not a bash script) executes the event-specific logic

---

### US-002: In-Memory Event Store with JSONL Persistence
**Project**: specweave
**As a** developer
**I want** hook events persisted in-memory and flushed to JSONL files
**So that** I can query recent analytics, agent activity, and task completions without adding native npm dependencies

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given a hook event is received, when the handler processes it, then the event is stored in an in-memory Map/array keyed by session ID and also appended to `.specweave/state/hooks/events.jsonl`
- [x] **AC-US2-02**: Given the dashboard server starts, when it initializes, then it reads existing JSONL files from `.specweave/state/hooks/` to hydrate the in-memory store (events.jsonl, agents.jsonl)
- [x] **AC-US2-03**: Given events.jsonl exceeds 10MB, when a new event is appended, then the file is rotated (renamed with timestamp suffix) and a new file is created
- [x] **AC-US2-04**: Given the server starts, when it scans JSONL files, then files older than 30 days are deleted
- [x] **AC-US2-05**: Given the dashboard server shuts down gracefully, when the shutdown signal is received, then all in-memory events not yet flushed are written to JSONL before exit

---

### US-003: Dashboard Server Auto-Start on Session Begin
**Project**: specweave
**As a** developer
**I want** the dashboard server to auto-start when a Claude Code session begins
**So that** the HTTP hook endpoint is available before the first hook event fires

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given `hooks.httpMode: true` in `.specweave/config.json`, when a Claude Code SessionStart command hook fires, then a Node.js command-bridge script starts the dashboard server in the background if not already running
- [x] **AC-US3-02**: Given the dashboard server is already running on the configured port, when the SessionStart hook fires, then the command-bridge detects the existing instance (via port check) and does not start a duplicate
- [x] **AC-US3-03**: Given `hooks.httpMode: true`, when the developer runs `specweave dashboard --hooks`, then the server starts with hook routes enabled on the same port as the dashboard
- [x] **AC-US3-04**: Given the server auto-starts, when it is ready to accept connections, then it writes the port and PID to `.specweave/state/hooks/server.pid` for discovery by the command-bridge

---

### US-004: Command-Bridge for Command-Only Events
**Project**: specweave
**As a** developer
**I want** the 9 command-only hook events (SessionStart, SessionEnd, Notification, SubagentStart, ConfigChange, PreCompact, TeammateIdle) forwarded to the HTTP server
**So that** all events flow through a unified TypeScript handler pipeline

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given a command-only event fires (SessionStart, SessionEnd, Notification, SubagentStart, ConfigChange, PreCompact, TeammateIdle), when the command-bridge script runs, then it reads the event payload from stdin and POSTs it to `http://localhost:{port}/api/hooks/{eventName}`
- [x] **AC-US4-02**: Given the dashboard server is not running, when the command-bridge attempts to POST, then it fails silently (exit 0) without blocking Claude Code
- [x] **AC-US4-03**: Given `hooks.httpMode: true`, when `specweave hooks generate-settings` runs, then it produces a valid `.claude/settings.json` hooks section with HTTP transport for the 8 supported events and command transport (pointing to the command-bridge script) for the remaining 9

---

### US-005: TypeScript Event Handlers Replacing Bash
**Project**: specweave
**As a** developer
**I want** TypeScript handler functions for all event types replacing the existing bash handler scripts
**So that** event processing is type-safe, testable, and works on all platforms

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given an increment lifecycle event (created/done/archived/reopened) arrives via hook, when the handler processes it, then it executes the equivalent logic of living-specs-handler.sh, status-line-handler.sh, project-bridge-handler.sh, and github-sync-handler.sh
- [x] **AC-US5-02**: Given a spec.updated event arrives, when the handler processes it, then it executes the equivalent logic of living-docs-handler.sh, ac-validation-handler.sh, and github-sync-handler.sh
- [x] **AC-US5-03**: Given a SubagentStart or SubagentStop event arrives, when the handler processes it, then it updates the in-memory agent tracking store with agent_id, agent_type, session_id, started_at/stopped_at, and duration_ms
- [x] **AC-US5-04**: Given a TaskCompleted event arrives, when the handler processes it, then it records the completion in the in-memory store and appends to `.specweave/state/hooks/events.jsonl`
- [x] **AC-US5-05**: Given any handler throws an error, when the error occurs during event processing, then the error is logged to `.specweave/logs/hooks.log` and the HTTP response is still returned (never blocks CC)

---

### US-006: HooksPage Dashboard UI
**Project**: specweave
**As a** developer
**I want** a HooksPage in the dashboard showing a real-time event stream
**So that** I have visibility into Claude Code's behavior during a session

**Acceptance Criteria**:
- [x] **AC-US6-01**: Given the dashboard is open, when hook events arrive, then the HooksPage displays them in a scrollable reverse-chronological timeline updated in real-time via SSE
- [x] **AC-US6-02**: Given the HooksPage is displayed, when the user selects a filter (event type, session ID, or time range), then only matching events are shown
- [x] **AC-US6-03**: Given consecutive events of the same type occur (e.g., repeated PostToolUse on Edit), when displayed in the timeline, then they are collapsed into a summary row showing count and expandable on click
- [x] **AC-US6-04**: Given an event resulted in a block/deny decision, when displayed in the timeline, then it is visually highlighted with a distinct style (red/warning)

---

### US-007: AgentsPage Dashboard UI
**Project**: specweave
**As a** developer
**I want** an AgentsPage in the dashboard showing subagent lifecycle
**So that** I can track agent activity and performance across sessions

**Acceptance Criteria**:
- [x] **AC-US7-01**: Given agents have been tracked via SubagentStart/SubagentStop events, when the AgentsPage loads, then it displays a table with columns: agent_id, agent_type, session_id, started_at, stopped_at, duration_ms
- [x] **AC-US7-02**: Given an agent is currently running (SubagentStart received, no SubagentStop yet), when the AgentsPage displays it, then the status shows "running" with a live duration counter
- [x] **AC-US7-03**: Given multiple sessions have agent data, when the user filters by session ID, then only agents from that session are displayed
- [x] **AC-US7-04**: Given new SubagentStart/SubagentStop events arrive, when the AgentsPage is open, then the table updates in real-time via SSE without page reload

---

### US-008: Settings Generator and Migration Config
**Project**: specweave
**As a** developer
**I want** documentation and tooling updated to reflect the HTTP hook architecture
**So that** I can enable, configure, and troubleshoot the new hook system

**Acceptance Criteria**:
- [x] **AC-US8-01**: Given `hooks.httpMode: true` in config.json, when `specweave hooks generate-settings` runs, then it writes a valid `.claude/settings.json` hooks block with HTTP URLs for the 8 supported events and command paths for the 9 command-only events
- [x] **AC-US8-02**: Given `hooks.httpMode: false` (or absent), when hooks are evaluated, then the existing bash hook system operates unchanged with no behavioral difference
- [x] **AC-US8-03**: Given a developer upgrades specweave, when config.json does not contain `hooks.httpMode`, then the default is `false` (opt-in for existing installs)
- [x] **AC-US8-04**: Given `hooks.httpMode: true`, when `specweave hooks status` runs, then it reports whether the dashboard server is running, the hook endpoint URL, and the count of events received in the current session

## Out of Scope

- **SQLite or any native npm dependency**: All persistence uses in-memory state and JSONL files only
- **External network access**: The hook server binds to localhost only; no remote connections
- **Parent-child agent tracking**: CC hook payloads do not expose subagent hierarchy; only flat agent start/stop is tracked
- **Custom user-defined hook handlers**: Only SpecWeave's built-in handlers are supported in this increment
- **Task timeline page**: Deferred to a follow-up increment; task data is persisted but no dedicated UI page yet
- **Dual-write migration**: When `hooks.httpMode` is toggled, it is a clean switch; old and new do not run simultaneously

## Technical Notes

### Dependencies
- No new npm packages. Uses native Node.js `http` module (already in dashboard server), `fs` for JSONL, and in-memory `Map`/`Array` for event storage
- Existing dashboard infrastructure: `Router`, `SSEManager`, `DashboardServer`, React client with Vite

### Constraints
- Hook HTTP response must complete within 500ms to avoid CC timeout
- JSONL files must be append-only during writes (no full-file rewrites)
- Dashboard server must remain a single process (no child process spawning for handlers)
- Command-bridge script must be a single self-contained Node.js file that can run via `node` (no build step required at hook invocation time)

### Architecture Decisions
- **Same process as dashboard**: Hook routes are added to the existing `DashboardServer` class via `Router.post()`. No separate server or port
- **In-memory + JSONL**: Events held in `Map<sessionId, HookEvent[]>` during server lifetime. Flushed to `.specweave/state/hooks/events.jsonl` on each event (append) and on shutdown (drain)
- **Hybrid transport**: 8 events via HTTP hooks (CC posts directly), 9 events via command hooks + command-bridge (Node.js script does `http.request` to localhost)
- **Config flag**: `hooks.httpMode` in `.specweave/config.json` controls which hook registration is active. `specweave hooks generate-settings` writes the appropriate `.claude/settings.json`

### CC HTTP Hook Response Format
- **Allow (default)**: Return 200 with empty body
- **Block PreToolUse**: Return 200 with `{ "hookSpecificOutput": { "hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "..." } }`
- **Block Stop/PostToolUse**: Return 200 with `{ "decision": "block", "reason": "..." }`
- **Error**: Non-2xx response is non-blocking; CC continues normally

### File Locations
- Hook event log: `.specweave/state/hooks/events.jsonl`
- Agent tracking: `.specweave/state/hooks/agents.jsonl`
- Server PID: `.specweave/state/hooks/server.pid`
- Hook processing log: `.specweave/logs/hooks.log`
- Legacy analytics (continues): `.specweave/state/analytics/events.jsonl`

## Success Metrics

- **Reliability**: Zero missed hook events when dashboard server is running (vs. current 60s idle gap)
- **Cross-platform**: Hook system works identically on macOS, Linux, and Windows without bash
- **Performance**: Hook HTTP response p99 under 200ms
- **Adoption**: `hooks.httpMode: true` becomes the default for new installs within one release cycle
- **Visibility**: Developers use HooksPage and AgentsPage during active Claude Code sessions to observe behavior

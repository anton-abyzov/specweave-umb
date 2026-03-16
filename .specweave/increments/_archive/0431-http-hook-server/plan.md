# Architecture Plan: HTTP Hook Server for SpecWeave

## Overview

Replace SpecWeave's bash-script hook system with an HTTP server built into the existing `DashboardServer` process. Claude Code posts hook events as HTTP requests; the server processes them in TypeScript, stores them in-memory with JSONL persistence, and broadcasts updates to the dashboard UI via SSE.

## Architecture Decision: Extend DashboardServer (Not a Separate Process)

**Decision**: Add hook routes directly to `DashboardServer` via `Router.post()`. No separate server, port, or process.

**Rationale**:
- The dashboard server already has the Router, SSE, and file-watcher infrastructure
- A single process means zero IPC overhead for broadcasting hook events to the UI
- The `DashboardServerOptions` can gain an optional `hooksEnabled: boolean` flag
- The server already binds to localhost with CORS restrictions matching what hooks need

**Rejected Alternative**: Separate hook server process. Would require IPC for SSE broadcast, additional port management, and more complex lifecycle (two PIDs to track).

## Component Architecture

```
Claude Code                        DashboardServer (single process)
-----------                        --------------------------------
                                   ┌──────────────────────────────┐
HTTP events (8)                    │  Router                      │
  POST /api/hooks/:event  ──────► │    /api/hooks/:event (POST)  │
                                   │    /api/hooks/events (GET)   │
Command events (9)                 │    /api/hooks/agents (GET)   │
  command-bridge.mjs ─────────────►│    /api/hooks/status (GET)   │
  (reads stdin, POSTs to localhost)│                              │
                                   │  HookEventRouter             │
                                   │    ├─ PreToolUse handler     │
                                   │    ├─ PostToolUse handler    │
                                   │    ├─ UserPromptSubmit       │
                                   │    ├─ Stop handler           │
                                   │    ├─ SessionStart handler   │
                                   │    ├─ SessionEnd handler     │
                                   │    └─ ... (per event type)   │
                                   │                              │
                                   │  HookEventStore              │
                                   │    ├─ Map<sessionId, events> │
                                   │    ├─ agents Map             │
                                   │    ├─ JSONL flush (append)   │
                                   │    └─ rotation (>10MB)       │
                                   │                              │
                                   │  SSEManager                  │
                                   │    └─ broadcast('hook-event')│
                                   └──────────────────────────────┘
```

## New SSE Event Types

Add to `SSEEventType` union in `src/dashboard/types.ts`:

```
'hook-event'      -- individual hook event received
'hook-agent'      -- agent start/stop lifecycle update
```

The SSE client context (`SSEContext.tsx`) already dynamically handles event types via its `EVENT_TYPES` array -- append these two entries.

## Component Breakdown

### C1: HookEventStore (`src/dashboard/server/hooks/hook-event-store.ts`)

In-memory store with JSONL persistence. Zero npm dependencies.

```
HookEventStore
─────────────────────────────────────────────────────
Fields:
  eventsBySession: Map<string, HookEvent[]>
  agents: Map<string, AgentRecord>
  eventsFilePath: string    (.specweave/state/hooks/events.jsonl)
  agentsFilePath: string    (.specweave/state/hooks/agents.jsonl)
  totalEventCount: number

Methods:
  constructor(projectRoot: string)
  hydrate(): void                     -- read JSONL on startup
  addEvent(event: HookEvent): void    -- store + append JSONL + check rotation
  updateAgent(data: AgentUpdate): void
  getEvents(opts: {sessionId?, eventType?, limit?}): HookEvent[]
  getAgents(opts: {sessionId?, status?}): AgentRecord[]
  getStats(): {totalEvents, activeSessions, activeAgents}
  flush(): void                       -- drain unflushed events on shutdown
  cleanup(): void                     -- delete JSONL files older than 30 days
```

**JSONL rotation**: When `events.jsonl` exceeds 10MB (checked via `fs.statSync` before each append), rename to `events-{ISO-timestamp}.jsonl` and create a fresh file. Use `fs.appendFileSync` for writes -- no full-file rewrites.

**Startup hydration**: Read `events.jsonl` + `agents.jsonl` line-by-line via `readline.createInterface` (same pattern as existing `ActivityStream.readJsonlAsActivity`). Skip malformed lines.

**30-day cleanup**: On startup, scan `.specweave/state/hooks/` for `events-*.jsonl` files. Parse the timestamp from the filename. Delete files older than 30 days.

### C2: HookEventRouter (`src/dashboard/server/hooks/hook-event-router.ts`)

Maps event names to handler functions. Accepts the parsed request body and returns the HTTP response payload.

```
HookEventRouter
─────────────────────────────────────────────────────
Fields:
  handlers: Map<string, HookHandler>
  store: HookEventStore
  logPath: string           (.specweave/logs/hooks.log)

Types:
  HookHandler = (payload: HookPayload) => Promise<HookResponse>
  HookPayload = { eventName: string; body: unknown; sessionId: string }
  HookResponse = { status: number; body?: unknown }

Methods:
  constructor(store: HookEventStore, projectRoot: string)
  register(eventName: string, handler: HookHandler): void
  handle(eventName: string, body: unknown): Promise<HookResponse>
```

**Handler registration** happens in the constructor. Each event type gets a dedicated handler function (see C3).

**Error isolation**: Every handler call is wrapped in try/catch. On error: log to `.specweave/logs/hooks.log` via `appendLog`, return 200 with empty body (never block Claude Code).

### C3: Event Handlers (`src/dashboard/server/hooks/handlers/`)

One file per logical handler group. Each exports a function matching the `HookHandler` signature.

```
handlers/
  pre-tool-use.ts        -- AC-US1-02: blocking rules, permissionDecision
  post-tool-use.ts       -- AC-US1-03: file-change detection, EDA event emit
  stop.ts                -- stop-reflect, stop-auto, stop-sync logic (TS ports)
  session-lifecycle.ts   -- SessionStart, SessionEnd
  subagent-lifecycle.ts  -- SubagentStart, SubagentStop -> agent tracking
  task-completed.ts      -- TaskCompleted -> store + JSONL
  user-prompt-submit.ts  -- user prompt analysis (port of user-prompt-submit.sh)
  passthrough.ts         -- PostToolUseFailure, PermissionRequest, Notification,
                            ConfigChange, PreCompact, TeammateIdle -> store only
```

**EDA event routing** (replaces processor.ts bash routing):

The existing `processor.ts` routes internal SpecWeave events (increment.created, spec.updated, etc.) to bash handlers. In the new system:
- `post-tool-use.ts` detects file writes to `.specweave/increments/` and emits internal events
- Internal events are processed by TypeScript equivalents of the bash handlers
- The existing bash handlers (`living-specs-handler.sh`, `github-sync-handler.sh`, etc.) are NOT ported in this increment. Instead, the PostToolUse handler calls the bash scripts directly via `child_process.execFile` for backward compatibility (same mechanism the processor daemon uses internally)
- `processor.ts` is a standalone daemon, NOT an importable library — do not attempt to import from it
- Full TypeScript ports of each bash handler happen in follow-up increments

**PreToolUse blocking rules** (AC-US1-02):
- Port the logic from `plugins/specweave/hooks/v2/dispatchers/pre-tool-use.sh`
- Return `{ hookSpecificOutput: { hookEventName: "PreToolUse", permissionDecision: "allow"|"deny", permissionDecisionReason: "..." } }`
- Skill-chain guard, increment-existence guard, and Write/Edit validators

### C4: Hook Route Registration (`DashboardServer.registerHookRoutes()`)

New private method on `DashboardServer`, called from `registerRoutes()` when hooks are enabled.

```typescript
private registerHookRoutes(): void {
  // Main hook endpoint -- Claude Code POSTs here
  this.router.post('/api/hooks/:event', async (req, res, params) => {
    const body = await readBody(req);
    const result = await this.hookRouter.handle(params.event, body);
    sendJson(res, result.body ?? {}, result.status);
    // Broadcast to SSE clients
    this.sseManager.broadcast('hook-event', {
      eventName: params.event,
      timestamp: new Date().toISOString(),
      ...summarizeForSSE(body),
    });
  });

  // Query endpoints for dashboard UI
  this.router.get('/api/hooks/events', async (req, res) => { ... });
  this.router.get('/api/hooks/agents', async (req, res) => { ... });
  this.router.get('/api/hooks/status', async (req, res) => { ... });
}
```

**Route ordering**: The POST route uses `:event` param. The GET routes use literal paths (`events`, `agents`, `status`). Since Router matches routes in registration order and POST vs GET are different methods, there is no conflict. Register GET routes first to be safe.

### C5: Command Bridge (`src/hooks/command-bridge.mjs`)

A single self-contained Node.js script (ES module, `.mjs` extension for no-build execution). Used for the 9 command-only events that Claude Code cannot send via HTTP.

```
#!/usr/bin/env node
// command-bridge.mjs
// Reads hook payload from stdin, POSTs to http://localhost:{port}/api/hooks/{event}
// Discovers port from .specweave/state/hooks/server.pid
// Fails silently (exit 0) if server unreachable
```

**Port discovery**: Read `.specweave/state/hooks/server.pid` (JSON: `{ port, pid }`). If file missing or server unreachable, exit 0.

**Event name**: Passed as first argument: `node command-bridge.mjs SessionStart`

**Stdin handling**: Read all stdin, parse as JSON, POST to `http://localhost:{port}/api/hooks/{eventName}` with the body. Print any response body to stdout (Claude Code may read it for command hooks that produce output).

**No build step**: The `.mjs` extension means Node.js treats it as ESM natively. Uses only `http`, `fs`, `path` from Node.js stdlib. No TypeScript, no imports from the specweave package.

### C6: Server Auto-Start and PID Management

**Auto-start flow** (AC-US3-01):
1. SessionStart command hook fires
2. `command-bridge.mjs SessionStart` runs
3. Bridge checks `.specweave/state/hooks/server.pid`
4. If no PID file or process not running: spawn `specweave dashboard --hooks` in background via `child_process.spawn` with `detached: true`
5. Wait up to 3 seconds for the PID file to appear (poll every 200ms)
6. POST the SessionStart payload to the server

**PID file** (`.specweave/state/hooks/server.pid`):
```json
{ "port": 8340, "pid": 12345, "startedAt": "2026-03-05T..." }
```

Written by `DashboardServer.start()` when `hooksEnabled: true`. Deleted by `DashboardServer.stop()`.

**Duplicate detection** (AC-US3-02): Before starting, check if port is in use via `net.connect`. If connection succeeds, the server is already running -- skip start.

### C7: Settings Generator (`src/hooks/generate-settings.ts`)

New CLI command: `specweave hooks generate-settings`

Reads `hooks.httpMode` from `.specweave/config.json`. If `true`, generates `.claude/settings.json` hooks section:

**HTTP events** (8 types supported by CC HTTP hooks):
```json
{
  "PreToolUse": [{ "type": "http", "url": "http://localhost:{port}/api/hooks/PreToolUse", "matcher": "Write|Edit" }],
  "PostToolUse": [{ "type": "http", "url": "http://localhost:{port}/api/hooks/PostToolUse" }],
  "Stop": [{ "type": "http", "url": "http://localhost:{port}/api/hooks/Stop" }],
  "SubagentStop": [{ "type": "http", "url": "http://localhost:{port}/api/hooks/SubagentStop" }],
  "TaskCompleted": [{ "type": "http", "url": "http://localhost:{port}/api/hooks/TaskCompleted" }],
  "UserPromptSubmit": [{ "type": "http", "url": "http://localhost:{port}/api/hooks/UserPromptSubmit" }],
  "PostToolUseFailure": [{ "type": "http", "url": "http://localhost:{port}/api/hooks/PostToolUseFailure" }],
  "PermissionRequest": [{ "type": "http", "url": "http://localhost:{port}/api/hooks/PermissionRequest" }]
}
```

**Command events** (9 types, forwarded via bridge):
```json
{
  "SessionStart": [{ "type": "command", "command": "node /path/to/command-bridge.mjs SessionStart" }],
  "SessionEnd": [{ "type": "command", "command": "node /path/to/command-bridge.mjs SessionEnd" }],
  "Notification": [{ "type": "command", "command": "node /path/to/command-bridge.mjs Notification" }],
  "SubagentStart": [{ "type": "command", "command": "node /path/to/command-bridge.mjs SubagentStart" }],
  "ConfigChange": [{ "type": "command", "command": "node /path/to/command-bridge.mjs ConfigChange" }],
  "PreCompact": [{ "type": "command", "command": "node /path/to/command-bridge.mjs PreCompact" }],
  "TeammateIdle": [{ "type": "command", "command": "node /path/to/command-bridge.mjs TeammateIdle" }]
}
```

### C8: HooksPage (`src/dashboard/client/src/pages/HooksPage.tsx`)

Dashboard page showing real-time hook event stream.

**Data flow**:
1. Initial load: `GET /api/hooks/events?limit=200` via `useApi`
2. Real-time updates: Subscribe to `hook-event` SSE type via `useSSEEvent`
3. Prepend new events to the list (reverse chronological)

**UI components**:
- Filter bar: event type dropdown, session ID text input, time range picker
- Event timeline: scrollable list with timestamp, event type badge, tool name, session ID
- Collapsible groups: consecutive same-type events collapse into summary row (count + expand)
- Deny/block highlighting: red-tinted row for events with `permissionDecision: "deny"`
- Event detail panel: click a row to see full JSON payload in a side panel

**SSE integration**: Add `'hook-event'` and `'hook-agent'` to the `EVENT_TYPES` array in `SSEContext.tsx`.

### C9: AgentsPage (`src/dashboard/client/src/pages/AgentsPage.tsx`)

Dashboard page showing subagent lifecycle.

**Data flow**:
1. Initial load: `GET /api/hooks/agents` via `useApi`
2. Real-time updates: Subscribe to `hook-agent` SSE type via `useSSEEvent`

**UI components**:
- Agent table: columns for agent_id, agent_type, session_id, started_at, stopped_at, duration_ms
- Running indicator: green "running" badge with live duration counter (via `setInterval`)
- Session filter: dropdown or text input to filter by session ID
- Summary stats: total agents, currently running, average duration

## Type Definitions

New types in `src/dashboard/types.ts`:

```typescript
// Hook event types (Claude Code HTTP hooks)
export type CCHookEventName =
  | 'PreToolUse' | 'PostToolUse' | 'Stop' | 'SubagentStop'
  | 'TaskCompleted' | 'UserPromptSubmit' | 'PostToolUseFailure'
  | 'PermissionRequest'
  // Command-only (forwarded via bridge)
  | 'SessionStart' | 'SessionEnd' | 'Notification' | 'SubagentStart'
  | 'ConfigChange' | 'PreCompact' | 'TeammateIdle';

export interface HookEvent {
  id: string;             // uuid
  eventName: CCHookEventName;
  sessionId: string;
  timestamp: string;      // ISO 8601
  payload: unknown;       // raw CC payload
  result?: {
    decision?: 'allow' | 'deny' | 'approve' | 'block';
    reason?: string;
  };
  durationMs?: number;    // handler processing time
}

export interface AgentRecord {
  agentId: string;
  agentType: string;
  sessionId: string;
  startedAt: string;
  stoppedAt?: string;
  durationMs?: number;
}
```

## Data Flow: Hook Event Lifecycle

```
1. CC sends POST /api/hooks/PreToolUse
2. Router matches route, readBody() parses JSON
3. hookRouter.handle("PreToolUse", body) called
4. PreToolUse handler evaluates blocking rules
5. Handler returns { status: 200, body: { hookSpecificOutput: ... } }
6. Event stored in HookEventStore (in-memory + JSONL append)
7. SSE broadcast: hook-event { eventName, sessionId, result, ... }
8. HTTP response sent to Claude Code
9. HooksPage receives SSE, prepends event to timeline
```

**Timing budget** (AC-US1-01 -- response within 500ms):
- readBody: ~5ms (typical payload <10KB)
- handler logic: ~10-50ms (file reads, rule evaluation)
- JSONL append: ~1-5ms (single fs.appendFileSync)
- SSE broadcast: ~1ms (non-blocking writes)
- Total: well under 500ms even with cold file I/O

## Configuration

In `.specweave/config.json`:

```json
{
  "hooks": {
    "httpMode": false,
    "port": 8340
  }
}
```

- `httpMode: false` (default) -- existing bash hook system, no behavioral change
- `httpMode: true` -- HTTP hooks enabled, dashboard server starts with hook routes
- `port` -- defaults to the dashboard server port (same process)

## File Locations Summary

New files to create:
```
src/dashboard/server/hooks/hook-event-store.ts
src/dashboard/server/hooks/hook-event-router.ts
src/dashboard/server/hooks/handlers/pre-tool-use.ts
src/dashboard/server/hooks/handlers/post-tool-use.ts
src/dashboard/server/hooks/handlers/stop.ts
src/dashboard/server/hooks/handlers/session-lifecycle.ts
src/dashboard/server/hooks/handlers/subagent-lifecycle.ts
src/dashboard/server/hooks/handlers/task-completed.ts
src/dashboard/server/hooks/handlers/user-prompt-submit.ts
src/dashboard/server/hooks/handlers/passthrough.ts
src/hooks/command-bridge.mjs
src/hooks/generate-settings.ts
src/dashboard/client/src/pages/HooksPage.tsx
src/dashboard/client/src/pages/AgentsPage.tsx
```

Files to modify:
```
src/dashboard/server/dashboard-server.ts   -- add registerHookRoutes(), hooksEnabled option, PID file, shutdown flush
src/dashboard/types.ts                     -- add HookEvent, AgentRecord, CCHookEventName, SSE types
src/dashboard/client/src/App.tsx           -- add HooksPage and AgentsPage routes
src/dashboard/client/src/components/layout/Sidebar.tsx  -- add Hooks and Agents nav items
src/dashboard/client/src/contexts/SSEContext.tsx         -- add hook-event, hook-agent to EVENT_TYPES
```

## Migration Path

1. Default: `hooks.httpMode` absent or `false` -- zero change, bash hooks work as before
2. Opt-in: Set `hooks.httpMode: true`, run `specweave hooks generate-settings`
3. The settings generator writes `.claude/settings.json` with HTTP URLs for 8 events, command bridge for 9
4. On next CC session start, the command-bridge auto-starts the dashboard server
5. All events flow through the HTTP server from that point

**No dual-write**: When `httpMode` is toggled, it is a clean switch. The old bash hooks and the new HTTP hooks do not run simultaneously.

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Handler takes >500ms, blocking CC | All handlers have internal 400ms timeout. If exceeded, return 200 immediately and process async |
| JSONL file corruption on crash | Append-only writes (no full rewrites). Startup hydration skips malformed lines |
| Port conflict with other services | PID file includes port. Settings generator reads port from config |
| Dashboard server not running when hook fires | Command-bridge fails silently (exit 0). CC continues normally on non-2xx |
| Large event volume fills disk | 10MB rotation + 30-day cleanup. In-memory store caps at 10,000 events per session |

## Domain Skill Recommendation

This increment is entirely within the **specweave** repository (Node.js, TypeScript, React). The implementation involves:
- **Backend**: Extending the existing Node.js HTTP server (no framework -- raw `http` module). No domain skill needed; the patterns are already established in `dashboard-server.ts`.
- **Frontend**: Two new React pages following the exact patterns of existing pages (e.g., `ActivityPage.tsx`, `ErrorsPage.tsx`). Uses `useApi`, `useSSEEvent`, TailwindCSS. No domain skill needed; copy the established component patterns.

No domain skills to chain -- the existing codebase patterns provide sufficient guidance.

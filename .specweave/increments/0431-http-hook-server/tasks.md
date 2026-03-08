---
increment: 0431-http-hook-server
title: "HTTP Hook Server for SpecWeave"
generated_by: sw:test-aware-planner
coverage_target: 90
by_user_story:
  US-001: [T-001, T-002, T-003]
  US-002: [T-004, T-005, T-006]
  US-003: [T-007, T-008]
  US-004: [T-009, T-010]
  US-005: [T-011, T-012, T-013]
  US-006: [T-014, T-015]
  US-007: [T-016, T-017]
  US-008: [T-018, T-019]
---

# Tasks: HTTP Hook Server for SpecWeave

## User Story: US-001 - HTTP Hook Event Receiver

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Tasks**: 3 total, 3 completed

---

### T-001: Add HookEvent and AgentRecord types to types.ts

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-05
**Status**: [x] completed

**Test Plan**:
- **Given** `src/dashboard/types.ts` is updated with hook-related types
- **When** TypeScript compiles the project
- **Then** all new types are valid, exported, and importable from other modules without errors

**Test Cases**:
1. **Unit**: `src/dashboard/server/hooks/__tests__/types.test.ts`
   - `testCCHookEventNameUnion()`: Verify the union covers all 17 event names (8 HTTP + 9 command)
   - `testHookEventShape()`: Construct a `HookEvent` object and assert all required fields type-check
   - `testAgentRecordShape()`: Construct an `AgentRecord` and assert required vs optional fields
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/dashboard/types.ts` in `repositories/anton-abyzov/specweave/`
2. Add `CCHookEventName` union type with all 17 event names
3. Add `HookEvent` interface: `id`, `eventName`, `sessionId`, `timestamp`, `payload`, optional `result`, optional `durationMs`
4. Add `AgentRecord` interface: `agentId`, `agentType`, `sessionId`, `startedAt`, optional `stoppedAt`, optional `durationMs`
5. Add `'hook-event'` and `'hook-agent'` to the `SSEEventType` union
6. Run `npx tsc --noEmit` from the repo root to confirm no type errors

---

### T-002: Implement HookEventRouter with handler registration and error isolation

**User Story**: US-001
**Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [x] completed

**Test Plan**:
- **Given** a `HookEventRouter` instance with registered handlers
- **When** `handle(eventName, body)` is called
- **Then** the matching handler is invoked, its response returned, and any thrown error is caught and logged without re-throwing

**Test Cases**:
1. **Unit**: `src/dashboard/server/hooks/__tests__/hook-event-router.test.ts`
   - `testHandleKnownEventCallsHandler()`: Register a stub handler, call `handle`, assert stub called and result returned
   - `testHandleUnknownEventReturns400()`: Call `handle` with an unregistered event name, assert `{ status: 400, body: { error: ... } }`
   - `testHandlerErrorIsolation()`: Register a handler that throws, call `handle`, assert 200 returned and log file written
   - `testPreToolUseReturnsPermissionDecision()`: Register a PreToolUse handler that returns deny, assert `hookSpecificOutput.permissionDecision === "deny"`
   - **Coverage Target**: 95%

**Implementation**:
1. Create `src/dashboard/server/hooks/hook-event-router.ts`
2. Define `HookHandler`, `HookPayload`, `HookResponse` types in this file
3. Implement `HookEventRouter` class with `handlers: Map<string, HookHandler>`, `store`, `logPath` fields
4. Implement `register(eventName, handler)` method
5. Implement `handle(eventName, body)`: extract `sessionId` from body, call registered handler in try/catch
6. On catch: append error to `logPath` via `fs.appendFileSync`, return `{ status: 200, body: {} }`
7. On unknown event: return `{ status: 400, body: { error: 'Unknown event type: ...' } }`
8. Run unit tests: `npx vitest run src/dashboard/server/hooks/__tests__/hook-event-router.test.ts`

---

### T-003: Register hook routes on DashboardServer and wire SSE broadcast

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-03, AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** the dashboard server is started with `hooksEnabled: true`
- **When** a POST to `/api/hooks/PreToolUse` is made with a valid JSON body
- **Then** it returns 200 within 500ms, and SSE clients receive a `hook-event` broadcast

**Test Cases**:
1. **Integration**: `src/dashboard/server/hooks/__tests__/hook-routes.test.ts`
   - `testPostKnownEventReturns200()`: Start test server with hooks enabled, POST valid body, assert 200
   - `testPostUnknownEventReturns400()`: POST to `/api/hooks/UnknownEvent`, assert 400 with JSON error
   - `testPostMalformedBodyReturns400()`: POST non-JSON body, assert 400
   - `testResponseWithin500ms()`: Measure round-trip time on POST, assert under 500ms
   - `testSSEBroadcastOnHookEvent()`: Connect SSE client, POST event, assert `hook-event` message received
   - **Coverage Target**: 90%

**Implementation**:
1. Add `hooksEnabled?: boolean` to `DashboardServerOptions` in `dashboard-server.ts`
2. Add `private hookEventRouter: HookEventRouter` field (initialized when `hooksEnabled`)
3. Add `private registerHookRoutes(): void` method — GET routes first, then POST `:event` route
4. In the POST route: `readBody`, call `hookRouter.handle`, `sendJson`, then `sseManager.broadcast('hook-event', summarizePayload)`
5. Add GET `/api/hooks/events`, `/api/hooks/agents`, `/api/hooks/status` query endpoints
6. Call `registerHookRoutes()` from `registerRoutes()` when `hooksEnabled` is true
7. Run integration tests

---

## User Story: US-002 - In-Memory Event Store with JSONL Persistence

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Tasks**: 3 total, 3 completed

---

### T-004: Implement HookEventStore with in-memory Map and JSONL append

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-03, AC-US2-05
**Status**: [x] completed

**Test Plan**:
- **Given** a `HookEventStore` instance with a temp directory
- **When** `addEvent(event)` is called
- **Then** the event is stored in the in-memory Map keyed by sessionId AND appended as a JSONL line to `events.jsonl`

**Test Cases**:
1. **Unit**: `src/dashboard/server/hooks/__tests__/hook-event-store.test.ts`
   - `testAddEventInMemoryStorage()`: Call `addEvent`, assert event appears in `getEvents({ sessionId })`
   - `testAddEventJSONLAppend()`: Call `addEvent` twice, read `events.jsonl`, assert two valid JSON lines
   - `testJSONLRotationAt10MB()`: Mock `fs.statSync` to return size > 10MB, call `addEvent`, assert old file renamed and new file created
   - `testFlushOnShutdown()`: Call `flush()`, assert all pending events written
   - `testGetEventsFilter()`: Add events with two sessionIds, filter by one, assert correct subset returned
   - **Coverage Target**: 95%

**Implementation**:
1. Create `src/dashboard/server/hooks/hook-event-store.ts`
2. Define fields: `eventsBySession: Map<string, HookEvent[]>`, `agents: Map<string, AgentRecord>`, `eventsFilePath`, `agentsFilePath`, `totalEventCount`
3. Implement `addEvent(event)`: push to `eventsBySession`, call `appendJSONL`, check rotation
4. Implement `appendJSONL(filePath, record)`: use `fs.appendFileSync` with `\n` delimiter
5. Implement rotation: if `fs.statSync(eventsFilePath).size > 10_485_760`, rename to `events-{Date.now()}.jsonl`, reset file
6. Implement `getEvents(opts)`: filter by `sessionId`, `eventType`, apply `limit`
7. Implement `getAgents(opts)`: filter by `sessionId`, `status` (running = no `stoppedAt`)
8. Implement `getStats()`: compute `totalEvents`, `activeSessions`, `activeAgents`
9. Implement `flush()`: write any buffered data synchronously
10. Run unit tests

---

### T-005: Implement JSONL hydration on server start and 30-day cleanup

**User Story**: US-002
**Satisfies ACs**: AC-US2-02, AC-US2-04
**Status**: [x] completed

**Test Plan**:
- **Given** `events.jsonl` and `agents.jsonl` contain valid JSON lines from a previous session
- **When** `hydrate()` is called on a fresh `HookEventStore` instance
- **Then** all events and agents are loaded into the in-memory Maps, and JSONL files older than 30 days are deleted

**Test Cases**:
1. **Unit**: `src/dashboard/server/hooks/__tests__/hook-event-store.test.ts` (extended)
   - `testHydrateLoadsEvents()`: Write 5 JSON lines to temp `events.jsonl`, call `hydrate()`, assert 5 events in store
   - `testHydrateSkipsMalformedLines()`: Include one invalid JSON line, assert other 4 loaded without throw
   - `testHydrateLoadsAgents()`: Write 2 agent records to `agents.jsonl`, assert both in `agents` Map
   - `testCleanupDeletesOldFiles()`: Create `events-{30+ days ago timestamp}.jsonl`, call `cleanup()`, assert file deleted
   - `testCleanupKeepsRecentFiles()`: Create `events-{5 days ago timestamp}.jsonl`, call `cleanup()`, assert file retained
   - **Coverage Target**: 90%

**Implementation**:
1. Add `hydrate(): Promise<void>` to `HookEventStore`
2. Use `readline.createInterface` over `fs.createReadStream(eventsFilePath)` to read line by line
3. Parse each line with `JSON.parse`, wrap in try/catch to skip malformed lines
4. Populate `eventsBySession` and update `totalEventCount`
5. Repeat for `agents.jsonl` populating `agents` Map
6. Add `cleanup(): void`: `fs.readdirSync` on hooks dir, filter `events-*.jsonl`, parse timestamp from name, delete if `Date.now() - ts > 30 * 86400 * 1000`
7. Call `hydrate()` then `cleanup()` from `DashboardServer.start()` when `hooksEnabled`
8. Run unit tests

---

### T-006: Wire HookEventStore into DashboardServer lifecycle

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-05
**Status**: [x] completed

**Test Plan**:
- **Given** the dashboard server starts and stops
- **When** events are received and then `stop()` is called
- **Then** events are persisted during the session and `flush()` is called on graceful shutdown

**Test Cases**:
1. **Integration**: `src/dashboard/server/hooks/__tests__/hook-routes.test.ts` (extended)
   - `testEventsPersistedAfterPost()`: POST two events, call `GET /api/hooks/events`, assert both returned
   - `testFlushCalledOnShutdown()`: Spy on `store.flush()`, call `server.stop()`, assert spy called
   - `testHydrateCalledOnStart()`: Pre-write events.jsonl, start server, assert `GET /api/hooks/events` returns hydrated data
   - **Coverage Target**: 85%

**Implementation**:
1. Instantiate `HookEventStore` in `DashboardServer` when `hooksEnabled: true`
2. Call `await store.hydrate()` and `store.cleanup()` in `DashboardServer.start()` before opening port
3. In POST route handler: call `store.addEvent(event)` after handler returns
4. In `DashboardServer.stop()`: call `store.flush()` before closing the server
5. Wire `GET /api/hooks/events` to return `store.getEvents(parseQueryParams(req))`
6. Wire `GET /api/hooks/agents` to return `store.getAgents(parseQueryParams(req))`
7. Wire `GET /api/hooks/status` to return `store.getStats()`
8. Run integration tests

---

## User Story: US-003 - Dashboard Server Auto-Start on Session Begin

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Tasks**: 2 total, 2 completed

---

### T-007: Write PID file on server start and add --hooks CLI flag

**User Story**: US-003
**Satisfies ACs**: AC-US3-03, AC-US3-04
**Status**: [x] completed

**Test Plan**:
- **Given** the dashboard server is started with `hooksEnabled: true`
- **When** the server is ready to accept connections
- **Then** `.specweave/state/hooks/server.pid` is written with `{ port, pid, startedAt }` and deleted on stop

**Test Cases**:
1. **Unit**: `src/dashboard/server/__tests__/dashboard-server-pid.test.ts`
   - `testPidFileWrittenOnStart()`: Start server with `hooksEnabled: true`, assert PID file exists with correct port and pid
   - `testPidFileDeletedOnStop()`: Start then stop server, assert PID file deleted
   - `testPidFileFormat()`: Parse PID file JSON, assert `port` is number, `pid` is number, `startedAt` is ISO string
   - **Coverage Target**: 90%

**Implementation**:
1. Add `pidFilePath: string` field to `DashboardServer` (only set when `hooksEnabled`)
2. In `DashboardServer.start()` after server is listening: write `{ port, pid: process.pid, startedAt: new Date().toISOString() }` to `pidFilePath` using `fs.writeFileSync`
3. Ensure `.specweave/state/hooks/` directory exists via `fs.mkdirSync(..., { recursive: true })`
4. In `DashboardServer.stop()`: `fs.rmSync(pidFilePath, { force: true })`
5. Add `--hooks` flag to the `specweave dashboard` CLI command, setting `hooksEnabled: true`
6. Run unit tests

---

### T-008: Implement command-bridge auto-start with duplicate detection

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02
**Status**: [x] completed

**Test Plan**:
- **Given** `hooks.httpMode: true` and no server running
- **When** the command-bridge SessionStart handler runs
- **Then** it spawns `specweave dashboard --hooks` in background and waits for PID file; if server already running, no duplicate is started

**Test Cases**:
1. **Unit**: `src/hooks/__tests__/command-bridge-autostart.test.ts`
   - `testAutoStartWhenNoServer()`: Mock `net.connect` to fail and PID file absent, assert `child_process.spawn` called with correct args
   - `testNoDuplicateWhenServerRunning()`: Mock `net.connect` to succeed (port in use), assert `spawn` NOT called
   - `testWaitsForPidFile()`: Mock spawn but PID file appears after 400ms, assert bridge waits and proceeds
   - `testFailsSilentlyIfTimeout()`: PID file never appears, assert bridge exits with code 0
   - **Coverage Target**: 90%

**Implementation**:
1. In `src/hooks/command-bridge.mjs`, add auto-start logic for the `SessionStart` event
2. Implement `isServerRunning(port)`: `Promise<boolean>` using `net.connect` with 200ms timeout
3. Implement `waitForPidFile(pidPath, timeoutMs)`: poll every 200ms up to `timeoutMs`, return port or null
4. If not running: `child_process.spawn('specweave', ['dashboard', '--hooks'], { detached: true, stdio: 'ignore' })` then `unref()`
5. Call `waitForPidFile` up to 3000ms; on timeout, exit 0
6. After PID file appears, read port and POST the SessionStart payload
7. Wrap entire auto-start block in try/catch; on any error, exit 0

---

## User Story: US-004 - Command-Bridge for Command-Only Events

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Tasks**: 2 total, 2 completed

---

### T-009: Implement command-bridge.mjs stdin-to-HTTP forwarding

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [x] completed

**Test Plan**:
- **Given** `command-bridge.mjs Notification` is invoked with a JSON payload on stdin
- **When** the dashboard server is running on the discovered port
- **Then** the payload is POSTed to `http://localhost:{port}/api/hooks/Notification` and the process exits 0

**Test Cases**:
1. **Unit**: `src/hooks/__tests__/command-bridge.test.ts`
   - `testReadsStdinAndPosts()`: Pipe JSON through stdin mock, assert `http.request` called with correct URL and body
   - `testFailsSilentlyWhenServerDown()`: Mock `http.request` to emit `ECONNREFUSED`, assert process exits 0
   - `testReadsPidFileForPort()`: Write a PID file to temp dir, assert correct port used in request URL
   - `testMissingPidFileExits0()`: PID file absent, assert process exits 0 without posting
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/hooks/command-bridge.mjs` as an ES module (no build step)
2. Shebang: `#!/usr/bin/env node`
3. Read event name from `process.argv[2]`
4. Discover PID file path: `path.join(process.cwd(), '.specweave/state/hooks/server.pid')`
5. Read and parse PID file; if absent, `process.exit(0)`
6. Read all stdin via `process.stdin.setEncoding('utf8')` accumulation
7. POST to `http://localhost:{port}/api/hooks/{eventName}` using native `http.request`
8. On error (ECONNREFUSED, timeout): `process.exit(0)`
9. On success: print response body to stdout if non-empty, then `process.exit(0)`
10. Run tests with Vitest (configure to handle `.mjs` via ESM mode)

---

### T-010: Implement settings generator command

**User Story**: US-004
**Satisfies ACs**: AC-US4-03
**Status**: [x] completed

**Test Plan**:
- **Given** `hooks.httpMode: true` in `.specweave/config.json`
- **When** `specweave hooks generate-settings` runs
- **Then** it writes `.claude/settings.json` with 8 HTTP hook entries and 9 command hook entries pointing to correct URLs and paths

**Test Cases**:
1. **Unit**: `src/hooks/__tests__/generate-settings.test.ts`
   - `testGeneratesHTTPHooksForSupportedEvents()`: Call generator with httpMode true, assert all 8 HTTP events present with `type: "http"` and correct URLs
   - `testGeneratesCommandHooksForCommandOnlyEvents()`: Assert all 9 command-only events have `type: "command"` with absolute path to `command-bridge.mjs`
   - `testDefaultsToFalseWhenHttpModeAbsent()`: Config without `hooks.httpMode`, assert no HTTP entries generated
   - `testOutputIsValidJSON()`: Parse generated settings, assert no parse error and `hooks` key present
   - **Coverage Target**: 85%

**Implementation**:
1. Create `src/hooks/generate-settings.ts`
2. Read `.specweave/config.json`, extract `hooks.httpMode` and `hooks.port` (default 8340)
3. Define `HTTP_EVENTS` array (8 items) and `COMMAND_EVENTS` array (9 items)
4. If `httpMode: true`: build hooks object with HTTP entries for 8 events and command entries for 9
5. Resolve absolute path to `command-bridge.mjs` for the command entries
6. Write to `.claude/settings.json` via `JSON.stringify(settings, null, 2)`
7. Register `specweave hooks generate-settings` CLI subcommand
8. Run unit tests

---

## User Story: US-005 - TypeScript Event Handlers Replacing Bash

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05
**Tasks**: 3 total, 3 completed

---

### T-011: Implement PreToolUse handler with blocking rules

**User Story**: US-005
**Satisfies ACs**: AC-US1-02, AC-US5-05
**Status**: [x] completed

**Test Plan**:
- **Given** a `PreToolUse` event with tool name `Write` targeting a protected path
- **When** the handler evaluates blocking rules
- **Then** it returns `{ status: 200, body: { hookSpecificOutput: { permissionDecision: "deny", permissionDecisionReason: "..." } } }`

**Test Cases**:
1. **Unit**: `src/dashboard/server/hooks/handlers/__tests__/pre-tool-use.test.ts`
   - `testAllowNonRestrictedTool()`: `Read` tool on any path returns `permissionDecision: "allow"`
   - `testDenySkillChainGuard()`: Write targeting skill-chain guarded path returns `permissionDecision: "deny"` with reason
   - `testDenyIncrementExistenceGuard()`: Write to tasks.md when no increment exists returns deny
   - `testAllowIncrementWriteWhenValid()`: Write to tasks.md with valid increment returns allow
   - `testHandlerNeverThrows()`: Pass malformed payload, assert no throw and response has status 200
   - **Coverage Target**: 95%

**Implementation**:
1. Create `src/dashboard/server/hooks/handlers/pre-tool-use.ts`
2. Export `preToolUseHandler: HookHandler`
3. Extract `tool_name`, `tool_input` from payload
4. Port skill-chain guard logic from `pre-tool-use.sh` (check for skill-chain marker files in `.specweave/state/`)
5. Port increment-existence guard (check if tasks.md target has corresponding increment directory)
6. Default response: `{ hookSpecificOutput: { hookEventName: "PreToolUse", permissionDecision: "allow", permissionDecisionReason: "OK" } }`
7. Register handler in `HookEventRouter` constructor
8. Run unit tests

---

### T-012: Implement subagent lifecycle and task-completed handlers

**User Story**: US-005
**Satisfies ACs**: AC-US5-03, AC-US5-04, AC-US5-05
**Status**: [x] completed

**Test Plan**:
- **Given** a `SubagentStart` event with `agent_id` and `agent_type` in payload
- **When** the handler processes it
- **Then** the agent is stored in the in-memory `agents` Map with `startedAt` set and no `stoppedAt`

**Test Cases**:
1. **Unit**: `src/dashboard/server/hooks/handlers/__tests__/subagent-lifecycle.test.ts`
   - `testSubagentStartCreatesRecord()`: Pass SubagentStart payload, assert `store.getAgents()` contains agent with `startedAt` set
   - `testSubagentStopUpdatesRecord()`: Start then stop same agent_id, assert `stoppedAt` set and `durationMs` computed
   - `testSubagentStopWithoutStartCreatesRecord()`: SubagentStop for unknown agent_id, assert graceful handling without throw
   - `testTaskCompletedStored()`: Pass TaskCompleted payload, assert event in store and `events.jsonl` appended
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/dashboard/server/hooks/handlers/subagent-lifecycle.ts`
2. Export `subagentStartHandler` and `subagentStopHandler` as `HookHandler` functions
3. `subagentStartHandler`: extract `agent_id`, `agent_type`, `session_id`, call `store.updateAgent({ agentId, agentType, sessionId, startedAt })`
4. `subagentStopHandler`: find existing record, set `stoppedAt`, compute `durationMs = Date.now() - new Date(startedAt).getTime()`
5. Implement `updateAgent` on `HookEventStore`: upsert into `agents` Map, append to `agents.jsonl`
6. Create `src/dashboard/server/hooks/handlers/task-completed.ts`
7. Export `taskCompletedHandler`: store event via `store.addEvent`, return `{ status: 200, body: {} }`
8. Register all handlers in `HookEventRouter` constructor
9. Run unit tests

---

### T-013: Implement passthrough and session-lifecycle handlers

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-05
**Status**: [x] completed

**Test Plan**:
- **Given** a `Notification` or `ConfigChange` event arrives
- **When** the passthrough handler processes it
- **Then** the event is stored and 200 with empty body is returned; session handlers route to existing processor for EDA events

**Test Cases**:
1. **Unit**: `src/dashboard/server/hooks/handlers/__tests__/passthrough.test.ts`
   - `testPassthroughStoresEvent()`: PostToolUseFailure payload stored in `store.getEvents()`, returns `{ status: 200 }`
   - `testPassthroughReturnEmptyBody()`: Assert response body is `{}` for all passthrough events
   - `testSessionStartDelegatedToProcessor()`: SessionStart payload triggers existing processor routing (spy on processEvent)
   - `testHandlerErrorIsolation()`: Throw inside passthrough handler, assert 200 still returned and error logged
   - **Coverage Target**: 85%

**Implementation**:
1. Create `src/dashboard/server/hooks/handlers/passthrough.ts`
2. Export `passthroughHandler: HookHandler` that calls `store.addEvent` and returns `{ status: 200, body: {} }`
3. Create `src/dashboard/server/hooks/handlers/session-lifecycle.ts`
4. Export `sessionStartHandler`: store event, call existing bash handler scripts directly via `child_process.execFile` for EDA routing (same mechanism the processor daemon uses)
5. Export `sessionEndHandler`: store event, call `store.flush()`
6. Create `src/dashboard/server/hooks/handlers/post-tool-use.ts`: detect file writes to `.specweave/increments/`, call bash handler scripts via `child_process.execFile` for EDA event routing (NOTE: `processor.ts` is a standalone daemon, NOT importable)
7. Create `src/dashboard/server/hooks/handlers/stop.ts`: store event, call existing bash handler scripts for stop-reflect/stop-auto logic via `child_process.execFile`
8. Register all handlers in `HookEventRouter` constructor
9. Run unit tests

---

## User Story: US-006 - HooksPage Dashboard UI

**Linked ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04
**Tasks**: 2 total, 2 completed

---

### T-014: Implement HooksPage with real-time SSE event stream

**User Story**: US-006
**Satisfies ACs**: AC-US6-01, AC-US6-03, AC-US6-04
**Status**: [x] completed

**Test Plan**:
- **Given** the HooksPage is rendered and SSE is connected
- **When** a `hook-event` SSE message arrives with `permissionDecision: "deny"`
- **Then** it is prepended to the timeline with a red/warning visual style, and consecutive same-type events are collapsed into a summary row

**Test Cases**:
1. **Unit**: `src/dashboard/client/src/__tests__/HooksPage.test.tsx`
   - `testRendersEventTimeline()`: Mock `useApi` with 3 events, assert 3 rows rendered
   - `testDenyEventHighlighted()`: Event with `result.decision === "deny"`, assert row has warning/red class
   - `testConsecutiveSameTypeCollapsed()`: 5 PostToolUse events in sequence, assert single summary row with count 5
   - `testExpandCollapsedGroup()`: Click summary row, assert all 5 events expand and become visible
   - `testSSEEventPrependedToTop()`: Fire SSE `hook-event` via context mock, assert new event appears first
   - **Coverage Target**: 85%

**Implementation**:
1. Add `'hook-event'` and `'hook-agent'` to `EVENT_TYPES` array in `src/dashboard/client/src/contexts/SSEContext.tsx`
2. Create `src/dashboard/client/src/pages/HooksPage.tsx`
3. Use `useApi('/api/hooks/events?limit=200')` for initial load
4. Use `useSSEEvent('hook-event', handler)` to prepend incoming events
5. Implement `collapseConsecutiveSameType(events)` utility: group runs of same `eventName` into `{ type, count, events[] }`
6. Render timeline: timestamp, event type badge, tool name, session ID
7. Deny/block rows: apply Tailwind classes `bg-red-50 border-red-200`
8. Click row: open side panel with full JSON via `JSON.stringify(payload, null, 2)`
9. Add route in `App.tsx` and nav item in `Sidebar.tsx`
10. Run Vitest unit tests

---

### T-015: Implement HooksPage filter bar

**User Story**: US-006
**Satisfies ACs**: AC-US6-02
**Status**: [x] completed

**Test Plan**:
- **Given** the HooksPage displays 10 events across two sessions
- **When** the user selects session ID "abc" in the filter bar
- **Then** only the events from session "abc" are shown

**Test Cases**:
1. **Unit**: `src/dashboard/client/src/__tests__/HooksPage.test.tsx` (extended)
   - `testFilterByEventType()`: Select "PreToolUse" in event type dropdown, assert only PreToolUse rows shown
   - `testFilterBySessionId()`: Type session ID in input, assert filtered results
   - `testFilterByTimeRange()`: Select "last 1 hour" range, assert only recent events shown
   - `testClearFiltersShowsAll()`: Clear all filters, assert all events restored
   - **Coverage Target**: 85%

**Implementation**:
1. Add filter state to `HooksPage`: `{ eventType: string, sessionId: string, timeRange: string }`
2. Implement `filterEvents(events, filters)` pure function
3. Render filter bar: event type `<select>` with all 17 event names + "All", session ID `<input>`, time range `<select>` with "Last 1h / 6h / 24h / All"
4. Apply filters client-side on the loaded events array
5. Run unit tests

---

## User Story: US-007 - AgentsPage Dashboard UI

**Linked ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04
**Tasks**: 2 total, 2 completed

---

### T-016: Implement AgentsPage with agent table and live duration counter

**User Story**: US-007
**Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-04
**Status**: [x] completed

**Test Plan**:
- **Given** the AgentsPage is rendered with one running agent and one completed agent
- **When** the page loads and one second passes
- **Then** the running agent shows a "running" badge and its duration counter increments; the completed agent shows a formatted static duration

**Test Cases**:
1. **Unit**: `src/dashboard/client/src/__tests__/AgentsPage.test.tsx`
   - `testRendersAgentTable()`: Mock `useApi` with 2 agents, assert table has 2 rows with correct columns
   - `testRunningAgentBadge()`: Agent with no `stoppedAt`, assert "running" badge rendered
   - `testLiveDurationCounter()`: Use fake timers, advance 1s, assert running agent duration updates
   - `testCompletedAgentDuration()`: Agent with `durationMs: 5000`, assert "5s" displayed
   - `testSSEUpdateAddsRow()`: Fire `hook-agent` SSE event, assert new agent row appears without page reload
   - **Coverage Target**: 85%

**Implementation**:
1. Create `src/dashboard/client/src/pages/AgentsPage.tsx`
2. Use `useApi('/api/hooks/agents')` for initial load
3. Use `useSSEEvent('hook-agent', handler)` to update agent list in real-time
4. Render table: `agent_id`, `agent_type`, `session_id`, `started_at`, `stopped_at`, `duration_ms` columns
5. Running indicator: green "running" badge for agents without `stoppedAt`
6. Live counter: `useEffect` with `setInterval(1000)` to recompute elapsed ms for running agents
7. Summary stats row: total agents, currently running count, average duration
8. Add route in `App.tsx` and nav item in `Sidebar.tsx`
9. Run Vitest unit tests using fake timers for counter behavior

---

### T-017: Implement AgentsPage session filter

**User Story**: US-007
**Satisfies ACs**: AC-US7-03
**Status**: [x] completed

**Test Plan**:
- **Given** agents from two sessions are displayed on AgentsPage
- **When** the user selects a session ID from the filter dropdown
- **Then** only agents from the selected session are shown

**Test Cases**:
1. **Unit**: `src/dashboard/client/src/__tests__/AgentsPage.test.tsx` (extended)
   - `testFilterBySession()`: 4 agents across 2 sessions, select one session, assert 2 rows shown
   - `testFilterDropdownPopulatedFromData()`: Dropdown contains unique session IDs from agent data
   - `testClearFilterShowsAll()`: Reset filter to "All sessions", assert all agents shown
   - **Coverage Target**: 85%

**Implementation**:
1. Add `sessionId` filter state to `AgentsPage`
2. Extract unique session IDs from agent data for dropdown options
3. Render session filter: `<select>` with "All sessions" option + unique session IDs
4. Filter `agents` array client-side before rendering the table
5. Run unit tests

---

## User Story: US-008 - Settings Generator and Migration Config

**Linked ACs**: AC-US8-01, AC-US8-02, AC-US8-03, AC-US8-04
**Tasks**: 2 total, 2 completed

---

### T-018: Implement hooks status command and config default enforcement

**User Story**: US-008
**Satisfies ACs**: AC-US8-02, AC-US8-03, AC-US8-04
**Status**: [x] completed

**Test Plan**:
- **Given** `hooks.httpMode` is absent from config.json
- **When** hooks are evaluated
- **Then** the system defaults to `false` and bash hooks operate unchanged; `specweave hooks status` reports server state accurately

**Test Cases**:
1. **Unit**: `src/hooks/__tests__/hooks-status.test.ts`
   - `testDefaultIsFalseWhenAbsent()`: Config without `hooks.httpMode`, assert `getHttpMode(config) === false`
   - `testBashHooksUnchangedWhenFalse()`: httpMode false, assert no HTTP entries in any generated settings output
   - `testStatusReportsServerDown()`: PID file absent, assert status output contains "not running"
   - `testStatusReportsServerUp()`: Write temp PID file and mock port check to succeed, assert output contains port and event count
   - **Coverage Target**: 85%

**Implementation**:
1. Add `getHttpMode(config: SpecWeaveConfig): boolean` helper returning `config?.hooks?.httpMode ?? false`
2. Guard settings generator: if `httpMode === false`, exit early without writing HTTP entries
3. Implement `specweave hooks status` CLI subcommand
4. Status command: read PID file; if absent, print "Dashboard server: not running"
5. If PID file present: check port via `net.connect`; if alive, GET `/api/hooks/status` and print "running on port {port}, {N} events"
6. If PID file present but port closed: print "Dashboard server: crashed (stale PID file)" and delete PID file
7. Run unit tests

---

### T-019: End-to-end integration test for full hook event flow

**User Story**: US-008
**Satisfies ACs**: AC-US8-01, AC-US8-02, AC-US8-03, AC-US8-04
**Status**: [x] completed

**Test Plan**:
- **Given** the dashboard server starts with `hooksEnabled: true` and config has `hooks.httpMode: true`
- **When** `specweave hooks generate-settings` runs and events are POSTed to the server
- **Then** the generated settings file is valid, events appear in the API, and bash hooks are unaffected when `httpMode: false`

**Test Cases**:
1. **Integration**: `src/hooks/__tests__/e2e-hook-flow.test.ts`
   - `testFullFlowHttpModeTrue()`: Start server, generate settings, POST PreToolUse, GET `/api/hooks/events`, assert event present
   - `testBashSystemUntouched()`: httpMode false, run generator, assert no HTTP entries in output
   - `testSettingsFileValid()`: Generated settings JSON has `hooks` key with arrays of hook entries
   - `testEventCountInStatus()`: POST 5 events, GET `/api/hooks/status`, assert `totalEvents === 5`
   - `testGracefulShutdown()`: POST event, stop server, restart with same temp dir, hydrate, assert event still present via GET
   - **Coverage Target**: 85%

**Implementation**:
1. Create `src/hooks/__tests__/e2e-hook-flow.test.ts`
2. Use `DashboardServer` directly (no subprocess) with a temp project root and ephemeral port
3. POST multiple event types and assert round-trip response and SSE broadcast
4. Verify JSONL files written to temp dir after each POST
5. Stop server, instantiate new `HookEventStore` with same temp dir, call `hydrate()`, assert events restored
6. Run `generateSettings()` and validate output JSON structure and event counts
7. Run full integration suite: `npx vitest run src/hooks/__tests__/e2e-hook-flow.test.ts`

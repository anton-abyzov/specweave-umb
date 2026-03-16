---
increment: 0489-dashboard-docs-services
title: "Fix dashboard docs preview services"
generated_by: sw:test-aware-planner
by_user_story:
  US-001: [T-001]
  US-002: [T-002]
  US-003: [T-003]
  US-004: [T-004]
build: [T-005]
---

# Tasks: 0489-dashboard-docs-services

## User Story: US-001 - Scope-specific docs commands

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Tasks**: 1 total, 0 completed

### T-001: Add scope-specific commands to command-runner.ts

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [x] completed

**Test Plan**:
- **Given** the ALLOWED_COMMANDS map in command-runner.ts
- **When** the module is loaded
- **Then** `docs-internal-start`, `docs-internal-stop`, `docs-public-start`, `docs-public-stop` are registered and `docs-preview-start`, `docs-preview-stop` are absent

**Test Cases**:
1. **Unit**: `tests/unit/core/dashboard/command-runner.test.ts`
   - `testInternalStartSpawnsCorrectCommand()`: ALLOWED_COMMANDS['docs-internal-start'] has cmd='specweave', args=['docs','preview']
   - `testPublicStartSpawnsCorrectCommand()`: ALLOWED_COMMANDS['docs-public-start'] has cmd='specweave', args=['docs','preview','--scope','public']
   - `testInternalStopHasHandler()`: ALLOWED_COMMANDS['docs-internal-stop'] has a handler function (not cmd+args)
   - `testPublicStopHasHandler()`: ALLOWED_COMMANDS['docs-public-stop'] has a handler function (not cmd+args)
   - `testOldCommandsRemoved()`: ALLOWED_COMMANDS does not contain 'docs-preview-start' or 'docs-preview-stop'
   - `testHandlerDispatchCallsKillProcessOnPort()`: execute('docs-internal-stop') calls killProcessOnPort(3015) not spawn
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/dashboard/server/command-runner.ts`
2. Change the ALLOWED_COMMANDS type to `Record<string, { cmd: string; args: string[] } | { handler: () => Promise<void> }>`
3. Remove `'docs-preview-start'` and `'docs-preview-stop'` entries
4. Add `'docs-internal-start': { cmd: 'specweave', args: ['docs', 'preview'] }`
5. Add `'docs-public-start': { cmd: 'specweave', args: ['docs', 'preview', '--scope', 'public'] }`
6. Import `killProcessOnPort` from `'../../utils/docs-preview/index.js'`
7. Add `'docs-internal-stop': { handler: () => killProcessOnPort(3015).then(() => undefined) }`
8. Add `'docs-public-stop': { handler: () => killProcessOnPort(3016).then(() => undefined) }`
9. In `execute()`, check `'handler' in spec`: if true call `spec.handler()` and resolve the execution in-process; if false spawn child process as before
10. Run tests

---

## User Story: US-002 - Correct service listing with proper ports

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Tasks**: 1 total, 0 completed

### T-002: Update /api/services in dashboard-server.ts

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Status**: [x] completed

**Test Plan**:
- **Given** the `/api/services` GET handler in dashboard-server.ts
- **When** a project is resolved and the endpoint is called
- **Then** the response contains exactly "Dashboard Server", "Internal Docs" (port 3015), and "Public Docs" (port 3016) — no "Docs Preview"

**Test Cases**:
1. **Unit**: `tests/unit/core/dashboard/services-endpoint.test.ts`
   - `testServicesListContainsInternalDocs()`: Response includes `{name:'Internal Docs', port:3015}`
   - `testServicesListContainsPublicDocs()`: Response includes `{name:'Public Docs', port:3016}`
   - `testServicesListNoDocsPreview()`: Response does NOT contain any entry with `name:'Docs Preview'`
   - `testInternalDocsPortFromSCOPE_PORTS()`: Port used for Internal Docs matches `SCOPE_PORTS.internal` (3015) not any config fallback
   - `testRunningStatusWhenPortReachable()`: When `isPortReachable(3015)` returns true, Internal Docs status is 'running'
   - `testStoppedStatusWhenPortUnreachable()`: When `isPortReachable(3015)` returns false, Internal Docs status is 'stopped'
   - `testServicesIncludeStartStopCommands()`: Internal Docs has `startCommand:'docs-internal-start'`, `stopCommand:'docs-internal-stop'`; Public Docs has equivalent public fields
   - `testDashboardServerHasNoStartStopCommand()`: Dashboard Server entry has no `startCommand` or `stopCommand`
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/dashboard/server/dashboard-server.ts`
2. Add import: `import { SCOPE_PORTS } from '../../utils/docs-preview/types.js';`
3. Remove the `docsPort` config lookup line
4. Replace the single "Docs Preview" entry with two entries using SCOPE_PORTS.internal (3015) and SCOPE_PORTS.public (3016)
5. Internal Docs: `startCommand: 'docs-internal-start', stopCommand: 'docs-internal-stop'`
6. Public Docs: `startCommand: 'docs-public-start', stopCommand: 'docs-public-stop'`
7. Keep the Dashboard Server entry unchanged (no startCommand/stopCommand)
8. Run tests

---

## User Story: US-003 - Configurable command timeout

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Tasks**: 1 total, 0 completed

### T-003: Add optional timeoutMs to useCommand hook

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Status**: [x] completed

**Test Plan**:
- **Given** the `useCommand` React hook
- **When** `execute(commandName, { timeoutMs: 300000 })` is called
- **Then** the safety timeout fires at 300 seconds, not 60; and the error message reflects the actual duration

**Test Cases**:
1. **Unit**: `tests/unit/core/dashboard/useCommand.test.ts`
   - `testDefaultTimeoutIs60s()`: With no options, setTimeout is called with 60000
   - `testCustomTimeoutApplied()`: With `{ timeoutMs: 300000 }`, setTimeout is called with 300000
   - `testTimeoutErrorMessageIncludesActualDuration()`: Timeout error says "300 seconds" not "60 seconds"
   - `testDefaultTimeoutErrorSays60Seconds()`: Default timeout error says "60 seconds"
   - `testQueryParamsStillWorkWithOptionsObject()`: Passing `{ queryParams: {...} }` still appends query string to fetch URL
   - `testBackwardCompatUndefinedOptions()`: Calling `execute('cmd')` with no second arg behaves identically to before
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/dashboard/client/src/hooks/useCommand.ts`
2. Change the `execute` callback signature from:
   `async (commandName: string, queryParams?: Record<string, string>)`
   to:
   `async (commandName: string, options?: { queryParams?: Record<string, string>; timeoutMs?: number })`
3. Inside the callback, extract: `const queryParams = options?.queryParams; const timeout = options?.timeoutMs ?? 60000;`
4. Replace the hardcoded `60000` in `setTimeout(...)` with `timeout`
5. Replace hardcoded `'Command timed out after 60 seconds'` with `` `Command timed out after ${timeout / 1000} seconds` ``
6. Replace hardcoded `'Timed out after 60 seconds.'` in `setOutput` with the parameterized string
7. Run tests

---

## User Story: US-004 - Data-driven service controls in ServicesPage

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05
**Tasks**: 1 total, 0 completed

### T-004: Replace name-hardcoded controls with data-driven rendering in ServicesPage.tsx

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05
**Status**: [x] completed

**Test Plan**:
- **Given** the ServicesPage component
- **When** rendered with services that include `startCommand`/`stopCommand` fields (Internal Docs, Public Docs) or without them (Dashboard Server)
- **Then** start/stop buttons appear for controllable services and only an Open link appears for non-controllable services; no `svc.name === 'Docs Preview'` check exists anywhere

**Test Cases**:
1. **Unit**: `tests/unit/core/dashboard/ServicesPage.test.tsx`
   - `testStartButtonAppearsWhenStartCommandPresent()`: Service with startCommand and status='stopped' renders a Start button
   - `testStopAndOpenButtonsWhenRunningWithCommand()`: Service with stopCommand and status='running' renders Open and Stop buttons
   - `testNoStartStopButtonsWithoutCommands()`: Dashboard Server (no startCommand) shows only Open link when running, nothing when stopped
   - `testHandleStartPassesTimeoutMs300s()`: Clicking Start calls `execute(svc.startCommand, { timeoutMs: 300000 })`
   - `testHandleStopPassesTimeoutMs300s()`: Clicking Stop calls `execute(svc.stopCommand, { timeoutMs: 300000 })`
   - `testNoHardcodedDocsPreviewNameCheck()`: Component source does not contain the string "Docs Preview" in any conditional
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/dashboard/client/src/pages/ServicesPage.tsx`
2. Add `startCommand?: string; stopCommand?: string;` to the `ServiceInfo` interface
3. Update `handleStart` to call `execute(commandName, { timeoutMs: 300000 })`
4. Update `handleStop` to call `execute(commandName, { timeoutMs: 300000 })`
5. Remove the `{svc.name === 'Docs Preview' && (...)}` block entirely
6. Remove the `{svc.status === 'running' && svc.name !== 'Docs Preview' && (...)}` block
7. Replace both removed blocks with data-driven rendering: when startCommand+stopCommand are present show Open+Stop (running) or Start (stopped); when absent show only Open link (running) or nothing (stopped)
8. Run tests

---

## Build & Verify

**Tasks**: 1 total, 0 completed

### T-005: Build and manual smoke test

**User Story**: US-001, US-002, US-003, US-004
**Satisfies ACs**: AC-US1-01, AC-US2-01, AC-US4-01
**Status**: [x] completed

**Test Plan**:
- **Given** all 4 file changes are applied
- **When** the specweave CLI is built and the dashboard is opened
- **Then** the Services page shows "Internal Docs" and "Public Docs" with correct ports, Start/Stop buttons work, and no runtime errors occur

**Implementation**:
1. Run `cd repositories/anton-abyzov/specweave && npx tsc --noEmit` to check types
2. Run `npx vitest run tests/unit/core/dashboard/` to run all new dashboard unit tests
3. Build the client: `cd src/dashboard/client && npm run build`
4. Manually verify dashboard Services page shows "Internal Docs" (port 3015) and "Public Docs" (port 3016)
5. Verify Start button triggers docs start without premature 60-second timeout
6. Verify "Docs Preview" entry is absent

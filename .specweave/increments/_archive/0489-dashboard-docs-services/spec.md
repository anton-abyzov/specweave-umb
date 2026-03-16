---
increment: 0489-dashboard-docs-services
title: Fix dashboard docs preview services
type: feature
priority: P1
status: completed
created: 2026-03-11T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Fix dashboard docs preview services

## Problem Statement

The dashboard Services page has several bugs and missing functionality around documentation preview services:
1. The single "Docs Preview" service entry should be split into "Internal Docs" and "Public Docs" matching the existing `SCOPE_PORTS` definition (internal:3015, public:3016).
2. Port detection checks `config.documentation.previewPort ?? 3000`, which is wrong -- internal docs use port 3015, public docs use port 3016.
3. `command-runner.ts` only has generic `docs-preview-start`/`docs-preview-stop` commands, lacking scope-specific variants.
4. `useCommand.ts` hardcodes a 60-second client-side timeout, but docs commands (which install npm packages and start Docusaurus) routinely exceed 60 seconds.
5. `ServicesPage.tsx` hardcodes `svc.name === 'Docs Preview'` for rendering start/stop/open controls, making it impossible to add new controllable services without code changes.

## Goals

- Correctly represent both Internal Docs and Public Docs as separate services with correct ports
- Provide scope-specific start/stop commands in the command runner
- Eliminate premature timeout for docs commands
- Make the ServicesPage service controls data-driven instead of name-hardcoded

## User Stories

### US-001: Scope-specific docs commands (P1)
**Project**: specweave

**As a** developer using the SpecWeave dashboard
**I want** separate start/stop commands for Internal Docs and Public Docs
**So that** I can independently manage each documentation server

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given command-runner.ts ALLOWED_COMMANDS, when the dashboard loads, then commands `docs-internal-start`, `docs-internal-stop`, `docs-public-start`, `docs-public-stop` are all registered
- [x] **AC-US1-02**: Given `docs-internal-start` is executed, when the command runs, then it spawns `specweave docs preview` (internal scope, port 3015)
- [x] **AC-US1-03**: Given `docs-public-start` is executed, when the command runs, then it spawns `specweave docs public preview` (public scope, port 3016)
- [x] **AC-US1-04**: Given `docs-internal-stop` or `docs-public-stop` is executed, when the command runs, then it kills the Docusaurus process on the corresponding port (3015 or 3016)
- [x] **AC-US1-05**: Given the old `docs-preview-start` and `docs-preview-stop` commands, when the code is updated, then they are removed from ALLOWED_COMMANDS

---

### US-002: Correct service listing with proper ports (P1)
**Project**: specweave

**As a** developer viewing the Services page
**I want** to see "Internal Docs" and "Public Docs" as separate services with correct port status
**So that** I know which documentation server is running and on which port

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given the `/api/services` endpoint, when called, then it returns two docs services: "Internal Docs" (checking port 3015) and "Public Docs" (checking port 3016)
- [x] **AC-US2-02**: Given a docs service entry, when the port is reachable, then the service status is "running"; otherwise "stopped"
- [x] **AC-US2-03**: Given the old "Docs Preview" service, when the code is updated, then it no longer appears in the service list
- [x] **AC-US2-04**: Given SCOPE_PORTS from `docs-preview/types.ts`, when ports are resolved, then the server uses these constants (not hardcoded 3000 or config fallback)

---

### US-003: Configurable command timeout (P1)
**Project**: specweave

**As a** developer starting a docs preview from the dashboard
**I want** the client-side timeout to be long enough for docs commands
**So that** the command does not falsely report a timeout while npm install and Docusaurus startup are still running

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given `useCommand` hook, when `execute` is called, then it accepts an optional `timeoutMs` parameter (defaults to 60000)
- [x] **AC-US3-02**: Given a docs start command is executed, when the timeout parameter is set to 300000 (300s), then the safety timeout fires at 300 seconds instead of 60
- [x] **AC-US3-03**: Given a non-docs command is executed, when no timeout override is provided, then the default 60-second timeout still applies
- [x] **AC-US3-04**: Given the timeout fires, when the command is still running, then the error message reflects the actual timeout duration (not hardcoded "60 seconds")

---

### US-004: Data-driven service controls in ServicesPage (P1)
**Project**: specweave

**As a** developer managing services on the dashboard
**I want** start/stop/open controls to appear for any controllable service based on data, not hardcoded name checks
**So that** adding new controllable services does not require UI code changes

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given the `/api/services` response, when a service includes `startCommand` and `stopCommand` fields, then ServicesPage renders start/stop buttons for that service
- [x] **AC-US4-02**: Given "Internal Docs" service, when rendered in ServicesPage, then it shows Open/Stop buttons when running and a Start button when stopped, using its `startCommand`/`stopCommand`
- [x] **AC-US4-03**: Given "Public Docs" service, when rendered in ServicesPage, then it shows the same Open/Stop/Start controls using its own `startCommand`/`stopCommand`
- [x] **AC-US4-04**: Given "Dashboard Server" service (no startCommand/stopCommand), when rendered, then it only shows the Open link, no start/stop buttons
- [x] **AC-US4-05**: Given the old `svc.name === 'Docs Preview'` check in ServicesPage, when the code is updated, then no service-name-specific conditionals exist in the rendering logic

## Functional Requirements

### FR-001: Command runner scope-specific commands
Replace the generic `docs-preview-start`/`docs-preview-stop` entries in `ALLOWED_COMMANDS` with four scope-specific entries: `docs-internal-start` (runs `specweave docs preview`), `docs-internal-stop` (runs `specweave docs kill` scoped to internal), `docs-public-start` (runs `specweave docs public preview`), `docs-public-stop` (runs `specweave docs kill` scoped to public).

### FR-002: Service API response enrichment
The `/api/services` endpoint in `dashboard-server.ts` must return each service with optional `startCommand` and `stopCommand` string fields. Internal Docs gets `startCommand: 'docs-internal-start'` and `stopCommand: 'docs-internal-stop'`. Public Docs gets the public equivalents. Dashboard Server gets neither.

### FR-003: Configurable client timeout
`useCommand.execute()` signature changes from `execute(commandName, queryParams?)` to `execute(commandName, options?)` where options includes `queryParams` and `timeoutMs`. ServicesPage passes `timeoutMs: 300000` for docs commands.

## Success Criteria

- Both "Internal Docs" and "Public Docs" appear as separate services in the dashboard
- Port detection uses correct ports (3015/3016) instead of 3000
- Docs start commands complete without premature timeout
- Start/stop controls render for both docs services without hardcoded name checks
- Existing non-docs commands and services are unaffected

## Out of Scope

- Changing the underlying `specweave docs` CLI behavior
- Adding new service types beyond Internal/Public Docs
- Server-side command timeout enforcement (only client-side safety timeout is addressed)
- Changes to the docs-preview/types.ts constants

## Dependencies

- `SCOPE_PORTS` from `src/utils/docs-preview/types.ts` (already exists: internal:3015, public:3016)
- Existing `specweave docs preview` and `specweave docs kill` CLI commands
- `isPortReachable()` utility from `hooks/hooks-status.ts`

## Technical Notes

- `docs kill` currently kills ALL Docusaurus processes. For scope-specific stop, consider using `killProcessOnPort(port)` directly or adding a scope flag to the kill command.
- The `ServiceInfo` interface in `ServicesPage.tsx` needs `startCommand?: string` and `stopCommand?: string` optional fields added.
- The dashboard types.ts (not docs-preview types.ts) may need the `CommandExecution` or `ServiceInfo` type updated.

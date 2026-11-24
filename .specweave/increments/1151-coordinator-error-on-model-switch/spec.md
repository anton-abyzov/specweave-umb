# Coordinator error on model switch

## Problem

On October 31, 2026 at 06:40:06 UTC the user switched the specweave coordinator on the M4 from Gemini · Auto to Claude Code · Opus 5.5 while Gemini run 1394 was still working. The thread then showed a red "Provider error" row:

> The provider event stream closed unexpectedly. Retry the turn; if it keeps failing, check the provider and server logs.

The next turn on Claude worked, so the error was false. It read like a provider or balance problem.

Evidence (server trace `server.trace.ndjson.3`, M4): `ws.rpc.orchestration.dispatchCommand` `thread.model-selection.set` at 06:40:06.001, then `AcpAdapterV2.interruptTurn` failed with `AcpTransportError` at 06:40:06.017, then `ProviderProcessSupervisor.reap`. The switch detaches the live Gemini session (`Provider or model selection changed.`), `ProviderSessionManager.failSubscribers` fails the run's event stream with `ProviderAdapterEventStreamError`, and `RunExecutionService`'s ingestion-failure path records the run as `failed` with that message.

## Scope

In: a model or provider switch that stops a running turn records the turn as stopped by the user ("Interrupt requested · Switched to another model", then "Run interrupted · Stopped by the user"), with no provider error. Out: deferring the switch until the turn ends; real provider failures keep their existing messages.

## Acceptance Criteria

- [ ] AC-01: `thread.model-selection.set` or `provider.switch` that releases the session of a starting or running run records a `run_interrupt_request` for that run (cause `user`, message "Switched to another model").
- [ ] AC-02: When a run's event stream fails after a Stop request was recorded for it, the run ends `interrupted` with a `run_interrupt_result`, and no provider failure item is written.
- [ ] AC-03: A stream failure with no Stop request still ends `failed` with "The provider event stream closed unexpectedly…".

## Approach

1. `apps/server/src/orchestration-v2/Orchestrator.ts`: in the thread-mutation handler, before the session detach, find starting or running runs whose provider thread uses a released session and emit a `run_interrupt_request` turn item for each.
2. `apps/server/src/orchestration-v2/RunExecutionService.ts`: in the ingestion-failure path, read the run's interrupt request; when present, write an `interrupted` terminal instead of a failed one.

Rejected: holding the switch until the turn ends (the user wanted Claude to take over at once, and their next message would queue behind a slow turn); matching the release detail text in the error (fragile).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 A switch during a turn still stops that turn immediately → kept (reversible).
### Open
- none

## Tasks

### T-01 Record a Stop when a model switch releases a running turn's session
- AC: AC-01 | Files: apps/server/src/orchestration-v2/Orchestrator.ts, apps/server/src/orchestration-v2/Orchestrator.test.ts | Test: `npx vitest run apps/server/src/orchestration-v2/Orchestrator.test.ts -t "model switch"` in specwithcode-dev

### T-02 End a stopped run as interrupted when its stream fails
- AC: AC-02, AC-03 | Files: apps/server/src/orchestration-v2/RunExecutionService.ts, apps/server/src/orchestration-v2/RunExecutionService.test.ts | Test: `npx vitest run apps/server/src/orchestration-v2/RunExecutionService.test.ts -t "stream"` in specwithcode-dev

### T-03 Ship and check on the M4
- AC: AC-01, AC-02 | Files: none | Test: PR merged, release installed on the M4, `SpecWithCode --version` matches

### T-04 Verify and close 1151
- AC: AC-01, AC-02, AC-03 | Files: none | Test: `specweave verify 1151`

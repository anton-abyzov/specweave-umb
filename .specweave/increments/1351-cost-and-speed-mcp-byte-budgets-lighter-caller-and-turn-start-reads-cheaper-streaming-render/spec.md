# Cost and speed: MCP byte budgets, lighter caller and turn-start reads, cheaper streaming render

## Problem

Five hot paths cost tokens, queries or renders on every call (triage report of increment 1346, section 3; Anton approved on November 14, 2026: "yes, adopt all, do what's recommended").

- P1. `studio_thread_read` returns up to 50 items of 20,000 characters each with no total budget, and `orchestrator_capabilities` returned 277,823 characters in one call on November 14, 2026. MCP clients spill results over about 25,000 tokens to a file, so the coordinator loses the reply.
- P2. Every MCP tool that acts as the caller loads the caller's whole thread (runs, messages, subagents, provider threads and turns, runtime requests, context transfers, turn items) at `apps/server/src/mcp/OrchestratorMcpService.ts:1391-1405`, through `loadCaller` and `loadThreadCaller` (`:1465`). Coordinators make hundreds of such calls on long threads.
- P3. Turn start reads the full runtime recovery projection three times to test one run (`apps/server/src/orchestration-v2/ProviderTurnStartService.ts:301`, `:310`, `:328`).
- P4. While an agent streams, the chat view re-renders on every git file-count change (`apps/web/src/components/ChatView.tsx:4941`), work rows are re-derived for unchanged entries (`packages/client-runtime/src/work-log/presentation.ts:406`), and the collapsed reasoning preview re-parses the whole block (`apps/web/src/components/chat/MessagesTimeline.tsx:4909`).
- P5. Cursor turns write every streamed token to the provider log (`apps/server/src/provider/EventNdjsonLogger.ts:258-274` filters other providers only), and the server sends a terminal's full history although the client keeps a bounded buffer (`apps/server/src/terminal/Manager.ts:415`).

## Scope

In: the five changes above in `repositories/anton-abyzov/specwithcode`, each with a test that fails on the pre-fix code, before and after numbers for P1 to P4, and a dated "Selected ports" section in `UPSTREAM.md`.

Out: the delegate wait and wake code in `OrchestratorMcpService.ts`, queue ordering (`Orchestrator.ts`, `QueuedRunOrder.ts`), ACP and Pi adapters, `auth/http.ts`, `serverSettings.ts`, the chunk reload guard and the connection supervisor (owned by increments 1347 to 1349). Long-thread index and paging, SQLite worker writes and the other "measure first" rows of the triage.

## Acceptance Criteria

- [ ] AC-01: A `studio_thread_read` result never exceeds a fixed serialized byte budget; when the page does not fit, it keeps the newest items, says it was cut, and returns a position that pages to the rest. Existing arguments keep working.
- [ ] AC-02: `orchestrator_capabilities` with no arguments fits the same budget on a catalog the size of the November 14 one (277,823 characters before), and every omitted detail is reachable by a documented argument or page.
- [ ] AC-03: A caller-acting MCP tool no longer loads the caller's messages, turn items, provider turns or runtime requests unless that tool reads them; behaviour of each tool is unchanged (existing MCP suite green).
- [ ] AC-04: Turn start checks the current attempt with a single-run read; the full recovery projection is read only where background items or turn ownership need it.
- [ ] AC-05: A git status change that keeps `isRepo`, `refName`, `pr` and `hasWorkingTreeChanges` equal does not re-render the chat view's git consumers.
- [ ] AC-06: Work-row derivation for an unchanged entry returns the cached result (same reference) and does no repeat work.
- [ ] AC-07: The collapsed reasoning preview parses at most a bounded prefix of the block; the expanded view still renders all of it.
- [ ] AC-08: Cursor streamed deltas are not written to the provider event log; non-delta Cursor events still are.
- [ ] AC-09: A client that states its history buffer size receives at most that much terminal history; a client that does not gets today's behaviour.
- [ ] AC-10: `reports/measurements.md` records before and after numbers for P1 to P4 (payload bytes, query or record-kind count, render or derivation count), and `reports/red-green.md` records the failing and passing run of each new test.
- [ ] AC-11: The PR has green CI, a ship verdict from `muse-wonder-1.0` at its exact head, is merged, and a release is requested. The public repository names the upstream project only in `UPSTREAM.md`.

## Approach

Each item is rebuilt on our code, reading the upstream diff only as a reference.

1. P1 and P2 share `OrchestratorMcpService.ts` and go to one lane. Budget logic lives in a new small module under `apps/server/src/mcp/` (pure functions, unit tested). P2 splits the caller read into a light read (thread row plus what authorization needs) and per-tool loads of the heavier record kinds.
2. P3 adds a single-run reader on the projection store if none exists and uses it in `makeRunControls`.
3. P4 is three independent web and client-runtime changes; web tests run from `apps/web`.
4. P5 extends the delta filter in `EventNdjsonLogger.ts` and adds an optional contract field for the client's terminal buffer size; old peers ignore it.

Risks: P2 touches handlers the 1347 to 1349 thread also edits. Keep the diff in the caller-load helpers and rebase on their merged PRs. A tool that silently needed a dropped record kind would misbehave, so the lane lists each handler's reads and the MCP suite must stay green.

## Decisions

### Asked
- D-01 Adopt sections 3 and 4 as recommended → yes (Anton, November 14, 2026).
### Defaulted (change any before sw-do)
- D-02 Byte budget → one constant for both tools, sized to stay under the MCP client spill limit (about 25,000 tokens) with margin; the lane picks the number and records it in `reports/measurements.md`.
- D-03 Capabilities over budget → a compact default (instances and model ids) plus arguments for one instance's full detail, not a hard truncation.
- D-04 One PR for the whole group, reviewed by Muse at its exact head.
### Open
- none

## Tasks

### T-01 Byte budget for studio_thread_read and orchestrator_capabilities
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/mcp/OrchestratorMcpService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/mcpResultBudget.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/mcpResultBudget.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/mcp/mcpResultBudget.test.ts

### T-02 MCP tools stop loading the caller's whole thread
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/mcp/OrchestratorMcpService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/OrchestratorMcpService.callerLoad.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/mcp/OrchestratorMcpService.callerLoad.test.ts

### T-03 Turn start reads one run
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ProviderTurnStartService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ProviderTurnStartService.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/ProviderTurnStartService.test.ts

### T-04 Streaming render cost
- AC: AC-05, AC-06, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/ChatView.tsx, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/work-log/presentation.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/studioMcpToolPresentation.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/MessagesTimeline.tsx | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run packages/client-runtime/src/work-log/presentation.test.ts

### T-05 Cursor delta logging and terminal history trim
- AC: AC-08, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/provider/EventNdjsonLogger.ts, repositories/anton-abyzov/specwithcode/apps/server/src/terminal/Manager.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/state/terminalOutput.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/provider/EventNdjsonLogger.test.ts

### T-06 Measurements, red-green record and provenance
- AC: AC-10 | Files: .specweave/increments/1351-cost-and-speed-mcp-byte-budgets-lighter-caller-and-turn-start-reads-cheaper-streaming-render/reports/measurements.md, .specweave/increments/1351-cost-and-speed-mcp-byte-budgets-lighter-caller-and-turn-start-reads-cheaper-streaming-render/reports/red-green.md, repositories/anton-abyzov/specwithcode/UPSTREAM.md | Test: test -s .specweave/increments/1351-cost-and-speed-mcp-byte-budgets-lighter-caller-and-turn-start-reads-cheaper-streaming-render/reports/measurements.md

### T-07 PR, cross-family review, merge and release request
- AC: AC-11 | Files: repositories/anton-abyzov/specwithcode | Test: cd repositories/anton-abyzov/specwithcode && gh pr view --json state -q .state | grep MERGED

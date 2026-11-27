# Quieter threads: fold wake notices, stop task_status polling, name every tool row

## Problem

Increment 1500 measured what people actually see in long threads (M5 database, November 27, 2026; report `.specweave/increments/1500-fewer-studio-code-tool-rows-research-batching-and-apply-only-what-pays-off/reports/research-batching.md`). Batching studio-code calls would remove under 2% of tool rows, and the owner accepted shipping no batching code. The rows that do crowd threads are other things:

- Of 1,300 single rows still visible on desktop across the 40 busiest threads, 785 are wake notices (a background task, background command or monitor finished) and 149 are system notices. In the coordinator, 110 of its 122 visible single rows are wake notices.
- Models poll children: 192 `delegate_task` then `task_status` pairs, each a model round trip, while blocking wait tools (`studio_thread_wait`, `delegate_task` `mode=wait`) already exist and completions wake the parent.
- 246 tool rows carry the name "Tool" or "tool" instead of their real tool (Claude 200, 87 of them in Claude native subagent threads; Muse 35; Copilot 9; Codex 2).

## Scope

In: fold adjacent wake notices on desktop and mobile with the reason one click away; tool descriptions and coordinator guidance that steer models to wait instead of polling `task_status`; real names on tool rows. Out: any batch or composite tool (1500 D-03).

## Acceptance Criteria

- [ ] AC-01: Adjacent wake notices in a settled turn show as one row on desktop and mobile that says how many and opens to each notice; a single notice still shows alone; measured with 1500's scripts, visible single rows in the 40-thread sample drop by at least 30%.
- [ ] AC-02: `task_status` and `delegate_task` descriptions say that a completion wakes the caller and that polling is not needed; a fixture or replay shows the coordinator guidance no longer suggests polling.
- [ ] AC-03: Tool rows from Claude native subagents, Muse, Copilot and Codex show the real tool name; a regression test covers each source that produced "Tool".

## Approach

Plan only; not started. Measure first with 1500's scripts (`reports/measure-*.scratch.test.ts.txt`, `shared.ts`). Rows: `apps/web/src/components/chat/MessagesTimeline.logic.ts` grouping and `apps/mobile/src/lib/threadActivity.ts`. Descriptions: the studio-code toolkit. Names: the provider adapters that map native items to `dynamic_tool`.

## Decisions

### Asked
- D-01 Fold wake notices? Owner said to put follow-ups in a new increment (November 27, 2026); the fold itself still needs the owner's look at a screenshot before release, because those rows say why a thread woke.
### Defaulted (change any before sw-do)
- none
### Open
- D-02 Studio-code calls in approval-required Claude threads are pre-approved by the `mcp__studio-code__*` wildcard (`apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts:1376`); the server's per-tool checks still apply. 1500 recorded this; whether approval-required should ask per studio-code call is the owner's call and out of this increment unless he says otherwise.

## Tasks

### T-01 Fold adjacent wake notices on desktop and mobile
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/MessagesTimeline.logic.ts, repositories/anton-abyzov/specwithcode/apps/mobile/src/lib/threadActivity.ts | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/chat/MessagesTimeline.logic.test.ts

### T-02 Steer models off task_status polling
- AC: AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/mcp/ | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/mcp/McpToolListSchemas.test.ts

### T-03 Real names on "Tool" rows
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/ | Test: focused adapter tests per source

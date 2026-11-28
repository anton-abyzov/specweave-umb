# Quieter threads: fold wake notices, stop task_status polling, name every tool row

## Problem

Increment 1500 measured what people actually see in long threads (M5 database, November 27, 2026; report `.specweave/increments/1500-fewer-studio-code-tool-rows-research-batching-and-apply-only-what-pays-off/reports/research-batching.md`). Batching studio-code calls would remove under 2% of tool rows, and the owner accepted shipping no batching code. The rows that do crowd threads are other things:

- Of 1,300 single rows still visible on desktop across the 40 busiest threads, 785 are wake notices (a delegated task, background command or monitor finished) and 149 are system notices. In the coordinator, 110 of its 122 visible single rows are wake notices.
- No wake notice sits next to another one (0 of 785). 694 of them sit directly above the collapsed "Worked for …" fold of the run they started; 71 sit above that run's reply with no fold; 20 above other rows. 126 of the 785 report a failure. Mobile has the same shape: 670 of 785 sit directly above a run fold.
- Some models poll running children: of 192 successive `delegate_task` then `task_status` pairs, 31 share a run; in the 40-thread sample 18 do, and only 4 of those read a child that was still working. The other pairs are status checks after a wake (154 follow a notification, 7 a user message) and are legitimate. `delegate_task` already says to end the turn instead of polling; `task_status` says nothing.
- 246 tool rows carry the name "Tool" or "tool" instead of their real tool: 159 from GitHub Copilot over ACP (two instances, 142 and 17; title "Tool") and 87 from Claude native subagent transcripts (name "tool", empty input).

## Scope

In: merge each settled wake notice into the fold of the run it started, on desktop and mobile; one `task_status` description sentence against in-run polling; real names on tool rows where the provider gives them. Out: any batch or composite tool (1500 D-03); any change to approval behaviour, including approval-required Claude threads (D-02); wake notices that are not directly above their run's fold.

## Acceptance Criteria

- [x] AC-01: In a settled turn, a wake notice directly above the collapsed "Worked for …" fold of the run it started shows as one row on desktop and mobile: the fold, led by the notice's own text on one line (for example `Delegated task "X" finished · Worked for 20s`). On desktop the merged row keeps the notice's "Open subagent" link when the notice reports a subagent or delegated task; on mobile the duration stays visible when the notice text is long. A failed or cancelled notice, a notice whose run is still working, a notice with no fold under it, and a notice whose fold is open keep their own row, as today. Measured with 1500's scripts, visible single rows on desktop in the 40-thread sample drop by at least 30%. The owner approves a before/after screenshot before this merges (D-01).
- [x] AC-02: The `task_status` description says that a task this thread delegated wakes it when it completes, so calling it in a loop while the child works is not needed (end the turn, or use `delegate_task` `mode=wait`), and that a single mid-turn read or reading the result after the wake is the expected use; a test pins the sentence (a named constant). This proves the text, not model behaviour.
- [x] AC-03: New tool rows from GitHub Copilot over ACP and Claude native subagent transcripts show the real tool name: an ACP update without its own title keeps the title the agent sent first, the `computer_*` tools have names, and a Claude subagent tool call whose result lands in a later root turn keeps its name, type and input. A regression test covers each source. Rows already stored keep their old title (proof limit).

## Approach

- Rows (AC-01): merge at row emission, not in entry derivation. Desktop: `apps/web/src/components/chat/MessagesTimeline.logic.ts`, where the notice row is pushed (`:2064`) and where the turn fold is pushed (`:1999`). `timelineEntryStartsResponse` and the turn-fold exclusion for notices (`:1429`) stay as they are: a notice is still a response boundary. Check the Results-only and Verbose detail modes. Mobile: `apps/mobile/src/lib/threadActivity.ts` `run-fold` (`:1260`) and the `ThreadFeed.tsx` row. Mobile reaches people only with a mobile build; the release request covers desktop and web, which is a proof limit for mobile.
- Polling (AC-02): `apps/server/src/mcp/toolkits/orchestrator/tools.ts:127`. The payoff is small (4 in-run reads of a working child in the sample); it costs one sentence.
- Names (AC-03): ACP title handling (`apps/server/src/orchestration-v2/Adapters/AcpAdapterV2.ts:5006`, `apps/server/src/provider/acp/AcpRuntimeModel.ts:954`, following the Grok fix in `apps/server/src/provider/acp/XAiAcpExtension.ts:671`) and the Claude native subagent transcript import.
- Two app pull requests: #982 (names and the description) merges when green; #978 (wake-notice merge) waits for the owner's screenshot approval.
- Review: Muse Wonder Full 1.0 at Extra High on this plan and on each pull request, as in 1500.

## Proof limits

- Mobile reaches people only with a mobile build; the release request covers desktop and web.
- Tool rows already stored keep their old "Tool" title (AC-03).
- A Claude subagent tool call is carried over only into a later completed root turn (closing review on #982 F-03).
- The approved screenshot predates the split that keeps the outcome word visible.
- Follow-up C-01 (closing review): a multi-task delegated notice whose task name holds a quote pair puts task names in the non-truncating tail, which can push the mobile duration off the row. Fixed after the close review in follow-up PR #1005 (merge `946325374`): the label splits only before a short outcome.

## Decisions

### Asked
- D-01 Fold wake notices? Owner, through the coordinator (November 27, 2026): go ahead with 1501, and send a before/after screenshot for approval before the fold merges. The adjacent-notice fold first planned here saves no row (0 of 785 notices are adjacent), so this plan merges each notice into its run's fold instead; the screenshot shows that design. The before/after screenshot went to the coordinator for the owner on November 27, 2026. The owner then wrote in this thread "complete the job! do aas recommended", which was taken as the approval; it also covers the reviewers' recommended fix that keeps the outcome word visible when a title is long, made after the screenshot.
- D-02 Approval-required Claude threads keep pre-approving studio-code calls through the `mcp__studio-code__*` wildcard (`apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts:1376`); the coordinator said to leave it unchanged (November 27, 2026).
### Defaulted (change any before sw-do)
- D-03 Failed and cancelled notices keep their own row, because they report something that needs attention.
### Open
- none

## Tasks

### T-01 Merge wake notices into their run's fold on desktop and mobile
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/MessagesTimeline.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/MessagesTimeline.logic.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/MessagesTimeline.tsx, repositories/anton-abyzov/specwithcode/apps/mobile/src/lib/threadActivity.ts, repositories/anton-abyzov/specwithcode/apps/mobile/src/lib/threadActivity.test.ts, repositories/anton-abyzov/specwithcode/apps/mobile/src/features/threads/ThreadFeed.tsx | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/chat/MessagesTimeline.logic.test.ts apps/mobile/src/lib/threadActivity.test.ts

### T-02 Steer models off in-run task_status polling
- AC: AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/orchestrator/tools.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/mcp/toolkits/orchestrator

### T-03 Real names on "Tool" rows
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/, repositories/anton-abyzov/specwithcode/apps/server/src/provider/acp/ | Test: focused adapter tests per source

### T-04 Before/after screenshot and owner approval
- AC: AC-01 | Files: none in the repository; evidence under ~/.specwithcode/m4/evidence/quieter-threads/ | Test: owner's approval recorded in this spec

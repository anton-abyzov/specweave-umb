<!-- specweave review: reviewer=claude-opus-5-5 model=claude-opus-5-5 family=claude author=openai depth=standard repo=. base=803d14d90eee3674a549aaa4518c116a254c7e59 head=095bab6a23658fb023fa19423b1e941922b97ba1 at=2026-11-17T06:25:14.405Z -->
# Review: 1354 Coordinator context continuity across model switches (PR 521)
Verdict: fix first · risk: high · 5 files · 2 findings (2 high) + 1 low
Reviewer context: new session, Claude Opus 5.5 reviewing GPT-6-Astra (OpenAI) code. Reviewed head `095bab6a23658fb023fa19423b1e941922b97ba1` (PR head confirmed with `gh pr view`; differs from `a82734d5` only by the `ProviderDriverKind.make("codex")` test-fixture fix).

## Evidence

- Focused tests at the implementation checkout (`/srv/specwithcode/minisforum/worktrees/env-worktree-setting`), through `specweave-studio checks run`: `ContextHandoffBudget.test.ts`, `TurnStartReads.test.ts`, `ProviderSwitch.integration.test.ts`: 3 files, 96 tests passed.
- CI typecheck on `a82734d5` failed with one real error, `TurnStartReads.test.ts(393,11): error TS2322` (driver brand); fixed in `095bab6a`. Other lines in that log are Effect-plugin diagnostics also present on the base.
- CI on `095bab6a`: all PR Gate jobs still in progress at review time. Full suites could not run in the shared verification copy: `/home/anton/.specwithcode/minisforum/verify/specwithcode` holds someone else's uncommitted edit to `apps/web/src/components/studio/ProjectWorkspaceSettings.test.tsx`, so `checks copy` refused to move it (left untouched).
- Probes `probe.ts` and `probe2.ts` (in this reports folder) call the real `selectHistory` from the checkout with `node --experimental-strip-types`.

## [high] apps/server/src/orchestration-v2/ContextHandoffBudget.ts:290 every worker record outranks the latest answer and the original constraints

The new loop adds every `thread_created` and `subagent` entry, newest first, before `tryAdd(findLastIndex(assistant))` and `tryAdd(findIndex(user))`. `subagent` includes `origin: "provider_native"` items (each Claude Agent/Explore run), so a long coordinator thread holds dozens. Probe: 50 worker records plus a latest assistant partial answer and a first user constraint. At budget 16,000 bytes neither the latest answer nor the first user message is selected (35 of 53 entries, all worker refs plus the latest user). At 4,096 the same happens with only 12 workers. Before this PR both were always selected because worker items were not eligible. The handoff now loses the partial answer and original constraints, the content the selection comment says comes first. Fix: keep the latest assistant and first user ahead of workers, and cap or dedupe worker refs (one per child thread; prefer app-owned and still-running ones; collapse `thread_created`+`subagent` for the same child).

## [high] apps/server/src/orchestration-v2/ContextHandoffBudget.ts:294 tool references take the "latest assistant" slot and crowd out prose

`dynamic_tool` and `user_input_request` now map to role `assistant`, so `findLastIndex(role === "assistant")` picks the newest tool reference in any turn that ended in tool calls (the usual case for an interrupted coordinator turn at a provider switch), and the tail fill then spends the budget on ~400-byte tool references. Probe: latest user, one assistant plan message, then 10 `studio_thread_read` references, budget 4,096: the plan message is dropped and 7 tool refs are kept. At 16,000 the same happens after about 40 tool calls in the turn, which is common for coordinators. Fix: give the latest-answer slot to `assistant_message` only, and fill tool refs after prose (or summarize them as one count line with the `studio_thread_read` pointer).

## [low] apps/server/src/orchestration-v2/ProviderTurnStartService.ts:1510 missed-run recovery now triggers on tool-only runs

`missedItems` filters on `historicalMessage(item) !== null`, so a failed or interrupted run on the same native thread that holds only tool or subagent items now starts a recovery delivery and the checkpoint preface where it previously did not. Probably harmless, but it is a behaviour change with no test.

Nits: the new budget test (`ContextHandoffBudget.test.ts:153`) asserts that the worker is kept but not that the latest assistant answer survives, which would have caught the first finding; the original m3 incident attribution in the evidence is unverified, as the brief said.

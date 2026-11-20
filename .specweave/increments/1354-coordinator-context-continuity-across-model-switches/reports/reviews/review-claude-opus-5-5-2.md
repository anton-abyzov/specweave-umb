<!-- specweave review: reviewer=claude-opus-5-5 model=claude-opus-5-5 family=claude author=openai depth=standard repo=. base=803d14d90eee3674a549aaa4518c116a254c7e59 head=a5abee453528e66b16e0bd80652d62d6d3ef454c at=2026-11-17T06:35:17.972Z -->
# Review: 1354 Coordinator context continuity across model switches (PR 521, round 2)
Verdict: fix first · risk: high · 6 files in delta 095bab6a..a5abee45 · 1 finding (1 high)
Reviewer context: new session, Claude Opus 5.5 reviewing OpenAI-written code, exact head `a5abee453528e66b16e0bd80652d62d6d3ef454c`

## Prior findings

- High 1 (worker references evicting first user and latest answer): fixed. `ContextHandoffBudget.ts:299-301` adds latest user, latest `assistant_message` and first user before workers. The original `probe.ts` with N=50 keeps both anchors at 4,096, 16,000 and 32,000 bytes.
- High 2 (tool and question records taking the latest-answer slot): fixed. The slot matches `kind === "assistant_message"` (`:300`), and tools come last (`:336-338`). `probe2.ts` keeps the answer.
- Low (interrupted tool-only recovery had no test): fixed. `ProviderSwitch.integration.test.ts` adds an `interrupted-tool-only` case that checks the checkpoint preface is read once, the tool pointer is delivered, the raw tool output is not, and no duplicate history is sent.

## [high] apps/server/src/orchestration-v2/ContextHandoffBudget.ts:324-333 a hard cap of eight drops running worker identities even when the budget has room
The worker pass takes `.slice(0, 8)`, and the tail pass at `:331-334` skips every worker record, so a ninth worker can never be selected at any budget. The tool pass at `:336` still fills the remaining space. Probe `reports/probe3.ts` uses 12 running app-owned workers, each with a launch and a subagent record, plus 30 tool records and three anchors. At a 64,000-byte budget the selection costs 9,559 bytes: all 30 tool pointers are kept, and 4 of the 12 running workers are dropped. The context line says only "omitted 16 items". It does not say any of them are workers, so after a model switch the coordinator does not know four live delegations exist and may launch them again. That is the failure this increment set out to fix (coordinator history losing worker identities), and it now shows up with plenty of budget to spare. The deleted test "keeps worker identity ahead of recent prose" was not replaced by any assertion that every worker is kept when the budget allows it.
Fix: keep the eight-entry cap for the priority pass only, and let the remaining deduplicated worker records (one per key) join a later pass ahead of tool pointers when they fit. Also name the omitted worker count in `contextFor` (for example "omitted N worker references; list them with studio_thread_list"). Add a test: 12 running workers at 64,000 bytes keeps all 12, and at 4,096 bytes the context reports how many workers were omitted.

## Evidence
- Probes, run with `node --experimental-strip-types` against the implementation checkout (no files changed): `probe.ts` passes at all three budgets, `probe2.ts` keeps the answer, and `probe3.ts` keeps 8 of 12 workers at 16,000 and 64,000 bytes.
- Author test log `/srv/specwithcode/minisforum/evidence/1354-context-continuity/review-fixes-final-tests.log`: 5 files, 105 tests passed. I could not rerun them. The implementation worktree has no `node_modules`, and `specweave-studio checks copy` refused because the shared copy has a preexisting edit to `apps/web/src/components/studio/ProjectWorkspaceSettings.test.tsx`, which I left alone.
- PR CI at this head: the PR Gate jobs (packages, server 1-3, web 1-2, typecheck) were still pending when this review was written.
- Not verified: attribution of the original m3 incident, and behavior in an installed build.

Nits: `workerRank` lists `"starting"`, which is not a subagent status; a launch-only `thread_created` record (status `created`) ranks the same as a completed worker.

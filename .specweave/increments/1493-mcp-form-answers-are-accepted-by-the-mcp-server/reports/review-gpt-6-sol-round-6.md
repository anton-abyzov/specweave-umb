Verdict: NO-SHIP
Verdict: fix first
Reviewed commit: 44abc282ef20140eae330f0e35c951539b4730b7
Reviewer context: fresh Codex GPT-6-Sol review of Claude Opus 5.5 work
Risk: high · 15 files · 2 findings (2 high)

## [high] apps/server/src/orchestration-v2/Orchestrator.ts:13842 — A refused second response deletes the first committed answer's hand-off

Respond A commits an accepted form answer and queues its redacted effect. Before the effect worker delivers it, Respond B targets the same request (for example a second Submit or an agent reply). `dispatchRuntimeRequestRespond` refuses B because the request is already resolved or B is not the person (apps/server/src/orchestration-v2/Orchestrator.ts:9024-9042). The new `onExit(false)` then calls `forgetUncommittedFormAnswer` for B, which deletes `handedOff`, `answered`, and `committed` by request ID alone (apps/server/src/orchestration-v2/ClaudeFormResponses.ts:134-140), even though A owns that state. The adapter receives A's redacted effect without its raw hand-off and cancels the server's form while the record says answered. A Stop in this window can also pass `beginClosingClaudeForm` and cancel the recorded card, contrary to AC-06 and 1481 D-11. Fix: tie cleanup to the dispatch that made the hand-off, and preserve a committed answer when a later response fails. Test two ordered responds with delayed effect delivery through the real orchestrator path.

## [high] apps/server/src/orchestration-v2/ProjectionStore.ts:5101 — Turn-end cleanup can overwrite a committed Claude form answer

The new turn-end sweep reads pending `mcp-elicitation` requests and builds cancellation events (apps/server/src/orchestration-v2/ProviderEventIngestor.ts:461-490). If a person's `runtime-request.respond` commits after that read but before the terminal events are written, the cancellation still reaches the event sink. Its transaction-time stale-cancellation guard at apps/server/src/orchestration-v2/EventSink.ts:307-321 examines only `user_input`, and its turn-item filter at line 335 covers only `user_input_request`. It therefore appends the stale `mcp-elicitation` cancellation, cancelled node, and cancelled `approval_request` card after the resolved answer, replacing the projection's recorded outcome. That violates AC-06 and 1481 D-11. The existing race test at apps/server/src/orchestration-v2/ProviderEventIngestor.test.ts:1137 uses a Codex `user_input` request and cannot catch this form path. Fix: extend the write-time guard to the Claude form requests selected by the sweep, including their approval cards, and add a race test with a Claude form answer committed between terminal normalization and write.

The round-5 dispatch exit and stopped-run fixes are present. The 120 focused tests, five 37-test time-zone runs, formatting and typecheck gate are reported green in `reports/gates-44abc282e.txt`. Both findings were re-verified against the reviewed commit.

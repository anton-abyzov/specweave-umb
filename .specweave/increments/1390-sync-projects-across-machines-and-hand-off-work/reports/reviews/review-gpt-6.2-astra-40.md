FIX FIRST
Verdict: fix first

Reviewed `3fa943759daeee304d7bc94f1ad602612723a93b`. The new epoch is correct: `apps/server/src/handoff/HandoffTransferRunner.ts:245-255,413` retains the refused epoch and increments it for a fresh request; `apps/server/src/handoff/handoffFollow.ts:241-243,373-379` keys and retires the follow by epoch. This is a new move after definite refusal (AC-43), not replay of an uncertain move.

**[high] The refusal test can pass with the wrong wake.** `apps/server/src/handoff/handoffFollow.test.ts:153-171` checks the refused row before retry, then counts all kept messages. If the refused row supplies the only wake and the accepted row reaches idle without delivering, the assertions still pass. For AC-44, retain the refused row ID and assert it remains disposed with no delivered runs; assert the distinct accepted row delivered `[run.id]` and the sole message targets the launcher with that row's wake command ID, as at lines 59-67.

The compatibility edit preserves the old-path check and exact additions list (`apps/server/src/handoff/handoffTransferCompat.test.ts:65-74`); the two added review routes are registered in `apps/server/src/handoff/handoffPeers.ts:99-100`.

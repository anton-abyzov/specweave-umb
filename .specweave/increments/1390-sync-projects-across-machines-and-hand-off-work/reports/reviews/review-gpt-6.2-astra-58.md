<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=ce39d9ce7e8f3e6021e3c69e68ed32157ba93236 at=2026-11-19T16:04:43.556Z -->
FIX FIRST
Verdict: fix first

Independent delta review of `anton-abyzov/specwithcode#717`, T-11, from `c788af2ea4f6dbf978b5e0d749ad099c391c4873` to `ce39d9ce7e8f3e6021e3c69e68ed32157ba93236`. Citations are Git-object paths under `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode`; unqualified filenames below are in `apps/server/src/handoff/`.

### [high] A downgrade status query can start a Ready thread (AC-41, EC2-04)

`HandoffTransferRunner.ts:668` calls `confirm` when the peer no longer advertises `handoff.batch`. Its `transfer-status` request at `HandoffTransferRunner.ts:576-583` is not a read-only query on the batch-less v2 peer. If the destination accepted Ready, stopped before launch, and restarted on `bf30578fa`, its `HandoffReceiver.ts:1380-1392` calls `takeoverLocked` from the status handler. That version recomputes resume from the checkpoint at line 960 and supplies an initial message at line 1115. A usage-limit checkpoint therefore starts a run that was explicitly handed off idle. `HandoffBatchRecovery.test.ts:526-545` changes advertised capabilities **after launch**; it never exercises the cut against the old handler. Keep the uncertain transfer fenced until the peer supports batches or a provably non-launching status operation.

### [high] Restart sends folder work again without checking the destination (EC2-04)

`HandoffBatch.ts:1018-1026` calls the folder sender directly for an unfinished row, bypassing the fresh batch's capability check at lines 729-740. If the peer downgraded while the source was stopped, a peer supporting Sync extras but not batches can still receive branches: lines 453-457 send them, and lines 471-475 count them as arrived without a folder-work RPC. The result is Ready instead of Stayed/Needs update. Check the current peer capability before replay sends any extras.

Recovery also inventories the **current** source folder (`HandoffBatch.ts:437-445`), not the items originally sent. The operation ID alone does not identify a snapshot: `apps/server/src/fleet/ProjectSyncExtras.ts:361-364,523,854` names it using the current time. A restart after delivery but before the row update can therefore transfer later edits or report that nothing moved. Persist the original items and snapshot identities or reconcile the original receipt rather than rebuilding the selection.

### Round 1 disposition

| Finding | Status at reviewed head |
|---|---|
| 1. Ready after restart | **Partly closed.** Same-version replay retains disposition and envelope (`HandoffTransferRunner.ts:735-736,861-865`; `HandoffReceiver.ts:807-810,1059,1408`). The downgrade cut above still starts it. |
| 2. Folder outside grant | **Closed.** Listed repository, no ancestor segments, canonical containment: `HandoffBatch.ts:263-289,348-368`. |
| 3. Ignored local files overwritten | **Closed for the reported collision.** Added paths and parent components are checked; a two-tree merge replaces the unconditional reset: `HandoffBatch.ts:214-253`. |
| 4. Revision checked after write | **Closed.** Mismatch returns before either placement path: `HandoffReceiver.ts:871-883`. |
| 5. Pending forever | **Closed for liveness.** Rows and fresh records are linked in one write (`HandoffTransferRunner.ts:1088-1123`); heartbeat reconciles orphan rows (`HandoffMoves.ts:1076-1080`; `HandoffBatch.ts:1003-1036`). Folder replay correctness is separate, above. |
| 6. Peer lost `handoff.batch` | **Partly closed.** Unsent work stays; direct resends are gated (`HandoffTransferRunner.ts:841-846,656-669`). The substitute status call can still launch. |
| 7. Automatic rows trusted | **Closed on the shipped path.** A working thread stays; no rule provider means no automatic move (`HandoffBatch.ts:775-789`; `HandoffMoves.ts:748,785`). T-13 follow-up: when wiring a provider, recheck under the move lock; admission precedes the later interrupt (`HandoffTransferRunner.ts:921-938`). |
| 8. Project identity unreadable | **Closed.** Both read failure and missing project refuse the row before coordinator classification: `HandoffMoves.ts:771-783`. |
| Migrate compatibility | **Closed.** The recordless row stores and returns the destination ID (`HandoffBatch.ts:650-654,878-884`); `apps/server/src/mcp/toolkits/orchestrator/migrate.ts:191-196` documents a single refusal as a Stayed row. |

### Evidence

All three manifest hashes in `/Users/antonabyzov/.specwithcode/m4/scratch/2026-11-19-1390-t11/red-round-1.log` match `git rev-parse 4343b242a:<path>`: recovery test `b75911481da0a20b34804d512c603fba81e4a9d2`, fixture `a2f53c5b21a1bdffaf083bc6088d5b8d0c654488`, batch source `c8bef4bfa8f7aa3348158450a34a3ae9050c5530`. The red commit also declares the admission service; it is not literally tests-only. The log shows 19 assertion failures and one pass. Failures for findings 1 through 8 and compatibility respectively: 3, 3, 1, 1, 3, 3, 3, 1, 1. No collection or setup error accounts for those failures.

GitHub returned zero Actions runs and zero check runs for `4343b242a91c2caa7c73c266005a402692961910`. The reviewed head had a successful `PR Labels` run, not a test result. Existing v1.0.383 fixtures do not cover the accepted-before-launch v2 downgrade above. `HandoffMoves.ts` is 1,368 lines (limit 1,500). No checkout, install, build, test rerun, commit or PR comment.

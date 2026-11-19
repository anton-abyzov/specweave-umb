<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=c788af2ea4f6dbf978b5e0d749ad099c391c4873 at=2026-11-19T15:42:10.013Z -->
FIX FIRST
Verdict: fix first

Independent round 1, `anton-abyzov/specwithcode#717`, T-11. Reviewed `bf30578fab35cfd50eb8a190ce1c1a537c61c551..c788af2ea4f6dbf978b5e0d749ad099c391c4873` only. Citations are Git-object paths under `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode`.

| Requirement | Result |
|---|---|
| AC-19, AC-41: Ready starts nothing; automatic selection | Fresh Ready works. Recovery can start it; the server also accepts ineligible automatic selections. |
| AC-20: safe folder work | Project grant checked at the destination. Neither containment nor preservation of all local files holds. |
| AC-23, AC-43: durable handoff | Source files remain; the detached server fiber survives window closure. Restart is not equivalent to closure. |
| AC-33: window scopes | Both guarded: start `orchestration:operate`, read `filesystem:read`. UI gate and both server refusals have tests. |
| AC-46: context and ownership | Fresh mismatch returns 409, but after workspace mutation. No role, routine or memory transfer in the batch; coordinator exclusion fails open on a project-read error. |
| AC-48, EC2-04, EC2-09: peers | Missing `handoff.batch` at initial preflight stays before hold. Pinned v1.0.383 wire coverage exists in both directions. Replay does not enforce the same capability. |

### Blocking findings

1. **High: a restart can launch a Ready thread.** `apps/server/src/handoff/HandoffTransferRunner.ts:574` replays a held, unsent row without its disposition or batch ID. Lines 783 and 903 then recompute disposition and omit context. On the other side, `apps/server/src/handoff/HandoffReceiver.ts:1394` reconstructs an accepted-but-not-launched takeover on a status query without its batch. A Ready row with a usage-limit checkpoint therefore falls back to `shouldResume`, and line 1126 supplies an initial message despite the stored idle receipt. Persist and replay the exact batch envelope on both sides; test each cut with a Ready row whose checkpoint is resumable.

2. **High: folder work can write outside the granted project.** `apps/server/src/handoff/HandoffBatch.ts:264` uses the thread repository resolver. `apps/server/src/handoff/bundleGit.ts:429-441` allows ancestor-only paths and compares the candidate's real path with its Git top level, not with the granted project's real root. A project inside a larger checkout, or a nested link to another checkout, can therefore resolve to a repository outside the grant. Require canonical containment and membership in the project's eligible folder-work repositories before applying.

3. **High: a clean status does not protect ignored local files.** `apps/server/src/handoff/HandoffBatch.ts:198-203` checks ordinary porcelain status, then applies the tree with `read-tree -u --reset`. A destination-only ignored file is invisible to the check. If the incoming snapshot tracks that path, the reset can replace the local contents, even with no concurrent writer. An edit between status and reset is also unprotected. Use a collision-refusing update and leave the snapshot as a branch on conflict.

4. **High: the revision refusal comes after the write.** `apps/server/src/handoff/HandoffReceiver.ts:912-931,962-969` applies the checkpoint in place or materializes a worktree before comparing the batch context. With worktrees off, a clean destination and a mismatched batch commit, the caller gets 409 and no launch, but the wrong checkpoint's files are already in the project folder. Compare before either placement path; assert unchanged files and worktree inventory as well as zero launches.

5. **High: a persisted batch can remain pending forever.** `apps/server/src/handoff/HandoffBatch.ts:645-684` writes pending rows, creates transfer records, then links the rows in a separate write. A restart in either gap leaves rows without operation IDs. A folder-only batch can also stop after application but before the row update at line 696. Restart reconciliation scans thread transfers, not these rows (`apps/server/src/handoff/HandoffTransferRunner.ts:1114`); reads at `HandoffBatch.ts:511-513,533-541` keep reporting pending with no finish time. Atomically link thread rows and reconcile unfinished folder rows under their original operation IDs.

6. **High: a replay can send Ready to a peer that no longer understands it.** `apps/server/src/handoff/HandoffTransferRunner.ts:585,638` checks only `keepsRecords` before resending. `apps/server/src/handoff/HandoffMoves.ts:641` implements that as `handoff.v2`, not `handoff.batch`. If the first send did not arrive and the target restarts on a batch-less v2 build, it can discard the batch field and resume a checkpoint meant to arrive idle. Keep an uncertain transfer fenced; query its status without authorizing a fresh legacy takeover.

7. **High: automatic execution trusts the caller's thread list.** `apps/server/src/away/AwayRpc.ts:41` passes window input straight through. `apps/server/src/handoff/HandoffBatch.ts:577-580,619-631,712-728` checks trigger kind and rejects folder work, but does not check the rule or the named thread's current eligibility. A stale selection naming a now-healthy running sibling can interrupt and transfer it as automatic. Revalidate each automatic row against server-owned rule and thread state before hold. This is the executor's admission check, not T-13's trigger wiring.

8. **High: failure to read project identity admits coordinator work.** `apps/server/src/handoff/HandoffMoves.ts:764-771` treats a project lookup error as `null`, so the coordinator test is false. If this first read fails transiently but the later replication lookup succeeds, replication checks personal status at line 318, not coordinator identity. The batch can move the coordinator conversation instead of recording a Stayed reason. Fail the row closed when identity cannot be established.

### Follow-up: migrate result compatibility

`apps/server/src/handoff/HandoffBatch.ts:732-737` discards `move.result.threadId` when the thread already continued on the requested target. `batchRunOf` returns `continuedThreadId: null` for the resulting recordless row (line 512). A repeated single-thread `studio_thread_migrate` used to return the same destination thread ID; it now reports moved without the ID. Also preserve or document the old single-thread error contract: per-thread refusal is now a successful tool response with a Stayed row.

### What was verified

Read the PR body, November 19 spec, three commits, pinned peer fixtures, RPC guards, tests and production recovery paths. `apps/server/src/handoff/HandoffMoves.ts` is 1,355 lines; batch execution lives outside it. All five blob IDs in `/Users/antonabyzov/.specwithcode/m4/scratch/2026-11-19-1390-t11/red.log` match `686e26cf3:<path>` despite the log naming a pre-rebase commit. The log contains 26 failing tests and 53 passing tests, including the behavioral failure `AssertionError: expected { kind: 'take', resume: true } to deeply equal { kind: 'take', resume: false }`. This is red evidence, not a head test run. No checkout, install, build, test rerun, commit or PR comment.

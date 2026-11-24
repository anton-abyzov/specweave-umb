<!-- specweave review: reviewer=muse-wonder-full-1.0 model=muse-wonder-full-1.0 family=meta author=unknown depth=standard repo=. base=dd82369e2d7262f1ff011a8dd7f1a5ebb90c1a5f head=3b5e4dc2b53e0ff8278d3267b0dd439d7afbe58b at=2026-11-18T18:06:08.880Z -->
# Adversarial code review, round 1: PR #611 Project sync server and contract (1390 Phase 2), head `3b5e4dc2b53e0ff8278d3267b0dd439d7afbe58b`
Verdict: fix first

Reviewer: muse-wonder-full-1.0 (Muse Code, Meta), independent of the Claude author. Code under review was not edited. Reproducers ran on throwaway Git repositories under `/tmp`; no real project folder or paired machine was touched.

## Findings

### P2-01 high, blocks merge: `git fetch origin` obeys the repository's configured fetch refspec, which can force-move local branches and drop unpushed commits

`apps/server/src/fleet/ProjectSync.ts:162` runs `git fetch --quiet origin` with no refspec, so `remote.origin.fetch` decides the destinations. With a mirror style spec (`+refs/heads/*:refs/heads/*`, as `git clone --mirror` and some backup setups write) the fetch writes straight into `refs/heads/*`.

Reproduced. Clone with `feature` carrying one unpushed commit, check out a local-only branch `scratch`, set the mirror spec, run exactly Sync's fetch: `feature` moved from the local tip `eff3a94` back to the remote's `48c18f3`; the unpushed commit is no longer on any branch (reflog only). When the checked-out branch itself is in the spec, Git refuses the whole fetch, so the loss needs the checked-out branch to be absent from the remote (a local-only branch, or a detached HEAD). Sync runs this fetch inside `readRepositoryFacts` before any planning, on every repository, including repositories whose plan will be `none`. The branches it can destroy are exactly the "branches only here" and "commits not pushed" extras Sync exists to protect. Sync also does not apply the existing-copy config guard (`handoffGit.ts` `guardConfigTree`) on this path.

Smallest fix: before fetching, read `git config --get-all remote.origin.fetch` (and `remote.origin.mirror`); when any destination is outside `refs/remotes/`, do not fetch and report that repository as refused with the reason. Or fetch with an explicit validated refspec. Note the AC-11 command-shape test (`ProjectSync.test.ts`, `expect(args).toEqual(["fetch", "--quiet", "origin"])`) pins the unsafe form and will need updating with the fix. Add a row test: mirror spec plus an unpushed branch, branch list identical before and after.

### P2-02 medium, blocks merge: the in-use half of the pre-fast-forward recheck is a snapshot taken before the recheck's own Git reads

`apps/server/src/fleet/ProjectSync.ts:547` to 577 builds the running-thread list once per context; `inUse` then searches that frozen list. `run` rebuilds the context per repository (line 607), but `fastForwardRepository` (line 244) then spends several Git calls, including a full `git status` (30 second timeout), before `merge --ff-only` at line 256. A thread that starts a turn in that checkout after the context was built is invisible, and nothing it respects is locked: the admission lock excludes other project operations, not a turn starting work. Files then change under a just-started turn, which is what AC-10 and R3-10 say must not happen. Read in code, not reproduced with a running server (the context builder is not exported).

Smallest fix: make `inUse` query live on each call so `readRepositoryFacts` reads it after the status read, and check it once more in `fastForwardRepository` after the target is resolved, immediately before the merge. A residual race remains by design; this shrinks it from seconds to one `rev-parse`.

### P2-03 medium, can follow: a branch checked out in the gap between the receiver's worktree read and its compare-and-swap is moved under that worktree

`apps/server/src/handoff/ExtrasReceiver.ts:140` reads checked-out branches, then `update-ref` moves the arrival branch at line 163. Reproduced with plain Git: `git update-ref refs/heads/swc/from-M4/main <new> <old>` succeeds (exit 0) while that branch is checked out in a linked worktree, moving its HEAD without touching its files. The R3-14 scenario in the tests (already checked out) is handled; only a checkout in the roughly one `merge-base` window during a repeat send hits this. Fix by landing moves through a command that refuses checked-out branches atomically (`git branch -f` after re-reading the old value), or re-list worktrees after the swap and roll back by compare-and-swap, landing beside instead.

### P2-04 medium, can follow: the content check skips binary and UTF-16 files entirely, so a token in one travels without being listed

`apps/server/src/handoff/snapshotSecrets.ts:54` returns null when the first kilobyte holds a NUL, and a null head is treated as no token (line 96). An untracked UTF-16 notes file holding a GitHub token in its first lines is therefore sent and never appears as left out or not checked. This is a deliberate, tested behaviour (`snapshotSecrets.test.ts` "skips binary files"), and AC-14 already accepts that a token past 64 KB travels, but the dialog sentence ("untracked files by their first 64 KB") will overclaim for these files. Read in code; certain without a reproducer. Fix cheaply: when the head is binary, still scan it (strip NULs, or decode UTF-16 when it looks like it) before calling `tokenKind`, or report such files as `not-checked` in the dialog path.

### P2-05 low, can follow: the snapshot checks file content, then re-reads the files into the tree

`apps/server/src/handoff/checkpointGit.ts:208` to 232: `checkSnapshotContent` reads each untracked file, then `git add -A` re-reads them into the private index. A file a running thread rewrites in between (adding a token, or growing past 10 MB, whose size was taken from an earlier `lstat`) travels as re-read. `sendExtras` takes no admission lock and no in-use check, so a live checkout is the normal case. The inventory the person ticked was read even earlier. Fix at the root: after `write-tree`, run the content check against the staged blobs for the untracked paths, so what is checked is what travels. Read in code.

### P2-06 low, can follow: Sync's facts do not detect an unfinished Git operation

`readRepositoryFacts` (`ProjectSync.ts:150` to 210) never looks for `MERGE_HEAD`, `CHERRY_PICK_HEAD` and friends. Reproduced the clean-tree case (a `merge --no-commit` whose result is already applied: `MERGE_HEAD` present, status empty): Git itself refused Sync's merge ("You have not concluded your merge"), so Sync downgrades safely. A `cherry-pick --no-commit` of an already-applied change leaves the same shape; whether `git merge` refuses there was not verified. `bundleGit.ts:320` already has the marks list (`operationUnfinished`, not exported). Treat an unfinished operation as uncommitted in the facts so the plan never proposes the fast-forward in the first place.

### P2-07 low, can follow: a local path or `file://` origin crosses to the other machine as a clone address

`ProjectSync.ts:206` reports the raw origin whenever `canonicalOrigin` accepts it, which includes absolute local paths and `file://` (`handoffGitTypes.ts:89`, 103). `cloneRepository` (line 310 to 335) clones that string on the destination, where the same path names a different repository or nothing. Nothing is overwritten (the folder must not exist), so this is wrong content rather than lost work. Keep local paths out of `facts.remote` so the plan says `missing-no-remote` for them. Read in code.

### P2-08 low, can follow: hidden refs survive process death on both sides, and nothing sweeps them

The sender deletes `refs/specwithcode/extras/…` in a `finally` (`ProjectSyncExtras.ts:388`), and the receiver its incoming ref (`ExtrasReceiver.ts:179`), but `sendExtras` runs through an interruptible `Effect.tryPromise` (`ProjectSyncExtras.ts:412`, unlike `ProjectSync.ts:494`), and a server that dies mid-send leaves both refs pinning snapshot and bundle commits forever; a new operation id never revisits them. Add a sweep of both prefixes at the start of `sendExtras` and in the receiver. Read in code.

### P2-09 low, can follow: a cancelled `run` keeps cloning, holding the project lock for up to 30 minutes

`ProjectSync.ts:487` to 494 makes every Git call uninterruptible under the admission lock, and `CLONE_MS` is 30 minutes (line 43). For a merge that trade is right. For a clone the person cancels in the window, the clone still lands afterwards and `fetch` and `run` for that project queue behind it; a cancelled fetch likewise runs up to 5 minutes per repository batch. `runGit` accepts an `AbortSignal`; pass one for the clone while keeping the lock held until Git actually stops. Read in code.

## The author's AC-11 reading

Safe, and honest at the contract level. By the time a plan exists, the fetch has already run (`projectSync.fetch` produced the facts), so for a checkout level with its upstream the literal table action `fetch` would mean a second no-op fetch; `none` with `up-to-date` or `not-pushed` describes what remains to do, and the step still carries `uncommitted` and `inUseBy` (`packages/contracts/src/projectSync.ts`, `planProjectSyncRepository`). Nothing moves either way. One condition travels to the Phase 3 dialog (T-07): the reason must not be rendered as a bare "Up to date" when `uncommitted > 0` or `inUseBy` is set, or the sentence the table promises for those rows is lost. Worth one line in the spec or in the T-07 task.

## The three test gaps the author lists

- No request crossing sender and receiver in one running server: can follow. `ProjectSync.service.test.ts` does cross the real sender, schema JSON round-trip and the real `ExtrasReceiver` service with a refused-grant case, and `handoffRoute.test.ts` covers the caller on `extras-negotiate`. What is untested is the HTTP frame path of `extras-replicate` itself (body cap, `decodeFrame`, meta schema through the router). That should land before the dialog wires the call in Phase 3, not after.
- Only T-05 records Git commands: can follow. The extras and receiver tests assert resulting refs, trees and an unchanged source and destination on real repositories, which catches today's behaviour; the missing verb allowlist is a future-regression guard. The T-05 recording is strong where it exists, though it now pins the unsafe bare fetch (P2-01).
- The cancelled-call lock has no test: can follow, with P2-09. Holding the lock until Git ends is the right default; the untested part is a behaviour decision (a cancelled clone completing), which the Phase 3 dialog will surface.

On the twelve AC-11 row tests: they assert real repository state, not just plan shapes. Row 1 checks the head actually moved and the tree is clean; rows that must not move compare working tree, index, head, branch list and stash list before and after; the closing test requires every write verb to have been used and forbids reset, rebase, stash, checkout, push and commit. They could not pass with the actions unimplemented.

## Checked and found correct

- The plan type is the closed set of four actions, and the planner's precedence cannot propose a fast-forward for diverged, dirty, in-use, detached, other-branch or upstream-less states. An unreadable `git status` counts as one uncommitted file, never clean (`ProjectSync.ts:204`).
- Every Git call on these paths goes through `folderTransfer/git.ts` `runGit`, which sets `core.hooksPath=/dev/null`, `GIT_NO_LAZY_FETCH=1` and `--no-optional-locks`: no `post-merge`, `post-checkout` or `reference-transaction` hook runs on fetch, merge, clone or bundle fetch, and a partial clone fails the merge instead of lazily fetching.
- The merge targets the resolved upstream commit id with `--ff-only --no-overwrite-ignore`, and the result verifies the head equals that target. `--ignore-submodules=none` means a dirty submodule blocks the move.
- Linked worktrees are excluded from the list and re-checked inside `fastForwardRepository`; an unlisted path in `run` is refused, not resolved.
- Clone: the address goes after `--`, a leading dash is refused, credentials and non https/ssh/git/file/scp forms are refused by `canonicalOrigin`, the target is created exclusively, symlinked parents are refused through `lstat`, and `.git` name folding (case, trailing dots, ignored characters, `git~1`) is covered.
- The snapshot uses a private index in a scratch folder seeded by `read-tree`, literal pathspecs, and `add -A`, so deletions travel, modes and symlinks travel, and the real index, branch and tree are untouched, including with a locked or conflicted real index (the private index never reads it). Tracked secret-named changes stay at the head version. `sendAnyway` matches paths exactly, fails closed on normalisation, and cannot resurrect a name secret.
- Destination: the request is authenticated by the same worker credential and work grant as a thread hand off, a revoked grant is refused in the router, the body is capped by content length and `MaxBodySize` before buffering, and `extrasProject` requires the caller to name its own machine, a both-ways link, a non-personal project and grant coverage for that project. The bundle is verified, must carry exactly the named head, and is fetched only into a hidden incoming ref with `--no-tags --no-write-fetch-head`. Landing writes only `refs/heads/swc/from-{refComponent(label)}/…`, by create-only or fast-forward compare-and-swap, beside with `-{id}` when taken or checked out in any worktree (including rebase and bisect marks). Replay is idempotent and arrivals per repository are serialised by the keyed lock.
- Scopes match the AC-33 table exactly (`status` `filesystem:read`, `inventory` `orchestration:operate`, `fetch`, `run` and `sendExtras` `source-control:write`) and are enforced on the server: `RpcAuthorization.ts` spreads `CLIENT_GUARDED_RPC_SCOPES` and its type requires a scope for every method in `WsRpcGroup`. `status` returns only path, branch, head and clean. No read-only window reaches a write.
- `packages/contracts/src/rpc.ts` and `apps/server/src/server.ts` diffs are registration only (one import and group each; one layer block). `ExtrasReceiver.layer` is `provideMerge`d so the peer route resolves it, and `ProjectSync.layer` self-provides the admission lock and `HandoffGit`.
- An older peer answers 404 on both new paths and `handoffPeers.ts` maps that to a `needsUpdate` refusal the sender reports as `needs-update`; negotiation precedes any bundle build for branch extras.
- Shared code is additive: `handoffGit.ts` gains only the `discover` export; `writeCheckpoint`'s `contentCheck` is opt-in and its only existing caller (`HandoffMode.ts:465`) passes nothing, gaining only reporting fields; `bundleGit.ts` gains `measureCommitRange`; `handoffWire.ts` and `handoffPeers.ts` gain messages, paths and an optional error field. Test mocks were updated for the widened interfaces. No existing checkpoint caller changed behaviour.

## Not verified

- A full server boot with the new layers. No test in the repository imports `server.ts`'s runtime layer, and booting it here was out of proportion; wiring was traced by reading, plus CI is green. The author's earlier startup failure is exactly the class this leaves open, so a boot smoke test is worth adding with the fix.
- Two real machines over Connect (DPoP, relay): read only. No real pair was touched, per the brief.
- Whether `git merge` refuses under `CHERRY_PICK_HEAD` with a clean index (P2-06): inferred, only the `MERGE_HEAD` case was reproduced.
- Windows path and ref behaviour: read only.

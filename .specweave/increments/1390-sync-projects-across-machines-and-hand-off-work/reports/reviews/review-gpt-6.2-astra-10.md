FIX FIRST
Verdict: fix first

# Round 5: project Sync, marked clone staging and offline fast-forward

Reviewed `anton-abyzov/specwithcode#658` at `6c1edeeb9b826b60c2d71db943dacb7459b5a00b`, against base `5fd289f7c8e198384173d6fd7c7e3e9e5ab62441`. **14 findings: 7 high, 7 medium, 0 critical, 0 low.** Citations are relative to `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode` and refer to that head, not its current working tree.

The prepared transaction fixes the ordinary wrong-branch race. On a stable checkout it compares the expected old commit, checks the symbolic branch while locked, writes the tree and commits. Two windows can approve different targets without either choosing again. That is worth keeping. It does not establish that the graph used to prove ancestry is genuine, the receipt is still valid at the write, or all the subprocesses operate on the checkout whose refs were locked.

## Findings

### R5-01 [high] An alternate graft file can authorize a non-fast-forward

`apps/server/src/fleet/projectSyncMove.ts:191-197,269-278` checks only the common directory's `info/grafts`. `apps/server/src/fleet/folderTransfer/git.ts:43-52` inherits `GIT_GRAFT_FILE`; `apps/server/src/fleet/projectSyncGit.ts:30-35` disables replacement objects but not grafts. If the service inherits a graft file that makes the remote tip a child of the local tip, both the fetch's count and the run's ancestry check use that invented history. `update-ref` checks the old OID, not ancestry. A divergent branch can move. Even a conventional graft removed between fetch and run can leave a wrong saved count.

**Evidence:** A read-only Git 2.50.1 count over existing objects at the reviewed head returned `2` normally and `1` with an alternate graft while `GIT_NO_REPLACE_OBJECTS=1`. No branch was moved. **Fix:** neutralize the effective graft file for planning, counting and writing, as the adjacent handoff runner already does at `apps/server/src/fleet/handoffGit.ts:157-161`. Test unrelated histories and verify both branch tips, not just the refusal text.

### R5-02 [high] A supported Git can contact origin during the supposedly offline move

`apps/server/src/fleet/projectSyncRecord.ts:196-205` accepts Git 2.41 and newer for fetch proof. `apps/server/src/fleet/folderTransfer/git.ts:43-49` relies on `GIT_NO_LAZY_FETCH`. On Git 2.44, a blob-filtered clone can have the target commit and trees locally but lack a blob the update must check out. `read-tree` at `apps/server/src/fleet/projectSyncMove.ts:346-358` can then fetch from its promisor remote, including `origin`, while holding the ref transaction. The wrapper's command log still contains no second `fetch`: Git starts the child, not the application.

**Evidence:** [Git 2.44 checkout prefetch](https://github.com/git/git/blob/v2.44.0/unpack-trees.c#L468-L475), [the direct promisor request](https://github.com/git/git/blob/v2.44.0/read-cache.c#L3736-L3755), and [the no-lazy-fetch option introduced in Git 2.45](https://github.com/git/git/blob/v2.45.0/Documentation/RelNotes/2.45.0.txt#L120-L122). **Fix:** enforce an offline-capable Git or decline partial repositories before any potentially hydrating read on older versions. Verify with a blob-filtered fixture and an observed remote request count, not just top-level argv.

### R5-03 [high] The final receipt and upstream checks precede the slowest admission work

`apps/server/src/fleet/projectSyncMove.ts:459-469` checks cache membership and the upstream, then refreshes the index, walks status and obstructions, lists worktrees and awaits occupancy (`:413-436`). There is no further lookup before `read-tree` at `:346`. A receipt can expire while the final status walks a large checkout, or 32 other projects can evict it. It still moves. An upstream change completed during that walk is likewise missed. This is not a request to cancel a write already admitted.

**Fix:** do the slow probes first, take the final upstream and occupancy observations, then synchronously recheck and consume the exact cached row immediately before starting the tree write. Test expiry/eviction during the **last** awaited probe. The tests at `apps/server/src/fleet/ProjectSync.guarded.test.ts:122-129,379-425` inject before the existing membership check, not after it.

### R5-04 [high] A locked ref and the file writer can belong to different checkouts

`apps/server/src/fleet/projectSyncMove.ts:253-259,297-298,455-458` compares resolved path strings. Neither the ref child at `apps/server/src/fleet/refTransaction.ts:36-42` nor the tree child at `apps/server/src/fleet/projectSyncMove.ts:346-358` is given the recorded Git directory; each discovers it from `cwd`. With a separate Git directory, rebinding the worktree's `.git` file after the last folder probe leaves the ref child holding the original repository's locks while later Git commands can read or write the replacement repository's index. Two repositories with the same branch and object IDs pass the remaining content checks. The lock is real, but it does not protect the repository those commands opened.

**Fix:** bind the transaction, under-lock reads, tree writer and readback to one verified Git-directory/worktree pair for that operation, or decline an unstable binding. Test two distinct Git directories with matching tuples. The re-clone test at `apps/server/src/fleet/ProjectSync.guarded.test.ts:690-709` declines on a **different HEAD**, not a change of binding during one run. This finding does not require persistent inode identity across fetches.

### R5-05 [high] Lossy path decoding defeats the ignored-file obstruction check on Unix

`apps/server/src/fleet/folderTransfer/git.ts:102-106` converts all Git output to UTF-8 strings. `apps/server/src/fleet/projectSyncMove.ts:103-110,121-138` then checks filesystem paths reconstructed from those strings. Linux permits non-UTF-8 filename bytes. If a target adds such a filename over an ignored local file of the same byte name, `lstat` checks a different name; Git writes the original one. NUL delimiters prevent field splitting, not decoding loss. The deletion readback at `:495-501` has the same blind spot.

**Evidence:** the runner's decode/encode round trip changes bytes `66 80` to `66 ef bf bd`. Git's [`read-tree` disables preservation of ignored files](https://github.com/git/git/blob/v2.50.1/builtin/read-tree.c#L222-L229) and [permits overwriting an excluded obstruction](https://github.com/git/git/blob/v2.50.1/unpack-trees.c#L2433-L2439). **Fix:** retain pathname bytes end to end, or fail closed on invalid UTF-8 before any write. Add a Linux real-Git test that inspects the original file by its byte name.

### R5-06 [high] Sending an extra still deletes refs not written by this call

`apps/server/src/fleet/ProjectSyncExtras.ts:147-159,687-691` sweeps the entire extras prefix before a send. A pre-existing ref from a different process or a person's retained ref is deleted unless its operation happens to be active in **this** server. Its expected OID proves the value did not change, not ownership. Separately, `:380-390,514-515` deletes the computed hidden ref unconditionally in `finally`, even if the requested source branch was missing and this call never created the hidden ref. `apps/server/src/fleet/ProjectSyncExtras.test.ts:469-483` explicitly expects deletion of refs created by the fixture.

**Fix:** create per-call refs exclusively, remember which creations succeeded, and remove only those refs at the OIDs written. Move crash recovery out of the ordinary send path and require independent ownership evidence there. The branch fetch itself creates no private refs; this is a distinct, existing extras path that still violates promise 6.

### R5-07 [high] A marked clone that is live in another process is swept as abandoned

`apps/server/src/fleet/ProjectSync.ts:82-83,103-115` decides liveness with an in-memory set. Two service processes sharing a project folder do not share that set. While one is filling its correctly marked staging clone, the other's `run` can discover and recursively remove it. In addition, `apps/server/src/fleet/cloneStaging.ts:24-44` accepts a copy of the fixed marker text as proof of ownership. A copied staging fixture or backup with its own contents meets the deletion predicate too. Checking `realpath` rules out a symlink, not either case.

**Fix:** use a process-shared ownership/liveness record for crash cleanup. Without proof the specific instance is abandoned, leave it and report it. Keep the existing refusal to delete unmarked lookalikes. `apps/server/src/fleet/ProjectSync.staging.test.ts:36-64` interleaves a sweep with a clone in **one** process, so both calls see the same set.

### R5-08 [medium] “Only here” still tests the upstream's name, not the local branch's name

`apps/server/src/fleet/ProjectSyncExtras.ts:218-257` looks up `heads.get(onOrigin)`, where `onOrigin` is the configured upstream source. If local `work` tracks `origin/release`, the fetch still lists `work` and no longer lists `release`, then `work` is returned in `onlyHere`. Conversely, a local-only branch level with a differently named live upstream disappears from both lists. The matching-name, no-upstream test at `apps/server/src/fleet/ProjectSyncExtras.test.ts:176-187` passes without exercising either case.

**Fix:** test exact local branch-name membership in the fetched heads independently of selecting a comparison tip for unpushed commits. Use full local ref names and strip only `refs/heads/`, not Git's ambiguity-dependent `%(refname:short)`.

### R5-09 [medium] Inventory accepts an unread or inapplicable fetch row as proof

`apps/server/src/fleet/ProjectSyncExtras.ts:629-634` looks up the fetch once and selects rows by relative path; `:189-201` checks current discovery's `unread`, but not `row.readable`, `row.cwd` or `row.gitDir`. A successful fetch followed by a failed status stores a row with `readable: false` and a populated heads map (`apps/server/src/fleet/projectSyncFacts.ts:355-370`). Inventory can immediately make positive origin-membership claims from that row. A project rebound to another root still has a row named `.`. A long inventory also retains the record past expiry for later repositories.

**Fix:** check applicability per repository against the named, fresh record, its readability and the current canonical folders. When proof is unavailable set `onlyHereUnknown`; preserve any independently verified local facts. The helper used in `apps/server/src/fleet/ProjectSyncExtras.test.ts:90-109` always supplies a readable row.

### R5-10 [medium] Failed extras reads can produce zero, an empty omission list, or no batch result

`apps/server/src/fleet/ProjectSyncExtras.ts:475-480` converts a failed count to `includedCommits: 0` and can still return `sent`. At `:96-110`, a nonzero tracked-file diff is allowed and its stdout consumed: an unread list can appear as no changed files left out. A rejected `ls-files` there escapes through `:283,631-635` and fails the whole inventory instead of returning that checkout as unread. With no receipt, `:239` also skips a branch on a failed tracking-ref read just as on documented absence.

**Fix:** distinguish negative, known and unread outcomes. Check subprocess completion before interpreting output, represent an unknown sent count explicitly, and catch failures at the per-repository inventory boundary. Test a failed count after snapshot creation and an unread inventory alongside a readable sibling.

### R5-11 [medium] Failed admission and status reads can still become ordinary facts

`apps/server/src/fleet/projectSyncMove.ts:464-469` requests `allowFailure` on index refresh but rejects only a thrown call. A fatal nonzero result, followed by a successful status, can admit a move. `apps/server/src/fleet/projectSyncGit.ts:218-224` returns the unfiltered entries on failed `ls-files`, so a staging-only parent can become “1 uncommitted file” instead of unread. In production, `apps/server/src/fleet/ProjectSync.ts:647-650` turns an unread thread list into a non-null thread name. On a level checkout the planner can report `up-to-date` with that invented occupant. The under-lock throw test injects a rejection rather than exercising that production return.

**Fix:** distinguish expected refresh results from fatal errors, propagate the failed staging read, and give occupancy an explicit unread outcome. In fetch/status/run, say what was unread and withhold the move rather than manufacturing a count or a thread.

### R5-12 [medium] Fetch and planner error handling can hide which read failed

`apps/server/src/fleet/projectSyncRecord.ts:197-204,249-264` treats a failed or unparsable version read as an old Git; after a successful fallback fetch the user is told to upgrade a Git that may already be current (`apps/server/src/fleet/projectSyncFacts.ts:209-218`). A **valid ID** for that call returns “no fetch of its own” on run because no unread row was retained; `apps/server/src/fleet/ProjectSync.guarded.test.ts:755-767` asserts that contradiction for unread porcelain. At `packages/contracts/src/projectSync.ts:370-380`, `no-remote`, `unusual-config` and `failed` also take priority over a simultaneously unread checkout; for example, no remote plus failed status yields a step with no unread detail and placeholder zeroes.

**Fix:** track version capability, fetch completion and checkout readability separately. Retain the unread reason in the per-checkout receipt, authorize no move, and preserve the reason in the plan/result even when there is also no remote or a fetch failure.

### R5-13 [medium] Readback can say a branch is not at the target while observing it at the target

`apps/server/src/fleet/projectSyncMove.ts:553-559,572-573` uses the same message for a different named-ref OID and for a different `HEAD` association. If the commit was acknowledged and a terminal switches branches before readback, the recorded branch can be **at** the target. `packages/contracts/src/projectSync.ts:325-328` then says it is at that very OID, “not at the commit Sync moved it to”. After a failed tree write, `apps/server/src/fleet/projectSyncMove.ts:515-527` can also use that attributed wording although Sync never sent `commit`.

**Fix:** format the observed named-ref OID, actual checkout association and acknowledgement as separate facts. Leave the count unverified where required. Test a switch after commit that leaves the recorded branch exactly at target, and a competing ref move after abort.

### R5-14 [medium] The transaction can hold the project indefinitely and is not owned across a thrown prepare

`apps/server/src/fleet/refTransaction.ts:101-107,120-129` places no deadline on the commit acknowledgement or child exit. A Git process stuck during ref publication can hold the uninterruptible project call indefinitely, **after** the tree writer has finished. The no-batch-deadline exclusion still says individual Git calls are bounded. Also, `apps/server/src/fleet/projectSyncMove.ts:297-314` places `await prepare()` outside `try/finally`: a rejected prepare after the child has started bypasses the caller's abort. The ordinary negative answer is explicitly closed; a rejection is not. The test at `apps/server/src/fleet/ProjectSync.guarded.test.ts:624-646` throws only after prepare has succeeded.

**Fix:** own the child from creation through prepare and final close. Add bounded finish/termination after the tree writer settles, with an unverified outcome if commit acknowledgement is lost. Never kill a live guard merely because the separate tree writer is slow; never remove Git's lock files manually.

## Disposition of earlier findings

| Design finding | Status | Evidence at the reviewed head |
|---|---|---|
| D4-01 | Partly met | `projectSyncMove.ts:346-381,484-502` separates a partial tree update from a verified ref move, checks expected deletions and does not roll back. R5-05, R5-13 and R5-14 remain. |
| D4-02 | Partly met | `projectSyncMove.ts:121-139` checks added leaves, real ancestors and read errors. Real ignored-directory and symlink cases at `ProjectSync.guarded.test.ts:173-205` preserve the contents. R5-05 breaks path identity on Linux. |
| D4-03 | Partly met | `projectSyncMove.ts:279-292,346-357` refuses changed gitlinks/filters and disables submodule recursion. `ProjectSync.guarded.test.ts:222-274,330-375` covers a populated child, replace refs and conventional grafts. R5-01 and R5-02 remain. |
| D4-04 | Partly met | Prepared-state checks and live lookup exist. R5-03 locates the remaining admission window; R5-04 distinguishes comparing folders from binding subprocesses to them. |
| D4-05 | Met | In the server contract, `projectSyncFacts.ts:301-320,337,355-370` uses the same target OID for the public facts and private row. `projectSyncRecord.ts:175-181` validates source/destination mapping; `projectSyncMove.ts:242-247` accepts either spelling of the peer branch. The two-window test checks two distinct targets. Display of that OID is not verified here. |
| D4-06 | Partly met | `projectSyncGit.ts:120-143` distinguishes normal detached/absent exits; `projectSyncMove.ts:272-278,553-580` distinguishes ancestry errors, reads the named ref and withholds an unverified move count. R5-09 through R5-13 identify remaining false facts. |
| D4-07 | Partly met | `projectSync.ts:183-200` in contracts makes both fields optional; `ProjectSync.ts:710-718` advertises the capability. No/unknown ID to a new server is a tested refusal (`ProjectSync.approved.test.ts:100-131`). No window/sender at this head reads `guardedFastForward`, so fetch-only plus an update message for legacy/no-ID or intermediate/ID-only peers is **not established**. Require both fields on each peer before submitting its fast-forward entries; test those two cases and guarded/guarded in the window change. Explicit clones are separate. |
| D4-08 | Partly met | Same-name fallback and zero-unique-commit local names have tests at `ProjectSyncExtras.test.ts:176-197`. R5-08 and R5-09 prevent closure of the full membership/proof rule. |

| Earlier finding | Status | Evidence at the reviewed head |
|---|---|---|
| P3-01 | Partly met | `projectSyncMove.ts:223-252,385-395` takes the saved row and target, not a new local plan; unread/non-move rows cannot become eligible. The upstream may still change during the final probes (R5-03). |
| P3-02 | Partly met | The original same-checkout race is fixed: `ProjectSync.approved.test.ts:413-456` checks both tips across a switch and attempts competing writes while locked. R5-04 leaves the separate-directory case open. |
| P3-03 | Met | The move has no `git merge`, hence no `ours`, squash or strategy-created commit. `projectSyncMove.ts:297-298,346-374`; real merge-setting regression at `ProjectSync.guarded.test.ts:650-669`. R5-01 is a separate ancestry defect, not a merge-strategy regression. |
| P3-04 | Met | For the original fetch defect, `projectSyncRecord.ts:244-281` reads fetch porcelain, sets its own refmap and disables pruning; there is no private fetch-ref sweep. Same-call ref ownership across **all** Sync surfaces is not met (R5-06). |
| P3-05 | Partly met | `projectSyncRecord.ts:91-121` bounds and scopes records; `ProjectSync.ts:728-730` looks up on demand. No later origin observation must revoke an approved target under the revised guarantee. Expiry/eviction during final probes remains R5-03. |
| P3-06 | Partly met | The old endpoint/offline-permission confusion is gone. `ProjectSync.guarded.test.ts:671-708` covers a changed URL and a re-clone at a different HEAD. Cross-fetch endpoint history is not required; within-write checkout binding remains R5-04. |
| P3-07 | Met | No `ls-remote` permission or budget fallback exists. The local row authorizes the target (`projectSyncMove.ts:223-252`); Git-initiated hydration is a separate violation of the offline promise (R5-02). |
| P3-08 | Partly met | Successful fetch plus unread porcelain is `ok`/unread, not `failed` (`projectSyncFacts.ts:197-228`); a failed address/settings pre-read can be `not-run`. R5-12 shows where the truthful reason is still lost. |
| P3-09 | Met | `projectSyncFacts.ts:104-115`, `ProjectSync.ts:411-414`, `ProjectSyncExtras.ts:189,669-685` now honor the unread discovery flag for status, fetch, inventory and send. `ProjectSync.service.test.ts:767-793` checks the latter two. A later per-operation read failure is a different case (R5-09 through R5-12). |
| P3-10 | Partly met | Detached and unread are distinct; a missing acknowledgement returns `movedUnverified`, not a confirmed zero (`projectSyncMove.ts:553-559`). R5-11 through R5-13 still produce definite or contradictory claims. |
| P3-11 | Not met | The named receipt fixes “latest fetch wins”, but the original `work`/`release` counterexample still holds verbatim (R5-08). Inventory also fails to validate the row it selected (R5-09). |

## Verification limits

The exact-head `PR Gate` passed; `Platform tests summary` was skipped. No local suite, install, build, commit or checkout mutation was performed. The record above distinguishes inspected tests from the read-only Git experiment. `apps/server/src/handoff/extrasTestKit.ts:32-45` records calls and delegates to real Git. The branch race, occupied worktree, partial tree write and warning-only deletion cases inspect actual refs/files. The failed ref commit and lost acknowledgement at `apps/server/src/fleet/ProjectSync.guarded.test.ts:584-621` use a real transaction with an injected abort or dropped acknowledgement; they are not real reflog I/O failures. No two-machine proof is claimed.

**Windows:** wire repository paths use `/`; discovery converts `path.relative` using the host separator (`apps/server/src/fleet/handoffGit.ts:259-265`), clone joins validated components, and `handoffGitTypes.ts:72-82` rejects drives/backslashes in a wire-relative path. This is not Windows filesystem proof. The new permission tests use POSIX directory modes (`ProjectSync.guarded.test.ts:144-146,469-521`), and the ref child timeout sends a process signal rather than the Windows process-tree termination used by the ordinary runner (`refTransaction.ts:94-98`; `folderTransfer/git.ts:77-80,117-128`). Windows is excluded, not counted as a blocker. Nothing here demands a current origin tip, push-address validation, an aggregate batch deadline, or detection or attribution of every concurrent file edit.

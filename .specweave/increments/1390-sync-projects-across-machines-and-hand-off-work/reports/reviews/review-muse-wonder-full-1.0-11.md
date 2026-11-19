<!-- specweave review: reviewer=muse-wonder-full-1.0 model=muse-wonder-full-1.0 family=meta author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=78613f229dfd9bce97be47cf29f6106c419c6c10 at=2026-11-19T01:29:55.881Z -->
# Adversarial code review: PR #649 Project sync follow-ups, origin-only fast-forward (1390 Phase 2), head `78613f229dfd9bce97be47cf29f6106c419c6c10`
Verdict: fix first

Reviewer: muse-wonder-full-1.0 (Muse Code, Meta), independent of the Claude author. The reviewed commit is `78613f229dfd9bce97be47cf29f6106c419c6c10`, which is the worker's `c3570dca5ed11bbf26657899a4379b45b11eac52` plus a clean merge of `main`. The app repository at `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode` was read only, with `git show` and per-commit diffs (`bfee23ae0`, `7e9276399`, `c3570dca5`). Code under review was not edited. Git and rename behaviour was reproduced in throwaway repositories under `/tmp` and removed. No test suite was run locally, per the brief; every named test body was read. On November 18, 2026, `gh pr checks 649` showed 6 pass, 12 skipping and 7 pending (the three server gates, the two web gates, packages and typecheck), no failures; the PR head matches the reviewed commit and is mergeable. This verdict does not rest on CI finishing.

One finding blocks. P2-19: the new clone staging folder is discovered and synced as a repository of the project, during a clone and forever after a crash. Everything else from round 2 is fixed. The two behaviour changes (P2-13, P2-15) are otherwise correct, and the contract change is additive. Because a ship verdict merges this and the Sync dialog right after it, P2-19 should be fixed in this PR: it is a small change (keep `.swc-clone-` folders out of Sync's repository list and sweep or report a leftover one), and after the dialog lands the phantom repository it creates is user-visible and can wedge fast-forward for the real repository above it.

## Round 2 findings revisited

### P2-10 fixed: the fast-forward target is pinned to a branch of `origin`, by commit hash

`apps/server/src/fleet/ProjectSync.ts:359` to 371 resolves `@{upstream}` to its full ref and accepts it only under `refs/remotes/origin/`, returning that ref's commit hash; anything else yields `otherUpstream` and no commit. Facts count ahead and behind against the hash (`ProjectSync.ts:316` to 322), and `fastForwardRepository` re-resolves the hash through the same function before merging the hash itself, never a name. The three named tests at `apps/server/src/fleet/ProjectSync.test.ts:926`, 944 and 960 are real-repository tests: a local-branch upstream (`branch.main.remote=.`) and a second remote's branch both plan `none:no-upstream` with the name in `detail`, no merge command runs, and a decoy local branch literally named `origin/main` is not what gets merged.

The configurations the brief asked about, each checked against Git in `/tmp` or in the code:

- `branch.x.merge` naming a non-branch ref: with `merge=refs/tags/v1`, `git rev-parse --symbolic-full-name @{upstream}` fails ("not stored as a remote-tracking branch"), so `originUpstream` returns null and nothing moves.
- `pushRemote` and `remote.pushDefault` (triangular workflow): `@{upstream}` ignores both; they name `@{push}` only. Verified in `/tmp`: the upstream stayed `refs/remotes/origin/main`.
- Detached HEAD: `branch` is null, so no upstream is read (`ProjectSync.ts:312`) and the plan is `fetch` with reason `detached`.
- `remote.origin.fetch` renaming tracking refs into another namespace, for example `refs/remotes/mirror/*`: the upstream resolves outside `refs/remotes/origin/`, so Sync plans `none:no-upstream`. That is the safe outcome, since Sync's own fetch writes `refs/remotes/origin/*` and never updates the renamed ref. Only the `detail` wording is imprecise there ("not a branch of origin", when it is origin's branch under a renamed tracking ref). A wording nit, not a finding.
- Upstream branch deleted on `origin`: see P2-20. It fast-forwards to the last fetched commit of that branch. Nothing is lost, but "Moved forward" then reports a commit this Sync did not fetch.

So no branch configuration I could construct makes Sync move a checkout to a local branch, another remote, or a name that merely reads like `origin/main`. P2-20 is the one remaining way the target is not from this Sync's fetch.

### P2-11 fixed: loopback spellings are normalised before the check

`normalHost` (`ProjectSync.ts:142` to 152) lower-cases, strips trailing dots and round-trips the host through `URL`, which canonicalises `127.1`, `2130706433`, `0x7f000001`, `0177.0.0.1` and `0` to dotted form and IPv6 to compressed form; `isLocalAddress` (`ProjectSync.ts:122` to 135) then also covers `0.0.0.0/8`, `::`, and IPv4-mapped loopback (`::ffff:7f00:1` form). The named test at `ProjectSync.test.ts:974` exercises all eleven spellings from round 2, including scp form and `[0:0:0:0:0:0:0:1]`, through both doors (facts name no clone address, and `cloneRepository` refuses), and confirms a LAN address and a `.local` host still cross. A host name that merely resolves to loopback still crosses, as accepted in round 2.

### P2-12 fixed: staged files past the read cap are reported not checked and left out

`checkStagedContent` now splices everything past the cap into `flagged` with reason `not-checked` (`apps/server/src/handoff/snapshotSecrets.ts:208` to 222 at this head), after sorting by path so the boundary is deterministic. Flagged paths are force-removed from the snapshot tree by the caller (`apps/server/src/handoff/checkpointGit.ts:256` to 268), so an unread file past the cap no longer travels. The named test at `snapshotSecrets.test.ts:312` covers it, and the `tooMany` test at line 332 now exists and pins the first file past the limit. The 64 KB nit is also fixed: the staged check slices bytes, not decoded characters (`snapshotSecrets.ts:233` to 235).

### P2-13 fixed: the arrival move is Git's own fast-forward-only fetch, and it is the right shape

`moveBranchForward` (`apps/server/src/handoff/ExtrasReceiver.ts:106` to 133) re-reads the branch and the hidden `via` ref, then runs `fetch --quiet --no-tags --no-prune --no-recurse-submodules --no-write-fetch-head --refmap= . <via>:refs/heads/<branch>` with no `+`, and confirms the branch afterwards. I reproduced this exact command in `/tmp` with the production runner's settings (`-c core.hooksPath=/dev/null`, `apps/server/src/fleet/folderTransfer/git.ts:29` to 40) against a repository carrying `fetch.prune=true`, `remote.origin.tagOpt=--tags`, a configured line `+refs/heads/*:refs/heads/stolen/*`, and `fetch.fsckObjects` and `transfer.fsckObjects` on:

- Only the destination ref moved. `git for-each-ref` before and after differed in exactly that one ref; no `refs/heads/stolen/*`, no tag movement, and a sentinel `.git/FETCH_HEAD` was untouched. The command-line flags and empty `--refmap=` override the configured fetch behaviour, as in P2-01. Hooks cannot run at all under `core.hooksPath=/dev/null`, so `reference-transaction` is off; there is no post-fetch hook in Git.
- A branch checked out in a linked worktree is refused (`fatal: refusing to fetch into branch ... checked out at ...`), exit 128, even when the move would be a no-op. The current branch of the main worktree is refused the same way. A branch under a conflicted rebase in a linked worktree is also refused with the same message; Git's checked-out test covers the rebase `head-name`. A bisect rests on the `checkedOutBranches` snapshot (`ExtrasReceiver.ts:64` to 91), as it did before; a bisect started after the snapshot holds a detached HEAD, and `git bisect reset` re-resolves the branch by name, so an arrival move in that window loses nothing of the person's.
- A non-fast-forward (a rival commit placed on the branch by `update-ref` after the read) is rejected and the rival stays. The named test at `ExtrasReceiver.test.ts:227` does exactly this through a git hook in the recording runner, so the compare-and-swap claim is tested behaviour, not only Git's documentation. The one semantic difference from a strict compare against `from`: if the branch moved to a commit that the incoming commit still continues, the fetch fast-forwards it. That loses nothing (it is still a fast-forward of the branch's own current head) and the comment at `ExtrasReceiver.ts:93` to 104 now says so accurately. The round 2 nit about that comment is fixed.
- The create case stays create-only and separate: `update-ref <branch> <commit> ""` (`ExtrasReceiver.ts:216` to 221), reached only when the ref does not exist and the name is not in the checked-out snapshot.
- `fetch.fsckObjects` and friends can only make this fetch fail, which returns false and falls back to a beside branch. Fail-closed. `transfer.hideRefs` hiding the hidden ref would do the same.

The test-kit allowlist was updated to the new form without widening it (`apps/server/src/handoff/extrasTestKit.ts:102` to 125): the only branch-moving fetch it allows is the exact 8-argument form from a hidden `extras-incoming` ref into `refs/heads/swc/from-`, with no `+` permitted by the pattern.

One residual, not filed: `git fetch` may run `gc --auto`, which can repack and prune long-unreachable objects. The bundle fetch into the incoming ref already had this property before this PR, so it is not a regression of P2-13.

### P2-14 fixed, with the worker's disclosed window accepted

`sweepStaleExtraRefs` (`apps/server/src/fleet/ProjectSyncExtras.ts:129` to 146) now asks `isActive` live for each ref at removal time and deletes with `update-ref -d <ref> <listed commit>`, so a ref that moved since listing is not deleted. The named test at `ProjectSync.service.test.ts:626` is a genuine two-send race: it holds the first send's listing open until the second send has created its ref, then requires both sends to succeed. The disclosed remainder (a retry reusing an operation id whose ref is recreated at the same commit between another sweep's live check and its delete) costs a failed send and nothing else; the snapshot commit is unpinned, not lost. Accepted, non-blocking.

### P2-15 partly fixed: the target folder is never deleted and never written over, but the staging folder is a Sync repository (P2-19)

The clone now runs in `.swc-clone-{name}-{random}` beside the target (`ProjectSync.ts:521` to 523`), failure or cancel removes only that staging folder (`ProjectSync.ts:528` to 531, 557 to 562), and success moves it in only after an `lstat` shows the target still absent (`ProjectSync.ts:564` to 573`). The two named tests at `ProjectSync.test.ts:1006` and 1029 put a person's folder and file at the target during failing and succeeding clones and assert both survive with nothing left beside them. The service test at `ProjectSync.service.test.ts:405` to 463 proves the cancel path against a real hanging clone: the staging folder is the only entry during the clone, the cancel holds the project lock until Git has ended and the staging folder is gone, and the next call observes it gone. Placement is sound: parents are created one at a time with a link check (`ProjectSync.ts:502` to 518`), the staging folder is created with `mkdtemp` in the target's own parent under the real project root, so the rename is within one filesystem and the staging name cannot collide with an existing folder.

The rename race, probed with Node's `fs.rename` on this machine: onto a non-empty folder, a file, or a symlink (to an empty or non-empty folder) it fails and the clone is refused with the staging folder discarded. Onto an empty folder created between the `lstat` and the `rename`, the rename replaces it. The whole loss in that sub-millisecond window is an empty folder the person just made; see P2-21. On a case-insensitive disk the pre-rename `lstat` itself finds a differently-cased existing target, so nothing is replaced there.

What is not handled is the staging folder's life as a repository of the project. That is P2-19, the blocking finding below. Files a person puts inside the staging folder itself are removed with it on failure; the worker disclosed this, the folder name is unguessable and short-lived, and I accept it.

### P2-16 fixed: the mirror setting is read with `--bool`, and unreadable values fail closed

`ProjectSync.ts:280` to 291 reads `remote.origin.mirror` with `--get-all --bool`; exit 1 (unset) is false, any other non-zero exit (including a value Git cannot read as a boolean, such as `fetch`) counts as set, and with several values the last one wins, which is Git's own rule. The named test at `ProjectSync.test.ts:1050` covers `2`, `yes`, `on`, a bare key, the unreadable value, and the false spellings.

### P2-17 fixed: the pre-check looks before it opens, and opens non-blocking

`readFileHead` (`snapshotSecrets.ts:49` to 85) `lstat`s first and returns null for anything that is not a regular file, then opens with `O_NONBLOCK` added to `O_NOFOLLOW`, and re-checks `isFile` on the handle, which is closed in a `finally`. A FIFO present at listing time is skipped by the `lstat`; one swapped in between the look and the open cannot block the non-blocking open and is rejected by the handle check. The named test at `snapshotSecrets.test.ts:355` covers the listed-file case (skipped on Windows, where the `lstat` still protects everything but the swap race).

### P2-18 fixed: an unreadable subfolder checkout counts as in use

`threadUsesCheckout` (`ProjectSync.ts:599` to 614) now treats `threadCheckout: null` as part of the checkout when the thread folder is inside it, and the only caller passes null exactly when `rev-parse --show-toplevel` failed (`ProjectSync.ts:830` to 836`). A folder outside or beside the checkout still does not block. The named pure-function test at `ProjectSync.test.ts:1077` pins both directions. The worker's note that only the pure function is tested is fair; the caller is three lines and reads as traced.

## The contract change is additive

`otherUpstream` is `Schema.optional(Schema.NullOr(...))` on `ProjectSyncRepositoryFacts` (`packages/contracts/src/projectSync.ts:102` to 115 at this head), and `planProjectSyncRepository` only reads it to fill the pre-existing `detail` field of the pre-existing `none`/`no-upstream` step. No new action, reason literal or step field appears anywhere in the diff.

Both skew directions hold. A window built against the old contract talking to a new server: Effect `Schema.Struct` decoding drops the unknown `otherUpstream` key (nothing in the contract or RPC layer sets `onExcessProperty: "error"`; the one use in the repo sets `"ignore"` explicitly), `upstream` arrives null with `ahead` and `behind` 0, and the old planner already maps that to `none:no-upstream`. The new `detail` sentence rides in a field the old window already renders. A new window talking to an old server: `otherUpstream` is absent, the planner treats it as null and produces the old step with no `detail`. The old server itself would still fast-forward to a non-origin upstream if asked to run, because its own planner and merge are the old code; that is version skew of behaviour on an un-updated machine, not a wire break, and no contract change could prevent it.

## New findings

### P2-19 medium, blocks: a clone's staging folder is discovered, listed and synced as a repository of the project; after a crash it stays forever and can wedge the real repository above it

Nothing in the repository scan knows the staging name. `discover` (`apps/server/src/fleet/handoffGit.ts:246` to 286) walks every directory under the project folder except `.git` and `node_modules` (`handoffGit.ts:47`), does not use Git ignore rules (by design, `handoffGit.ts:44` to 46), and registers any folder containing `.git` as a repository. `syncRepositories` (`ProjectSync.ts:199` to 211) filters only linked worktrees, which a staging clone is not. The only mentions of the name in the tree are its creation site and one test. Consequences, all from the code as read:

- During a clone (up to 30 minutes), `projectSync.status` runs without the project lock (`ProjectSync.ts:848` to 854`) and lists `.swc-clone-{name}-{random}` as a repository of the project once Git has created its `.git`. `fetch` and `run` enumerate repositories the same way when they next start.
- If the server is killed mid-clone (a crash, or an update restart that does not wait), the cancel cleanup never runs and the staging folder is permanent: no code recognises, removes or reports it, and each retry makes a new one beside it. The leftover is then fetched, listed in the dialog as a repository with a random suffix, eligible for fast-forward in a later `run`, and enumerated for extras. Where its parent folder is not Git-ignored in the repository above it, that repository's own status counts the staging folder as untracked (`ProjectSync.ts:224` to 235`), so the real repository is planned `fetch` with reason `uncommitted` forever and never fast-forwards, with no hint naming the cause.
- The scan also walks the whole staging tree against its entry limits (`handoffGit.ts:48` to 50`), so a large clone in progress can push a concurrent status scan into its root-only fallback.

Before this PR, a crash mid-clone left the partial clone at the target's own name, where the next run refused with "A folder is already there" and the person could see what to remove. The staging design is the right fix for P2-15, but it needs its second half: keep `.swc-clone-` folders out of Sync's repository list (in `syncRepositories` or the scan Sync uses), and remove or report a leftover at the start of `repositories()` or `cloneRepository`, the way stale extras refs are swept. Blocks because the dialog that lists these repositories merges immediately after this PR, and the wedged state has no user-facing remedy. The worker's "not proven" list does not mention this case.

### P2-20 low, does not block: a branch deleted on `origin` still fast-forwards to its stale tracking ref

Sync's fetch is `--no-prune`, so when the upstream branch is deleted on `origin`, `refs/remotes/origin/{branch}` keeps its last fetched commit. Reproduced in `/tmp` with the production fetch arguments: after deleting the branch on the remote, the fetch exited 0, the upstream still resolved, and the count read behind 1. Facts and `fastForwardRepository` therefore move a clean, unused checkout to that commit and report "Moved forward", although this Sync fetched no such branch. Nothing is lost (the move is still `--ff-only` to a commit that was origin's, on a checkout with no work of its own), and `--no-prune` is a deliberate part of the P2-01 design, so this predates the PR. Listed because the brief asked, and because the sentence the dialog will show is then wrong about where the commits came from. A later pass could compare the tracking ref against what the fetch just wrote, or treat a branch absent from the fetched heads as no upstream.

### P2-21 low, does not block: an empty folder created at the target between the final `lstat` and the `rename` is replaced by the finished clone

`ProjectSync.ts:564` to 569 checks the target is absent, then renames. POSIX `rename` of a directory onto an existing empty directory replaces it (probed with Node on this machine; non-empty folders, files and symlinks all fail instead, and on Windows the rename fails onto anything existing). So the worker's claim "never replaces an existing folder" has this one exception, in a sub-millisecond window after a clone that ran for minutes, and the whole loss is the empty folder. Same class as the parent-undo residual accepted in round 2. The claim in the comment at `ProjectSync.ts:563` should be read with that exception.

## The worker's "not proven" list, judged

- P2-14's remaining window: real, costs a failed send only. Does not block.
- P2-15 removing files placed inside the staging folder itself: real, needs the person to write into an unguessable folder during the clone. Does not block. The undisclosed half of P2-15 is P2-19, which does.
- P2-13's compare-and-swap "not tested directly": the claim understates the test at `ExtrasReceiver.test.ts:227`, which swaps the branch head between the read and the move and asserts the rival survives. Proven.
- P2-10's third test red only for the short name: the hash merge is also asserted directly (`commands.find(merge).at(-1)` equals the published head), and `fastForwardRepository` resolves its target only through `originUpstream`. Sufficient.
- Nothing ran against a live project or a paired machine: true for this review as well. It does not change the verdict either way; the blocking finding is visible in the code and the scan it feeds.

## Not verified

- The test suite at this head: not run locally, per the brief. CI was still pending on the server, web, packages and typecheck gates when checked on November 18, 2026, with no failures; every test cited was read.
- Two real machines over Connect, and the Sync dialog (which is not in this PR): read only from the contract side.
- Windows: the FIFO test skips there, and the rename-replaces-empty-folder behaviour (P2-21) is POSIX; on Windows the same code refuses, which is the safer direction.
- Whether an app update restart waits for a running clone: not read. P2-19 needs only a kill or crash during a clone, which no update policy can rule out.

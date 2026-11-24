FIX FIRST
Verdict: fix first

# Round 7: Project Sync, marked clone staging and offline fast-forward

Reviewed `anton-abyzov/specwithcode#658` at `15f738f1145766a7042466c6bd15094041f85131`. **1 of 3 R6 blockers fixed, 2 partly fixed. 2 high blockers, 0 critical, 2 non-blocking follow-ups.** All seven regression cases failed at baseline and passed at this head. Neither outstanding failure is covered by those cases.

## R6 disposition

Source and test citations below are relative to `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode` at the reviewed commit.

| R6 blocker | Decision and implementation evidence | Would the tests fail without the fix? |
|---|---|---|
| R6-01: an offline move can hydrate from origin | **Partly fixed.** `apps/server/src/fleet/projectSyncMove.ts:209-220,294-305` checks promisor, filter-only and extension keys before peeling `HEAD`, without a version exemption. It refuses when those keys are visible to `git config`. The query can still read a different configuration from the checkout writer (R7-01). | **Yes, three cases.** `apps/server/src/fleet/ProjectSync.admission.test.ts:214-269`: the two config-only cases actually advanced `main` on the baseline. In the real filtered clone, the baseline reached the writer and failed on the missing blob instead of declining at admission. Its packet trace was already empty on the test host; the trace assertion alone was not red. The `2.45.0` version string is simulated, not a run of that Git binary. |
| R6-02: a Git directory ending in a space binds to its sibling | **Fixed.** `apps/server/src/fleet/projectSyncGit.ts:107-119,277-282` strips only the terminating newline and rejects invalid UTF-8 or an unexpected line count. `apps/server/src/fleet/projectSyncFacts.ts:264-281` keeps the exact Git directory; `apps/server/src/fleet/projectSyncMove.ts:286-294,342-344,518-524` uses it for binding, the transaction and the last comparison. An embedded newline is refused rather than guessed. | **Yes, on the wrong repository's actual ref.** `apps/server/src/fleet/ProjectSync.admission.test.ts:272-305` failed because the unspaced sibling advanced. It also checks that sibling's index, the spaced repository's ref and staged entries, the checked-out file, and the reported count. |
| R6-03: hidden-ref cleanup deletes a ref it did not write | **Partly fixed.** `apps/server/src/fleet/ProjectSyncExtras.ts:419-425,582-589,603-620` leaves an observed symbolic ref alone, deletes without dereferencing, and stays with the original Git-directory *path* when a gitfile points elsewhere. The path is not a stable repository identity (R7-02). | **Yes, three cases.** `apps/server/src/fleet/ProjectSyncExtras.round6.test.ts:77-107,109-134`: baseline cleanup deleted `keep` in both the branch and snapshot sends, and deleted the ref in the replacement repository. The last test uses two different Git-directory paths; it does not replace the directory at the original path. |

## Blocking findings

### R7-01 [high] The partial-clone check and the tree writer can read different Git settings

**AC-11 promise 2: `run` does not ask origin again.** `apps/server/src/fleet/projectSyncMove.ts:209-220` treats exit 1 from `git config --get-regexp` as proof that the checkout has no promisor. `apps/server/src/fleet/folderTransfer/git.ts:57-66,97-106` inherits the server's `GIT_CONFIG`. [Git documents that this variable selects a single file for `git config` and has no effect on other Git commands](https://github.com/git/git/blob/v2.45.0/Documentation/git-config.txt#L439-L444).

For example, the selected file can contain the ordinary origin URL and fetch settings while the repository's own config also declares origin a promisor. The explicit fetch can succeed and produce the behind row; the move's config query finds no promisor in the selected file. On Git 2.45.0, `read-tree -u` at `apps/server/src/fleet/projectSyncMove.ts:395-407` reads the real repository configuration. With the new blob missing, [checkout prefetches it](https://github.com/git/git/blob/v2.45.0/unpack-trees.c#L470-L475) through a [direct promisor request](https://github.com/git/git/blob/v2.45.0/read-cache.c#L3736-L3755) that [starts `git fetch`](https://github.com/git/git/blob/v2.45.0/promisor-remote.c#L17-L35). No concurrent config change is required. Read-only queries independently confirmed the config-only override locally; the 2.45.0 transport conclusion is from the tagged Git source, not a local transport reproduction.

**Fix:** prohibit Git transport for the offline move and its children, not for the preceding fetch. At minimum, refuse the move when a config-only override prevents the probe from attesting to the writer's configuration. Extend the missing-blob case to cover differing config views and assert refusal before the writer, unchanged tip and no origin traffic.

### R7-02 [high] Cleanup follows a replacement repository at the same absolute path

**AC-11 promise 6: Sync deletes only refs it wrote in this call.** `apps/server/src/fleet/ProjectSyncExtras.ts:419-425` stores two path strings. After waiting for the peer, `apps/server/src/fleet/ProjectSyncExtras.ts:582-589,608-619` starts fresh Git processes at that path. Neither the direct-ref read nor the deletion establishes which repository now occupies it.

Consider a checkout restored from a copy while the send waits for its peer. The copy contains the hidden direct ref and its original OID, exactly as in the regression fixture. If the restored Git directory occupies the **same path**, every path comparison still passes. The OID comparison and `--no-deref` both succeed, and Sync deletes the restored repository's ref, which this call never wrote there. That ref can be the restored repository's only reference to an uncommitted-work snapshot. The replacement can finish before cleanup starts; this does not depend on winning the interval between the ref check and the delete. The fixture at `apps/server/src/fleet/ProjectSyncExtras.round6.test.ts:113-134` keeps the original directory at its original path, so it cannot detect this case.

**Fix:** keep temporary refs in repository storage private to this send, or retain an identity-stable handle to the original ref store through publication and cleanup. If ownership cannot be established, leave the ref rather than deleting by pathname and OID. This must cover snapshot publication too: `apps/server/src/fleet/ProjectSyncExtras.ts:464-476` reads back a ref that `apps/server/src/handoff/checkpointGit.ts:343` published by checkout path. Verify that a same-path replacement keeps its ref for both send kinds.

## Follow-up (non-blocking)

1. **A disabled promisor is reported as a partial clone.** `apps/server/src/fleet/projectSyncMove.ts:209-220` tests key presence, so a full clone whose only matching key is `remote.origin.promisor=false` cannot fast-forward and gets a misleading reason. [Git ignores that false value](https://github.com/git/git/blob/v2.45.0/promisor-remote.c#L116-L127). This is a conservative refusal, not an unsafe write. Distinguish an enabled promisor from an explicit false once transport is independently disabled.
2. **Cleanup can report a leftover that is already gone.** `apps/server/src/fleet/ProjectSyncExtras.ts:582-595,615-619` uses the same no-match result for an absent ref and one it must not delete. If another operation has already removed the hidden name, the answer says it “was left in the repository.” Distinguish confirmed absence from changed ownership or an unread ref, or say only that cleanup could not confirm ownership.

## Verification

Compared file contents against `8438feb7b029eb03e6a378552d44ffa6a41d4c35`, not commit ancestry. The affected production blobs match the rebased baseline before test-first commit `ae63ece05`; the two regression-test files are unchanged between that commit and the reviewed head.

The [exact-head PR Gate](https://github.com/anton-abyzov/specwithcode/actions/runs/44501634419) succeeded on attempt 2. Its [server artifact](https://github.com/anton-abyzov/specwithcode/actions/runs/44501634419/artifacts/14518870493) records **21/21 admission tests and 3/3 round-six extras tests passed**. Baseline assertion failures were checked in `/Users/antonabyzov/.specwithcode/m4/scratch/2026-11-18-1390-phase-2/red/round6.txt`. No local suite, install, build or change to the reviewed checkout was needed.

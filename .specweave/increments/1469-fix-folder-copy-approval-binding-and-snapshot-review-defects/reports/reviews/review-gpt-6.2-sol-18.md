<!-- specweave review: reviewer=gpt-6.2-sol model=gpt-6.2-sol family=openai author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=36ca15252ab61f834da351753e02039ee38f2451 head=16bf34d4fc3753f8192f56142e8c01bd4735786f at=2026-11-25T02:08:01.174Z -->
# Review of increment 1469, PR #903
Verdict: fix first

Reviewed `36ca15252ab61f834da351753e02039ee38f2451..16bf34d4fc3753f8192f56142e8c01bd4735786f` as the GPT-6.2-Sol fallback for Claude Opus 5.5.

## Findings

**High · AC-13 · re-verified by source trace.** Review -16 remains open when two exclusions cover the same path. `apps/web/src/components/studio/handoffFolderCopyPending.ts:352` keeps a single owner per project and path, and `:355` does the same for Secrets off. A later exclusion overwrites the first owner. `:369` then deletes the only record when that later owner clicks **Sync again with secrets** (`apps/web/src/components/studio/useCopySecrets.ts:122`).

Open A's copy to X before `.env.local` exists. Add the file and open Y's preview in B and C. Untick it in B. Refresh A's older scan. A records the newly found file as excluded under A|X, overwriting B|Y even after the windows redraw (`apps/web/src/components/studio/handoffCopyScanRecovery.ts:56`, `apps/web/src/components/studio/useCopySecrets.ts:140`). Compare again and finish X with the file excluded. A clicks **Sync again with secrets** on X. A's click deletes the shared entry. C still holds Y's original pointer and can approve Y with `.env.local` staged and named, even though B never re-ticked it (`apps/web/src/components/studio/HandoffFolderCopy.tsx:610`, `:913`, `:954`, `apps/web/src/components/studio/useCopySecrets.ts:200`, `apps/web/src/studio/copySecretsPolicy.ts:98`, `apps/server/src/fleet/folderTransfer/destinationService.ts:1465`). Give each owner its own exclusion entry so clearing A|X preserves B|Y.

Review -17's original clock comparison and draft-carried override are gone. Re-verified at `apps/web/src/components/studio/useCopySecrets.ts:122` and `apps/web/src/components/studio/handoffFolderCopyPending.ts:376`, `:404`. No additional blocking regression found for AC-12 or AC-14 through AC-16.

## Follow-ups

Add a same-path regression across windows and destinations. The new tests use distinct paths (`apps/web/src/components/studio/handoffCopyRefresh.test.ts:134`, `apps/web/src/components/studio/useCopySecrets.crossWindow.test.tsx:152`). Legacy unowned exclusions can stay after a repeat, which leaves more secrets on the source. Tests were inspected only. Exact-head CI was running during review.

Verdict: fix first

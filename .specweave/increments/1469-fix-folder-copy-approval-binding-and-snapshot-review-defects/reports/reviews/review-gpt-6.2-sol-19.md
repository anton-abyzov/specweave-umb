<!-- specweave review: reviewer=gpt-6.2-sol model=gpt-6.2-sol family=openai author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=16bf34d4fc3753f8192f56142e8c01bd4735786f head=3c7862e453e29559aba120f1a52c34f89d6b3594 at=2026-11-25T02:11:56.793Z -->
# Review of increment 1469, PR #903
Verdict: fix first

Reviewed `16bf34d4fc3753f8192f56142e8c01bd4735786f..3c7862e453e29559aba120f1a52c34f89d6b3594` as the GPT-6.2-Sol fallback for Claude Opus 5.5.

## Findings

**High · AC-13 · re-verified by source trace.** `apps/web/src/components/studio/handoffFolderCopyPending.ts:350` drops saved exclusions from the preceding format. The earlier writer stores `file:.env.local` and `off` under the same project prefix. The new reader treats `file` as the owner and `.env.local` as the action, which the union ignores at `:401`. It skips `off` at `:351`.

On the old build, open the same measured copy in B and C. Untick `.env.local` in B, then change a regular file class in C. C saves its own stale secrets choice with the new class selection for the same operation (`apps/web/src/components/studio/HandoffFolderCopy.tsx:825`). The separate exclusion still protects the copy on the old build. Reload on the new build in the same browser profile and origin. The exclusion is now ignored, so Compare and Copy can stage and name `.env.local` without any re-tick (`apps/web/src/components/studio/useCopySecrets.ts:201`, `apps/web/src/components/studio/HandoffFolderCopy.tsx:913`, `:920`, `apps/server/src/fleet/folderTransfer/destinationService.ts:1465`). Read both key formats and cover resuming a stale pointer with a legacy file or Secrets off entry. The scenario requires storage from a preceding PR build. Production exposure is unverified.

Review -18's same-path overwrite is closed for owner-keyed entries. A|X and B|Y write distinct file and off keys, and A|X's clear leaves B|Y's entries intact (`apps/web/src/components/studio/handoffFolderCopyPending.ts:368`, `:388`). The added test asserts both survive and checks an explicit re-tick (`apps/web/src/components/studio/handoffCopyRefresh.test.ts:150`). Review -17 stays closed. No delta changes to AC-12 or AC-14 through AC-16.

## Follow-ups

None. Tests were inspected only.

Verdict: fix first

<!-- specweave review: reviewer=gpt-6.2-sol model=gpt-6.2-sol family=openai author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=fe29b0d6ddc84581726c2644b6979a37b2cf901d head=36ca15252ab61f834da351753e02039ee38f2451 at=2026-11-25T01:54:35.244Z -->
# Review of increment 1469, PR #903
Verdict: fix first

Reviewed `fe29b0d6ddc84581726c2644b6979a37b2cf901d..36ca15252ab61f834da351753e02039ee38f2451` as the GPT-6.2-Sol fallback for Claude Opus 5.5.

## Findings

**High · AC-13 · re-verified by source trace.** `apps/web/src/components/studio/useCopySecrets.ts:113` clears every current project exclusion. `apps/web/src/components/studio/HandoffFolderCopy.tsx:1392` does this when the person authorizes a repeat of the finished copy shown in that window. The exclusion keys have no destination or operation ID (`apps/web/src/components/studio/handoffFolderCopyPending.ts:107`, `:336`, `:350`).

Leave Done open for a copy to X with a secret left behind. In a second window, preview a new copy of the same project to Y while `.env.local` is included. In a third window, resume Y and untick `.env.local`. The second window still holds its original choice in memory, and the shared exclusion keeps the file out. Click **Sync again with secrets** on X. Before Y stages its list, that click removes Y’s exclusion as well. The second window still holds Y’s operation even after the shared pointer changes (`HandoffFolderCopy.tsx:610`, `:954`). Its next approval stages `.env.local` for Y and names it in `expectedSecrets` (`useCopySecrets.ts:177`, `:188`; `HandoffFolderCopy.tsx:913`, `:916`; `apps/web/src/studio/copySecretsPolicy.ts:98`). The destination then pulls the file (`apps/server/src/fleet/folderTransfer/destinationService.ts:1463`). The X click authorizes secrets to X. Keep its override scoped to that new operation.

## Follow-ups

The single-window regression test covers the all-off case (`apps/web/src/components/studio/HandoffFolderCopy.secretsGate.test.tsx:356`). Add coverage for an exclusion on a different destination while Done remains open. The exact-head web gates were running at review time. No tests were run locally.

Verdict: fix first

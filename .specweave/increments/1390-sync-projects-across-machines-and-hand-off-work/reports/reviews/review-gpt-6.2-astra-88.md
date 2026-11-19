<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=0543eba16ae75a83f6d08af3a55f3e43e116a96f at=2026-11-19T19:23:42.843Z -->
# Review: 1390 T-13 automatic handoff follow-up
Verdict: ship
Reviewer context: fresh session, Git objects only. Reviewed `0543eba16ae75a83f6d08af3a55f3e43e116a96f` against `6e4233fc8`. CI reported green; no tests rerun.

Admission is unchanged: `apps/server/src/orchestration-v2/ProviderFallbackWorker.ts:2114` still rechecks the fresh trigger's key, track and local exhaustion after checking Stop and rereading provider state. A missing trigger cannot admit a move.

The automatic source path supplies the original thread and returned continuation; `apps/server/src/orchestration-v2/LimitHandoffAdapter.ts:112` checks the existing handoff link before changing its note. The receiver uses the same lineage-derived ID for launch and annotation (`apps/server/src/handoff/HandoffReceiver.ts:1021`, `:1174`, `:1326`); a manual or absent trigger produces no arrival link (`apps/server/src/handoff/handoffLine.ts:66`). No wrong-thread move, interruption or loss found.

## Follow-ups

- **Low: dismissal lasts only for the mounted banner.** `apps/web/src/components/chat/LimitHandoffCandidates.tsx:213` stores the opened episode in a component ref. Dismiss, leave the thread, and return while the same track is still exhausted: the fresh banner opens it again. Stable polling on one mount does not loop. Keep the dismissal keyed by scoped thread and episode outside the banner if it must survive navigation.
- **Low: the dialog can outlive its project context.** The banner resolves the title from the scoped thread (`apps/web/src/components/chat/LimitHandoffCandidates.tsx:261`), but `apps/web/src/components/handoff/HandOffProgress.tsx:488` stores one window-wide request, and the host at `:532` renders it without checking the active project. Navigation while open can leave project A's correctly labeled notice over project B. The view has no move or interrupt action.

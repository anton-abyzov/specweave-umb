<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=c95cb95b2ee36d69257e18a8c2d917cacd23bdf8 at=2026-11-20T00:43:20.172Z -->
# Review: 1427 relay sender labels
Verdict: ship

Reviewer context: fresh session. Static delta review of `6f6aeb17d..c95cb95b2`; no builds or tests run.

The prior finding is fixed. `apps/web/src/studio/relaySenders.ts:55` filters by thread ID and, when supplied, environment. A bare ID shared across environments returns no sender. The conversation combines both worker lists at `apps/web/src/components/studio/CoordinatorConversation.tsx:313` and renders “Message from a thread” at line 1312 rather than naming the local worker.

The regression at `apps/web/src/studio/relaySenders.test.ts:43` uses two workers with the same ID. It asserts the selected worker for each named environment and no sender for the bare ID. A unique local match still supplies its title; the unique remote case retains its machine suffix.

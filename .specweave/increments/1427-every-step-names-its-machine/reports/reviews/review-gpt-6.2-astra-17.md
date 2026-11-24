<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=6f6aeb17d9a8b04ea57f51c461da6f137f9430e2 at=2026-11-20T00:39:01.341Z -->
# Review: 1427 T-02 relay sender labels
Verdict: fix first

Reviewer context: fresh session, four changed files, one high finding. Reviewed commit `6f6aeb17d9a8b04ea57f51c461da6f137f9430e2` against `e667809696031f3a16646370ed130e92b658393b`. Static review only; no build or tests run.

## [high] `apps/web/src/studio/relaySenders.ts:52` attributes a remote relay to a local worker with the same ID

Suppose the coordinator on M5 has a local worker titled “Local checks” and a remote worker on M6 titled “Remote checks”, both with ID `thread-check`. For a relay from M6, `apps/web/src/components/studio/CoordinatorConversation.tsx:313` puts the local shell first, and line 532 passes only the sender ID to the lookup. The first ID match wins. The label reads “Message from Local checks” without a machine suffix, not “Message from Remote checks · M6”. The environment key used for list comparison does not participate in sender lookup.

Resolve by sender environment and thread ID when both are known. With only a bare ID, return no sender if distinct environments match, so the existing neutral label is shown. Add a same-ID local/remote regression case: `apps/web/src/studio/relaySenders.test.ts:35` currently gives the two workers different IDs.

The moved-worker assertion at `apps/web/src/studio/relaySenders.test.ts:29` checks the direction `M5 → M6`; line 38 checks the unique remote worker's label. A missing ID retains the neutral fallback, and a unique plain local worker retains its title without a machine suffix. No real host name, person's name or private path was apparent in the added lines.

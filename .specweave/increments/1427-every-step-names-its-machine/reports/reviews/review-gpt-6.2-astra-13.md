<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=1e6523111a7a4cdab30d7e0712576cc909487240 at=2026-11-20T00:18:08.211Z -->
# Review: 1427 T-01, agents name the machine for every step
Verdict: fix first

Reviewer context: independent session, GPT-6.2 Astra. Reviewed `anton-abyzov/specwithcode#766` at `1e6523111a7a4cdab30d7e0712576cc909487240`, using the 20-file merge-base diff against `abe3b99ed7cefbd75f352e714e587f56284ef9a9`. Static review only; no checkout, build or test run.

## [high] `apps/server/src/project/ProjectWorkspaceService.ts:195` treats machine nicknames as prompt syntax

The coordinator role, worker role (line 206) and coordinator clock (`apps/server/src/project/currentTimeLine.ts:15`) interpolate the display name verbatim. The nickname normalizer trims, collapses whitespace and limits length; it does not neutralize skill mentions or app tags. A permitted nickname containing a skill mention therefore reaches adapters as a mention the user did not request. The snapshot bounds and hashes the role; it does not escape it. The new clock-marker regex correctly fences a spoofed line *inside memory*, but never sees the nickname in the real clock or role.

Apply the existing `fenceLine` helper to display labels at the prompt boundary, including the joined-name fallback and placement list. Keep the underlying labels unchanged for lookup and display. Assert that the rendered role and clock neutralize mention syntax, not just that `fenceText` recognizes a normal clock line.

## [medium] `apps/server/src/mcp/threadNotFoundHint.ts:35` still omits the responding machine

A lookup for a coordinator that has never run still returns “was not found on this machine,” even when the execution server knows its name. The new wording fixes the linked-coordinator advice, but the hint itself loses its origin when quoted. Use the responding server's label when available. The added test checks the advice, not the machine name.

## Other checks

The grant predicates, remote failure codes, revoked/expired branches and forwarded-code allowlist are unchanged. The new tests exercise linked and unlinked denials and a refused remote launch; none rely on allowing a formerly refused operation. Label lookup uses the execution server's own environment ID, then its descriptor label, not a window or coordinator ID. The move test changes the descriptor between snapshots; it is not an end-to-end migration test.

Public-data check: the PR body contains no identified personal name, private path or host name. The new assertions reuse the fleet-style fixture label `Minis` at `apps/server/src/mcp/workGrantAccess.test.ts:156` and `M4`/`M1` at `apps/server/src/fleet/RemoteWorkers.test.ts:810`. These are not verified hostnames; use neutral A/B labels if they denote actual machines.

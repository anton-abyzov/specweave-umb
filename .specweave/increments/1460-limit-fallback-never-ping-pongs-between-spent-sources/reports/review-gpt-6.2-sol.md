<!-- specweave review: reviewer=gpt-6.2-sol model=gpt-6.2-sol family=openai author=claude depth=deep repo=repositories/anton-abyzov/specwithcode base=29d788d8c head=dad226959879cad3da744d591c978da87ad6fa2d at=2026-11-24T16:39:58.293Z -->
# Review: 1460 Limit fallback never ping-pongs between spent sources (round 5, final head)

Verdict: ship · risk: medium · 0 open findings

Reviewed head: `dad226959879cad3da744d591c978da87ad6fa2d` (PR #875, merged into specwithcode main as `525b3b2c0`). Reviewer: GPT-6.2 Sol (Codex on m4), November 24, 2026. Thread: "Adversarial review: limit fallback ping-pong (1460)", branch `review-1460-ping-pong` on m4. Five rounds, each run against the head it names. Rounds 1 to 4 asked for fixes first; round 5 answered "CLEAN".

## Round 1 at `db22778c2`: 1 blocker, 5 major, 2 minor

1. Blocker: a fleet handoff was still possible after the hop cap. Allowed as D-04 in round 1; round 2 reversed that (see round 2).
2. Major: the way back could dispatch to a held home. Fixed: `planApiCreditReturn` and `apiCreditReturn` skip a held source.
3. Major: preswitch, coordinator turns, worker launches and fleet preflight ignored holds. Fixed: shared `LimitSourceHoldsShared`, `heldSelections` in `packages/shared/src/providerFallback.ts`, and held sources count as out in `limitHandoffTrack`.
4. Major: the cap counted failed runs, not admitted hops. Fixed: the chain is counted by the start message (`limit-fallback:<thread>:<previous stop>`).
5. Major: a released hold came back, and simulated stops held sources. Fixed: `recoveredAt` tombstones, and simulated stops and outlived plan limits are filtered out.
6. Major: the fold hid real replies, and the group id was unstable. Fixed: refusal-only folding, and an opened group keeps its id.
7. Minor: sweep-cost coverage. Answered: the completed-thread reads match `origin/main`.
8. Minor: run scans during render. Fixed: a `runsById` map in `LimitHopsTimelineRow.tsx`.

## Round 2 at `175d2d1ec`: 1 blocker, 3 major, 1 minor

1. Blocker: an open failure reset the cap (`hop-1:r3` parsed as a run id). Fixed: `fallbackMove` parse (D-07), with a sweep test that fails on the old parse.
2. Major: a parked chain could hand off more than once. Fixed: a parked chain makes no automatic handoff (D-04 rewritten), with a sweep test.
3. Major: a status refresh cleared a hold. Fixed: a release needs a real usage read after the stop for that model, and records `recoveredAt` (D-08). Sweep and unit tests.
4. Major: the refusal heuristic hid answers. Fixed: the server's own `isUsageLimitReply`, and a length rule for "resolved" (D-09).
5. Minor: run-read fan-out. Unchanged; it matches `origin/main`.

## Round 3 at `1e1a02352`: 1 blocker, 2 major

1. Blocker: a parked thread returned home automatically. Fixed: no way back for a parked chain (D-10), with a sweep test.
2. Major: a usage read during handoff preflight was ignored. Fixed: `usageReadReleasesHold` is applied to the re-read providers in `admitHandoff` (D-11), with a sweep test.
3. Major: the incident's Cursor refusal did not fold. Fixed: a match against the run's own recorded failure (D-12).

## Round 4 at `a1f397a30`: 1 major

1. Major: the substring match folded real replies. Fixed: a whole normalized match only (D-13), with fold and unit tests.

## Round 5 at `dad226959`: CLEAN

## Evidence outside the review

- PR #875 CI: 27 checks green on `dad226959`.
- Focused suites: server 609/609 (35 files), web 750/750 (12 files, run from `apps/web`).
- 1465 chaos rig: #875 heads `1e1a02352` and `a1f397a30` pass the ping-pong and storm seeds that fail on pre-merge `eccf131f7`. The first nightly on main (run 45444966907) passed 6/6.
- Not covered by the rig yet: the 4-hop cap and "parked makes no move". The sweep tests in `ProviderFallbackWorker.pingPongSweep.test.ts` cover both.

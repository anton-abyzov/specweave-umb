<!-- specweave review: reviewer=muse-wonder-full-1.0 model=muse-wonder-full-1.0 family=meta author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=3b9be8c2673021e978db37d55c95446d6299d22c head=8222aff35 at=2026-11-28T12:30:46.186Z -->
# Security review, round 5, PR #1028

Reviewer: Muse Wonder Full 1.0 (meta), reasoning effort high. Commit read: `8222aff35`. Earlier rounds on this PR: 0881e4543 (three slices), 8f5989a92, 4e2def6b7, 6415bb98a; each "fix first" was fixed and re-reviewed.

Verdict: ship

## Fix 1: one reply settles one release (confirmed)

Each `release()` pushes its entry before writing, and a `released` reply shifts only the oldest entry. A release that timed out keeps its entry until its own reply comes. The Swift helper answers each release line once and in order, and never drops one from its queue.

## Fix 2: rescue on any exit (confirmed)

The exit handler rescues the union of unanswered entries, whether the helper was stopped or not. The union is copied before the queue is cleared. The rescue helper runs with `rescue: false`, so rescues never chain, and the session's `releaseOrphaned` still covers what the session holds.

## Edge cases checked

- a release after stdin ended;
- an extra `released` with an empty queue (a no-op);
- waiters settled more than once (harmless, because `finish` is idempotent);
- a rescue when the helper never started (guarded, and unreachable);
- the exit after the ready timeout (no rescue, no `onExit`).

## Findings

- Nit: entries kept the caller's arrays by reference. Fixed after review in `3b9be8c26` by copying them.
- Nit: no direct test for an extra reply with an empty queue, or for a release after `stop()`. Both are one-line paths that read correctly.

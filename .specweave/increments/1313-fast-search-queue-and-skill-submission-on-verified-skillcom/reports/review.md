# Review: 1313, vskill-platform PRs 214 and 215, vskill PR 234

Verdict: ship · risk: medium · 3 open findings (0 critical, 0 high, 3 low)

Reviewer context: independent read-only sessions with fresh context, one pass per pull request before merge, plus a second pass on the PR 215 fix commit with each finding re-verified by a separate reader.

## PR 214 (search), merged as `be2ac096`

Findings fixed before merge: hedged answers cached as complete, stale rows selectable in the palette, load-more retrying after an error. Follow-up in PR 215 (`bf078fea`): a hedged answer now schedules the merged answer into the cache.

## PR 234 (vskill submit, skill publish, first push), merged as `8df623a`

10 findings, all fixed in `811fe67` before merge.

## PR 215 (queue, submission intake, UI), merged as `069c78fb`

Round 1, 10 findings, all fixed in `c0a0b650`: undeclared (state, updatedAt) index pinned by schema and an idempotent migration; per-state reads limited to 4 at once; approximate positions rendered; queue position on the status page fetched from the positions route; estimated counts flagged and missing states filled from the previous snapshot; id tiebreaker in position counts and filtered pages; paused queue re-sends with a delay instead of spending retries; owner and blocklist reads moved after the idempotency check and lock.

Round 2 on `c0a0b650`, 3 confirmed:

- [medium] `src/lib/queue/fetch-submission-list.ts` statesWithRows trusted estimated zeros. Fixed in `e928a84d`: only exact counts may skip a state.
- [low] `fetch-submission-list.ts` mapWithConcurrency kept starting reads after one failed. Fixed in `e928a84d`; test added.
- [low] `src/lib/cron/queue-stats-refresh.ts`: while the exact count keeps timing out, a rare state's count is carried forward from the last exact snapshot. Open, accepted: the snapshot is flagged estimated and shown as "About N".

CI caught one regression the reviews missed: `src/app/skills/loading.tsx` turned a missing skill page from 404 into 200. Removed in `e928a84d`, with a guard test.

Open, accepted:

- [low] A stale exact zero can hide a state's first row from the "all" list for up to 10 minutes.
- [low] The SSR queue page drops the approximate-position map until the first client poll.

## Production check, 2026-11-12

Queue list 200 in 0.2 s, positions 200 in 0.35 s, uncached search about 1 s, repeat 0.15 s. `vskill@1.2.17 submit --wait` took agents-md-author from RECEIVED to PUBLISHED in 2.7 s (submission sub_38935138-ab60-4083-9df4-e893d2f116de).

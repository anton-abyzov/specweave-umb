# Plan: Queue Resilience & Smart Resubmission

## Phase 1: Fix Queue Timeouts

1. **wrangler.jsonc** — Increase `max_batch_timeout` from 10 to 30
2. **Queue consumer** — Wrap `processSubmission()` in `Promise.race()` with 25s timeout
3. **tier2.ts** — Add 8s `AbortSignal.timeout()` to `ai.run()` call

## Phase 2: Recovery Cron

4. **submission-store.ts** — Add `getStuckSubmissions()` that scans for non-terminal states older than 5 min
5. **Cron handler** — After discovery run, scan for stuck submissions and re-enqueue (or mark FAILED if already retried)

## Phase 3: Slug Collision Fix

6. **submission-store.ts** — Change slug generation to `{owner}-{repo}-{name}`
7. **publishSkill()** — Write new slug key; also write old slug as redirect/alias for backward compat
8. **getPublishedSkill()** — Try new slug first, fall back to old slug

## Phase 4: Smart Crawler Dedup

9. **github-discovery.ts** — After discovering skills in a repo, call dedup check per-skill before submitting
10. **submissions route** — Internal requests also respect dedup (skip already-verified)

## Phase 5: KV Pagination & Observability

11. **submission-store.ts** — Add cursor-based pagination to `getSubmissionIndex()` and `getPublishedSkillsList()`
12. **New route** — `GET /api/v1/admin/queue/status`

## Phase 6: Rate Limits

13. **discover route** — Add 20/IP/hour rate limit
14. **submissions route** — GitHub-authenticated users get 30/hour limit

## Files Modified

| File | Change |
|------|--------|
| wrangler.jsonc | max_batch_timeout: 30 |
| src/lib/queue/consumer.ts | Timeout wrapper |
| src/lib/scanner/tier2.ts | 8s AI timeout |
| src/lib/submission-store.ts | Slug fix, KV pagination, getStuckSubmissions |
| src/lib/crawler/github-discovery.ts | Per-skill dedup |
| src/app/api/v1/submissions/route.ts | Internal dedup |
| src/app/api/v1/admin/queue/status/route.ts | New endpoint |
| src/app/api/v1/submissions/discover/route.ts | Rate limit |

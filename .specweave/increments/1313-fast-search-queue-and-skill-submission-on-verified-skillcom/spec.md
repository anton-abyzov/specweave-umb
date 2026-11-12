# Fast search, queue and skill submission on verified-skill.com

## Problem

Measured on production, 2026-11-12:

- An uncached search (`GET /api/v1/skills/search?q=higg`) takes 5 to 20s; a cached one 0.15s. Server-Timing shows the edge index read at 2 to 4s and "enrichment" at 2 to 13s, while Postgres full-text answers in about 0.1s. The enrichment step looks up blocklisted and rejected skills from two KV sets. `search-index:rejected-set` does not exist in the production namespace (checked with `wrangler kv key list`), so every uncached search falls back to `ILIKE '%q%'` on the 3.9M-row Submission table. Nothing refreshes the sets except a manual admin call, and they expire after 7 days.
- The search palette aborts the in-flight request on every keystroke and has no timeout, so with multi-second responses no response lands and the user sees only skeletons. Each typed prefix is its own 30s cache entry. Failures show as "No results found".
- The public queue is down by scale: `GET /api/v1/submissions?state=active` returns 503 after 21s and `/api/v1/submissions/positions` 503 after 11s. 802k crawler rows sit in RECEIVED; the list runs `count(*)` over them and a ROW_NUMBER position map over every active row.
- `POST /api/v1/submissions` makes three sequential anonymous GitHub calls before saving, and a person's job waits in the same FIFO queue as crawler jobs behind a 30s batch timeout.
- `vskill submit owner/repo` without `--skill` gets a 400, `vskill skill publish <name>` can never work, and a brand-new local skill has no path to a pushed repo (first push has no upstream).

## Scope

In: search API and palette, queue list and position reads, submission intake latency, the vskill CLI and Studio create-to-queue path, quick UI fixes on search, queue and submit pages, a written list of remaining UI/UX gaps.
Out: new infrastructure (no Durable Object fan-out, no bigger database), the landing page (another thread), redesign of /publish private tenants, LLM scan model changes.

## Acceptance Criteria

- [ ] AC-01: An uncached production search for a 3 to 6 letter prefix returns in under 1s (Server-Timing enrichment under 100ms), and never runs a substring scan on Submission.
- [ ] AC-02: The blocklist and rejected KV sets are rebuilt on a schedule, so they cannot expire silently.
- [ ] AC-03: Typing "higg" in the palette shows results, never an endless skeleton: a slower response still renders, earlier results stay visible while a longer prefix loads, and a failure shows an error with Retry instead of "No results found".
- [ ] AC-04: `GET /api/v1/submissions?state=active` and `/api/v1/submissions/positions` answer 200 in under 2s on production.
- [ ] AC-05: `POST /api/v1/submissions` does at most one GitHub repo lookup before saving, and a person's submission is picked up within seconds, not behind crawler jobs.
- [ ] AC-06: `vskill submit owner/repo` works without `--skill`; `vskill skill publish` either works from a checkout or says what to run; the first push of a new skill sets upstream.
- [ ] AC-07: A new skill created locally and submitted lands in the production queue and its status page loads.
- [ ] AC-08: Remaining UI/UX gaps are listed for the owner, with the quick ones fixed.

## Approach

Three pull requests, shipped in order, each reviewed and released with `npm run release` (platform) or the vskill tag flow.

1. Search (vskill-platform): memoize the parsed KV sets per isolate, drop the Postgres fallbacks, start enrichment together with the edge read, rebuild the sets from cron, cache KV index reads at the colo, keep the response cache for minutes with a background refresh. Palette: latest-wins by sequence instead of abort, local filter of the previous results for a longer prefix, timeout, error state with Retry, combobox semantics.
2. Queue and submission (vskill-platform): positions per id with the existing `[state, priority, createdAt]` index, totals from the cron stats instead of `count(*)`, one cached repo-meta lookup on submit, person lane with a short batch timeout, parallel pre-scan reads. Quick UI fixes: loading states, dead links, keyboard access on the queue table, submit timeout.
3. vskill CLI and Studio: default skill name on submit, a working `skill publish`, `git push -u` on first push, `--wait` status follow.

Rejected: a trigram index on Submission (costs disk and write time on a 3.9M-row table to serve a lookup KV already covers); a dedicated search service (cost).

Risk: queue consumer config changes affect ingestion; the release gate rolls back on error signatures.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 On a KV miss, search returns no blocked or rejected extras instead of scanning Postgres → accepted; the sets are rebuilt by cron.
- D-02 Public queue totals come from the 10-minute stats and may lag → accepted.
### Open
- none

## Tasks

### T-01 Search API: fast enrichment, cron-rebuilt sets, colo-cached index reads, longer response cache
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/search/route.ts, repositories/anton-abyzov/vskill-platform/src/lib/search.ts, repositories/anton-abyzov/vskill-platform/src/lib/search-index.ts, repositories/anton-abyzov/vskill-platform/src/lib/search-index/chunked.ts | Test: npm --prefix repositories/anton-abyzov/vskill-platform test -- src/app/api/v1/skills/search src/lib/__tests__/search

### T-02 Search palette: results always land, local prefix filter, error and retry
- AC: AC-03 | Files: repositories/anton-abyzov/vskill-platform/src/app/components/SearchPalette.tsx | Test: npm --prefix repositories/anton-abyzov/vskill-platform test -- SearchPalette

### T-03 Queue list and positions answer fast
- AC: AC-04 | Files: repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/submission-list-route.ts, repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/positions/route.ts | Test: npm --prefix repositories/anton-abyzov/vskill-platform test -- src/app/api/v1/submissions

### T-04 Submission intake: one repo lookup, person lane picked up in seconds
- AC: AC-05 | Files: repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/route.ts, repositories/anton-abyzov/vskill-platform/wrangler.jsonc | Test: npm --prefix repositories/anton-abyzov/vskill-platform test -- src/app/api/v1/submissions

### T-05 vskill CLI and Studio: create, push and submit a new skill
- AC: AC-06 | Files: repositories/anton-abyzov/vskill/src/commands/submit.ts, repositories/anton-abyzov/vskill/src/commands/skill.ts | Test: npm --prefix repositories/anton-abyzov/vskill test -- submit

### T-06 Quick UI fixes and the UI/UX gap list
- AC: AC-08 | Files: repositories/anton-abyzov/vskill-platform/src/app/queue, repositories/anton-abyzov/vskill-platform/src/app/submit, repositories/anton-abyzov/vskill-platform/src/app/skills | Test: npm --prefix repositories/anton-abyzov/vskill-platform test -- src/app/queue src/app/submit

### T-07 Release and check on production
- AC: AC-01, AC-04, AC-07 | Files: .specweave/increments/1313-fast-search-queue-and-skill-submission-on-verified-skillcom/reports | Test: bash scripts/release/release.sh verify platform

### T-08 Verify and close 1313
- AC: AC-08 | Files: .specweave/increments/1313-fast-search-queue-and-skill-submission-on-verified-skillcom/spec.md | Test: specweave verify 1313-fast-search-queue-and-skill-submission-on-verified-skillcom

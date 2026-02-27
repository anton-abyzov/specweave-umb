# Implementation Plan: Fix Blocklist Global Poisoning, Duplicate Blocked Submissions, and Crawler Dedup Bypass

## Overview

Three surgical fixes to the vskill-platform submission pipeline. No schema migrations required -- all changes are query-level and logic-level within existing code.

## Architecture

### Bug 1: Scoped Blocklist Matching

**Root cause**: Every blocklist lookup uses `WHERE skillName = X AND isActive = true` without considering `sourceUrl`. The `BlocklistEntry` model already has a `sourceUrl` column, but it's never used in matching.

**Fix**: Introduce a shared helper `findActiveBlocklistEntry(skillName, repoUrl?)` that builds an OR query:
```
WHERE isActive = true AND skillName = X AND (sourceUrl = repoUrl OR sourceUrl IS NULL)
```

This means:
- Entries with `sourceUrl = null` are **global bans** (match any repo) -- backward compatible with any entries that lack a source
- Entries with `sourceUrl = "https://github.com/evil/repo"` only match submissions from that specific repo

**Files to change**:
1. `src/lib/blocklist-check.ts` (NEW) -- shared helper function for scoped blocklist matching
2. `src/lib/queue/process-submission.ts` -- use helper in early blocklist check (line 243)
3. `src/app/api/v1/internal/finalize-scan/route.ts` -- use helper in early blocklist check (line 257)
4. `src/app/api/v1/blocklist/check/route.ts` -- accept optional `repoUrl` param, use helper
5. `src/app/api/v1/submissions/[id]/route.ts` -- use helper for per-submission blocklist badge
6. `src/lib/blocklist-upsert.ts` -- add `sourceUrl` to the dedup lookup (line 42-48)
7. `src/lib/data.ts` -- use helper for skill detail blocklist check
8. `src/app/api/v1/admin/reports/[id]/route.ts` -- use helper in report resolution
9. `src/app/api/v1/admin/submissions/[id]/reject/route.ts` -- use helper in reject flow

### Bug 2: Blocked Dedup

**Root cause**: `checkSubmissionDedup` (line 55) groups BLOCKED with REJECTED/TIER1_FAILED/DEQUEUED and returns `kind: "rejected"`. The submission route (line 518-521) only blocks on `kind === "pending"` or `kind === "verified"`, letting `kind === "rejected"` fall through to create a new submission.

**Fix**: Split BLOCKED into its own dedup kind:
1. In `checkSubmissionDedup`, return `kind: "blocked"` instead of `kind: "rejected"` when state is BLOCKED
2. In `checkSubmissionDedupBatch`, same treatment
3. In POST `/api/v1/submissions`, handle `kind === "blocked"` by returning `{ blocked: true, submissionId }`

**Files to change**:
1. `src/lib/submission-dedup.ts` -- add `"blocked"` kind, return it for BLOCKED state
2. `src/app/api/v1/submissions/route.ts` -- handle `dedup.kind === "blocked"` in POST handler

### Bug 3: Crawler Discovery Dedup Race

**Root cause**: In `github-discovery.ts` `processRepo()`, the flow is:
1. `hasBeenDiscovered()` -- check
2. HTTP POST to `/api/v1/submissions` -- submit
3. `markDiscovered()` -- mark

When two parallel batches process the same repo, both can pass step 1 before either reaches step 3.

**Fix**: Move `markDiscovered()` to BEFORE the HTTP POST (write-ahead). On successful POST, update the record with `submissionId`. This is safe because:
- If the POST fails, the discovery record prevents infinite retries
- The stale-after-days TTL (30d) will naturally expire stale records
- On next discovery run, `hasBeenDiscovered` returns true, skipping duplicate submission

**Files to change**:
1. `src/lib/crawler/github-discovery.ts` -- reorder markDiscovered and submission POST in `processRepo()`

## Testing Strategy

- **Unit tests**: Update existing test suites for `submission-dedup.test.ts`, `blocklist-upsert.test.ts`, `blocklist-e2e.test.ts`
- **New unit tests**: `blocklist-check.test.ts` for the shared scoped matching helper
- **Integration**: Verify the crawler dedup ordering via `discovery-dedup.test.ts`
- Run full suite: `npx vitest run`

## Technical Challenges

### Challenge 1: Backward compatibility with seed data
**Context**: Seed data entries have `sourceUrl` set to specific malicious repos. The new scoped matching must continue to block those exact repos while NOT blocking legitimate skills with the same name from other repos.
**Solution**: The `OR` query `(sourceUrl = repoUrl OR sourceUrl IS NULL)` naturally handles this -- seed entries with a specific sourceUrl only match that repo.

### Challenge 2: Performance of OR queries on blocklist
**Context**: Adding an OR condition to blocklist lookups could slow queries.
**Solution**: The `@@index([skillName])` index on BlocklistEntry already covers the primary filter. The OR on `sourceUrl` adds minimal overhead since the result set after `skillName` filtering is tiny (usually 0-2 rows).

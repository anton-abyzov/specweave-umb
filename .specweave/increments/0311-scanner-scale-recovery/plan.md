# Plan: Fix Scanner Infrastructure & Scale Discovery to 60K+

## Approach

Four-phase execution: recovery first (operational), then crawler scaling (main code), dashboard fixes (parallel), and operational tooling (last).

## Phase 1: Recovery (Operational — T-001 to T-003)

Manual steps — no code changes. Deploy 0306, configure Cloudflare secrets, run rebuild-index.

## Phase 2: Scale Platform Crawler (T-004 to T-010)

**Primary repo**: `repositories/anton-abyzov/vskill-platform/`

### Token Rotation (T-004)
- Add `GITHUB_TOKENS` to `CloudflareEnv` interface in `src/lib/env.d.ts`
- In `github-discovery.ts`, parse `GITHUB_TOKENS` (comma-separated) → array
- Create `getNextToken()` function with round-robin counter
- Replace single `ghHeaders` construction with per-call token selection

### Query Diversity (T-005)
- Expand `CODE_SEARCH_QUERIES` and `REPO_SEARCH_QUERIES` arrays
- Add `generateTimeShardedQueries(baseQuery, days)` for date-bounded queries
- Add `generateStarShardedQueries(baseQuery)` for star-range shards
- Add npm keywords array expansion

### Parallel Sources (T-006)
- Wrap source functions in `Promise.allSettled()`
- Each source gets its own `seen` Set, merge after completion
- Preserve per-source error isolation

### Adaptive Delays (T-007)
- Extract `X-RateLimit-Remaining` and `X-RateLimit-Reset` from responses
- Replace `delay(QUERY_DELAY)` with `adaptiveDelay(rateLimitInfo)`
- Raise `MAX_PER_CRON` to 5,000

### Discovery TTL (T-008)
- Add `staleAfterDays` parameter to `hasBeenDiscovered()`
- Compare `lastSeenAt` against threshold
- Default 30 days

### Bulk Endpoint (T-009)
- Extend request body schema
- Pass tokens/dateRange/maxPerRun to `runGitHubDiscovery()`

### Tests (T-010)
- Unit tests in `src/lib/crawler/__tests__/`

## Phase 3: Dashboard Fixes (T-011 to T-013)

**Primary repo**: `repositories/anton-abyzov/specweave/`

Can run in parallel with Phase 2. Fixes the SpecWeave local dashboard to show real data from the platform API and handle missing token gracefully.

## Phase 4: Operational (T-014 to T-015)

Scripts and docs. After code changes are deployed.

## Risk Mitigation

- Token rotation: backward compatible — falls back to single `GITHUB_TOKEN`
- Parallel execution: `Promise.allSettled()` prevents one source failure from killing others
- Adaptive delay: conservative defaults, never goes below 200ms
- All changes are additive — no existing behavior removed

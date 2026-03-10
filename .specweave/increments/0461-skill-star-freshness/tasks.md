---
increment: 0461-skill-star-freshness
total_tasks: 12
completed_tasks: 12
by_user_story:
  US-005: [T-001, T-002]
  US-001: [T-003, T-004, T-005]
  US-002: [T-006, T-007, T-008]
  US-003: [T-009, T-010]
  US-004: [T-011, T-012]
---

# Tasks: Skill Star Count Freshness & Search Index Sync

> Implementation order follows plan.md: C5 → C1 → C2 → C3 → C4

---

## User Story: US-005 - Fix SearchShardQueueMessage Type

**Linked ACs**: AC-US5-01, AC-US5-02
**Tasks**: 2 total, 2 completed

### T-001: Add missing fields to SearchShardQueueMessage entry type

**User Story**: US-005 | **Satisfies ACs**: AC-US5-01 | **Status**: [x] completed

**Test Plan**:
- **Given** the `SearchShardQueueMessage` type in `src/lib/queue/types.ts`
- **When** an entry object is constructed by a caller with ownerSlug, repoSlug, skillSlug, trustTier
- **Then** TypeScript accepts it without a compile error

**Test Cases**:
1. **Unit**: `src/lib/queue/__tests__/types.test.ts`
   - `searchShardEntryAcceptsNewOptionalFields()`: Construct `SearchShardQueueMessage` with all four new fields — run `tsc --noEmit` to assert no compile error
   - **Coverage Target**: 100% (type-only change; compile check is the test)

**Implementation**:
1. Open `src/lib/queue/types.ts`
2. In `SearchShardQueueMessage.entry`, after `isTainted?`, add: `ownerSlug?: string; repoSlug?: string; skillSlug?: string; trustTier?: string;`
3. Run `npx tsc --noEmit` to confirm no errors

---

### T-002: Populate new slug fields in publishSkill() queue message

**User Story**: US-005 | **Satisfies ACs**: AC-US5-02 | **Status**: [x] completed

**Test Plan**:
- **Given** a skill published with ownerSlug, repoSlug, skillSlug, trustTier in its DB record
- **When** `publishSkill()` sends the search shard queue message
- **Then** the message entry contains all four fields populated from the skill record

**Test Cases**:
1. **Unit**: `src/lib/__tests__/submission-store.test.ts`
   - `publishSkillIncludesSlugFieldsInQueueMessage()`: Spy on `queue.send` — assert `message.entry` has `ownerSlug`, `repoSlug`, `skillSlug`, `trustTier` set from the skill DB record
   - **Coverage Target**: 90%

**Implementation**:
1. Locate queue message construction in `src/lib/submission-store.ts` (~line 1186)
2. Ensure `ownerSlug`, `repoSlug`, `skillSlug`, `trustTier` are included in the `entry` object (add explicitly if the conditional spread does not already cover them)
3. Run unit tests to confirm

---

## User Story: US-001 - Fetch GitHub Stars at Publish Time

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Tasks**: 3 total, 3 completed

### T-003: Create shared github-metrics.ts module

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed

**Test Plan**:
- **Given** a valid GitHub repo URL and an API token
- **When** `fetchGitHubStars()` is called
- **Then** it returns `{ stars: number; forks: number }` from the GitHub REST API within the timeout; on failure it returns `null`

**Test Cases**:
1. **Unit**: `src/lib/__tests__/github-metrics.test.ts`
   - `fetchGitHubStarsReturnsStarsAndForks()`: Mock `fetch` with 200 JSON — assert correct stars/forks returned
   - `fetchGitHubMetricsDetailedReturnsRateLimitInfo()`: Mock 429 response — assert `{ httpStatus: 429, retryAfterMs }` returned without throwing
   - `fetchGitHubStarsReturnsNullOnNetworkError()`: Mock `fetch` to throw — assert `null` returned
   - `fetchGitHubStarsReturnsNullOnTimeout()`: Mock `fetch` to delay past `timeoutMs` — assert `null` returned
   - **Coverage Target**: 95%

**Implementation**:
1. Create `src/lib/github-metrics.ts`
2. Export `fetchGitHubStars(repoUrl: string, token?: string, timeoutMs?: number): Promise<{ stars: number; forks: number } | null>` — calls `api.github.com/repos/{owner}/{repo}`, parses `stargazers_count` / `forks_count`
3. Export `fetchGitHubMetricsDetailed(repoUrl: string, token?: string): Promise<DetailedGitHubMetrics | null>` — full response including `httpStatus`, `retryAfterMs`, `lastCommitAt` for enrichment use
4. Use `parseGitHubUrl` from `popularity-fetcher.ts` for URL parsing
5. Accept explicit `token` parameter; never read `process.env.GITHUB_TOKEN`
6. Wrap fetch in `AbortController` with configurable `timeoutMs` (default 5000)
7. Run unit tests

---

### T-004: Integrate fetchGitHubStars into publishSkill()

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed

**Test Plan**:
- **Given** a skill being published
- **When** `publishSkill()` runs
- **Then** it calls `fetchGitHubStars()` before the DB upsert and stores the result in `githubStars`; if the API fails it falls back to 0 without failing the publish; the queue message entry reflects the fetched star count

**Test Cases**:
1. **Unit**: `src/lib/__tests__/submission-store.test.ts`
   - `publishSkillFetchesStarsBeforeUpsert()`: Mock `fetchGitHubStars` returning `{ stars: 1500 }` — assert `db.skill.upsert` called with `githubStars: 1500`
   - `publishSkillFallsBackToZeroWhenGitHubFails()`: Mock `fetchGitHubStars` to throw — assert publish completes with `githubStars: 0`
   - `publishSkillQueueMessageReflectsFetchedStars()`: Mock `fetchGitHubStars` returning 800 — assert queued `entry.githubStars === 800`
   - **Coverage Target**: 90%

**Implementation**:
1. Import `fetchGitHubStars` from `src/lib/github-metrics.ts` in `submission-store.ts`
2. Before `db.skill.upsert()`, resolve token from `getWorkerEnv()?.GITHUB_TOKEN` with fallback to `getCloudflareContext().env.GITHUB_TOKEN`
3. Call `fetchGitHubStars(sub.repoUrl, ghToken, 5000).catch(() => null)` — store as `starCount`
4. Pass `githubStars: starCount?.stars ?? 0` in both `create` and `update` blocks of the upsert and in the queue message entry
5. Run unit tests

---

### T-005: Replace local GitHub fetch functions in enrichment.ts and admin/enrich/route.ts

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed

**Test Plan**:
- **Given** `enrichment.ts` and `admin/enrich/route.ts` had local `fetchGitHubMetrics` / `fetchGitHub` functions
- **When** the shared module is in place
- **Then** both files import from `github-metrics.ts`, the local copies are deleted, and existing enrichment behaviour is unchanged

**Test Cases**:
1. **Unit**: `src/lib/cron/__tests__/enrichment.test.ts`
   - `enrichmentCallsSharedFetchGitHubMetrics()`: Mock `github-metrics` module — assert enrichment calls `fetchGitHubMetricsDetailed` from that module, not a local function
   - **Coverage Target**: 85%

**Implementation**:
1. In `enrichment.ts`, delete local `fetchGitHubMetrics()` and import `fetchGitHubMetricsDetailed` from `src/lib/github-metrics.ts`
2. In `admin/enrich/route.ts`, delete local `fetchGitHub()` and import from `src/lib/github-metrics.ts`
3. Run `npx tsc --noEmit` and unit tests

---

## User Story: US-002 - Enrichment Cron Dispatches Search Shard Updates

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Tasks**: 3 total, 3 completed

### T-006: Add buildSearchEntry() helper and SkillForSearchEntry type to search-index.ts

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed

**Test Plan**:
- **Given** a DB skill record with all relevant fields
- **When** `buildSearchEntry()` is called
- **Then** it returns a valid `SearchIndexEntry` with all fields correctly mapped; `buildSearchIndex()` uses it internally

**Test Cases**:
1. **Unit**: `src/lib/__tests__/search-index.test.ts`
   - `buildSearchEntryMapsAllRequiredFields()`: Pass a full mock skill — assert returned entry has correct name, certTier, trustScore, ownerSlug, repoSlug, skillSlug, trustTier
   - `buildSearchEntryHandlesNullOptionalFields()`: Pass record with null pluginName, command, skillPath — assert entry has `undefined` for those optional fields
   - **Coverage Target**: 95%

**Implementation**:
1. In `src/lib/search-index.ts`, define and export `SkillForSearchEntry` type matching the Prisma select used by `buildSearchIndex()`
2. Export `SEARCH_ENTRY_SELECT` constant (Prisma select object) for reuse in enrichment and admin endpoints
3. Export `buildSearchEntry(skill: SkillForSearchEntry): SearchIndexEntry`
4. Update `buildSearchIndex()` to call `buildSearchEntry()` internally
5. Run unit tests

---

### T-007: Add searchKv option to EnrichmentOptions and wire cron orchestration

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed

**Test Plan**:
- **Given** `runEnrichmentBatch()` is called with `searchKv` in options
- **When** the cron orchestration initialises enrichment
- **Then** `searchKv` receives `env.SEARCH_CACHE_KV` and is accessible within the batch loop

**Test Cases**:
1. **Unit**: `src/lib/cron/__tests__/enrichment.test.ts`
   - `enrichmentOptionsAcceptsSearchKv()`: Construct `EnrichmentOptions` with `searchKv` — assert `npx tsc --noEmit` passes (compile-time check)
   - **Coverage Target**: 80%

**Implementation**:
1. In `src/lib/cron/enrichment.ts`, add `searchKv?: QueueKV` to `EnrichmentOptions`
2. In `scripts/build-worker-entry.ts`, pass `searchKv: env.SEARCH_CACHE_KV` alongside existing `kv: env.SUBMISSIONS_KV`
3. Run `npx tsc --noEmit`

---

### T-008: Dispatch incremental shard updates in enrichment loop

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed

**Test Plan**:
- **Given** the enrichment batch updates a skill's `githubStars` or `npmDownloadsWeekly` to a different value
- **When** the DB transaction completes for that skill
- **Then** `updateSearchShard()` is called inline with `"upsert"` action; if metrics did not change no shard call is made; if the shard call fails enrichment continues to the next skill

**Test Cases**:
1. **Unit**: `src/lib/cron/__tests__/enrichment.test.ts`
   - `enrichmentDispatchesShardWhenStarsChange()`: Mock DB update changing `githubStars` — assert `updateSearchShard` called with `"upsert"`
   - `enrichmentDispatchesShardWhenDownloadsChange()`: Mock `npmDownloadsWeekly` change — assert `updateSearchShard` called
   - `enrichmentSkipsShardWhenMetricsUnchanged()`: Mock update where values match previous — assert `updateSearchShard` NOT called
   - `enrichmentContinuesWhenShardUpdateFails()`: Mock `updateSearchShard` to throw — assert next skill still processed
   - **Coverage Target**: 90%

**Implementation**:
1. After `tx.$transaction()` in the enrichment loop, compute `starsChanged` and `downloadsChanged` by comparing pre- and post-update values
2. If either changed and `opts.searchKv` is set: query fresh skill with `SEARCH_ENTRY_SELECT`, build entry via `buildSearchEntry()`, call `updateSearchShard(opts.searchKv, entry, "upsert")`
3. Wrap shard call in `.catch(err => console.warn(...))` — best-effort, non-blocking
4. Skip if `fresh.isDeprecated` is true
5. Run unit tests

---

## User Story: US-003 - Admin Refresh-Skills Endpoint

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Tasks**: 2 total, 2 completed

### T-009: Create refresh-skills POST handler

**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [x] completed

**Test Plan**:
- **Given** a POST to `/api/v1/admin/refresh-skills`
- **When** the body contains at least one filter (`repoUrl`, `author`, or `skillNames`)
- **Then** matching non-deprecated skills are re-enriched, DB updated, shard dispatched, and `{ refreshed, errors, skills }` returned; `dryRun: true` returns the skill list without modifications; empty body returns 400

**Test Cases**:
1. **Unit**: `src/app/api/v1/admin/refresh-skills/__tests__/route.test.ts`
   - `refreshByRepoUrlUpdatesMatchingSkills()`: POST `{ repoUrl }` — assert DB updated and shard dispatched for matching skills
   - `refreshByAuthorIsCaseInsensitive()`: POST `{ author: "Owner" }` — assert skills by "owner" or "Owner" matched
   - `refreshBySkillNamesMatchesExactly()`: POST `{ skillNames: ["a", "b"] }` — assert exactly those skills refreshed
   - `dryRunReturnsListWithoutModifying()`: POST `{ repoUrl, dryRun: true }` — assert no DB writes, returns `{ skills, count }`
   - `emptyBodyReturns400()`: POST `{}` — assert 400 with descriptive error
   - `missingAuthReturns401()`: No auth header — assert 401
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/app/api/v1/admin/refresh-skills/route.ts`
2. Auth check: `hasInternalAuth || requireAdmin` (following `admin/enrich/route.ts` pattern)
3. Zod schema: `{ repoUrl?: string, author?: string, skillNames?: string[], dryRun?: boolean }` with `.refine()` requiring at least one filter
4. Build Prisma `where` combining provided filters with `isDeprecated: false`
5. If `dryRun`: return `{ skills: names, count }` without mutations
6. For each skill: `fetchGitHubStars()`, `db.skill.update({ githubStars, metricsRefreshedAt })`, `updateSearchShard(kv, buildSearchEntry(fresh), "upsert")`
7. Return `{ refreshed: N, errors: N, skills: names }`
8. Run unit tests

---

### T-010: Run full compile and test check for refresh-skills

**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [x] completed

**Test Plan**:
- **Given** T-009 is complete
- **When** `npx tsc --noEmit` and `npx vitest run` execute
- **Then** zero type errors and all refresh-skills tests pass

**Test Cases**:
1. **Integration**: `src/app/api/v1/admin/refresh-skills/__tests__/route.test.ts`
   - `routeExportsPostHandler()`: Assert `route.ts` exports a named `POST` function
   - **Coverage Target**: 85%

**Implementation**:
1. Confirm route is at the correct Next.js App Router path (`route.ts` exports `POST`)
2. Run `npx tsc --noEmit`
3. Run `npx vitest run src/app/api/v1/admin/refresh-skills`

---

## User Story: US-004 - Admin Dedup-Skills Endpoint

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05
**Tasks**: 2 total, 2 completed

### T-011: Create dedup-skills POST handler

**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05 | **Status**: [x] completed

**Test Plan**:
- **Given** a POST to `/api/v1/admin/dedup-skills`
- **When** duplicate skills exist (same `repoUrl` + same `skillPath`)
- **Then** the endpoint detects them, keeps the highest-trustScore entry (tiebreaker: most recent `certifiedAt`), deprecates losers in DB, dispatches `remove` shard for each loser; `dryRun` returns groups without modifying; no duplicates returns `{ duplicateGroups: 0, deprecated: 0 }`

**Test Cases**:
1. **Unit**: `src/app/api/v1/admin/dedup-skills/__tests__/route.test.ts`
   - `detectsDuplicatesBySameRepoUrlAndSkillPath()`: Two skills same repoUrl+skillPath — assert group detected
   - `keepsBestTrustScore()`: Trust 0.9 vs 0.5 — assert 0.9 survives, 0.5 deprecated
   - `usesRecentCertifiedAtAsTiebreaker()`: Equal trust scores — assert most recent `certifiedAt` wins
   - `deprecatesLosersInDB()`: Assert loser has `isDeprecated: true` after endpoint runs
   - `removesLoserFromSearchShard()`: Assert `updateSearchShard` called with `"remove"` for each loser
   - `dryRunReturnsGroupsWithoutModifying()`: POST `{ dryRun: true }` — assert no DB writes, returns `{ duplicateGroups, groups }`
   - `returnsZeroCountsWhenNoDuplicates()`: No duplicates — assert `{ duplicateGroups: 0, deprecated: 0 }`
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/app/api/v1/admin/dedup-skills/route.ts`
2. Auth check following existing admin pattern
3. Find duplicate groups: raw SQL or Prisma `groupBy` on `(repoUrl, skillPath)` with `HAVING COUNT(*) > 1`, using `COALESCE(skillPath, '')` so null skillPaths group correctly
4. For each group: load all non-deprecated entries, sort by `trustScore DESC`, `certifiedAt DESC NULLS LAST` — winner = first, losers = rest
5. If `dryRun`: return `{ duplicateGroups, groups: [{ winner: name, losers: [name] }] }`
6. For each loser: `db.skill.update({ isDeprecated: true })`, `updateSearchShard(kv, buildSearchEntry(loser), "remove")`
7. Return `{ duplicateGroups: N, deprecated: N }`
8. Run unit tests

---

### T-012: Final compile, full test suite, and AC sign-off

**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05 | **Status**: [x] completed

**Test Plan**:
- **Given** all tasks T-001 through T-011 are complete
- **When** the full test suite runs
- **Then** all tests pass, `npx tsc --noEmit` reports zero errors, and every AC from spec.md is covered

**Test Cases**:
1. **Integration**: Full project
   - `npx tsc --noEmit`: zero type errors
   - `npx vitest run`: all tests pass with >= 90% overall coverage
   - **Coverage Target**: 90%

**Implementation**:
1. Confirm dedup-skills route exports `POST` at correct App Router path
2. Run `npx tsc --noEmit` — fix any remaining type errors
3. Run `npx vitest run` — fix any failing tests
4. Mark all ACs in `spec.md` as `[x]` completed
5. Update `completed_tasks` to 12 in this file's frontmatter

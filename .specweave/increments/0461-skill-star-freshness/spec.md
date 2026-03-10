---
increment: 0461-skill-star-freshness
title: Skill Star Count Freshness & Search Index Sync
type: feature
priority: P1
status: completed
created: 2026-03-09T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skill Star Count Freshness & Search Index Sync

## Problem Statement

Skills published on verified-skill.com sometimes show 0 stars in search results even when their GitHub repos have thousands of stars. Root causes:

1. `publishSkill()` never fetches GitHub stars before the DB upsert -- `githubStars` defaults to 0.
2. The enrichment cron updates stars in the DB but never dispatches incremental `updateSearchShard()` calls, so the KV search index remains stale until the next full rebuild.
3. Duplicate skill entries exist (same skill under old flat slug and new hierarchical slug) with no admin tooling to detect or resolve them.
4. `SearchShardQueueMessage.entry` is missing `ownerSlug`, `repoSlug`, `skillSlug`, and `trustTier` fields that `SearchIndexEntry` expects.

## Goals

- Every newly published skill displays its real GitHub star count in search immediately
- Enrichment cron propagates metric changes to the KV search index incrementally
- Admins can force-refresh metrics and deduplicate skills without a full index rebuild
- Search shard queue messages carry all fields needed for correct index entries

## User Stories

### US-001: Fetch GitHub Stars at Publish Time
**Project**: vskill-platform
**As a** skill searcher
**I want** newly published skills to show their GitHub star count immediately
**So that** I can assess skill popularity from the first search result

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a skill being published, when `publishSkill()` runs, then it fetches GitHub stars via the GitHub REST API (5s timeout) before the DB upsert and stores the result in `githubStars`
- [x] **AC-US1-02**: Given the GitHub API is unavailable or times out, when `publishSkill()` runs, then it falls back to `githubStars: 0` without failing the publish
- [x] **AC-US1-03**: Given a skill is published with fetched stars, when the search shard is updated, then the shard entry reflects the fetched star count (not 0)

---

### US-002: Enrichment Cron Dispatches Search Shard Updates
**Project**: vskill-platform
**As a** skill searcher
**I want** search results to reflect the latest star and download counts
**So that** the metrics I see are not stale between full index rebuilds

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given the enrichment batch updates a skill's `githubStars` to a value different from its previous DB value, when the batch loop completes that skill, then an `updateSearchShard()` call is dispatched for that skill
- [x] **AC-US2-02**: Given the enrichment batch updates a skill's `npmDownloadsWeekly` to a different value, when the batch loop completes that skill, then an `updateSearchShard()` call is dispatched for that skill
- [x] **AC-US2-03**: Given a skill's metrics did not change during enrichment, when the batch loop completes that skill, then no search shard update is dispatched
- [x] **AC-US2-04**: Given the search shard dispatch fails, when the enrichment processes the next skill, then enrichment continues (shard dispatch is best-effort, logged but non-blocking)

---

### US-003: Admin Refresh-Skills Endpoint
**Project**: vskill-platform
**As a** platform admin
**I want** to trigger targeted metric re-enrichment with immediate search shard sync
**So that** I can fix stale star counts for specific skills without waiting for the next cron cycle

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given a POST to `/api/v1/admin/refresh-skills` with body `{ repoUrl }`, when the endpoint runs, then it re-fetches GitHub metrics and dispatches search shard updates for all non-deprecated skills matching that repoUrl
- [x] **AC-US3-02**: Given a POST with body `{ author }`, when the endpoint runs, then it re-enriches all non-deprecated skills by that author
- [x] **AC-US3-03**: Given a POST with body `{ skillNames: ["a", "b"] }`, when the endpoint runs, then it re-enriches exactly those named skills
- [x] **AC-US3-04**: Given a POST with body `{ dryRun: true }`, when the endpoint runs, then it returns the list of skills that would be refreshed without making any DB or shard updates
- [x] **AC-US3-05**: Given a POST with an empty body (no filters), when the endpoint runs, then it returns 400 with an error message requiring at least one filter

---

### US-004: Admin Dedup-Skills Endpoint
**Project**: vskill-platform
**As a** platform admin
**I want** to detect and deprecate duplicate skill entries
**So that** search results do not show the same skill twice under different slugs

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given a POST to `/api/v1/admin/dedup-skills`, when duplicate skills exist (same `repoUrl` + same `skillPath`), then the endpoint identifies them as duplicates
- [x] **AC-US4-02**: Given duplicates are found, when the endpoint resolves them, then it keeps the entry with the highest `trustScore` (tiebreaker: most recent `certifiedAt`) and deprecates the others by setting `isDeprecated: true`
- [x] **AC-US4-03**: Given a duplicate is deprecated, when the shard is updated, then a `remove` action is dispatched for the deprecated entry's search shard
- [x] **AC-US4-04**: Given a POST with body `{ dryRun: true }`, when the endpoint runs, then it returns the list of duplicate groups and which entry would survive without modifying the DB
- [x] **AC-US4-05**: Given no duplicates exist, when the endpoint runs, then it returns a 200 with `{ duplicateGroups: 0, deprecated: 0 }`

---

### US-005: Fix SearchShardQueueMessage Type
**Project**: vskill-platform
**As a** developer
**I want** `SearchShardQueueMessage.entry` to include all fields that `SearchIndexEntry` expects
**So that** incremental shard updates produce complete index entries

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given the `SearchShardQueueMessage` type in `queue/types.ts`, when reviewed, then `entry` includes optional fields `ownerSlug`, `repoSlug`, `skillSlug`, and `trustTier` matching `SearchIndexEntry`
- [x] **AC-US5-02**: Given all callers that construct `SearchShardQueueMessage`, when they build the `entry` object, then they populate `ownerSlug`, `repoSlug`, `skillSlug`, and `trustTier` from the skill's DB record

## Out of Scope

- Full search index rebuild optimization (existing `buildSearchIndex` is unchanged)
- Real-time WebSocket push of metric updates to the frontend
- Merging install counts across duplicates (negligible, KV-keyed per skill name)
- Changes to the enrichment cron schedule or batch size
- GitHub GraphQL API migration (REST API with token is sufficient)

## Technical Notes

### Dependencies
- GitHub REST API (`api.github.com/repos/{owner}/{repo}`) for star fetches
- Existing `parseGitHubUrl` from `popularity-fetcher.ts`
- Existing `updateSearchShard` from `search-index.ts`
- Existing admin auth pattern (`requireAdmin` + `hasInternalAuth`)

### Constraints
- Star fetch at publish time: 5s timeout, best-effort (non-blocking)
- Enrichment shard dispatch: only when `githubStars` or `npmDownloadsWeekly` actually changed
- Admin endpoints: require `X-Internal-Key` or `SUPER_ADMIN` JWT
- `refresh-skills`: at least one filter required (no "refresh everything" footgun)
- Dedup winner: highest `trustScore`, tiebreaker `certifiedAt` DESC

### Architecture Decisions
- Inline `updateSearchShard` calls in enrichment loop rather than queue messages, since enrichment already runs in the worker context with KV access
- Admin endpoints follow the existing pattern in `/api/v1/admin/enrich/route.ts`
- Dedup discards install counts on deprecated entries (no merge)

## Success Metrics

- 100% of newly published skills show non-zero stars in search within 60s of publish (when repo has stars)
- 0 stale star counts in search index after enrichment cron completes
- Admin can resolve all duplicates in a single dedup endpoint call

# Tasks: 0342-db-first-skill-architecture

## Phase 1: Schema Migration & DB Seed

### T-001: Add Prisma schema columns and indexes
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test**: Given schema.prisma → When migration runs → Then Skill model has extensible, extensibilityTier, extensionPoints, source columns and new indexes

Add to Skill model in prisma/schema.prisma:
- `extensible Boolean @default(false)`
- `extensibilityTier String?`
- `extensionPoints Json @default("[]")`
- `source String @default("community")`
- `@@index([githubStars(sort: Desc)])`
- `@@index([trustScore(sort: Desc)])`
- `@@index([createdAt(sort: Desc)])`
- `@@index([author])`

Run: `npx prisma migrate dev --name add_extensibility_and_source`

### T-002: Create idempotent seed script
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Test**: Given seed script runs → When querying DB → Then ~133 skills exist with correct data, search_vector populated

Create `scripts/seed-skills.ts`:
- Import skills from seed-data.ts
- Map each to Prisma Skill upsert (keyed on `name`)
- Include all fields: displayName, description, author, repoUrl, category, currentVersion, certTier, certMethod, certScore, trustScore, trustTier, labels, githubStars, githubForks, npmDownloads, npmPackage, trendingScore7d, trendingScore30d, extensible, extensibilityTier, extensionPoints, source: "seed"
- Batch in chunks of 20
- Add to push-deploy.sh after db:generate

## Phase 2: Data Layer Rewrite

### T-003: Rewrite getSkills() to DB-only
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test**: Given filters {category: "coding", sortBy: "githubStars", limit: 20, offset: 0} → When getSkills() called → Then returns 20 skills from DB sorted by stars, no seed-data.ts imported

Replace merge logic in data.ts with pure Prisma findMany:
- Build WHERE clause from filters (category, certTier, author, search, extensible)
- ORDER BY from sortBy/sortDir
- SKIP/TAKE from offset/limit
- Return mapDbSkillToSkillData() results

### T-004: Rewrite getSkillByName(), getSkillCategories(), getTrendingSkills()
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03, AC-US2-05 | **Status**: [x] completed
**Test**: Given skill name "algorithmic-art" → When getSkillByName() called → Then returns skill from DB (not seed lookup)

- getSkillByName(): db.skill.findUnique({ where: { name } })
- getSkillCategories(): db.skill.groupBy({ by: ["category"], _count: true })
- getTrendingSkills(): db.skill.findMany({ orderBy: { trendingScore7d: "desc" }, take: limit })

### T-005: Add getSkillCount(filters) and update mapDbSkillToSkillData()
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04, AC-US2-06 | **Status**: [x] completed
**Test**: Given filters → When getSkillCount(filters) called → Then returns count from db.skill.count()

- New getSkillCount(): builds same WHERE as getSkills(), returns db.skill.count()
- mapDbSkillToSkillData(): add extensible, extensibilityTier, extensionPoints fields

### T-006: Add build-time fallback
**User Story**: US-002 | **Satisfies ACs**: AC-US2-07 | **Status**: [x] completed
**Test**: Given DB unreachable during build → When getSkills() called → Then returns seed-data.ts fallback without error

Wrap getSkills() with try/catch that falls back to seed data during build only.

## Phase 3: Pre-Computed Stats

### T-007: Create computePlatformStats() function
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**Test**: Given skills in DB → When computePlatformStats() called → Then returns object with totalSkills, totalStars, uniqueRepos, categories, topStarRepos, topNpmSkills from DB aggregates

New file: src/lib/stats-compute.ts
- db.skill.count() for totals
- db.skill.groupBy() for categories
- Raw SQL for deduped stars
- findMany with ORDER BY for top-N lists

### T-008: Create stats refresh cron and getPlatformStats()
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Test**: Given stats computed → When written to KV → Then getPlatformStats() returns cached blob

New file: src/lib/cron/stats-refresh.ts
- Calls computePlatformStats()
- Writes to SUBMISSIONS_KV key `platform:stats` (2h TTL)
- getPlatformStats(): reads KV, falls back to live compute

### T-009: Add PlatformStats type
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**Test**: Given PlatformStats type → When used in stats-compute.ts → Then TypeScript compiles

Add to src/lib/types.ts: PlatformStats interface with all stat fields.

## Phase 4: Background Enrichment

### T-010: Create enrichment batch job
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02 | **Status**: [x] completed
**Test**: Given 20 skills with stale updatedAt → When enrichment runs → Then githubStars and npmDownloads updated in DB

New file: src/lib/cron/enrichment.ts
- Select 20 oldest-refreshed skills
- Fetch GitHub API (stars, forks, lastCommitAt) and npm API (downloads)
- Update Skill rows in DB
- Compute trending scores

### T-011: Integrate enrichment + stats into cron handler
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03, AC-US4-04 | **Status**: [x] completed
**Test**: Given hourly cron fires → When handler runs → Then enrichment + stats refresh execute

Add to scheduled handler: runEnrichmentBatch() then refreshPlatformStats().

## Phase 5: Simplify Publish Pipeline

### T-012: Remove KV dual-write from publishSkill()
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04 | **Status**: [x] completed
**Test**: Given skill published → When publishSkill() called → Then only Prisma upsert runs, no KV skill write

In submission-store.ts:
- Remove KV `skill:{slug}` put
- Remove addToPublishedIndex() call
- Remove dead functions
- Remove _publishedCache from data.ts
- Keep SUBMISSIONS_KV for sub/scan/hist keys

## Phase 6: Consumer Updates

### T-013: Update homepage to use pre-computed stats
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01 | **Status**: [x] completed
**Test**: Given stats in KV → When homepage renders → Then shows correct totalSkills, stars, repos from pre-computed stats

Replace in page.tsx:
- `const [stats, topSkills] = await Promise.all([getPlatformStats(), getTrendingSkills(8)])`
- Remove all in-memory stats computation functions

### T-014: Update skills browse page with DB pagination
**User Story**: US-006 | **Satisfies ACs**: AC-US6-02 | **Status**: [x] completed
**Test**: Given 133 skills in DB → When browsing page 2 with limit 20 → Then shows skills 21-40 from DB

Replace in skills/page.tsx:
- getSkills({ limit: PER_PAGE, offset: (page-1)*PER_PAGE })
- getSkillCount(filters) for total
- Remove allSkills.slice()

### T-015: Update API routes
**User Story**: US-006 | **Satisfies ACs**: AC-US6-03, AC-US6-04 | **Status**: [x] completed
**Test**: Given API call GET /api/v1/skills?limit=20&offset=20 → Then returns 20 skills from DB with X-Total-Count header

- /api/v1/skills: DB pagination + count
- /api/v1/stats: return getPlatformStats()

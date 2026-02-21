# Tasks: Fix Marketplace Skill Loss

## Phase 1: Immediate Fix (P0)

### T-001: Add enumeratePublishedSkills() function
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-04 | **Status**: [ ] pending
**Test**: Given KV contains 50 `skill:*` keys and 3 `skill:alias:*` keys → When `enumeratePublishedSkills()` is called → Then it returns 50 `PublishedSkillSummary` objects (aliases excluded), handling pagination across multiple list pages

**Implementation**:
- Add `enumeratePublishedSkills()` to `submission-store.ts`
- Reuse existing `listAllKeys()` helper for cursor-based pagination
- Filter out `skill:alias:*` keys
- Read each `skill:*` value and parse into `PublishedSkillSummary`
- Handle malformed values gracefully (skip with warning)

---

### T-002: Update getPublishedSkillsList() with enumeration fallback
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [ ] pending
**Test**: Given KV index blob has 5 entries but KV enumeration finds 50 → When `getPublishedSkillsList()` is called → Then it returns 50 entries AND triggers index rebuild

**Implementation**:
- Call both index blob read and `enumeratePublishedSkills()`
- Compare counts, return the larger set (deduplicated by slug)
- If enumeration > index, rebuild the index blob from enumerated data
- If both are empty, return empty (seed data handles base case)

---

### T-003: Cache enumeration results in existing published cache
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [ ] pending
**Test**: Given `enumeratePublishedSkills()` takes 300ms → When `getPublishedSkillsList()` is called twice within 60s → Then the second call returns in <5ms from cache

**Implementation**:
- Integrate enumeration into the existing `_publishedCache` in `data.ts`
- The cache already has 60s TTL and is reset via `_resetPublishedCache()`
- No new caching mechanism needed

---

### T-004: Unit tests for KV enumeration
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06 | **Status**: [ ] pending
**Test**: Test suite covers: empty index + populated keys, populated index + fewer keys, pagination with multiple pages, alias key exclusion, malformed value handling

**Implementation**:
- Add test file `src/lib/__tests__/kv-enumeration.test.ts`
- Mock KV with `vi.hoisted()` + `vi.mock()`
- Test scenarios: 0 keys, 50 keys across 2 pages, alias exclusion, JSON parse error

---

### T-005: Document addToPublishedIndex as best-effort cache
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02, AC-US5-03 | **Status**: [ ] pending
**Test**: Given `submission-store.ts` → When reviewed → Then `addToPublishedIndex()` has JSDoc comment explaining it is a cache, not source of truth

**Implementation**:
- Add JSDoc to `addToPublishedIndex()`
- Add JSDoc to `getPublishedSkillsList()`
- Note that Prisma is the durable source, KV index is cache

---

## Phase 2: Durable Source of Truth (P0-P1)

### T-006: Add Prisma write to publishSkill()
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [ ] pending
**Test**: Given a submission with ID "sub_123" and scan score 92 → When `publishSkill()` is called → Then a Prisma `Skill` record is upserted with correct fields AND the KV write also succeeds

**Implementation**:
- In `publishSkill()`, after KV write, call `getDb()` and upsert Skill record
- Map fields: slug -> name, skillName -> displayName, repoUrl -> repoUrl, extractOwner -> author
- Set certTier: SCANNED, certMethod: AUTOMATED_SCAN, certScore: scan.score
- Wrap Prisma call in try/catch (KV path must still succeed if Prisma fails)
- Handle extensibility: store extensionPoints in labels array as JSON

---

### T-007: Unit tests for dual publish (KV + Prisma)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [ ] pending
**Test**: Test suite covers: successful dual write, Prisma failure with KV success, duplicate skill upsert

**Implementation**:
- Update existing `submission-store.test.ts` or create new test file
- Mock both KV and Prisma
- Verify Prisma upsert is called with correct fields
- Verify KV write succeeds even when Prisma throws

---

### T-008: Add getPublishedSkillsFromDb() to data.ts
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [ ] pending
**Test**: Given Prisma `Skill` table has 200 records → When `getPublishedSkillsFromDb()` is called with `{ category: "development", limit: 20 }` → Then it returns 20 development-category skills sorted by trendingScore7d

**Implementation**:
- New async function in `data.ts`
- Query `db.skill.findMany()` with where/orderBy/skip/take
- Support all existing filter params: category, certTier, author, search, extensible, sortBy, sortDir, offset, limit
- Map Prisma `Skill` to `SkillData` interface

---

### T-009: Update getSkills() to Prisma-primary
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-05 | **Status**: [ ] pending
**Test**: Given Prisma has 200 skills and seed has 118 → When `getSkills()` is called → Then it returns 200 + unique seed skills not in Prisma (merged without duplicates)

**Implementation**:
- Try Prisma first via `getPublishedSkillsFromDb()`
- If Prisma succeeds, merge with seed data (seed is canonical for its 118 skills)
- If Prisma fails, fall back to existing KV + seed path
- Dedup by skill name (seed wins for overlapping names)

---

### T-010: Update getSkillByName() to check Prisma
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [ ] pending
**Test**: Given skill "my-cool-skill" exists in Prisma but not in KV → When `getSkillByName("my-cool-skill")` is called → Then it returns the Prisma skill data

**Implementation**:
- After seed check, try `db.skill.findUnique({ where: { name } })`
- If found, map to `SkillData` and return
- If Prisma fails, fall back to existing KV path

---

### T-011: Update getSkillCount() and getSkillCategories()
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [ ] pending
**Test**: Given Prisma has 200 skills → When `getSkillCount()` is called → Then returns 200 + unique seed skills

**Implementation**:
- `getSkillCount()`: try `db.skill.count()` + unique seed count, fall back to existing
- `getSkillCategories()`: try `db.skill.groupBy({ by: ["category"] })` + seed categories, fall back to existing

---

### T-012: Unit tests for Prisma-primary data layer
**User Story**: US-003 | **Satisfies ACs**: AC-US3-07 | **Status**: [ ] pending
**Test**: Test suite covers: Prisma available path, Prisma failure fallback, merge with seed, filter support, pagination

**Implementation**:
- Update `data.test.ts` with Prisma mock scenarios
- Test fallback chain: Prisma -> KV enum -> KV index -> seed

---

### T-013: Create admin rebuild-index endpoint
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05 | **Status**: [ ] pending
**Test**: Given KV has 50 `skill:*` keys → When POST /api/v1/admin/rebuild-index is called → Then `skills:published-index` is rebuilt with 50 entries AND Prisma is backfilled with 50 Skill records

**Implementation**:
- New file `src/app/api/v1/admin/rebuild-index/route.ts`
- Auth via `requireRole()` or X-Internal-Key
- Enumerate all `skill:*` keys, read values
- Write new `skills:published-index` blob
- Upsert each skill into Prisma `Skill` table
- Return `{ ok: true, rebuilt, errors, orphanedAliases, prismaBackfilled }`

---

### T-014: Unit tests for rebuild-index endpoint
**User Story**: US-004 | **Satisfies ACs**: AC-US4-06 | **Status**: [ ] pending
**Test**: Test suite covers: rebuild from 0 keys, rebuild from 50 keys with aliases, malformed values, auth check

**Implementation**:
- New test file `src/app/api/v1/admin/rebuild-index/__tests__/route.test.ts`
- Mock KV and Prisma
- Test auth rejection for unauthenticated requests

---

### T-015: Fix DATABASE_URL in worker/cron context
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03 | **Status**: [ ] pending
**Test**: Given worker env has DATABASE_URL but process.env does not → When `getDb()` is called from cron context → Then it returns a working PrismaClient using the worker env URL

**Implementation**:
- Update `getDb()` in `db.ts` to check `getWorkerEnv()?.DATABASE_URL` as fallback
- Update `worker-with-queues.js` to set `process.env.DATABASE_URL` from env before cron calls
- Add clear error logging when DATABASE_URL is not available

---

### T-016: Document DATABASE_URL worker binding
**User Story**: US-006 | **Satisfies ACs**: AC-US6-04 | **Status**: [ ] pending
**Test**: Given wrangler.jsonc → When reviewed → Then DATABASE_URL is documented as required secret

**Implementation**:
- Verify DATABASE_URL is configured in Cloudflare dashboard as a secret (not in wrangler.jsonc for security)
- Add comment in `worker-with-queues.js` documenting the requirement

---

### T-017: Unit tests for getDb() worker context fallback
**User Story**: US-006 | **Satisfies ACs**: AC-US6-05 | **Status**: [ ] pending
**Test**: Test suite covers: process.env available, worker env fallback, neither available (throws)

**Implementation**:
- Add tests to `src/lib/__tests__/db.test.ts`
- Mock `getWorkerEnv()` and `process.env`

---

## Phase 3: Monitoring (P2)

### T-018: Create health monitoring endpoint
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04 | **Status**: [ ] pending
**Test**: Given KV index has 45 entries, KV enumeration finds 50, Prisma has 48 → When GET /api/v1/admin/health/skills is called → Then response shows drift_detected: true with specific drifts and recommendations

**Implementation**:
- New file `src/app/api/v1/admin/health/skills/route.ts`
- Query all four sources: KV index count, KV enumeration count, Prisma count, seed count
- Compare counts; flag drift when difference > 5% or > 10 skills
- Generate recommendations array
- Auth via requireRole or X-Internal-Key

---

### T-019: Unit tests for health endpoint
**User Story**: US-007 | **Satisfies ACs**: AC-US7-05 | **Status**: [ ] pending
**Test**: Test suite covers: no drift, KV index < KV keys, Prisma < KV, auth check

**Implementation**:
- New test file `src/app/api/v1/admin/health/skills/__tests__/route.test.ts`
- Mock all data sources
- Verify drift detection thresholds

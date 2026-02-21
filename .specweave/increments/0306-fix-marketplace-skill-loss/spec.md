---
increment: 0306-fix-marketplace-skill-loss
title: "Fix Marketplace Skill Loss - Restore KV Enumeration + Prisma Migration"
type: bug
priority: P0
status: planned
created: 2026-02-21
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Fix: Marketplace Skill Loss - Restore KV Enumeration + Prisma Migration

## Overview

**Severity**: Critical / Production
**Impact**: Marketplace skill count dropped from thousands of community skills to 1-3. Users see nearly empty marketplace.

### Root Cause Analysis

The marketplace data layer (`data.ts`) merges 118 seed skills with community skills read from a single KV blob (`skills:published-index`). Five compounding failures cause skill loss:

1. **Single-blob index as sole data source**: `getPublishedSkillsList()` reads only the `skills:published-index` KV key. If this blob is corrupted, stale, or empty, ALL community skills vanish from the marketplace. Individual `skill:*` keys (one per published skill) survive but are never enumerated for the list view.

2. **Slug format changed 3x, migration reads from the index**: `migrateSkillSlugs()` reads from `skills:published-index` to discover which skills to migrate. If the index is empty (due to #1), migration has nothing to migrate, creating a permanent data gap where old-format `skill:*` keys remain orphaned.

3. **Race condition in `addToPublishedIndex()`**: This function does read-modify-write on a single KV key without atomicity. Concurrent queue workers can overwrite each other's additions, silently losing skills from the index even when individual `skill:*` keys are written successfully.

4. **Prisma `Skill` table exists but is completely unused for serving**: The DB schema has a full `Skill` model with certTier, scores, labels, etc. but `data.ts` never queries Prisma. The only data path is: seed data + KV blob. Published skills should be written to Prisma AND KV, and reads should use Prisma as primary.

5. **Discovery cron may silently fail after 0291**: The DB-based dedup (`discovery-dedup.ts`) requires `DATABASE_URL` in the worker context. The cron handler in `worker-with-queues.js` calls `runGitHubDiscovery(env)` but does not set `DATABASE_URL` in process.env, causing `getDb()` to throw, which is caught and silently logged.

### Fix Strategy

**Phase 1 (Immediate)**: Add `getPublishedSkillsFromKV()` that enumerates all `skill:*` keys via `kv.list()`, bypassing the index blob. Use this as fallback when the index returns fewer skills than KV enumeration. Rebuild the index from KV keys.

**Phase 2 (Durable)**: Write published skills to the Prisma `Skill` table during `publishSkill()`. Migrate `getSkills()` / `getSkillByName()` to read from Prisma as primary source of truth, with KV as fast cache.

**Phase 3 (Monitoring)**: Add a health endpoint that compares KV key count vs index count vs Prisma count. Alert when drift exceeds threshold. Add logging to discovery cron for DATABASE_URL availability.

## User Stories

### US-001: KV Enumeration Fallback for Published Skills (P0)
**Project**: specweave

**As a** marketplace visitor
**I want** all published skills to appear in the skill listing
**So that** I can discover community skills even when the KV index blob is stale or corrupted

**Acceptance Criteria**:
- [ ] **AC-US1-01**: New function `enumeratePublishedSkills()` in `submission-store.ts` uses `kv.list({ prefix: "skill:" })` with pagination to discover all individual skill keys, excluding `skill:alias:*` keys
- [ ] **AC-US1-02**: `getPublishedSkillsList()` calls both the index blob AND `enumeratePublishedSkills()`, returns whichever has MORE entries (with dedup by slug)
- [ ] **AC-US1-03**: When enumeration finds more skills than the index, the index is rebuilt from the enumerated data (write-through repair)
- [ ] **AC-US1-04**: `enumeratePublishedSkills()` handles KV list pagination correctly (cursor-based, handles `list_complete` flag)
- [ ] **AC-US1-05**: Performance: KV enumeration adds at most 500ms latency for up to 5000 keys; results are cached in the existing `_publishedCache` for 60s
- [ ] **AC-US1-06**: Unit tests cover: empty index + populated keys scenario, populated index + fewer keys scenario, pagination with multiple pages, alias key exclusion

---

### US-002: Write Published Skills to Prisma Skill Table (P0)
**Project**: specweave

**As a** platform operator
**I want** every published skill to be persisted in the Prisma `Skill` table
**So that** I have a durable, queryable source of truth that survives KV corruption

**Acceptance Criteria**:
- [ ] **AC-US2-01**: `publishSkill()` in `submission-store.ts` upserts a record into `Skill` table (via Prisma) in addition to writing to KV; uses `repoUrl` + `name` for dedup
- [ ] **AC-US2-02**: Prisma `Skill` fields populated from submission + scan data: name (slug), displayName (skillName), description, author (extracted from repoUrl), repoUrl, category (default "development"), currentVersion ("1.0.0"), certTier (SCANNED), certMethod (AUTOMATED_SCAN), certScore, certifiedAt, labels (["community","verified"])
- [ ] **AC-US2-03**: If Prisma write fails (e.g., DB unreachable), the KV-only path still succeeds (graceful degradation)
- [ ] **AC-US2-04**: Extensibility metadata (extensible, extensionPoints) stored as JSON in Skill labels or a new column if needed
- [ ] **AC-US2-05**: Unit tests cover: successful dual write, Prisma failure with KV success, duplicate skill upsert updates instead of errors

---

### US-003: Migrate getSkills() to Prisma-Primary (P1)
**Project**: specweave

**As a** platform operator
**I want** the skills listing page to read from Prisma as the primary source
**So that** the marketplace is resilient to KV blob corruption and can leverage SQL filtering/sorting

**Acceptance Criteria**:
- [ ] **AC-US3-01**: New function `getPublishedSkillsFromDb()` in `data.ts` queries `Skill` table with support for category, certTier, author, search, sorting, pagination, and extensibility filtering
- [ ] **AC-US3-02**: `getSkills()` reads from Prisma if available, falls back to seed+KV if Prisma fails (e.g., at build time when no DATABASE_URL)
- [ ] **AC-US3-03**: `getSkillByName()` checks Prisma before KV; returns Prisma data if found
- [ ] **AC-US3-04**: `getSkillCount()` and `getSkillCategories()` also query Prisma when available
- [ ] **AC-US3-05**: Seed data is still merged (not duplicated): skills that exist in seed AND Prisma use the seed data (seed is canonical for those 118 skills)
- [ ] **AC-US3-06**: Performance: Prisma query for paginated listing completes in <200ms (existing indexes on category, certTier, trendingScore7d)
- [ ] **AC-US3-07**: Unit tests mock Prisma client to verify fallback path, merge logic, and filter support

---

### US-004: Rebuild Published Index from Surviving KV Keys (P1)
**Project**: specweave

**As a** platform operator
**I want** a one-time admin endpoint that rebuilds `skills:published-index` from individual `skill:*` KV keys
**So that** I can recover from a corrupted index without manual KV surgery

**Acceptance Criteria**:
- [ ] **AC-US4-01**: New `POST /api/v1/admin/rebuild-index` endpoint, authenticated via X-Internal-Key or SUPER_ADMIN JWT
- [ ] **AC-US4-02**: Endpoint enumerates all `skill:*` keys (excluding `skill:alias:*`), reads each value, rebuilds the `skills:published-index` blob
- [ ] **AC-US4-03**: Also populates Prisma `Skill` table from the KV data (backfill for US-002)
- [ ] **AC-US4-04**: Returns a report: `{ rebuilt: N, errors: M, orphanedAliases: K }`
- [ ] **AC-US4-05**: Idempotent: running multiple times produces the same result
- [ ] **AC-US4-06**: Unit tests cover: rebuild from 0 keys, rebuild from 50 keys with 2 aliases, error handling for malformed KV values

---

### US-005: Fix addToPublishedIndex Race Condition (P1)
**Project**: specweave

**As a** platform operator
**I want** concurrent skill publishes to not lose index entries
**So that** the published index stays consistent under queue concurrency

**Acceptance Criteria**:
- [ ] **AC-US5-01**: `addToPublishedIndex()` is made idempotent and resilient to concurrent writes: either uses KV metadata versioning for optimistic concurrency, or the index becomes a secondary cache that is periodically rebuilt (US-004 approach)
- [ ] **AC-US5-02**: Since Prisma is now the primary source (US-002/US-003), the KV index becomes a performance cache; if a race loses an entry, the next cache rebuild or Prisma read recovers it
- [ ] **AC-US5-03**: Document in code comments that `skills:published-index` is a best-effort cache, not source of truth
- [ ] **AC-US5-04**: Unit tests verify that concurrent calls to `addToPublishedIndex()` with different slugs do not lose entries (simulated with delayed reads)

---

### US-006: Fix Discovery Cron DATABASE_URL in Worker Context (P1)
**Project**: specweave

**As a** platform operator
**I want** the discovery cron to have access to DATABASE_URL in the worker context
**So that** DB-based dedup does not silently fail and new skills continue to be discovered

**Acceptance Criteria**:
- [ ] **AC-US6-01**: The scheduled handler in `worker-with-queues.js` sets `process.env.DATABASE_URL` from `env.DATABASE_URL` (or via `setWorkerEnv`) before calling `runGitHubDiscovery(env)`
- [ ] **AC-US6-02**: `getDb()` in `db.ts` also checks the worker env (via `getWorkerEnv()`) for DATABASE_URL, similar to how `getKV()` uses worker context as fallback
- [ ] **AC-US6-03**: If DATABASE_URL is not available, discovery logs a clear error message (not a silent catch) and falls back gracefully
- [ ] **AC-US6-04**: Add `DATABASE_URL` as a secret binding in `wrangler.jsonc` vars or secrets (or document that it must be configured)
- [ ] **AC-US6-05**: Unit tests verify that `getDb()` uses worker context when `process.env.DATABASE_URL` is not set

---

### US-007: Marketplace Health Monitoring Endpoint (P2)
**Project**: specweave

**As a** platform operator
**I want** a health endpoint that reports skill count consistency across data sources
**So that** I can detect skill loss early before users are affected

**Acceptance Criteria**:
- [ ] **AC-US7-01**: New `GET /api/v1/admin/health/skills` endpoint returns `{ kv_index_count, kv_enumerated_count, prisma_count, seed_count, drift_detected, drifts: [] }`
- [ ] **AC-US7-02**: Drift is flagged when any count differs from another by more than 5% or more than 10 skills
- [ ] **AC-US7-03**: Endpoint is authenticated (SUPER_ADMIN or X-Internal-Key)
- [ ] **AC-US7-04**: Response includes a `recommendations` array with actionable suggestions (e.g., "Run rebuild-index to fix KV drift")
- [ ] **AC-US7-05**: Unit tests cover: no drift scenario, KV index < KV keys drift, Prisma < KV drift

## Functional Requirements

### FR-001: Data Source Priority
The data layer MUST query sources in this order: (1) Prisma Skill table, (2) KV enumeration, (3) KV index blob, (4) seed data. Each layer is a fallback for the one above.

### FR-002: Backward Compatibility
Existing seed data (118 skills) MUST continue to appear. The slug format (`makeSlug`) MUST NOT change. Existing `skill:alias:*` keys MUST continue to resolve.

### FR-003: No Data Loss During Migration
The transition from KV-primary to Prisma-primary MUST be additive. No published skill should disappear during the migration window.

## Success Criteria

- Marketplace shows correct total skill count (seed + all published community skills)
- KV enumerated count matches Prisma count within 5%
- Discovery cron successfully writes to DB dedup table in worker context
- No skill loss incidents for 7 days after deployment

## Out of Scope

- Removing KV entirely (KV stays as cache layer)
- Changing the scan/publish pipeline (only adding Prisma write)
- UI changes to the marketplace page (data layer only)
- Migrating seed data into Prisma (seed stays hardcoded)

## Dependencies

- Prisma `Skill` table already exists in schema (no migration needed)
- DATABASE_URL must be configured as a Cloudflare secret for worker context
- Existing `listAllKeys()` helper in `submission-store.ts` for KV enumeration

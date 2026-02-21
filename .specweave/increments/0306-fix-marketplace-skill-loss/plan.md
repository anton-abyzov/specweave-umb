# Implementation Plan: Fix Marketplace Skill Loss

## Overview

This plan addresses a critical production bug where the marketplace dropped from thousands of community skills to 1-3 visible skills. The root cause is over-reliance on a single KV blob (`skills:published-index`) as the sole source of community skill data, combined with race conditions in concurrent writes, slug migration reading from the same blob, and the Prisma `Skill` table being completely unused for serving.

The fix has three phases: (1) immediate KV enumeration fallback, (2) Prisma as durable source of truth, (3) health monitoring.

## Architecture

### Current Data Flow (Broken)

```
[Seed Data: 118 skills] ──merge──> getSkills() ──> Marketplace Page
                                       ^
[KV "skills:published-index" blob] ────┘ (single blob, prone to corruption/loss)

[KV "skill:{slug}" keys] ─── NOT enumerated for list view
[Prisma Skill table]      ─── NOT used at all for reads
```

### Target Data Flow (Fixed)

```
[Seed Data: 118 skills] ──merge──> getSkills() ──> Marketplace Page
                                       ^
[Prisma Skill table] ─── PRIMARY ─────┘
                                       ^
[KV enumeration "skill:*"] ── FALLBACK ┘ (when Prisma unavailable)
                                       ^
[KV "skills:published-index"] ── CACHE ┘ (best-effort, rebuilt periodically)
```

### Components Modified

| File | Change |
|------|--------|
| `src/lib/submission-store.ts` | Add `enumeratePublishedSkills()`, update `getPublishedSkillsList()` fallback, update `publishSkill()` to write Prisma |
| `src/lib/data.ts` | Add `getPublishedSkillsFromDb()`, update `getSkills()` / `getSkillByName()` to read Prisma-first |
| `src/lib/db.ts` | Update `getDb()` to check worker context for DATABASE_URL |
| `src/lib/worker-context.ts` | No changes needed (already has get/set/clear) |
| `.open-next/worker-with-queues.js` | Set DATABASE_URL from env before cron calls |
| `src/app/api/v1/admin/rebuild-index/route.ts` | NEW: Admin endpoint for index rebuild + Prisma backfill |
| `src/app/api/v1/admin/health/skills/route.ts` | NEW: Health monitoring endpoint |

### Data Model

No schema changes needed. The existing Prisma `Skill` model has all required fields:
- `name` (unique slug), `displayName`, `description`, `author`, `repoUrl`
- `category`, `currentVersion`, `certTier`, `certMethod`, `certScore`, `certifiedAt`
- `labels`, `trendingScore7d`, `trendingScore30d`

### API Contracts

**POST /api/v1/admin/rebuild-index**
- Auth: X-Internal-Key or SUPER_ADMIN JWT
- Response: `{ ok: true, rebuilt: number, errors: number, orphanedAliases: number, prismaBackfilled: number }`

**GET /api/v1/admin/health/skills**
- Auth: X-Internal-Key or SUPER_ADMIN JWT
- Response: `{ kv_index_count, kv_enumerated_count, prisma_count, seed_count, drift_detected, drifts: [], recommendations: [] }`

## Technology Stack

- **Language/Framework**: TypeScript, Next.js 15, Cloudflare Workers
- **Database**: PostgreSQL via Prisma (existing)
- **Cache**: Cloudflare KV (existing SUBMISSIONS_KV binding)
- **Testing**: Vitest, ESM mocking via `vi.hoisted()` + `vi.mock()`

### Architecture Decisions

- **Prisma as primary, KV as cache**: KV has no transactions or atomic read-modify-write. Prisma gives us SQL UPSERT atomicity. KV stays as a fast cache for the listing page.
- **Additive migration**: We never remove data from KV during this increment. The migration is purely additive: write to Prisma in addition to KV, read from Prisma with KV fallback.
- **Rebuild endpoint over migration script**: A rebuild endpoint can be run repeatedly and is accessible from cron/admin UI. A migration script runs once and is harder to retry.

## Implementation Phases

### Phase 1: Immediate Fix (US-001, US-005)
1. Add `enumeratePublishedSkills()` function that uses `kv.list({ prefix: "skill:" })` with pagination
2. Update `getPublishedSkillsList()` to compare index blob vs enumeration, return larger set
3. Auto-repair index when enumeration finds more skills
4. Document `addToPublishedIndex()` as best-effort cache (not source of truth)

### Phase 2: Durable Source of Truth (US-002, US-003, US-004, US-006)
1. Update `publishSkill()` to upsert into Prisma `Skill` table
2. Add `getPublishedSkillsFromDb()` that queries Prisma
3. Update `getSkills()`, `getSkillByName()`, `getSkillCount()`, `getSkillCategories()` to read Prisma-first
4. Create admin rebuild endpoint to backfill Prisma from KV keys
5. Fix DATABASE_URL availability in worker/cron context

### Phase 3: Monitoring (US-007)
1. Create health endpoint comparing all data sources
2. Add drift detection logic
3. Add actionable recommendations

## Testing Strategy

- **TDD mode**: RED-GREEN-REFACTOR for all new functions
- **Unit tests**: Mock KV (`kv.list`, `kv.get`, `kv.put`) and Prisma client
- **Integration pattern**: Tests verify fallback chains (Prisma down -> KV enum -> KV index -> seed)
- **Concurrency tests**: Simulate parallel `addToPublishedIndex()` calls
- **ESM mocking**: Use `vi.hoisted()` + `vi.mock()` pattern per project memory

## Technical Challenges

### Challenge 1: KV List Pagination in Workers
**Problem**: `kv.list()` returns paginated results. Must handle cursor correctly.
**Solution**: Reuse existing `listAllKeys()` helper from `submission-store.ts` (already handles pagination with cursor).
**Risk**: Low. Helper is battle-tested.

### Challenge 2: Prisma Availability in Worker Context
**Problem**: Queue consumers and cron handlers run in worker context where `process.env` is not automatically set from Cloudflare env.
**Solution**: Extend `getDb()` to check `getWorkerEnv()` for DATABASE_URL. Set `process.env.DATABASE_URL` in scheduled handler before calling discovery.
**Risk**: Medium. Need to ensure DATABASE_URL is configured as a Cloudflare secret.

### Challenge 3: Build-Time Prisma Calls
**Problem**: During `next build`, there is no DATABASE_URL. Prisma calls will fail.
**Solution**: All Prisma reads are wrapped in try/catch with fallback to KV/seed. The existing `catch {}` pattern in `data.ts` already handles this for KV; extend it to Prisma.
**Risk**: Low. Existing pattern proven.

### Challenge 4: Concurrent publishSkill Writes
**Problem**: Multiple queue workers can call `publishSkill()` simultaneously.
**Solution**: Prisma `upsert()` is atomic. KV write is last-writer-wins (acceptable for cache). The index blob is documented as a cache that is periodically rebuilt.
**Risk**: Low. Prisma upsert handles this natively.

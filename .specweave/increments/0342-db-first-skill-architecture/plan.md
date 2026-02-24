# Plan: 0342-db-first-skill-architecture

## Approach

Phased migration from in-memory seed merge to DB-first architecture. Each phase is independently deployable.

## Phase 1: Schema + Seed (Foundation)
1. Add Prisma columns: extensible, extensibilityTier, extensionPoints, source
2. Add DB indexes: githubStars DESC, trustScore DESC, createdAt DESC, author
3. Create idempotent seed script that upserts 118 skills from seed-data.ts
4. Run migration + seed against Neon

## Phase 2: Data Layer Rewrite (Core Change)
1. Rewrite getSkills() → pure Prisma query
2. Rewrite getSkillByName() → db.skill.findUnique()
3. Rewrite getSkillCategories() → db.skill.groupBy()
4. Add getSkillCount(filters) → db.skill.count()
5. Rewrite getTrendingSkills() → DB ORDER BY
6. Update mapDbSkillToSkillData() for new fields
7. Add build-time fallback for SSG

## Phase 3: Pre-Computed Stats
1. Create computePlatformStats() with DB aggregates
2. Create stats-refresh cron (writes to KV platform:stats)
3. Create getPlatformStats() helper (reads KV, fallback live)

## Phase 4: Background Enrichment
1. Create enrichment batch job (20 skills/hour, GitHub + npm API)
2. Add trending score computation formula
3. Integrate into hourly cron handler

## Phase 5: Simplify Publish Pipeline
1. Remove KV dual-write from publishSkill()
2. Remove dead KV skill functions
3. Remove _publishedCache

## Phase 6: Consumer Updates
1. Homepage → getPlatformStats() + getTrendingSkills(8)
2. Skills page → DB pagination with SKIP/TAKE
3. /api/v1/skills → DB pagination + count
4. /api/v1/stats → KV stats blob

## Parallelization Strategy

- Phase 1 (schema + seed) must complete first
- Phases 2, 3, 4 can be developed in parallel
- Phase 5 depends on Phase 2 (data layer must be DB-first before removing KV reads)
- Phase 6 depends on Phases 2 + 3 (consumers need new data layer + stats)

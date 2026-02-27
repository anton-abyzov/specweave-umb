---
increment: 0342-db-first-skill-architecture
title: "Database-first skill architecture"
type: feature
priority: P1
status: completed
created: 2026-02-23
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Feature: Database-First Skill Architecture

## Overview

Move all skills (certified vendor + community) into the Prisma/Neon DB as the single source of truth. Remove the in-memory seed-data merge from `getSkills()`. Add pre-computed platform stats, background enrichment cron, and DB-level filtering/sorting/pagination.

## Background

The vskill-platform currently has 118 "seed" skills hardcoded in TypeScript (`seed-data.ts`, 3756 lines) that are never stored in the DB. The `Skill` table only has ~15 community-submitted skills. `getSkills()` merges seed + DB + KV in memory on every request, then filters/sorts/paginates in JavaScript. Homepage stats (stars, downloads, categories) are computed in-memory per request. Community skills get `githubStars: 0, npmDownloads: 0` permanently because no background enrichment writes back to DB.

## User Stories

### US-001: Schema Migration & DB Seed
**Project**: vskill-platform

**As a** platform operator
**I want** all 118 seed skills stored in the Prisma DB with full data
**So that** the DB is the single source of truth for all skills

**ACs:**
- [x] AC-US1-01: Prisma schema has new columns: extensible, extensibilityTier, extensionPoints, source
- [x] AC-US1-02: DB indexes added for githubStars DESC, trustScore DESC, createdAt DESC, author
- [x] AC-US1-03: Idempotent seed script upserts all 118 skills into DB with full data (stars, downloads, trending, cert info)
- [x] AC-US1-04: After seed, `SELECT COUNT(*) FROM "Skill"` returns ~133 (118 seed + existing community)
- [x] AC-US1-05: search_vector trigger populates tsvector for all seeded skills (full-text searchable)

### US-002: DB-Only Data Layer
**Project**: vskill-platform

**As a** developer
**I want** `getSkills()` to be a pure DB query with no in-memory merge
**So that** filtering, sorting, and pagination happen at the DB level

**ACs:**
- [x] AC-US2-01: `getSkills()` uses Prisma WHERE/ORDER BY/SKIP/TAKE — no seed-data.ts import
- [x] AC-US2-02: `getSkillByName()` is a single `db.skill.findUnique()` — no seed lookup
- [x] AC-US2-03: `getSkillCategories()` uses `db.skill.groupBy()` — no in-memory counting
- [x] AC-US2-04: New `getSkillCount(filters)` function uses `db.skill.count()` for pagination totals
- [x] AC-US2-05: `getTrendingSkills()` uses DB query with ORDER BY trendingScore7d DESC
- [x] AC-US2-06: `mapDbSkillToSkillData()` maps new fields: extensible, extensibilityTier, extensionPoints
- [x] AC-US2-07: Build-time fallback: if DB unreachable during `next build`, falls back to seed-data.ts

### US-003: Pre-Computed Platform Stats
**Project**: vskill-platform

**As a** homepage visitor
**I want** stats (total skills, stars, downloads, categories) to load instantly
**So that** the homepage doesn't recompute everything on each visit

**ACs:**
- [x] AC-US3-01: `computePlatformStats()` uses DB aggregate queries (COUNT, GROUP BY, SUM, raw SQL for deduped stars)
- [x] AC-US3-02: Stats stored in KV key `platform:stats` with 2h TTL
- [x] AC-US3-03: `getPlatformStats()` reads KV blob, falls back to live computation if missing
- [x] AC-US3-04: Homepage uses pre-computed stats — no `getSkills()` full-load
- [x] AC-US3-05: `/api/v1/stats` returns KV-cached stats — no in-memory iteration

### US-004: Background Enrichment Cron
**Project**: vskill-platform

**As a** platform operator
**I want** skill metrics (GitHub stars, npm downloads) updated automatically
**So that** the DB has fresh data and trending scores reflect reality

**ACs:**
- [x] AC-US4-01: Enrichment batch job selects 20 oldest-refreshed skills, fetches GitHub + npm metrics, writes to DB
- [x] AC-US4-02: Trending scores recomputed based on actual star/download data
- [x] AC-US4-03: Stats refresh runs after enrichment, updates KV blob
- [x] AC-US4-04: Integrated into existing hourly cron handler

### US-005: Simplify Publish Pipeline (DB-Only)
**Project**: vskill-platform

**As a** developer
**I want** `publishSkill()` to write only to Prisma (no KV dual-write)
**So that** there's no split-brain between KV and DB

**ACs:**
- [x] AC-US5-01: `publishSkill()` removes KV `skill:{slug}` write and `addToPublishedIndex()` call
- [x] AC-US5-02: Dead KV skill functions removed: getPublishedSkill, getPublishedSkillsList, enumeratePublishedSkills, addToPublishedIndex
- [x] AC-US5-03: `_publishedCache` in data.ts removed
- [x] AC-US5-04: SUBMISSIONS_KV retained for submission lifecycle (sub/scan/hist keys)

### US-006: Consumer Updates (Homepage, APIs, Pages)
**Project**: vskill-platform

**As a** user browsing skills
**I want** pages to use efficient DB queries with proper pagination
**So that** the site stays fast even with thousands of skills

**ACs:**
- [x] AC-US6-01: Homepage uses `getPlatformStats()` + `getTrendingSkills(8)` — no full skill load
- [x] AC-US6-02: Skills browse page uses DB-level SKIP/TAKE pagination with total count
- [x] AC-US6-03: `/api/v1/skills` uses DB pagination + count query
- [x] AC-US6-04: `/api/v1/stats` returns KV-cached stats blob

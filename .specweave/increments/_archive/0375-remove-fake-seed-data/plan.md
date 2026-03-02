# Implementation Plan: Remove fake seed data from vskill-platform

## Overview

This is a data cleanup refactor that removes 156 hardcoded fake skill entries from `src/lib/seed-data.ts`, renames the file to `agent-data.ts` (keeping only the 44 agent entries), updates the Prisma seed script, adds counter-based 404 deprecation to enrichment, creates a production DB cleanup script, and updates all tests.

## Architecture

### Components Affected

1. **`src/lib/seed-data.ts` -> `src/lib/agent-data.ts`**: Remove all skill data, keep agents only
2. **`prisma/seed.ts`**: Remove skill upsert, keep admin + blocklist + agent compat seeding
3. **`src/lib/cron/enrichment.ts`**: Add repo404Count tracking and threshold-based deprecation
4. **`scripts/cleanup-seed-skills.ts`**: New one-time cleanup script for production DB
5. **Test files**: Update mocks, remove seed-accuracy tests, add 404 counter tests

### Data Model Change

Add to Prisma `Skill` model:
```prisma
repo404Count  Int     @default(0)
```

This tracks consecutive GitHub 404 responses during enrichment. Reset to 0 on successful fetch. Deprecates skill when threshold (3) reached.

### Files Modified

| File | Change |
|------|--------|
| `src/lib/seed-data.ts` | DELETE (git mv to agent-data.ts, strip skills) |
| `src/lib/agent-data.ts` | NEW (agents array + AgentData re-export only) |
| `src/lib/data.ts` | Update import path |
| `src/lib/agent-branding.ts` | Update comment |
| `prisma/seed.ts` | Remove skill upsert loop, update import |
| `prisma/schema.prisma` | Add `repo404Count` field |
| `src/lib/cron/enrichment.ts` | Add 404 counter logic |
| `scripts/cleanup-seed-skills.ts` | NEW cleanup script |
| `src/lib/__tests__/seed-data-accuracy.test.ts` | DELETE |
| `src/lib/__tests__/data.test.ts` | Update mock path |
| `src/lib/__tests__/popularity-fetcher.test.ts` | Remove TC-021 seed import test |
| `src/lib/cron/__tests__/enrichment.test.ts` | Add 404 counter tests |

## Technology Stack

- **Language/Framework**: TypeScript, Prisma, Vitest
- **Database**: PostgreSQL (via Prisma)
- **Runtime**: Node.js (scripts), Cloudflare Workers (production)

**Architecture Decisions**:
- **Counter-based 404 deprecation**: Rather than immediately deprecating on a single 404, use a counter with threshold=3. This handles transient GitHub outages gracefully.
- **Static agents**: Agents remain in static code (not DB) because they change infrequently and are used for UI display only.
- **Dry-run-first cleanup**: The DB cleanup script defaults to dry-run mode for safety. Production execution requires explicit `--execute` flag.

## Implementation Phases

### Phase 1: Prisma Schema + Migration
1. Add `repo404Count` to Skill model
2. Generate and apply migration

### Phase 2: File Rename + Data Removal
1. Create `agent-data.ts` with agents only
2. Delete `seed-data.ts`
3. Update all imports across codebase

### Phase 3: Seed Script Update
1. Remove skill upsert loop from `prisma/seed.ts`
2. Remove `SKILL_NAME_RENAMES` map
3. Update import to `agent-data`
4. Keep admin + blocklist seeding intact

### Phase 4: Enrichment 404 Hardening
1. Add `repo404Count` increment on 404
2. Add threshold check and auto-deprecation
3. Add counter reset on successful fetch

### Phase 5: DB Cleanup Script
1. Create `scripts/cleanup-seed-skills.ts`
2. Identify seed skills by known ID patterns (`sk_anthropic_*`, `sk_openai_*`, `sk_google_*`, `sk_community_*`, `sk_specweave_*`, `sk_mktg_*`)
3. Delete in correct FK order: MetricsSnapshot -> AgentCompat -> SkillVersion -> Skill
4. Dry-run mode by default

### Phase 6: Test Updates
1. Delete `seed-data-accuracy.test.ts`
2. Update mock paths in `data.test.ts`
3. Remove TC-021 from `popularity-fetcher.test.ts`
4. Add enrichment 404 counter tests
5. Run full test suite

## Testing Strategy

- **TDD mode**: RED -> GREEN -> REFACTOR per project config
- Write failing tests for 404 counter behavior FIRST
- Then implement enrichment changes
- Verify all existing tests pass after import path updates
- Cleanup script tested via dry-run against real DB

## Technical Challenges

### Challenge 1: Distinguishing seed skills from real pipeline skills in DB
**Solution**: Use known ID prefix patterns (`sk_anthropic_*`, etc.) and cross-reference with seed data names. The cleanup script will skip any skill that has a submission record (came through pipeline).
**Risk**: Very low -- seed skills have distinct naming patterns and no submission records.

### Challenge 2: Agent compat records depend on skill IDs
**Solution**: The cleanup script deletes AgentCompat records for seed skills before deleting the skills. Real skills from the pipeline will have their own AgentCompat records created during submission processing.
**Risk**: None -- FK cascade handles this correctly.

### Challenge 3: Breaking existing imports
**Solution**: Comprehensive grep for all `seed-data` references, update systematically. Only 6 files import from it.
**Risk**: Low -- Vitest and TypeScript compiler will catch any missed imports.

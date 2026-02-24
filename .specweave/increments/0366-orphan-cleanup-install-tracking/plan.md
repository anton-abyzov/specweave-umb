# Implementation Plan: Orphan cleanup on re-submission + install tracking phone-home

## Overview

Two independent features sharing a single increment because they both improve data quality for the same `Skill` model. No schema changes needed -- both features use existing columns (`isDeprecated`, `vskillInstalls`).

## Architecture

### Components

- **Orphan Cleanup Module** (`src/lib/orphan-cleanup.ts`): Pure function that takes a list of `{ repoUrl, skillName }` pairs and deprecates matching stale Skill records. Called from the submission route.
- **Install Tracking Endpoint** (`src/app/api/v1/skills/[name]/installs/route.ts`): New Next.js API route that increments `vskillInstalls`.
- **CLI Phone-Home** (`src/api/client.ts` in the vskill repo): New `reportInstall(skillName)` function. Called from `src/commands/add.ts` after successful install.

### Data Model

No new tables or columns. Uses existing fields:
- `Skill.isDeprecated: Boolean @default(false)` -- set to `true` on orphan cleanup
- `Skill.vskillInstalls: Int @default(0)` -- incremented by install tracking endpoint

### API Contracts

#### Existing (modified)
- `POST /api/v1/submissions` -- adds orphan cleanup step before creating submissions

#### New
- `POST /api/v1/skills/:name/installs`
  - **Auth**: None (public, rate-limited)
  - **Rate limit**: 60/hour per IP via `checkRateLimit(RATE_LIMIT_KV, "install:{ip}", 60, 3600)`
  - **Request**: Empty body (skill name is in URL path)
  - **Response 200**: `{ ok: true }`
  - **Response 404**: `{ error: "Skill not found" }`
  - **Response 429**: `{ error: "Too many requests" }` + `Retry-After` header

## Technology Stack

- **Language/Framework**: TypeScript, Next.js 15, Cloudflare Workers
- **Database**: Prisma (PostgreSQL)
- **Rate Limiting**: Existing KV-based `checkRateLimit()`
- **CLI**: Node.js ESM (vskill repo)

**Architecture Decisions**:
- **Same-transaction cleanup vs cron**: Cleanup in the submission flow avoids a separate cron job. The cost is one `findMany` + one `updateMany` per submission request, which is negligible.
- **Simple counter vs dedup**: A simple counter is appropriate for the current scale. Deduplication adds complexity (tracking install IDs, user fingerprints) that is not justified yet.
- **IP-based rate limiting**: Consistent with existing submission endpoint pattern. 60/hour is generous enough for legitimate use while preventing abuse.
- **Fire-and-forget phone-home**: Using `AbortController` with 2s timeout ensures the CLI never blocks. All errors are swallowed.

## Implementation Phases

### Phase 1: Orphan Cleanup (Platform)
1. Create `src/lib/orphan-cleanup.ts` with `deprecateOrphanSkills(pairs: { repoUrl, skillName }[])` function
2. Integrate into `POST /api/v1/submissions` -- both single-skill and batch paths
3. Write unit tests for the cleanup logic

### Phase 2: Install Tracking Endpoint (Platform)
1. Create `src/app/api/v1/skills/[name]/installs/route.ts`
2. Implement rate limiting + atomic increment
3. Write unit tests

### Phase 3: CLI Phone-Home (vskill CLI)
1. Add `reportInstall(skillName)` to `src/api/client.ts`
2. Call from `src/commands/add.ts` after successful install
3. Respect `VSKILL_NO_TELEMETRY` env var
4. Write unit tests

## Testing Strategy

- **Unit tests**: Orphan cleanup logic (mock Prisma), install endpoint (mock DB + KV), CLI phone-home (mock fetch)
- **Integration**: Manually verify orphan cleanup in submission flow, verify counter increments
- **All tests use Vitest** with `vi.mock()` / `vi.hoisted()` for ESM mocking

## Technical Challenges

### Challenge 1: Slug Resolution for Orphan Matching
**Problem**: The submission uses `skillName` but Skill records use a slug derived from `repoUrl + skillName`. Must use the same `makeSlug()` function from `submission-store.ts`.
**Solution**: Import `makeSlug` and resolve slugs before the `findMany` query.
**Risk**: Low -- `makeSlug` is a pure function already used in `publishSkill`.

### Challenge 2: Race Condition on Concurrent Submissions
**Problem**: Two concurrent submissions for the same skill could both try to deprecate the same Skill record.
**Solution**: Eventual consistency is acceptable per requirements. The `updateMany` is idempotent (setting `isDeprecated = true` twice is harmless). No locking needed.

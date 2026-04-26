# Implementation Plan: Fix submission published-skill link collision

## Overview

Two-layer fix to the read path on `vskill-platform`. Layer 1 makes the submission detail page link to the actual published Skill via the existing `submission.skillId` relation. Layer 2 hardens the legacy-redirect endpoint to refuse ambiguous matches instead of silently picking one. Both layers are read-only — no schema migration, no write-path change.

## Design

### Components

- **`src/lib/data.ts` — `getSubmissionFull(id)`** (line 844). Today returns `{ submission, scanResult, stateHistory }`. We extend it to additionally return `publishedSkillName: string | null` by Prisma-`include`-ing the `skill` relation on the submission fetch (or a follow-up `db.skill.findUnique({where:{id: submission.skillId}, select:{name:true}})` if the existing fetch doesn't go through Prisma).
- **`src/app/api/v1/submissions/[id]/route.ts`** — surfaces `publishedSkillName` in the JSON body alongside `skillName`. No change to caching (`Cache-Control: no-cache`) or error paths.
- **`src/app/submit/[id]/page.tsx`** — the `(currentState === "PUBLISHED" || ...)` block at line 644-653 swaps `href={skillUrl(data.skillName)}` for a small helper:
  ```ts
  const publishedHref = data.publishedSkillName
    ? skillUrl(data.publishedSkillName)
    : skillUrl(data.skillName);
  ```
  Because `skillUrl()` already handles the 3-segment canonical case (`src/lib/skill-url.ts:14-21`), passing the hierarchical name yields `/skills/<owner>/<repo>/<skill>` directly — bypassing the legacy redirect entirely.
- **`src/app/api/v1/legacy-redirect/[slug]/route.ts`** — `findFirst` → `findMany({ take: 2 })`. Three branches: 0 → 404, 1 → 301 (existing canonical builder), 2+ → 404 with `X-Legacy-Ambiguous: true` header.

### Data Model

No schema change. Existing relations:

- `Submission.skillId` → `Skill.id` (already populated by `publish.ts:634-636` on publish).
- `Skill.name` is the hierarchical 3-segment string (e.g. `anton-abyzov/greet-anton/greet-anton-abyzov`) created by `buildHierarchicalName()` in `src/lib/slug.ts:105-107` and stored as the unique key on the Skill row.

### API Contracts

- `GET /api/v1/submissions/[id]` — response body gains one field:
  ```json
  {
    "id": "sub_...",
    "repoUrl": "...",
    "skillName": "greet-anton-abyzov",
    "publishedSkillName": "anton-abyzov/greet-anton/greet-anton-abyzov",
    "skillPath": "...",
    "state": "PUBLISHED",
    "...": "..."
  }
  ```
  Field is `string | null`. Backwards compatible — no existing client breaks.
- `GET /api/v1/legacy-redirect/[slug]` — adds `X-Legacy-Ambiguous: true` response header on 404 when 2+ skills share the slug.

## Technology Stack

- **Framework**: Next.js 15 App Router (vskill-platform).
- **Persistence**: Prisma + Cloudflare D1/Postgres. Read-only Prisma calls.
- **Tests**: vitest. ESM mocking via `vi.hoisted()` + `vi.mock()` per project convention.

**Architecture Decisions**:

- **Use existing `submission.skillId` relation, not the legacy slug.** The data is already correct on write; the bug is purely on read. Joining via the foreign key eliminates an entire class of slug-collision risk and is the simplest correct fix.
- **Defense in depth at the legacy-redirect layer too.** Even after Layer 1 lands, anyone reaching `/skills/<flat>` from an external link (badge, bookmark, GitHub README) still hits the redirect. Refusing ambiguity there protects every entry point, not just the submit page.
- **No `@@unique` migration in this increment.** Production data has duplicate `legacySlug` rows; adding a unique constraint requires a dedup migration that's out of scope. Refusing ambiguity at runtime is the correct interim behaviour.
- **Header `X-Legacy-Ambiguous: true` for ops debugging.** Lets us identify ambiguity hits in logs without parsing the 404 body. No PII, no skill names — just a boolean.

## Implementation Phases

### Phase 1: TDD RED
Write failing vitest tests for all three branches (data join, API response, legacy-redirect ambiguity).

### Phase 2: TDD GREEN
- Update `getSubmissionFull` to include the joined `Skill.name` as `publishedSkillName`.
- Update the API route to surface the field.
- Update the submit page to prefer it.
- Update the legacy-redirect handler to use `findMany({take:2})` with the three-branch decision.

### Phase 3: REFACTOR + verify
- Run full vitest suite to ensure no regressions in adjacent files.
- Manual verify: hit the production submission `sub_8f8f75d7-...` after deploy and confirm the link resolves correctly.

## Testing Strategy

- **Unit (vitest)**: mock Prisma client; assert `publishedSkillName` is the linked Skill's hierarchical name when `skillId` set, `null` otherwise.
- **API**: mock `getSubmissionFull` and assert the route returns `publishedSkillName` in the JSON body.
- **Page (vitest + RTL or shallow)**: render the published-state branch with mocked fetch; assert the anchor's `href` is the canonical 3-segment URL when `publishedSkillName` is set.
- **Legacy redirect**: mock `db.skill.findMany`; assert 404 for 0 matches, 301 for 1 match (with correct `Location`), 404 + `X-Legacy-Ambiguous` for 2+ matches.

## Technical Challenges

### Challenge 1: `getSubmissionFull` may go through KV/cached path, not direct Prisma

**Solution**: read the function and decide whether to (a) augment the cached return shape (preferred — single source of truth) or (b) do a separate `db.skill.findUnique` after the cached fetch.
**Risk**: changing the cached shape means callers reading `getSubmissionFull` from disk-cache may see `undefined` until the cache rolls. Mitigated by treating `undefined` and `null` identically in the consuming page.

### Challenge 2: Submit page is a server component reading from the API route

**Solution**: confirmed — the page consumes the JSON shape from the API. Just adding the field to the API response and reading `data.publishedSkillName` in the JSX is sufficient.
**Risk**: none — additive field.

### Challenge 3: `findMany({take:2})` performance

**Solution**: same indexed scan as `findFirst`, just bounded at 2 rows. No measurable cost.
**Risk**: none.

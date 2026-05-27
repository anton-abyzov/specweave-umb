# Tasks — Increment 0854: Source-Link Auto-Deprecation Pipeline + Backfill

All file paths below are relative to `repositories/anton-abyzov/vskill-platform/` unless noted.

## T-001: Write failing test for check-source ctx.waitUntil
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [ ] pending
**Test Plan**: Given the route handler runs with `getCloudflareContext` returning a stubbed `ctx.waitUntil`, When `check-source?url=<404-url>&skill=<name>` is called, Then waitUntil receives the deprecation promise, and after awaiting it `prisma.skill.updateMany` was called with `data: { isDeprecated: true }`.
**File**: `src/app/api/v1/skills/__tests__/check-source.waitUntil.test.ts` (NEW)

## T-002: Implement ctx.waitUntil in check-source route
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [ ] pending
**Test Plan**: Given the test from T-001, When the route is updated to use `getCloudflareContext({ async: true }).ctx.waitUntil`, Then the test passes.
**File**: `src/app/api/v1/skills/check-source/route.ts`

## T-003: Refactor DeprecationBanner to accept sourceState prop
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [ ] pending
**Test Plan**: Given DeprecationBanner receives `sourceState="offline"` as a prop (no internal fetch), Then it renders the DEPRECATED banner.
**File**: `src/app/skills/[owner]/[repo]/[skill]/DeprecationBanner.tsx`

## T-004: Create SourceLinkAndBanner client wrapper
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [ ] pending
**Test Plan**: Given a mock fetch returning `{ exists: false }`, When `<SourceLinkAndBanner>` is rendered, Then the link gets line-through style + warning glyph + correct title/aria-label, and the banner shows DEPRECATED state.
**File**: `src/app/skills/[owner]/[repo]/[skill]/SourceLinkAndBanner.tsx` (NEW)

## T-005: Integrate SourceLinkAndBanner into skill detail page
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [ ] pending
**Test Plan**: Given the skill detail page renders for a non-deprecated skill with `repoUrl + skillPath`, Then `<SourceLinkAndBanner>` mounts and the banner runs the live check.
**File**: `src/app/skills/[owner]/[repo]/[skill]/page.tsx`

## T-006: Component test for SourceLinkAndBanner (offline + online + checking)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [ ] pending
**Test Plan**: Given check-source returns offline, Then link has broken visual + banner shows DEPRECATED. Given online, Then link is plain + banner shows green pill. Given checking, Then both show pending state.
**File**: `src/app/skills/[owner]/[repo]/[skill]/__tests__/SourceLinkAndBanner.test.tsx` (NEW)

## T-007: Implement runStaleSourceSweep cron function
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-04 | **Status**: [ ] pending
**Test Plan**: Given a batch of 3 fake skills (404, 200, 429), When the sweep runs, Then only the 404 skill is deprecated, the 200 is untouched, the 429 is not deprecated. KV `updateSearchShard` is called once with "remove" for the 404.
**File**: `src/lib/cron/stale-source-sweep.ts` (NEW)

## T-008: Unit test for runStaleSourceSweep
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02 | **Status**: [ ] pending
**File**: `src/lib/cron/__tests__/stale-source-sweep.test.ts` (NEW)

## T-009: Wire stale-source-sweep into cohort-dispatch
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03 | **Status**: [ ] pending
**File**: `src/lib/cron/cohort-dispatch.ts`

## T-010: Invoke runStaleSourceSweep from build-worker-entry scheduled handler
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03 | **Status**: [ ] pending
**File**: `scripts/build-worker-entry.ts`

## T-011: Implement backfill-stale-source script
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [ ] pending
**Test Plan**: Manual run `--dry-run` → kie-ai appears in report. Real run → kie-ai's `isDeprecated` flips to true in DB. Script handles `--limit` and `--max-age-days`.
**File**: `scripts/backfill-stale-source.ts` (NEW)

## T-012: Run vitest + ensure all tests green
**Status**: [ ] pending
**Cmd**: `cd repositories/anton-abyzov/vskill-platform && npx vitest run`

## T-013: Run backfill --dry-run against prod
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [ ] pending
**Cmd**: `npx tsx scripts/backfill-stale-source.ts --dry-run`
**Verify**: `stephengpope/thepopebot/kie-ai` appears in deprecated list.

## T-014: Run backfill live against prod
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [ ] pending
**Cmd**: `npx tsx scripts/backfill-stale-source.ts`
**Verify**: `curl https://verified-skill.com/api/v1/skills/stephengpope/thepopebot/kie-ai | jq .skill.isDeprecated` → `true`.

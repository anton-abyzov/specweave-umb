---
increment: 0854-source-link-deprecation-pipeline
title: "Source-link auto-deprecation pipeline + stale-skill backfill"
type: bug
priority: P1
status: planned
created: 2026-05-27
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Source-link auto-deprecation pipeline + stale-skill backfill

## Overview

`https://verified-skill.com/skills/stephengpope/thepopebot/kie-ai` renders a clickable source link that 404s on GitHub. The upstream file was removed 2026-03-31; our DB still treats the skill as active. Three converging code bugs prevent the existing auto-deprecation logic from ever firing, and the hourly enrichment cron has a 60+ day backlog. This increment fixes the three bugs, ships a one-shot backfill, and adds a dedicated stale-source-sweep cron so the backlog drains in hours not months.

## User Stories

### US-001: Stale source visually marked + auto-deprecated on view (P1)
**Project**: vskill-platform

**As a** verified-skill.com visitor
**I want** broken source links to be visually flagged (not clickable into a silent 404)
**So that** I know the skill is no longer installable before I waste a click

**Acceptance Criteria**:
- [ ] **AC-US1-01**: Visiting `/skills/{owner}/{repo}/{skill}` whose `skillPath` 404s upstream causes `Skill.isDeprecated=true` in DB within 10 seconds of page load.
- [ ] **AC-US1-02**: When the client check-source call reports `offline`, the rendered source-path link visually indicates broken state (line-through + warning glyph + descriptive `title`/`aria-label`). The link stays clickable so power users can confirm the upstream 404 themselves.
- [ ] **AC-US1-03**: The `<DeprecationBanner>` mounts on every skill detail page that has a `repoUrl` + `skillPath` (not only when `isDeprecated` is already true) so the live source check runs.

---

### US-002: Worker fire-and-forget DB writes survive isolate termination (P1)
**Project**: vskill-platform

**As** the platform
**I want** `/api/v1/skills/check-source` DB side-effects (deprecate / un-deprecate) to use `ctx.waitUntil`
**So that** the writes actually land on Cloudflare Workers (bare `Promise.catch()` gets killed when the response returns)

**Acceptance Criteria**:
- [ ] **AC-US2-01**: `deprecateStaleSkill` and `undeprecateSkill` are invoked via `getCloudflareContext({ async: true }).ctx.waitUntil(...)` with a typeof-function guard for local dev. Pattern matches `src/app/api/v1/auth/login/route.ts:91-105`.
- [ ] **AC-US2-02**: Unit test mocks `getCloudflareContext`, captures the waitUntil promise, awaits it, and asserts `prisma.skill.updateMany` was called with `data: { isDeprecated: true }`.

---

### US-003: One-shot backfill clears existing stale-source backlog (P1)
**Project**: vskill-platform

**As** an operator
**I want** a CLI script that probes every "long-unrefreshed" skill and deprecates dead ones in one pass
**So that** the in-flight backlog (incl. `stephengpope/thepopebot/kie-ai`) is cleared immediately, not in 60+ days

**Acceptance Criteria**:
- [ ] **AC-US3-01**: `npx tsx scripts/backfill-stale-source.ts --dry-run` prints the list of skills it would deprecate and includes `stephengpope/thepopebot/kie-ai` in the production data.
- [ ] **AC-US3-02**: Without `--dry-run` the script deprecates the matched skills (sets `isDeprecated=true`) and invalidates the relevant KV search-index shards via the Cloudflare REST API.
- [ ] **AC-US3-03**: Script supports `--limit N` and `--max-age-days N` flags; uses `p-limit` concurrency control (default 10) to avoid hammering raw.githubusercontent.com.

---

### US-004: Dedicated stale-source-sweep cron drains backlog hourly (P2)
**Project**: vskill-platform

**As** the platform
**I want** a fast lightweight cron task that probes only `skillPath` HEAD (no metric fetches)
**So that** the existing enrichment cron's 60+ day refresh cycle stops being the only mechanism that catches stale sources

**Acceptance Criteria**:
- [ ] **AC-US4-01**: `runStaleSourceSweep` exists at `src/lib/cron/stale-source-sweep.ts` and processes >=500 skills/run by default.
- [ ] **AC-US4-02**: Cron triggers only deprecate on definitive 404 from raw.githubusercontent.com (not 429/5xx/3xx); shares the circuit-breaker pattern from `runEnrichmentBatch`.
- [ ] **AC-US4-03**: Cron is wired into `scripts/build-worker-entry.ts` and the cohort dispatch, runs at a gated minute on the existing schedule so no new wrangler cron trigger is needed.
- [ ] **AC-US4-04**: KV search-shard cleanup uses the existing `updateSearchShard()` helper for deprecated skills.

## Functional Requirements

### FR-001: Client component contract change
`<DeprecationBanner>` becomes a sub-component of a new `<SourceLinkAndBanner>` client wrapper. The wrapper owns the single `check-source` fetch and shares state with both the source link rendering and the banner so we don't double-fetch per page view.

### FR-002: Backward-compatible 24h guard
`deprecateStaleSkill` already has a 24h-since-`updatedAt` guard that prevents flapping during fresh publishes. The backfill script's queries use `metricsRefreshedAt < now() - 30d` (or null) so the guard is effectively respected.

## Success Criteria

- Live verification: `curl https://verified-skill.com/api/v1/skills/stephengpope/thepopebot/kie-ai | jq .skill.isDeprecated` returns `true` after backfill + deploy.
- Workers logs show `[stale-source-sweep] processed N skills, deprecated M` within 1 hour of deploy.
- E2E test on stale-source fixture page passes: link has broken styling, banner shows DEPRECATED, DB reflects `isDeprecated:true`.

## Out of Scope

- Display URL `/blob/HEAD/...` re-engineering (skill.sourceBranch is not consumed for display links). Future cleanup.
- Resurrecting "moved" skills (path changed upstream). We deprecate; re-discovery is out of scope.
- Admin tooling to manually un-deprecate a single skill (existing `undeprecateSkill` flow already handles auto-recovery on fresh submissions).

## Dependencies

- `@opennextjs/cloudflare` - already a dependency (used by auth routes for `getCloudflareContext`).
- `p-limit` - already a dependency (used by enrichment cron).
- Hetzner Postgres direct connection string in env (`DATABASE_URL`) for the backfill script.
- Cloudflare REST API env (`CF_API_TOKEN`, `CF_ACCOUNT_ID`, `CF_KV_NAMESPACE_ID` for SEARCH_INDEX_KV) for the script's KV cleanup.

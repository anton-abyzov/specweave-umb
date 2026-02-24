---
increment: 0366-orphan-cleanup-install-tracking
title: "Orphan cleanup on re-submission + install tracking phone-home"
type: feature
priority: P1
status: planned
created: 2026-02-24
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Orphan cleanup on re-submission + install tracking phone-home

## Overview

Two related improvements to the vskill platform:

1. **Orphan cleanup**: When a skill is re-submitted (new submission for same repo+skillName), automatically deprecate the previous Skill record using the existing `isDeprecated` field. This runs in the same transaction as the batch submission flow, requiring only one `findMany` + one `updateMany` query.

2. **Install tracking phone-home**: The vskill CLI sends a fire-and-forget POST to the platform after each successful `vskill add`, incrementing `Skill.vskillInstalls`. Enabled by default, opt-out via `VSKILL_NO_TELEMETRY=1` env var. The CLI uses a 2-second timeout and swallows all errors silently.

## User Stories

### US-001: Orphan Skill Cleanup on Re-submission (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** stale Skill records to be automatically deprecated when a skill is re-submitted
**So that** the search index and registry only surface the latest version

**Acceptance Criteria**:
- [ ] **AC-US1-01**: When a submission is created for a repo+skillName that already has a published Skill record, the old Skill record gets `isDeprecated = true` within the same transaction
- [ ] **AC-US1-02**: Orphan cleanup uses one `findMany` + one `updateMany` Prisma query (no N+1)
- [ ] **AC-US1-03**: Cleanup runs inside the existing batch submission flow in `POST /api/v1/submissions` -- no separate cron job
- [ ] **AC-US1-04**: Skills that are NOT being re-submitted are never touched by the cleanup logic
- [ ] **AC-US1-05**: The cleanup is idempotent -- running it multiple times for the same submission produces the same result

---

### US-002: Install Tracking Phone-Home from CLI (P1)
**Project**: vskill (CLI) + vskill-platform

**As a** platform operator
**I want** the vskill CLI to report successful installs to the platform
**So that** `vskillInstalls` reflects real usage and feeds into trending scores

**Acceptance Criteria**:
- [ ] **AC-US2-01**: After a successful `vskill add <skill>`, the CLI sends `POST /api/v1/skills/:name/installs` to the platform
- [ ] **AC-US2-02**: The phone-home uses the same `BASE_URL` ("https://verified-skill.com") as existing API calls
- [ ] **AC-US2-03**: The phone-home has a 2-second timeout and silently swallows ALL errors (network, HTTP, parse)
- [ ] **AC-US2-04**: The phone-home never blocks or delays the CLI command -- it runs as fire-and-forget
- [ ] **AC-US2-05**: Setting `VSKILL_NO_TELEMETRY=1` disables the phone-home entirely
- [ ] **AC-US2-06**: The platform endpoint increments `Skill.vskillInstalls` by 1 for the named skill
- [ ] **AC-US2-07**: The platform endpoint is rate-limited at 60 requests/hour per IP using existing `checkRateLimit()` from `src/lib/rate-limit.ts` with `RATE_LIMIT_KV`
- [ ] **AC-US2-08**: The platform endpoint returns 404 if the skill does not exist
- [ ] **AC-US2-09**: No deduplication of installs -- simple counter increment

## Functional Requirements

### FR-001: Orphan Cleanup in Submission Flow
When `POST /api/v1/submissions` processes a new submission (single or batch), before creating the submission record, query for existing Skill records matching the same `repoUrl` + `skillName` (via slug) and set `isDeprecated = true` on all matches. This uses the existing `isDeprecated` boolean field already respected by search and enrichment.

### FR-002: Install Tracking Endpoint
New route `POST /api/v1/skills/:name/installs` that:
- Validates the skill exists (404 if not)
- Rate-limits by IP (60/hour)
- Increments `Skill.vskillInstalls` atomically via Prisma `update({ increment: 1 })`
- Returns `{ ok: true }` on success

### FR-003: CLI Phone-Home
After a successful skill installation in `src/commands/add.ts`, fire a non-blocking POST to the install tracking endpoint. Use `AbortController` with 2-second timeout. Wrap in try/catch that swallows everything. Check `VSKILL_NO_TELEMETRY` env var before sending.

## Success Criteria

- Orphan Skill records are cleaned up within the same request as re-submission (no background job, no cron)
- `vskillInstalls` counter reflects actual CLI installs within eventual consistency window
- CLI `vskill add` latency is unchanged (phone-home is non-blocking)
- No new Prisma migrations required (uses existing `isDeprecated` field and `vskillInstalls` column)

## Out of Scope

- Install deduplication (same user installing same skill twice counts as 2)
- Admin dashboard for viewing install analytics
- Gaming prevention beyond rate limiting
- Cron-based orphan cleanup
- New database columns or migrations

## Dependencies

- Existing `Skill.isDeprecated` field (already in schema)
- Existing `Skill.vskillInstalls` field (already in schema)
- Existing `checkRateLimit()` in `src/lib/rate-limit.ts`
- Existing `RATE_LIMIT_KV` Cloudflare KV namespace
- Existing `BASE_URL` in vskill CLI (`src/api/client.ts`)

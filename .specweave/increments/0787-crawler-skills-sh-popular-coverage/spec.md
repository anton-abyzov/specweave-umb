---
increment: 0787-crawler-skills-sh-popular-coverage
title: Fix skills.sh crawler popular-skills coverage
type: feature
priority: P1
status: completed
---

# 0787: Fix skills.sh crawler popular-skills coverage

## Problem

A 2026-04-27 audit of verified-skill.com showed only 36/50 of skills.sh's all-time top-50 popular skills are indexed — including the #1 (`vercel-labs/skills/find-skills`, 1.2M installs). Two confirmed bugs in `repositories/anton-abyzov/vskill-platform/crawl-worker/sources/skills-sh.js`:

1. **Off-by-one** at line 40: `configStartPage = 1` but skills.sh API is zero-indexed. Page 0 (top 200, 33K–1.2M installs) has never been fetched. The 36/50 hits are accidental coverage from other crawlers (vendor-org-discovery, github-events).
2. **Rigid path mapping** at line 101: `skills/${skillName}/SKILL.md` assumes `skillId == on-disk dir name`. Breaks for `vercel-labs/agent-skills` (`vercel-react-best-practices` → `react-best-practices`), `remotion-dev/skills` (`remotion-best-practices` → `remotion`), and a few `microsoft/azure-skills` entries.

## Goal

Ensure crawlers reliably submit the most popular skills.sh skills to the platform queue with high (≥96%) coverage of the top 50.

## User Stories

### US-001: Page-0 off-by-one fix
**Project**: vskill-platform

**As a** platform operator
**I want** the skills.sh crawler to fetch page 0 (the most popular skills) on every run
**So that** the top-200 most-installed skills are submitted to our queue

**Acceptance Criteria**:
- [x] **AC-US1-01**: Default `configStartPage = 0` in `crawl-worker/sources/skills-sh.js` so the most-popular page is always crawled
- [x] **AC-US1-02**: A run with no checkpoint fetches page 0 first and submits all skills it returns (~200)
- [x] **AC-US1-03**: An existing checkpoint with `lastPage >= 1` triggers a one-shot page-0 backfill, then writes `backfilledPage0: true` so the next run skips it

### US-002: Path-resolution candidate fallback
**Project**: vskill-platform

**As a** platform operator
**I want** the bulk-submission endpoint to try multiple candidate paths when verifying a SKILL.md exists
**So that** skills whose skills.sh `skillId` differs from the on-disk dir name (e.g. `vercel-react-best-practices` vs `react-best-practices`) still land in the queue

**Acceptance Criteria**:
- [x] **AC-US2-01**: Crawler emits `skillPathCandidates: string[]` from a `candidateSkillPaths(skillId)` helper that handles vendor-prefix stripping
- [x] **AC-US2-02**: `src/app/api/v1/submissions/bulk/route.ts` Phase-2.5 verification iterates candidates via `checkSkillMdExists`, accepts the first 200, persists the resolved path on the submission row
- [x] **AC-US2-03**: Behavior is monotonic — when `skillPathCandidates` is absent, falls back to today's claimed-path → root-SKILL.md logic; when present, only adds attempts (never removes)

### US-003: Backfill the 14 currently-missing top-50 popular skills
**Project**: vskill-platform

**As a** platform user
**I want** the missing top-50 popular skills (find-skills, react-best-practices, remotion, soultrace, etc.) indexed
**So that** the marketplace's "most popular" view reflects skills.sh's real ranking

**Acceptance Criteria**:
- [x] **AC-US3-01**: Backfill is self-healing — first scheduled run after deploy automatically submits page 0 because every existing checkpoint has `backfilledPage0` undefined
- [x] **AC-US3-02**: Submission flow is idempotent — already-published skills are deduped by the existing bulk endpoint logic; backfill log line `[skills-sh] one-shot page-0 backfill` is added so VM logs prove the path ran
- [x] **AC-US3-03**: Coverage check (Python script from the audit) shows ≥48/50 of skills.sh top 50 indexed within 4 hours of deploy

### US-004: Coverage telemetry
**Project**: vskill-platform

**As a** platform operator
**I want** a `/coverage` endpoint on the crawl-worker
**So that** I can detect coverage regressions without re-running the audit script manually

**Acceptance Criteria**:
- [x] **AC-US4-01**: `GET /coverage` returns `{ skillsShTotal, lastSkillsShRunAt, lastSampledAt }` from existing scheduler metrics — no new GitHub or skills.sh API calls
- [x] **AC-US4-02**: `crawl-worker/README.md` documents the endpoint and what the metric means

## Out of Scope

- `GET /api/v1/submissions?repoUrl=…&q=…` filter ignored — separate spawned task.
- `GET /api/v1/queue/health` reports terminal-state submissions as `oldestActive` — separate spawned task.

## Non-Functional Requirements

- **Quota**: Zero new GitHub API calls. Reuses existing unauthenticated `raw.githubusercontent.com` HEAD primitive in the bulk route.
- **Backwards compatibility**: Crawler change is monotonic — clients without `skillPathCandidates` see no behavior change.
- **Test coverage**: ≥1 unit test per AC. Crawler tests stay on `node:test` (existing); bulk-route test uses vitest (existing).

---
increment: 0254-repo-health-check
title: "Repo Health Check for Skill Detail Pages"
type: feature
priority: P1
status: planned
created: 2026-02-20
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Feature: Repo Health Check for Skill Detail Pages

## Overview

When viewing a skill on verified-skill.com, users currently see a "Repository" link but have no indication whether the source repo is still accessible, has gone private, or was deleted. This increment adds a lazy, on-demand health check that pings the GitHub API, caches the result in KV with a 24h TTL, and displays an ONLINE/OFFLINE/STALE status tag next to the Repository link on the skill detail page.

## User Stories

### US-001: Repository Health Status Display (P1)
**Project**: vskill-platform

**As a** skill consumer browsing the registry
**I want** to see whether a skill's GitHub repository is still accessible
**So that** I can avoid installing skills whose source code is unreachable or abandoned

**Acceptance Criteria**:
- [x] **AC-US1-01**: The skill detail page shows a status tag (ONLINE, OFFLINE, or STALE) next to the Repository link when `repoUrl` is present
- [x] **AC-US1-02**: The status tag loads asynchronously via a client component so it does not block server-side rendering
- [x] **AC-US1-03**: ONLINE is shown when the GitHub API returns HTTP 200 for the repo
- [x] **AC-US1-04**: OFFLINE is shown when the GitHub API returns HTTP 404 or a network error
- [x] **AC-US1-05**: STALE is shown when the last commit was more than 365 days ago (repo accessible but inactive)
- [x] **AC-US1-06**: A loading skeleton is shown while the health check is in flight
- [x] **AC-US1-07**: If the skill has no `repoUrl`, no health tag is rendered

---

### US-002: KV-Cached Health Results (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** repo health results cached in Cloudflare KV with a 24-hour TTL
**So that** we avoid excessive GitHub API calls and stay within rate limits

**Acceptance Criteria**:
- [x] **AC-US2-01**: Health check results are stored in a dedicated `REPO_HEALTH_KV` namespace with key pattern `repo-health:{skillName}`
- [x] **AC-US2-02**: Cached results are returned immediately without hitting the GitHub API when the cache entry exists and is not expired
- [x] **AC-US2-03**: KV entries use a 24-hour `expirationTtl` so stale entries are automatically purged
- [x] **AC-US2-04**: The cached result includes: status (ONLINE/OFFLINE/STALE), checkedAt timestamp, and lastCommitAt (if available)

---

### US-003: Repo Health API Endpoint (P1)
**Project**: vskill-platform

**As a** frontend developer
**I want** a `GET /api/v1/skills/[name]/repo-health` endpoint
**So that** the client component can fetch health status on demand

**Acceptance Criteria**:
- [x] **AC-US3-01**: The endpoint returns JSON with `{ status, checkedAt, lastCommitAt }` and appropriate HTTP status codes
- [x] **AC-US3-02**: Returns 404 if the skill does not exist in the registry
- [x] **AC-US3-03**: Returns cached result from KV when available; otherwise performs a fresh GitHub API check
- [x] **AC-US3-04**: Sets `Cache-Control: public, max-age=3600` header on successful responses
- [x] **AC-US3-05**: Gracefully handles GitHub API errors (rate limiting, timeouts) by returning OFFLINE status rather than 500

## Functional Requirements

### FR-001: GitHub Repository Check
The health check calls the GitHub API `GET /repos/{owner}/{repo}` to determine:
1. Whether the repo is accessible (HTTP 200 = ONLINE, 404 = OFFLINE)
2. When the last commit was pushed (`pushed_at` field). If > 365 days ago, status = STALE.

### FR-002: KV Storage Schema
```
Key:    repo-health:{skillName}
Value:  { "status": "ONLINE|OFFLINE|STALE", "checkedAt": "ISO", "lastCommitAt": "ISO|null" }
TTL:    86400 seconds (24 hours)
```

### FR-003: Client Component
A `"use client"` component `RepoHealthBadge` that:
- Accepts `skillName` and `repoUrl` as props
- Calls `/api/v1/skills/{name}/repo-health` on mount via `useEffect` + `fetch`
- Renders a colored status pill matching the existing design system (MONO font, pill style)

## Success Criteria

- Health check endpoint responds in < 200ms for cached results
- Zero impact on initial page load time (async client component)
- GitHub API calls reduced to at most 1 per skill per 24 hours

## Out of Scope

- Periodic background refresh (cron-based health checks)
- Health checks for non-GitHub repositories
- Admin dashboard for health check analytics
- Webhook-based real-time repo status updates

## Dependencies

- Cloudflare KV (new `REPO_HEALTH_KV` namespace)
- GitHub API (public, unauthenticated for public repos; optional `GITHUB_TOKEN` for higher rate limits)
- Existing `getSkillByName()` data layer function
- Existing skill detail page (`src/app/skills/[name]/page.tsx`)

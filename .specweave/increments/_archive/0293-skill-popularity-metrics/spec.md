---
increment: 0293-skill-popularity-metrics
title: "Populate Skill Popularity Metrics from APIs"
type: feature
priority: P1
status: completed
created: 2026-02-21
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Feature: Populate Skill Popularity Metrics from APIs

## Overview

Currently, skill popularity metrics (githubStars, githubForks, npmDownloads) in the vskill-platform are hardcoded in seed data. Published skills from KV always show 0 for these fields, and the skill detail page renders misleading "0" stat cards. This increment adds a server-side popularity fetcher that pulls real metrics from the GitHub REST API and npm registry API, then updates the in-memory and KV-stored skill data. The UI is also updated to hide zero-value metrics instead of displaying misleading zeros.

## User Stories

### US-001: Fetch Popularity Metrics from External APIs (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** the system to fetch real githubStars, githubForks, and npmDownloads from GitHub and npm APIs
**So that** skill popularity metrics reflect actual usage data instead of hardcoded zeros

**Acceptance Criteria**:
- [x] **AC-US1-01**: A `fetchGitHubMetrics(repoUrl)` function extracts owner/repo from a GitHub URL and calls `GET /repos/{owner}/{repo}` to return `{ stars, forks, lastCommitAt }`
- [x] **AC-US1-02**: A `fetchNpmDownloads(packageName)` function calls the npm registry downloads API (`GET /downloads/point/last-month/{package}`) to return the monthly download count
- [x] **AC-US1-03**: Both functions return null/zero gracefully when the API is unreachable, returns 404, or rate-limits (never throw)
- [x] **AC-US1-04**: GitHub API calls include an `Accept: application/vnd.github.v3+json` header; if `GITHUB_TOKEN` env var is set, include `Authorization: Bearer {token}` for higher rate limits
- [x] **AC-US1-05**: Results are cached in-memory with a configurable TTL (default 1 hour) to avoid hammering external APIs

---

### US-002: Add npmPackage Field to SkillData (P1)
**Project**: vskill-platform

**As a** platform developer
**I want** the SkillData type and Prisma schema to include an optional `npmPackage` field
**So that** the system knows which npm package to query for download metrics

**Acceptance Criteria**:
- [x] **AC-US2-01**: `SkillData` interface in `types.ts` includes `npmPackage?: string`
- [x] **AC-US2-02**: The Prisma `Skill` model includes `npmPackage String?`
- [x] **AC-US2-03**: Seed data is updated to include `npmPackage` for skills that have a corresponding npm package (at least 5 skills with realistic npm package names)

---

### US-003: Populate Metrics into Skill Data Layer (P1)
**Project**: vskill-platform

**As a** platform developer
**I want** `getSkillByName` and `getSkills` to enrich skill records with live popularity data
**So that** all consumers of the data layer see real metrics without each caller fetching separately

**Acceptance Criteria**:
- [x] **AC-US3-01**: `getSkillByName` calls the fetcher to enrich the returned skill with live GitHub and npm metrics when available
- [x] **AC-US3-02**: `getSkills` enriches published skills from KV with live metrics (using cached results from the in-memory TTL cache)
- [x] **AC-US3-03**: If the fetcher returns null (API down, rate limited), the existing values from seed data or KV are preserved (no regression to zero)
- [x] **AC-US3-04**: The enrichment is behind a feature flag `ENABLE_LIVE_METRICS` env var (default: `false`) so it can be disabled without code changes

---

### US-004: Hide Zero Metrics on UI (P1)
**Project**: vskill-platform

**As a** visitor browsing the skill registry
**I want** zero-value metrics to be hidden from the UI
**So that** I don't see misleading "0 stars" or "0 forks" on skills that simply haven't had their metrics fetched yet

**Acceptance Criteria**:
- [x] **AC-US4-01**: Skill detail page (`/skills/[name]`) hides the Stars stat card when `githubStars === 0`
- [x] **AC-US4-02**: Skill detail page hides the Forks stat card when `githubForks === 0`
- [x] **AC-US4-03**: Skills listing page (`/skills`) already conditionally renders stars/forks/npm -- verify and ensure consistency
- [x] **AC-US4-04**: Homepage trending rows continue to show stars (already non-zero for seed data)
- [x] **AC-US4-05**: Homepage dashboard metric cards (total GitHub Stars, NPM Downloads) exclude skills with zero values from aggregation to avoid inflating totals with meaningless data

## Functional Requirements

### FR-001: GitHub Metrics Fetcher
- Input: GitHub repository URL (e.g., `https://github.com/owner/repo`)
- Parses owner/repo from URL, handles both `github.com` and `www.github.com`
- Calls GitHub REST API v3 `GET /repos/{owner}/{repo}`
- Extracts: `stargazers_count`, `forks_count`, `pushed_at`
- Returns: `{ stars: number, forks: number, lastCommitAt: string | null }`
- Error handling: returns `null` on any failure (network, 404, 403, rate limit)

### FR-002: npm Downloads Fetcher
- Input: npm package name (e.g., `@anthropic/skills`)
- Calls npm registry API `GET https://api.npmjs.org/downloads/point/last-month/{package}`
- Extracts: `downloads` count
- Returns: `number` (0 on failure)
- Error handling: returns `0` on any failure

### FR-003: TTL Cache
- Simple in-memory Map with TTL expiry (same pattern as existing `_publishedCache`)
- Key: `github:{owner}/{repo}` or `npm:{packageName}`
- Default TTL: 3600 seconds (1 hour)
- Configurable via `METRICS_CACHE_TTL_SECONDS` env var

## Success Criteria

- All published skills with valid GitHub URLs show real star/fork counts within 1 cache cycle
- Skills with npm packages show real download counts
- Zero-value metrics are hidden from all UI surfaces
- No API errors bubble up to the user-facing pages
- Tests pass with >80% coverage on new code

---

### US-005: Find Command Install Hint (P1)
**Project**: vskill CLI

**As a** developer discovering skills with `vskill find`
**I want** the search results to show how to install a skill
**So that** I know the next step without consulting documentation

**Acceptance Criteria**:
- [x] **AC-US5-01**: In non-interactive mode (no TTY or piped output), a hint line is appended after results: `To install: npx skills add <name>`
- [x] **AC-US5-02**: In interactive TTY mode, a key-bindings footer is shown: `↑↓ navigate  i install  q quit`
- [x] **AC-US5-03**: Pressing `i` on a selected result triggers the install flow for that skill (interactive mode only)
- [x] **AC-US5-04**: The hint is suppressed when `--no-hint` flag or `--json` output flag is used

---

### US-006: Smart URL Resolver for `vskill install` / `skills add` (P1)
**Project**: vskill CLI

**As a** developer installing a skill from a marketplace browse URL
**I want** `vskill install https://skills.sh/owner/toolkit/skill` to resolve correctly
**So that** I can copy-paste URLs from the browser without getting confusing errors

**Acceptance Criteria**:
- [x] **AC-US6-01**: URLs matching `https://skills.sh/{owner}/{toolkit}/{skill}` are parsed and resolved to the correct skill without attempting `/.well-known/skills/index.json`
- [x] **AC-US6-02**: Incomplete skills.sh paths (e.g. missing skill segment) show a descriptive error: `Incomplete skills.sh URL — expected /owner/toolkit/skill`
- [x] **AC-US6-03**: Non-skills.sh URLs fall through to the existing `/.well-known/skills/index.json` probe unchanged
- [x] **AC-US6-04**: The generic error message when `/.well-known/` probe fails no longer mentions `skills/index.json` internals; instead shows: `Could not resolve skill at this URL`
- [x] **AC-US6-05**: A "Resolving..." progress line is printed before network calls when input is a URL

---

### US-007: Skills.sh Install Compatibility (P1)
**Project**: vskill CLI

**As a** developer using both vskill and skills.sh CLIs
**I want** skills installed by either tool to be discoverable and manageable by the other
**So that** I don't have duplicate or invisible skills across tools

**Acceptance Criteria**:
- [x] **AC-US7-01**: Research task produces a compatibility gap analysis with actionable recommendations and a draft implementation plan
- [x] **AC-US7-02**: Skills installed by `npx skills` in `.agents/skills/{name}/` are visible to `vskill list`
- [x] **AC-US7-03**: Skills installed by `vskill install` are visible to `npx skills list`
- [x] **AC-US7-04**: Agent detection covers at least the same agents as skills.sh (50+ agents)
- [x] **AC-US7-05**: Claude Code agent uses `.claude/skills/` path (matching skills.sh), not `.claude/commands/`

## Out of Scope

- Cron/scheduled background job for metrics refresh (future increment)
- Storing fetched metrics back to the database/KV (future increment)
- PyPI, crates.io, or other package registry support
- Webhook-based real-time updates from GitHub

## Dependencies

- GitHub REST API v3 (public, rate-limited to 60/hr unauthenticated, 5000/hr with token)
- npm registry downloads API (public, no auth required)
- Existing `SkillData` type and data layer in `src/lib/data.ts`

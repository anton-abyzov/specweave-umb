---
increment: 0389-vendor-org-skill-auto-discovery
title: "Vendor org skill auto-discovery and import"
type: feature
priority: P1
status: planned
created: 2026-02-28
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Vendor org skill auto-discovery and import

## Overview

Replace the manual `import-vendor-skills.ts` script with an automated crawl source that periodically discovers and submits SKILL.md files from vendor organization repositories (anthropics, openai, google-gemini, google). The new `vendor-org-discovery` source enumerates all public repos for each vendor org via the GitHub REST API, scans each repo's file tree for SKILL.md files, and submits discoveries through the existing `/api/v1/submissions/bulk` endpoint. The submission pipeline's vendor fast-path (`isVendorRepo` -> `VENDOR_APPROVED`) handles the rest.

**Key design decisions:**
- Two-phase GitHub API approach: `GET /orgs/{org}/repos` (paginated) then Trees API per-repo
- Reuse existing `DiscoveryRecord`-based dedup from `discovery-dedup.ts`
- Submit through `/api/v1/submissions/bulk` (no direct Prisma writes from crawl worker)
- Runs on VM-2 alongside `github-graphql-check` and `sourcegraph`
- Both a scheduled crawl source (every 6h) and a dedicated admin endpoint for on-demand triggers

## User Stories

### US-001: Automated vendor org repo enumeration (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** the system to automatically enumerate all public repositories from vendor organizations (anthropics, openai, google-gemini, google) every 6 hours
**So that** new vendor repos containing skills are discovered without manual intervention

**Acceptance Criteria**:
- [x] **AC-US1-01**: A new crawl source module `vendor-org-discovery.js` exists at `crawl-worker/sources/` that iterates over all VENDOR_ORGS
- [x] **AC-US1-02**: For each vendor org, the source calls `GET /orgs/{org}/repos` with pagination (`per_page=100`) to enumerate all public repos
- [x] **AC-US1-03**: Fork repos (`fork: true`) and zero-star repos (`stargazers_count: 0`) are skipped during enumeration
- [x] **AC-US1-04**: For each qualifying repo, the source calls the Trees API (`GET /repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1`) to find SKILL.md files
- [x] **AC-US1-05**: Token rotation via the existing `GITHUB_TOKENS` env var is used for all GitHub API calls, with adaptive delay between requests
- [x] **AC-US1-06**: Discovered skills are submitted via `InlineSubmitter` to `POST /api/v1/submissions/bulk` — no direct Prisma writes from the crawl worker

---

### US-002: Deduplication and force-rescan (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** vendor org discovery to deduplicate against previously discovered skills and allow forced re-scanning
**So that** only genuinely new skills create submissions, but I can force a full re-scan when needed

**Acceptance Criteria**:
- [x] **AC-US2-01**: Before submitting, each discovered `repoFullName + skillPath` is checked against the `DiscoveryRecord` table via `hasBeenDiscovered()` from `discovery-dedup.ts`
- [x] **AC-US2-02**: Successfully submitted discoveries are marked via `markDiscovered()` with source `"vendor-org-discovery"`
- [x] **AC-US2-03**: The admin endpoint accepts a `force: true` parameter that bypasses dedup checks, causing all discovered skills to be re-submitted regardless of existing `DiscoveryRecord` entries
- [x] **AC-US2-04**: The `DiscoveryRunLog` table is updated after each run via `logDiscoveryRun()` with source breakdown and trigger info

---

### US-003: Scheduled execution on VM-2 (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** the vendor-org-discovery source to run on VM-2 on a 6-hour schedule
**So that** vendor skills are continuously discovered without overloading GitHub API rate limits

**Acceptance Criteria**:
- [x] **AC-US3-01**: `vendor-org-discovery` is added to VM-2's `ASSIGNED_SOURCES` env var (alongside `github-graphql-check`, `sourcegraph`, `submission-scanner`)
- [x] **AC-US3-02**: The scheduler config includes `vendor-org-discovery` with a 6-hour (21600000ms) cooldown and a 30-minute timeout
- [x] **AC-US3-03**: The source module exports a default function matching the scheduler's source module contract (`export default async function(config)`)
- [x] **AC-US3-04**: Rate limiting respects GitHub REST API limits: adaptive delay based on `x-ratelimit-remaining` headers, 60s backoff on 403/429

---

### US-004: Admin on-demand discovery endpoint (P2)
**Project**: vskill-platform

**As a** platform admin
**I want** a dedicated endpoint to trigger vendor org discovery on demand
**So that** I can immediately discover skills from new vendor repos without waiting for the next scheduled run

**Acceptance Criteria**:
- [x] **AC-US4-01**: A new endpoint `POST /api/v1/admin/discovery/vendor-orgs` exists that triggers vendor org discovery
- [x] **AC-US4-02**: The endpoint accepts optional body parameters: `orgs` (array of specific orgs to scan, defaults to all VENDOR_ORGS), `force` (boolean to bypass dedup), `dryRun` (boolean to preview without submitting)
- [x] **AC-US4-03**: Authentication requires either `X-Internal-Key` header or `SUPER_ADMIN` JWT role
- [x] **AC-US4-04**: The endpoint returns a JSON response with `candidatesFound`, `newSubmissions`, `skippedDedup`, `skippedFiltered`, `durationMs`, and `orgBreakdown`
- [x] **AC-US4-05**: `vendor-org-discovery` is also registered as a valid source in the existing `POST /api/v1/admin/discovery` endpoint's source filter, enabling it alongside `github-code`, `github-repo`, `npm`, and `skills.sh`

---

### US-005: Pipeline integration via bulk submissions (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** vendor-discovered skills to flow through the existing submission pipeline
**So that** they benefit from the vendor fast-path (`VENDOR_APPROVED`) without bypassing pipeline integrity

**Acceptance Criteria**:
- [x] **AC-US5-01**: The crawl worker submits discoveries via `POST /api/v1/submissions/bulk` using `InlineSubmitter`, identical to how other crawl sources (sourcegraph, github-sharded) submit
- [x] **AC-US5-02**: Each submitted repo includes `repoUrl`, `skillName`, and `skillPath` fields matching the bulk endpoint's expected format
- [x] **AC-US5-03**: The submission pipeline's `processSubmission` correctly identifies vendor repos via `isVendorRepo()` and fast-paths them to `VENDOR_APPROVED` state
- [x] **AC-US5-04**: No direct Prisma writes occur from the crawl worker — all persistence goes through the platform's API endpoints

## Functional Requirements

### FR-001: Vendor org repo enumeration
The `vendor-org-discovery` source iterates over the `VENDOR_ORGS` set (anthropics, openai, google-gemini, google). For each org, it calls `GET /orgs/{org}/repos?type=public&per_page=100&sort=updated` with pagination. Repos where `fork === true` or `stargazers_count === 0` are excluded. The remaining repos proceed to tree scanning.

### FR-002: Per-repo SKILL.md tree scan
For each qualifying repo, the source fetches the default branch via `GET /repos/{owner}/{repo}`, then calls `GET /repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1`. It filters tree entries for blobs ending in `SKILL.md` (case-sensitive), excluding paths inside agent config directories (via `isAgentConfigPath` or equivalent check). Each matching path produces a `DiscoveredRepo` record.

### FR-003: Token rotation and rate limiting
All GitHub API calls rotate through tokens from the `GITHUB_TOKENS` environment variable. Adaptive delay is applied based on `x-ratelimit-remaining` response headers. On 403/429 responses, a 60-second backoff is applied with one retry.

### FR-004: Submission via InlineSubmitter
Discovered skills are buffered and submitted in batches of 15 via `InlineSubmitter` to `POST /api/v1/submissions/bulk`. The `InlineSubmitter` handles retry logic (exponential backoff on 429/5xx).

## Success Criteria

- Vendor skills from all 4 orgs are automatically discovered within 6 hours of being published
- Zero manual script execution required for ongoing vendor skill imports
- Discovery runs complete within 30 minutes (well under the scheduler timeout)
- No duplicate submissions created for already-known skills (dedup via DiscoveryRecord)
- Admin can trigger immediate discovery via the dedicated endpoint

## Out of Scope

- Changing the VENDOR_ORGS list (already defined in `trusted-orgs.ts`)
- Modifying the vendor fast-path in `processSubmission` (already works)
- Private repo access (only public repos enumerated)
- Modifying the `import-vendor-skills.ts` script (will be deprecated naturally but not removed in this increment)
- Adding new vendor organizations

## Dependencies

- Existing `DiscoveryRecord` and `DiscoveryRunLog` Prisma models (already exist)
- Existing `discovery-dedup.ts` functions: `hasBeenDiscovered`, `markDiscovered`, `logDiscoveryRun`
- Existing `InlineSubmitter` class in `crawl-worker/lib/inline-submitter.js`
- Existing `trusted-orgs.ts` with `VENDOR_ORGS` set
- Existing `POST /api/v1/submissions/bulk` endpoint
- Existing vendor fast-path in `processSubmission` (`isVendorRepo` -> `VENDOR_APPROVED`)
- VM-2 deployment infrastructure with `ASSIGNED_SOURCES` env var
- `scheduler.js` source module contract

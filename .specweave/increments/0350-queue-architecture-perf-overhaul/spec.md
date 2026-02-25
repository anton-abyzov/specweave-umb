# 0350 — Queue Architecture & Performance Overhaul

## Problem
1. Queue stats show all zeros — submissions only written to KV, never to Prisma DB
2. Queue table empty — reads stale KV `submissions:index` blob with concurrent write contention
3. External SAST scans never dispatch — `external-scan-dispatch.ts` uses `process.env` (empty in CF Workers)
4. Search doesn't match by repoUrl — one repo with hundreds of skills not discoverable by repo name
5. Admin routes broken — `process.env.INTERNAL_BROADCAST_KEY` empty in production

## User Stories

### US-001: DB-backed submission pipeline
**As** a platform operator
**I want** submissions written to both KV (real-time) and Prisma DB (durable)
**So that** stats, dedup, and listing work correctly

**ACs**:
- [x] AC-US1-01: `createSubmission` writes to Prisma DB
- [x] AC-US1-02: `createSubmissionsBatch` writes to Prisma DB via `createMany`
- [x] AC-US1-03: `updateState` syncs state to Prisma DB (best-effort)
- [x] AC-US1-04: Stats endpoint returns accurate non-zero counts
- [x] AC-US1-05: Queue table shows all submissions with correct states

### US-002: Eliminate KV index blob contention
**As** a developer submitting 56+ skills in a batch
**I want** concurrent queue consumers to not corrupt shared state
**So that** all submissions are tracked accurately

**ACs**:
- [x] AC-US2-01: `submissions:index` blob writes removed from all code paths
- [x] AC-US2-02: GET /api/v1/submissions uses Prisma DB with proper pagination
- [x] AC-US2-03: In-flight submissions re-hydrated from individual KV keys
- [x] AC-US2-04: Broken optimistic concurrency verify-read removed from `updateState`
- [x] AC-US2-05: KV writes in `updateState` parallelized

### US-003: Fix external scan dispatch to Hetzner VMs
**As** a security engineer
**I want** Semgrep/njsscan/TruffleHog scans to dispatch to our Hetzner VMs
**So that** published skills get deep security analysis

**ACs**:
- [x] AC-US3-01: `external-scan-dispatch.ts` uses CF env parameter (not process.env)
- [x] AC-US3-02: Missing secret bindings added to CloudflareEnv
- [x] AC-US3-03: Function signature accepts optional `cfEnv` parameter

### US-004: Search by repository URL
**As** a user searching for skills
**I want** to search by repository name/URL
**So that** I can find all skills from a multi-skill repository

**ACs**:
- [x] AC-US4-01: Edge search matches `repoUrl` substring
- [x] AC-US4-02: Postgres ILIKE fallback includes `repoUrl`

### US-005: Fix process.env across production paths
**As** a platform operator
**I want** all admin routes and utilities to use CF env resolution
**So that** authentication and webhooks work in production

**ACs**:
- [x] AC-US5-01: Shared `internal-auth.ts` helper created
- [x] AC-US5-02: All admin routes use shared helper
- [x] AC-US5-03: Webhook scan-results uses CF env
- [x] AC-US5-04: GitHub OAuth uses CF env
- [x] AC-US5-05: Cron crawl dispatch parallelized

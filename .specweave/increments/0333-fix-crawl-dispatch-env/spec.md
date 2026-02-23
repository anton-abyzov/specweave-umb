# 0333: Fix Crawl Dispatch process.env Mismatch

## Problem
`crawl-dispatch.ts` reads `CRAWLER_WORKERS` and `SCANNER_WORKER_SECRET` from `process.env`, which is empty in Cloudflare Workers runtime. Secrets set via `wrangler secret put` are only available on the `env` handler parameter. This silently drops all VM crawl dispatches — the scraper pipeline has been stalled >1 day with 5K skills on the homepage and zero new submissions.

## User Stories

### US-001: Fix crawl dispatch env access
As a platform operator, I want the hourly cron to successfully dispatch crawl jobs to Hetzner VMs so that new skills are continuously discovered.

**Acceptance Criteria:**
- [x] AC-US1-01: `dispatchCrawlJob()` reads `CRAWLER_WORKERS` from Cloudflare env, not `process.env`
- [x] AC-US1-02: `dispatchCrawlJob()` reads `SCANNER_WORKER_SECRET` from Cloudflare env, not `process.env`
- [x] AC-US1-03: `scheduled()` handler passes `env` to `dispatchCrawlJob()` as third parameter
- [x] AC-US1-04: Backwards compatible — fallback to `getWorkerEnv()` / `getCloudflareContext()` when no explicit env
- [x] AC-US1-05: Diagnostic log in `scheduled()` confirms env vars are present

### US-002: Add missing CloudflareEnv types
As a developer, I want all Cloudflare secret bindings typed in `CloudflareEnv` so that TypeScript catches missing env access patterns.

**Acceptance Criteria:**
- [x] AC-US2-01: `CRAWLER_WORKERS`, `SCANNER_WORKER_SECRET`, `PLATFORM_URL`, `GITLAB_TOKEN` added to `CloudflareEnv`

### US-003: Update tests
As a developer, I want tests to pass mock env explicitly instead of manipulating `process.env`.

**Acceptance Criteria:**
- [x] AC-US3-01: Tests pass mock `CloudflareEnv` with `CRAWLER_WORKERS` + `SCANNER_WORKER_SECRET`
- [x] AC-US3-02: Fallback path test verifies `getCloudflareContext` still works when no explicit env
- [x] AC-US3-03: All existing test cases (TC-007 through TC-010) pass

## Scope
- `src/lib/crawl-dispatch.ts`
- `src/lib/env.d.ts`
- `scripts/build-worker-entry.ts`
- `src/lib/__tests__/crawl-dispatch.test.ts`

## Out of Scope
- `external-scan-dispatch.ts` (same bug pattern, follow-up increment)

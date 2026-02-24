---
id: US-001
feature: FS-333
title: Fix crawl dispatch env access
status: completed
priority: P0
created: 2026-02-23
project: vskill-platform
---
# US-001: Fix crawl dispatch env access

**Feature**: [FS-333](./FEATURE.md)

**As a** platform operator
**I want** the hourly cron to successfully dispatch crawl jobs to Hetzner VMs
**So that** new skills are continuously discovered

---

## Acceptance Criteria

- [x] **AC-US1-01**: `dispatchCrawlJob()` reads `CRAWLER_WORKERS` from Cloudflare env, not `process.env`
- [x] **AC-US1-02**: `dispatchCrawlJob()` reads `SCANNER_WORKER_SECRET` from Cloudflare env, not `process.env`
- [x] **AC-US1-03**: `scheduled()` handler passes `env` to `dispatchCrawlJob()` as third parameter
- [x] **AC-US1-04**: Backwards compatible — fallback to `getWorkerEnv()` / `getCloudflareContext()` when no explicit env
- [x] **AC-US1-05**: Diagnostic log in `scheduled()` confirms env vars are present

---

## Implementation

**Increment**: [0333-fix-crawl-dispatch-env](../../../../../increments/0333-fix-crawl-dispatch-env/spec.md)

**Files Modified**:
- `src/lib/crawl-dispatch.ts`
- `scripts/build-worker-entry.ts`
- `src/lib/__tests__/crawl-dispatch.test.ts`

### Notes

The fix ensures that Cloudflare secret bindings passed via the `env` handler parameter are properly read instead of attempting to access the empty `process.env` in Cloudflare Workers runtime. A backwards-compatible fallback path maintains support for scenarios where the env is not explicitly passed.

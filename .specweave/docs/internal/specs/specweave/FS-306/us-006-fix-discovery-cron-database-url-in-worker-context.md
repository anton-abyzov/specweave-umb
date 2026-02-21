---
id: US-006
feature: FS-306
title: Fix Discovery Cron DATABASE_URL in Worker Context
status: not-started
priority: P1
created: 2026-02-21
project: specweave
external:
  github:
    issue: 1252
    url: https://github.com/anton-abyzov/specweave/issues/1252
---
# US-006: Fix Discovery Cron DATABASE_URL in Worker Context

**Feature**: [FS-306](./FEATURE.md)

platform operator
**I want** the discovery cron to have access to DATABASE_URL in the worker context
**So that** DB-based dedup does not silently fail and new skills continue to be discovered

---

## Acceptance Criteria

- [ ] **AC-US6-01**: The scheduled handler in `worker-with-queues.js` sets `process.env.DATABASE_URL` from `env.DATABASE_URL` (or via `setWorkerEnv`) before calling `runGitHubDiscovery(env)`
- [ ] **AC-US6-02**: `getDb()` in `db.ts` also checks the worker env (via `getWorkerEnv()`) for DATABASE_URL, similar to how `getKV()` uses worker context as fallback
- [ ] **AC-US6-03**: If DATABASE_URL is not available, discovery logs a clear error message (not a silent catch) and falls back gracefully
- [ ] **AC-US6-04**: Add `DATABASE_URL` as a secret binding in `wrangler.jsonc` vars or secrets (or document that it must be configured)
- [ ] **AC-US6-05**: Unit tests verify that `getDb()` uses worker context when `process.env.DATABASE_URL` is not set

---

## Implementation

**Increment**: [0306-fix-marketplace-skill-loss](../../../../../increments/0306-fix-marketplace-skill-loss/spec.md)


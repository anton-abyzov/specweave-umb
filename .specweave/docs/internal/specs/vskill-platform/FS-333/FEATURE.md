---
id: FS-333
title: Fix Crawl Dispatch process.env Mismatch
type: feature
status: completed
priority: P0
created: 2026-02-23
lastUpdated: 2026-02-23
tldr: Fix crawl dispatch environment variable access in Cloudflare Workers runtime
complexity: low
auto_created: true
---
# Fix Crawl Dispatch process.env Mismatch

## TL;DR

**What**: Fix crawl dispatch environment variable access in Cloudflare Workers runtime
**Status**: completed | **Priority**: P0
**User Stories**: 3

## Overview

The `crawl-dispatch.ts` module reads `CRAWLER_WORKERS` and `SCANNER_WORKER_SECRET` from `process.env`, which is empty in Cloudflare Workers runtime. Secrets set via `wrangler secret put` are only available on the `env` handler parameter. This silently dropped all VM crawl dispatches, stalling the scraper pipeline for over 1 day with 5,000 skills on the homepage and zero new submissions.

## Implementation History

| Increment | Status |
|-----------|--------|
| [0333-fix-crawl-dispatch-env](../../../../../increments/0333-fix-crawl-dispatch-env/spec.md) | completed |

## User Stories

- [US-001: Fix crawl dispatch env access](./us-001-fix-crawl-dispatch-env-access.md)
- [US-002: Add missing CloudflareEnv types](./us-002-add-missing-cloudflare-env-types.md)
- [US-003: Update tests](./us-003-update-tests.md)

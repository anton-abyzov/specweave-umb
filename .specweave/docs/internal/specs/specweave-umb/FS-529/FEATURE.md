---
id: FS-529
title: "Fix GitHub API Rate Limit Exhaustion"
type: feature
status: completed
priority: P1
created: 2026-03-15
lastUpdated: 2026-03-15
tldr: "SpecWeave exhausts GitHub's 5000 req/hour API limit during normal sync operations."
complexity: medium
stakeholder_relevant: true
---

# Fix GitHub API Rate Limit Exhaustion

## TL;DR

**What**: SpecWeave exhausts GitHub's 5000 req/hour API limit during normal sync operations.
**Status**: completed | **Priority**: P1
**User Stories**: 2

## Overview

SpecWeave exhausts GitHub's 5000 req/hour API limit during normal sync operations. The reconciler scans ALL 529 increments (175 active + 372 archived + 12 abandoned), making individual `getIssue()` calls per user story — 350+ API calls per run. Combined with DuplicateDetector triple-scan and AC checkbox N+1, total reaches ~5000 calls/hour.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0529-fix-github-api-rate-limit](../../../../../increments/0529-fix-github-api-rate-limit/spec.md) | ✅ completed | 2026-03-15 |

## User Stories

- [US-001: Scope reconciler to active increments only](./us-001-scope-reconciler-to-active-increments-only.md)
- [US-002: Eliminate redundant API calls in sync pipeline](./us-002-eliminate-redundant-api-calls-in-sync-pipeline.md)

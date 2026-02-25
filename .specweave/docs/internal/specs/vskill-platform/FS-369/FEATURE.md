---
id: FS-369
title: Fix Duplicate Processing False Rejections
type: feature
status: active
priority: P0
created: 2026-02-24
lastUpdated: 2026-02-24
complexity: medium
stakeholder_relevant: true
project: vskill-platform
external_tools:
  github:
    type: milestone
    id: 8
    url: https://github.com/anton-abyzov/specweave-umb/milestone/8
---

# Fix Duplicate Processing False Rejections

## TL;DR

**What**: Add state guards and pipeline idempotency to prevent duplicate processing from overwriting PUBLISHED submissions to REJECTED, plus bulk restore for affected submissions.
**Status**: active | **Priority**: P0
**User Stories**: 3

## Overview

Submissions are processed multiple times by the queue (retry + recovery cron). Because `updateState()` has no guards, the last write wins — causing PUBLISHED submissions to be overridden to REJECTED. Confirmed on 7+ submissions scoring 100/100 PASS but ending as REJECTED.

## User Stories

- [US-001: State Guard](./us-001-state-guard.md)
- [US-002: Pipeline Idempotency](./us-002-pipeline-idempotency.md)
- [US-003: Bulk Restore](./us-003-bulk-restore.md)

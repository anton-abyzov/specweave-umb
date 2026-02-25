---
id: FS-364
title: Admin-Only Rejected Skills with Bulk Actions
type: feature
status: active
priority: P1
created: 2026-02-24
lastUpdated: 2026-02-24
complexity: medium
stakeholder_relevant: true
project: vskill-platform
external_tools:
  github:
    type: milestone
    id: 6
    url: https://github.com/anton-abyzov/specweave-umb/milestone/6
---

# Admin-Only Rejected Skills with Bulk Actions

## TL;DR

**What**: Fix rejected skills tab display bug, make it admin-only, add pagination with category filtering, and add bulk actions (reprocess/block).
**Status**: active | **Priority**: P1
**User Stories**: 3

## Overview

The Trust Center's "Rejected Skills" tab has a display bug (API returns `rejections` key but frontend reads `entries`). The tab is publicly visible when it should be admin-only. No way to act on rejected skills in bulk. Many rejections are platform errors not real security issues.

## User Stories

- [US-001: Admin views rejected skills](./us-001-admin-views-rejected-skills.md)
- [US-002: Admin bulk reprocesses rejected skills](./us-002-admin-bulk-reprocesses-rejected-skills.md)
- [US-003: Admin bulk blocks rejected skills](./us-003-admin-bulk-blocks-rejected-skills.md)

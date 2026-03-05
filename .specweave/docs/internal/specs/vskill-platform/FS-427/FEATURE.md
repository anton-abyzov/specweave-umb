---
id: FS-427
title: Umbrella Sync Lifecycle Test
type: feature
status: active
priority: P1
created: 2026-03-05
lastUpdated: 2026-03-05
tldr: End-to-end lifecycle test for umbrella cross-project sync.
complexity: low
stakeholder_relevant: true
external_tools:
  github:
    type: milestone
    id: 4
    url: https://github.com/anton-abyzov/vskill-platform/milestone/4
---

# Umbrella Sync Lifecycle Test

## TL;DR

**What**: End-to-end lifecycle test for umbrella cross-project sync.
**Status**: active | **Priority**: P1
**User Stories**: 1

![Umbrella Sync Lifecycle Test illustration](assets/feature-fs-427.jpg)

## Overview

End-to-end lifecycle test for umbrella cross-project sync. Tests that creating an increment with cross-project user stories automatically syncs to GitHub, JIRA, and ADO per child repo.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0427-umbrella-sync-lifecycle-test](../../../../../increments/0427-umbrella-sync-lifecycle-test/spec.md) | ⏳ active | 2026-03-05 |

## User Stories

- [US-VPL-001: VSkill-Platform Sync Routing Verification](./us-vpl-001-vskill-platform-sync-routing-verification.md)

## Related Projects

This feature spans multiple projects:

- [specweave](../../specweave/FS-427/)
- [vskill](../../vskill/FS-427/)

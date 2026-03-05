---
id: FS-425
title: Umbrella Sync E2E Verification
type: feature
status: active
priority: P2
created: 2026-03-04
lastUpdated: 2026-03-05
tldr: Verify that umbrella sync routing correctly routes GitHub issues, JIRA
  tickets, and ADO work items to per-child-repo targets based on the **Project**
  field in each user story.
complexity: low
stakeholder_relevant: true
external_tools:
  github:
    type: milestone
    id: 3
    url: https://github.com/anton-abyzov/vskill/milestone/3
---

# Umbrella Sync E2E Verification

## TL;DR

**What**: Verify that umbrella sync routing correctly routes GitHub issues, JIRA tickets, and ADO work items to per-child-repo targets based on the **Project** field in each user story.
**Status**: active | **Priority**: P2
**User Stories**: 1

![Umbrella Sync E2E Verification illustration](assets/feature-fs-425.jpg)

## Overview

Verify that umbrella sync routing correctly routes GitHub issues, JIRA tickets, and ADO work items to per-child-repo targets based on the **Project** field in each user story.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0425-umbrella-sync-e2e-test](../../../../../increments/0425-umbrella-sync-e2e-test/spec.md) | ⏳ active | 2026-03-04 |

## User Stories

- [US-VSK-001: VSkill Repo Sync Verification](./us-vsk-001-vskill-repo-sync-verification.md)

## Related Projects

This feature spans multiple projects:

- [specweave](../../specweave/FS-425/)
- [vskill-platform](../../vskill-platform/FS-425/)

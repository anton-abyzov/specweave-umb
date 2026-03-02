---
id: FS-400
title: "FS-400: Sync Pipeline Reliability"
type: feature
status: completed
priority: P1
created: 2026-03-02
lastUpdated: 2026-03-02
tldr: "The GitHub sync pipeline has multiple structural bugs causing increments to go unsynced, milestones to remain open after completion, and task-level progress to never reach external tools."
complexity: high
stakeholder_relevant: true
---

# FS-400: Sync Pipeline Reliability

## TL;DR

**What**: The GitHub sync pipeline has multiple structural bugs causing increments to go unsynced, milestones to remain open after completion, and task-level progress to never reach external tools.
**Status**: completed | **Priority**: P1
**User Stories**: 6

![FS-400: Sync Pipeline Reliability illustration](assets/feature-fs-400.jpg)

## Overview

The GitHub sync pipeline has multiple structural bugs causing increments to go unsynced, milestones to remain open after completion, and task-level progress to never reach external tools. Five specific failures were identified through audit of increments 0390-0399.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0400-sync-pipeline-reliability](../../../../../increments/0400-sync-pipeline-reliability/spec.md) | ✅ completed | 2026-03-02 |

## User Stories

- [US-001: Task completion triggers external sync](./us-001-task-completion-triggers-external-sync.md)
- [US-002: Milestone lifecycle is fully automated](./us-002-milestone-lifecycle-is-fully-automated.md)
- [US-003: externalLinks and github fields stay consistent](./us-003-externallinks-and-github-fields-stay-consistent.md)
- [US-004: Sync errors surface instead of being swallowed](./us-004-sync-errors-surface-instead-of-being-swallowed.md)
- [US-005: Metadata schema validation enforced globally](./us-005-metadata-schema-validation-enforced-globally.md)
- [US-006: Stale milestone cleanup command](./us-006-stale-milestone-cleanup-command.md)

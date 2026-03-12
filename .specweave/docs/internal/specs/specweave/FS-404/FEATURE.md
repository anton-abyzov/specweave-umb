---
id: FS-404
title: "Spec: JIRA Sync Plugin Critical Fixes (0403)"
type: feature
status: ready_for_review
priority: P1
created: 2026-03-02
lastUpdated: 2026-03-02
tldr: The JIRA sync plugin suite (`specweave-jira`) has 18 bugs identified via
  grill report,.
complexity: high
stakeholder_relevant: true
external_tools:
  github:
    type: milestone
    id: 199
    url: "https://github.com/anton-abyzov/specweave/milestone/199"
---

# Spec: JIRA Sync Plugin Critical Fixes (0403)

## TL;DR

**What**: The JIRA sync plugin suite (`specweave-jira`) has 18 bugs identified via grill report,.
**Status**: ready_for_review | **Priority**: P1
**User Stories**: 8

## Overview

The JIRA sync plugin suite (`specweave-jira`) has 18 bugs identified via grill report,
ranging from data integrity failures to complete feature breakage on self-hosted JIRA
instances. This increment addresses all bugs grouped by priority.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0404-jira-sync-plugin-fixes](../../../../../increments/0404-jira-sync-plugin-fixes/spec.md) | ⏳ ready_for_review | 2026-03-02 |

## User Stories

- [US-001: Consistent Metadata Path for JIRA Issue Keys](./us-001-consistent-metadata-path-for-jira-issue-keys.md)
- [US-002: Self-Hosted JIRA Server Compatibility](./us-002-self-hosted-jira-server-compatibility.md)
- [US-003: Correct Content Format Per API Version](./us-003-correct-content-format-per-api-version.md)
- [US-004: Dynamic Epic Link Field Detection](./us-004-dynamic-epic-link-field-detection.md)
- [US-005: Pagination and Rate Limiting for JIRA API](./us-005-pagination-and-rate-limiting-for-jira-api.md)
- [US-006: Safe Conflict Resolution](./us-006-safe-conflict-resolution.md)
- [US-007: Reorganization Detector Reliability](./us-007-reorganization-detector-reliability.md)
- [US-008: Misc Bug Fixes (Prefix, Empty Epics, Verify, ESM)](./us-008-misc-bug-fixes-prefix-empty-epics-verify-esm.md)

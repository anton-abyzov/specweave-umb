---
id: FS-435
title: Redesign vskill find command with install counts
type: feature
status: active
priority: P1
created: 2026-03-05
lastUpdated: 2026-03-07
tldr: The `vskill find` command currently displays results in a grouped
  marketplace table with 50 results by default, which is overwhelming and buries
  the most useful skills.
complexity: low
stakeholder_relevant: true
external_tools:
  github:
    type: milestone
    id: 12
    url: "https://github.com/anton-abyzov/vskill-platform/milestone/12"
---

# Redesign vskill find command with install counts

## TL;DR

**What**: The `vskill find` command currently displays results in a grouped marketplace table with 50 results by default, which is overwhelming and buries the most useful skills.
**Status**: active | **Priority**: P1
**User Stories**: 1

## Overview

The `vskill find` command currently displays results in a grouped marketplace table with 50 results by default, which is overwhelming and buries the most useful skills. Results are sorted by score but lack install counts, making it hard for users to gauge real-world adoption. The search API does not return `vskillInstalls` in its response, so the CLI cannot display this data even if it wanted to.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0435-find-command-redesign](../../../../../increments/0435-find-command-redesign/spec.md) | ⏳ active | 2026-03-05 |

## User Stories

- [US-VPL-002: Install counts in search API response (P1)](./us-vpl-002-install-counts-in-search-api-response-p1.md)

## Related Projects

This feature spans multiple projects:

- [vskill](../../vskill/FS-435/)

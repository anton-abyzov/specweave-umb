---
id: FS-395
title: "Init Location Guard Rails"
type: feature
status: ready_for_review
priority: P1
created: 2026-03-01
lastUpdated: 2026-03-02
tldr: "Add guard rails to `specweave init` to prevent creating `.specweave/` folders in wrong locations."
complexity: medium
stakeholder_relevant: true
---

# Init Location Guard Rails

## TL;DR

**What**: Add guard rails to `specweave init` to prevent creating `.specweave/` folders in wrong locations.
**Status**: ready_for_review | **Priority**: P1
**User Stories**: 2

## Overview

Add guard rails to `specweave init` to prevent creating `.specweave/` folders in wrong locations. Two new checks run early in the init flow:

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0395-init-location-guard-rails](../../../../../increments/0395-init-location-guard-rails/spec.md) | ⏳ ready_for_review | 2026-03-01 |

## User Stories

- [US-001: Prevent Init Inside Umbrella Sub-Repos (P0)](./us-001-prevent-init-inside-umbrella-sub-repos-p0.md)
- [US-002: Prevent Init in Suspicious Paths (P0)](./us-002-prevent-init-in-suspicious-paths-p0.md)

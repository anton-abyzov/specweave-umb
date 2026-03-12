---
id: FS-416
title: "Umbrella sync consolidation: distributed routing and increment cleanup"
type: feature
status: completed
priority: P1
created: "2026-03-03T00:00:00.000Z"
lastUpdated: 2026-03-03
tldr: "SpecWeave's umbrella mode (`umbrella.enabled: true`) supports multiple repos under `repositories/org/repo-name/` with per-repo sync config (`childRepos[].sync`)."
complexity: medium
stakeholder_relevant: true
---

# Umbrella sync consolidation: distributed routing and increment cleanup

## TL;DR

**What**: SpecWeave's umbrella mode (`umbrella.enabled: true`) supports multiple repos under `repositories/org/repo-name/` with per-repo sync config (`childRepos[].sync`).
**Status**: completed | **Priority**: P1
**User Stories**: 3

## Overview

SpecWeave's umbrella mode (`umbrella.enabled: true`) supports multiple repos under `repositories/org/repo-name/` with per-repo sync config (`childRepos[].sync`). However, the sync pipeline (LivingDocsSync, sync-progress, ExternalIssueAutoCreator) reads only the global `sync.github` config — all GitHub issues, Jira tickets, and ADO work items route to a single repo regardless of which project the increment belongs to. Additionally, orphaned increments and living docs have accumulated in nested repo `.specweave/` directories instead of the umbrella root, and type system gaps make the config schema difficult to validate or extend safely.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0416-umbrella-sync-consolidation](../../../../../increments/0416-umbrella-sync-consolidation/spec.md) | ✅ completed | 2026-03-03T00:00:00.000Z |

## User Stories

- [US-001: Distributed External Sync Routing (P1)](./us-001-distributed-external-sync-routing-p1.md)
- [US-002: Consolidate Nested Increments (P1)](./us-002-consolidate-nested-increments-p1.md)
- [US-003: Type System and Bug Fixes (P2)](./us-003-type-system-and-bug-fixes-p2.md)

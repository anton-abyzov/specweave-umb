---
id: 0385-fix-github-issue-auto-closure
title: Fix GitHub issue auto-closure on increment completion
status: completed
started: 2026-02-27T00:00:00.000Z
type: bug
priority: P1
project: specweave
totalACs: 3
satisfiedACs: 3
---

# Fix GitHub Issue Auto-Closure

## Problem
When increments complete via `specweave complete`, GitHub issues stay open. The closure chain depends on living docs files (FEATURE.md, us-*.md) that don't exist for most increments. `SyncCoordinator` explicitly skips GitHub ("Handled by GitHubFeatureSync pipeline"), creating circular delegation where nobody actually closes anything.

## User Stories

### US-001: Direct metadata-based issue closure
As a developer, I want GitHub issues to close automatically when an increment completes, without depending on living docs files.

- [x] **AC-US1-01**: `closeCompletedIncrementIssues()` reads issue numbers from both metadata formats (externalLinks and legacy github.issues)
- [x] **AC-US1-02**: Method deduplicates issue numbers, checks state via API, closes open issues with completion comment
- [x] **AC-US1-03**: `completeIncrement()` calls the new method as a fallback after LifecycleHookDispatcher

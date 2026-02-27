---
id: US-001
feature: FS-385
title: "Direct metadata-based issue closure"
status: completed
priority: P1
created: 2026-02-27
tldr: "As a developer, I want GitHub issues to close automatically when an increment completes, without depending on living docs files."
---

# US-001: Direct metadata-based issue closure

**Feature**: [FS-385](./FEATURE.md)

As a developer, I want GitHub issues to close automatically when an increment completes, without depending on living docs files.

---

## Acceptance Criteria

- [x] **AC-US1-01**: `closeCompletedIncrementIssues()` reads issue numbers from both metadata formats (externalLinks and legacy github.issues)
- [x] **AC-US1-02**: Method deduplicates issue numbers, checks state via API, closes open issues with completion comment
- [x] **AC-US1-03**: `completeIncrement()` calls the new method as a fallback after LifecycleHookDispatcher

---

## Implementation

**Increment**: [0385-fix-github-issue-auto-closure](../../../../../increments/0385-fix-github-issue-auto-closure/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_

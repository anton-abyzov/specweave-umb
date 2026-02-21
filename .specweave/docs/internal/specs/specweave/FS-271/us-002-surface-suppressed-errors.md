---
id: US-002
feature: FS-271
title: Surface suppressed errors
status: complete
priority: P1
created: 2026-02-21
project: specweave
external:
  github:
    issue: 1200
    url: "https://github.com/anton-abyzov/specweave/issues/1200"
---
# US-002: Surface suppressed errors

**Feature**: [FS-271](./FEATURE.md)

developer debugging sync failures
**I want** error details to be logged instead of silently swallowed
**So that** I can diagnose why GitHub issues are not being created

---

## Acceptance Criteria

- [x] **AC-US2-01**: `ExternalIssueAutoCreator.checkExistingIssue()` logs a warning on JSON parse errors instead of silent catch
- [x] **AC-US2-02**: `sync-progress.ts checkExistingGitHubIssue()` logs a warning on errors instead of silent catch
- [x] **AC-US2-03**: `sync-progress.ts detectActiveIncrement()` logs a debug message on errors instead of silent catch

---

## Implementation

**Increment**: [0271-fix-external-sync-pipeline](../../../../../increments/0271-fix-external-sync-pipeline/spec.md)


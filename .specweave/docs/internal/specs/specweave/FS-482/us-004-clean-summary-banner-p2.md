---
id: US-004
feature: FS-482
title: "Clean Summary Banner (P2)"
status: completed
priority: P1
created: "2026-03-10T00:00:00.000Z"
tldr: "**As a** developer."
project: specweave
external:
  github:
    issue: 1531
    url: "https://github.com/anton-abyzov/specweave/issues/1531"
---

# US-004: Clean Summary Banner (P2)

**Feature**: [FS-482](./FEATURE.md)

**As a** developer
**I want** a concise init completion summary
**So that** I can quickly verify what was configured

---

## Acceptance Criteria

- [x] **AC-US4-01**: Given a successful init, when the summary banner renders, then it does not display tracker, repoCount, isGreenfield, hasPendingClones, syncPermissions, projectMaturity, or structureDeferred fields
- [x] **AC-US4-02**: Given a successful init, when the summary banner renders, then it shows: project name, adapter, provider, language, and defaults (testing, quality gates, LSP, git hooks)
- [x] **AC-US4-03**: Given the `SummaryBannerOptions` interface, when inspected, then removed fields (tracker, repoCount, isGreenfield, hasPendingClones, externalPluginInstalled, syncPermissions, projectMaturity, structureDeferred) are no longer present

---

## Implementation

**Increment**: [0482-simplify-init](../../../../../increments/0482-simplify-init/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-011**: Remove external tool fields from SummaryBannerOptions interface
- [x] **T-012**: Verify summary banner renders correctly with simplified data

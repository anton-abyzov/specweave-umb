---
id: US-002
feature: FS-514
title: "Brownfield repo layout detection"
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** developer with repositories in a non-standard layout (missing org subfolder),."
---

# US-002: Brownfield repo layout detection

**Feature**: [FS-514](./FEATURE.md)

**As a** developer with repositories in a non-standard layout (missing org subfolder),
**I want** `specweave init` to detect this and show me exactly how to fix it,
**So that** I understand why my repos aren't being recognized and can follow a clear path to fix it.

---

## Acceptance Criteria

- [x] **AC-US2-01**: After `specweave init`, when repos exist at `repositories/{name}/.git` (1-level), a warning is displayed
- [x] **AC-US2-02**: Warning lists the affected repository names
- [x] **AC-US2-03**: Warning shows the exact `mkdir` + `mv` fix command with the first affected repo as example
- [x] **AC-US2-04**: When repos follow the standard 2-level `{org}/{repo}` pattern, no warning is shown
- [x] **AC-US2-05**: When no `repositories/` directory exists, no warning is shown
- [x] **AC-US2-06**: Warning does not appear when `scanUmbrellaRepos()` already found valid repos

---

## Implementation

**Increment**: [0514-init-sync-setup-brownfield](../../../../../increments/0514-init-sync-setup-brownfield/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_

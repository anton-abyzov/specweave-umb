---
id: US-002
feature: FS-492
title: "Extract umbrella config helper (P2)"
status: completed
priority: P1
created: 2026-03-11T00:00:00.000Z
tldr: "**As a** maintainer of the specweave CLI."
project: specweave
external:
  github:
    issue: 1545
    url: https://github.com/anton-abyzov/specweave/issues/1545
---

# US-002: Extract umbrella config helper (P2)

**Feature**: [FS-492](./FEATURE.md)

**As a** maintainer of the specweave CLI
**I want** the umbrella config generation logic to exist in a single reusable function
**So that** prefix deduplication and childRepos mapping are consistent and changes don't require dual edits

---

## Acceptance Criteria

- [x] **AC-US2-01**: A new exported function `buildUmbrellaConfig(discovery: UmbrellaDiscoveryResult, projectName: string)` exists in `cli/helpers/init/` and returns `{ umbrella: { enabled, projectName, childRepos }, repository: { umbrellaRepo: true } }`
- [x] **AC-US2-02**: Both call sites in `init.ts` (initial scan at ~line 360 and post-clone re-scan at ~line 420) use the new helper instead of inline logic
- [x] **AC-US2-03**: Prefix deduplication behavior is preserved: 3-char uppercase prefix from repo name, with numeric suffix disambiguation
- [x] **AC-US2-04**: The helper is exported from the `cli/helpers/init/index.ts` barrel file

---

## Implementation

**Increment**: [0492-init-project-resolution-redesign](../../../../../increments/0492-init-project-resolution-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_

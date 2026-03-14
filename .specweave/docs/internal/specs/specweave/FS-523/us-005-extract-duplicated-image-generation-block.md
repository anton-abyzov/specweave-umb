---
id: US-005
feature: FS-523
title: Extract Duplicated Image Generation Block
status: completed
priority: P1
created: 2026-03-14
tldr: "**As a** SpecWeave maintainer."
project: specweave
external:
  github:
    issue: 1569
    url: https://github.com/anton-abyzov/specweave/issues/1569
---

# US-005: Extract Duplicated Image Generation Block

**Feature**: [FS-523](./FEATURE.md)

**As a** SpecWeave maintainer
**I want** the image generation and TL;DR injection logic extracted to a private helper
**So that** the cross-project and single-project paths share one implementation

---

## Acceptance Criteria

- [x] **AC-US5-01**: Given `living-docs-sync.ts`, when searching for `generateLivingDocsImagesEnhanced`, then it is called from exactly one private helper method (not inline in two places)
- [x] **AC-US5-02**: Given SPECWEAVE_SKIP_IMAGE_GEN=true, when sync runs in either cross-project or single-project mode, then image generation is skipped (behavior preserved)
- [x] **AC-US5-03**: Given a successful image generation, when the helper runs, then the image markdown is injected after the TL;DR section in FEATURE.md content

---

## Implementation

**Increment**: [0523-living-docs-sync-cleanup](../../../../../increments/0523-living-docs-sync-cleanup/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-007**: Run full test suite and confirm all grep invariants

---
id: US-004
feature: FS-219
title: Umbrella-Aware Docs
status: complete
priority: P0
created: 2026-02-21
project: specweave
external:
  github:
    issue: 1197
    url: https://github.com/anton-abyzov/specweave/issues/1197
---
# US-004: Umbrella-Aware Docs

**Feature**: [FS-219](./FEATURE.md)

developer with an umbrella project
**I want** `specweave docs` to serve documentation from both the umbrella root and child repos
**So that** I get a unified documentation experience across all repositories

---

## Acceptance Criteria

- [x] **AC-US4-01**: `specweave docs preview` works correctly from an umbrella root, serving `.specweave/docs/internal/` at the umbrella level
- [x] **AC-US4-02**: Documentation sidebar aggregates child repo docs when child repos have their own `.specweave/docs/`
- [x] **AC-US4-03**: `specweave docs status` shows umbrella docs summary including child repo doc counts
- [x] **AC-US4-04**: SpecWeave's own `docs-site/` remains untouched (product website concern, not framework concern)

---

## Implementation

**Increment**: [0219-multi-repo-migrate](../../../../../increments/0219-multi-repo-migrate/spec.md)


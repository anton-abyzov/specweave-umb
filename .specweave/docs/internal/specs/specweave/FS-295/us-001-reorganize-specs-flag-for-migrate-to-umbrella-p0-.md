---
id: US-001
feature: FS-295
title: "Reorganize Specs Flag for migrate-to-umbrella (P0)"
status: not_started
priority: P1
created: 2026-02-21
tldr: "Reorganize Specs Flag for migrate-to-umbrella (P0)"
project: specweave
---

# US-001: Reorganize Specs Flag for migrate-to-umbrella (P0)

**Feature**: [FS-295](./FEATURE.md)

---

## Acceptance Criteria

- [ ] **AC-US1-01**: `migrate-to-umbrella --reorganize-specs` is a valid CLI flag (added to commander options)
- [ ] **AC-US1-02**: Running without `--execute` shows a dry-run plan listing each FS-XXX folder and its target project directory
- [ ] **AC-US1-03**: Running with `--execute --reorganize-specs` physically moves FS-XXX folders from the centralized location to per-project directories under `.specweave/docs/internal/specs/{project}/`
- [ ] **AC-US1-04**: The command reads increment `spec.md` files to determine project ownership via the `**Project**:` field in user stories
- [ ] **AC-US1-05**: FS-XXX folders with assets/ subdirectories are moved intact (entire tree preserved)
- [ ] **AC-US1-06**: Cross-project specs (multiple `**Project**:` values) are copied to each relevant project folder
- [ ] **AC-US1-07**: Specs with no project mapping fall back to the umbrella root `specweave/` project folder
- [ ] **AC-US1-08**: The operation is idempotent -- running again on already-reorganized specs is a no-op with informative output

---

## Implementation

**Increment**: [0295-multi-repo-docs-restructuring](../../../../../increments/0295-multi-repo-docs-restructuring/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-004**: Implement reorganizeSpecs() execution and config update

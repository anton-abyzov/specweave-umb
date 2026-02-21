---
increment: 0295-multi-repo-docs-restructuring
title: "Multi-Repo Docs Restructuring"
type: feature
priority: P1
status: planned
created: 2026-02-21
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Feature: Multi-Repo Docs Restructuring

## Overview

After migrating to an umbrella workspace, all living docs (FS-XXX spec folders) remain centralized under `.specweave/docs/internal/specs/specweave/` regardless of which repo they actually belong to. This increment adds a `--reorganize-specs` flag to `migrate-to-umbrella` that:

1. Enables `multiProject` mode in config.json
2. Maps each FS-XXX folder to its owning repo based on the `**Project**:` field in increment specs
3. Moves spec folders to per-repo `.specweave/docs/internal/specs/` directories
4. Verifies the restructured layout works with living-docs sync

### Current State

```
specweave-umb/.specweave/docs/internal/specs/specweave/
├── FS-142/   # belongs to specweave
├── FS-282/   # belongs to vskill-platform
├── FS-286/   # belongs to vskill
├── FS-294/   # belongs to specweave
└── ... (30+ folders, all under "specweave" regardless of actual project)
```

### Target State

```
specweave-umb/.specweave/docs/internal/specs/
├── specweave/
│   ├── FS-142/
│   └── FS-294/
├── vskill/
│   └── FS-286/
└── vskill-platform/
    └── FS-282/
```

Config.json changes:
```json
{
  "multiProject": {
    "enabled": true
  }
}
```

## User Stories

### US-001: Reorganize Specs Flag for migrate-to-umbrella (P0)
**Project**: specweave

**As a** developer with an umbrella workspace where all specs are under one project folder
**I want to** run `specweave migrate-to-umbrella --reorganize-specs` to redistribute spec folders by project
**So that** living docs are organized per-repo matching the multi-repo structure

**Acceptance Criteria**:
- [x] **AC-US1-01**: `migrate-to-umbrella --reorganize-specs` is a valid CLI flag (added to commander options)
- [x] **AC-US1-02**: Running without `--execute` shows a dry-run plan listing each FS-XXX folder and its target project directory
- [x] **AC-US1-03**: Running with `--execute --reorganize-specs` physically moves FS-XXX folders from the centralized location to per-project directories under `.specweave/docs/internal/specs/{project}/`
- [x] **AC-US1-04**: The command reads increment `spec.md` files to determine project ownership via the `**Project**:` field in user stories
- [x] **AC-US1-05**: FS-XXX folders with assets/ subdirectories are moved intact (entire tree preserved)
- [x] **AC-US1-06**: Cross-project specs (multiple `**Project**:` values) are copied to each relevant project folder
- [x] **AC-US1-07**: Specs with no project mapping fall back to the umbrella root `specweave/` project folder
- [x] **AC-US1-08**: The operation is idempotent -- running again on already-reorganized specs is a no-op with informative output

---

### US-002: Enable multiProject Mode (P0)
**Project**: specweave

**As a** developer running `--reorganize-specs`
**I want** `multiProject.enabled` to be set to `true` in config.json automatically
**So that** living-docs sync and other SpecWeave features use per-project paths

**Acceptance Criteria**:
- [x] **AC-US2-01**: `--reorganize-specs --execute` sets `multiProject.enabled = true` in `.specweave/config.json`
- [x] **AC-US2-02**: If `multiProject.enabled` is already `true`, the config is not rewritten
- [x] **AC-US2-03**: The dry-run output includes a line showing the config change that will be applied

---

### US-003: Verify Living-Docs Sync Post-Reorganization (P1)
**Project**: specweave

**As a** developer who just reorganized specs
**I want** `specweave sync-progress` to work correctly with the new per-project folder structure
**So that** future increments sync living docs to the right project folder

**Acceptance Criteria**:
- [x] **AC-US3-01**: After reorganization, `specweave sync-progress` finds and updates specs in per-project folders
- [x] **AC-US3-02**: New increments created after reorganization have their living docs placed in the correct project folder based on `**Project**:` field
- [x] **AC-US3-03**: The `specweave living-docs` builder recognizes the multi-project folder structure

---

### US-004: Test Coverage (P1)
**Project**: specweave

**As a** developer
**I want** unit tests for the reorganization logic
**So that** the migration is reliable and edge cases are handled

**Acceptance Criteria**:
- [x] **AC-US4-01**: Unit tests cover: project detection from spec.md, dry-run plan generation, folder move operations, config update, idempotency
- [x] **AC-US4-02**: Unit tests cover edge cases: no project field, cross-project specs, assets subfolder preservation, already-reorganized state
- [x] **AC-US4-03**: Tests use Vitest + vi.mock() pattern
- [x] **AC-US4-04**: Coverage for new reorganization module reaches 80%+

## Out of Scope

- Creating `.specweave/docs/` directories inside child repo git working trees (specs stay in umbrella root)
- Reorganizing non-spec docs (repos/, organization/, architecture/ folders stay as-is)
- Automated rollback of reorganization (manual restore from git history)
- Renaming FS-XXX IDs or changing feature numbering

## Dependencies

- 0219-multi-repo-migrate (completed -- provides migrate-to-umbrella CLI)
- Existing `LivingDocsSync` class with `autoDetectProjectIdSync`
- Existing `umbrella.childRepos[]` config for repo-to-project mapping

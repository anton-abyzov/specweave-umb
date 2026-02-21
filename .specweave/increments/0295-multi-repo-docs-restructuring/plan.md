# Implementation Plan: Multi-Repo Docs Restructuring

## Overview

Add a `--reorganize-specs` flag to the existing `migrate-to-umbrella` CLI command that redistributes FS-XXX living doc folders from a single centralized project directory to per-project directories. This involves:

1. A new `reorganizeSpecs()` function in the migration module
2. Project detection by parsing increment `spec.md` files for `**Project**:` fields
3. Physical folder moves within `.specweave/docs/internal/specs/`
4. Config.json update to enable `multiProject` mode

## Architecture

### Components

- **`migrate-to-umbrella.ts` (CLI)**: Extended with `--reorganize-specs` flag, routes to new handler
- **`umbrella-migrator.ts` (Core)**: New `reorganizeSpecs()` export function
- **`spec-project-mapper.ts` (New)**: Maps FS-XXX folders to projects by scanning increment specs
- **Config.json**: `multiProject.enabled` toggle

### Data Flow

```
1. CLI receives --reorganize-specs
2. spec-project-mapper scans:
   a. .specweave/docs/internal/specs/{currentProject}/FS-XXX/ folders
   b. .specweave/increments/*/metadata.json for feature_id → FS-XXX mapping
   c. .specweave/increments/*/spec.md for **Project**: field
3. Build move plan: { fsId, source, targetProject, targetPath }[]
4. Dry-run: display plan | --execute: move folders + update config
```

### Project Detection Strategy

For each FS-XXX folder:
1. Find the increment whose `feature_id` matches (e.g., feature_id=FS-282 → increment 0282-*)
2. Parse that increment's `spec.md` for `**Project**:` lines
3. If multiple projects found → copy to each
4. If no project found → keep in current location (fallback)
5. Map project name to umbrella childRepos config for path validation

### Config Update

```json
// Before
{ "multiProject": { "enabled": false } }

// After
{ "multiProject": { "enabled": true } }
```

## Technology Stack

- **Language**: TypeScript (ESM, `.js` extensions in imports)
- **Framework**: Node.js CLI (commander.js)
- **Testing**: Vitest + vi.mock()
- **Filesystem**: `fs/promises` for async file operations

**Architecture Decisions**:
- **Move within umbrella root only**: Specs stay under `.specweave/docs/internal/specs/` but in project-specific subdirectories. We do NOT move specs into child repo git working trees.
- **Reuse existing CLI**: Extend `migrate-to-umbrella` rather than creating a new command, since this is conceptually part of the umbrella migration workflow.
- **Scan increment specs for project**: The `**Project**:` field in spec.md user stories is the authoritative source for project ownership.

## Implementation Phases

### Phase 1: Project Mapper (T-001, T-002)
- Create `spec-project-mapper.ts` with functions to scan increments and build FS-XXX → project mappings
- TDD: Write tests first, then implement

### Phase 2: CLI + Core Migration Logic (T-003, T-004)
- Add `--reorganize-specs` flag to CLI
- Implement `reorganizeSpecs()` in umbrella-migrator with dry-run/execute modes
- Config.json multiProject toggle

### Phase 3: Verification (T-005, T-006)
- Verify living-docs sync works with new folder structure
- End-to-end test with actual reorganization

## Testing Strategy

- TDD mode: RED → GREEN → REFACTOR for each task
- Unit tests for project mapper (mock filesystem)
- Unit tests for reorganize logic (mock moves)
- Integration verification with living-docs sync

## Technical Challenges

### Challenge 1: Feature ID to Increment Mapping
**Problem**: FS-XXX IDs don't always match increment numbers directly (e.g., FS-282 may not be increment 0282).
**Solution**: Scan all `metadata.json` files for `feature_id` field. Fall back to numeric matching (FS-282 → 0282-*).
**Risk**: Some increments may lack `feature_id`. Mitigation: use glob pattern matching as fallback.

### Challenge 2: Cross-Project Specs
**Problem**: Some specs have user stories targeting multiple projects (e.g., 0277-multi-package-manager-docs targets vskill-platform, specweave, and vskill).
**Solution**: Copy the FS-XXX folder to each relevant project directory. The copy is acceptable because living docs are read-only views of increment data.
**Risk**: Duplicated content. Mitigation: symlinks considered but rejected for portability; copies are small.

### Challenge 3: Idempotency
**Problem**: Running `--reorganize-specs` twice should not fail or create duplicates.
**Solution**: Check if target already exists. If source and target are identical, skip. If target exists with same content, skip with info message.

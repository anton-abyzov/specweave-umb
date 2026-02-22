---
increment: 0302-umbrella-aware-docs-targeting
title: "Umbrella-Aware Project Targeting for Docs Command"
type: feature
priority: P1
status: planned
created: 2026-02-21
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Feature: Umbrella-Aware Project Targeting for Docs Command

## Overview

When `specweave docs` is run from an umbrella project root, it currently only sees the umbrella-level `.specweave/docs/` directory and fails silently if the user intended to work with a child repo's docs. Each child repo (e.g., specweave, vskill, vskill-platform) has its own `.specweave/docs/internal/` and `.specweave/docs/public/` directories that should be independently targetable.

The fix adds a `--project <id>` flag to all `specweave docs` subcommands (preview, build, validate, status) so that when run from an umbrella root, users can explicitly target a child repo's docs. Without the flag, the command detects umbrella mode and lists available repos with their doc counts, suggesting the `--project` flag.

## User Stories

### US-001: Target child repo docs via --project flag (P1)
**Project**: specweave

**As a** developer working in an umbrella project
**I want** to pass `--project <repo-id>` to any `specweave docs` subcommand
**So that** the command operates on the specified child repo's docs instead of the umbrella root

**Acceptance Criteria**:
- [x] **AC-US1-01**: `specweave docs preview --project vskill` resolves the docs path to `repositories/anton-abyzov/vskill/.specweave/docs/internal/` and launches preview from there
- [x] **AC-US1-02**: `specweave docs build --project specweave` builds docs from the specweave child repo's `.specweave/docs/`
- [x] **AC-US1-03**: `specweave docs validate --project vskill-platform` validates docs in the vskill-platform child repo
- [x] **AC-US1-04**: `specweave docs status --project vskill` shows status for the vskill child repo's docs only
- [x] **AC-US1-05**: When `--project <id>` is given but the ID doesn't match any `umbrella.childRepos[].id` in config.json, the command exits with a clear error listing valid repo IDs
- [x] **AC-US1-06**: The `--project` flag works with both `--scope internal` and `--scope public`

---

### US-002: Umbrella detection and guidance when no --project is given (P1)
**Project**: specweave

**As a** developer running `specweave docs` from an umbrella root without `--project`
**I want** the command to detect umbrella mode and show me which repos have docs
**So that** I know how to target the correct repo instead of getting a silent failure

**Acceptance Criteria**:
- [x] **AC-US2-01**: When umbrella mode is detected and no `--project` flag is given, preview/build/validate commands print a list of child repos with doc counts and suggest using `--project <id>`
- [x] **AC-US2-02**: If the umbrella root itself has docs (`.specweave/docs/internal/` exists), the command proceeds with those docs but also shows a notice about child repos being available via `--project`
- [x] **AC-US2-03**: If the umbrella root has NO docs AND no `--project` is given, the command exits with a clear message listing available child repos
- [x] **AC-US2-04**: `specweave docs status` (without --project) shows a combined view of umbrella root + all child repos (existing behavior enhanced)

---

### US-003: Update /sw:docs skill for umbrella awareness (P2)
**Project**: specweave

**As a** developer using `/sw:docs` from within an AI agent session in an umbrella project
**I want** the docs skill to detect umbrella mode and search/load docs from the correct child repo
**So that** I get relevant documentation regardless of which repo the docs belong to

**Acceptance Criteria**:
- [x] **AC-US3-01**: The `/sw:docs` skill dashboard shows docs from all child repos, grouped by repo
- [x] **AC-US3-02**: `/sw:docs <topic>` searches across all child repos' docs, not just the umbrella root
- [x] **AC-US3-03**: `/sw:docs --serve` guidance includes `--project <id>` usage for umbrella projects

## Functional Requirements

### FR-001: Umbrella Detection
The docs command must detect umbrella mode by reading `.specweave/config.json` and checking for `umbrella.enabled === true` with a non-empty `umbrella.childRepos` array.

### FR-002: Project Resolution
Given a `--project <id>`, resolve the child repo's path from `umbrella.childRepos[].path` where `id` matches. Compute the docs root as `path.resolve(projectRoot, childRepo.path)` and use that as the effective project root for all docs operations.

### FR-003: Backward Compatibility
- Single-repo projects (no umbrella config) must work exactly as before
- `--project` flag is ignored in non-umbrella projects (no error, just warning)
- Existing umbrella behavior for `docsStatusCommand` and `docsPreviewCommand` (child repo info display) is preserved

## Success Criteria

- All 5 docs subcommands (preview, build, validate, status, kill) support `--project` in umbrella mode
- Zero regressions for single-repo projects
- Unit test coverage >= 80% for new code paths

## Out of Scope

- Unified multi-repo docs preview (serving all repos simultaneously in one Docusaurus instance) -- that's a separate feature
- Creating `.specweave/docs/` directories in child repos that don't have them
- Interactive prompting / selection UI (TUI) for repo selection -- just CLI flag + guidance text

## Dependencies

- Existing `umbrella.childRepos` config structure in `.specweave/config.json`
- Existing `getUmbrellaChildRepoDocs()` function in `src/cli/commands/docs.ts`

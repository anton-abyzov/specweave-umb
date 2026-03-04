---
increment: 0416-umbrella-sync-consolidation
title: 'Umbrella sync consolidation: distributed routing and increment cleanup'
type: feature
priority: P1
status: completed
created: 2026-03-03T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Umbrella Sync Consolidation

## Problem Statement

SpecWeave's umbrella mode (`umbrella.enabled: true`) supports multiple repos under `repositories/org/repo-name/` with per-repo sync config (`childRepos[].sync`). However, the sync pipeline (LivingDocsSync, sync-progress, ExternalIssueAutoCreator) reads only the global `sync.github` config — all GitHub issues, Jira tickets, and ADO work items route to a single repo regardless of which project the increment belongs to. Additionally, orphaned increments and living docs have accumulated in nested repo `.specweave/` directories instead of the umbrella root, and type system gaps make the config schema difficult to validate or extend safely.

## Goals

- Enable per-repo routing of GitHub, Jira, and ADO sync targets via `childRepos[].sync` config
- Provide a safe CLI migration path to consolidate orphaned increments and living docs into the umbrella root
- Formalize the umbrella config type system and fix known project detection bugs

## User Stories

### US-001: Distributed External Sync Routing (P1)
**Project**: specweave
**As a** SpecWeave user with an umbrella project containing multiple repos
**I want** GitHub issues, Jira tickets, and ADO work items to route to the correct per-repo target
**So that** each project's increments are tracked in their own external tracker instead of all landing in one repo

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given `umbrella.syncStrategy` is `"distributed"` and an increment's project matches a `childRepos[].name`, when GitHub sync runs, then issues are created using that child repo's `sync.github.owner` and `sync.github.repo`
- [x] **AC-US1-02**: Given `umbrella.syncStrategy` is `"centralized"` or is absent, when sync runs, then all issues route to the global `sync.github` config (current behavior preserved)
- [x] **AC-US1-03**: Given `syncStrategy` is `"distributed"`, when `sync-progress` syncs AC checkboxes, then updates are sent to the correct per-project GitHub repo
- [x] **AC-US1-04**: Given `syncStrategy` is `"distributed"`, when `ExternalIssueAutoCreator` creates a Jira issue, then it uses the matched `childRepos[].sync.jira.projectKey`
- [x] **AC-US1-05**: Given `syncStrategy` is `"distributed"`, when `ExternalIssueAutoCreator` creates an ADO work item, then it uses the matched `childRepos[].sync.ado.project`

### US-002: Consolidate Nested Increments (P1)
**Project**: specweave
**As a** SpecWeave user migrating to umbrella mode
**I want** a CLI command that moves orphaned increments and living docs from nested repo `.specweave/` directories to the umbrella root
**So that** the umbrella root is the single source of truth for all increments across repos

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given the `--consolidate` flag is passed to `migrate-to-umbrella`, when the command runs, then it scans all `repositories/*/` paths for nested `.specweave/increments/` directories
- [x] **AC-US2-02**: Given an increment exists in a nested repo but not in the umbrella root, when `--consolidate --execute` runs, then the increment directory is moved to the umbrella root `.specweave/increments/`
- [x] **AC-US2-03**: Given an increment exists in both a nested repo and the umbrella root (duplicate), when `--consolidate --execute` runs, then the umbrella root version is kept and the nested copy is removed
- [x] **AC-US2-04**: Given living doc specs exist in a nested repo's `.specweave/docs/`, when `--consolidate --execute` runs, then they are moved to the umbrella root `.specweave/docs/`
- [x] **AC-US2-05**: Given `--consolidate` is run without `--execute`, when the command runs, then it prints a dry-run plan of all planned moves and deletions without making any changes

### US-003: Type System and Bug Fixes (P2)
**Project**: specweave
**As a** SpecWeave developer
**I want** the umbrella config schema to have proper TypeScript types and known detection bugs fixed
**So that** routing logic is type-safe and project resolution works correctly for all umbrella repos

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given the `ChildRepoConfig` type, when it is read, then it has a typed `sync` field of type `ChildRepoSyncConfig` with optional `github`, `jira`, and `ado` sub-fields (no `any` casts)
- [x] **AC-US3-02**: Given the `UmbrellaConfig` type, when it is read, then it has a `syncStrategy` field typed as `"centralized" | "distributed"` (optional, defaulting to `"centralized"`)
- [x] **AC-US3-03**: Given `multi-project-detector.ts` resolves project names, when it reads the config, then it reads the `name` field (not `displayName`) matching the actual config schema
- [x] **AC-US3-04**: Given `ProjectResolutionService.getAvailableProjects()` is called in an umbrella context where `umbrella.projects[]` is empty or absent, when it runs, then it falls back to enumerating `umbrella.childRepos[]` names as available projects

## Out of Scope

- Per-user-story routing within the same project (all user stories in one project go to the same external repo)
- Dashboard UI for distributed sync status
- ADO boards or areas configuration per child repo
- Automatic detection and migration without explicit `--consolidate` flag
- External trackers beyond GitHub, Jira, and ADO

## Technical Notes

### Key Files

- `src/sync/LivingDocsSync.ts` — reads global `sync.github`; needs `SyncTargetResolver` integration
- `src/sync/sync-progress.ts` — reads global GitHub config for AC checkbox sync; needs per-repo routing
- `src/sync/ExternalIssueAutoCreator.ts` — creates Jira/ADO items; needs per-repo project keys
- `src/umbrella/multi-project-detector.ts` — `displayName` bug to fix (should be `name`)
- `src/umbrella/ProjectResolutionService.ts` — `getAvailableProjects()` fallback gap
- `src/commands/migrate-to-umbrella.ts` — extend with `--consolidate` and `--execute` flags
- Config types file — add `ChildRepoSyncConfig`, update `ChildRepoConfig` and `UmbrellaConfig`

### Architecture Decisions

- Introduce a `SyncTargetResolver` helper: given an increment's project name and umbrella config, returns resolved `{ github, jira, ado }` targets. All three sync components call this helper.
- Fallback rule: if no matching `childRepos` entry is found for a project, fall back to global config to prevent breakage for increments with no project assignment.
- Dry-run is the default for `--consolidate`; destructive operations require explicit `--execute` flag.

### Dependencies

- Existing umbrella config: `umbrella.childRepos[].name`, `umbrella.childRepos[].sync`
- `migrate-to-umbrella` CLI command (existing, being extended)

## Success Metrics

- GitHub issues for `vskill` increments appear in the vskill repo, not specweave, when `syncStrategy: "distributed"`
- Zero orphaned increments remain in nested repo `.specweave/` after `--consolidate --execute`
- `ChildRepoConfig` and `UmbrellaConfig` pass TypeScript strict-mode with no `any` on sync fields

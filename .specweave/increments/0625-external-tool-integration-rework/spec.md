---
increment: 0625-external-tool-integration-rework
title: Rework External Tool Integration Architecture
type: feature
priority: P1
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Rework External Tool Integration Architecture

## Overview

Consolidate the fragmented external tool configuration (`umbrella`, `multiProject`, `projectMappings`) into a unified `workspace` section in config.json. Remove boolean flags — the repos array IS the config. Make the `**Project**:` field mandatory in all specs unconditionally. Rework the init and sync-setup CLI flows to use workspace semantics. Add a dashboard workspace page for visual repo-to-tool mapping management.

## Personas

- **Solo Developer**: Single-project user who shouldn't need to understand multi-project concepts
- **Workspace Owner**: Manages multiple repos in an umbrella workspace with external tool connections
- **CI/CD Pipeline**: Non-interactive consumer of config.json that needs deterministic behavior

## User Stories

### US-001: Workspace Config Schema (P1)
**Project**: specweave

**As a** workspace owner
**I want** a single `workspace` section in config.json that replaces both `umbrella` and `multiProject`
**So that** I have one canonical place to define my repos and their external tool connections

**Acceptance Criteria**:
- [x] **AC-US1-01**: New `workspace` section added to `SpecWeaveConfig` type with fields: `name` (string), `rootRepo` (optional sync config for umbrella's own GH/Jira/ADO connection), `repos` (array of `WorkspaceRepo`)
- [x] **AC-US1-02**: `WorkspaceRepo` type includes: `id`, `path`, `name?`, `prefix`, `techStack?`, `role?`, `sync: { github?, jira?, ado? }` — structurally equivalent to current `ChildRepoConfig` but without the legacy field names (`githubUrl`, `jiraProject`, `adoProject`)
- [x] **AC-US1-03**: `multiProject.enabled` and `umbrella.enabled` boolean flags are removed from the type system and config schema
- [x] **AC-US1-04**: Single-project mode is just a workspace with 0 or 1 repos — no special flag needed
- [x] **AC-US1-05**: JSON schema (`specweave-config.schema.json`) updated to reflect new workspace structure and reject old `umbrella`/`multiProject` keys with deprecation messages

### US-002: Config Migration (P1)
**Project**: specweave

**As a** user with an existing config.json
**I want** automatic migration from old `umbrella`/`multiProject`/`projectMappings` to the new `workspace` format
**So that** my existing setup keeps working after the upgrade

**Acceptance Criteria**:
- [x] **AC-US2-01**: Migration function reads `umbrella.childRepos` + `umbrella.sync` + `umbrella.projectName` and maps them to `workspace.repos[]` + `workspace.rootRepo` + `workspace.name`
- [x] **AC-US2-02**: Migration function reads `multiProject.projects` and merges into `workspace.repos[]`, deduplicating by id
- [x] **AC-US2-03**: Migration function reads `projectMappings` and injects matching sync targets into `workspace.repos[].sync`
- [x] **AC-US2-04**: Old keys (`umbrella`, `multiProject`, `projectMappings`) are removed from config after migration
- [x] **AC-US2-05**: Migration is idempotent — running it twice produces the same result
- [x] **AC-US2-06**: Config version bumped (e.g. `"3.0"`) to signal migration has occurred; `config-manager.ts` auto-migrates on load when version < 3.0

---

### US-003: Multi-Project Detection Refactor (P1)
**Project**: specweave

**As a** SpecWeave internal module (PM agent, sync coordinator, importers)
**I want** `multi-project-detector.ts` to read from `workspace.repos` instead of `umbrella.enabled`/`multiProject.enabled`
**So that** detection logic is consistent with the new config schema

**Acceptance Criteria**:
- [x] **AC-US3-01**: `detectMultiProjectMode()` checks `config.workspace.repos.length > 1` as the primary detection signal (replaces `umbrella.enabled` and `multiProject.enabled` checks)
- [x] **AC-US3-02**: `parseChildRepos()` reads from `workspace.repos` instead of `umbrella.childRepos`
- [x] **AC-US3-03**: Fallback detection (specs folders, sync profiles) remains as secondary signals for configs that haven't migrated yet
- [x] **AC-US3-04**: `MultiProjectDetectionResult.umbrellaEnabled` field deprecated; replaced by `hasWorkspace: boolean`

---

### US-004: Init Flow Workspace Awareness (P2)
**Project**: specweave

**As a** new user running `specweave init`
**I want** the init flow to explain the workspace concept and always write a `workspace` section
**So that** I understand the umbrella model and my config is future-proof from day one

**Acceptance Criteria**:
- [x] **AC-US4-01**: Init always writes `workspace: { name: <projectName>, repos: [] }` in config.json (replacing the current conditional `umbrella` block)
- [x] **AC-US4-02**: When repos are discovered via `scanUmbrellaRepos()`, they populate `workspace.repos[]` with proper `sync` sub-objects (empty by default)
- [x] **AC-US4-03**: Init no longer writes `umbrella.enabled`, `umbrella.childRepos`, or `multiProject` keys
- [x] **AC-US4-04**: `buildUmbrellaConfig()` helper renamed to `buildWorkspaceConfig()` and returns `{ workspace: WorkspaceConfig }` instead of `{ umbrella: UmbrellaConfig }`
- [x] **AC-US4-05**: Interactive init offers to connect the root workspace folder to a GitHub repo (populates `workspace.rootRepo.github`)

---

### US-005: Sync-Setup Workspace Walkthrough (P1)
**Project**: specweave

**As a** workspace owner running `specweave sync-setup`
**I want** a guided walkthrough that maps each workspace repo to its external tool targets
**So that** I can configure GitHub/Jira/ADO connections per repo without manually editing config.json

**Acceptance Criteria**:
- [x] **AC-US5-01**: After credential collection, wizard lists all repos from `workspace.repos[]` and asks user to map each to an external project (GitHub repo, Jira project, ADO project)
- [x] **AC-US5-02**: Umbrella root repo (`workspace.rootRepo`) is offered as the first mapping target
- [x] **AC-US5-03**: "Select all" shortcut available — maps all repos to the same external project when appropriate (e.g., monorepo with one GH repo)
- [x] **AC-US5-04**: Wizard writes resolved mappings into `workspace.repos[N].sync.{github|jira|ado}` in config.json
- [x] **AC-US5-05**: Bidirectional mapping: wizard asks sync direction (import, export, bidirectional) per provider per repo
- [x] **AC-US5-06**: Wizard validates each mapping (e.g., GitHub repo exists, Jira project key resolves) before writing config

---

### US-006: Mandatory Project Field in Specs (P1)
**Project**: specweave

**As a** PM agent writing spec.md
**I want** the `**Project**:` field to be unconditionally required on every user story
**So that** sync routing always has a clear target, regardless of workspace size

**Acceptance Criteria**:
- [x] **AC-US6-01**: `template-creator.ts` always emits `**Project**: {{RESOLVED_PROJECT}}` in spec templates — not gated by any `umbrella.enabled` or `multiProject` check
- [x] **AC-US6-02**: PM skill (`phases/02-spec-creation.md`) requires `**Project**:` field on every US unconditionally — no conditional "if umbrella" language
- [x] **AC-US6-03**: Architect skill requires `**Project**:` field on every component/module — no conditional language
- [x] **AC-US6-04**: `spec-validator` (used by `sw:validate`) flags missing `**Project**:` field as an error, not a warning
- [x] **AC-US6-05**: For single-project workspaces, the default project value is `workspace.name` (auto-resolved, no user burden)

---

### US-007: Import Flow Fix (P2)
**Project**: specweave

**As a** user importing issues from GitHub/Jira/ADO
**I want** imported items to have `**Project**:` per user story (not at the top of spec.md) and map to workspace repos
**So that** imported specs follow the same structure as natively created ones

**Acceptance Criteria**:
- [x] **AC-US7-01**: `markdown-generator.ts` places `**Project**: <repo-id>` inside each `### US-NNN` block, never as a top-level spec field
- [x] **AC-US7-02**: Import coordinator reads `workspace.repos[]` to resolve which repo an external item maps to (by matching GitHub owner/repo, Jira project key, or ADO project name)
- [x] **AC-US7-03**: When no workspace repo match is found, import defaults to `workspace.name` as the project value and emits a warning
- [x] **AC-US7-04**: `item-converter` preserves the `**Project**:` field when converting external items to SpecWeave user stories

---

### US-008: External Tool Resolver Migration (P1)
**Project**: specweave

**As a** sync coordinator resolving which external tool to use for a user story
**I want** `external-tool-resolver.ts` to read sync targets from `workspace.repos[].sync` instead of `projectMappings` + `umbrella.childRepos[].sync`
**So that** resolution logic has a single source of truth

**Acceptance Criteria**:
- [x] **AC-US8-01**: `ExternalToolResolver.resolveForProject()` looks up `workspace.repos.find(r => r.id === projectId).sync` as the primary resolution path
- [x] **AC-US8-02**: `workspace.rootRepo.sync` is used when `projectId` matches `workspace.name`
- [x] **AC-US8-03**: Fallback to `sync.defaultProfile` when no workspace repo match exists (unchanged behavior)
- [x] **AC-US8-04**: Legacy `projectMappings` lookup removed after config migration guarantees they're merged into `workspace.repos`

---

### US-009: Dashboard Workspace Page (P2)
**Project**: specweave

**As a** workspace owner using the SpecWeave dashboard
**I want** a dedicated Workspace page showing my repos and their external tool mappings
**So that** I can visualize and edit project-to-tool connections without touching config.json

**Acceptance Criteria**:
- [x] **AC-US9-01**: New `WorkspacePage.tsx` added to dashboard with route `/workspace`
- [x] **AC-US9-02**: Page displays a table: columns = repo id, repo name, GitHub mapping, Jira mapping, ADO mapping, sync status
- [x] **AC-US9-03**: Root repo (`workspace.rootRepo`) displayed as the first row with a visual distinction (e.g., badge "Root")
- [x] **AC-US9-04**: Each mapping cell is editable — clicking opens an inline editor to set/change the external target
- [x] **AC-US9-05**: "Add Repo" button appends a new entry to `workspace.repos[]` via API
- [x] **AC-US9-06**: Changes save via `PATCH /api/workspace/repos/:id` endpoint that writes to config.json
- [x] **AC-US9-07**: Sidebar navigation updated to include "Workspace" link

---

### US-010: Dashboard Workspace API (P2)
**Project**: specweave

**As a** dashboard frontend
**I want** REST API endpoints for reading and modifying workspace config
**So that** the Workspace page can perform CRUD operations

**Acceptance Criteria**:
- [x] **AC-US10-01**: `GET /api/workspace` returns `{ name, rootRepo, repos }` from config.json
- [x] **AC-US10-02**: `PATCH /api/workspace/repos/:id` updates a single repo's sync config and writes back to config.json
- [x] **AC-US10-03**: `POST /api/workspace/repos` adds a new repo entry to `workspace.repos[]`
- [x] **AC-US10-04**: `DELETE /api/workspace/repos/:id` removes a repo entry from `workspace.repos[]`
- [x] **AC-US10-05**: All write endpoints validate input (repo id uniqueness, valid sync target structure) and return 400 on validation failure
- [x] **AC-US10-06**: API routes registered in `router.ts` under the existing dashboard server

---

### US-011: Backward Compatibility Guard (P1)
**Project**: specweave

**As a** user who hasn't upgraded yet
**I want** SpecWeave to read old-format configs gracefully and auto-migrate them
**So that** the upgrade is seamless and I don't lose my configuration

**Acceptance Criteria**:
- [x] **AC-US11-01**: `config-manager.ts` detects config version < 3.0 and runs migration on load (lazy migration, writes back only when config is next saved)
- [x] **AC-US11-02**: All code paths that previously read `config.umbrella` now read `config.workspace` — no dual-read fallback in business logic
- [x] **AC-US11-03**: Migration logs a one-time info message: "Config migrated from v2.0 to v3.0 — umbrella/multiProject consolidated into workspace"
- [x] **AC-US11-04**: If migration encounters an unrecoverable error (corrupt JSON, conflicting IDs), it logs a warning and preserves the original config untouched

## Functional Requirements

### FR-001: Workspace Config Schema
The `workspace` section replaces `umbrella`, `multiProject`, and `projectMappings`. Structure:
```json
{
  "workspace": {
    "name": "my-workspace",
    "rootRepo": {
      "github": { "owner": "myorg", "repo": "umbrella" }
    },
    "repos": [
      {
        "id": "frontend",
        "path": "repositories/myorg/frontend",
        "prefix": "FE",
        "sync": {
          "github": { "owner": "myorg", "repo": "frontend" },
          "jira": { "projectKey": "FE" }
        }
      }
    ]
  }
}
```

### FR-002: Migration Rules
| Old Key | New Key |
|---------|---------|
| `umbrella.projectName` | `workspace.name` |
| `umbrella.childRepos[]` | `workspace.repos[]` |
| `umbrella.sync` | `workspace.rootRepo` |
| `umbrella.storyRouting` | Removed (routing uses `**Project**:` field) |
| `multiProject.projects` | Merged into `workspace.repos[]` |
| `projectMappings[id]` | Merged into `workspace.repos[id].sync` |

### FR-003: Project Field Resolution
For specs without explicit `**Project**:`, the default is `workspace.name`. This allows single-project users to never think about the field while keeping the routing key present.

## Success Criteria

- Zero config.json manual edits required during upgrade (auto-migration handles it)
- All existing sync operations (push, pull, create, close) work identically after migration
- Dashboard workspace page loads in < 500ms with 20 repos
- `specweave init` produces valid workspace config on fresh projects
- No dual-read paths remain in codebase — all reads go through `workspace`

## Out of Scope

- **New sync providers** (e.g., Linear, Notion) — this rework is structural, not adding providers
- **Workspace-level RBAC/permissions** — access control is not part of this increment
- **Real-time collaborative editing** of workspace config — single-writer model via dashboard
- **Cross-workspace sync** — syncing between multiple SpecWeave workspaces
- **Removing the `sync` top-level config** — only `umbrella`/`multiProject`/`projectMappings` are consolidated; the `sync` section (enabled, direction, profiles) remains as-is
- **Story routing automation** — the `storyRouting` config is removed; routing relies on explicit `**Project**:` field

## Dependencies

- Existing `ExternalToolResolver` (ADR-0211) — refactored, not replaced
- Dashboard server infrastructure (`router.ts`, SSE, Vite client build)
- Config manager's read-modify-write pattern for safe concurrent access
- PM and Architect skill markdown templates

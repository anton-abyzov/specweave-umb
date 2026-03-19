---
increment: 0625-external-tool-integration-rework
title: "Rework External Tool Integration Architecture"
generated: 2026-03-19
agent_domains:
  config-agent: T-001 to T-010
  consumers-agent: T-011 to T-020
  cli-agent: T-021 to T-030
  dashboard-agent: T-031 to T-040
  skills-agent: T-041 to T-045
---

# Tasks: Rework External Tool Integration Architecture

## Domain 1: Config Schema + Migration (config-agent)

### T-001: Define WorkspaceConfig, WorkspaceRepo, WorkspaceRepoSync types
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] completed
**Test**: Given `src/core/config/types.ts` is opened → When `WorkspaceConfig`, `WorkspaceRepo`, `WorkspaceRepoSync` interfaces are added → Then `WorkspaceRepo` has `id`, `path`, `prefix`, `name?`, `techStack?`, `role?`, `sync?: { github?, jira?, ado? }` fields; `WorkspaceConfig` has `name`, `rootRepo?`, `repos: WorkspaceRepo[]`; old `UmbrellaConfig.enabled` and `MultiProjectConfig.enabled` boolean flags are removed from types

### T-002: Add `workspace` field to SpecWeaveConfig, deprecate old fields
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04
**Status**: [x] completed
**Test**: Given `SpecWeaveConfig` in `types.ts` → When `workspace?: WorkspaceConfig` field is added and `umbrella?`, `multiProject?`, `projectMappings?` are marked `@deprecated` → Then TypeScript compiles without errors and existing code referencing deprecated fields gets deprecation warnings

### T-003: Update JSON schema (`specweave-config.schema.json`) for workspace structure
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05
**Status**: [x] completed
**Test**: Given `specweave-config.schema.json` → When `workspace` object schema is added with required `repos` array and `umbrella`/`multiProject` keys are marked deprecated → Then schema validation rejects configs with `umbrella.enabled: true` and accepts configs with only `workspace`; schema passes JSON Schema Draft-07 validation

### T-004: Implement `workspace-migrator.ts` — umbrella → workspace migration
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-04
**Status**: [x] completed
**Test**: Given a config with `umbrella.childRepos`, `umbrella.sync`, and `umbrella.projectName` → When `migrateToWorkspace(config)` is called → Then `workspace.repos` contains all entries from `umbrella.childRepos`, `workspace.rootRepo` equals `umbrella.sync`, `workspace.name` equals `umbrella.projectName`, and `umbrella` key is absent from returned config

### T-005: Implement `workspace-migrator.ts` — multiProject → workspace migration
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-04
**Status**: [x] completed
**Test**: Given a config with `multiProject.projects` containing repos not in `workspace.repos` → When `migrateToWorkspace(config)` is called → Then each `multiProject.projects` entry is merged into `workspace.repos[]`, deduplication by `id` preserves umbrella entries when both exist, and `multiProject` key is absent from returned config

### T-006: Implement `workspace-migrator.ts` — projectMappings → workspace.repos[].sync migration
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-04
**Status**: [x] completed
**Test**: Given a config with `projectMappings: { "frontend": { github: {...}, jira: {...} } }` → When `migrateToWorkspace(config)` is called → Then `workspace.repos.find(r => r.id === "frontend").sync` contains the merged GitHub and Jira config from `projectMappings`, and `projectMappings` key is absent from returned config

### T-007: Implement migration idempotency and version bump
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05, AC-US2-06
**Status**: [x] completed
**Test**: Given a config that has already been migrated (has `workspace` and no legacy keys, version `"3.0"`) → When `migrateToWorkspace(config)` is called a second time → Then the returned config is structurally identical to the input; version field reads `"3.0"` and calling migration on a v2.x config bumps it to `"3.0"`

### T-008: Hook migration into `ConfigManager.read()` and cleanup into `ConfigManager.write()`
**User Story**: US-011 | **Satisfies ACs**: AC-US11-01, AC-US11-02
**Status**: [x] completed
**Test**: Given `config-manager.ts` → When `ConfigManager.read()` is called with a file containing legacy `umbrella` keys → Then the returned config object has `workspace` populated (migration applied) and no `umbrella` key; when `ConfigManager.write()` is subsequently called, the written JSON contains only `workspace` and no legacy keys

### T-009: Migration logging and error handling
**User Story**: US-011 | **Satisfies ACs**: AC-US11-03, AC-US11-04
**Status**: [x] completed
**Test**: Given a config undergoing first-time migration → When `migrateToWorkspace()` completes successfully → Then a single info log line "Config migrated from v2.0 to v3.0 — umbrella/multiProject consolidated into workspace" is emitted; given a config with corrupt conflicting IDs → When migration fails → Then a warning is logged and the original config object is returned untouched

### T-010: Unit tests — all migration paths (umbrella-only, multiProject-only, both, idempotent, error)
**User Story**: US-002, US-011 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06, AC-US11-01, AC-US11-02, AC-US11-03, AC-US11-04
**Status**: [x] completed
**Test**: Given `workspace-migrator.test.ts` with fixtures for umbrella-only, multiProject-only, both-combined, already-migrated, and corrupt configs → When all test cases run → Then 100% coverage of migration logic achieved, all 7 key test scenarios from plan pass, and `npx vitest run` exits 0

---

## Domain 2+3: Core Consumers — Detector, Resolver, Project-Manager (consumers-agent)

### T-011: Rewrite `detectMultiProjectMode()` to check `workspace.repos.length > 1`
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01
**Status**: [x] completed
**Test**: Given a config with `workspace.repos` containing 2+ entries → When `detectMultiProjectMode()` is called → Then `MultiProjectDetectionResult.isMultiProject` is `true`; given `workspace.repos` with 0 or 1 entries → Then `isMultiProject` is `false`; old `umbrella.enabled` and `multiProject.enabled` checks are removed

### T-012: Rewrite `parseChildRepos()` to read from `workspace.repos`
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02
**Status**: [x] completed
**Test**: Given a config with `workspace.repos: [{ id: "frontend", path: "...", prefix: "FE" }]` → When `parseChildRepos()` is called → Then the returned array contains `WorkspaceRepo` entries matching `workspace.repos`; all references to `umbrella.childRepos` in the function are removed

### T-013: Update fallback detection (folder scan) as secondary strategy
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03
**Status**: [x] completed
**Test**: Given a config with no `workspace` section but a `repositories/` folder with multiple sub-repos → When `detectMultiProjectMode()` is called → Then folder scan fallback triggers and `isMultiProject` returns `true`; given a fully configured `workspace.repos`, folder scan is skipped entirely

### T-014: Deprecate `umbrellaEnabled`, add `hasWorkspace` to `MultiProjectDetectionResult`
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04
**Status**: [x] completed
**Test**: Given `multi-project-detector.ts` → When `MultiProjectDetectionResult` is updated → Then `hasWorkspace: boolean` field exists and is `true` when `workspace.repos` has entries; `umbrellaEnabled` field is marked `@deprecated` and always returns `false`; consuming code using `hasWorkspace` compiles correctly

### T-015: Update `ExternalToolResolver.resolveForProject()` to read `workspace.repos[].sync`
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-02
**Status**: [x] completed
**Test**: Given a config with `workspace.repos: [{ id: "frontend", sync: { github: { owner: "acme", repo: "fe" } } }]` → When `resolveForProject("frontend")` is called → Then result contains the GitHub sync config from `workspace.repos`; given `projectId === workspace.name` → Then `workspace.rootRepo.sync` is returned

### T-016: Update ExternalToolResolver fallback to `sync.defaultProfile`
**User Story**: US-008 | **Satisfies ACs**: AC-US8-03
**Status**: [x] completed
**Test**: Given a config where no `workspace.repos` entry matches the given `projectId` → When `resolveForProject("unknown")` is called → Then fallback reads `config.sync.defaultProfile` and returns those sync settings; behavior is identical to pre-refactor fallback

### T-017: Remove legacy `projectMappings` lookup from ExternalToolResolver
**User Story**: US-008 | **Satisfies ACs**: AC-US8-04
**Status**: [x] completed
**Test**: Given `external-tool-resolver.ts` after migration guarantees → When the file is inspected → Then zero references to `config.projectMappings` remain; integration test confirms resolver returns correct results for a migrated config with only `workspace` present

### T-018: Update `template-creator.ts` — `detectProjectFromCwd()` reads `workspace.repos`
**User Story**: US-006 | **Satisfies ACs**: AC-US6-05
**Status**: [x] completed
**Test**: Given a config with `workspace.repos` and CWD matching a repo path → When `detectProjectFromCwd()` is called → Then the matching `workspace.repos[].id` is returned as the project; given no match → Then `workspace.name` is returned as default

### T-019: Update `umbrella-detector.ts` — rename to workspace-aware, read `workspace.repos`
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02
**Status**: [x] completed
**Test**: Given `src/core/living-docs/umbrella-detector.ts` → When `loadFromWorkspaceConfig()` is implemented → Then it reads `config.workspace.repos` and returns the equivalent of the old `loadFromUmbrellaConfig()` result; detection strategy order: clone job config → workspace config → git directory scan

### T-020: Unit + integration tests for detector and resolver
**User Story**: US-003, US-008 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US8-01, AC-US8-02, AC-US8-03, AC-US8-04
**Status**: [x] completed
**Test**: Given test files for `multi-project-detector.test.ts` and `external-tool-resolver.test.ts` → When all test cases run including workspace-based detection, fallback paths, and resolver lookup → Then coverage ≥ 95% for both files and `npx vitest run` exits 0

---

## Domain 4: CLI Flows — Init, Sync-Setup, Import (cli-agent)

### T-021: Rename `scanUmbrellaRepos()` → `scanWorkspaceRepos()`, return `WorkspaceRepo[]`
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04
**Status**: [x] completed
**Test**: Given `src/cli/helpers/init/path-utils.ts` → When `scanWorkspaceRepos()` is implemented → Then it returns `WorkspaceRepo[]` (with `id`, `path`, `prefix`, `sync: {}`) instead of `ChildRepoConfig[]`; all callers updated to use new function name and return type

### T-022: Rename `buildUmbrellaConfig()` → `buildWorkspaceConfig()`, return `{ workspace: WorkspaceConfig }`
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04
**Status**: [x] completed
**Test**: Given `src/cli/commands/init.ts` → When `buildWorkspaceConfig()` is called with discovered repos → Then it returns `{ workspace: { name, rootRepo: {}, repos: WorkspaceRepo[] } }` instead of `{ umbrella: UmbrellaConfig }`; no references to `buildUmbrellaConfig` remain in codebase

### T-023: Init always writes `workspace` section to config.json (removes `umbrella` write)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-03
**Status**: [x] completed
**Test**: Given a fresh directory running `specweave init` non-interactively → When init completes → Then `config.json` contains `workspace: { name: <projectName>, repos: [] }` and contains no `umbrella`, `multiProject`, or `projectMappings` keys

### T-024: Init populates `workspace.repos[]` from `scanWorkspaceRepos()` results
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02
**Status**: [x] completed
**Test**: Given a directory with `repositories/org/repo-a` and `repositories/org/repo-b` sub-repos → When `specweave init` scans and builds config → Then `config.workspace.repos` contains two entries with `sync: {}` populated as empty defaults; no `umbrella.childRepos` key is written

### T-025: Init interactive mode offers GitHub connection for root workspace folder
**User Story**: US-004 | **Satisfies ACs**: AC-US4-05
**Status**: [x] completed
**Test**: Given interactive `specweave init` with a user providing GitHub owner/repo → When init completes → Then `config.workspace.rootRepo.github` contains `{ owner, repo }` matching user input; given user skips → Then `rootRepo` is omitted from config

### T-026: Sync-setup adds repo mapping step after credential collection
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03
**Status**: [x] completed
**Test**: Given `specweave sync-setup` with credentials validated and `workspace.repos` containing 3 repos → When the mapping step runs → Then wizard displays all 3 repos plus root repo for mapping; "Select all" shortcut maps all repos to the same external project when chosen

### T-027: Sync-setup writes resolved mappings to `workspace.repos[N].sync`
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04, AC-US5-05
**Status**: [x] completed
**Test**: Given user maps repo "frontend" to GitHub `acme/fe` with direction `bidirectional` → When wizard saves → Then `config.workspace.repos` entry with `id: "frontend"` has `sync.github: { owner: "acme", repo: "fe", direction: "bidirectional" }`; no writes occur to `umbrella.childRepos`

### T-028: Sync-setup validates each mapping before writing config
**User Story**: US-005 | **Satisfies ACs**: AC-US5-06
**Status**: [x] completed
**Test**: Given user enters a non-existent GitHub repo as mapping target → When wizard calls validation → Then an error message displays "Repository not found" and wizard returns to the mapping prompt without writing partial config; given valid targets → Then all validations pass and config is written atomically

### T-029: `markdown-generator.ts` places `**Project**:` inside each `### US-NNN` block
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01
**Status**: [x] completed
**Test**: Given `markdown-generator.ts` generating a spec from imported GitHub issues → When the spec markdown is produced → Then `**Project**: <repo-id>` appears inside each `### US-NNN` block (not as a top-level field); the generated markdown passes `spec-validator` without Project field errors

### T-030: Import coordinator resolves workspace repos; defaults to `workspace.name` on no match
**User Story**: US-007 | **Satisfies ACs**: AC-US7-02, AC-US7-03, AC-US7-04
**Status**: [x] completed
**Test**: Given `workspace.repos` with a repo having `sync.github: { owner: "acme", repo: "fe" }` and an import from `acme/fe` → When import coordinator runs → Then imported items get `**Project**: <repo-id>`; given no workspace repo matches the import source → Then `**Project**: <workspace.name>` is used and a warning logged

---

## Domain 5: Dashboard — API + React WorkspacePage (dashboard-agent)

### T-031: Implement `GET /api/workspace` endpoint
**User Story**: US-010 | **Satisfies ACs**: AC-US10-01
**Status**: [x] completed
**Test**: Given dashboard server running with a config containing `workspace` → When `GET /api/workspace` is called → Then response body is `{ name, rootRepo, repos }` matching config.json exactly; status 200 with `Content-Type: application/json`

### T-032: Implement `PATCH /api/workspace/repos/:id` endpoint
**User Story**: US-010 | **Satisfies ACs**: AC-US10-02
**Status**: [x] completed
**Test**: Given `PATCH /api/workspace/repos/frontend` with body `{ sync: { github: { owner: "acme", repo: "fe" } } }` → When endpoint handles request → Then `workspace.repos.find(r => r.id === "frontend").sync.github` is updated in config.json and response returns the updated repo object with status 200

### T-033: Implement `POST /api/workspace/repos` endpoint
**User Story**: US-010 | **Satisfies ACs**: AC-US10-03
**Status**: [x] completed
**Test**: Given `POST /api/workspace/repos` with body `{ id: "backend", path: "repositories/org/backend", prefix: "BE" }` → When endpoint handles request → Then new entry appended to `workspace.repos[]` in config.json; response returns the created repo object with status 201

### T-034: Implement `DELETE /api/workspace/repos/:id` endpoint
**User Story**: US-010 | **Satisfies ACs**: AC-US10-04
**Status**: [x] completed
**Test**: Given `DELETE /api/workspace/repos/frontend` → When endpoint handles request → Then the entry with `id: "frontend"` is removed from `workspace.repos[]` in config.json; response status 204; subsequent `GET /api/workspace` does not include the deleted entry

### T-035: Input validation for all write endpoints (400 on invalid input)
**User Story**: US-010 | **Satisfies ACs**: AC-US10-05
**Status**: [x] completed
**Test**: Given `POST /api/workspace/repos` with a duplicate `id` already in `workspace.repos` → When endpoint handles request → Then response status 400 with error message "Repo id already exists"; given `PATCH` with invalid sync structure → Then 400 returned with validation details

### T-036: Register workspace API routes in `router.ts`
**User Story**: US-010 | **Satisfies ACs**: AC-US10-06
**Status**: [x] completed
**Test**: Given dashboard `router.ts` → When workspace routes are registered under `/api/workspace` → Then all 4 endpoints (GET, PATCH, POST, DELETE) are discoverable via the router; existing routes remain unaffected; integration test confirms all routes respond correctly

### T-037: Create `WorkspacePage.tsx` with repo table (id, name, GitHub, Jira, ADO, sync status)
**User Story**: US-009 | **Satisfies ACs**: AC-US9-01, AC-US9-02, AC-US9-03
**Status**: [x] completed
**Test**: Given `WorkspacePage.tsx` renders with mock API response containing 3 repos + rootRepo → When page loads → Then table displays 4 rows (rootRepo first with "Root" badge, then 3 repos); columns: repo id, name, GitHub mapping, Jira mapping, ADO mapping, sync status; page accessible at `/workspace` route

### T-038: Implement inline editor for mapping cells
**User Story**: US-009 | **Satisfies ACs**: AC-US9-04
**Status**: [x] completed
**Test**: Given a rendered `WorkspacePage` → When user clicks a GitHub mapping cell → Then an inline input field appears with current value; when user types new value and presses Enter → Then `PATCH /api/workspace/repos/:id` is called with updated sync config and cell reverts to display mode showing new value

### T-039: Add "Add Repo" button and Workspace sidebar nav link
**User Story**: US-009 | **Satisfies ACs**: AC-US9-05, AC-US9-07
**Status**: [x] completed
**Test**: Given `WorkspacePage` and sidebar navigation → When "Add Repo" button is clicked → Then a form appears and on submit calls `POST /api/workspace/repos`; the sidebar contains a "Workspace" link that navigates to `/workspace`; sidebar link is highlighted when on the workspace page

### T-040: Integrate WorkspacePage with API — live data load and save
**User Story**: US-009 | **Satisfies ACs**: AC-US9-06
**Status**: [x] completed
**Test**: Given `WorkspacePage` connected to live dashboard server → When page mounts → Then `GET /api/workspace` is called and table populated with real config data in < 500ms for 20 repos; when inline editor saves → Then `PATCH /api/workspace/repos/:id` is called and config.json reflects changes

---

## Domain 6: Skills + Validation Enforcement (skills-agent)

### T-041: Update `template-creator.ts` to always emit `**Project**: {{RESOLVED_PROJECT}}`
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01
**Status**: [x] completed
**Test**: Given `template-creator.ts` generating spec templates for a single-project workspace → When `createIncrementTemplates()` runs → Then every `### US-NNN` block in the generated `spec.md` contains `**Project**: <workspace.name>`; no conditional `if umbrella.enabled` guard wraps the Project field emission

### T-042: Update PM skill to require `**Project**:` unconditionally in spec-creation phase
**User Story**: US-006 | **Satisfies ACs**: AC-US6-02
**Status**: [x] completed
**Test**: Given PM skill `phases/02-spec-creation.md` → When file is reviewed → Then all instructions for user story creation contain `**Project**:` as a required field with no conditional "if umbrella" or "if multi-project" language; spec generated by PM skill includes `**Project**:` on every US

### T-043: Update Architect skill to require `**Project**:` on every component unconditionally
**User Story**: US-006 | **Satisfies ACs**: AC-US6-03
**Status**: [x] completed
**Test**: Given Architect skill template files → When reviewed → Then component/module spec blocks always include `**Project**:` with no conditional guards; plan.md generated by Architect skill includes `**Project**:` on all components

### T-044: Update `spec-validator` to flag missing `**Project**:` as error (not warning)
**User Story**: US-006 | **Satisfies ACs**: AC-US6-04
**Status**: [x] completed
**Test**: Given a `spec.md` with a `### US-001` block missing `**Project**:` field → When `specweave validate` runs → Then output contains an ERROR (not warning) for "Missing **Project**: field in US-001"; exit code is non-zero; given all US blocks have `**Project**:` → Then no Project-related errors appear

### T-045: Implement `workspace.name` auto-resolution as default Project for single-project workspaces
**User Story**: US-006 | **Satisfies ACs**: AC-US6-05
**Status**: [x] completed
**Test**: Given a single-project workspace with `workspace.name: "my-app"` and no explicit `**Project**:` override → When `detectProjectFromCwd()` in `template-creator.ts` runs → Then default project value resolves to `"my-app"` automatically; user is never prompted to specify a project name in a single-repo workspace

---

## Domain 7: Config Reference Documentation + Deployment (docs-agent)

### T-046: Document every `workspace` field in `reference/configuration.md`
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US2-01
**Status**: [x] completed
**Test**: Given `docs-site/docs/reference/configuration.md` → When a new `## Workspace` section is added → Then every field of `WorkspaceConfig`, `WorkspaceRepo`, `WorkspaceRepoSync` is documented with: field name, type, required/optional, default, description, and example value; no deprecated `umbrella`/`multiProject` flags documented as active settings

### T-047: Remove deprecated `umbrella` and `multiProject` config documentation
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04
**Status**: [x] completed
**Test**: Given `configuration.md` after edit → When searching for "umbrella.enabled" or "multiProject.enabled" → Then these no longer appear as valid config options; a migration note explains old configs auto-upgrade to `workspace` format

### T-048: Update Quick Reference table and remove `umbrella`/`multiProject` enabled flags
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04
**Status**: [x] completed
**Test**: Given the Quick Reference table in `configuration.md` → When reviewed → Then rows for `umbrella.enabled` and `multiProject.enabled` are removed; the `workspace` section link is added to the table of contents

### T-049: Build and deploy docs to spec-weave.com
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01
**Status**: [x] completed
**Test**: Given `docs-site/` with updated configuration.md → When `npm run deploy` succeeds → Then spec-weave.com/docs/reference/configuration shows the new Workspace section with all fields; site is live and accessible

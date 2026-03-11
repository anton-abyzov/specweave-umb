---
increment: 0492-init-project-resolution-redesign
title: "Redesign specweave init project resolution"
type: feature
priority: P1
status: planned
created: 2026-03-11
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Redesign specweave init project resolution

## Problem Statement

The `specweave init` command has several path-resolution issues that cause confusion and maintenance burden:

1. **No-args ambiguity**: When called without arguments, `initCommand(projectName?)` receives `undefined`. The code at line 107 treats `!projectName` the same as `projectName === '.'` and uses CWD. While this accidentally works, the semantics are unclear -- the `undefined` and `'.'` cases follow the same branch but for different reasons. There is no explicit documentation or tests asserting that bare `specweave init` is equivalent to `specweave init .`.

2. **Explicit name always creates a subdirectory**: `specweave init my-project` resolves to `path.resolve(process.cwd(), projectName)` and creates a new folder. There is no way to say "initialize in CWD but use this name for the config" without the `.` notation plus a follow-up name prompt.

3. **Post-scaffold project setup only triggers on empty directories**: The repo-connect flow (clone GitHub repos, set up from scratch) only fires when both `.git` and `repositories/` are absent (line 404: `!hasGit && !hasRepos`). Users who `git clone` a repo first and then run `specweave init .` never see the project setup question, even though they may want to clone additional repos into an umbrella workspace.

4. **Duplicate umbrella config logic**: The umbrella config generation code (prefix deduplication, childRepos mapping) is duplicated verbatim at lines 361-380 and again at lines 420-437 in `init.ts`. Any change to the prefix algorithm must be applied in two places.

5. **Guard-clause error messages lack context**: `detectUmbrellaParent()` suggests "Run specweave init in the umbrella root instead" but does not show the resolved target path. When `detectSuspiciousPath()` fires, it shows the suspicious segment and suggested root but not the full resolved path, making it hard for the user to understand what went wrong.

## Goals

- Make `specweave init` (no args) unambiguously and explicitly initialize in CWD, equivalent to `specweave init .`
- Extract duplicated umbrella config logic into a reusable helper function
- Improve guard-clause error messages to include the resolved target path
- Relax the post-scaffold guard so project setup is available even when `.git` already exists

## User Stories

### US-001: No-args init uses CWD explicitly (P1)
**Project**: specweave

**As a** developer
**I want** `specweave init` with no arguments to explicitly initialize SpecWeave in my current directory
**So that** the behavior is predictable and I don't need to remember to pass `.`

**Acceptance Criteria**:
- [ ] **AC-US1-01**: Running `specweave init` (no args) in a project directory creates `.specweave/` in CWD, identical to `specweave init .`
- [ ] **AC-US1-02**: Running `specweave init` in the home directory is blocked with the existing safety error
- [ ] **AC-US1-03**: If the CWD directory name does not match the project name pattern (`/^[a-z0-9-]+$/`), the user is prompted for a config name (existing behavior preserved)
- [ ] **AC-US1-04**: Running `specweave init my-project` still creates a `my-project/` subdirectory with `.specweave/` inside it (no regression)
- [ ] **AC-US1-05**: The `undefined` and `'.'` code paths in `initCommand` are unified into a single branch with a comment explaining the intent

---

### US-002: Extract umbrella config helper (P2)
**Project**: specweave

**As a** maintainer of the specweave CLI
**I want** the umbrella config generation logic to exist in a single reusable function
**So that** prefix deduplication and childRepos mapping are consistent and changes don't require dual edits

**Acceptance Criteria**:
- [ ] **AC-US2-01**: A new exported function `buildUmbrellaConfig(discovery: UmbrellaDiscoveryResult, projectName: string)` exists in `cli/helpers/init/` and returns `{ umbrella: { enabled, projectName, childRepos }, repository: { umbrellaRepo: true } }`
- [ ] **AC-US2-02**: Both call sites in `init.ts` (initial scan at ~line 360 and post-clone re-scan at ~line 420) use the new helper instead of inline logic
- [ ] **AC-US2-03**: Prefix deduplication behavior is preserved: 3-char uppercase prefix from repo name, with numeric suffix disambiguation
- [ ] **AC-US2-04**: The helper is exported from the `cli/helpers/init/index.ts` barrel file

---

### US-003: Improved guard-clause error messages and relaxed post-scaffold guard (P2)
**Project**: specweave

**As a** user who runs init from the wrong directory or in an existing repo
**I want** error messages to show me the resolved target path, and to be offered the project setup prompt even in an existing git repo
**So that** I can quickly correct my command and set up my workspace flexibly

**Acceptance Criteria**:
- [ ] **AC-US3-01**: When `detectUmbrellaParent()` blocks init, the error message includes the resolved `targetDir` (e.g., "Cannot initialize at /path/to/target: inside an umbrella project at /path/to/umbrella")
- [ ] **AC-US3-02**: When `detectSuspiciousPath()` blocks init, the error message includes the full resolved path and the suspicious segment
- [ ] **AC-US3-03**: Post-scaffold project setup prompt is shown when `.git` exists but `repositories/` does not (condition relaxed from `!hasGit && !hasRepos` to `!hasRepos`)
- [ ] **AC-US3-04**: If the user selects "I have existing code here" or "Starting from scratch" in the project setup prompt, no repos are cloned (no regression)

## Functional Requirements

### FR-001: Unified path resolution
When `projectName` is `undefined`, treat it identically to `'.'` (CWD). Collapse the two branches in `initCommand` into one. The logic: if no name or `.`, use `process.cwd()` as `targetDir`; if an explicit name is given, resolve to `path.resolve(process.cwd(), projectName)` and create the subdirectory.

### FR-002: Extract `buildUmbrellaConfig()`
Create a helper function that accepts `UmbrellaDiscoveryResult` and `projectName`, and returns the umbrella and repository config fragments. Move the prefix-deduplication loop and childRepos mapping from `init.ts` into this function.

### FR-003: Relax post-scaffold guard
Change the post-scaffold condition from `!hasGit && !hasRepos` to `!hasRepos` so the project setup question appears even when `.git` exists. This enables users who cloned a repo to then add additional repos into an umbrella layout.

### FR-004: Enhanced error messages
Update the guard-clause blocks for `detectUmbrellaParent()` and `detectSuspiciousPath()` to include the resolved `targetDir` in the error output.

## Success Criteria

- All existing `specweave init` tests pass without modification
- New unit tests cover: no-args CWD resolution, `buildUmbrellaConfig()` helper, relaxed post-scaffold guard
- Zero duplicate lines for umbrella config generation in `init.ts`
- Error messages for guard clauses include resolved paths

## Out of Scope

- Changing the `specweave init <name>` subdirectory-creation behavior (it stays as-is)
- Modifying the `specweave migrate-to-umbrella` command
- Changing language selection, adapter detection, or plugin installation flows
- Adding new CLI flags or options to the init command
- Refactoring the smart-reinit flow
- Changes to `find-project-root.ts` or `hooks/platform.ts` (runtime resolution, not init-time)
- Changes to the deprecated `resolve-structure.ts` command

## Dependencies

- `src/cli/helpers/init/path-utils.ts` -- umbrella scanning functions, types
- `src/cli/helpers/init/repo-connect.ts` -- post-scaffold flow
- `src/cli/helpers/init/types.ts` -- `UmbrellaDiscoveryResult`, `DiscoveredRepo`
- `src/cli/commands/init.ts` -- main init command

## Technical Notes

- The `initCommand` function signature `(projectName?: string, options?: InitOptions)` remains unchanged; the behavior change is internal to the function body
- `findProjectRoot()` in `utils/find-project-root.ts` and `hooks/platform.ts` are NOT affected -- they resolve at runtime, not during init
- The `resolve-structure.ts` command is deprecated (v1.0.415) and is not touched by this change
- `detectProvider()`, `promptSmartReinit()`, and `installAllPlugins()` helpers are not modified
- The prefix deduplication algorithm: take first 3 chars of repo name, uppercase; if collision, take first 2 chars + incrementing numeric suffix

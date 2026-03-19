---
increment: 0581-init-always-multi-repo
title: Simplify init to always use repositories/owner/repo structure
type: change-request
priority: P1
status: completed
created: 2026-03-18T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Simplify Init to Always Use repositories/owner/repo Structure

## Problem Statement

SpecWeave init currently presents a 4-way question ("How would you like to set up your code?") that forces users to predict their future repository topology upfront. Single-repo users who later add repositories must run `migrate-to-umbrella`, a 505-line command that rewires config, moves files, and regularly confuses users. The dual-mode system (`isMultiRepo` branching, `-single`/`-multirepo` type suffixes, `single-project-migrator.ts`) creates maintenance burden and inconsistent behavior. A single repo is simply an umbrella workspace with one repository -- not a fundamentally different mode.

## Goals

- Eliminate the single vs multi-repo distinction from init flow entirely
- Ensure every new workspace starts with `repositories/` structure from day one
- Remove migration tooling that exists only because of the dual-mode split
- Simplify config types by removing mode-specific suffixes and flags
- Update all documentation to reflect the unified model

## Rationale

1. **Growth without migration** -- start with 1 repo, add more by just cloning
2. **No prediction required** -- users do not guess future org topology during init
3. **Consistent paths** -- every tool, CI script, agent template uses the same structure
4. **Real-world pattern** -- companies grow: stats repos, Obsidian vaults, shared configs
5. **Umbrella project mapping is orthogonal** -- external tool integration configured separately

## User Stories

### US-001: Simplified Init Flow
**Project**: specweave
**As a** SpecWeave user
**I want** init to ask only which repositories to connect instead of presenting a 4-way setup question
**So that** I can start working immediately without predicting my future repository topology

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a user runs `specweave init`, when the init wizard starts, then no "How would you like to set up your code?" 4-way question is presented
- [x] **AC-US1-02**: Given a user runs `specweave init`, when prompted for repositories, then the prompt asks "Which repositories to connect?" accepting clone URLs, patterns, or "add later via specweave get"
- [x] **AC-US1-03**: Given init completes, when the workspace is created, then a `repositories/` directory exists at the workspace root
- [x] **AC-US1-04**: Given init completes, when the summary banner is displayed, then it shows "Workspace (N repositories)" instead of "Single repository"
- [x] **AC-US1-05**: Given init completes, when next-steps are displayed, then `specweave get` is shown and `migrate-to-umbrella` is never shown

---

### US-002: Remove migrate-to-umbrella Command
**Project**: specweave
**As a** SpecWeave maintainer
**I want** the migrate-to-umbrella command removed
**So that** there is no dead code supporting a migration path that no longer applies

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given the codebase after this change, when examining `src/cli/commands/`, then `migrate-to-umbrella.ts` does not exist
- [x] **AC-US2-02**: Given the codebase after this change, when examining `bin/specweave.js`, then no registration block for `migrate-to-umbrella` exists
- [x] **AC-US2-03**: Given a user runs `specweave migrate-to-umbrella`, when the CLI processes the command, then it prints "This command has been removed. Use `specweave get` to add repositories." and exits with code 0
- [x] **AC-US2-04**: Given the codebase after this change, when examining `src/consolidation/`, then `consolidation-engine.ts` and `spec-project-mapper.ts` still exist

---

### US-003: Remove resolve-structure Command
**Project**: specweave
**As a** SpecWeave maintainer
**I want** the deprecated resolve-structure command removed
**So that** unused deprecated code does not remain in the codebase

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given the codebase after this change, when examining `src/cli/commands/`, then `resolve-structure.ts` does not exist
- [x] **AC-US3-02**: Given the codebase after this change, when examining `bin/specweave.js`, then no registration block for `resolve-structure` exists

---

### US-004: Config and Type Simplification
**Project**: specweave
**As a** SpecWeave maintainer
**I want** config types cleaned of single/multi mode artifacts
**So that** the type system reflects the unified architecture without dead branches

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given the `RepositoryHosting` type in `src/cli/helpers/init/types.ts`, when inspected after this change, then no values contain `-single` or `-multirepo` suffixes
- [x] **AC-US4-02**: Given the `RepositoryHosting` type in `src/cli/helpers/issue-tracker/types.ts`, when inspected after this change, then no values contain `-single` or `-multirepo` suffixes
- [x] **AC-US4-03**: Given the `RepoArchitecture` type in `src/core/repo-structure/repo-structure-manager.ts`, when inspected after this change, then `'single'` is not a valid value
- [x] **AC-US4-04**: Given the `SetupArchitecture` type in `src/core/repo-structure/setup-state-manager.ts`, when inspected after this change, then `'single'` is not a valid value
- [x] **AC-US4-05**: Given the codebase after this change, when examining `src/core/config/`, then `single-project-migrator.ts` does not exist

---

### US-005: Documentation Updates
**Project**: specweave
**As a** SpecWeave user reading documentation
**I want** all docs to describe the unified repository model without references to single vs multi modes
**So that** documentation matches the actual init behavior

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given `CLAUDE.md` in the specweave repo, when inspected after this change, then the "Multi-repo" section describes a single unified model without single/multi distinction
- [x] **AC-US5-02**: Given the `AGENTS.md` template, when inspected after this change, then the section formerly titled "Multi-Repo Structure" is titled "Repository Structure"
- [x] **AC-US5-03**: Given `docs-site/docs/guides/multi-project-setup.md`, when inspected after this change, then it describes the unified repositories/ structure without migration instructions
- [x] **AC-US5-04**: Given `docs-site/docs/guides/command-reference-by-priority.md`, when inspected after this change, then `migrate-to-umbrella` does not appear
- [x] **AC-US5-05**: Given `docs-site/docs/getting-started/installation.md`, when inspected after this change, then the init flow description matches the new simplified prompt sequence

---

### US-006: Test Updates
**Project**: specweave
**As a** SpecWeave maintainer
**I want** tests rewritten to validate the unified init flow
**So that** the test suite covers the new behavior and does not test removed code paths

**Acceptance Criteria**:
- [x] **AC-US6-01**: Given `tests/unit/cli/commands/init-multirepo.test.ts`, when inspected after this change, then it tests the new simplified flow where init always creates `repositories/`
- [x] **AC-US6-02**: Given the codebase after this change, when examining `tests/unit/cli/commands/`, then `migrate-to-umbrella.test.ts` does not exist
- [x] **AC-US6-03**: Given a test for init, when init completes, then the resulting config does not contain `multiProject.enabled`
- [x] **AC-US6-04**: Given a test for init, when init completes and `specweave get <url>` is run, then the repository is cloned into `repositories/owner/repo`

## Out of Scope

These are explicitly deferred to Stage 2:
- Replacing all 40+ `umbrella.enabled` check sites across the codebase
- Renaming `umbrella` to `workspace` in config schema
- Building a migration utility for existing single-repo users
- Changes to `consolidation-engine.ts` or `spec-project-mapper.ts`

## Non-Functional Requirements

- **Compatibility**: Existing workspaces initialized before this change continue to function without modification
- **Performance**: No change to init execution time beyond removing unnecessary prompts (fewer I/O waits)
- **Security**: No changes to credential handling or authentication flows

## Edge Cases

- **User selects "add later"**: Init completes with empty `repositories/` directory; `specweave get` works on next invocation
- **User pastes invalid clone URL**: Existing URL validation still applies; init does not regress error handling
- **Config files from pre-change installs**: Old configs with `multiProject.enabled: true` or `repository.umbrellaRepo: true` are tolerated at read time (no crash), but not written during new init
- **Invoking removed commands**: `migrate-to-umbrella` and `resolve-structure` show deprecation messages and exit cleanly

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Docs referencing single/multi missed during update | 0.4 | 3 | 1.2 | Grep-based sweep for "single.repo", "multi.repo", "isMultiRepo" across all doc files |
| Old configs with removed flags cause runtime errors | 0.3 | 7 | 2.1 | Read-time tolerance: ignore unknown/deprecated flags rather than failing |
| Downstream tools depend on `-single`/`-multirepo` type suffixes | 0.2 | 6 | 1.2 | Search all repos in umbrella for suffix usage before removing |

## Technical Notes

### Dependencies
- `src/cli/commands/init.ts` -- primary init flow
- `src/cli/helpers/init/types.ts` -- RepositoryHosting type
- `src/cli/helpers/issue-tracker/types.ts` -- RepositoryHosting type (duplicated)
- `src/core/repo-structure/repo-structure-manager.ts` -- RepoArchitecture type
- `src/core/repo-structure/setup-state-manager.ts` -- SetupArchitecture type
- `bin/specweave.js` -- command registration

### Constraints
- Must not break existing umbrella workspaces
- `consolidation-engine.ts` and `spec-project-mapper.ts` must be preserved
- Stage 2 scope boundaries must be respected

### Architecture Decisions
- Single repo is modeled as an umbrella workspace with one repository, not a separate mode
- `umbrella.enabled` is always set to `true` during init; the flag itself is not removed (Stage 2)
- `multiProject.enabled` is no longer written but tolerated if present in existing configs
- Removed commands emit deprecation messages rather than being silently unregistered

## Success Metrics

- Init flow asks 0 questions about repository architecture mode
- `repositories/` directory exists in 100% of new workspaces
- `migrate-to-umbrella.ts` and `resolve-structure.ts` deleted (net code reduction ~537 lines)
- All documentation references to single vs multi distinction updated
- Existing test suite passes after rewrite with no skipped tests

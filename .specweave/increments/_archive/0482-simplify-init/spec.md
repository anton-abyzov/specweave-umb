---
increment: 0482-simplify-init
title: Radically Simplify specweave init
type: feature
priority: P1
status: completed
created: 2026-03-10T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Radically Simplify specweave init

## Problem Statement

The current `specweave init` command is 1,242 lines with 41 helper modules totaling ~13,000 lines. It handles brownfield/greenfield classification, repository hosting setup (GitHub/ADO/Bitbucket), umbrella cloning, multi-project folder creation, issue tracker setup, and complex wizard flows -- all in one command. This makes init slow, confusing, and brittle. Most of these concerns already have dedicated commands (`sync-setup`, `migrate-to-umbrella`, `import`).

## Goals

- Reduce init.ts from 1,242 to ~300 lines
- Remove ~2,649 lines total across 7+ files
- Complete init in < 10 seconds with 0-2 prompts
- Zero backward compatibility breaks -- existing configs keep working
- Guide users to the right follow-up commands post-init

## User Stories

### US-001: Simplified Init Command (P1)
**Project**: specweave

**As a** developer
**I want** `specweave init` to quickly scaffold the project structure without asking about external tools
**So that** I can start using SpecWeave immediately without a lengthy wizard

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a directory without `.specweave/`, when running `specweave init`, then `.specweave/` directory, config.json, CLAUDE.md, AGENTS.md, and .gitignore are created in < 10 seconds
- [x] **AC-US1-02**: Given any init invocation, when the command runs, then no prompts appear about greenfield/brownfield, repository hosting, issue trackers, or repo cloning
- [x] **AC-US1-03**: Given a directory with a `.git/config` containing a remote URL, when running init, then the adapter (Claude/Cursor/Generic) and git provider (GitHub/ADO/Bitbucket) are auto-detected silently without prompting
- [x] **AC-US1-04**: Given the `--quick` flag, when running init, then zero interactive prompts are shown
- [x] **AC-US1-05**: Given interactive mode (no `--quick`), when running init, then at most 2 prompts appear: language selection (if non-English locale detected) and adapter confirmation
- [x] **AC-US1-06**: Given the generated config.json, when inspecting its contents, then it contains only core fields: project name, adapter, repository.provider, language, hooks, auto, lsp, and testing defaults -- no multiProject, issueTracker, projectMaturity, or structureDeferred fields

---

### US-002: Guided Next Steps (P1)
**Project**: specweave

**As a** developer
**I want** clear guidance after init on what commands to run next
**So that** I know how to configure external tools and start working

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given a successful init, when the completion output is displayed, then it shows 3 follow-up commands: `specweave sync-setup`, `specweave increment "feature"`, and `specweave migrate-to-umbrella` with brief descriptions
- [x] **AC-US2-02**: Given a successful init, when the summary banner is displayed, then it shows the project name, detected adapter, detected provider, and language
- [x] **AC-US2-03**: Given any adapter (Claude, Cursor, Generic), when next steps are displayed, then verbose adapter-specific instruction blocks are removed in favor of the universal command list
- [x] **AC-US2-04**: Given a successful init, when the output is displayed, then documentation and GitHub links are still present

---

### US-003: Simplified Config Schema (P1)
**Project**: specweave

**As a** developer
**I want** the generated config.json to be minimal and clean
**So that** it is not cluttered with unconfigured external tool settings

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given a fresh init, when config.json is generated, then it contains no `multiProject`, `issueTracker`, `projectMaturity`, or `structureDeferred` fields
- [x] **AC-US3-02**: Given a fresh init, when config.json is generated, then it contains no sync profiles or provider-specific connection settings
- [x] **AC-US3-03**: Given a directory with a GitHub remote in `.git/config`, when init runs, then `repository.provider` is set to "github" and `repository.organization` is populated from the remote URL
- [x] **AC-US3-04**: Given an existing config.json that contains sync profiles, umbrella config, or issueTracker sections, when that config is loaded by any SpecWeave command, then it still works correctly (backward compatible via optional chaining)

---

### US-004: Clean Summary Banner (P2)
**Project**: specweave

**As a** developer
**I want** a concise init completion summary
**So that** I can quickly verify what was configured

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given a successful init, when the summary banner renders, then it does not display tracker, repoCount, isGreenfield, hasPendingClones, syncPermissions, projectMaturity, or structureDeferred fields
- [x] **AC-US4-02**: Given a successful init, when the summary banner renders, then it shows: project name, adapter, provider, language, and defaults (testing, quality gates, LSP, git hooks)
- [x] **AC-US4-03**: Given the `SummaryBannerOptions` interface, when inspected, then removed fields (tracker, repoCount, isGreenfield, hasPendingClones, externalPluginInstalled, syncPermissions, projectMaturity, structureDeferred) are no longer present

---

### US-005: Barrel and Type Cleanup (P2)
**Project**: specweave

**As a** maintainer
**I want** unused init types and barrel exports cleaned up
**So that** the codebase is not cluttered with dead code from removed init flows

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given `types.ts`, when inspected, then `ProjectMaturity` and `RepositoryHosting` types (and REPO_FETCH_LIMITS constant) are removed
- [x] **AC-US5-02**: Given `index.ts` barrel, when inspected, then exports for `setupRepositoryHosting`, `promptTestingConfig`, `promptTranslationConfig`, `promptBrownfieldAnalysis`, `promptDeepInterviewConfig`, `promptQualityGatesConfig`, `promptAndRunExternalImport`, and their associated types are removed
- [x] **AC-US5-03**: Given `index.ts` barrel, when inspected, then `detectProvider` is exported from `./provider-detection.js`
- [x] **AC-US5-04**: Given the full test suite (`npx vitest run`), when run after all removals, then no tests fail due to missing imports or broken references
- [x] **AC-US5-05**: Given `npm run build`, when run after all changes, then TypeScript compiles cleanly with zero errors

## Functional Requirements

### FR-001: Simplified Init Flow
The rewritten `initCommand()` follows this sequence:
1. CI/quick detection
2. Language selection (keep existing logic)
3. Path resolution + all guards (umbrella, suspicious path, nested checks)
4. Smart re-init detection
5. Adapter auto-detection (auto-detect, confirm only in interactive mode)
6. Provider auto-detection from `.git/config` (silent, no prompt, uses `detectProvider()`)
7. Create directory structure
8. Copy instruction templates (CLAUDE.md, AGENTS.md)
9. Create config.json (simplified -- no maturity, no structureDeferred, provider from detection)
10. Install plugins / Claude setup
11. Git init if needed
12. Smart defaults
13. Git hooks
14. LSP auto-enable
15. Simplified summary banner
16. Guided next-steps output

### FR-002: Removed Init Responsibilities
The following are explicitly removed from init and handled by dedicated commands:
- External tool setup (GitHub/JIRA/ADO connections) --> `specweave sync-setup`
- Repository cloning (ADO/GitHub/Bitbucket) --> `specweave migrate-to-umbrella`
- Issue import --> `specweave import`
- Multi-project folder creation --> `specweave migrate-to-umbrella`
- Brownfield/greenfield classification --> removed entirely (no longer needed)

### FR-003: Deprecation of resolve-structure
The `resolve-structure` command receives a deprecation warning since init no longer sets `structureDeferred`. The command still functions for existing projects.

## Out of Scope

- Deleting helper modules (repository-setup.ts, greenfield-detection.ts, brownfield-analysis.ts) -- they stay in the codebase for use by other commands
- Changing `sync-setup`, `migrate-to-umbrella`, or `import` commands
- Modifying smart-reinit, smart-defaults, or plugin installer logic
- Changing how existing config.json files are read by other commands

## Technical Notes

- All files are in `repositories/anton-abyzov/specweave/`
- Full implementation plan with file-by-file diffs at: plan.md (this increment)
- Implementation order: directory-structure.ts -> next-steps.ts -> summary-banner.ts -> types.ts -> index.ts -> init.ts -> config.json.template -> resolve-structure.ts -> init.test.ts
- `detectProvider()` already exists in `provider-detection.ts` -- just needs to be exported and imported by init.ts

## Success Metrics

- init.ts reduced from 1,242 to ~300 lines
- Total lines removed: ~2,649 across all files
- `specweave init . --quick` completes in < 10 seconds with zero prompts
- `npx vitest run` passes with zero failures
- `npm run build` compiles cleanly
- No backward compatibility regressions with existing config files

## Dependencies

- `provider-detection.ts` must export `detectProvider()` (currently internal)
- Existing `sync-setup` command must handle all external tool configuration (already does)
- Existing `migrate-to-umbrella` command must handle repo cloning and multi-project setup (already does)

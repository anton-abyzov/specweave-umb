---
increment: 0640-init-ux-nonempty-workspace
title: Rework specweave init UX for non-empty folders and workspace clarity
type: feature
priority: P1
status: completed
created: 2026-03-20T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Rework specweave init UX for non-empty folders and workspace clarity

## Problem Statement

`specweave init` has three UX gaps that confuse new users:

1. **Non-empty folder blindspot** — Running init in a folder with existing source code silently proceeds with a brief "Directory contains N file(s)" message. Users don't understand the umbrella model or how to structure their workspace. They need clear options: start fresh, restructure in-place, or continue anyway.

2. **GitHub connection buried** — The root workspace's own GitHub repo question appears late in the flow (after repo cloning), catching users off guard. It should be the first question after language/adapter selection, with a clear explanation of what "root repo" means.

3. **Silent failure on bad repo input** — Entering `anton-abyzov` (org-only, missing `/repo`) passes through `parseRepoInput()` silently returning an empty array. No error, no guidance. Users think something is broken.

## Goals

- Guide users through workspace setup when init detects existing source files
- Make the umbrella workspace model understandable to first-time users
- Move GitHub root repo connection to the front of the init flow
- Validate repository input format and provide actionable error messages
- Support multiple source acquisition methods: GitHub clone, local path copy, sibling folder detection

## User Stories

### US-001: Non-empty folder detection and workspace setup (P1)
**Project**: specweave

**As a** developer running `specweave init` in an existing repository
**I want** clear guidance on how to set up the workspace around my code
**So that** I understand the umbrella model and choose the right setup path

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a directory with 1+ non-hidden files and no `.specweave/` folder, when `specweave init .` runs, then a workspace setup menu appears with 3 options: "Start empty (recommended)", "Restructure here", and "Continue in-place"
- [x] **AC-US1-02**: Given the user selects "Start empty", when the option is chosen, then init explains the `repositories/{org}/{repo}` structure and offers sub-options: clone from GitHub, copy from local path, or add later
- [x] **AC-US1-03**: Given the user selects "Copy from local path" under "Start empty", when the user provides a valid directory path, then init copies the directory contents into `repositories/{org}/{repo-name}/` using the detected or prompted org/name
- [x] **AC-US1-04**: Given the user selects "Restructure here", when the directory has a git remote, then init auto-detects org from the git remote URL and proposes `repositories/{org}/{repo-name}/` as the target, warning about symlinks, CI paths, and relative imports
- [x] **AC-US1-05**: Given the user selects "Restructure here", when no git remote exists, then init prompts for org name and repo name with sensible defaults from the directory name and any `package.json` author/name fields

### US-002: Restructure safety warnings (P1)
**Project**: specweave

**As a** developer choosing to restructure an existing repo in-place
**I want** clear warnings about what might break
**So that** I can make an informed decision and commit my work first

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given the user selects "Restructure here", when there are uncommitted git changes, then init displays a warning recommending `git commit` first and asks for confirmation to proceed
- [x] **AC-US2-02**: Given the user confirms restructure, when the move completes, then all non-hidden files and directories (except `.git`, `.specweave`, `repositories/`) are moved into `repositories/{org}/{repo-name}/`
- [x] **AC-US2-03**: Given restructure is selected, when the warning is shown, then it explicitly mentions risks: symlinks may break, CI paths may need updating, relative imports from outside the repo will fail
- [x] **AC-US2-04**: Given the user selects "Continue in-place", when chosen, then init proceeds with the current non-destructive behavior (creates `.specweave/` alongside existing files) with no file moves

### US-003: Root repo GitHub connection as first question (P1)
**Project**: specweave

**As a** developer setting up a SpecWeave workspace
**I want** the GitHub repo connection question for the workspace root to appear early
**So that** I understand the umbrella model before being asked about child repositories

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given `specweave init` runs interactively with no existing `.specweave/`, when the adapter is confirmed, then the next prompt asks whether to connect the workspace root to a GitHub repo, with an explanation: "This umbrella folder itself can be tracked as a GitHub repository for workspace-level config and specs"
- [x] **AC-US3-02**: Given the user confirms GitHub connection, when owner and repo are provided, then `config.workspace.rootRepo.github` is set in config.json before any child repo prompts
- [x] **AC-US3-03**: Given the user declines GitHub connection, when they press enter or select "no", then init proceeds to child repository setup without setting rootRepo
- [x] **AC-US3-04**: Given the init is running in CI mode or `--quick` mode, when the GitHub connection prompt would appear, then it is skipped silently (non-interactive)

### US-004: Repository input validation (P1)
**Project**: specweave

**As a** developer entering repository identifiers during init
**I want** clear validation errors when my input format is wrong
**So that** I can fix the input immediately instead of seeing silent failures

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given the user enters `anton-abyzov` (org-only, no slash), when `parseRepoInput()` processes it, then it returns an error descriptor `{ type: 'org-only', value: 'anton-abyzov' }` instead of silently skipping
- [x] **AC-US4-02**: Given `parseRepoInput()` returns an org-only error, when the prompt loop handles it, then it displays: "'{value}' looks like an org name. Use '{value}/repo-name' format, or '{value}/*' to clone all repos from this org"
- [x] **AC-US4-03**: Given the user enters a completely invalid string (not a URL, not org/repo, not a pattern), when processed, then a message displays: "Could not parse '{value}' — expected formats: org/repo, https://github.com/org/repo, or git@github.com:org/repo.git"
- [x] **AC-US4-04**: Given the user enters a mix of valid and invalid tokens (e.g., `anton-abyzov/specweave badtoken`), when processed, then valid repos are parsed successfully and errors are reported for invalid tokens only

## Out of Scope

- Automatic detection of project framework/language during restructure (future increment)
- Restructure for non-git directories with complex build systems (Bazel, Buck)
- Migration of CI/CD configuration files to match new paths (user responsibility)
- Support for non-GitHub providers in the root repo connection prompt (ADO/Bitbucket handled by `sw:sync-setup`)
- Automatic symlink repair after restructure

## Technical Notes

### Target Files
- `src/cli/commands/init.ts` — reorder GitHub root repo prompt; integrate workspace setup
- `src/cli/helpers/init/index.ts` — export new workspace-setup module
- `src/cli/helpers/init/summary-banner.ts` — no changes expected
- **New**: `src/cli/helpers/init/workspace-setup.ts` — non-empty folder detection, 3-option menu, restructure logic, local path copy
- `src/cli/helpers/init/repo-connect.ts` — enhance `parseRepoInput()` to return validation errors

### Architecture Decisions
- Workspace setup logic goes in a new `workspace-setup.ts` module to keep `init.ts` from growing beyond 1500-line limit
- `parseRepoInput()` return type changes from `ParsedRepo[]` to `{ repos: ParsedRepo[], errors: ParseError[] }` — callers must be updated
- Restructure uses `fs.renameSync()` for same-filesystem moves (fast, atomic per-file), falling back to copy+delete for cross-filesystem edge cases
- Local path copy uses `fs-extra` `copySync` with filter to exclude `.git` directories

### Org Detection Priority
1. Git remote URL via existing `detectProvider()` → `providerInfo.owner`
2. `package.json` → `repository.url` field parsed for org
3. `package.json` → scope from `name` field (e.g., `@myorg/pkg` → `myorg`)
4. Manual prompt as fallback

## Non-Functional Requirements

- **Performance**: Workspace setup menu must appear within 500ms of detecting non-empty folder. Restructure file move must handle 10,000+ files without OOM.
- **Compatibility**: All paths must work on Windows (backslash), macOS, and Linux. `fs.renameSync` cross-device fallback required.
- **Accessibility**: All prompts use inquirer's built-in keyboard navigation. Error messages include the expected format for screen reader clarity.

## Edge Cases

- **No .git directory**: Non-empty folder with source files but no git — skip restructure remote detection, prompt for org/name manually
- **Multiple git remotes**: Use `origin` remote if available, otherwise prompt user to choose
- **Monorepo root**: Folder contains `packages/` or `apps/` — restructure moves entire tree, does not try to split
- **Local path with spaces**: `copySync` must handle paths with spaces in directory names
- **Relative path input**: User enters `../sibling-repo` as local path — resolve to absolute before copying
- **Same directory as target**: User tries to copy a path that resolves to the current directory — detect and reject
- **Empty org/repo after parse**: parseRepoInput receives valid URL format but empty org or repo segment — return parse error

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Restructure breaks user's git history | 0.1 | 8 | 0.8 | Warn about committing first; do not modify `.git/` |
| parseRepoInput breaking change affects callers | 0.3 | 5 | 1.5 | Return type is additive (new `errors` field); existing `.repos` access unchanged via wrapper |
| Cross-device rename fails silently | 0.2 | 6 | 1.2 | Catch EXDEV error, fall back to copy+delete with progress indicator |
| Users confused by 3-option menu | 0.2 | 3 | 0.6 | "Recommended" label on start-empty; inline help text on each option |

## Success Metrics

- Zero silent failures when org-only input is entered (validation error shown 100% of the time)
- Non-empty folder detection triggers for all directories with 1+ non-hidden files
- GitHub root repo prompt appears before child repo prompt in interactive mode
- Restructure correctly moves all files in test scenarios with 100+ files

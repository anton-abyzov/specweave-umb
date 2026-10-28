# Clarify project root and worktrees

## Problem

Project settings repeats the saved folder in its expandable header and General. The nested checkout differs from the umbrella planning root, making the location misleading about worktree scope and storage.

## Scope

In: read-only configuration/source investigation, migration-impact recommendation, and removal of the redundant header folder disclosure. Preserve General > Project folder and all behavior.

Out: root migration, repository registration, grants, thread bindings, worktree moves, deployment and restart.

## Acceptance Criteria

- [ ] AC-01: A retained report separates the saved root, planning authority, launch repository override and managed storage, and records current migration impact from the supported CLI.
- [ ] AC-02: The settings header identifies the project without repeating General's folder control. Folder mutation behavior stays unchanged.
- [ ] AC-03: Focused settings checks, production web build, visual evidence and fresh-context review qualify the source change; installed acceptance is stated separately.

## Approach

Trace the supported project snapshot, project move --check, ThreadIncrementProgress, FolderLayout, ThreadLaunchService and GitVcsDriverCore. In the isolated managed worktree /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1100-project-folder-clarity, remove only the header ProjectLocation and its import from ProjectWorkspaceSettings. Retain the reusable component and General's guarded control. Run existing checks and inspect the resulting UI. Review the exact diff in a fresh context.

## Decisions

### Asked
- None. The user requested a plan before code and an explanation/design assessment.

### Defaulted (change any before sw-do)
- Keep folder management only in General; header keeps the project name.
- Preserve the configured root and every existing thread binding.
- An umbrella migration needs a separate reviewed action, with explicit child repository selection for code worktrees.

### Open
- None within scope. Applying the umbrella migration is outside this increment.

## Tasks

### T-01 Verify roots and migration impact
- AC: AC-01 | Files: reports/findings.md | Test: specweave-studio project move --check 1332065e-795b-4f98-91c4-f114917e53f6 /Users/antonabyzov/Projects/github/specweave-umb --base-dir /Users/antonabyzov/.specwithcode/m4

### T-02 Remove the duplicate header location
- AC: AC-02, AC-03 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/studio/ProjectWorkspaceSettings.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/studio/ProjectWorkspaceSettings.test.tsx, reports/validation.md | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/studio/ProjectWorkspaceSettings.test.tsx

### T-03 Verify and close 1100
- AC: AC-03 | Files: reports/review.md, reports/verify.md, reports/verify.json | Test: specweave verify 1100

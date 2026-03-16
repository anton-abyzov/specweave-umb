---
increment: 0520-pr-based-increment-closure
title: PR-Based Increment Closure
type: feature
priority: P1
status: completed
created: 2026-03-13T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: PR-Based Increment Closure

## Problem Statement

SpecWeave currently pushes all commits directly to the working branch (typically `main`). Teams that follow PR-based workflows have no way to integrate SpecWeave's automated closure flow with their code review process. This forces users to either abandon SpecWeave's `sw:done` flow or skip code review entirely, creating a gap between spec-driven development and standard engineering practices.

## Goals

- Enable PR-based workflow as an opt-in `pushStrategy` in `cicd` config
- Automate feature branch creation, commit isolation, and PR submission via a new `sw:pr` skill
- Integrate branching into existing `sw:do`, `sw:auto`, and `sw:done` lifecycle without affecting the default `direct` push strategy
- Store PR references in increment metadata for traceability
- Support multi-repo umbrella setups where each touched repo gets its own branch and PR
- Provide an optional enterprise extension point for environment-based release strategies

## User Stories

### US-001: PR-Based Push Strategy Configuration (P1)
**Project**: specweave

**As a** team lead configuring SpecWeave
**I want** to set `cicd.pushStrategy` to `pr-based` with git-specific options
**So that** all increment work flows through pull requests instead of direct pushes

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a `config.json` with `cicd.pushStrategy: "pr-based"`, when the config loader reads the file, then it parses the `cicd.git` sub-object containing `branchPrefix` (string, default `"sw/"`), `targetBranch` (string, default `"main"`), and `deleteOnMerge` (boolean, default `true`)
- [x] **AC-US1-02**: Given `cicd.pushStrategy` is absent from config, when the config loader applies defaults, then `pushStrategy` defaults to `"direct"` and no `git` sub-object is required
- [x] **AC-US1-03**: Given the `CiCdConfig` TypeScript interface, when a developer inspects the type, then it contains a `git?: { branchPrefix: string; targetBranch: string; deleteOnMerge: boolean }` sub-object
- [x] **AC-US1-04**: Given a `PrRef` interface, when a developer inspects the type, then it contains `repo` (string), `prNumber` (number), `prUrl` (string), `branch` (string), `targetBranch` (string), and `createdAt` (ISO 8601 string)
- [x] **AC-US1-05**: Given the `IncrementMetadataV2` interface, when a developer inspects the type, then it contains an optional `prRefs?: PrRef[]` field

---

### US-002: Feature Branch Creation in sw:do and sw:auto (P1)
**Project**: specweave

**As a** developer starting increment work
**I want** `sw:do` and `sw:auto` to automatically create a local feature branch when `pushStrategy` is `pr-based`
**So that** all my commits are isolated from the target branch

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given `pushStrategy` is `"pr-based"` and the developer is on the target branch, when `sw:do` starts (Step 2.7), then a local branch named `{branchPrefix}{increment-id}` is created and checked out (e.g., `sw/0520-pr-based-increment-closure`)
- [x] **AC-US2-02**: Given `pushStrategy` is `"pr-based"` and the developer is already on a non-target branch, when `sw:do` starts, then the existing branch is used as-is without renaming
- [x] **AC-US2-03**: Given `pushStrategy` is `"pr-based"` and the feature branch already exists locally, when `sw:do` starts, then it checks out the existing branch instead of creating a new one
- [x] **AC-US2-04**: Given `pushStrategy` is `"direct"`, when `sw:do` starts, then no branch creation occurs and the existing branch is used unchanged
- [x] **AC-US2-05**: Given `pushStrategy` is `"pr-based"` and there are uncommitted changes in the working tree, when the branch is created, then the uncommitted changes carry over to the new branch (standard `git checkout -b` behavior)

---

### US-003: PR Creation and Metadata Storage via sw:pr (P1)
**Project**: specweave

**As a** developer finishing increment work
**I want** a `sw:pr` skill that pushes my branch and creates a pull request with an auto-generated description
**So that** my work enters the review process with full context from spec.md

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given quality gates have passed in `sw:done`, when `sw:pr` is invoked (Step 8.5), then the current branch is pushed to the remote with upstream tracking (`git push -u origin {branch}`)
- [x] **AC-US3-02**: Given the branch is pushed, when `sw:pr` creates a PR via `gh pr create`, then the PR title is the increment title from spec.md frontmatter and the PR body contains a summary section auto-generated from spec.md user stories and acceptance criteria
- [x] **AC-US3-03**: Given the PR is created successfully, when `sw:pr` updates metadata, then a `PrRef` object is appended to the `prRefs` array in `metadata.json` via an `addPrRef` helper on MetadataManager
- [x] **AC-US3-04**: Given PR creation fails (e.g., `gh` not authenticated, network error), when `sw:pr` handles the error, then a warning is logged but increment closure is NOT blocked
- [x] **AC-US3-05**: Given an umbrella workspace with multiple touched repos, when `sw:pr` runs, then it creates a separate branch and PR in each touched repo, continuing with remaining repos if one fails, and stores all `PrRef` entries in the increment metadata
- [x] **AC-US3-06**: Given a `getPrRefs` helper on MetadataManager, when called with an increment ID, then it returns the `prRefs` array from metadata (empty array if none)

---

### US-004: Enterprise Environment Promotion Configuration (P2)
**Project**: specweave

**As an** enterprise team lead
**I want** to configure environment promotion strategies in the `cicd` config
**So that** PRs can target specific environment branches in a structured release pipeline

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given a `config.json` with `cicd.release.strategy` set to `"env-promotion"` and `cicd.environments` defined as an ordered array of `{ name: string; branch: string }` objects (e.g., `[{name: "dev", branch: "develop"}, {name: "staging", branch: "staging"}, {name: "prod", branch: "main"}]`), when the config loader reads the file, then both fields are parsed and available on `CiCdConfig`
- [x] **AC-US4-02**: Given `cicd.release.strategy` is absent, when the config loader applies defaults, then it defaults to `"trunk"` and no `environments` array is required
- [x] **AC-US4-03**: Given `release.strategy` is `"env-promotion"` and `pushStrategy` is `"pr-based"`, when `sw:pr` runs, then the PR targets the first environment branch in the `environments` array (the lowest environment) instead of `git.targetBranch`

---

## Out of Scope

- Automatic PR merging (human review and merge is intentional)
- `sw:pr-review` AI review skill (enterprise-only, separate increment)
- GitHub Actions / CI pipeline integration for PR status checks
- Branch protection rule management
- Automatic rebase or conflict resolution before PR creation
- PR template customization beyond auto-generated spec summary

## Non-Functional Requirements

- **Backward Compatibility**: Default `pushStrategy: "direct"` is unchanged; solo developers and existing setups are completely unaffected
- **Fault Tolerance**: PR creation failure warns but never blocks increment closure
- **CLI Dependency**: `gh` CLI must be installed and authenticated; `sw:pr` checks for `gh` availability before attempting PR creation

## Edge Cases

- **Branch already exists remotely**: `git push -u` updates the existing remote branch; `gh pr create` detects an existing PR and reports it rather than creating a duplicate
- **Target branch diverged**: PR is created regardless; merge conflicts are visible in the PR and handled by the human reviewer
- **User on non-matching branch**: `sw:pr` uses the current branch as-is; naming convention is a convenience, not enforced
- **No commits on feature branch**: `sw:pr` skips PR creation and logs a warning that there are no changes to submit
- **`gh` CLI not installed**: `sw:pr` detects missing `gh` binary, logs a warning with install instructions, and does not block closure
- **Multi-repo partial failure**: If PR creation fails for one repo in umbrella mode, remaining repos still get their PRs; all results (successes and failures) are reported at the end

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| `gh` CLI not installed on user machine | 0.3 | 3 | 0.9 | Check for `gh` early, provide install instructions, degrade gracefully |
| Branch naming collision with user branches | 0.1 | 2 | 0.2 | Use distinctive `sw/` prefix; accept existing branches as-is |
| Enterprise config complexity confuses users | 0.2 | 4 | 0.8 | Enterprise fields are optional with sensible defaults; core flow works without them |

## Technical Notes

- **Config types**: Extend `CiCdConfig` in `src/core/config/types.ts` with `git` sub-object and `release`/`environments` fields
- **Metadata types**: Add `PrRef` interface and `prRefs` field to `IncrementMetadataV2` in `src/core/types/increment-metadata.ts`
- **MetadataManager helpers**: Add `addPrRef(incrementId, prRef)` and `getPrRefs(incrementId)` to `src/core/increment/metadata-manager.ts`
- **Skill location**: `sw:pr` skill goes in `plugins/specweave/skills/pr/SKILL.md`
- **gh CLI usage**: Shell out via `child_process.execSync` or equivalent, consistent with existing `github-push-sync` patterns
- **Multi-repo detection**: Use umbrella config's `childRepos` to identify which repos have changes (check `git status` per repo)

## Success Metrics

- 100% of existing `pushStrategy: "direct"` users see zero behavior change after this ships
- `sw:pr` successfully creates PRs with auto-descriptions in single-repo and multi-repo setups
- PR URL is retrievable from increment metadata after closure

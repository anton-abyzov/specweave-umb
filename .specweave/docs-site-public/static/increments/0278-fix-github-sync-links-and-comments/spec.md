---
increment: 0278-fix-github-sync-links-and-comments
title: "Fix GitHub Sync Links and AC Comments"
type: bug
priority: P1
status: completed
created: 2026-02-21
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Fix GitHub Sync Links and AC Comments

## Overview

Three critical issues in the GitHub external sync pipeline cause broken user experience when syncing SpecWeave increments to GitHub issues:

1. **Branch hardcoded to `develop`**: `UserStoryIssueBuilder` and `GitHubFeatureSync` hardcode `branch: 'develop'` instead of detecting the actual default branch from the GitHub API. While this works for `anton-abyzov/specweave` (which uses `develop`), it breaks for any repo with a different default branch (e.g., `main`).

2. **AC progress comments never posted**: The `github-ac-comment-poster.ts` `parseIssueLinks()` function looks for issue links in the **spec.md YAML frontmatter** (`userStories:` block), but the sync pipeline stores issue numbers in **metadata.json** (`github.issues[]`) and **user story file frontmatter** (`external.github.issue`). The result: `parseIssueLinks()` always returns empty, so no AC progress comments are ever posted to GitHub issues.

3. **Links in issue body point to wrong repo in umbrella setups**: The `UserStoryIssueBuilder` builds URLs using the sync profile's `owner/repo` (e.g., `anton-abyzov/specweave`), but the living docs files live in the umbrella repo (`anton-abyzov/specweave-umb`). Since the `.specweave/docs/` folder is only in the umbrella and not pushed to the source repo, all Feature Spec and User Story File links return 404.

## User Stories

### US-001: Detect default branch instead of hardcoding (P1)
**Project**: specweave

**As a** SpecWeave user with repos using non-`develop` default branches
**I want** the GitHub sync to detect the actual default branch from the GitHub API
**So that** links in GitHub issues point to valid URLs regardless of the repo's default branch

**Acceptance Criteria**:
- [x] **AC-US1-01**: `GitHubFeatureSync.syncFeatureToGitHub()` detects the default branch from GitHub API instead of hardcoding `'develop'`
- [x] **AC-US1-02**: `UserStoryIssueBuilder` receives the detected branch and uses it for all URL generation
- [x] **AC-US1-03**: `UserStoryContentBuilder.buildIssueBody()` uses detected branch instead of hardcoded `'develop'`
- [x] **AC-US1-04**: Default branch detection is cached per sync session (one API call per feature sync, not per user story)

---

### US-002: Fix AC progress comment posting (P1)
**Project**: specweave

**As a** SpecWeave user who completes acceptance criteria
**I want** AC progress comments to be posted to the correct GitHub issues
**So that** GitHub issues reflect real-time progress on acceptance criteria

**Acceptance Criteria**:
- [x] **AC-US2-01**: `parseIssueLinks()` in `github-ac-comment-poster.ts` reads issue numbers from **metadata.json** (`github.issues[]` and `externalLinks.github.issues`) instead of spec.md frontmatter
- [x] **AC-US2-02**: When an AC is completed in spec.md, a progress comment is posted to the corresponding GitHub issue
- [x] **AC-US2-03**: The metadata.json path is derived from the spec.md path (sibling file in the same increment folder)

---

### US-003: Fix Links section for umbrella repos (P2)
**Project**: specweave

**As a** SpecWeave user with an umbrella repo setup
**I want** Feature Spec and User Story File links in GitHub issues to point to accessible locations
**So that** GitHub issue links lead to valid content instead of 404 pages

**Acceptance Criteria**:
- [x] **AC-US3-01**: When the sync repo differs from the umbrella repo, links point to the increment's spec.md in the sync target repo (which is always pushed) rather than the umbrella's living docs
- [x] **AC-US3-02**: Feature Spec link uses the increment spec.md path as fallback when living docs are not in the target repo
- [x] **AC-US3-03**: User Story File link uses the increment spec.md path as fallback when living docs are not in the target repo
- [x] **AC-US3-04**: Increment link always points to the increment folder in the target repo

## Functional Requirements

### FR-001: Default branch detection
Add a method to `GitHubFeatureSync` (or utility) that calls `gh api repos/{owner}/{repo} --jq '.default_branch'` once per sync session and passes the result to `UserStoryIssueBuilder`. Cache the result to avoid repeated API calls.

### FR-002: AC comment poster metadata lookup
Modify `parseIssueLinks()` in `github-ac-comment-poster.ts` to read issue links from `metadata.json` (same directory as spec.md). Support both formats: `github.issues[].userStory` (old) and `externalLinks.github.issues` (new).

### FR-003: Link fallback for umbrella repos
In `UserStoryIssueBuilder.buildBody()`, when generating the Links section, use paths that are known to exist in the target repo. Since increments are always pushed, prefer links to `/.specweave/increments/{id}/spec.md` over living docs paths that may only exist in the umbrella.

## Success Criteria

- All links in GitHub issues resolve to valid pages (no 404s)
- AC progress comments appear on GitHub issues when ACs are completed
- Default branch detection works for repos with `main`, `develop`, or any other default branch

## Out of Scope

- JIRA/ADO sync (separate providers, same bugs may exist but are out of scope here)
- Changing the overall sync architecture
- Adding new sync providers
- Fixing umbrella repo structure (that's by design)

## Dependencies

- specweave CLI codebase at `repositories/anton-abyzov/specweave/`
- GitHub API access for default branch detection

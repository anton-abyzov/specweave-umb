---
increment: 0501-single-repo-clone
title: "Single Repo Clone via --repo Flag"
type: feature
priority: P1
status: planned
created: 2026-03-12
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Single Repo Clone via --repo Flag

## Problem Statement

The `/sw-github:clone` command only supports org-level bulk cloning. Users who want to add a single repository to their umbrella workspace must either clone manually and configure childRepos by hand, or run a full org fetch just to clone one repo. This is wasteful and error-prone.

## Goals

- Allow cloning a single GitHub repo with a simple `--repo owner/repo` flag
- Support all common GitHub URL formats (shorthand, HTTPS, SSH)
- Reuse existing clone infrastructure (background jobs, childRepos update, resume/skip)
- Maintain consistency with bulk clone UX (dry-run, error handling)

## User Stories

### US-001: Parse Repository Identifier from Multiple Formats (P1)
**Project**: specweave

**As a** developer
**I want** to provide a repo in any common format (owner/repo, HTTPS URL, SSH URL)
**So that** I don't have to remember a specific format when cloning

**Acceptance Criteria**:
- [ ] **AC-US1-01**: Given input `owner/repo`, when parseRepoIdentifier() is called, then it returns `{ owner: "owner", repo: "repo" }`
- [ ] **AC-US1-02**: Given input `github.com/owner/repo`, when parseRepoIdentifier() is called, then it returns `{ owner: "owner", repo: "repo" }`
- [ ] **AC-US1-03**: Given input `https://github.com/owner/repo`, when parseRepoIdentifier() is called, then it returns `{ owner: "owner", repo: "repo" }`
- [ ] **AC-US1-04**: Given input `git@github.com:owner/repo.git`, when parseRepoIdentifier() is called, then it returns `{ owner: "owner", repo: "repo" }`
- [ ] **AC-US1-05**: Given input `invalid-string`, when parseRepoIdentifier() is called, then it returns null

---

### US-002: Validate Repository Exists on GitHub (P1)
**Project**: specweave

**As a** developer
**I want** the tool to verify the repository exists before cloning
**So that** I get a clear error instead of a cryptic git failure

**Acceptance Criteria**:
- [ ] **AC-US2-01**: Given a valid owner/repo that exists on GitHub, when validation runs via GitHub API (`GET /repos/{owner}/{repo}`), then it returns success
- [ ] **AC-US2-02**: Given a repo that does not exist or the user lacks access, when the API returns 404, then the error message reads "Repository {owner}/{repo} not found or you don't have access. Check the repo name and ensure your token has 'repo' scope."
- [ ] **AC-US2-03**: Given no GH_TOKEN or GITHUB_TOKEN is available and the input is not SSH format, when validation runs, then the command exits with a missing-token error before attempting the API call

---

### US-003: Clone Single Repo into Umbrella Structure (P1)
**Project**: specweave

**As a** developer
**I want** `--repo owner/repo` to clone into `repositories/{owner}/{repo}/`
**So that** the repo follows the existing umbrella convention and gets registered in childRepos

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Given `--repo owner/repo` and the repo does not exist locally, when the clone command runs, then the repo is cloned to `repositories/{owner}/{repo}/` via the background job system
- [ ] **AC-US3-02**: Given `--repo owner/repo` and `repositories/{owner}/{repo}/.git` already exists, when the clone command runs, then it skips cloning and reports the repo is already cloned
- [ ] **AC-US3-03**: Given a successful clone, when the clone worker completes, then `config.json` umbrella.childRepos includes an entry with `id: repo`, `path: repositories/{owner}/{repo}`
- [ ] **AC-US3-04**: Given input in SSH format `git@github.com:owner/repo.git`, when the clone runs, then it uses the SSH clone URL (no PAT embedded)
- [ ] **AC-US3-05**: Given input in HTTPS or shorthand format, when the clone runs, then it uses the HTTPS clone URL with the resolved PAT

---

### US-004: Flag Precedence and Dry-Run Support (P2)
**Project**: specweave

**As a** developer
**I want** `--repo` to take precedence over `--org`/`--pattern` and work with `--dry-run`
**So that** the CLI behavior is predictable and I can preview before cloning

**Acceptance Criteria**:
- [ ] **AC-US4-01**: Given both `--repo owner/repo` and `--org myorg` are provided, when the command runs, then `--repo` takes precedence and `--org`/`--pattern` are ignored
- [ ] **AC-US4-02**: Given `--repo owner/repo` and `--dry-run`, when the command runs, then it validates the repo exists, prints what would be cloned, and does not actually clone
- [ ] **AC-US4-03**: Given `--repo` with an unparseable value, when the command runs, then it exits with an error describing the supported formats

---

### US-005: Update Clone Skill Definition (P1)
**Project**: specweave

**As a** developer
**I want** the clone.md skill definition to document the `--repo` flag
**So that** the LLM knows about the new capability and can use it correctly

**Acceptance Criteria**:
- [ ] **AC-US5-01**: Given the updated clone.md, when a user invokes `/sw-github:clone --repo owner/repo`, then the skill definition includes syntax examples and behavior description for the `--repo` flag
- [ ] **AC-US5-02**: Given the updated clone.md, when it documents `--repo`, then it lists all supported input formats (owner/repo, github.com/owner/repo, https://..., git@...)

## Out of Scope

- Support for non-GitHub hosts (GitLab, Bitbucket, ADO) via `--repo`
- Cloning multiple repos via repeated `--repo` flags
- Interactive repo selection when using `--repo`
- Private repo cloning without a token when using HTTPS format

## Non-Functional Requirements

- **Performance**: Single repo validation + clone should complete in under 30 seconds for typical repos
- **Compatibility**: Works on macOS, Linux, Windows (same as existing clone infrastructure)

## Edge Cases

- Trailing `.git` in any format: stripped during parsing (`owner/repo.git` -> `owner/repo`)
- Trailing slash in URL: stripped (`https://github.com/owner/repo/` -> `owner/repo`)
- URL with extra path segments (`https://github.com/owner/repo/tree/main`): parse only owner/repo, ignore rest
- Owner or repo containing hyphens, dots, underscores: handled by regex
- Empty `--repo` value: parse returns null, command exits with format error

## Technical Notes

- `parseRepoIdentifier()` goes in `src/core/repo-structure/url-generator.ts` alongside existing `parseGitRemoteUrl()`
- `cloneSingleGitHubRepo()` goes in `src/cli/helpers/init/github-repo-cloning.ts` -- composes parseRepoIdentifier(), GitHub API validation, buildGitHubCloneUrl(), and launchCloneJob()
- The clone.md skill definition at `plugins/specweave-github/commands/clone.md` needs a new section for `--repo` usage
- SSH format detection: if the original input starts with `git@`, set clone URL format to SSH

## Success Metrics

- Users can clone a single repo with one command instead of manual git clone + config editing
- Zero regression in existing bulk clone behavior (--org, --pattern, --dry-run all unaffected)

## Dependencies

- Existing `launchCloneJob()` in `src/core/background/job-launcher.ts`
- Existing `buildGitHubCloneUrl()` in `src/cli/helpers/init/github-repo-cloning.ts`
- Existing clone-worker.ts (handles childRepos config update)
- GitHub API access via GH_TOKEN/GITHUB_TOKEN

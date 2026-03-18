---
increment: 0570-fix-vskill-install-3part-resolution
title: Fix vskill install 3-part resolution and error messaging
type: bugfix
priority: P1
status: completed
created: 2026-03-18T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Fix vskill install 3-part Resolution and Error Messaging

## Problem Statement

The `vskill install owner/repo/skill` command has two bugs:

1. The 3-part handler falls back to `installSingleSkillLegacy` which hardcodes the path `skills/{name}/SKILL.md`. Skills at non-standard paths (e.g. `plugins/skills/skills/scout/SKILL.md`) are never found, even though `discoverSkills()` already scans the full GitHub tree and could locate them.

2. When a user typos the repo (e.g. `vskill install vskill/scout` instead of `anton-abyzov/vskill/scout`), `getDefaultBranch()` silently returns `"main"` on 404, then `fetchSkillContent()` gets a 404 and shows the generic "SKILL.md not found" error. The user has no indication the repo itself does not exist.

## Goals

- 3-part install resolves skills at any path in the repo, not just `skills/{name}/SKILL.md`
- Non-existent repos produce a clear, actionable error message
- No regressions to existing 2-part or marketplace install flows

## User Stories

### US-001: Discovery-based 3-part skill resolution (P1)
**Project**: vskill
**As a** skill consumer
**I want** `vskill install owner/repo/skill` to find skills at any path in the repo
**So that** I can install skills regardless of the repo's directory layout

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a repo where a skill lives at a non-standard path (not `skills/{name}/SKILL.md`), when the user runs `vskill install owner/repo/skillName`, then `discoverSkills(owner, repo)` is called first and the skill is resolved by matching `skillName` against discovered entries
- [x] **AC-US1-02**: Given `discoverSkills()` returns a match for the requested skill name, when the match is found, then installation uses the discovered `rawUrl` path instead of the hardcoded `skills/{name}/SKILL.md` pattern
- [x] **AC-US1-03**: Given `discoverSkills()` returns no match for the requested skill name, when the fallback executes, then `installSingleSkillLegacy` is called with the hardcoded `skills/{name}/SKILL.md` path as before
- [x] **AC-US1-04**: Given `discoverSkills()` returns an empty array (API error, rate limit, etc.), when the fallback executes, then `installSingleSkillLegacy` is called unchanged from current behavior
- [x] **AC-US1-05**: Given the repo is a marketplace repo and the 3-part handler already matched via marketplace detection, when marketplace install succeeds, then `discoverSkills()` is never called (existing marketplace path is unchanged)

---

### US-002: Clear error for non-existent repositories (P1)
**Project**: vskill
**As a** skill consumer
**I want** a clear error message when the repository does not exist on GitHub
**So that** I understand the repo is wrong instead of debugging a misleading "SKILL.md not found" error

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given a non-existent GitHub repo `owner/repo`, when `checkRepoExists(owner, repo)` is called, then it returns `false`
- [x] **AC-US2-02**: Given an existing GitHub repo `owner/repo`, when `checkRepoExists(owner, repo)` is called, then it returns `true`
- [x] **AC-US2-03**: Given a non-existent repo, when `vskill install owner/repo/skill` is run, then the error message reads `Repository owner/repo does not exist on GitHub` followed by a hint to use flat-name search
- [x] **AC-US2-04**: Given the GitHub API returns a 403 rate-limit or network error, when `checkRepoExists()` is called, then it fails open and returns `true` (assumes repo exists, lets downstream handle errors)
- [x] **AC-US2-05**: Given `GITHUB_TOKEN` is set in the environment, when `checkRepoExists()` makes the API call, then the token is included in the Authorization header (same pattern as `getDefaultBranch`)

## Out of Scope

- Modifying `getDefaultBranch()` behavior or signature
- Changing 2-part (`owner/repo`) install flow
- Changing marketplace detection or marketplace install flow
- Adding repo-existence checks to `--skill` flag path or `--repo` flag path
- Retry logic or exponential backoff for GitHub API calls

## Technical Notes

### Dependencies
- `discoverSkills()` from `src/discovery/github-tree.ts` (already imported in `add.ts`)
- `getDefaultBranch()` from `src/discovery/github-tree.ts` (already imported)
- GitHub REST API `GET /repos/{owner}/{repo}` endpoint

### Constraints
- `checkRepoExists()` must be exported from `src/discovery/github-tree.ts` alongside `getDefaultBranch`
- Must follow the same auth header pattern as `getDefaultBranch` (use `GITHUB_TOKEN` if available)
- Must fail open silently on network/rate-limit errors (no `warnRateLimitOnce`)

### Architecture Decisions
- `discoverSkills()` is called as primary resolution for 3-part format; hardcoded path is fallback only
- `checkRepoExists()` is a standalone function, not embedded in `getDefaultBranch`
- Repo-existence check is placed before `discoverSkills()` in the 3-part path to fail fast

## Non-Functional Requirements

- **Performance**: `checkRepoExists()` adds one GitHub API call; acceptable since it only fires for 3-part format and prevents wasted subsequent calls on non-existent repos
- **Compatibility**: No change to CLI interface or flags; existing install commands continue to work
- **Security**: `GITHUB_TOKEN` handling follows existing patterns; no new token exposure vectors

## Edge Cases

- **Rate-limited API**: `checkRepoExists()` returns `true` (fail open); `discoverSkills()` returns `[]` (existing behavior); falls through to hardcoded path
- **Private repo without token**: `checkRepoExists()` gets 404 (same as non-existent); shows repo-not-found error. This is acceptable -- user needs `GITHUB_TOKEN` for private repos
- **Discovery finds multiple skills with same name**: `discoverSkills()` returns all; match by exact `name` field picks the first match (same as interactive prompt dedup)
- **3-part with marketplace repo**: Marketplace path runs first and short-circuits; discovery is never called

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Private repo mistaken for non-existent | 0.3 | 3 | 0.9 | Error hint suggests checking GITHUB_TOKEN |
| discoverSkills API call adds latency | 0.2 | 2 | 0.4 | Only called in 3-part non-marketplace path |
| Rate limit hit from extra API call | 0.2 | 2 | 0.4 | checkRepoExists fails open silently |

## Success Metrics

- Skills at non-standard paths are installable via 3-part format without requiring `--skill` flag workarounds
- Non-existent repo errors show the repo name and a hint, not "SKILL.md not found"
- All existing tests continue to pass; new tests cover both bug fixes

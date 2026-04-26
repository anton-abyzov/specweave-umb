---
increment: 0770-studio-authored-skill-github-link
title: Studio header — clickable GitHub link for locally-authored skills
type: feature
priority: P1
status: completed
created: 2026-04-26T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio header — clickable GitHub link for locally-authored skills

## Overview

The `vskill studio` skill detail header (`/#/skills/{workspace}/{skill}`) currently renders a clickable `↗` GitHub anchor only for skills installed via the platform — those whose lockfile receipt carries `sourceRepoUrl` + `sourceSkillPath` (per increments 0737 and 0743). Locally-authored skills, even when their parent directory is a git repo with a `github.com` origin remote, fall through to the read-only copy-chip with no clickable link to the source on GitHub.

This increment closes that gap: when a skill has no lockfile entry, the eval-server detects the parent git repo, parses the `origin` remote, computes the SKILL.md path via `git ls-files`, and emits the same `repoUrl` + `skillPath` payload the existing UI already consumes. The result: header parity with `verified-skill.com` for any skill the author has pushed to GitHub. Non-github remotes and non-git skills keep the existing copy-chip fallback unchanged.

Concrete repro of the gap: `TestLab/greet-anton` at `/Users/antonabyzov/Projects/TestLab/greet-anton` has `git remote -v` → `git@github.com:anton-abyzov/greet-anton.git`. After this increment, opening `http://localhost:3136/#/skills/TestLab/greet-anton` shows a `↗` anchor that opens the SKILL.md on GitHub in a new tab.

## User Stories

### US-001: Authored skill in github-pushed git repo shows clickable link (P1)
**Project**: vskill

**As a** skill author
**I want** the studio header to expose a clickable `↗` link to my SKILL.md on GitHub when my skill lives in a git repo with a `github.com` origin remote
**So that** I have one-click navigation from the studio to the source on GitHub — parity with `verified-skill.com` and with platform-installed skills

**Acceptance Criteria**:
- [x] **AC-US1-01**: When `skill.dir` (or any ancestor walked up to filesystem root, max 12 levels) contains a `.git` directory, the eval-server resolves the `origin` remote URL and populates `repoUrl` on the `/api/skills` payload for that skill
- [x] **AC-US1-02**: `skillPath` is the path of the SKILL.md relative to the git repo root, computed via `git ls-files --full-name SKILL.md` run from `skill.dir`; falls back to `relative(gitRoot, join(skillDir, "SKILL.md"))` when the file is untracked
- [x] **AC-US1-03**: SSH remote `git@github.com:owner/repo.git` and HTTPS remotes `https://github.com/owner/repo[.git]` (and the no-`.git` variant) both normalize to canonical `https://github.com/owner/repo`
- [x] **AC-US1-04**: With populated `repoUrl` + `skillPath`, the existing `SourceFileLink` component in `DetailHeader` emits the `↗` anchor with `target="_blank"` and `href = https://github.com/{owner}/{repo}/blob/HEAD/{skillPath}` — no UI changes required

---

### US-002: Skills outside git or with non-github remotes keep the copy-chip fallback (P1)
**Project**: vskill

**As a** skill author working on a skill that is not in a git repo, or in a repo with a non-`github.com` remote (gitlab, bitbucket, internal)
**I want** the studio header to continue showing the existing copy-chip with no broken link
**So that** the existing 0737/0743 behavior is preserved and I never get a 404 anchor

**Acceptance Criteria**:
- [x] **AC-US2-01**: When `skill.dir` is not inside any git working tree (no `.git` ancestor up to filesystem root), `repoUrl` and `skillPath` remain `null` and `SourceFileLink` renders the `data-testid="source-file-copy"` chip
- [x] **AC-US2-02**: When `origin` remote is non-github (`git@gitlab.com:...`, `https://bitbucket.org/...`, internal hosts, empty string, malformed), `repoUrl` and `skillPath` remain `null` (no link, no error) — same copy-chip fallback
- [x] **AC-US2-03**: Skills with a matching lockfile entry (the existing 0737/0743 path) take precedence: when the lockfile resolver returns non-null, the new authored-skill detector is NOT consulted — preserves install-time provenance for installed skills even when the workspace is itself a git repo with a different remote

---

### US-003: Detection is fast, safe, and cached per skill.dir for the studio session (P2)
**Project**: vskill

**As a** user opening the studio with many skills in the workspace
**I want** repeated git lookups to be cached and bounded
**So that** skill list rendering is not slowed down and the eval-server never hangs on a stuck git command

**Acceptance Criteria**:
- [x] **AC-US3-01**: Authored-skill detection results are memoized in a module-level `Map<absoluteSkillDir, {repoUrl, skillPath}>` for the eval-server process lifetime; the cache is not shared across processes and is not persisted to disk
- [x] **AC-US3-02**: A single uncached skill triggers at most 2 `child_process` invocations (`git config --get remote.origin.url` + `git ls-files --full-name SKILL.md`); detection short-circuits to `{null, null}` on the first failure (e.g. git config missing → no ls-files call)
- [x] **AC-US3-03**: All git invocations use `execFileSync` (NOT `execSync`) with explicit argv, `cwd` set to the discovered git root or skill dir, a 1500ms hard timeout, and `stdio: ["ignore", "pipe", "ignore"]` to silence stderr; thrown errors are caught and converted to `{null, null}` — `buildSkillMetadata` never throws because of git

## Functional Requirements

### FR-001: Walk-up `.git` discovery
Starting from `skill.dir`, walk parents up to 12 levels checking for a `.git` directory (or a `.git` file for git worktrees — `existsSync` is sufficient). Bail at filesystem root or 12 levels, whichever comes first. Return the discovered git root or null.

### FR-002: Pure `parseGithubRemote(remote: string): string | null`
Pure string transformation. Accepts:
- `git@github.com:owner/repo.git` → `https://github.com/owner/repo`
- `git@github.com:owner/repo` → `https://github.com/owner/repo`
- `https://github.com/owner/repo.git` → `https://github.com/owner/repo`
- `https://github.com/owner/repo` → `https://github.com/owner/repo`
- `ssh://git@github.com/owner/repo.git` → `https://github.com/owner/repo`

Rejects (returns `null`):
- Non-`github.com` hosts (gitlab.com, bitbucket.org, internal hosts)
- Empty strings, whitespace-only, malformed URLs
- URLs with no `owner/repo` segment

### FR-003: `detectAuthoredSourceLink(skillDir: string): {repoUrl, skillPath}`
Composes FR-001 + FR-002 + git invocations. Memoized per absolute `skillDir`. Returns `{null, null}` on any failure. Never throws.

### FR-004: `resolveSourceLink` precedence
Existing lockfile resolution runs first. Only when no matching lockfile entry exists (or no lockfile at all) does the function fall through to `detectAuthoredSourceLink`. This preserves all existing 0737/0743 behavior.

### FR-005: No UI changes
`SourceFileLink.tsx` and `DetailHeader.tsx` are NOT modified. They already consume `repoUrl` + `skillPath` correctly. Verification of the UI behavior is purely an integration concern.

## Success Criteria

- Opening `http://localhost:3136/#/skills/TestLab/greet-anton` in the studio renders a clickable `↗` anchor in the header
- Clicking the anchor opens `https://github.com/anton-abyzov/greet-anton/blob/HEAD/SKILL.md` (or the actual ls-files path) in a new tab
- All existing tests in `skill-metadata-source-link.test.ts` (0737/0743) still pass — no regressions
- New unit tests for `parseGithubRemote` and `detectAuthoredSourceLink` cover all branches in FR-002 and the edge cases in AC-US2-01, AC-US2-02, AC-US3-02, AC-US3-03
- Skills with no `.git` ancestor or non-github remote continue to render the copy-chip — verified manually and by test

## Out of Scope

- Non-github hosts (gitlab, bitbucket, custom self-hosted) — null fallback only; SourceFileLink builds `/blob/HEAD/` URLs which are github-specific syntax
- Branch detection beyond `HEAD` — `HEAD` resolves to the default branch on github.com, which is the canonical "view this skill" target. Branch-aware blob URLs are a future increment.
- Detecting blob URLs for un-pushed commits or commits on non-default branches — same as above
- Editing or writing back to the repo from the studio (no PR creation, no commit, no push)
- Persistent disk cache or cache invalidation on file change — in-memory module-level Map only
- Parallel git invocations across skills — sequential is fine for typical workspace sizes (<50 skills)

## Dependencies

- Existing `SourceFileLink` component (introduced in 0707, refined in 0737/0743) — must continue to render the anchor when `repoUrl` is a valid `https://` URL
- Existing `DetailHeader` component — must continue passing `skill.repoUrl` + `skill.skillPath` to `SourceFileLink`
- Existing `resolveSourceLink` lockfile path — preserved unchanged; new logic appends a fall-through branch
- `child_process.execFileSync` — already imported in `api-routes.ts`
- `git` CLI on PATH — assumed available in the user's shell environment (eval-server does not bundle git)

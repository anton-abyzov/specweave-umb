# Implementation Plan: Fix vskill install 3-part resolution and error messaging

## Overview

Two targeted fixes to `vskill install` in the vskill CLI:

1. **3-part resolution** -- Replace the hardcoded `plugins/{plugin}/skills/{name}/SKILL.md` probing loop in the 3-part handler (lines 1767-1778 of `add.ts`) with a single call to `discoverSkills()`, which already scans the full GitHub tree and matches skills at all supported paths (root, `skills/*/SKILL.md`, `plugins/*/skills/*/SKILL.md`). This eliminates N+1 raw fetch probes and produces correct `skillSubpathOverride` values by reusing the discovery infrastructure.

2. **Repo existence check** -- Add a `checkRepoExists()` function to `github-tree.ts` that validates the repo exists before attempting install. When a non-existent repo is supplied (e.g., `owner/typo-repo/skill`), the current code falls through to `installSingleSkillLegacy` which hits a 404 on the raw content URL and prints "SKILL.md not found" -- a misleading message. The new check produces a clear "Repository owner/repo does not exist on GitHub" error.

## Architecture

### Component: `github-tree.ts` (Discovery Layer)

**New export: `checkRepoExists(owner, repo): Promise<boolean>`**

```
checkRepoExists(owner, repo)
  |
  v
GET api.github.com/repos/{owner}/{repo}  (same endpoint as getDefaultBranch)
  |
  +---> 200: return true
  +---> 404: return false
  +---> network error / other: return true (fail-open, let downstream handle)
```

Design decisions:
- Reuses the same GitHub API endpoint that `getDefaultBranch()` already calls
- Fail-open on network errors so offline/rate-limited users aren't blocked -- downstream fetch will produce a clear error
- Does NOT share the branch cache; this is a separate concern (existence vs. default branch)
- Leverages existing `warnRateLimitOnce()` for 403 responses

**No changes to `discoverSkills()` or `getDefaultBranch()`** -- they already work correctly. The fix is purely about WHERE they are called from in `add.ts`.

### Component: `add.ts` (Command Handler)

**Change 1: 3-part handler (lines 1758-1781)**

Current flow:
```
3-part input (owner/repo/skill)
  |
  v
detectMarketplaceRepo() --> marketplace? --> installMarketplaceRepo()
  |                                   |
  | (not marketplace)                 | (no plugin match)
  v                                   v
for each plugin:                    for each plugin:
  probe raw URL at                    probe raw URL at
  plugins/{p}/skills/{s}/SKILL.md     plugins/{p}/skills/{s}/SKILL.md
  |                                   |
  v                                   v
fallback: installSingleSkillLegacy()  fallback: installSingleSkillLegacy()
  (hardcoded skills/{s}/SKILL.md)       with subpath override
```

New flow:
```
3-part input (owner/repo/skill)
  |
  v
checkRepoExists(owner, repo) --> false? --> error + exit(1)
  |
  v (repo exists)
detectMarketplaceRepo() --> marketplace? --> installMarketplaceRepo()
  |                                   |
  | (not marketplace)                 | (no plugin match)
  v                                   v
discoverSkills(owner, repo)         discoverSkills(owner, repo)
  |                                   |
  v                                   v
find skill by name in results       find skill by name in results
  |                                   |
  +---> found: installSingleSkillLegacy(subpathOverride = discovered.path)
  +---> not found: installSingleSkillLegacy() (existing default path)
```

Key design choices:
- `checkRepoExists()` runs BEFORE `detectMarketplaceRepo()` because marketplace detection also calls the GitHub API and silently returns `{ isMarketplace: false }` on 404 -- wasting a round-trip to discover the repo is missing
- `discoverSkills()` replaces the per-plugin probing loop. It makes ONE Trees API call instead of N raw content fetches
- When discovery finds the skill, its `.path` field (e.g., `plugins/sw/skills/architect/SKILL.md`) becomes the `skillSubpathOverride` argument to `installSingleSkillLegacy`
- When discovery does NOT find the skill (or returns empty), the existing fallback to `installSingleSkillLegacy` without override preserves backward compatibility

**Change 2: Error messaging in installSingleSkillLegacy**

No changes to `installSingleSkillLegacy` itself. The repo existence check happens earlier in the 3-part handler, so the misleading "SKILL.md not found" case for non-existent repos is eliminated before reaching that function.

### Data Flow

```
User input: "vskill install owner/repo/skill"
  |
  v
addCommand("owner/repo/skill", opts)
  |
  v
parts = ["owner", "repo", "skill"]  (length === 3)
  |
  v
checkRepoExists("owner", "repo")
  |
  +---> false: console.error("Repository owner/repo does not exist on GitHub")
  |            + process.exit(1)
  |
  v (true)
detectMarketplaceRepo("owner", "repo")
  |
  +---> marketplace with plugin match: installMarketplaceRepo(...)
  |
  +---> marketplace, no plugin match:
  |     discoverSkills("owner", "repo")
  |       |
  |       v
  |     find(s => s.name === "skill")
  |       |
  |       +---> found: installSingleSkillLegacy(owner, repo, skill, opts, found.path)
  |       +---> not found: installSingleSkillLegacy(owner, repo, skill, opts)
  |
  +---> not marketplace:
        discoverSkills("owner", "repo")
          |
          v
        find(s => s.name === "skill")
          |
          +---> found: installSingleSkillLegacy(owner, repo, skill, opts, found.path)
          +---> not found: installSingleSkillLegacy(owner, repo, skill, opts)
```

## Technology Stack

- **Language**: TypeScript (ESM, `.js` import extensions)
- **Runtime**: Node.js
- **Testing**: Vitest with `vi.hoisted()` + `vi.mock()` pattern
- **API**: GitHub REST API v3 (repos endpoint, trees endpoint via discoverSkills)

## Implementation Phases

### Phase 1: Add `checkRepoExists` to github-tree.ts

- Add `checkRepoExists(owner: string, repo: string): Promise<boolean>` export
- Single fetch to `https://api.github.com/repos/{owner}/{repo}` with appropriate headers
- Return `true` on 200, `false` on 404, `true` on error (fail-open)
- Call `warnRateLimitOnce(res)` on 403

### Phase 2: Refactor 3-part handler in add.ts

- Import `checkRepoExists` from `../discovery/github-tree.js`
- At top of 3-part block: call `checkRepoExists(threeOwner, threeRepo)`, exit with clear error if false
- Replace the for-loop probing (lines 1767-1778) with `discoverSkills(threeOwner, threeRepo)`
- Match `threeSkill` against discovered results by name
- If found, pass `discovered.path` as `skillSubpathOverride` to `installSingleSkillLegacy`
- If not found, fall through to existing `installSingleSkillLegacy` call (preserves backward compat)

### Phase 3: Tests

- Unit test for `checkRepoExists`: 200 returns true, 404 returns false, network error returns true
- Update existing 3-part tests in `add.test.ts` to mock `checkRepoExists` (always returns true for existing tests)
- New test: 3-part format with non-existent repo prints error and exits
- New test: 3-part format on marketplace repo uses discoverSkills to find skill path
- New test: 3-part format when discoverSkills finds skill, correct subpathOverride is passed

## Testing Strategy

**Mock pattern**: Follows existing `add.test.ts` conventions -- module-scope mock functions with `vi.hoisted()` and `vi.mock()`.

New mock needed:
```typescript
const mockCheckRepoExists = vi.fn().mockResolvedValue(true);
```

Added to the existing `vi.mock("../discovery/github-tree.js", ...)` block:
```typescript
checkRepoExists: (...args: unknown[]) => mockCheckRepoExists(...args),
```

Test cases:
1. `checkRepoExists` unit tests in a new describe block or inline in github-tree tests
2. 3-part + non-existent repo: `mockCheckRepoExists.mockResolvedValue(false)` => expect `process.exit(1)` and error message containing "does not exist"
3. 3-part + marketplace + skill-in-plugin: `mockDiscoverSkills` returns skill with `path: "plugins/sw/skills/architect/SKILL.md"` => verify `installSingleSkillLegacy` called with that subpath
4. Existing TC-017/018/023/024/025 pass unchanged (mockCheckRepoExists defaults to true)

## Technical Challenges

### Challenge 1: API Rate Limiting
**Context**: Adding `checkRepoExists` introduces one additional GitHub API call per 3-part install.
**Mitigation**: The repos endpoint is the same one `getDefaultBranch` already calls. For most installs, both calls happen in sequence and GitHub counts them independently. The fail-open design means rate-limited users still get the install attempt (just with a less specific error on failure). Future optimization: could share the repos API response between `checkRepoExists` and `getDefaultBranch` via a shared cache, but this is unnecessary for the current scope.

### Challenge 2: Discovery vs. Probing Race Condition
**Context**: `discoverSkills` uses the Trees API which returns a snapshot. If a skill was just pushed, Trees may lag behind raw content.
**Mitigation**: The fallback to `installSingleSkillLegacy` without override handles this case -- it uses the existing `skills/{name}/SKILL.md` default path. This is the same behavior as today for non-marketplace repos.

### Challenge 3: Backward Compatibility
**Context**: The 3-part handler currently works for marketplace repos where the skill lives under `plugins/*/skills/*/SKILL.md`.
**Mitigation**: The marketplace detection and `hasPlugin` check remain unchanged (first code path). Discovery only replaces the probing loop that runs when the skill name doesn't match a plugin name. The fallback to `installSingleSkillLegacy` without override is preserved as the final catch-all.

# Implementation Plan: Single Repo Clone via --repo Flag

## Overview

Extend the existing `/sw-github:clone` command to support a `--repo` flag that clones a single GitHub repository into the umbrella workspace. The implementation adds two new functions to existing modules, wires them into the clone skill definition, and reuses the background job infrastructure (launchCloneJob, clone-worker) for consistency.

No new files are created. Three existing files are extended. All new code follows the TypeScript ESM conventions (`.js` extensions in imports, `--moduleResolution nodenext`).

## Architecture

### Component Map

```
User input ("owner/repo" | URL | SSH)
        |
        v
+---------------------------+
| parseRepoIdentifier()     |  <-- NEW in url-generator.ts
| - shorthand: owner/repo   |
| - github.com/owner/repo   |
| - delegates to existing   |
|   parseGitRemoteUrl() for |
|   https:// and git@ URLs  |
+---------------------------+
        |
        v
  { owner, repo, inputType }
        |
        v
+---------------------------+
| cloneSingleGitHubRepo()   |  <-- NEW in github-repo-cloning.ts
| 1. parseRepoIdentifier()  |
| 2. resolveToken()         |
| 3. validateRepoExists()   |  <-- GitHub API GET /repos/{owner}/{repo}
| 4. check local .git dir   |
| 5. buildGitHubCloneUrl()  |  <-- existing, reused
| 6. launchCloneJob()       |  <-- existing, reused (1-repo array)
+---------------------------+
        |
        v
+---------------------------+
| clone-worker (background) |  <-- UNCHANGED
| - git clone               |
| - update childRepos       |
| - write result.json       |
+---------------------------+
```

### Files Modified

| File | Change | Scope |
|------|--------|-------|
| `src/core/repo-structure/url-generator.ts` | Add `parseRepoIdentifier()` | ~45 lines |
| `src/cli/helpers/init/github-repo-cloning.ts` | Add `cloneSingleGitHubRepo()`, export `buildGitHubCloneUrl()` | ~85 lines |
| `plugins/specweave-github/commands/clone.md` | Document `--repo` flag, examples | ~40 lines |
| `tests/unit/core/repo-structure/url-generator.test.ts` | Tests for `parseRepoIdentifier()` | ~80 lines |
| `tests/unit/cli/helpers/init/github-repo-cloning.test.ts` | Tests for `cloneSingleGitHubRepo()` | ~120 lines |

### No New Files

Every change goes into an existing file. No new modules, no new workers, no new types files.

## Design Decisions

### D-1: parseRepoIdentifier() delegates to parseGitRemoteUrl() for standard URLs

**Decision**: The new function handles shorthand formats (`owner/repo`, `github.com/owner/repo`) itself, then delegates to the existing `parseGitRemoteUrl()` for full HTTPS and SSH URLs.

**Rationale**: Avoids duplicating regex logic. `parseGitRemoteUrl()` already handles `https://github.com/owner/repo.git` and `git@github.com:owner/repo.git` correctly. The new function only adds the two shorthand formats on top.

**Implementation**:
```typescript
export function parseRepoIdentifier(input: string): {
  owner: string;
  repo: string;
  inputType: 'ssh' | 'https' | 'shorthand';
} | null {
  const trimmed = input.trim();
  if (!trimmed) return null;

  // 1. Try standard git URL formats via existing parser
  const gitResult = parseGitRemoteUrl(trimmed);
  if (gitResult && gitResult.host.includes('github')) {
    return {
      owner: gitResult.owner,
      repo: stripGitSuffix(gitResult.repo),
      inputType: gitResult.urlType
    };
  }

  // 2. github.com/owner/repo (no protocol)
  const bareHostMatch = trimmed.match(
    /^github\.com\/([\w.-]+)\/([\w.-]+?)(?:\.git)?\/?(?:\/.*)?$/
  );
  if (bareHostMatch) {
    return { owner: bareHostMatch[1], repo: bareHostMatch[2], inputType: 'https' };
  }

  // 3. owner/repo shorthand (exactly two segments)
  const shorthandMatch = trimmed.match(
    /^([\w.-]+)\/([\w.-]+?)(?:\.git)?\/?$/
  );
  if (shorthandMatch) {
    return { owner: shorthandMatch[1], repo: shorthandMatch[2], inputType: 'shorthand' };
  }

  return null;
}
```

### D-2: inputType field distinguishes SSH from HTTPS/shorthand

**Decision**: Return an `inputType` field so the caller knows whether the original input was SSH (`git@...`), which determines clone URL format without requiring a separate flag.

**Rationale**: Per spec AC-US3-04 and AC-US3-05: SSH input uses SSH clone URL; HTTPS/shorthand input uses HTTPS clone URL with PAT. The `inputType` makes this decision trivial in `cloneSingleGitHubRepo()`:

```typescript
const urlFormat = parsed.inputType === 'ssh' ? 'ssh' : 'https';
```

### D-3: Background job reused for single repo

**Decision**: Even for a single repo, we call `launchCloneJob()` with a 1-element repository array.

**Rationale**:
- The clone-worker already handles `childRepos` config update on completion -- free for single repo too.
- Job tracking via `/sw:jobs` works automatically.
- Resume/skip detection (already-cloned check) is handled by `launchCloneJob()`'s pre-flight logic.
- Zero new infrastructure code.

### D-4: Repo validation via GitHub API before cloning

**Decision**: `cloneSingleGitHubRepo()` calls `GET /repos/{owner}/{repo}` before launching the clone job.

**Rationale**: Provides a clear, user-friendly error ("Repository not found or you don't have access") instead of a cryptic git clone failure message in the background worker logs. The API call is fast (single request, <500ms) and confirms both existence and access.

**Token requirement**: For HTTPS/shorthand input, a token is required (AC-US2-03). For SSH input, validation is still attempted if a token is available, but SSH clone can proceed without one (SSH key auth is separate from API auth).

### D-5: buildGitHubCloneUrl() made public (exported)

**Decision**: The existing `buildGitHubCloneUrl()` function (currently module-private in `github-repo-cloning.ts`) is exported so `cloneSingleGitHubRepo()` can use it.

**Rationale**: The function is already the canonical way to build clone URLs. Rather than duplicating the logic, we export it. The helpers `buildGitHubHttpsCloneUrl()` and `buildGitHubSshCloneUrl()` remain private.

### D-6: --repo takes precedence over --org (flag precedence)

**Decision**: When `--repo` is provided alongside `--org`/`--pattern`, the `--repo` path executes and `--org`/`--pattern` are ignored. This is documented in clone.md and handled with an early-return branch.

**Rationale**: Unambiguous behavior. The user explicitly asked for a single repo -- honoring `--org` or `--pattern` alongside `--repo` would be contradictory.

### D-7: HTTPS URL regex relaxation for extra path segments

**Decision**: `parseRepoIdentifier()` handles URLs with extra path segments like `https://github.com/owner/repo/tree/main` by extracting only the first two path segments (owner/repo).

**Rationale**: Users often copy URLs from their browser which include branch/file paths. Rejecting these would be a poor UX. The existing `parseGitRemoteUrl()` regex is strict (matches exactly `/owner/repo` or `/owner/repo.git`), so the new function needs a broader regex or pre-processing to strip trailing path segments before delegating.

**Implementation**: Pre-process the URL to extract the first two path segments before delegating to `parseGitRemoteUrl()`:

```typescript
// Strip extra path segments from HTTPS URLs:
// https://github.com/owner/repo/tree/main -> https://github.com/owner/repo
const httpsExtraPath = trimmed.match(
  /^(https?:\/\/github\.com\/[\w.-]+\/[\w.-]+?)(?:\.git)?(?:\/.*)?$/
);
if (httpsExtraPath) {
  const cleaned = httpsExtraPath[1];
  const gitResult = parseGitRemoteUrl(cleaned);
  if (gitResult) {
    return { owner: gitResult.owner, repo: gitResult.repo, inputType: 'https' };
  }
}
```

## Data Flow

### cloneSingleGitHubRepo() Sequence

```
1. Parse input
   input: "anton-abyzov/specweave"
   -> parseRepoIdentifier() -> { owner: "anton-abyzov", repo: "specweave", inputType: "shorthand" }

2. Resolve token
   -> GH_TOKEN || GITHUB_TOKEN from env
   -> If missing + inputType !== 'ssh' -> error "Missing token"

3. Validate repo exists (API)
   -> GET https://api.github.com/repos/anton-abyzov/specweave
   -> 200: continue
   -> 404: error "Repository not found..."

4. Check local existence
   -> fs.existsSync(projectPath + "/repositories/anton-abyzov/specweave/.git")
   -> If exists: return { alreadyCloned: true }

5. Build clone URL
   -> buildGitHubCloneUrl("anton-abyzov", "specweave", pat, "https")
   -> "https://{pat}@github.com/anton-abyzov/specweave.git"

6. Launch clone job
   -> launchCloneJob({
        projectPath,
        repositories: [{
          owner: "anton-abyzov",
          name: "specweave",
          path: "repositories/anton-abyzov/specweave",
          cloneUrl: "https://{pat}@github.com/anton-abyzov/specweave.git"
        }]
      })

7. Return result
   -> { jobId, clonedRepos: ["specweave"] }
```

### Dry-Run Flow

When `--dry-run` is provided, steps 1-4 execute normally (validation is useful feedback), but step 6 is skipped. Instead, the function prints what would be cloned and returns without launching a job.

## Function Signatures

### parseRepoIdentifier (url-generator.ts)

```typescript
/**
 * Parse a repository identifier from various input formats.
 * Supports: owner/repo, github.com/owner/repo, https://github.com/owner/repo[.git],
 *           git@github.com:owner/repo[.git]
 *
 * Delegates to parseGitRemoteUrl() for standard git URL formats.
 *
 * @param input - Repository identifier in any supported format
 * @returns Parsed owner/repo with input type, or null if unparseable
 */
export function parseRepoIdentifier(input: string): {
  owner: string;
  repo: string;
  inputType: 'ssh' | 'https' | 'shorthand';
} | null;
```

### cloneSingleGitHubRepo (github-repo-cloning.ts)

```typescript
export interface SingleRepoCloneOptions {
  /** Raw repo identifier (any format) */
  repoIdentifier: string;
  /** Project root path */
  projectPath: string;
  /** GitHub PAT (optional for SSH) */
  pat?: string;
  /** Dry-run mode -- validate only, don't clone */
  dryRun?: boolean;
}

export interface SingleRepoCloneResult {
  /** Whether the clone job was launched */
  cloned: boolean;
  /** Job ID if clone was launched */
  jobId?: string;
  /** Whether repo was already cloned locally */
  alreadyCloned?: boolean;
  /** Parsed owner */
  owner?: string;
  /** Parsed repo name */
  repo?: string;
  /** Error message if failed */
  error?: string;
}

/**
 * Clone a single GitHub repository into the umbrella workspace.
 * Validates the repo exists, checks for local duplicates, then
 * launches a background clone job via existing infrastructure.
 */
export async function cloneSingleGitHubRepo(
  options: SingleRepoCloneOptions
): Promise<SingleRepoCloneResult>;
```

## Testing Strategy

### Unit Tests for parseRepoIdentifier()

File: `tests/unit/core/repo-structure/url-generator.test.ts` (extend existing)

| Test Case | Input | Expected |
|-----------|-------|----------|
| Shorthand | `owner/repo` | `{ owner: "owner", repo: "repo", inputType: "shorthand" }` |
| Bare host | `github.com/owner/repo` | `{ owner: "owner", repo: "repo", inputType: "https" }` |
| HTTPS URL | `https://github.com/owner/repo` | `{ owner: "owner", repo: "repo", inputType: "https" }` |
| HTTPS .git | `https://github.com/owner/repo.git` | `{ owner: "owner", repo: "repo", inputType: "https" }` |
| SSH URL | `git@github.com:owner/repo.git` | `{ owner: "owner", repo: "repo", inputType: "ssh" }` |
| Invalid | `invalid-string` | `null` |
| Empty | `""` | `null` |
| Trailing slash | `owner/repo/` | `{ owner: "owner", repo: "repo", inputType: "shorthand" }` |
| Trailing .git | `owner/repo.git` | `{ owner: "owner", repo: "repo", inputType: "shorthand" }` |
| Extra path | `https://github.com/owner/repo/tree/main` | `{ owner: "owner", repo: "repo", inputType: "https" }` |
| Hyphens/dots | `my-org/my.repo` | `{ owner: "my-org", repo: "my.repo", inputType: "shorthand" }` |

### Unit Tests for cloneSingleGitHubRepo()

File: `tests/unit/cli/helpers/init/github-repo-cloning.test.ts` (extend existing)

Test cases:
- Valid shorthand -> validates via API -> launches clone job
- Repo not found (404) -> returns error message per AC-US2-02
- Missing token for HTTPS -> returns missing-token error per AC-US2-03
- Already cloned locally -> returns alreadyCloned: true, no job
- SSH input -> uses SSH clone URL (no PAT embedded)
- HTTPS input -> uses HTTPS clone URL with PAT
- Dry-run mode -> validates but does not launch job
- Unparseable input -> returns error with supported formats
- Repo path follows `repositories/{owner}/{repo}` convention

All tests mock `fetch` (for GitHub API), `launchCloneJob`, and `fs.existsSync` (for local check) following the existing test patterns in the file.

## Edge Cases

| Edge Case | Handling |
|-----------|----------|
| Trailing `.git` in any format | Stripped during parsing |
| Trailing `/` in URL | Stripped by regex |
| Extra path segments in URL | Only owner/repo extracted |
| Owner/repo with hyphens, dots, underscores | Handled by `[\w.-]+` regex character class |
| Empty `--repo` value | parseRepoIdentifier returns null -> command exits with format error |
| Non-GitHub host in URL | parseRepoIdentifier returns null (GitHub-only per out-of-scope) |

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| parseGitRemoteUrl regex too strict for edge cases | Low | Low | parseRepoIdentifier pre-processes URLs before delegating |
| GitHub API rate limit on validation call | Very Low | Low | Single request; existing rate-limit backoff not needed for 1 call |
| Token resolution inconsistency | Low | Medium | Reuse same GH_TOKEN/GITHUB_TOKEN lookup as existing clone flow |

## Implementation Order

1. **parseRepoIdentifier()** in url-generator.ts + tests (US-001, pure function, no deps)
2. **Export buildGitHubCloneUrl()** in github-repo-cloning.ts (trivial change)
3. **cloneSingleGitHubRepo()** in github-repo-cloning.ts + tests (US-002, US-003, US-004)
4. **Update clone.md** skill definition (US-005)
5. **Integration verification** -- manual test with real repo

## Domain Skill Recommendation

No additional domain skills needed. This is a pure TypeScript/Node.js change within the existing SpecWeave CLI codebase. The complexity is low (two new functions extending existing modules), all within the `backend:nodejs` domain but not warranting a separate domain skill invocation given the narrow scope.

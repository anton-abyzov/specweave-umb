# Implementation Plan: Fix vskill install: verification name collision + restore scope prompt

## Overview

Two targeted bug fixes across the vskill-platform (server) and vskill (client) repositories. The server fix scopes the rejection query by `repoUrl` to eliminate false-positive warnings. The client fix threads `repoUrl` through all `checkInstallSafety` call sites and restores the removed project/global scope prompt. No new schemas, no new ADRs -- all changes follow existing patterns.

## Architecture

### Change Map

```
vskill-platform (server)
  src/app/api/v1/blocklist/check/route.ts
    L50-72: Add optional repoUrl WHERE clause to rejection query

vskill (client)
  src/blocklist/blocklist.ts
    L155: Add repoUrl? third param to checkInstallSafety()
    L160: Append &repoUrl= to API URL when present

  src/commands/add.ts
    L984:  installPluginDir      -- pluginName only (local path, no repoUrl)
    L1192: installOneGitHubSkill -- owner/repo available, construct repoUrl
    L1419: installRepoPlugin     -- ownerRepo available, construct repoUrl
    L2050: installFromRegistry   -- no repoUrl yet (catch block, name-only)
    L2144: installFromRegistry   -- detail.repoUrl available from registry response
    L2258: installSingleSkillLegacy -- owner/repo in scope, construct repoUrl

    L752-799: promptInstallOptions -- restore scope prompt
```

### Component Boundaries

1. **Server rejection query** (vskill-platform) -- single file change, self-contained
2. **Client API call** (vskill/blocklist.ts) -- function signature change, backward compatible
3. **Call site threading** (vskill/add.ts) -- mechanical pass-through at 6 sites
4. **Scope prompt restoration** (vskill/add.ts) -- isolated UX change in `promptInstallOptions()`

### Data Flow

```
User runs: npx vskill i owner/repo

  add.ts parses owner/repo
    |
    v
  checkInstallSafety(skillName, contentHash?, repoUrl?)
    |                                          ^
    |                            constructed from owner/repo
    v                            or detail.repoUrl from registry
  GET /api/v1/blocklist/check?name=X&repoUrl=Y
    |
    v
  route.ts:
    blocklist check  -- already scoped (findActiveBlocklistEntry handles repoUrl)
    rejection query  -- NEW: add repoUrl WHERE clause when param present
    taint check      -- unchanged (author-level, not repo-scoped)
    |
    v
  Response: { blocked, rejected, tainted, ... }
```

## Implementation Details

### 1. Server: Scope rejection query by repoUrl (vskill-platform)

**File**: `src/app/api/v1/blocklist/check/route.ts` lines 50-72

The `repoUrl` is already parsed from search params at line 12. The blocklist lookup at line 27 already passes it. Only the rejection query (lines 50-72) ignores it.

**Change**: When `repoUrl` is provided, add it to the `where` clause:

```typescript
const rejectedSubmission = await db.submission.findFirst({
  where: {
    skillName: name,
    state: { in: [...REJECTION_STATES] },
    ...(repoUrl ? { repoUrl } : {}),
  },
  // ... rest unchanged
});
```

**Why this works**:
- When `repoUrl` is present: query scopes to `skillName + repoUrl`, hitting the compound index `[repoUrl, skillName]` on Submission (schema line 202)
- When `repoUrl` is absent: query falls back to `skillName` only (current behavior, backward compatible)
- The spread pattern `...(repoUrl ? { repoUrl } : {})` is the idiomatic Prisma conditional where clause

**Pattern precedent**: `findActiveBlocklistEntry` in `blocklist-check.ts` already uses `OR: [{sourceUrl: repoUrl}, {sourceUrl: null}]` for scoped lookups. The rejection query is simpler -- no global ban concept for submissions, so direct equality is correct.

### 2. Client: Add repoUrl param to checkInstallSafety (vskill)

**File**: `src/blocklist/blocklist.ts` lines 155-179

**Change**: Add optional third parameter, append to URL when present:

```typescript
export async function checkInstallSafety(
  skillName: string,
  contentHash?: string,
  repoUrl?: string,
): Promise<InstallSafetyResult> {
  try {
    let url = `${getApiBaseUrl()}/api/v1/blocklist/check?name=${encodeURIComponent(skillName)}`;
    if (repoUrl) {
      url += `&repoUrl=${encodeURIComponent(repoUrl)}`;
    }
    // ... rest unchanged
```

**Backward compatibility**: Third param is optional. All existing call sites continue to work with 1 or 2 args. Server ignores unknown params -- older servers simply ignore the extra query param.

### 3. Client: Thread repoUrl through call sites (vskill)

Each of the 6 `checkInstallSafety` call sites, with repoUrl availability:

| Line | Function | repoUrl source | Change |
|------|----------|----------------|--------|
| 984 | `installPluginDir` | None (local path install) | Leave as-is: `checkInstallSafety(pluginName)` |
| 1192 | `installOneGitHubSkill` | `owner`/`repo` params | `checkInstallSafety(skillName, undefined, \`https://github.com/${owner}/${repo}\`)` |
| 1419 | `installRepoPlugin` | `ownerRepo` param | `checkInstallSafety(pluginName, undefined, \`https://github.com/${ownerRepo}\`)` |
| 2050 | `installFromRegistry` (catch) | None (lookup failed) | Leave as-is: `checkInstallSafety(skillName)` |
| 2144 | `installFromRegistry` (success) | `detail.repoUrl` | `checkInstallSafety(skillName, undefined, detail.repoUrl)` |
| 2258 | `installSingleSkillLegacy` | `owner`/`repo` params | `checkInstallSafety(skillName, undefined, \`https://github.com/${owner}/${repo}\`)` |

**Note on URL format**: The `repoUrl` stored in Submission uses `https://github.com/owner/repo` format (confirmed by line 377 of add.ts: `const repoUrl = \`https://github.com/${owner}/${repo}\``). The same format must be sent in the API query for the WHERE clause to match.

### 4. Client: Restore scope prompt (vskill)

**File**: `src/commands/add.ts`, function `promptInstallOptions()` at line 752

**Current code** (lines 798-799):
```typescript
// Scope: --global flag -> global install; default -> project (cwd)
useGlobal = !!opts.global;
```

**Change**: Replace with a `promptChoice` call matching the pre-`af41f86` behavior:

```typescript
// Scope: skip prompt if --global or --cwd already set
if (!opts.global && !opts.cwd) {
  const prompter2 = createPrompter();
  const scopeIdx = await prompter2.promptChoice("Installation scope:", [
    { label: "Project", hint: "install in current project root" },
    { label: "Global", hint: "install in user home directory" },
  ]);
  useGlobal = scopeIdx === 1;
} else {
  useGlobal = !!opts.global;
}
```

**Skip conditions**:
- `--global` flag set: skip, use global (AC-US3-02)
- `--cwd` flag set: skip, use project (AC-US3-03)
- `--yes` (non-interactive): already handled by `shouldPrompt` check at line 756 (AC-US3-04)
- Non-TTY: already handled by `isTTY()` check at line 756

**Note**: `resolveInstallBase()` at line 723 already handles the actual path resolution based on `opts.global`. The prompt just sets the `global` field in the returned `InstallSelections`.

## Testing Strategy

TDD mode. Tests should cover:

### Server tests (vskill-platform)
- **Unit**: Mock Prisma, verify the rejection query includes `repoUrl` in WHERE when param is present
- **Unit**: Mock Prisma, verify the rejection query omits `repoUrl` when param is absent (backward compat)
- **Integration**: Hit the API route with two skills sharing a name but different repoUrls -- only the matching one returns `rejected: true`

### Client tests (vskill)
- **Unit**: `checkInstallSafety` appends `&repoUrl=` to URL when third param provided
- **Unit**: `checkInstallSafety` omits `repoUrl` when third param is undefined
- **Unit**: URL-encodes special characters in repoUrl
- **Unit**: Scope prompt displayed when neither `--global` nor `--cwd` set
- **Unit**: Scope prompt skipped when `--global` set
- **Unit**: Scope prompt skipped when `--cwd` set
- **Unit**: Scope prompt skipped when `--yes` set (non-interactive)

## Technical Challenges

### Challenge: Staggered deployment (client updates before server)
**Solution**: The `repoUrl` query parameter is purely additive. Older servers ignore unknown query params in URL parsing. The client's `checkInstallSafety` graceful degradation (catch block, lines 174-178) handles any unexpected server behavior. No coordination needed.

### Challenge: URL format consistency between submission storage and query
**Solution**: Both paths use `https://github.com/owner/repo` format. Submission creation (add.ts line 377) and the new query param construction use the same template. The compound index `[repoUrl, skillName]` matches exact strings, so format consistency is critical and already guaranteed.

## Deployment Order

Either repo can be deployed first due to backward compatibility:
1. **Server first** (preferred): Deploy vskill-platform with scoped rejection query. Existing clients send no `repoUrl`, server falls back to name-only. No behavior change until client updates.
2. **Client first**: Deploy vskill with `repoUrl` in API calls. Old server ignores the param. No behavior change until server updates.
3. **Scope prompt**: Client-only change, independent of server. Can ship in same vskill release.

# Implementation Plan: Multi-Skill Repo Install & Queue Admin Gating

## Overview

This increment spans two projects with two independent workstreams:

1. **vskill CLI** (`repositories/anton-abyzov/vskill/`): Add a skill discovery layer to the GitHub `add` path that uses the GitHub Trees API to find all SKILL.md files in a repo, then iterates the existing install pipeline for each discovered skill.

2. **vskill-platform** (`repositories/anton-abyzov/vskill-platform/`): Wrap the batch submission form on `/queue` with an `isAdmin` guard so only admin users see it.

## Architecture

### Component 1: Skill Discovery Module (vskill CLI)

**New file**: `src/discovery/github-tree.ts`

Responsible for calling the GitHub Trees API and returning a list of discovered skill paths.

```typescript
interface DiscoveredSkill {
  name: string;       // e.g., "repo-name" for root, "foo" for skills/foo/SKILL.md
  path: string;       // e.g., "SKILL.md" or "skills/foo/SKILL.md"
  rawUrl: string;     // raw.githubusercontent.com URL for fetching content
}

async function discoverSkills(owner: string, repo: string): Promise<DiscoveredSkill[]>
```

**Algorithm**:
1. `GET https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1`
2. Filter tree entries where `path` matches `SKILL.md` or `skills/*/SKILL.md`
3. For each match, derive `name` from path (root -> repo name, `skills/{name}/SKILL.md` -> name)
4. Return array of `DiscoveredSkill`

**Fallback**: If Trees API returns 404 or rate-limited, fall back to fetching just root `SKILL.md` (current behavior).

### Component 2: Multi-Skill Install Loop (vskill CLI)

**Modified file**: `src/commands/add.ts`

The existing `addCommand` GitHub path (lines 396-551) is refactored:

- When `--skill` is NOT provided, call `discoverSkills()` first
- Loop through discovered skills, calling the existing blocklist/security/scan/install pipeline for each
- Aggregate results and display summary
- When `--skill` IS provided, skip discovery and use the existing single-skill path (backward compat)

### Component 3: Queue Page Admin Gate (vskill-platform)

**Modified file**: `src/app/queue/page.tsx`

The batch submission section (lines 251-339) is wrapped in an `isAdmin` conditional. The `useAdminStatus` hook is already imported and used on this page.

### Data Model

No database changes. The lockfile format is unchanged -- each discovered skill gets its own entry keyed by skill name.

### API Contracts

No new API endpoints. The GitHub Trees API is a read-only external call:
- `GET https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1`
- Response: `{ tree: [{ path: string, type: "blob" | "tree", ... }] }`

## Technology Stack

- **Language**: TypeScript (ESM, `--moduleResolution nodenext`)
- **CLI Framework**: Commander.js (existing)
- **HTTP**: Native `fetch()` (existing pattern in add.ts)
- **Frontend**: React / Next.js 15 (existing)
- **Testing**: Vitest (existing)

**Architecture Decisions**:

- **GitHub Trees API vs. multiple fetches**: Trees API returns the entire repo structure in one request, avoiding N+1 fetches. This is critical for repos with 100+ skills.
- **No new CLI flags**: Discovery is automatic when `--skill` is absent. This keeps the UX simple -- `vskill add owner/repo` "just works" for multi-skill repos.
- **Partial failure model**: Each skill is installed independently. A scan failure for one skill does not abort the others. This is important for large repos where one skill might have legitimate issues.
- **UI-only admin gate**: The submission API is not changed. Admin gating is enforced in the React component because the API already has its own auth checks and the batch form is a convenience UI, not a security boundary.

## Implementation Phases

### Phase 1: Discovery Module
- Create `src/discovery/github-tree.ts` with `discoverSkills()` function
- Unit tests for tree parsing, name derivation, fallback behavior

### Phase 2: Multi-Skill Install Loop
- Refactor `addCommand` to use discovery when `--skill` is absent
- Extract single-skill install into a reusable function
- Update lockfile handling for multiple skills
- Update summary output for multi-skill results
- Integration tests

### Phase 3: Queue Admin Gate
- Wrap batch form in `isAdmin` conditional on `/queue` page
- Test: admin sees form, non-admin does not

## Testing Strategy

- **vskill CLI**: Mock `fetch` for GitHub Trees API responses. Test discovery with various tree structures (root only, root + skills/*, skills/* only, empty). Mock the install pipeline to verify each skill is processed independently. Existing add.test.ts tests must pass unchanged.
- **vskill-platform**: Component test for queue page verifying batch form visibility based on `isAdmin` state from `useAdminStatus` hook.

## Technical Challenges

### Challenge 1: GitHub Trees API Rate Limiting
**Solution**: The Trees API is a single call per `add` invocation. Unauthenticated rate limit is 60/hour which is sufficient. If rate-limited, fall back to fetching just root SKILL.md.
**Risk**: Low. Most users run `add` infrequently.

### Challenge 2: Backward Compatibility
**Solution**: When `--skill` is provided, skip discovery entirely and use the existing single-fetch path. When discovery finds only a root SKILL.md, the behavior is identical to current. All existing tests remain untouched.
**Risk**: Low. The refactoring is additive -- the existing install logic is extracted but not changed.

### Challenge 3: Large Repo Performance
**Solution**: The Trees API returns the full tree in one request. Individual SKILL.md fetches are sequential (to respect rate limits) but each is small (<100KB). For a repo with 200 skills, this is ~200 small fetches which completes in seconds.
**Risk**: Medium. For very large repos, consider adding a `--limit N` flag in the future.

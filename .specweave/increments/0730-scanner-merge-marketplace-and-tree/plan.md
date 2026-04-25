# Implementation Plan: Scanner merges marketplace + orphan top-level skills

## Overview

Single-file change to `repositories/anton-abyzov/vskill-platform/src/lib/scanner.ts`:
- Refactor `discoverSkillsEnhanced` to ALWAYS run the Git Trees tree-walk (currently only on manifest-absent path)
- After fetching marketplace manifest, compute the set of paths covered by registered plugins
- Filter tree-walk results to orphans (paths NOT in the covered set, NOT rejected by `shouldRejectSkillPath`)
- Merge: `result.skills = marketplace_skills + orphans`

## Architecture

### Components touched

| File | Change |
|---|---|
| `src/lib/scanner.ts` | Refactor `discoverSkillsEnhanced` (lines 514-593): always tree-walk, compute covered-paths set, return merged result. Mark orphans with `plugin: null`. |
| `src/lib/__tests__/scanner-discovery.test.ts` | Update existing "empty plugins array" test (it currently asserts `skills: []` for orphan-present case — must change to assert orphan included). Add new tests for AC-US1-01..06 + AC-US2-01..04. |
| `src/lib/scanner.ts` `DiscoveredSkill` type | Add optional `plugin?: string | null` field (or update if already nullable). Verify downstream consumers (publish, search, outbox-writer) accept null. |

### Algorithm

```ts
async function discoverSkillsEnhanced(repoUrl, token):
  empty = { skills: [], count: 0, plugins: null, marketplace: null, truncated: false }
  match = parse owner/repo from repoUrl
  if !match return empty

  branch = await detectBranch(owner, repo, token)
  mkt = await fetchMarketplaceManifest(owner, repo, token)

  // ALWAYS run tree-walk
  treeResult = await fetchGitTree(owner, repo, branch, token)
  if treeResult.error:
    // Tree-walk failed — degrade gracefully
    if mkt:
      plugins = await discoverSkillsFromMarketplace(...)
      return { skills: plugins.flatMap(...), plugins, marketplace, truncated: true, error: treeResult.error }
    return { ...empty, error: treeResult.error }

  treeSkills = filter tree to *.SKILL.md and SKILL.md, reject via shouldRejectSkillPath

  if !mkt:
    // No manifest — current tree-walk-only behavior
    return { skills: treeSkills, count, plugins: null, marketplace: null, truncated: treeResult.truncated }

  // Manifest present — merge
  plugins = await discoverSkillsFromMarketplace(owner, repo, mkt.branch, mkt.manifest, token)
  registeredPaths = new Set(plugins.flatMap(p => p.skills.map(s => s.path)))
  orphans = treeSkills.filter(s => !registeredPaths.has(s.path))

  return {
    skills: [...plugins.flatMap(p => p.skills), ...orphans.map(o => ({ ...o, plugin: null }))],
    count: registered + orphans.length,
    plugins,
    marketplace: { name: mkt.manifest.name, version: ... },
    truncated: treeResult.truncated,
  }
```

### Type extension

```ts
interface DiscoveredSkill {
  name: string;
  path: string;
  plugin?: string | null;  // NEW: explicit plugin name when registered, null/absent when orphan
}
```

Existing consumers either ignore `plugin` (search index, outbox-writer with nullable pluginName) or already handle missing plugin.

## Test Strategy

Strict TDD. RED tests for each AC, then minimum-viable code.

### New test file structure (additions to scanner-discovery.test.ts)

1. **describe "marketplace + orphan top-level skills (0730)"**
   - AC-US1-01: manifest + 5 registered + 2 top-level SKILL.md → returns 7 skills, 2 with plugin=null
   - AC-US1-02: orphan skills carry `plugin: null` marker
   - AC-US1-03: tree-walk 502s → returns marketplace skills + truncated=true
   - AC-US1-04: registered "foo" at plugins/x/skills/foo + top-level skills/foo → both kept (different paths)
   - AC-US1-05: top-level .claude/skills/foo/SKILL.md → still rejected
   - AC-US1-06: empty plugins + top-level SKILL.md → returns the orphan

2. **describe "no double-counting (0730)"**
   - AC-US2-01: nested-layout plugin → its own paths excluded from orphans
   - AC-US2-02: flat-layout plugin (skills="./") → plugin SKILL.md excluded from orphans
   - AC-US2-03: explicit-array plugin → all listed paths excluded from orphans
   - AC-US2-04: total = registered + orphans, zero intersection

### Updates to existing tests

The "empty plugins array" test at line ~223 currently asserts the old behavior. Either:
- Remove it (replaced by AC-US1-06)
- Update its expectation to match new behavior

Decision: update + keep — same test name, new expectation. Annotates the change in commit history.

### Regression anchors

- All current "marketplace" tests must still pass (5 registered → 7 skills found, etc.)
- All current "tree-walk fallback" tests (no marketplace) must still pass
- Path rejection (`shouldRejectSkillPath`) tests unchanged

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Extra GitHub API call per discovery (rate-limit pressure) | Tree-walk uses one Git Trees API call (`?recursive=1`) — already used by fallback path. Net cost: marketplace-mode discovery now does +1 call. At submit time this runs once per submission. Scheduler is bounded by existing rate-limit handling. |
| Existing consumers break on `plugin: null` orphans | `outbox-writer` already accepts null plugin via tree-walk-only flow. `submission/publish.ts` already has `pluginName: null` fallback. Verified via grep: no consumer asserts non-null. |
| Path filter mis-computes covered set for flat layout | Test AC-US2-02 explicitly covers flat layout. Implementation reads paths from `discoverSkillsFromMarketplace` output (which already returns the correct file paths, regardless of layout — see scanner.ts:411,434,466) so we just collect those into a Set. |
| Tree-walk returns truncated when repo has > 100k files | Existing `data.truncated` flag is propagated; `truncated: true` on result already documented. Orphan detection becomes incomplete in this case — acceptable for v1 (rare). |
| Removing the "early return" changes hot-path latency | Marketplace mode previously made N parallel calls (one per plugin). Adding +1 tree-walk in parallel doesn't extend wall-clock significantly. Could even be done via Promise.all with marketplace fetch. |

## ADRs

No new ADR required — this is a defect fix bringing actual behavior in line with documented contract ("We'll find all SKILL.md files"). Existing ADR-002 (integrity / Merkle root) and ADR-004 (semver) are unaffected; orphans go through the same publish path.

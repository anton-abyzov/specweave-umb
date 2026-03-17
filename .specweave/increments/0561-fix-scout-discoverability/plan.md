# Architecture Plan: Fix Scout Skill Discoverability

## Problem Analysis

Scout lives at `plugins/skills/skills/scout/SKILL.md` in the `anton-abyzov/vskill` repo. Three independent discovery systems fail to find it because they only match two patterns:

1. Root: `SKILL.md`
2. Skills dir: `skills/{name}/SKILL.md`

None match `plugins/{plugin}/skills/{name}/SKILL.md` (unless it matches the framework exclusion regex `plugins/specweave*/skills/`).

### Affected Systems (3 layers)

```
Layer 1 -- CLI Discovery (vskill repo)
  github-tree.ts::discoverSkills()
  Regex: /^skills\/([^/]+)\/SKILL\.md$/
  MISSES: plugins/*/skills/*/SKILL.md

Layer 2 -- Platform Discovery (vskill-platform repo)
  scanner.ts::discoverSkillsEnhanced()        -- tree-based fallback
  crawl-worker/lib/skill-discovery.js          -- VM scanner
  crawl-worker/sources/vendor-org-discovery.js -- vendor org scanner
  These use shouldRejectSkillPath() denylist --
  plugin skills PASS THROUGH correctly.
  They discover ANY path ending in /SKILL.md.

Layer 3 -- Search & Display (vskill-platform repo)
  search-index.ts -- builds KV shards from DB rows
  search.ts       -- edge KV search + Postgres fallback
  PublisherSkillsList.tsx -- reads from /api/v1/authors/*/skills
  These render whatever is in the DB -- no filtering issue.
```

### Root Cause Diagnosis

The problem has TWO distinct causes:

**Cause A -- CLI discovery gap (vskill repo)**: `github-tree.ts::discoverSkills()` uses an allowlist with only two patterns. Skills at `plugins/*/skills/*/SKILL.md` are invisible to the CLI. Running `vskill install anton-abyzov/vskill` never shows Scout.

**Cause B -- Platform DB may be missing Scout**: The platform-side discovery (`discoverSkillsEnhanced`, `discoverSkillsInRepo`, `vendor-org-discovery`) uses a broader denylist approach -- they match ANY `SKILL.md` and only reject agent-config and framework-plugin paths. Since `plugins/skills/` does NOT match `FRAMEWORK_PLUGIN_RE` (`/^plugins\/specweave[^/]*\/skills\//`), Scout should pass through. However, if the vskill repo was crawled before enhanced discovery was deployed, or if expansion failed, Scout may never have reached the DB. This requires verification and potential re-submission.

## Architecture Decisions

### ADR-1: Extend CLI discovery to support plugin skill paths

**Decision**: Add a third pattern to `github-tree.ts::discoverSkills()` that matches `plugins/{plugin}/skills/{name}/SKILL.md`, excluding framework plugins (`plugins/specweave*/`).

**Pattern**:
```
/^plugins\/(?!specweave)[^/]+\/skills\/([^/]+)\/SKILL\.md$/
```

Matches:
- `plugins/skills/skills/scout/SKILL.md` -> name: "scout"
- `plugins/marketing/skills/social-media-posting/SKILL.md` -> name: "social-media-posting"
- `plugins/google-workspace/skills/gws/SKILL.md` -> name: "gws"

Does NOT match:
- `plugins/specweave/skills/pm/SKILL.md` (framework, excluded)
- `plugins/specweave-github/skills/push/SKILL.md` (framework, excluded)

**Rationale**: The CLI's `discoverSkills` is the only discovery mechanism using an allowlist approach. All platform-side discovery uses a denylist. Aligning CLI with the platform's exact denylist approach is tempting but inappropriate -- the CLI installs skills directly into the user's agent config without security scanning, so being conservative about auto-discovery is correct.

**Trade-offs**:
- Pro: Minimal, targeted change. Framework plugins stay excluded.
- Pro: Consistent with existing pattern structure (additive only).
- Con: Two slightly different discovery approaches between CLI and platform. Acceptable because they serve different security contexts.

### ADR-2: No changes to platform-side discovery

**Decision**: No code changes needed to `discoverSkillsEnhanced`, `discoverSkillsInRepo`, `vendor-org-discovery`, or `shouldRejectSkillPath`. These already correctly discover and accept `plugins/*/skills/*/SKILL.md` paths.

**Action**: Verify Scout is in the platform DB. If missing, trigger a manual submission via the bulk API. This is an operational step, not a code change.

### ADR-3: Agent file collection for plugin skills

**Decision**: Extend the agent file matching in `discoverSkills()` to also collect `plugins/{plugin}/skills/{name}/agents/*.md` files.

**Rationale**: Skills installed from plugin paths need their agent files. Without this, plugin skills install without agent configurations. The existing pattern for `skills/{name}/agents/*.md` must be mirrored for `plugins/{plugin}/skills/{name}/agents/*.md`.

## Component Design

### Component 1: CLI Discovery Extension

**File**: `repositories/anton-abyzov/vskill/src/discovery/github-tree.ts`

**Change**: Add two new match blocks in the `for (const entry of tree)` loop, AFTER the existing `skills/{name}/SKILL.md` match:

```typescript
// plugins/{plugin}/skills/{name}/SKILL.md -- non-framework plugins only
// IMPORTANT: Only match non-specweave plugins. Framework plugins are
// handled by installRepoPlugin and should never appear in discovery.
const pluginMatch = entry.path.match(
  /^plugins\/(?!specweave)[^/]+\/skills\/([^/]+)\/SKILL\.md$/
);
if (pluginMatch) {
  const skillName = pluginMatch[1];
  skills.push({
    name: skillName,
    path: entry.path,
    rawUrl: `https://raw.githubusercontent.com/${owner}/${repo}/${branch}/${entry.path}`,
  });
  continue;
}

// plugins/{plugin}/skills/{name}/agents/*.md
const pluginAgentMatch = entry.path.match(
  /^plugins\/(?!specweave)[^/]+\/skills\/([^/]+)\/agents\/([^/]+\.md)$/
);
if (pluginAgentMatch) {
  const skillName = pluginAgentMatch[1];
  const agentFilename = pluginAgentMatch[2];
  let map = agentFilesBySkill.get(skillName);
  if (!map) {
    map = {};
    agentFilesBySkill.set(skillName, map);
  }
  map[`agents/${agentFilename}`] =
    `https://raw.githubusercontent.com/${owner}/${repo}/${branch}/${entry.path}`;
}
```

**Ordering constraint**: New match MUST come AFTER existing `skills/{name}/SKILL.md`. If a skill name exists at both `skills/scout/SKILL.md` and `plugins/foo/skills/scout/SKILL.md`, the skills-dir version takes priority via `continue`.

**Description enrichment**: Already handled -- the existing parallel fetch loop at the end of `discoverSkills()` iterates over all entries in the `skills` array and fetches descriptions from each `rawUrl`. No changes needed.

### Component 2: Platform DB Verification (operational)

No code changes. After CLI fix is deployed:

1. Query platform DB: does a Skill record with `skillPath` containing `plugins/skills/skills/scout` exist?
2. If missing, POST to `/api/v1/submissions/bulk` with:
   ```json
   {
     "repos": [{
       "repoUrl": "https://github.com/anton-abyzov/vskill",
       "skillName": "scout",
       "skillPath": "plugins/skills/skills/scout/SKILL.md",
       "source": "manual"
     }]
   }
   ```
3. After submission completes the scan pipeline, verify Scout appears in search via `vskill search scout`

## Data Flow

```
CLI: vskill install anton-abyzov/vskill
  |
  v
discoverSkills("anton-abyzov", "vskill")
  |
  v
GitHub Trees API: GET /repos/anton-abyzov/vskill/git/trees/{branch}?recursive=1
  |
  v
Match loop (sequential priority):
  1. path == "SKILL.md"                                     [existing]
  2. /^skills\/([^/]+)\/SKILL\.md$/                         [existing]
  3. /^plugins\/(?!specweave)[^/]+\/skills\/([^/]+)\/SKILL\.md$/ [NEW]
  |
  v
Result: [{name: "scout", path: "plugins/skills/skills/scout/SKILL.md", ...}, ...]
  |
  v
Parallel description fetch (3s timeout per skill)
  |
  v
Interactive selection -> install
```

## Testing Strategy

### Unit Tests (`github-tree.test.ts`)

| # | Test Case | Input Path | Expected |
|---|-----------|------------|----------|
| 1 | Plugin skill discovery | `plugins/skills/skills/scout/SKILL.md` | Discovered, name="scout" |
| 2 | Multiple plugin skills | `plugins/marketing/skills/social-media-posting/SKILL.md` | Discovered, name="social-media-posting" |
| 3 | Framework exclusion | `plugins/specweave/skills/pm/SKILL.md` | NOT discovered |
| 4 | Framework variant exclusion | `plugins/specweave-github/skills/push/SKILL.md` | NOT discovered |
| 5 | Dedup: skills/ wins over plugins/ | Both `skills/scout/SKILL.md` AND `plugins/x/skills/scout/SKILL.md` | Only one "scout" entry |
| 6 | Plugin agent files | `plugins/skills/skills/scout/agents/research.md` | Agent URL attached to scout |
| 7 | Deeply nested (rejected) | `plugins/a/b/c/skills/x/SKILL.md` | NOT discovered (too deep) |
| 8 | Existing patterns unchanged | `SKILL.md`, `skills/foo/SKILL.md` | Still discovered (regression check) |

### Integration Verification

1. Run `vskill install anton-abyzov/vskill` and confirm Scout appears in the skill list
2. Run `vskill search scout` and confirm it appears in platform search results

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Framework plugins accidentally discovered | Very Low | High | Negative lookahead `(?!specweave)` in regex |
| Name collision skills/ vs plugins/*/skills/ | Low | Medium | First-match-wins via `continue` |
| Breaking existing discovery | Very Low | High | Additive-only change; existing patterns untouched |
| Platform DB still missing Scout post-fix | Medium | Low | Manual submission as operational step |

## Implementation Order

1. Extend `github-tree.ts::discoverSkills()` with plugin skill + agent file patterns
2. Unit tests for all new patterns + regression tests for existing patterns
3. Verify Scout in platform DB, manual re-submission if needed
4. End-to-end verification: CLI install + platform search

## Out of Scope

- Changing platform-side discovery code (already works)
- Changing search indexing logic (indexes whatever is in the DB)
- Changing publisher page UI (displays whatever the API returns)
- Supporting arbitrary nesting depths beyond `plugins/*/skills/*/SKILL.md`
- Changing the `installRepoPlugin` flow (marketplace plugin installation)

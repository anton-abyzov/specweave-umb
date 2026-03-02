# Implementation Plan: Fix marketplace install routing and find grouping

## Overview

Fix five interrelated issues in vskill's install routing and find command. All changes are localized to four existing files with no new modules. The core change is making `detectMarketplaceRepo` resilient (retry + raw fallback), then inserting marketplace-first checks into the two code paths (3-part format, `--skill` flag) that currently bypass it.

## Architecture

### Changed Components

| File | Changes | Complexity |
|------|---------|------------|
| `src/commands/add.ts` | Retry+fallback in `detectMarketplaceRepo`, marketplace-first routing in 3-part and `--skill` branches, fix tip message | Medium |
| `src/commands/find.ts` | Group results by `repoUrl`, per-group install hints | Medium |
| `src/discovery/github-tree.ts` | Add rate-limit warning helper (shared), defensive comment on regex | Low |
| `src/marketplace/marketplace.ts` | Add `hasPlugin(name, content)` helper | Low |

### No New Modules

All changes fit within existing files. The rate-limit warning helper is a module-level utility in `github-tree.ts` (already the home for GitHub API interactions) and is imported by `add.ts`.

## Key Design Decisions

### D-001: Retry strategy in `detectMarketplaceRepo`

**Decision**: Retry the Contents API once (1s delay), then fallback to `raw.githubusercontent.com`.

**Rationale**: The raw.githubusercontent.com endpoint does not count against GitHub API rate limits, making it a reliable fallback. A single retry handles transient network blips. Two retries would add 2+ seconds of latency for genuine 404s (non-marketplace repos).

**Implementation**:
```
Contents API → (fail) → wait 1s → Contents API → (fail) → raw fallback → (fail) → { isMarketplace: false }
```

The raw fallback needs the default branch, which is already cached by `getDefaultBranch` (called earlier in the flow or warm from prior calls). If the branch cache is cold, `getDefaultBranch` itself makes one API call, but that call uses the repo metadata endpoint (not contents), so it is a separate rate-limit bucket.

### D-002: Marketplace-first routing for 3-part and `--skill`

**Decision**: Insert `detectMarketplaceRepo` call before `installSingleSkillLegacy` in both paths. If marketplace detected AND name matches a plugin, route to marketplace. Otherwise fall through unchanged.

**Rationale**: The marketplace check is cheap (single API call, cached after first use per process). The fallthrough preserves backward compatibility for non-marketplace repos. Matching plugin name by exact string comparison (case-sensitive) matches existing `getPluginSource` behavior.

**Pre-selection**: `installMarketplaceRepo` currently shows all plugins unchecked. To pre-select a specific plugin, pass a new optional parameter `preSelected?: string[]` that pre-checks matching items in the checkbox list. When `--yes` is also set, it installs only the pre-selected plugin(s) instead of all.

### D-003: Find grouping strategy

**Decision**: Group results by `repoUrl` in the display layer only. Groups with 2+ entries get a header row; singletons render as before.

**Rationale**: The API response is a flat array. Grouping is purely a presentation concern. The `table()` utility takes `string[][]` rows, so grouped output uses the same table with inserted header/separator rows containing merged cells.

**JSON mode**: Unaffected -- the flat array is returned before any grouping logic runs.

### D-004: Rate-limit warning dedup

**Decision**: Module-level `let rateLimitWarned = false` flag in `github-tree.ts`, exported as a helper `warnRateLimitOnce()`. Both `detectMarketplaceRepo` (in `add.ts`) and `discoverSkills` (in `github-tree.ts`) call this helper.

**Rationale**: A module-level flag is the simplest dedup mechanism for a single CLI invocation. No persistence needed since the CLI is a one-shot process.

## Implementation Phases

### Phase 1: Foundation (US-001, US-005)

**Resilient marketplace detection + rate-limit warning**

1. Add `warnRateLimitOnce(res: Response)` to `github-tree.ts` -- checks 403 + `x-ratelimit-remaining: 0` header, prints yellow warning once
2. Refactor `detectMarketplaceRepo` in `add.ts`:
   - Wrap existing Contents API call in a retry loop (max 1 retry, 1s delay)
   - On 403, call `warnRateLimitOnce`
   - After retry exhaustion, fallback to `raw.githubusercontent.com/{owner}/{repo}/{branch}/.claude-plugin/marketplace.json`
   - Parse with existing `getAvailablePlugins` validator
3. Add `hasPlugin(name, content)` convenience to `marketplace.ts` (thin wrapper over `getPluginSource !== null`)

### Phase 2: Core Routing (US-002, US-004)

**Marketplace-first routing + tip fix**

4. 3-part format (line ~1441): Before `installSingleSkillLegacy`, call `detectMarketplaceRepo(owner, repo)`. If marketplace AND `hasPlugin(threeSkill, manifest)`, call `installMarketplaceRepo` with `preSelected: [threeSkill]`
5. `--skill` flag (line ~1457): Same pattern -- detect marketplace, check plugin match, route or fall through
6. Add `preSelected` parameter to `installMarketplaceRepo` signature. When set, pre-check those items in the checkbox list. When `--yes` + `preSelected`, install only the pre-selected plugins
7. Fix tip at line ~1690: Use `vskill install ${ownerRepo}` when no `pluginName`, or `vskill install ${ownerRepo} --plugin ${detail.pluginName}` when present
8. Also fix the generic tip at line ~1449: Change from `owner/repo or owner/repo/skill` to just `owner/repo`

### Phase 3: Find Grouping (US-003)

**Display grouping in find results**

9. In `findCommand`, after sorting and before rendering:
   - Group results by `repoUrl` (Map<string, SkillSearchResult[]>)
   - Entries with no `repoUrl` or unique `repoUrl` go to a "standalone" bucket
   - For groups with 2+ entries: insert a header row (marketplace name from first skill's repoUrl), then indented skill rows
   - After the table, show per-group install hints for marketplace groups
10. Standalone entries keep the existing per-skill install hint

### Phase 4: Guard Tests (US-004)

11. Add negative test to `github-tree.test.ts`: confirm `plugins/foo/SKILL.md` path does NOT match `discoverSkills` regex
12. Add defensive comment on the regex in `github-tree.ts`

## Testing Strategy

### Unit Tests (Vitest)

| Test Area | File | Key Scenarios |
|-----------|------|---------------|
| Retry + fallback | `add.test.ts` | API 200 first try; API 500 then 200; API 500+500 then raw 200; API 403 rate limit; all fail |
| 3-part marketplace routing | `add.test.ts` | 3-part with marketplace match; 3-part with marketplace miss; 3-part with non-marketplace |
| `--skill` marketplace routing | `add.test.ts` | Same pattern as 3-part |
| Pre-selection in marketplace | `add.test.ts` | preSelected filters checkbox; --yes with preSelected installs subset |
| Tip message fix | `add.test.ts` | With pluginName; without pluginName |
| Find grouping | `find.test.ts` | 2+ skills same repo grouped; singleton not grouped; no repoUrl not grouped; JSON unaffected |
| Rate-limit warning | `github-tree.test.ts` | 403 with header prints once; 403 without header no warning; second 403 no duplicate |
| Discovery scope | `github-tree.test.ts` | `plugins/foo/SKILL.md` not matched |
| `hasPlugin` helper | `marketplace.test.ts` | Match found; match not found; invalid JSON |

### Mock Strategy

All tests mock `fetch` at the module level (existing pattern in `add.test.ts`). The retry tests use a fetch mock that returns different responses on sequential calls.

## Technical Challenges

### Challenge 1: `installMarketplaceRepo` pre-selection

**Problem**: Currently all checkboxes start unchecked. Pre-selecting requires threading a parameter through the function signature.

**Solution**: Add optional `preSelected?: string[]` to `installMarketplaceRepo`. When present, set `checked: true` for matching plugin names in the `promptCheckboxList` items. When `--yes` and `preSelected` are both set, skip the prompt and install only the pre-selected plugins (not all).

**Risk**: Low. The parameter is optional and defaults to existing behavior.

### Challenge 2: Table grouping without breaking column alignment

**Problem**: The `table()` function expects uniform `string[][]` rows. Header rows for groups need to span all columns or use a different rendering approach.

**Solution**: Render grouped output as a series of per-group sections, each with its own mini-table for the skills, preceded by a bold header line. Standalone skills render in a single table at the end. This avoids stretching the `table()` function.

**Risk**: Medium. The visual output changes. Mitigation: test with real terminal output to verify alignment.

### Challenge 3: Raw fallback branch resolution

**Problem**: The raw fallback URL needs the default branch name. If `getDefaultBranch` itself is rate-limited, the fallback chain breaks.

**Solution**: `getDefaultBranch` caches results. If the cache is warm (likely, since marketplace detection runs after other GitHub calls), no extra API call is needed. If cold, `getDefaultBranch` falls back to "main" on any error, which is correct for the vast majority of repos.

**Risk**: Low. The "main" fallback is already battle-tested.

## File Change Summary

```
src/commands/add.ts        ~80 lines changed  (retry, routing, tip, preSelected param)
src/commands/find.ts       ~60 lines changed  (grouping logic + hint rendering)
src/discovery/github-tree.ts ~20 lines added  (warnRateLimitOnce, comment)
src/marketplace/marketplace.ts ~10 lines added (hasPlugin helper)
src/commands/add.test.ts   ~120 lines added   (retry, routing, tip tests)
src/commands/find.test.ts  ~60 lines added    (grouping tests)
src/discovery/github-tree.test.ts ~30 lines added (rate-limit, scope guard tests)
src/marketplace/marketplace.test.ts ~15 lines added (hasPlugin tests)
```

Total estimated: ~395 lines across 8 files (4 source + 4 test).

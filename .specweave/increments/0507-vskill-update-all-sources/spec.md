---
increment: 0507-vskill-update-all-sources
title: 'vskill update: unified skill update across all source types'
type: feature
priority: P1
status: completed
created: 2026-03-12T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: vskill update: unified skill update across all source types

## Overview

`vskill update` currently hardcodes all updates through the verified-skill.com registry API (`getSkill()`). Skills installed from GitHub repos, marketplace plugins, or local paths fail silently because the registry has no record of them. This feature makes `update` parse the lockfile `source` field to determine the correct fetch strategy per source type, so every installed skill can be updated from its actual origin.

## User Stories

### US-001: Source-Aware Update Routing (P1)
**Project**: vskill

**As a** vskill user
**I want** `vskill update` to parse the lockfile `source` field and fetch from the correct origin
**So that** skills installed from any source type are updated properly instead of failing silently

**Acceptance Criteria**:
- [x] **AC-US1-01**: `source` field is parsed into a typed discriminant: `registry:`, `github:` (flat), `github:...#plugin:` (plugin dir), `marketplace:`, `local:`
- [x] **AC-US1-02**: `registry:name` sources fetch via existing `getSkill()` API call (unchanged behavior)
- [x] **AC-US1-03**: `github:owner/repo` sources fetch SKILL.md from `raw.githubusercontent.com` using detected default branch
- [x] **AC-US1-04**: `github:owner/repo#plugin:name` sources with `pluginDir === true` re-fetch the full plugin directory (all `skills/*/SKILL.md` files under the plugin)
- [x] **AC-US1-05**: `marketplace:owner/repo#name` sources re-fetch `marketplace.json` from GitHub raw URL, resolve the plugin source path, then fetch the SKILL.md content
- [x] **AC-US1-06**: `local:*` sources print an informational skip message ("managed by specweave refresh-plugins") and do not attempt a fetch
- [x] **AC-US1-07**: Missing or unrecognized source prefixes fall back to registry lookup via `getSkill()` with a dim warning printed

---

### US-002: SHA-Based Change Detection (P1)
**Project**: vskill

**As a** vskill user
**I want** update to compare SHA hashes before overwriting skill files
**So that** unchanged skills are skipped efficiently and I see clear before/after output

**Acceptance Criteria**:
- [x] **AC-US2-01**: SHA-256 hash (truncated to 12 chars) of fetched content is compared against `entry.sha` in lockfile
- [x] **AC-US2-02**: When SHA matches, skill is skipped with `dim` "already up to date" message
- [x] **AC-US2-03**: When SHA differs, the old SHA and new SHA are printed in the format `name: oldsha -> newsha`
- [x] **AC-US2-04**: Lockfile `sha` field is updated after successful write for all source types

---

### US-003: Security Scanning on All Sources (P1)
**Project**: vskill

**As a** vskill user
**I want** Tier 1 security scanning applied to all fetched content regardless of source type
**So that** malicious content is blocked even from trusted-seeming origins like GitHub or local paths

**Acceptance Criteria**:
- [x] **AC-US3-01**: `runTier1Scan()` is called on every fetched content blob before writing to disk
- [x] **AC-US3-02**: Scan verdict FAIL prevents the skill from being updated (same as current registry behavior)
- [x] **AC-US3-03**: Scan verdict and score are printed for every updated skill
- [x] **AC-US3-04**: `local:*` sources are excluded from scanning since they are skipped entirely

---

### US-004: Graceful Failure Handling (P2)
**Project**: vskill

**As a** vskill user
**I want** partial update failures to not block successful updates
**So that** a single network error does not prevent other skills from updating

**Acceptance Criteria**:
- [x] **AC-US4-01**: When a source fetch fails (network error, 404, rate limit), a yellow warning is printed with the skill name and error message
- [x] **AC-US4-02**: The update loop continues to the next skill after a failure
- [x] **AC-US4-03**: The lockfile is written once after the loop with all successful updates applied
- [x] **AC-US4-04**: `GITHUB_TOKEN` from environment is propagated to GitHub API calls (branch detection, marketplace.json fetch) to reduce rate limiting
- [x] **AC-US4-05**: The final summary reports count of updated skills and lists any that failed

---

### US-005: Plugin Directory Full Update (P2)
**Project**: vskill

**As a** vskill user
**I want** plugin-dir sources to update all skills within the plugin, not just a single SKILL.md
**So that** multi-skill plugins from GitHub are fully synchronized

**Acceptance Criteria**:
- [x] **AC-US5-01**: When `entry.pluginDir === true`, the update re-discovers all `skills/*/SKILL.md` paths under the plugin using the GitHub Trees API
- [x] **AC-US5-02**: Each discovered skill file is fetched, scanned, and written to the agent's skill directory
- [x] **AC-US5-03**: The lockfile entry SHA is computed from the combined content of all skill files in the plugin
- [x] **AC-US5-04**: Agent file entries that no longer exist upstream (skill removed from plugin) are not deleted -- only additions and updates are applied

## Functional Requirements

### FR-001: Source Parser Module
A `parseSource(source: string)` function parses the lockfile `source` field into a typed result:
- `{ type: "registry", name: string }`
- `{ type: "github", owner: string, repo: string }`
- `{ type: "github-plugin", owner: string, repo: string, pluginName: string }`
- `{ type: "marketplace", owner: string, repo: string, pluginName: string }`
- `{ type: "local", path: string }`
- `{ type: "unknown", raw: string }` (fallback)

### FR-002: Fetch Strategy Per Source Type
Each parsed source type maps to a fetch function that returns `{ content: string, version?: string }` or throws on failure. The fetch functions reuse existing utilities (`getDefaultBranch`, `getSkill`, `discoverSkills`, marketplace helpers).

### FR-003: GITHUB_TOKEN Propagation
GitHub API requests (Trees API, raw content) include an `Authorization: token <GITHUB_TOKEN>` header when `process.env.GITHUB_TOKEN` is set. Raw.githubusercontent.com requests for public repos work without auth.

## Success Criteria

- `vskill update --all` successfully updates skills from all 5 source types in a single run
- Zero silent failures -- every source type either updates, skips (up-to-date/local), or reports an error
- Existing `registry:` update behavior is unchanged (backward compatible)
- Test coverage >= 90% for the new source parser and fetch routing logic

## Out of Scope

- Lockfile schema changes (no new fields added to `SkillLockEntry`)
- Auto-migration of lockfiles missing `source` field (handled by fallback)
- Interactive prompts during update (overwrite is always default, guarded by SHA comparison)
- Updating the `specweave refresh-plugins` flow for `local:` sources
- Deleting skills that were removed from upstream plugin directories

## Dependencies

- `src/discovery/github-tree.ts` -- `getDefaultBranch()`, `discoverSkills()` for GitHub source fetching
- `src/api/client.ts` -- `getSkill()` for registry fallback
- `src/marketplace/index.ts` -- `getAvailablePlugins()`, `getPluginSource()` for marketplace resolution
- `src/scanner/index.ts` -- `runTier1Scan()` for security scanning
- `src/lockfile/types.ts` -- `SkillLockEntry.source` field (existing, no changes)

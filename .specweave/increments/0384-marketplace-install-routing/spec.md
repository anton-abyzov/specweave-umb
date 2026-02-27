---
increment: 0384-marketplace-install-routing
title: Fix marketplace install routing and find grouping
type: feature
priority: P1
status: completed
created: 2026-02-27T00:00:00.000Z
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Fix marketplace install routing and find grouping

## Overview

Fix several interrelated issues in vskill's install routing, marketplace detection, find command output, and discovery scope. The 3-part format (`owner/repo/skill`) and `--skill` flag silently bypass marketplace detection, `discoverSkills` scans `plugins/` which it should not, `find` outputs a flat list without grouping by repo, the tip on line 1690 suggests broken 3-part format instead of `--plugin`, and marketplace API rate limits are silently swallowed instead of shown to the user.

**Project**: vskill

## User Stories

### US-001: Resilient marketplace detection (P1)
**Project**: vskill

**As a** vskill user
**I want** marketplace detection to retry once and fall back to raw content fetch on GitHub API failure
**So that** transient API errors do not silently bypass the marketplace install flow

**Acceptance Criteria**:
- [x] **AC-US1-01**: `detectMarketplaceRepo` retries the GitHub Contents API call once (1 retry, ~1s delay) before returning `{ isMarketplace: false }`
- [x] **AC-US1-02**: If the Contents API fails after retry, `detectMarketplaceRepo` falls back to fetching raw `marketplace.json` via `raw.githubusercontent.com` before giving up
- [x] **AC-US1-03**: On GitHub API 403 with rate-limit headers, a yellow warning is printed: "GitHub API rate limit reached. Falling back to raw content fetch." with guidance to set `GITHUB_TOKEN`

---

### US-002: Route 3-part and --skill formats through marketplace check (P1)
**Project**: vskill

**As a** vskill user
**I want** `vskill install owner/repo/name` and `vskill install owner/repo --skill name` to check marketplace first
**So that** marketplace plugins are installed through the marketplace flow even when a specific plugin name is given

**Acceptance Criteria**:
- [x] **AC-US2-01**: When the 3-part format `owner/repo/name` is used, `addCommand` first calls `detectMarketplaceRepo(owner, repo)`. If the repo is a marketplace AND the third part matches a plugin name in `marketplace.json`, route to `installMarketplaceRepo` (pre-selecting that plugin)
- [x] **AC-US2-02**: When `--skill name` is used with `owner/repo`, `addCommand` first calls `detectMarketplaceRepo(owner, repo)`. If the repo is a marketplace AND the skill name matches a plugin name in `marketplace.json`, route to `installMarketplaceRepo` (pre-selecting that plugin)
- [x] **AC-US2-03**: If marketplace detection succeeds but the given name does NOT match any plugin in the manifest, fall through to the existing skill install path (`installSingleSkillLegacy`)
- [x] **AC-US2-04**: If marketplace detection fails (not a marketplace repo), the existing behavior is preserved unchanged

---

### US-003: Group find results by repository (P2)
**Project**: vskill

**As a** vskill user
**I want** `vskill find` results to be grouped by `repoUrl` when multiple skills share a repo
**So that** I can see which skills come from the same marketplace and get a single install hint per repo

**Acceptance Criteria**:
- [x] **AC-US3-01**: When multiple results share the same `repoUrl`, they are grouped under a marketplace header showing `owner/repo` with indented plugin rows beneath
- [x] **AC-US3-02**: Each group displays a group-level install hint: `npx vskill install owner/repo` (installs all plugins via marketplace flow)
- [x] **AC-US3-03**: Individual (ungrouped) skills show the existing per-skill install hint: `npx vskill install owner/repo --plugin name`
- [x] **AC-US3-04**: Skills without a `repoUrl` or with a unique `repoUrl` remain as standalone rows (no grouping)
- [x] **AC-US3-05**: JSON output mode (`--json`) is unaffected by grouping (flat array as before)

---

### US-004: Fix tip message and discovery scope (P1)
**Project**: vskill

**As a** vskill user
**I want** the install tip to show the correct command format and `discoverSkills` to only scan `skills/` (not `plugins/`)
**So that** tips work when copy-pasted and discovery does not surface plugin internals

**Acceptance Criteria**:
- [x] **AC-US4-01**: The tip on line ~1690 of `add.ts` (`installFromRegistry`) shows `vskill install owner/repo` (not `owner/repo/skill`). When `detail.pluginName` is present, the tip appends `--plugin <pluginName>`
- [x] **AC-US4-02**: `discoverSkills` in `github-tree.ts` only matches `skills/{name}/SKILL.md` pattern, never `plugins/{name}/SKILL.md` or any other subdirectory
- [x] **AC-US4-03**: The existing regex `^skills\/([^/]+)\/SKILL\.md$` is confirmed correct (it already excludes `plugins/`); add an explicit negative test to prevent regression

---

### US-005: Show rate-limit warning on GitHub API 403 (P2)
**Project**: vskill

**As a** vskill user
**I want** to see a yellow warning when GitHub API returns 403 due to rate limiting
**So that** I understand why marketplace detection or discovery failed and can set `GITHUB_TOKEN` to fix it

**Acceptance Criteria**:
- [x] **AC-US5-01**: When any GitHub API call in `detectMarketplaceRepo` or `discoverSkills` receives HTTP 403 with `x-ratelimit-remaining: 0`, a yellow warning is printed: "GitHub API rate limit reached. Set GITHUB_TOKEN for higher limits."
- [x] **AC-US5-02**: The warning is printed at most once per CLI invocation (dedup via module-level flag)
- [x] **AC-US5-03**: After the warning, the function continues with its existing fallback behavior (return empty / return false)

## Functional Requirements

### FR-001: Retry + raw fallback in detectMarketplaceRepo
- On first GitHub Contents API failure (non-200, network error), wait ~1s and retry once
- If retry also fails, attempt raw fetch: `https://raw.githubusercontent.com/{owner}/{repo}/{branch}/.claude-plugin/marketplace.json`
- Raw fallback uses `getDefaultBranch` (already cached) for the branch
- Parse and validate with `getAvailablePlugins` as before

### FR-002: Marketplace-first routing for 3-part and --skill
- In the 3-part branch (line ~1441), before calling `installSingleSkillLegacy`, call `detectMarketplaceRepo(owner, repo)`
- If marketplace detected, check if `threeSkill` matches a plugin name via `getAvailablePlugins`
- If match found, call `installMarketplaceRepo` with pre-selection of that plugin
- Same logic for `--skill` branch (line ~1457)

### FR-003: Find grouping by repoUrl
- After sorting results, group entries sharing the same non-null `repoUrl`
- Groups with 2+ entries get a header row and indented children
- Singleton entries render as before
- Group header: bold `owner/repo` with plugin count
- Group install hint: `npx vskill install owner/repo`

### FR-004: Fix tip at line ~1690
- Change from: `vskill install ${ownerRepo}/${detail.name}`
- Change to: `vskill install ${ownerRepo}` (when no pluginName)
- Change to: `vskill install ${ownerRepo} --plugin ${detail.pluginName}` (when pluginName present)

### FR-005: Discovery scope guard
- `discoverSkills` regex already excludes `plugins/` — add defensive comment and test
- No code change needed to regex itself; add negative test case

## Success Criteria

- All 5 user stories pass acceptance criteria with unit tests
- Existing `add.test.ts` and `find.test.ts` tests continue to pass
- No regression in marketplace install flow for the standard `owner/repo` case

## Out of Scope

- Changing the marketplace.json schema or format
- Adding GitHub token authentication to API calls (only warning about it)
- Redesigning the interactive TUI for find results
- Modifying the `installRepoPlugin` or `installAllRepoPlugins` functions
- Adding new CLI flags

## Dependencies

- GitHub Contents API (existing usage)
- `raw.githubusercontent.com` (existing usage for raw content fallback)
- `verified-skill.com` search API (for find results, unchanged)

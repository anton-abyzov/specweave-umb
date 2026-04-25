---
increment: 0730-scanner-merge-marketplace-and-tree
title: Scanner merges marketplace + orphan top-level skills
type: bug
priority: P1
status: completed
created: 2026-04-25T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# 0730 — Scanner merges marketplace + orphan top-level skills

## Overview

When a GitHub repository contains both a `.claude-plugin/marketplace.json` AND top-level `SKILL.md` files outside any registered plugin, the platform's scanner currently surfaces only the marketplace-registered skills. The submit page advertises "We'll find ALL SKILL.md files" but that contract breaks the moment a manifest is present. Fix: tree-walk regardless of manifest, and merge in any orphan SKILL.md paths as standalone skills.

## Problem

`vskill-platform/src/lib/scanner.ts:514-535` (`discoverSkillsEnhanced`) gives marketplace.json absolute precedence:

```ts
const mkt = await fetchMarketplaceManifest(owner, repo, token);
if (mkt) {
  const plugins = await discoverSkillsFromMarketplace(...);
  return { skills: allSkills, ... };  // EARLY RETURN — tree-walk skipped
}
// fall back: only when manifest missing
```

Confirmed by [`scanner-discovery.test.ts:223`](repositories/anton-abyzov/vskill-platform/src/lib/__tests__/scanner-discovery.test.ts:223) — `plugins: []` returns `skills: []`, no fallback.

Real-world repos hit this: e.g. `anton-abyzov/vskill` has 5 registered plugins (~7 skills) AND `skills/greet-anton/SKILL.md` + `skills/greet-elena/SKILL.md` at the root. The two greet skills are invisible to the platform regardless of submit path. The submit page's promise is broken.

## User Stories

### US-001: Submit-time discovery finds all SKILL.md files
**Project**: vskill-platform

**As a** skill author submitting a repo on verified-skill.com
**I want** every SKILL.md in my repo to be discovered, whether it's inside a marketplace-registered plugin or a top-level standalone skill
**So that** the submit page's "We'll find ALL SKILL.md files" promise is accurate and I don't lose visibility on standalone skills

**Acceptance Criteria**:
- [x] **AC-US1-01**: When a repo has both `marketplace.json` AND top-level `skills/<name>/SKILL.md` (not inside any registered plugin's source path), `discoverSkillsEnhanced` returns BOTH the marketplace skills AND the orphan top-level skill
- [x] **AC-US1-02**: Each orphan skill in the result carries a `plugin: null` marker (or distinct group label) to distinguish it from marketplace-registered skills
- [x] **AC-US1-03**: When the orphan tree-walk fails (rate-limit, 502, network error), discovery does NOT crash — it returns the marketplace skills with `truncated: true` set on the result
- [x] **AC-US1-04**: Orphan filter keys on file PATH (not skill name) — a registered plugin skill named `foo` and a top-level `skills/foo/SKILL.md` are treated as distinct entries with different paths
- [x] **AC-US1-05**: Orphan SKILL.md inside agent/IDE config dirs (`.claude/skills/...`, `.cursor/skills/...`) is still rejected via existing `shouldRejectSkillPath` rules — no security regression
- [x] **AC-US1-06**: Existing test "handles marketplace.json with empty plugins array" is updated: when `plugins: []` AND a top-level `SKILL.md` exists, scanner returns the orphan (was: empty array). Marketplace metadata is still attached to the result.

---

### US-002: No double-counting between marketplace and orphan branches
**Project**: vskill-platform

**As a** maintainer of the scanner
**I want** the orphan filter to exclude any path already covered by a registered plugin (flat layout, nested layout, or explicit array form)
**So that** the same SKILL.md never appears twice in the result

**Acceptance Criteria**:
- [x] **AC-US2-01**: For a marketplace plugin with `source: "./plugins/foo"` and default nested layout, every `plugins/foo/skills/*/SKILL.md` path in the tree-walk is excluded from the orphan set
- [x] **AC-US2-02**: For a marketplace plugin with flat layout (`source: "./plugins/foo", skills: "./"`), the file `plugins/foo/SKILL.md` is excluded from the orphan set
- [x] **AC-US2-03**: For a marketplace plugin with explicit array (`source: "./", skills: ["./skills/a", "./skills/b"]`), both `skills/a/SKILL.md` and `skills/b/SKILL.md` are excluded from the orphan set
- [x] **AC-US2-04**: After filtering, the result's total skill count equals `marketplace_skills.length + orphans.length` with zero overlap

## Out of Scope (Follow-ups)

- **Submit-page UI label** — visually distinguish "standalone" vs "in-plugin" skills in the submission preview. Defer to follow-up increment 0731.
- **Crawler scheduled-discovery delta** — the periodic scanner already calls `discoverSkillsEnhanced`, so it inherits the fix automatically. No schedule change needed.

## Dependencies

- Existing helpers: `fetchMarketplaceManifest`, `discoverSkillsFromMarketplace`, `shouldRejectSkillPath`, `githubHeaders` (no changes)
- `Skill.pluginName` Prisma column is already nullable (`schema.prisma:219`) — no DB migration
- `outbox-writer.ts` already accepts skills with null plugin name via the tree-walk-only path

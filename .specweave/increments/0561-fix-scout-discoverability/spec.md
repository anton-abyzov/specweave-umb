---
increment: 0561-fix-scout-discoverability
title: Fix Scout Skill Discoverability
status: completed
priority: P1
type: bugfix
created: 2026-03-17T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Fix Scout Skill Discoverability

## Problem Statement

Skills nested under `plugins/*/skills/*/SKILL.md` in the vskill repo are invisible to CLI discovery. The `discoverSkills()` function in `github-tree.ts` only matches root `SKILL.md` and `skills/*/SKILL.md` -- it explicitly skips the `plugins/` directory. This means 7 legitimate skills (including Scout) cannot be found via `vskill install --repo anton-abyzov/vskill`. On the platform side, Scout may not appear in search results due to missing crawl/index data, though the direct URL works.

## Goals

- All non-specweave plugin skills discoverable via `vskill install --repo`
- Scout and sibling skills appear in `vskill search` and platform search
- Regression tests prevent future discovery gaps

## User Stories

### US-VSKILL-001: CLI Discovery of Plugin-Nested Skills
**Project**: vskill
**As a** skill user
**I want** `vskill install --repo owner/repo` to discover skills under `plugins/*/skills/*/SKILL.md`
**So that** I can install Scout and other plugin-nested skills without knowing their exact path

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a repo with `plugins/skills/skills/scout/SKILL.md`, when running `discoverSkills(owner, repo)`, then Scout is included in the returned array with name "scout" and correct rawUrl
- [x] **AC-US1-02**: Given a repo with `plugins/specweave-github/skills/push/SKILL.md`, when running `discoverSkills(owner, repo)`, then that skill is NOT included (framework plugin exclusion preserved)
- [x] **AC-US1-03**: Given a repo with `plugins/marketing/skills/slack-messaging/SKILL.md`, when running `discoverSkills(owner, repo)`, then slack-messaging is included with name "slack-messaging"
- [x] **AC-US1-04**: Given a repo with agent files at `plugins/skills/skills/scout/agents/helper.md`, when running `discoverSkills()`, then `agentRawUrls` for Scout contains the agent file entry

### US-VSKILL-002: Regression Tests for Plugin Discovery
**Project**: vskill
**As a** developer
**I want** tests that verify non-specweave plugin paths are discoverable and specweave paths are excluded
**So that** future changes do not re-break plugin-nested skill discovery

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given a test with a mock GitHub tree containing paths for both `plugins/skills/skills/scout/SKILL.md` and `plugins/specweave/skills/pm/SKILL.md`, when `discoverSkills()` runs, then only the non-specweave skill is returned
- [x] **AC-US2-02**: Given a test with multiple non-specweave plugin skills (`plugins/marketing/skills/slack-messaging/SKILL.md`, `plugins/mobile/skills/appstore/SKILL.md`), when `discoverSkills()` runs, then all are returned with correct names and rawUrls

### US-PLATFORM-001: Re-crawl and Reindex Scout
**Project**: vskill-platform
**As a** platform operator
**I want** Scout and sibling plugin skills to appear in search results
**So that** users can find official skills via `vskill search` and the publisher page

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given Scout exists at `plugins/skills/skills/scout/SKILL.md` in the vskill repo, when a re-crawl is triggered, then Scout appears in the Skill table in Postgres
- [x] **AC-US3-02**: Given Scout is in Postgres, when the search index is rebuilt, then `vskill search scout` returns the `anton-abyzov/vskill/scout` entry
- [x] **AC-US3-03**: Given Scout is indexed, when searching on verified-skill.com publisher page, then Scout appears in results

## Out of Scope

- Skill description showing "owner/repo" instead of SKILL.md description (commit 5ccb236) -- deliberate change with broader implications, separate increment
- Changes to `installRepoPlugin()` flow -- only `discoverSkills()` is modified
- Platform-side code changes -- `discoverSkillsEnhanced()` in scanner.ts already handles non-specweave plugin paths correctly
- Framework plugin path validation changes -- `FRAMEWORK_PLUGIN_RE` is working as intended

## Technical Notes

### Dependencies
- GitHub Trees API (used by `discoverSkills()`)
- Platform crawl pipeline (for re-crawl trigger)
- SEARCH_CACHE_KV (for search index rebuild)

### Constraints
- Negative lookahead must exclude `plugins/specweave*/` to preserve framework skill exclusion
- Agent files under `plugins/*/skills/*/agents/*.md` must also be discovered and attached

### Architecture Decisions
- Single file change in vskill: `src/discovery/github-tree.ts`
- Add third regex: `/^plugins\/(?!specweave)[^/]+\/skills\/([^/]+)\/SKILL\.md$/`
- Add matching agent regex: `/^plugins\/(?!specweave)[^/]+\/skills\/([^/]+)\/agents\/([^/]+\.md)$/`
- Platform fix is operational (re-crawl + reindex), not code

## Non-Functional Requirements

- **Performance**: Adding one regex check per tree entry has negligible impact on discovery time (tree iteration is already O(n))
- **Compatibility**: Regex negative lookahead (`(?!specweave)`) is standard ES2015, supported in all Node.js versions vskill targets

## Edge Cases

- Plugin directory named `specweave-custom` by a third party: correctly excluded by negative lookahead (matches `specweave*` pattern)
- Plugin directory named `spectools` or `spectral`: correctly included (does not start with `specweave`)
- Empty `plugins/` directory: no matches, no errors
- Plugin with both root SKILL.md and nested skills: both patterns match independently

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Negative lookahead too broad, blocks legitimate plugins | 0.1 | 7 | 0.7 | Regex only excludes exact `specweave` prefix; test with all known plugin names |
| Re-crawl doesn't pick up Scout due to submission pipeline issue | 0.2 | 5 | 1.0 | Verify platform scanner.ts handles path; manual submission as fallback |
| Agent file regex doesn't match nested agent paths | 0.1 | 3 | 0.3 | Test with actual Scout agent file paths |

## Success Metrics

- `vskill install --repo anton-abyzov/vskill` lists all 7 non-specweave plugin skills
- `vskill search scout` returns `anton-abyzov/vskill/scout` in results
- All existing `discoverSkills()` tests continue to pass
- New regression tests cover plugin-nested skill discovery

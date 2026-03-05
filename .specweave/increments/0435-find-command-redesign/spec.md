---
increment: 0435-find-command-redesign
title: "Redesign vskill find command with install counts"
type: feature
priority: P1
status: active
created: 2026-03-05
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Redesign vskill find command with install counts

## Problem Statement

The `vskill find` command currently displays results in a grouped marketplace table with 50 results by default, which is overwhelming and buries the most useful skills. Results are sorted by score but lack install counts, making it hard for users to gauge real-world adoption. The search API does not return `vskillInstalls` in its response, so the CLI cannot display this data even if it wanted to.

## Goals

- Simplify CLI output to a flat, scannable list sorted by installs
- Surface install counts so users can identify popular, battle-tested skills
- Reduce default result count to 15 for focused, actionable output
- Extend the search API to include `vskillInstalls` in responses

## User Stories

### US-VSK-001: Flat install-sorted search results (P1)
**Project**: vskill
**As a** CLI user searching for skills
**I want** results displayed as a flat list sorted by install count in a clean `repo@skill-name` format
**So that** I can quickly identify and install the most popular skills

**Acceptance Criteria**:
- [ ] **AC-US1-01**: Given a user runs `vskill find <query>`, when results are returned, then they are sorted by `vskillInstalls` descending with relevance score as tiebreaker
- [ ] **AC-US1-02**: Given a TTY terminal, when results are displayed, then each result shows `repo@skill-name  1.2K installs` on the first line and `  URL` (clickable OSC 8 link) on the next line, with no marketplace grouping or table headers
- [ ] **AC-US1-03**: Given the user does not pass `--limit`, when the command runs, then the default limit is 15 (not 50) and a hint `Use --limit N for more` appears when `hasMore` is true
- [ ] **AC-US1-04**: Given a blocked skill in the results, when it is displayed, then it shows threat info (severity and threat type) instead of install count
- [ ] **AC-US1-05**: Given `--json` flag, when results are displayed, then the JSON output includes a `vskillInstalls` field for each result

### US-VPL-002: Install counts in search API response (P1)
**Project**: vskill-platform
**As a** CLI developer consuming the search API
**I want** `vskillInstalls` included in search results
**So that** I can display install popularity in the CLI output

**Acceptance Criteria**:
- [ ] **AC-US2-01**: Given a search API request to `/api/v1/skills/search`, when the edge KV path returns results, then each result includes a `vskillInstalls` number field
- [ ] **AC-US2-02**: Given a search API request, when the Postgres fallback path returns results, then each result includes `vskillInstalls` read from the `Skill` table
- [ ] **AC-US2-03**: Given the `SearchIndexEntry` type, when it is updated, then it includes a `vskillInstalls` field and the `INDEX_VERSION` constant is bumped from 4 to 5 to trigger a full index rebuild
- [ ] **AC-US2-04**: Given the `SearchResult` type, when it is updated, then it includes a `vskillInstalls` number field with a default of 0 for backward compatibility

## Out of Scope

- Changing the web UI search results page (only CLI output is redesigned)
- Adding install count tracking or incrementing logic (already exists)
- Modifying the `vskill info` command (already shows installs via `SkillDetail`)
- Paginated browsing in the CLI (users can use `--limit` or the website)

## Technical Notes

### vskill CLI (US-VSK-001)
- Current default limit in `client.ts#searchSkills()` is hardcoded to 50 -- change to 15
- `SkillSearchResult` interface needs a `vskillInstalls?: number` field
- `searchSkills()` must map `s.vskillInstalls` from the API response
- Remove the marketplace grouping logic (`extractBaseRepo`, group-by-repo, `Plugin Marketplace:` headers)
- New format per result: `owner/repo@skill-name` (bold) + humanized installs (e.g. `1.2K`, `15`, `3.4M`), then indented URL line with clickable link
- Non-TTY output: tab-separated flat lines (`name\trepo\tinstalls`) -- no table helper
- Blocked results: show `BLOCKED  severity | threatType` instead of installs

### vskill-platform (US-VPL-002)
- `SearchIndexEntry` in `search-index.ts`: add `vskillInstalls: number`
- `buildSearchIndex()` already reads full `Skill` rows which include `vskillInstalls` -- just include it in the shard entry
- `SearchResult` in `search.ts`: add `vskillInstalls: number`
- Edge path (`searchSkillsEdge`): map `entry.vskillInstalls` to result
- Postgres path (`searchSkills`): add `"vskillInstalls"` to both SELECT queries (tsvector and ILIKE fallback) and to `SkillSearchRow`
- Bump `INDEX_VERSION` from 4 to 5 so admin rebuild picks up the new field

## Success Metrics

- CLI output is visually scannable in under 3 seconds for 15 results
- Install counts surface in both edge and Postgres search paths
- Existing `--json` consumers get `vskillInstalls` without breaking changes

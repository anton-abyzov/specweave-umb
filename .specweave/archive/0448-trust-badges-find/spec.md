---
increment: 0448-trust-badges-find
title: "Trust badges in vskill find output"
type: feature
priority: P1
status: planned
created: 2026-03-07
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Trust badges in vskill find output

## Overview

Display colored trust tier badges (T4 certified, T3 verified, T2/T1 maybe) alongside star counts in `vskill find` CLI output. The platform search API already returns `trustTier` in skill records; the CLI must parse it and render an appropriate colored badge in both TTY and non-TTY output modes.

## User Stories

### US-001: See trust badges in find results (P1)
**Project**: vskill

**As a** CLI user searching for skills
**I want** to see a colored trust badge next to each skill in `vskill find` output
**So that** I can quickly assess the trustworthiness of a skill before installing it

**Acceptance Criteria**:
- [x] **AC-US1-01**: T4 skills display a green checkmark with "certified" label
- [x] **AC-US1-02**: T3 skills display a cyan checkmark with "verified" label
- [x] **AC-US1-03**: T2 skills display a yellow question mark with "maybe" label
- [x] **AC-US1-04**: T1 skills display a dim question mark with "maybe" label
- [x] **AC-US1-05**: Blocked skills (T0) show "BLOCKED" in red instead of a trust badge
- [x] **AC-US1-06**: Skills with no trustTier show no badge (empty string)

---

### US-002: Trust tier in non-TTY and JSON output (P1)
**Project**: vskill

**As a** developer piping `vskill find` output to other tools
**I want** the trust tier to appear in non-TTY tab-separated and JSON output
**So that** I can programmatically filter or sort skills by trust level

**Acceptance Criteria**:
- [x] **AC-US2-01**: Non-TTY tab-separated output includes trustTier as the 4th column (after stars)
- [x] **AC-US2-02**: JSON output (--json) includes the trustTier field on each result
- [x] **AC-US2-03**: Blocked skills in non-TTY output show "BLOCKED" as the 3rd column (no trust tier column)

---

### US-003: Platform API returns trustTier in search results (P1)
**Project**: vskill-platform

**As the** vskill CLI
**I want** the `/api/v1/skills/search` endpoint to return `trustTier` for each skill
**So that** badges can be rendered client-side without additional API calls

**Acceptance Criteria**:
- [x] **AC-US3-01**: Postgres search results include trustTier from the Skill table
- [x] **AC-US3-02**: Edge KV search index entries include trustTier (sharded index)
- [x] **AC-US3-03**: Blocked skills enriched via BlocklistEntry set trustTier to "T0"
- [x] **AC-US3-04**: CLI client maps `trustTier` from raw API response to `SkillSearchResult.trustTier`

## Functional Requirements

### FR-001: Trust badge rendering in TTY mode
The `getTrustBadge(trustTier)` function returns a colored ANSI string based on the tier:
- T4: green checkmark + "certified"
- T3: cyan checkmark + "verified"
- T2: yellow "?" + "maybe"
- T1: dim "?" + "maybe"
- undefined/other: empty string

Badge is appended after the star count on the first line of each result entry.

### FR-002: Trust tier in non-TTY output
Non-TTY tab-separated format includes trustTier as column 4:
`name\trepo\tstars\ttrustTier\tpluginName\taltRepos`

### FR-003: Search index includes trustTier
The KV sharded search index (`SearchIndexEntry`) stores `trustTier` per skill. The `compactEntry()` function omits it when the value is "T1" (default) to save space.

## Success Criteria

- All 5 trust tiers render correctly in TTY mode with appropriate colors
- Non-TTY output includes trustTier for programmatic consumption
- JSON output preserves trustTier field
- Blocked skills show BLOCKED label instead of trust badge
- No additional API calls needed (trustTier comes in the search response)

## Out of Scope

- Trust score numeric value in find output (only tier badge shown)
- Filtering find results by trust tier (future: `--min-tier T3`)
- Trust tier explanation or help text in find output
- Provenance verification details in find output

## Dependencies

- **vskill-platform**: Search API must return `trustTier` in skill records (implemented)
- **Trust score engine**: `trust-score.ts` computes tiers from scan verdicts, provenance, community signals (implemented)
- **Search index rebuild**: KV shards must include `trustTier` field (implemented)

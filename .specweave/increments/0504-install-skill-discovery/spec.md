---
increment: 0504-install-skill-discovery
title: Install Command Skill Discovery & Disambiguation
type: feature
priority: P1
status: completed
created: 2026-03-12T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Install Command Skill Discovery & Disambiguation

## Problem Statement

When a user types `vskill install skill-creator` (flat name, no slashes), the CLI attempts a direct `getSkill()` API lookup. If the skill is not found by exact name, the user gets a generic error suggesting `vskill find`. This forces a two-step workflow: search first with `vskill find`, then copy the exact `owner/repo/skill` path and install. The install command should be smart enough to search and disambiguate in one step.

## Goals

- Eliminate the two-step find-then-install workflow for flat-name installs
- Present ranked, trustworthy results when multiple skills match a query
- Maintain backward compatibility for `owner/repo` and `owner/repo/skill` install formats
- Provide safe defaults in non-interactive (CI/piped) environments

## User Stories

### US-001: Search Registry on Flat Name Install (P1)
**Project**: vskill
**As a** CLI user
**I want** `vskill install skill-creator` to search the registry automatically
**So that** I do not need to run `vskill find` as a separate step

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a flat name input (no slashes), when `installFromRegistry` is invoked, then `searchSkills(flatName)` is called instead of `getSkill(flatName)`
- [x] **AC-US1-02**: Given `searchSkills()` returns exactly one non-blocked result, then installation proceeds automatically by re-invoking `addCommand("owner/repo/skill", opts)` using the result's slug fields
- [x] **AC-US1-03**: Given `searchSkills()` returns zero results, then the CLI prints an error message and suggests `vskill find <query>` for broader search
- [x] **AC-US1-04**: Given `searchSkills()` throws an error (network failure, API down), then the CLI falls back to the existing `getSkill()` + `installFromRegistry` behavior

---

### US-002: Interactive Disambiguation for Multiple Matches (P1)
**Project**: vskill
**As a** CLI user in an interactive terminal
**I want** to choose from ranked search results when my query matches multiple skills
**So that** I can install the correct skill without retyping the command

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given multiple non-blocked results and a TTY environment, then the CLI displays results using the same format as `vskill find` (skill ID, stars, trust badge, URL) and presents an interactive `promptChoice` selection
- [x] **AC-US2-02**: Given the user selects a result from the interactive prompt, then the CLI re-invokes `addCommand("owner/repo/skill", opts)` with the selected result's slug fields
- [x] **AC-US2-03**: Given results contain both blocked and non-blocked skills, then blocked skills are displayed with BLOCKED label but are not selectable in the interactive prompt

---

### US-003: Non-TTY Disambiguation (P1)
**Project**: vskill
**As a** CI pipeline or script author
**I want** clear output and a non-zero exit code when a flat name is ambiguous
**So that** my automation fails explicitly instead of installing the wrong skill

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given multiple results and a non-TTY environment, then the CLI prints the ranked result list (same display format as `vskill find`) and exits with code 1
- [x] **AC-US3-02**: Given a non-TTY environment, then the error message instructs the user to specify the exact `owner/repo/skill` path

---

### US-004: Result Ranking with Exact Match Priority (P1)
**Project**: vskill
**As a** CLI user
**I want** results ranked by relevance and trust
**So that** the most likely correct skill appears first

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given search results, then results are sorted: blocked at end, then by cert tier (CERTIFIED > VERIFIED > other), then by GitHub stars descending, then by score descending -- matching the `find` command ranking
- [x] **AC-US4-02**: Given a result whose `skillSlug` exactly matches the input query (case-insensitive), then that result is promoted to first position among non-blocked results regardless of cert tier or stars
- [x] **AC-US4-03**: Given all search results are blocked, then the CLI displays the blocked results and prints an error that no installable skills were found

---

### US-005: --yes Flag Auto-Pick (P2)
**Project**: vskill
**As a** script author or power user
**I want** `--yes` to auto-select the first ranked non-blocked result
**So that** I can script installs without interactive prompts

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given the `--yes` flag and multiple search results, then the CLI automatically selects the first non-blocked result after ranking (including exact-match priority) and proceeds with installation
- [x] **AC-US5-02**: Given the `--yes` flag and all results are blocked, then the CLI exits with code 1 and an error message

## Out of Scope

- Changing behavior for `owner/repo` or `owner/repo/skill` install formats (these bypass the search path entirely)
- Adding new search API parameters or modifying the `searchSkills()` function signature
- Caching search results across invocations
- Modifying the `vskill find` command itself

## Technical Notes

### Dependencies
- `searchSkills()` in `src/api/client.ts` -- existing search API client
- `formatSkillId()`, `getSkillUrl()`, `getTrustBadge()` in `src/commands/find.ts` -- display helpers (must be exported or extracted to shared module)
- `createPrompter().promptChoice()` in `src/utils/prompts.ts` -- interactive selection
- `isTTY()` in `src/utils/prompts.ts` -- environment detection

### Constraints
- The search query is the exact flat name passed to `searchSkills()` without client-side modification; the server handles fuzzy/prefix matching
- Result limit remains at default 7 (matching `find` command)
- The 3-part `addCommand("owner/repo/skill")` re-invocation reuses the entire existing install pipeline (marketplace detection, blocklist checks, trust tier validation, agent selection)

### Architecture Decisions
- Search-first replaces direct `getSkill()` lookup in the flat-name path only
- On search API failure, fall back to existing `getSkill()` behavior for resilience
- Re-invoke `addCommand` with constructed `owner/repo/skill` path rather than calling `getSkill()` again -- avoids duplicate API calls and reuses the battle-tested 3-part install handler

## Non-Functional Requirements

- **Performance**: No additional API calls beyond the single `searchSkills()` call (replacing the existing `getSkill()` call); fallback path adds one call only on search failure
- **Compatibility**: Works on all platforms (macOS, Linux, Windows) -- no platform-specific behavior
- **Security**: Blocked skills are never auto-installed; `--yes` skips blocked results; existing blocklist and trust-tier gates in the 3-part handler remain unchanged

## Edge Cases

- **All results blocked**: Display blocked results with BLOCKED labels, print "no installable skills found" error, exit code 1
- **Search API failure**: Fall back to existing `installFromRegistry` behavior (direct `getSkill()` lookup)
- **Single result is blocked**: Treat as zero installable matches -- show the blocked result, print error
- **Exact slug match among lower-ranked results**: Promote to first position before cert-tier sorting
- **Result has no ownerSlug/repoSlug/skillSlug**: Skip that result for installation (cannot construct `owner/repo/skill` path); show it in display but mark as not installable

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Search API returns different shape than expected | 0.2 | 5 | 1.0 | Existing `searchSkills()` already normalizes the response; fallback to `getSkill()` on any error |
| Display helpers in find.ts are not exported | 0.3 | 3 | 0.9 | Extract shared helpers to a common module or re-export from find.ts |
| Users rely on current `getSkill()` exact-match behavior | 0.1 | 4 | 0.4 | Fallback path preserves original behavior on search failure |

## Success Metrics

- Users can install a skill by flat name in a single command without needing `vskill find` first
- Non-TTY environments fail explicitly with actionable error messages instead of installing wrong skills
- Zero regressions in `owner/repo` and `owner/repo/skill` install paths

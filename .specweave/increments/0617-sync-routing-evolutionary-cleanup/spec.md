---
increment: 0617-sync-routing-evolutionary-cleanup
title: Sync Routing Evolutionary Cleanup
type: feature
priority: P1
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Sync Routing Evolutionary Cleanup

## Problem Statement

The sync routing engine (`sync-target-resolver.ts`) implements a 3-phase resolver (umbrella match → name/ID match → prefix routing → global fallback) that correctly routes sync operations to per-repo external targets. However, this infrastructure is dormant because upstream systems never populate the fields it depends on:

1. **`project` field missing**: Only 5 of 80+ increments set `project` in metadata.json — `template-creator.ts` creates metadata without it, so Phase 1 (name/ID match) never activates.
2. **Flat JIRA/ADO targeting**: All sync goes to `SWE2E`/`SpecWeaveSync` regardless of which child repo owns the work, because the resolver always falls through to Phase 3 (global fallback).
3. **Wizard asks meaningless question**: The sync-setup wizard asks "What is your repository architecture?" even though all projects now use umbrella structure — wasting user time on every setup.
4. **User story IDs lack prefix**: Stories use `US-001` format instead of `US-{PREFIX}-NNN`, so Phase 2 (prefix routing) never activates.

This increment activates the dormant routing by auto-populating the fields the resolver already knows how to consume.

## Goals

- Auto-populate `project` field during increment creation so Phase 1 resolves without manual intervention
- Simplify sync-setup wizard by removing the redundant architecture question
- Auto-prefix user story IDs to activate Phase 2 prefix routing for new stories
- Add `project` field validation to `sw:validate` for umbrella setups
- Maintain full backward compatibility — old increments and stories continue working via Phase 3 fallback

## User Stories

### US-SPE-001: Auto-Populate Project Field During Increment Creation (P0)
**Project**: specweave
**As a** developer creating increments in an umbrella workspace
**I want** the `project` field to be automatically set based on my working context
**So that** sync routing (Phase 1) activates without manual metadata editing

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a `cwd` inside a child repo path (e.g., `repositories/anton-abyzov/specweave/`), when `specweave create-increment` runs, then `metadata.json.project` is set to the matching `childRepos[].id` (e.g., `"specweave"`)
- [x] **AC-US1-02**: Given a `cwd` at the umbrella root (not inside any child repo), when creating an increment, then `metadata.json.project` is set to `umbrella.projectName` (e.g., `"specweave-umb"`)
- [x] **AC-US1-03**: Given `umbrella.enabled` is `false` or absent, when creating an increment, then no `project` field is added to metadata.json (existing behavior preserved)
- [x] **AC-US1-04**: Given a child repo with `disabled: true` in config, when `cwd` matches that repo's path, then the project field is still set (disabled only affects sync, not identification)
- [x] **AC-US1-05**: Given the `project` field is auto-set in metadata.json, when the sync resolver runs Phase 1, then it matches the child repo and returns per-repo sync targets instead of falling through to global fallback

---

### US-SPE-002: Simplify Sync-Setup Wizard (P1)
**Project**: specweave
**As a** developer running sync-setup for the first time
**I want** the wizard to skip the "repository architecture" question and auto-detect umbrella mode
**So that** setup is faster and does not ask questions with only one valid answer

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given `umbrella.enabled: true` in config.json, when running `sync-setup`, then the wizard does not prompt "What is your repository architecture?" and proceeds as multi-repo
- [x] **AC-US2-02**: Given `umbrella.enabled` is `false` or absent, when running `sync-setup`, then the wizard still asks the architecture question (backward-compatible for non-umbrella projects)
- [x] **AC-US2-03**: Given GitHub API is rate-limited (HTTP 403/429), when the wizard attempts repo detection, then it falls back to config-based detection without crashing or hanging
- [x] **AC-US2-04**: Given auto-detection succeeds, when displaying the setup summary, then the detected child repo count is shown (e.g., "Detected 2 active child repos: specweave, vskill")

---

### US-SPE-003: Auto-Prefix User Story IDs (P1)
**Project**: specweave
**As a** PM agent generating specs in an umbrella workspace
**I want** user story IDs to use `US-{PREFIX}-NNN` format from child repo config
**So that** Phase 2 prefix routing activates automatically for new stories

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given a spec being generated for `project: specweave` (prefix `SPE`), when user stories are created, then IDs use format `US-SPE-001`, `US-SPE-002`, etc.
- [x] **AC-US3-02**: Given a spec for the umbrella project (`specweave-umb`), when user stories are created, then IDs use plain format `US-001` (no prefix — umbrella has no child-repo prefix)
- [x] **AC-US3-03**: Given existing stories with old `US-001` format in the same increment, when new stories are appended, then numbering continues from the highest existing number (no collisions)
- [x] **AC-US3-04**: Given `story-router.ts` receives a `US-SPE-001` ID, when extracting the prefix, then it matches `childRepos[].prefix === "SPE"` and returns the correct repo routing
- [x] **AC-US3-05**: Given old stories without prefix (`US-001`), when the sync resolver processes them, then Phase 3 global fallback handles them correctly (no regression)

---

### US-SPE-004: Add Project Validation to sw:validate (P2)
**Project**: specweave
**As a** developer running quality checks on increments
**I want** `sw:validate` to warn when `project` is missing in umbrella setups
**So that** I catch routing gaps before sync operations fail silently

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given `umbrella.enabled: true` and `childRepos.length > 1`, when `sw:validate` runs on an increment with no `project` field in metadata.json, then it emits a warning (not error) with message suggesting auto-set
- [x] **AC-US4-02**: Given a single-repo project (no umbrella), when `sw:validate` runs on an increment without `project`, then no warning is emitted
- [x] **AC-US4-03**: Given an increment with `project` set to a value not matching any `childRepos[].id` or `umbrella.projectName`, when validating, then it emits a warning about unrecognized project name

## Out of Scope

- Per-user-story external project targeting (stories within one increment always route to the same project)
- Renaming "umbrella" to "workspace" in config schema
- Multi-target fan-out sync for cross-cutting increments (one increment → multiple external projects)
- Merging sync profiles into the routing chain
- Backfilling `project` field on existing 80+ increments (they continue via Phase 3 fallback)
- Changing JIRA/ADO project mapping (SWE2E/SpecWeaveSync remain defaults — per-repo JIRA projects are a separate initiative)

## Technical Notes

### Dependencies
- `sync-target-resolver.ts` — the 3-phase resolver (already implemented, dormant)
- `template-creator.ts` — increment metadata generation (needs `project` field injection)
- `us-id-generator.ts` + `story-router.ts` — user story ID generation and prefix extraction
- `sync-setup.ts` + `issue-tracker/index.ts` — wizard flow
- `three-file-validator.ts` + `increment-structure-validator.ts` — validation rules

### Constraints
- Backward compatibility is non-negotiable: all existing increments and stories must continue working
- No changes to the resolver itself — only upstream systems that feed it
- Wizard simplification must not break non-umbrella project setups

### Architecture Decisions
- **Project field in metadata.json** (not just spec.md frontmatter): metadata.json is the authoritative source for increment routing; spec.md `**Project**:` lines are per-story and may differ in umbrella mode
- **Auto-detect from cwd**: Uses `childRepos[].path` matching against working directory to determine project, same pattern used by `resolveEffectiveRoot()`
- **Prefix from config**: Uses existing `childRepos[].prefix` field (SPE, VSK, VPL) — no new config schema needed

## Non-Functional Requirements

- **Performance**: Project field detection adds < 5ms to increment creation (single config read + path comparison)
- **Compatibility**: Works on Windows, macOS, Linux path formats (use path.resolve for comparison)
- **Backward Compatibility**: All existing increments without `project` field continue to sync via Phase 3 global fallback

## Edge Cases

- **Nested child repo paths**: `cwd` is deep inside a child repo (e.g., `repositories/anton-abyzov/specweave/src/sync/`) — must still match the repo root
- **Multiple path matches**: If child repo paths overlap (shouldn't happen, but defensive), pick the longest/most-specific match
- **Disabled child repo**: `vskill-platform` is `disabled: true` — project field should still be set (disabled controls sync, not identification)
- **Missing prefix in config**: If a child repo has no `prefix` field, fall back to plain `US-NNN` format for that repo
- **Rate-limited GitHub API during wizard**: Must not block setup — fall back to config-based repo list

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Auto-set project breaks existing sync for edge-case configs | 0.2 | 6 | 1.2 | Phase 3 fallback always catches unmatched projects; add integration test |
| Prefix collision between repos | 0.1 | 4 | 0.4 | Prefixes are manually configured in config; validate uniqueness in sw:validate |
| Wizard auto-detection incorrect for edge-case setups | 0.2 | 3 | 0.6 | Only skip question when `umbrella.enabled: true` is explicit; preserve question for all other cases |

## Success Metrics

- 100% of new increments created in umbrella mode have `project` field auto-populated
- Phase 1 resolver activates for all new increments (verifiable via sync debug logs)
- Sync-setup wizard completes with 1 fewer question in umbrella mode
- Zero regressions: existing increments without `project` still sync via Phase 3 fallback

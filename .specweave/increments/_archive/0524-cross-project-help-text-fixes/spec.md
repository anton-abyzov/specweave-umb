---
increment: 0524-cross-project-help-text-fixes
title: "Cross-Project Help Text Fixes"
type: change-request
priority: P2
status: active
created: 2026-03-14
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Cross-Project Help Text Fixes

## Problem Statement

Several CLI help descriptions and UI labels across the three repos (specweave, vskill, vskill-platform) are vague or ambiguous. This lightweight increment fixes real text issues while serving as a validation vehicle for the living docs auto-sync hook across all three projects.

## Goals

- Fix one real help-text or label issue per repo (specweave, vskill, vskill-platform)
- Validate that the auto-sync hook propagates changes across all three projects
- Keep scope minimal -- text-only changes, no logic changes

## User Stories

### US-001: Clarify specweave validate-jira help description
**Project**: specweave

**As a** CLI user
**I want** the `validate-jira` command help text to specify what resources it validates and creates
**So that** I understand what the command does before running it

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given I run `specweave validate-jira --help`, when I read the command description, then it reads "Validate Jira connection, project, and issue-type configuration; create missing issue types if needed" instead of the current generic "Validate Jira configuration and create missing resources"

---

### US-002: Clarify vskill init command description
**Project**: vskill

**As a** CLI user
**I want** the `vskill init` help text to clearly state what the command does and that the lockfile update is optional
**So that** the ambiguous "(optional)" phrasing is removed

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given I run `vskill init --help`, when I read the command description, then it reads "Detect installed AI agents and optionally update the lockfile" instead of the current "Show detected AI agents and update lockfile (optional)"

---

### US-003: Improve vskill-platform 404 page help text
**Project**: vskill-platform

**As a** site visitor
**I want** the 404 page description to suggest checking the URL for typos
**So that** I get actionable guidance instead of just "it may have been moved or removed"

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given I visit a non-existent URL on verified-skill.com, when the 404 page renders, then the description paragraph reads "This URL doesn't match any page. Check the address for typos, or use the links below to navigate."

## Out of Scope

- Logic changes to any command behavior
- Adding new CLI options or flags
- Changing error messages in code paths (only help text and static UI copy)
- Comprehensive help text audit across all commands

## Technical Notes

### Dependencies
- No cross-repo dependencies -- each story is an independent text change

### Constraints
- Text-only changes; no runtime behavior modifications
- Each change is a single string replacement in one file

### Architecture Decisions
- No architecture impact -- pure copy changes

## Non-Functional Requirements

- **Compatibility**: All three changes are backward-compatible string updates
- **Accessibility**: 404 page text remains readable at all font sizes (no layout change)

## Edge Cases

- Existing scripts that parse `--help` output: no impact since description is informational only
- Localization: none of the three repos use i18n, so direct string edits are safe

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Help text change breaks a snapshot test | 0.3 | 2 | 0.6 | Update any affected snapshot if present |
| Auto-sync hook does not trigger for one repo | 0.2 | 3 | 0.6 | Manual sync fallback via `specweave sync-living-docs` |

## Success Metrics

- All three text changes merged and deployed
- Auto-sync hook fires for all three repos after increment completion

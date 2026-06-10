---
increment: 0873-desktop-verified-skill-repo-link
title: Desktop verified-skill repository link
type: bug
priority: P1
status: completed
created: 2026-06-04T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Desktop verified-skill repository link

## Overview

Skill Studio's desktop skill detail byline currently shows a clickable
`owner/repo` chip that opens the GitHub repository root. That chip should route
users to the matching verified-skill.com skill page for the exact repository and
skill, while the existing source-file chip remains the direct GitHub blob link.

## User Stories

### US-001: Repo chip opens verified-skill skill page (P1)
**Project**: vskill

**As a** Skill Studio desktop user
**I want** the repository chip in a skill detail page to open the matching
verified-skill.com skill page
**So that** I can inspect the verified registry page for the exact GitHub
repository and skill without manually searching the website

**Acceptance Criteria**:
- [x] **AC-US1-01**: When `RepoLink` receives a parseable GitHub `repoUrl` and a
  skill name, it renders a clickable `owner/repo` chip whose `href` is
  `https://verified-skill.com/skills/{owner}/{repo}/{skill}`.
- [x] **AC-US1-02**: `DetailHeader` passes the selected `SkillInfo.skill` into
  `RepoLink` so the desktop detail page points at the exact verified-skill page.
- [x] **AC-US1-03**: Existing GitHub source-file behavior is preserved:
  `SourceFileLink` still points to `https://github.com/{owner}/{repo}/blob/HEAD/{skillPath}`.
- [x] **AC-US1-04**: Invalid, empty, or non-GitHub repository URLs still render
  no repo chip.

## Functional Requirements

### FR-001: Canonical verified-skill URL builder
`RepoLink` should keep its existing GitHub repo parsing guardrails, then build
the verified-skill URL from parsed owner/repo and a sanitized skill slug.

### FR-002: Backward-compatible component contract
`RepoLink` should accept an optional `skillName`. If the skill name is absent,
fallback behavior can remain the GitHub repo root so current callers outside the
detail page do not break.

## Success Criteria

- Desktop detail byline exposes the verified-skill skill page link.
- Existing author/source-file links remain unchanged.
- Focused eval-ui unit tests pass.

## Out of Scope

- Creating a new verified-skill repository-level route.
- Changing the direct source-file GitHub blob link.
- Changing website page rendering or registry data.

## Dependencies

- Existing verified-skill route shape: `/skills/{owner}/{repo}/{skill}`.
- Existing `SkillInfo.repoUrl`, `SkillInfo.skill`, and `SkillInfo.skillPath`
  fields in the desktop API payload.

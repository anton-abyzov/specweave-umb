---
increment: 0386-skill-path-view-source
title: "Add skillPath to Skill model and View Source link"
type: feature
priority: P1
status: in-progress
created: 2026-02-27
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Add skillPath to Skill model and View Source link

## Overview

The skill detail page on verified-skill.com shows the repository URL but has no direct link to the actual SKILL.md file within the repo. The `skillPath` field is already stored in the `Submission` model but never copied to the published `Skill` record. This increment adds `skillPath` to the Skill model, surfaces it in the API, and renders a "View Source" link on the skill detail page.

## User Stories

### US-001: View Source File Link (P1)
**Project**: vskill-platform

**As a** skill consumer browsing verified-skill.com
**I want** a direct link to the SKILL.md source file
**So that** I can quickly review the skill's source without navigating the repo manually

**Acceptance Criteria**:
- [x] **AC-US1-01**: Skill model has `skillPath` optional column in database
- [x] **AC-US1-02**: `publishSkill()` copies `skillPath` from Submission to Skill during publish
- [x] **AC-US1-03**: Skill detail page shows "Source" meta row with clickable deep-link to `{repoUrl}/blob/HEAD/{skillPath}`
- [x] **AC-US1-04**: When `skillPath` is null, "Source path unknown" placeholder is shown

---

### US-002: Backfill Existing Skills (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** existing published skills to have their `skillPath` populated
**So that** all skills show the View Source link, not just newly published ones

**Acceptance Criteria**:
- [x] **AC-US2-01**: Backfill script queries Skills with null skillPath and populates from linked Submissions
- [x] **AC-US2-02**: Script supports dry-run mode and execute mode
- [x] **AC-US2-03**: Script logs updated/skipped counts

## Out of Scope

- Non-GitHub hosting providers (GitLab, Bitbucket)
- Pinning to specific git SHA (uses HEAD ref)
- Frontend tests for the new meta row

---
increment: 0574-docs-skills-page-accuracy
title: Fix Skills Are Structured Expertise docs page
type: feature
priority: P1
status: completed
created: 2026-03-18T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Fix Skills Are Structured Expertise docs page

## Overview

The "Skills Are Structured Expertise" overview page (`docs-site/docs/overview/skills-as-structured-expertise.md`) contains outdated claims about skill counts, lists removed/nonexistent skills, and has a dead link. This increment corrects all inaccuracies to match the current core skill set (44 skills in `plugins/specweave/skills/`).

## User Stories

### US-001: Accurate skills documentation (P1)
**Project**: specweave

**As a** new SpecWeave user reading the docs,
**I want** the skills overview page to accurately reflect the current core skills and plugin architecture,
**So that** I can trust the documentation and find the right skill names to use.

**Acceptance Criteria**:
- [x] **AC-US1-01**: The "100+ Skills" heading is replaced with accurate language reflecting 44 core skills plus marketplace/community plugins
- [x] **AC-US1-02**: Removed/nonexistent skill references are replaced — `/backend:nodejs`, `backend:python`, `backend:go`, `/testing:qa`, `/sw:security`, `/backend:database-optimizer`, `/sw:code-review` are all removed and substituted with actual core skills
- [x] **AC-US1-03**: The "Frontend (`/sw:architect`)" misleading entry is corrected — architect is a general-purpose system design skill, not frontend-specific
- [x] **AC-US1-04**: The dead link to `../skills/skill-development-guidelines` is removed or replaced with a valid link
- [x] **AC-US1-05**: The page clearly distinguishes core skills (shipped with SpecWeave) from domain-specific plugins (installed via vskill marketplace)

## Out of Scope

- Changes to any other documentation pages
- Adding new documentation pages
- Updating actual skill implementations

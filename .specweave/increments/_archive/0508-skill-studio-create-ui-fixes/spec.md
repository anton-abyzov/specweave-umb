---
increment: 0508-skill-studio-create-ui-fixes
title: 'Fix Skill Studio Create Skill UI: formatting, duplication, preview crash'
type: bug
priority: P1
status: completed
created: 2026-03-12T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Fix Skill Studio Create Skill UI

## Overview

Fix three UI bugs in the "Create a New Skill" page affecting both CreateSkillInline and CreateSkillPage components.

## User Stories

### US-001: Preview button crash fix (P1)
**Project**: vskill

**As a** skill author
**I want** the SKILL.md Preview toggle to work without errors
**So that** I can preview my skill's rendered markdown before saving

**Acceptance Criteria**:
- [x] **AC-US1-01**: Clicking Preview toggle renders the SKILL.md body as formatted HTML without React errors
- [x] **AC-US1-02**: Empty body shows "Start writing to see preview" placeholder in preview mode

---

### US-002: AI reasoning banner formatting (P1)
**Project**: vskill

**As a** skill author using AI generation
**I want** the AI reasoning banner to show properly formatted text
**So that** I can read the AI's design decisions clearly

**Acceptance Criteria**:
- [x] **AC-US2-01**: AI reasoning text renders markdown formatting (bold, headers, lists) instead of raw markdown syntax
- [x] **AC-US2-02**: Reasoning banner is collapsible, collapsed by default, with a chevron toggle and "click to expand" hint

## Out of Scope

- Extracting shared component for the banner (pre-existing duplication between Inline and Page)
- HTML sanitization for renderMarkdown (local dev tool, self-XSS only)

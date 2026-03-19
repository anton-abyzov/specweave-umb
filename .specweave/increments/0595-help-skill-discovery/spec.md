---
increment: 0595-help-skill-discovery
title: 'Create /sw:help skill and clean up framework terminology'
type: feature
priority: P1
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
---

# Feature: Create /sw:help skill and clean up framework terminology

## Overview

Create `/sw:help` as the primary discovery and onboarding entry point for SpecWeave users. Shows available skills organized by workflow stage, inline usage statistics, and contextual next actions. Also removes "framework" terminology from public docs — SpecWeave is a spec-driven development tool, not a framework.

## User Stories

### US-001: Help Skill Discovery (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** a `/sw:help` command that shows all available skills organized by workflow stage
**So that** I can discover what SpecWeave offers without reading extensive documentation

**Acceptance Criteria**:
- [x] **AC-US1-01**: SKILL.md exists at `plugins/specweave/skills/help/SKILL.md` with proper frontmatter
- [x] **AC-US1-02**: Skill is registered in `plugin.json` provides.skills array
- [x] **AC-US1-03**: Help output organizes skills by workflow stage (Plan, Implement, Verify, Close, Sync, Explore, Media)
- [x] **AC-US1-04**: Help output includes one-liner description for each skill
- [x] **AC-US1-05**: Help gathers and displays inline usage statistics via `specweave analytics` and `specweave status`
- [x] **AC-US1-06**: Help shows contextual next actions when an active increment exists
- [x] **AC-US1-07**: Help includes getting started guidance for new users (no `.specweave/` directory)

---

### US-002: Framework Terminology Cleanup (P1)
**Project**: specweave

**As a** SpecWeave documentation reader
**I want** consistent "spec-driven development tool" terminology instead of "framework"
**So that** the product positioning is clear and accurate

**Acceptance Criteria**:
- [x] **AC-US2-01**: `introduction.md` replaces "spec-first AI development framework" with "spec-first AI development tool"
- [x] **AC-US2-02**: `philosophy.md` replaces "framework" with "SpecWeave"
- [x] **AC-US2-03**: `plugins-ecosystem.md` replaces "core framework" with "SpecWeave"
- [x] **AC-US2-04**: `generic-ai-tools.md` replaces all SpecWeave-referencing "framework" occurrences
- [x] **AC-US2-05**: Tech stack references ("React framework", "Next.js framework") are preserved unchanged

---

### US-003: Help Documentation Page (P2)
**Project**: specweave

**As a** SpecWeave docs reader
**I want** a `/sw:help` documentation page on the docs site
**So that** I can learn about the help command from the web

**Acceptance Criteria**:
- [x] **AC-US3-01**: `docs/commands/help.md` exists following existing command page patterns
- [x] **AC-US3-02**: Page documents what `/sw:help` shows and how to use it

## Out of Scope

- Creating a CLI `specweave help` command (the skill IS the help)
- Refactoring existing skills
- Changing skill trigger patterns for other skills

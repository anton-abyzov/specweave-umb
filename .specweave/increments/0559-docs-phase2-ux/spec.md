---
increment: 0559-docs-phase2-ux
title: "Docs Phase 2: UX, Dual Activation, Plugin Accuracy, Team-Lead Section"
type: feature
priority: P1
status: active
created: 2026-03-17
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Docs Phase 2: UX, Dual Activation, Plugin Accuracy, Team-Lead Section

## Overview

Improve documentation accuracy and usability by adding dual activation examples (slash + natural language) to key skill pages, fixing plugin-related inaccuracies in the skills reference and fundamentals pages, correcting vskill install commands, and adding a dedicated team-lead documentation entry to the sidebar.

## User Stories

### US-001: Dual Activation Examples (P1)
**Project**: specweave

**As a** new SpecWeave user
**I want** to see both slash command and natural language examples for each key skill
**So that** I understand I can use either invocation method and choose what feels natural

**Acceptance Criteria**:
- [x] **AC-US1-01**: The skills reference page shows both slash command and natural language trigger for every core skill section (increment, do, auto, done, brainstorm, team-lead, grill, code-reviewer)
- [x] **AC-US1-02**: The workflows overview page includes a dual-activation tip showing the natural language equivalent for each workflow phase command
- [x] **AC-US1-03**: The commands overview page shows natural language alternatives alongside slash commands in the quick reference table

---

### US-002: Plugin Accuracy Verification (P1)
**Project**: specweave

**As a** documentation reader
**I want** the plugin ecosystem page and skills reference to accurately reflect the actual plugin structure
**So that** I am not misled about which plugins exist and how many skills are bundled

**Acceptance Criteria**:
- [x] **AC-US2-01**: The skills/fundamentals.md page correctly states 1 bundled specweave plugin with 44 skills (not "22 plugins with 126 skills")
- [x] **AC-US2-02**: The reference/skills.md page removes references to non-existent separate plugins (backend, frontend, testing, infra, k8s, kafka, confluent, payments, cost, docs) from skill tables and instead notes these are community/domain skills available via verified-skill.com
- [x] **AC-US2-03**: The skills reference "Installing Domain Plugins" section accurately reflects available vskill marketplace plugins (mobile, skills, marketing, productivity, google-workspace)

---

### US-003: Fix vskill Install Commands (P1)
**Project**: specweave

**As a** user following documentation
**I want** all vskill install commands to use correct syntax
**So that** I can successfully install plugins without trial and error

**Acceptance Criteria**:
- [x] **AC-US3-01**: All instances of `vskill add specweave --plugin X` are replaced with the correct syntax `npx vskill install --repo anton-abyzov/specweave --plugin sw`
- [x] **AC-US3-02**: Plugin install commands for non-existent separate specweave plugins (sw-github, sw-jira, sw-ado, sw-diagrams, sw-release) are corrected to reference the unified sw plugin
- [x] **AC-US3-03**: The vskill marketplace plugins listed in docs match the actual marketplace.json (mobile, skills, marketing, productivity, google-workspace)

---

### US-004: Team-Lead Documentation Section (P2)
**Project**: specweave

**As a** user exploring multi-agent coordination
**I want** the team-lead skill to be prominently accessible in the sidebar navigation
**So that** I can quickly find how to use parallel agent teams

**Acceptance Criteria**:
- [x] **AC-US4-01**: A dedicated "Team-Lead" entry exists in the Agent Teams sidebar category linking to the existing agent-teams-and-swarms page
- [x] **AC-US4-02**: The agent-teams-and-swarms page includes dual activation examples (slash + natural language) for team-lead operations

---

### US-005: Navigation Improvements (P2)
**Project**: specweave

**As a** documentation visitor
**I want** improved sidebar navigation with clear grouping
**So that** I can find what I need without scanning every entry

**Acceptance Criteria**:
- [x] **AC-US5-01**: The Agent Teams sidebar category includes team-lead as a visible entry

---

### US-006: Mermaid Diagram Fixes (P2)
**Project**: specweave

**As a** documentation reader
**I want** all Mermaid diagrams to render correctly
**So that** I can understand visual workflows without rendering errors

**Acceptance Criteria**:
- [x] **AC-US6-01**: Mermaid diagrams in workflows/overview.md that use emoji characters in node labels are updated to use text-only labels for reliable cross-browser rendering

## Functional Requirements

### FR-001: Dual Activation Pattern
Each dual activation example follows a consistent format showing slash command alongside natural language equivalent.

### FR-002: Plugin Accuracy
Plugin counts and names must match the actual marketplace.json files in the specweave and vskill repositories.

### FR-003: Command Syntax
All vskill commands must use the `npx vskill install` syntax with correct flags.

## Success Criteria

- All vskill install commands in docs are valid and executable
- Plugin counts match actual codebase (1 sw plugin with 44 skills, 5 vskill marketplace plugins)
- Core skills show both invocation methods
- No Mermaid rendering issues from emoji characters

## Out of Scope

- Changing the actual plugin architecture or application code
- Creating entirely new documentation pages
- Fixing external links or third-party references

## Dependencies

- Existing docs-site at specweave/docs-site/
- Existing marketplace.json files in specweave and vskill repos

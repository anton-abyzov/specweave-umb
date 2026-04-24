---
increment: 0700-studio-plugin-cli-wrapper
title: "Skill Studio: wrap Claude Code /plugin commands (list/enable/disable/install/uninstall) with UI actions"
type: feature
priority: P1
status: planned
created: 2026-04-24
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skill Studio: wrap Claude Code /plugin commands (list/enable/disable/install/uninstall) with UI actions

## Overview

Wrap Claude Code's plugin management commands so users can browse, install, enable, disable, and uninstall plugins from Skill Studio without dropping to a terminal. Per-plugin action menu on AVAILABLE > Plugins rows, marketplace drawer, SSE streaming for long operations. Phase 1 delivers list + enable/disable via filesystem state; phase 2 adds install/uninstall via 'claude' subprocess.

<!--
====================================================================
  TEMPLATE FILE - MUST BE COMPLETED VIA PM/ARCHITECT SKILLS
====================================================================

This is a TEMPLATE created by increment skill.
DO NOT manually fill in the placeholders below.

To complete this specification, run:
  Tell Claude: "Complete the spec for increment 0700-studio-plugin-cli-wrapper"

This will activate the PM skill which will:
- Define proper user stories with acceptance criteria
- Conduct market research and competitive analysis
- Create user personas
- Define success metrics

====================================================================
-->

## User Stories

### US-001: [Story Title] (P1)
**Project**: vskill

**As a** [user type]
**I want** [goal]
**So that** [benefit]

**Acceptance Criteria**:
- [ ] **AC-US1-01**: [Specific, testable criterion]
- [ ] **AC-US1-02**: [Another criterion]

---

### US-002: [Story Title] (P2)
**Project**: vskill

**As a** [user type]
**I want** [goal]
**So that** [benefit]

**Acceptance Criteria**:
- [ ] **AC-US2-01**: [Specific, testable criterion]
- [ ] **AC-US2-02**: [Another criterion]

## Functional Requirements

### FR-001: [Requirement]
[Detailed description]

## Success Criteria

[Measurable outcomes - metrics, KPIs]

## Out of Scope

[What this explicitly does NOT include]

## Dependencies

[Other features or systems this depends on]

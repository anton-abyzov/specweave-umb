---
increment: 0272-external-issue-import
title: "External Issue Import (/sw:import)"
type: feature
priority: P1
status: active
created: 2026-02-21
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: External Issue Import (`/sw:import`)

## Overview

Add `/sw:import` slash command to pull issues from GitHub/Jira/ADO and create SpecWeave increments with platform-specific suffixes (G=GitHub, J=Jira, A=ADO), including 3-layer duplicate prevention and pre-filled spec generation.

<!--
====================================================================
  TEMPLATE FILE - MUST BE COMPLETED VIA PM/ARCHITECT SKILLS
====================================================================

See plan.md for full implementation details and architecture.
See tasks.md for task breakdown with AC references.

====================================================================
-->

## User Stories

### US-001: [Story Title] (P1)
**Project**: specweave

**As a** [user type]
**I want** [goal]
**So that** [benefit]

**Acceptance Criteria**:
- [ ] **AC-US1-01**: [Specific, testable criterion]
- [ ] **AC-US1-02**: [Another criterion]

---

### US-002: [Story Title] (P1)
**Project**: specweave

**As a** [user type]
**I want** [goal]
**So that** [benefit]

**Acceptance Criteria**:
- [ ] **AC-US2-01**: [Specific, testable criterion]
- [ ] **AC-US2-02**: [Another criterion]

## Functional Requirements

### FR-001: Platform Suffix Recognition
Update increment-utils.ts regex patterns from `E?` to `[GJAE]?` across all 6 methods.

### FR-002: Import-to-Increment Bridge
New module converting ExternalItem to full increment with metadata.json, spec.md, plan.md, tasks.md.

### FR-003: Duplicate Prevention
Scan metadata.json external_ref field across all lifecycle directories to prevent re-import.

## Success Criteria

- `/sw:import` creates properly-suffixed increments from all 3 platforms
- Duplicate detection blocks re-imports with clear feedback
- All existing tests pass with no regressions

---
increment: 0690-triage-preexisting-vitest-failures
title: "Triage 82 pre-existing vitest failures across 17 files"
type: bug
priority: P2
status: planned
created: 2026-04-23
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Triage 82 pre-existing vitest failures across 17 files

## Overview

During 0680 Phase 1 testing pass a full vitest sweep returned 3000/3096 passing with 82 failures in 17 files. Verified via git stash that the pattern is identical on baseline (main before 0680) — the failures predate 0680 and are unrelated. Need a systematic triage: enumerate the 17 files, categorize each failure (stale mock, env config drift, timing/flakiness, actual regression, etc.), and decide per file whether to fix, delete as dead test, or mark as known-broken. Output: one or more follow-up bug-type increments (depending on root-cause clustering), or a single umbrella increment if causes are diverse. Goal: get to a clean vitest run so future regressions are signal, not noise.

<!--
====================================================================
  TEMPLATE FILE - MUST BE COMPLETED VIA PM/ARCHITECT SKILLS
====================================================================

This is a TEMPLATE created by increment skill.
DO NOT manually fill in the placeholders below.

To complete this specification, run:
  Tell Claude: "Complete the spec for increment 0690-triage-preexisting-vitest-failures"

This will activate the PM skill which will:
- Define proper user stories with acceptance criteria
- Conduct market research and competitive analysis
- Create user personas
- Define success metrics

====================================================================
-->

## User Stories

### US-001: [Story Title] (P1)
**Project**: vskill-platform

**As a** [user type]
**I want** [goal]
**So that** [benefit]

**Acceptance Criteria**:
- [ ] **AC-US1-01**: [Specific, testable criterion]
- [ ] **AC-US1-02**: [Another criterion]

---

### US-002: [Story Title] (P2)
**Project**: vskill-platform

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

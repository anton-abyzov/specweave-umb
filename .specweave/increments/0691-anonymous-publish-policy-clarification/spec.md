---
increment: 0691-anonymous-publish-policy-clarification
title: "Clarify anonymous publish attribution policy (publishedBy null vs reject)"
type: change-request
priority: P3
status: planned
created: 2026-04-23
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Clarify anonymous publish attribution policy (publishedBy null vs reject)

## Overview

0680 grill rubric R-010 flagged ambiguity: current publish.ts behavior for a submission with no userId is to populate SkillVersion.publishedBy=null and proceed. Rubric R-010 suggested tightening to throw/reject. Resolved in 0680 in favor of permissive behavior per the team-lead brief (matches test T-017 expectation). This increment decides the product-level policy: (A) keep permissive — allow anonymous publishes, attribution is best-effort; (B) tighten — reject submissions without an authenticated user; (C) intermediate — allow anonymous BUT tag the SkillVersion with a clearly-different sentinel (e.g., publishedBy='system:anonymous') and surface it in the UI so consumers can filter. Deliverable: a policy decision + the code/UI/spec changes needed to implement it consistently across publish.ts, the versioning UI, and any future yank/deprecate endpoints. Consult product stakeholders before implementation.

<!--
====================================================================
  TEMPLATE FILE - MUST BE COMPLETED VIA PM/ARCHITECT SKILLS
====================================================================

This is a TEMPLATE created by increment skill.
DO NOT manually fill in the placeholders below.

To complete this specification, run:
  Tell Claude: "Complete the spec for increment 0691-anonymous-publish-policy-clarification"

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

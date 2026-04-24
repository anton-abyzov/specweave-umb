---
increment: 0689-e2e-github-seed-mock-fixture
title: "Replace GitHub seed repo with local fixture for E2E versioning flow"
type: bug
priority: P3
status: planned
created: 2026-04-23
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Replace GitHub seed repo with local fixture for E2E versioning flow

## Overview

0680 E2E (tests/e2e/skill-versioning.spec.ts) smoke-tests successfully but the full submit-publish-version flow skips gracefully when GitHub returns 422 on the seed repo (anthropics/skills-frontend-design). Skip guard is [400,409,422,429]. Unit coverage (9/9 skill-version-creation + 7/7 publish-v2) exercises the same code paths, so correctness is proven — but CI has no end-to-end HTTP proof of the submit-to-version flow. Fix: either (a) introduce a local git-server fixture that serves a minimal skill repo the E2E can always submit, or (b) add a deterministic test-mode shim in the submission pipeline that accepts a local fixture path instead of a GitHub URL when NODE_ENV=test. Tighten skip guard to log a warning rather than silently skip.

<!--
====================================================================
  TEMPLATE FILE - MUST BE COMPLETED VIA PM/ARCHITECT SKILLS
====================================================================

This is a TEMPLATE created by increment skill.
DO NOT manually fill in the placeholders below.

To complete this specification, run:
  Tell Claude: "Complete the spec for increment 0689-e2e-github-seed-mock-fixture"

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

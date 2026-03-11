---
id: US-005
feature: FS-491
title: "Anti-Rationalization Tables (P2)"
status: completed
priority: P1
created: 2026-03-11T00:00:00.000Z
tldr: "**As a** SpecWeave user following TDD or running grill reviews."
project: specweave
external:
  github:
    issue: 1542
    url: https://github.com/anton-abyzov/specweave/issues/1542
---

# US-005: Anti-Rationalization Tables (P2)

**Feature**: [FS-491](./FEATURE.md)

**As a** SpecWeave user following TDD or running grill reviews
**I want** explicit anti-rationalization tables with common excuses and rebuttals embedded in the skill instructions
**So that** AI agents resist the temptation to skip quality steps with plausible-sounding justifications

---

## Acceptance Criteria

- [x] **AC-US5-01**: Given sw:tdd-cycle SKILL.md is updated, when an agent reads it, then it contains an anti-rationalization table with 8+ entries (excuse -> rebuttal pairs)
- [x] **AC-US5-02**: The tdd-cycle table includes at minimum: "I'll test after" -> "Tests written after pass immediately, proving nothing", "This is too simple to test" -> rebuttal, "Just this once" -> rebuttal
- [x] **AC-US5-03**: Given sw:grill SKILL.md is updated, when an agent reads it, then it contains an anti-rationalization table with 6+ entries relevant to code review shortcuts
- [x] **AC-US5-04**: The grill table includes at minimum: "Close enough to the spec" -> "Close enough ships bugs", "We can fix it later" -> rebuttal, "The tests pass" -> rebuttal

---

## Implementation

**Increment**: [0491-shift-quality-left-per-task-gates](../../../../../increments/0491-shift-quality-left-per-task-gates/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-007**: Add Anti-Rationalization Table to sw:tdd-cycle SKILL.md
- [x] **T-008**: Add Anti-Rationalization Table to sw:grill SKILL.md

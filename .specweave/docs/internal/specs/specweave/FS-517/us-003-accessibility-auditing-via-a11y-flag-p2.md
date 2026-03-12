---
id: US-003
feature: FS-517
title: "Accessibility Auditing via --a11y Flag (P2)"
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** developer."
project: specweave
---

# US-003: Accessibility Auditing via --a11y Flag (P2)

**Feature**: [FS-517](./FEATURE.md)

**As a** developer
**I want** accessibility auditing integrated into my E2E test runs
**So that** I catch WCAG violations without needing a separate accessibility plugin

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given `sw:e2e --a11y <increment-id>` is invoked, when tests run, then each test page is scanned with `@axe-core/playwright` after the primary assertion
- [x] **AC-US3-02**: Given an axe violation is found on a page tested by `AC-US1-01`, when the report is generated, then the violation is attached to the `AC-US1-01` result entry under an `a11y` field
- [x] **AC-US3-03**: Given `--a11y` is used in standalone mode (no specific AC context), when violations are found, then they are grouped by page URL in the report's top-level `a11y` field
- [x] **AC-US3-04**: Given axe finds zero violations, when the report is generated, then the `a11y` field shows `{ violations: [], passes: N }` where N is the count of passed axe rules

---

## Implementation

**Increment**: [0517-sw-e2e-skill](../../../../../increments/0517-sw-e2e-skill/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-002**: Verify --a11y coverage in SKILL.md Section 6

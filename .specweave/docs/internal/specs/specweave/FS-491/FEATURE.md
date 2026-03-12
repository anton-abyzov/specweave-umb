---
id: FS-491
title: "Shift Quality Left — Per-Task Gates"
type: feature
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
lastUpdated: 2026-03-11
tldr: "SpecWeave currently batches all quality review at increment closure (`sw:grill` + `sw:done`)."
complexity: high
stakeholder_relevant: true
external_tools:
  github:
    type: 'milestone'
    id: 237
    url: 'https://github.com/anton-abyzov/specweave/milestone/237'
externalLinks:
  jira:
    epicKey: 'SWE2E-148'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-148'
    syncedAt: '2026-03-11T08:21:05.394Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 384
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/384'
    syncedAt: '2026-03-11T08:21:16.459Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# Shift Quality Left — Per-Task Gates

## TL;DR

**What**: SpecWeave currently batches all quality review at increment closure (`sw:grill` + `sw:done`).
**Status**: completed | **Priority**: P1
**User Stories**: 6

## Overview

SpecWeave currently batches all quality review at increment closure (`sw:grill` + `sw:done`). By the time reviewers examine the work, multiple tasks may have drifted from the spec. Bugs compound, and fixing late-discovered issues requires revisiting decisions made 10+ tasks ago. The obra/superpowers research (14 AI coding agent skills) proved that per-task spec-compliance and code-quality reviews catch drift early, reducing rework by surfacing misalignment after each task -- not at the end.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0491-shift-quality-left-per-task-gates](../../../../../increments/0491-shift-quality-left-per-task-gates/spec.md) | ✅ completed | 2026-03-11T00:00:00.000Z |

## User Stories

- [US-001: Per-Task Review Gates in sw:do (P1)](./us-001-per-task-review-gates-in-sw-do-p1.md)
- [US-002: Adversarial Spec Reviewer in sw:grill (P1)](./us-002-adversarial-spec-reviewer-in-sw-grill-p1.md)
- [US-003: Systematic Debugging Skill (P1)](./us-003-systematic-debugging-skill-p1.md)
- [US-004: Fresh Verification Discipline in sw:do (P2)](./us-004-fresh-verification-discipline-in-sw-do-p2.md)
- [US-005: Anti-Rationalization Tables (P2)](./us-005-anti-rationalization-tables-p2.md)
- [US-006: Public Docs and Changelog Updates (P2)](./us-006-public-docs-and-changelog-updates-p2.md)

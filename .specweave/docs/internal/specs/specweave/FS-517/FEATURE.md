---
id: FS-517
title: "sw:e2e -- SpecWeave-Integrated Playwright E2E Skill"
type: feature
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
lastUpdated: 2026-03-12
tldr: "The SpecWeave team-lead testing agent references `testing:e2e` which does not exist, leaving E2E test generation and execution as a manual gap."
complexity: high
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: 'SWE2E-193'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-193'
    syncedAt: '2026-03-12T21:09:38.671Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 1193
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/1193'
    syncedAt: '2026-03-12T21:09:46.533Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# sw:e2e -- SpecWeave-Integrated Playwright E2E Skill

## TL;DR

**What**: The SpecWeave team-lead testing agent references `testing:e2e` which does not exist, leaving E2E test generation and execution as a manual gap.
**Status**: completed | **Priority**: P1
**User Stories**: 4

![sw:e2e -- SpecWeave-Integrated Playwright E2E Skill illustration](assets/feature-fs-517.jpg)

## Overview

The SpecWeave team-lead testing agent references `testing:e2e` which does not exist, leaving E2E test generation and execution as a manual gap. There is no automated bridge between spec.md acceptance criteria and Playwright tests, and sw:done Gate 2a runs Playwright directly without structured AC-mapped reporting. Accessibility auditing also requires a separate (nonexistent) `testing:accessibility` plugin.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0517-sw-e2e-skill](../../../../../increments/0517-sw-e2e-skill/spec.md) | ✅ completed | 2026-03-12T00:00:00.000Z |

## User Stories

- [US-001: Generate E2E Tests from Acceptance Criteria (P1)](./us-001-generate-e2e-tests-from-acceptance-criteria-p1.md)
- [US-002: Run E2E Tests and Produce AC-Mapped Report (P1)](./us-002-run-e2e-tests-and-produce-ac-mapped-report-p1.md)
- [US-003: Accessibility Auditing via --a11y Flag (P2)](./us-003-accessibility-auditing-via-a11y-flag-p2.md)
- [US-004: Team-Lead Testing Agent Integration (P1)](./us-004-team-lead-testing-agent-integration-p1.md)

---
id: FS-531
title: "Fix test mock drift with shared npm constants"
type: feature
status: completed
priority: P1
created: 2026-03-15T00:00:00.000Z
lastUpdated: 2026-03-15
tldr: "PR #1572 auto-fix bot missed TC-UH-02 because the test mock strings for `installation-health-checker` lack the `--registry https://registry.npmjs.org` flag that production code includes."
complexity: high
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: 'SWE2E-218'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-218'
    syncedAt: '2026-03-15T08:59:04.639Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 1364
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/1364'
    syncedAt: '2026-03-15T08:59:11.400Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# Fix test mock drift with shared npm constants

## TL;DR

**What**: PR #1572 auto-fix bot missed TC-UH-02 because the test mock strings for `installation-health-checker` lack the `--registry https://registry.npmjs.org` flag that production code includes.
**Status**: completed | **Priority**: P1
**User Stories**: 4

![Fix test mock drift with shared npm constants illustration](assets/feature-fs-531.jpg)

## Overview

PR #1572 auto-fix bot missed TC-UH-02 because the test mock strings for `installation-health-checker` lack the `--registry https://registry.npmjs.org` flag that production code includes. The root cause is that npm command strings are hardcoded independently in both production code and test mocks, so changes to one silently leave the other stale. This fragile pattern affects 15+ test files across the codebase.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0531-fix-test-mock-drift-prevention](../../../../../increments/0531-fix-test-mock-drift-prevention/spec.md) | ✅ completed | 2026-03-15T00:00:00.000Z |

## User Stories

- [US-001: Fix TC-UH-02 Registry Flag in Test Mocks (P0)](./us-001-fix-tc-uh-02-registry-flag-in-test-mocks-p0.md)
- [US-002: Shared npm Constants Module (P0)](./us-002-shared-npm-constants-module-p0.md)
- [US-003: Migrate Production Code to Shared Constants (P0)](./us-003-migrate-production-code-to-shared-constants-p0.md)
- [US-004: Migrate Test Mocks to Shared Constants (P1)](./us-004-migrate-test-mocks-to-shared-constants-p1.md)

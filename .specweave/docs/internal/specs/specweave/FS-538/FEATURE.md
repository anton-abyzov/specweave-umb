---
id: FS-538
title: "Fix mobile project detection phantom plugin references and add tests"
type: feature
status: completed
priority: P1
created: 2026-03-15T00:00:00.000Z
lastUpdated: 2026-03-15
tldr: "The project-detector.ts module maps React Native, Expo, iOS, and Android project types to `plugins: ['mobile']`, but no 'mobile' plugin exists in marketplace.json."
complexity: medium
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: 'SWE2E-277'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-277'
    syncedAt: '2026-03-15T23:03:16.867Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 1374
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/1374'
    syncedAt: '2026-03-15T23:03:24.531Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# Fix mobile project detection phantom plugin references and add tests

## TL;DR

**What**: The project-detector.ts module maps React Native, Expo, iOS, and Android project types to `plugins: ['mobile']`, but no "mobile" plugin exists in marketplace.json.
**Status**: completed | **Priority**: P1
**User Stories**: 3

![Fix mobile project detection phantom plugin references and add tests illustration](assets/feature-fs-538.jpg)

## Overview

The project-detector.ts module maps React Native, Expo, iOS, and Android project types to `plugins: ['mobile']`, but no "mobile" plugin exists in marketplace.json. This causes phantom plugin references that silently fail during auto-install. Additionally, `build.gradle` detection triggers false positives for Java/Spring projects that use Gradle but are not Android projects. Finally, auto-install.ts COMPONENT_MAPPING has

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0538-mobile-detect-test-fix](../../../../../increments/0538-mobile-detect-test-fix/spec.md) | ✅ completed | 2026-03-15T00:00:00.000Z |

## User Stories

- [US-001: Remove Phantom Mobile Plugin References (P0)](./us-001-remove-phantom-mobile-plugin-references-p0.md)
- [US-002: Add Mobile Keywords to Auto-Install Component Mapping (P1)](./us-002-add-mobile-keywords-to-auto-install-component-mapping-p1.md)
- [US-003: Comprehensive Test Coverage for Mobile Detection Pipeline (P1)](./us-003-comprehensive-test-coverage-for-mobile-detection-pipeline-p1.md)

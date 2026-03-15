---
id: FS-527
title: Test AC Checkbox Sync
type: feature
status: active
priority: P2
created: 2026-03-15
lastUpdated: 2026-03-15
tldr: Test increment to verify that:.
complexity: medium
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: SWE2E-208
    epicUrl: https://antonabyzov.atlassian.net/browse/SWE2E-208
    syncedAt: 2026-03-15T03:06:35.791Z
    projectKey: SWE2E
    domain: antonabyzov.atlassian.net
  ado:
    featureId: 1356
    featureUrl: https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/1356
    syncedAt: 2026-03-15T03:06:40.652Z
    organization: EasyChamp
    project: SpecWeaveSync
external_tools:
  github:
    type: milestone
    id: 10
    url: https://github.com/anton-abyzov/specweave-umb/milestone/10
---

# Test AC Checkbox Sync

## TL;DR

**What**: Test increment to verify that:.
**Status**: active | **Priority**: P2
**User Stories**: 2

![Test AC Checkbox Sync illustration](assets/feature-fs-527.jpg)

## Overview

Test increment to verify that:
1. JIRA story descriptions now show native checkboxes (ADF taskItem) for each AC
2. Marking an AC complete in spec.md auto-updates the JIRA story description checkbox
3. Epic → Story hierarchy is intact in JIRA, ADO, and GitHub
4. ADO Issue appears as child of the ADO Epic with correct title

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0527-test-ac-checkbox-sync](../../../../../increments/0527-test-ac-checkbox-sync/spec.md) | ⏳ active | 2026-03-15 |

## User Stories

- [US-001: Verify JIRA native AC checkboxes](./us-001-verify-jira-native-ac-checkboxes.md)
- [US-002: Verify full hierarchy across platforms](./us-002-verify-full-hierarchy-across-platforms.md)

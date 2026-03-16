---
id: FS-537
title: "Project-Specific Skill Generation + Public Docs Cross-References"
type: feature
status: completed
priority: P1
created: 2026-03-15T00:00:00.000Z
lastUpdated: 2026-03-15
tldr: "SpecWeave already extracts rich project knowledge through living docs analysis (module graphs, API surfaces, ADRs, skill-memories)."
complexity: high
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: 'SWE2E-269'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-269'
    syncedAt: '2026-03-15T22:08:18.163Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 1373
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/1373'
    syncedAt: '2026-03-15T22:08:29.621Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# Project-Specific Skill Generation + Public Docs Cross-References

## TL;DR

**What**: SpecWeave already extracts rich project knowledge through living docs analysis (module graphs, API surfaces, ADRs, skill-memories).
**Status**: completed | **Priority**: P1
**User Stories**: 7

![Project-Specific Skill Generation + Public Docs Cross-References illustration](assets/feature-fs-537.jpg)

## Overview

SpecWeave already extracts rich project knowledge through living docs analysis (module graphs, API surfaces, ADRs, skill-memories). However, this knowledge stays locked inside markdown files -- it is never codified into reusable AI coding instructions. Teams repeatedly make the same corrections across increments without those patterns ever becoming permanent skills. Meanwhile, the 26 existing skills have no cross-references to their public documentation, making discoverability poor.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0537-project-skill-gen-docs](../../../../../increments/0537-project-skill-gen-docs/spec.md) | ✅ completed | 2026-03-15T00:00:00.000Z |

## User Stories

- [US-001: Signal Detection on Increment Closure](./us-001-signal-detection-on-increment-closure.md)
- [US-002: Suggestion Engine](./us-002-suggestion-engine.md)
- [US-003: Skill Generation Command](./us-003-skill-generation-command.md)
- [US-004: Drift Detection](./us-004-drift-detection.md)
- [US-005: SkillGen Configuration Model](./us-005-skillgen-configuration-model.md)
- [US-006: Public Documentation Page](./us-006-public-documentation-page.md)
- [US-007: Resources Section for Existing Skills](./us-007-resources-section-for-existing-skills.md)

---
id: FS-498
title: "Studio Skill Origin Classification (Consumed vs Editable)"
type: feature
status: completed
priority: P1
created: 2026-03-11T00:00:00.000Z
lastUpdated: 2026-03-12
tldr: "When `npx vskill studio` scans for skills, it discovers ALL SKILL.md files including those inside agent config directories (`.claude/skills/`, `.cursor/skills/`, `.windsurf/skills/`, etc.)."
complexity: high
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: 'SWE2E-168'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-168'
    syncedAt: '2026-03-12T00:15:00.493Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 766
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/766'
    syncedAt: '2026-03-12T00:15:07.458Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# Studio Skill Origin Classification (Consumed vs Editable)

## TL;DR

**What**: When `npx vskill studio` scans for skills, it discovers ALL SKILL.md files including those inside agent config directories (`.claude/skills/`, `.cursor/skills/`, `.windsurf/skills/`, etc.).
**Status**: completed | **Priority**: P1
**User Stories**: 5

![Studio Skill Origin Classification (Consumed vs Editable) illustration](assets/feature-fs-498.jpg)

## Overview

When `npx vskill studio` scans for skills, it discovers ALL SKILL.md files including those inside agent config directories (`.claude/skills/`, `.cursor/skills/`, `.windsurf/skills/`, etc.). These are installed copies meant for consumption by AI agents, not the user's source skills for editing and development. Currently there is no visual distinction -- users cannot tell which skills they should be working on versus which are just installed copies.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0498-studio-skill-origin-classification](../../../../../increments/0498-studio-skill-origin-classification/spec.md) | ✅ completed | 2026-03-11T00:00:00.000Z |

## User Stories

- [US-001: Origin Classification in Scanner](./us-001-origin-classification-in-scanner.md)
- [US-002: Sidebar Split into Source and Installed Sections](./us-002-sidebar-split-into-source-and-installed-sections.md)
- [US-003: Visual De-emphasis of Installed Skills](./us-003-visual-de-emphasis-of-installed-skills.md)
- [US-004: Read-Only Mode for Installed Skills](./us-004-read-only-mode-for-installed-skills.md)
- [US-005: Info Banner Explaining Origin Distinction](./us-005-info-banner-explaining-origin-distinction.md)

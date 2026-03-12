---
id: FS-496
title: "Skill Studio UI Polish & Editor AI Builder"
type: feature
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
lastUpdated: 2026-03-11
tldr: "The Skill Studio Create Skill forms label the skill definition body as 'System Prompt,' which is confusing because the file is actually SKILL.md."
complexity: high
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: 'SWE2E-156'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-156'
    syncedAt: '2026-03-11T22:58:00.942Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 556
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/556'
    syncedAt: '2026-03-11T22:58:11.677Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# Skill Studio UI Polish & Editor AI Builder

## TL;DR

**What**: The Skill Studio Create Skill forms label the skill definition body as "System Prompt," which is confusing because the file is actually SKILL.md.
**Status**: completed | **Priority**: P1
**User Stories**: 6

## Overview

The Skill Studio Create Skill forms label the skill definition body as "System Prompt," which is confusing because the file is actually SKILL.md. The body content in both create forms and the SkillContentViewer renders as raw preformatted text rather than styled markdown. The description textarea is too short. The Editor page lacks an AI regenerate workflow for iterating on skill content. There is no visibility into whether the Skill-Creator tool is installed.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0496-skill-studio-ui-polish](../../../../../increments/0496-skill-studio-ui-polish/spec.md) | ✅ completed | 2026-03-11T00:00:00.000Z |

## User Stories

- [US-001: Rename "System Prompt" to "SKILL.md"](./us-001-rename-system-prompt-to-skill-md.md)
- [US-002: Write/Preview Toggle for SKILL.md Body](./us-002-write-preview-toggle-for-skill-md-body.md)
- [US-003: Increase Description Textarea Height](./us-003-increase-description-textarea-height.md)
- [US-004: Render SKILL.md Body as Markdown in SkillContentViewer](./us-004-render-skill-md-body-as-markdown-in-skillcontentviewer.md)
- [US-005: AI Regenerate on Editor Page](./us-005-ai-regenerate-on-editor-page.md)
- [US-006: Skill-Creator Installation Check](./us-006-skill-creator-installation-check.md)

---
id: FS-457
title: Consent-First Plugin Auto-Loading
type: feature
status: planned
priority: P0
created: 2026-03-09T00:00:00.000Z
lastUpdated: 2026-03-10T00:00:00.000Z
tldr: >-
  SpecWeave's plugin auto-loading mechanism silently installs plugins without
  user consent.
complexity: low
stakeholder_relevant: true
external_tools:
  github:
    type: milestone
    id: 11
    url: 'https://github.com/anton-abyzov/vskill/milestone/11'
externalLinks:
  jira:
    epicKey: SWE2E-56
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-56'
    syncedAt: '2026-03-10T07:49:17.523Z'
    projectKey: SWE2E
    domain: antonabyzov.atlassian.net
  ado:
    featureId: 121
    featureUrl: >-
      https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/121
    syncedAt: '2026-03-10T07:49:18.269Z'
    organization: EasyChamp
    project: SpecWeaveSync
updated: '2026-03-10'
---

# Consent-First Plugin Auto-Loading

## TL;DR

**What**: SpecWeave's plugin auto-loading mechanism silently installs plugins without user consent.
**Status**: planned | **Priority**: P0
**User Stories**: 1

## Overview

SpecWeave's plugin auto-loading mechanism silently installs plugins without user consent. The `UserPromptSubmit` hook uses an LLM (Haiku) to detect relevant plugins and installs them with `--force --yes` flags, bypassing any approval step. This leads to irrelevant plugins being installed (e.g., Java/Rust backend skills for a Node.js project). Additionally, LSP plugins bypass the existing `suggestOnly` config flag entirely. The `suggestOnly` mechanism exists but defaults to `false`, making the unsafe behavior the default.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0457-prevent-unwanted-agent-dotfolders](../../../../../increments/0457-prevent-unwanted-agent-dotfolders/spec.md) | ⏳ planned | 2026-03-09 |

## User Stories

- [US-VK-005: Clean Up Phantom Marketplace Entries](./us-vk-005-clean-up-phantom-marketplace-entries.md)

## Related Projects

This feature spans multiple projects:

- [specweave](../../specweave/FS-457/)

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
complexity: high
stakeholder_relevant: true
external_tools:
  github:
    type: milestone
    id: 234
    url: 'https://github.com/anton-abyzov/specweave/milestone/234'
externalLinks:
  jira:
    epicKey: SWE2E-55
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-55'
    syncedAt: '2026-03-10T07:49:05.975Z'
    projectKey: SWE2E
    domain: antonabyzov.atlassian.net
  ado:
    featureId: 120
    featureUrl: >-
      https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/120
    syncedAt: '2026-03-10T07:49:06.963Z'
    organization: EasyChamp
    project: SpecWeaveSync
updated: '2026-03-10'
---

# Consent-First Plugin Auto-Loading

## TL;DR

**What**: SpecWeave's plugin auto-loading mechanism silently installs plugins without user consent.
**Status**: planned | **Priority**: P0
**User Stories**: 6

## Overview

SpecWeave's plugin auto-loading mechanism silently installs plugins without user consent. The `UserPromptSubmit` hook uses an LLM (Haiku) to detect relevant plugins and installs them with `--force --yes` flags, bypassing any approval step. This leads to irrelevant plugins being installed (e.g., Java/Rust backend skills for a Node.js project). Additionally, LSP plugins bypass the existing `suggestOnly` config flag entirely. The `suggestOnly` mechanism exists but defaults to `false`, making the unsafe behavior the default.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0457-prevent-unwanted-agent-dotfolders](../../../../../increments/0457-prevent-unwanted-agent-dotfolders/spec.md) | ⏳ planned | 2026-03-09 |

## User Stories

- [US-SW-001: Default to Suggest-Only Mode](./us-sw-001-default-to-suggest-only-mode.md)
- [US-SW-002: Suggest-Only Recommendation Display](./us-sw-002-suggest-only-recommendation-display.md)
- [US-SW-003: LSP Plugin Consent Guard](./us-sw-003-lsp-plugin-consent-guard.md)
- [US-SW-004: TypeScript Types and Config Schema Update](./us-sw-004-typescript-types-and-config-schema-update.md)
- [US-SW-006: Update Hook Plugin Detection Logic](./us-sw-006-update-hook-plugin-detection-logic.md)
- [US-SW-007: Test Suite Updates](./us-sw-007-test-suite-updates.md)

## Related Projects

This feature spans multiple projects:

- [vskill](../../vskill/FS-457/)

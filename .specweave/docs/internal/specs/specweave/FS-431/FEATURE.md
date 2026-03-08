---
id: FS-431
title: HTTP Hook Server for SpecWeave
type: feature
status: completed
priority: P0
created: 2026-03-05T00:00:00.000Z
lastUpdated: 2026-03-07T00:00:00.000Z
tldr: >-
  SpecWeave's current hook system relies on bash scripts, a file-based JSONL
  event queue, and a background processor daemon with a 60-second idle timeout.
complexity: high
stakeholder_relevant: true
external_tools:
  github:
    type: milestone
    id: 233
    url: 'https://github.com/anton-abyzov/specweave/milestone/233'
externalLinks:
  jira:
    epicKey: WTTC-97
    epicUrl: 'https://antonabyzov.atlassian.net/browse/WTTC-97'
    syncedAt: '2026-03-07T23:54:13.429Z'
    projectKey: WTTC
    domain: antonabyzov.atlassian.net
  ado:
    featureId: 98
    featureUrl: >-
      https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/98
    syncedAt: '2026-03-07T23:54:13.842Z'
    organization: EasyChamp
    project: SpecWeaveSync
updated: '2026-03-07'
---

# HTTP Hook Server for SpecWeave

## TL;DR

**What**: SpecWeave's current hook system relies on bash scripts, a file-based JSONL event queue, and a background processor daemon with a 60-second idle timeout.
**Status**: completed | **Priority**: P0
**User Stories**: 8

![HTTP Hook Server for SpecWeave illustration](assets/feature-fs-431.jpg)

## Overview

SpecWeave's current hook system relies on bash scripts, a file-based JSONL event queue, and a background processor daemon with a 60-second idle timeout. This architecture is fragile: bash scripts break on Windows, the file-based queue has race conditions, the processor daemon can miss events during its idle gap, and analytics are scattered across flat files. Claude Code now supports HTTP hooks natively, posting events to a URL and awaiting a JSON response. Replacing the bash/daemon system with an HTTP server built into the existing dashboard process eliminates these reliability issues while enabling real-time event visibility.

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0431-http-hook-server](../../../../../increments/0431-http-hook-server/spec.md) | ✅ completed | 2026-03-05T00:00:00.000Z |

## User Stories

- [US-001: HTTP Hook Event Receiver](./us-001-http-hook-event-receiver.md)
- [US-002: In-Memory Event Store with JSONL Persistence](./us-002-in-memory-event-store-with-jsonl-persistence.md)
- [US-003: Dashboard Server Auto-Start on Session Begin](./us-003-dashboard-server-auto-start-on-session-begin.md)
- [US-004: Command-Bridge for Command-Only Events](./us-004-command-bridge-for-command-only-events.md)
- [US-005: TypeScript Event Handlers Replacing Bash](./us-005-typescript-event-handlers-replacing-bash.md)
- [US-006: HooksPage Dashboard UI](./us-006-hookspage-dashboard-ui.md)
- [US-007: AgentsPage Dashboard UI](./us-007-agentspage-dashboard-ui.md)
- [US-008: Settings Generator and Migration Config](./us-008-settings-generator-and-migration-config.md)

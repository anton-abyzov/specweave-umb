---
id: FS-468
title: "MCP-Aware Eval Simulation for Skill Benchmarks"
type: feature
status: completed
priority: P1
created: 2026-03-10T00:00:00.000Z
lastUpdated: 2026-03-12
tldr: "The vskill eval system already has basic MCP awareness: `mcp-detector.ts` identifies MCP tool references in SKILL.md content, and `prompt-builder.ts` injects simulation instructions into the eval system prompt when MCP dependencies are detected."
complexity: high
stakeholder_relevant: true
externalLinks:
  jira:
    epicKey: 'SWE2E-165'
    epicUrl: 'https://antonabyzov.atlassian.net/browse/SWE2E-165'
    syncedAt: '2026-03-12T00:14:06.858Z'
    projectKey: 'SWE2E'
    domain: 'antonabyzov.atlassian.net'
  ado:
    featureId: 744
    featureUrl: 'https://dev.azure.com/easychamp/99023ebb-7d44-42c8-b27f-09378c47172b/_workitems/edit/744'
    syncedAt: '2026-03-12T00:14:13.503Z'
    organization: 'EasyChamp'
    project: 'SpecWeaveSync'
---

# MCP-Aware Eval Simulation for Skill Benchmarks

## TL;DR

**What**: The vskill eval system already has basic MCP awareness: `mcp-detector.ts` identifies MCP tool references in SKILL.md content, and `prompt-builder.ts` injects simulation instructions into the eval system prompt when MCP dependencies are detected.
**Status**: completed | **Priority**: P1
**User Stories**: 5

![MCP-Aware Eval Simulation for Skill Benchmarks illustration](assets/feature-fs-468.jpg)

## Overview

The vskill eval system already has basic MCP awareness: `mcp-detector.ts` identifies MCP tool references in SKILL.md content, and `prompt-builder.ts` injects simulation instructions into the eval system prompt when MCP dependencies are detected. However, this initial implementation has gaps that cause MCP-dependent skills to receive lower eval scores than they deserve:

## Implementation History

| Increment | Status | Completion Date |
|-----------|--------|----------------|
| [0468-mcp-eval-simulation](../../../../../increments/0468-mcp-eval-simulation/spec.md) | ✅ completed | 2026-03-10T00:00:00.000Z |

## User Stories

- [US-001: MCP-aware eval generation (P1)](./us-001-mcp-aware-eval-generation-p1.md)
- [US-002: Simulation-aware assertion judging (P1)](./us-002-simulation-aware-assertion-judging-p1.md)
- [US-003: Expand MCP server registry (P1)](./us-003-expand-mcp-server-registry-p1.md)
- [US-004: Fair MCP-aware comparison mode (P2)](./us-004-fair-mcp-aware-comparison-mode-p2.md)
- [US-005: Simulation quality signal in benchmark results (P2)](./us-005-simulation-quality-signal-in-benchmark-results-p2.md)

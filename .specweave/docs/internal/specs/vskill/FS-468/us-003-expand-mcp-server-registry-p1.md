---
id: US-003
feature: FS-468
title: "Expand MCP server registry (P1)"
status: completed
priority: P1
created: 2026-03-10T00:00:00.000Z
tldr: "**As a** skill author using Notion, Jira, Confluence, Figma, or Sentry MCP tools."
project: vskill
---

# US-003: Expand MCP server registry (P1)

**Feature**: [FS-468](./FEATURE.md)

**As a** skill author using Notion, Jira, Confluence, Figma, or Sentry MCP tools
**I want** the MCP detector to recognize my tool references
**So that** my skill gets proper simulation instructions during eval

---

## Acceptance Criteria

- [x] **AC-US3-01**: `MCP_REGISTRY` includes entries for Notion (`notion_`), Jira (`jira_`), Confluence (`confluence_`), Figma (`figma_`), and Sentry (`sentry_`)
- [x] **AC-US3-02**: Each new registry entry has a valid server name, prefix array, URL, and transport type
- [x] **AC-US3-03**: `detectMcpDependencies` correctly matches tool references for all new servers

---

## Implementation

**Increment**: [0468-mcp-eval-simulation](../../../../../increments/0468-mcp-eval-simulation/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_

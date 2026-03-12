---
id: US-001
feature: FS-468
title: "MCP-aware eval generation (P1)"
status: completed
priority: P1
created: 2026-03-10T00:00:00.000Z
tldr: "**As a** skill author."
project: vskill
---

# US-001: MCP-aware eval generation (P1)

**Feature**: [FS-468](./FEATURE.md)

**As a** skill author
**I want** `vskill eval init` to generate eval cases that account for MCP tool simulation
**So that** my MCP-dependent skill's evals have assertions that are fair to simulated output

---

## Acceptance Criteria

- [x] **AC-US1-01**: `buildEvalInitPrompt` detects MCP dependencies in the skill content and appends MCP simulation context to the generation prompt
- [x] **AC-US1-02**: Generated eval assertions for MCP skills reference "simulated" tool calls (e.g. "demonstrates calling slack_send_message with channel and message parameters") rather than expecting real API responses
- [x] **AC-US1-03**: Generated eval cases for non-MCP skills are unchanged (no regression)

---

## Implementation

**Increment**: [0468-mcp-eval-simulation](../../../../../increments/0468-mcp-eval-simulation/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_

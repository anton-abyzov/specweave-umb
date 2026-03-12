---
id: US-002
feature: FS-468
title: "Simulation-aware assertion judging (P1)"
status: completed
priority: P1
created: 2026-03-10T00:00:00.000Z
tldr: "**As a** skill author."
project: vskill
---

# US-002: Simulation-aware assertion judging (P1)

**Feature**: [FS-468](./FEATURE.md)

**As a** skill author
**I want** the eval judge to understand that tool calls are simulated during evaluation
**So that** assertions are evaluated against the quality of the simulation rather than real API responses

---

## Acceptance Criteria

- [x] **AC-US2-01**: The judge system prompt is augmented with simulation context when the skill has MCP dependencies
- [x] **AC-US2-02**: The judge evaluates whether the LLM demonstrated the correct tool call workflow (tool name, parameters, realistic mock response) rather than checking for real API artifacts
- [x] **AC-US2-03**: Non-MCP skill judging is unaffected (no regression)

---

## Implementation

**Increment**: [0468-mcp-eval-simulation](../../../../../increments/0468-mcp-eval-simulation/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_

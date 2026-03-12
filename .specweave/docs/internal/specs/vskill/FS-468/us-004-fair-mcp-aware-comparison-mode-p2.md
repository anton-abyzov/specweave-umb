---
id: US-004
feature: FS-468
title: "Fair MCP-aware comparison mode (P2)"
status: completed
priority: P1
created: 2026-03-10T00:00:00.000Z
tldr: "**As a** skill author."
project: vskill
---

# US-004: Fair MCP-aware comparison mode (P2)

**Feature**: [FS-468](./FEATURE.md)

**As a** skill author
**I want** the A/B comparison eval to account for MCP simulation so skill vs. baseline is a fair comparison
**So that** my MCP-dependent skill is not unfairly penalized in comparison benchmarks

---

## Acceptance Criteria

- [x] **AC-US4-01**: The comparator's blind judge prompt includes context that both responses may contain simulated tool interactions
- [x] **AC-US4-02**: The comparison judge evaluates simulation quality (realistic parameters, plausible responses, complete workflow) rather than penalizing simulated output
- [x] **AC-US4-03**: Comparison results for non-MCP skills are unchanged

---

## Implementation

**Increment**: [0468-mcp-eval-simulation](../../../../../increments/0468-mcp-eval-simulation/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_

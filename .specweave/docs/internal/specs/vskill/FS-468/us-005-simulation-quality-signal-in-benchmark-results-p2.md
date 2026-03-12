---
id: US-005
feature: FS-468
title: "Simulation quality signal in benchmark results (P2)"
status: completed
priority: P1
created: 2026-03-10T00:00:00.000Z
tldr: "**As a** platform operator."
project: vskill
---

# US-005: Simulation quality signal in benchmark results (P2)

**Feature**: [FS-468](./FEATURE.md)

**As a** platform operator
**I want** benchmark results to indicate whether MCP simulation was active during the eval run
**So that** I can distinguish eval results for MCP skills from non-MCP skills

---

## Acceptance Criteria

- [x] **AC-US5-01**: `BenchmarkResult` includes an optional `mcpSimulation` field indicating whether simulation mode was active and which servers were simulated
- [x] **AC-US5-02**: The benchmark output (benchmark.json) records MCP simulation metadata when applicable
- [x] **AC-US5-03**: History and stats computations handle the new field without breaking existing data

---

## Implementation

**Increment**: [0468-mcp-eval-simulation](../../../../../increments/0468-mcp-eval-simulation/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_

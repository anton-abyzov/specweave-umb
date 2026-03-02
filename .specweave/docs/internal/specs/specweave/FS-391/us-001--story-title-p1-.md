---
id: US-001
feature: FS-391
title: "ASCII Diagram Utility Functions (P1)"
status: completed
priority: P1
created: 2026-03-01T00:00:00.000Z
tldr: "**As a** SpecWeave skill author
**I want** reusable ASCII diagram generator functions
**So that** skills produce consistent, well-formatted diagrams for AskUserQuestion previews."
project: specweave
---

# US-001: ASCII Diagram Utility Functions (P1)

**Feature**: [FS-391](./FEATURE.md)

**As a** SpecWeave skill author
**I want** reusable ASCII diagram generator functions
**So that** skills produce consistent, well-formatted diagrams for AskUserQuestion previews

---

## Acceptance Criteria

- [x] **AC-US1-01**: `renderBoxDiagram(nodes, connections)` generates ASCII box diagrams with Unicode box-drawing characters, max 80 chars wide
- [x] **AC-US1-02**: `renderDAG(tasks, dependencies)` generates ASCII directed acyclic graph showing parallel lanes and critical path
- [x] **AC-US1-03**: `renderTable(headers, rows, options?)` generates ASCII tables with aligned columns and optional header separators
- [x] **AC-US1-04**: `renderTree(items)` generates ASCII tree diagrams with proper branch characters
- [x] **AC-US1-05**: All functions handle edge cases: empty input, single node, overflow truncation at 80 chars

---

## Implementation

**Increment**: [0391-askuserquestion-markdown-previews](../../../../../increments/0391-askuserquestion-markdown-previews/spec.md)

**Tasks**: See increment tasks.md for implementation details.

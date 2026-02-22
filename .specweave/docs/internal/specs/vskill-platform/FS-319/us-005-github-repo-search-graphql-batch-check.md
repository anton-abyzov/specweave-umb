---
id: US-005
feature: FS-319
title: GitHub Repo Search + GraphQL Batch Check
status: complete
priority: P1
created: 2026-02-22
project: vskill-platform
external:
  github:
    issue: 1269
    url: https://github.com/anton-abyzov/specweave/issues/1269
---
# US-005: GitHub Repo Search + GraphQL Batch Check

**Feature**: [FS-319](./FEATURE.md)

platform operator
**I want** date-sharded repo search combined with GraphQL batch file-existence checks
**So that** I can discover 70k+ repos by checking candidates in bulk (250k repos/hr/token)

---

## Acceptance Criteria

- [x] **AC-US5-01**: Repo search uses monthly date shards (`created:2024-01-01..2024-01-31`, etc.) + star shards
- [x] **AC-US5-02**: Candidate repos are batch-checked for SKILL.md via GraphQL aliases (50 repos per query)
- [x] **AC-US5-03**: GraphQL queries check multiple file patterns: `SKILL.md`, `.cursorrules`, `mcp.json`, `.claude/commands`
- [x] **AC-US5-04**: Token rotation across multiple GitHub tokens for throughput
- [x] **AC-US5-05**: Repos confirmed to have target files are batch-submitted to platform

---

## Implementation

**Increment**: [0319-discovery-scale-up](../../../../../increments/0319-discovery-scale-up/spec.md)


---
id: US-001
feature: FS-520
title: "PR-Based Push Strategy Configuration (P1)"
status: completed
priority: P1
created: 2026-03-13T00:00:00.000Z
tldr: "**As a** team lead configuring SpecWeave."
project: specweave
---

# US-001: PR-Based Push Strategy Configuration (P1)

**Feature**: [FS-520](./FEATURE.md)

**As a** team lead configuring SpecWeave
**I want** to set `cicd.pushStrategy` to `pr-based` with git-specific options
**So that** all increment work flows through pull requests instead of direct pushes

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given a `config.json` with `cicd.pushStrategy: "pr-based"`, when the config loader reads the file, then it parses the `cicd.git` sub-object containing `branchPrefix` (string, default `"sw/"`), `targetBranch` (string, default `"main"`), and `deleteOnMerge` (boolean, default `true`)
- [x] **AC-US1-02**: Given `cicd.pushStrategy` is absent from config, when the config loader applies defaults, then `pushStrategy` defaults to `"direct"` and no `git` sub-object is required
- [x] **AC-US1-03**: Given the `CiCdConfig` TypeScript interface, when a developer inspects the type, then it contains a `git?: { branchPrefix: string; targetBranch: string; deleteOnMerge: boolean }` sub-object
- [x] **AC-US1-04**: Given a `PrRef` interface, when a developer inspects the type, then it contains `repo` (string), `prNumber` (number), `prUrl` (string), `branch` (string), `targetBranch` (string), and `createdAt` (ISO 8601 string)
- [x] **AC-US1-05**: Given the `IncrementMetadataV2` interface, when a developer inspects the type, then it contains an optional `prRefs?: PrRef[]` field

---

## Implementation

**Increment**: [0520-pr-based-increment-closure](../../../../../increments/0520-pr-based-increment-closure/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Add GitConfig interface and extend CiCdConfig with git sub-object
- [x] **T-002**: Extend config-loader RawConfig to parse cicd.git sub-object
- [x] **T-003**: Add PrRef interface and prRefs field to IncrementMetadataV2

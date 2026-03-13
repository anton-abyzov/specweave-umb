---
id: US-004
feature: FS-520
title: "Enterprise Environment Promotion Configuration (P2)"
status: completed
priority: P1
created: 2026-03-13T00:00:00.000Z
tldr: "**As an** enterprise team lead."
project: specweave
---

# US-004: Enterprise Environment Promotion Configuration (P2)

**Feature**: [FS-520](./FEATURE.md)

**As an** enterprise team lead
**I want** to configure environment promotion strategies in the `cicd` config
**So that** PRs can target specific environment branches in a structured release pipeline

---

## Acceptance Criteria

- [x] **AC-US4-01**: Given a `config.json` with `cicd.release.strategy` set to `"env-promotion"` and `cicd.environments` defined as an ordered array of `{ name: string; branch: string }` objects (e.g., `[{name: "dev", branch: "develop"}, {name: "staging", branch: "staging"}, {name: "prod", branch: "main"}]`), when the config loader reads the file, then both fields are parsed and available on `CiCdConfig`
- [x] **AC-US4-02**: Given `cicd.release.strategy` is absent, when the config loader applies defaults, then it defaults to `"trunk"` and no `environments` array is required
- [x] **AC-US4-03**: Given `release.strategy` is `"env-promotion"` and `pushStrategy` is `"pr-based"`, when `sw:pr` runs, then the PR targets the first environment branch in the `environments` array (the lowest environment) instead of `git.targetBranch`

---

## Implementation

**Increment**: [0520-pr-based-increment-closure](../../../../../increments/0520-pr-based-increment-closure/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-011**: Add ReleaseConfig and EnvironmentConfig interfaces to CiCdConfig (P2)
- [x] **T-012**: Extend config-loader to parse and merge release and environments (P2)
- [x] **T-013**: Implement env-promotion target branch selection in sw:pr (P2)
- [x] **T-014**: Write integration tests for full PR-based config and metadata round-trip (P2)

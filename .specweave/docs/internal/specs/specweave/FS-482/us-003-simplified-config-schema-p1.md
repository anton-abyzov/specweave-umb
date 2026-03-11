---
id: US-003
feature: FS-482
title: Simplified Config Schema (P1)
status: not_started
priority: P1
created: 2026-03-10
tldr: "**As a** developer."
project: specweave
external:
  github:
    issue: 1530
    url: https://github.com/anton-abyzov/specweave/issues/1530
---

# US-003: Simplified Config Schema (P1)

**Feature**: [FS-482](./FEATURE.md)

**As a** developer
**I want** the generated config.json to be minimal and clean
**So that** it is not cluttered with unconfigured external tool settings

---

## Acceptance Criteria

- [ ] **AC-US3-01**: Given a fresh init, when config.json is generated, then it contains no `multiProject`, `issueTracker`, `projectMaturity`, or `structureDeferred` fields
- [ ] **AC-US3-02**: Given a fresh init, when config.json is generated, then it contains no sync profiles or provider-specific connection settings
- [ ] **AC-US3-03**: Given a directory with a GitHub remote in `.git/config`, when init runs, then `repository.provider` is set to "github" and `repository.organization` is populated from the remote URL
- [ ] **AC-US3-04**: Given an existing config.json that contains sync profiles, umbrella config, or issueTracker sections, when that config is loaded by any SpecWeave command, then it still works correctly (backward compatible via optional chaining)

---

## Implementation

**Increment**: [0482-simplify-init](../../../../../increments/0482-simplify-init/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-008**: Verify config.json has no external tool fields after init
- [ ] **T-009**: Verify provider auto-detection populates config.json
- [ ] **T-010**: Verify backward compatibility with existing configs

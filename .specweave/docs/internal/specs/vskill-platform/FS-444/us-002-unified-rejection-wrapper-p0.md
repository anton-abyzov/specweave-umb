---
id: US-002
feature: FS-444
title: "Unified Rejection Wrapper (P0)"
status: completed
priority: P0
created: 2026-03-07T00:00:00.000Z
tldr: "**As a** platform developer."
project: vskill-platform
external:
  github:
    issue: 32
    url: https://github.com/anton-abyzov/vskill-platform/issues/32
---

# US-002: Unified Rejection Wrapper (P0)

**Feature**: [FS-444](./FEATURE.md)

**As a** platform developer
**I want** a single `shouldRejectSkillPath()` function that combines agent-config and framework-plugin checks
**So that** call sites use one function for all path rejection logic

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given a path inside `.claude/skills/`, when `shouldRejectSkillPath()` is called, then it returns `true` (agent-config rejection still works)
- [x] **AC-US2-02**: Given a path inside `plugins/specweave/skills/`, when `shouldRejectSkillPath()` is called, then it returns `true` (framework-plugin rejection works)
- [x] **AC-US2-03**: Given a legitimate skill path like `skills/frontend/SKILL.md`, when `shouldRejectSkillPath()` is called, then it returns `false`
- [x] **AC-US2-04**: `isAgentConfigPath()` remains exported for backward compatibility; `shouldRejectSkillPath()` is the recommended entrypoint

---

## Implementation

**Increment**: [0444-filter-framework-plugin-skills](../../../../../increments/0444-filter-framework-plugin-skills/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-003**: Add `shouldRejectSkillPath()` and `rejectionReason()` to skill-path-validation.ts
- [x] **T-004**: TDD REFACTOR - skill-path-validation.ts

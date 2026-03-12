---
id: US-003
feature: FS-502
title: "Component Migration to Shared Context"
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** developer."
project: vskill
external:
  github:
    issue: 98
    url: https://github.com/anton-abyzov/vskill/issues/98
---

# US-003: Component Migration to Shared Context

**Feature**: [FS-502](./FEATURE.md)

**As a** developer
**I want** all 10 components that currently call `api.getConfig()` independently to use the shared ConfigContext instead
**So that** config state is consistent everywhere and we remove duplicated fetch logic

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given the codebase after migration, when searching for `api.getConfig()` in component files, then zero direct calls exist in: ModelSelector, LeftPanel, CreateSkillInline, SkillImprovePanel, AiEditBar, EditorPanel, ModelCompareModal, BenchmarkPage, ComparisonPage, CreateSkillPage
- [x] **AC-US3-02**: Given components that derive local model overrides from config (SkillImprovePanel, AiEditBar, CreateSkillPage), when they mount, then they initialize their local "selected model for this action" state from the context's config values while retaining independent local model selection
- [x] **AC-US3-03**: Given BenchmarkPage calls `handleStartBenchmark` or `handleStartBaseline`, when the run starts, then it reads the model from the context's cached value (no additional `api.getConfig()` call)

---

## Implementation

**Increment**: [0502-config-context-sync](../../../../../increments/0502-config-context-sync/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-009**: Migrate ModelSelector to useConfig() and updateConfig() (Category C)
- [x] **T-003**: Migrate LeftPanel to useConfig() (Category A)
- [x] **T-004**: Migrate CreateSkillInline to useConfig() (Category A)
- [x] **T-005**: Migrate ModelCompareModal to useConfig() (Category A)
- [x] **T-006**: Migrate EditorPanel to useConfig() (Category A)
- [x] **T-007**: Migrate BenchmarkPage to useConfig() — 3 call sites (Category A)
- [x] **T-008**: Migrate ComparisonPage to useConfig() (Category A)
- [x] **T-010**: Migrate SkillImprovePanel to useConfig() preserving local model override (Category B)
- [x] **T-011**: Migrate AiEditBar to useConfig() preserving local model override (Category B)
- [x] **T-012**: Migrate CreateSkillPage to useConfig() preserving local model override (Category B)
- [x] **T-013**: Verify zero api.getConfig() calls in all migrated component files
- [x] **T-014**: Run full test suite and confirm no regressions

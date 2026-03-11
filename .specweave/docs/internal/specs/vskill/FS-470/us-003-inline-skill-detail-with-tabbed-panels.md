---
id: US-003
feature: FS-470
title: "Inline Skill Detail with Tabbed Panels"
status: completed
priority: P1
created: 2026-03-10T00:00:00.000Z
tldr: "**As a** skill author evaluating and editing a skill."
project: vskill
external:
  github:
    issue: 61
    url: https://github.com/anton-abyzov/vskill/issues/61
---

# US-003: Inline Skill Detail with Tabbed Panels

**Feature**: [FS-470](./FEATURE.md)

**As a** skill author evaluating and editing a skill
**I want** the right panel to show skill details organized in tabs matching the current workspace panels
**So that** I can edit, test, run evals, check activation, view history, and inspect dependencies without navigating away

---

## Acceptance Criteria

- [x] **AC-US3-01**: Clicking a skill card in the left panel selects it and renders its detail in the right panel without a page navigation or hash change
- [x] **AC-US3-02**: The selected skill card is highlighted with a left accent border (`var(--accent)`) and slightly elevated background (`var(--surface-2)`)
- [x] **AC-US3-03**: The detail panel header shows a breadcrumb (plugin / skill), benchmark status pill, pass rate, and case/assertion counts (reusing current `WorkspaceHeader` data logic)
- [x] **AC-US3-04**: Six tabs are rendered below the header: Editor, Tests, Run, Activation, History, Deps -- matching the current LeftRail panel groups (Build, Evaluate, Insights)
- [x] **AC-US3-05**: Each tab renders the corresponding existing panel component (`EditorPanel`, `TestsPanel`, `RunPanel`, `ActivationPanel`, `HistoryPanel`, `DepsPanel`) wrapped in the existing `WorkspaceProvider` context

---

## Implementation

**Increment**: [0470-skill-studio-full-redesign](../../../../../increments/0470-skill-studio-full-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-012**: Create `TabBar.tsx` horizontal tab bar replacing LeftRail
- [x] **T-013**: Create `DetailHeader.tsx` extracting logic from `WorkspaceHeader`
- [x] **T-014**: Modify `WorkspaceContext.tsx` to remove `useSearchParams` dependency
- [x] **T-015**: Modify `SkillWorkspace.tsx` to accept props instead of `useParams`

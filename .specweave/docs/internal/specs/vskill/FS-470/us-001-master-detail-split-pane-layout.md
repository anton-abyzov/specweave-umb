---
id: US-001
feature: FS-470
title: "Master-Detail Split-Pane Layout"
status: completed
priority: P1
created: 2026-03-10T00:00:00.000Z
tldr: "**As a** skill author using the local Skill Studio."
project: vskill
external:
  github:
    issue: 59
    url: https://github.com/anton-abyzov/vskill/issues/59
---

# US-001: Master-Detail Split-Pane Layout

**Feature**: [FS-470](./FEATURE.md)

**As a** skill author using the local Skill Studio
**I want** a side-by-side layout with a skill list on the left and skill details on the right
**So that** I can browse and switch between skills without losing context or triggering full-page navigations

---

## Acceptance Criteria

- [x] **AC-US1-01**: The root route renders a split-pane layout with a left panel (280px fixed width) and a right panel (flex: 1), replacing the current sidebar nav + SkillListPage + separate SkillWorkspace page routes
- [x] **AC-US1-02**: Both panels scroll independently with `overflow-y: auto` and fill the full viewport height
- [x] **AC-US1-03**: A 1px vertical border separates the two panels using `var(--border-subtle)` color
- [x] **AC-US1-04**: The layout uses the existing design system (Tailwind v4 + CSS variables: `--surface-0..4`, `--text-*`, `--accent`, etc.)
- [x] **AC-US1-05**: The left panel header displays the "Skill Studio" brand with project name (from `/api/config`) and a model selector (existing `ModelSelector` component)

---

## Implementation

**Increment**: [0470-skill-studio-full-redesign](../../../../../increments/0470-skill-studio-full-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-004**: Create `StudioLayout.tsx` CSS Grid shell
- [x] **T-005**: Create `LeftPanel.tsx` container
- [x] **T-006**: Create `RightPanel.tsx` container
- [x] **T-007**: Rewrite `App.tsx` as `StudioProvider` + `StudioLayout` shell

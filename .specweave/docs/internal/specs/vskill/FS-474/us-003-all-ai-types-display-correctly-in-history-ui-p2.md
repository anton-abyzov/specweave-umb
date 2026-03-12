---
id: US-003
feature: FS-474
title: "All AI Types Display Correctly in History UI (P2)"
status: completed
priority: P1
created: 2026-03-10T00:00:00.000Z
tldr: "**As a** skill author using Skill Studio."
project: vskill
---

# US-003: All AI Types Display Correctly in History UI (P2)

**Feature**: [FS-474](./FEATURE.md)

**As a** skill author using Skill Studio
**I want** all AI command types to have proper type badges and filter options in the History tab
**So that** I can distinguish and filter between different types of AI operations

---

## Acceptance Criteria

- [x] **AC-US3-01**: `HistoryPanel.tsx` filter type union includes `"instruct"` so instruct entries can be filtered in the workspace panel
- [x] **AC-US3-02**: `HistoryPage.tsx` `TYPE_PILL` map includes entries for `"instruct"`, `"ai-generate"`, and `"eval-generate"` with distinct colors and labels
- [x] **AC-US3-03**: `HistoryPage.tsx` `FilterBar` type dropdown includes options for "AI Edit", "AI Generate", and "Eval Generate"
- [x] **AC-US3-04**: Backend `HistorySummary` and `HistoryFilter` type unions include the new `"ai-generate"` and `"eval-generate"` types
- [x] **AC-US3-05**: Frontend `types.ts` type unions are updated to match backend types

---

## Implementation

**Increment**: [0474-ai-command-history](../../../../../increments/0474-ai-command-history/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_

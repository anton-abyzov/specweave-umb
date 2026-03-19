---
id: US-006
feature: FS-622
title: Cost Formatting (P1)
status: completed
priority: P1
created: 2026-03-19T00:00:00.000Z
tldr: "**As a** skill developer."
project: vskill
external_tools:
  jira:
    key: SWE2E-719
  ado:
    id: 1558
---

# US-006: Cost Formatting (P1)

**Feature**: [FS-622](./FEATURE.md)

**As a** skill developer
**I want** cost values displayed consistently across all panels
**So that** cost information is easy to read and compare

---

## Acceptance Criteria

- [x] **AC-US6-01**: `formatCost()` utility formats costs as "$0.0042" for small values, "$1.23" for larger
- [x] **AC-US6-02**: Shows "N/A" when cost is null (no token data available)
- [x] **AC-US6-03**: Shows "Free" badge for free providers (Ollama, Gemini free tier)
- [x] **AC-US6-04**: Shows "Subscription" badge for CLI subscription providers (Claude Max, Codex/ChatGPT)
- [x] **AC-US6-05**: Input vs output token breakdown displayed where data is available

---

## Implementation

**Increment**: [0622-dashboard-cost-realtime-redesign](../../../../../increments/0622-dashboard-cost-realtime-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_

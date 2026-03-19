---
id: US-001
feature: FS-622
title: Pricing Engine (P1)
status: completed
priority: P1
created: 2026-03-19T00:00:00.000Z
tldr: "**As a** skill developer."
project: vskill
external_tools:
  jira:
    key: SWE2E-714
  ado:
    id: 1553
---

# US-001: Pricing Engine (P1)

**Feature**: [FS-622](./FEATURE.md)

**As a** skill developer
**I want** the system to calculate costs for all LLM providers
**So that** I can see evaluation costs regardless of which provider I use

---

## Acceptance Criteria

- [x] **AC-US1-01**: Centralized pricing table exists in `src/eval/pricing.ts` with per-model input/output token costs for Anthropic, OpenAI, and Google
- [x] **AC-US1-02**: `calculateCost(provider, model, inputTokens, outputTokens)` returns dollar cost from token counts; returns null only when tokens unavailable
- [x] **AC-US1-03**: `getBillingMode(provider)` returns "per-token", "subscription", or "free" for UI badge display
- [x] **AC-US1-04**: Fuzzy model name matching resolves aliases (e.g., "sonnet" → "claude-sonnet-4-6", "opus" → "claude-opus-4-6")
- [x] **AC-US1-05**: Pricing table includes `updatedAt` date per entry for staleness detection
- [x] **AC-US1-06**: `estimateCost(provider, model, estInputTokens, estOutputTokens)` provides pre-run cost estimates

---

## Implementation

**Increment**: [0622-dashboard-cost-realtime-redesign](../../../../../increments/0622-dashboard-cost-realtime-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_

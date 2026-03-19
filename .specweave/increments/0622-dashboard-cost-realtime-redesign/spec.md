---
increment: 0622-dashboard-cost-realtime-redesign
title: "Dashboard Cost Display & Real-Time Updates Redesign"
type: feature
priority: P1
status: planned
created: 2026-03-19
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Dashboard Cost Display & Real-Time Updates Redesign

## Overview

The vskill Studio dashboard cost display is nearly useless — only OpenRouter returns actual cost data. Claude (CLI + API), Codex, Gemini, and Ollama all show "N/A". The StatsPanel shows zero cost information. Panels don't auto-refresh after benchmark runs complete.

This increment adds a centralized pricing engine for all providers, cost metrics across all dashboard panels, SSE-based real-time panel updates, and client-side SWR caching.

## User Stories

### US-001: Pricing Engine (P1)
**Project**: vskill

**As a** skill developer
**I want** the system to calculate costs for all LLM providers
**So that** I can see evaluation costs regardless of which provider I use

**Acceptance Criteria**:
- [x] **AC-US1-01**: Centralized pricing table exists in `src/eval/pricing.ts` with per-model input/output token costs for Anthropic, OpenAI, and Google
- [x] **AC-US1-02**: `calculateCost(provider, model, inputTokens, outputTokens)` returns dollar cost from token counts; returns null only when tokens unavailable
- [x] **AC-US1-03**: `getBillingMode(provider)` returns "per-token", "subscription", or "free" for UI badge display
- [x] **AC-US1-04**: Fuzzy model name matching resolves aliases (e.g., "sonnet" → "claude-sonnet-4-6", "opus" → "claude-opus-4-6")
- [x] **AC-US1-05**: Pricing table includes `updatedAt` date per entry for staleness detection
- [x] **AC-US1-06**: `estimateCost(provider, model, estInputTokens, estOutputTokens)` provides pre-run cost estimates

---

### US-002: Cost in LLM Responses (P1)
**Project**: vskill

**As a** skill developer
**I want** each LLM call to include cost data
**So that** costs propagate through benchmark and sweep results automatically

**Acceptance Criteria**:
- [x] **AC-US2-01**: Anthropic API client calculates cost from `input_tokens`/`output_tokens` using pricing engine
- [x] **AC-US2-02**: OpenRouter client preserves existing `total_cost` with fallback to pricing engine calculation
- [x] **AC-US2-03**: Ollama client returns `cost: 0` and `billingMode: "free"`
- [x] **AC-US2-04**: Claude CLI client returns `billingMode: "subscription"` (Max plan)
- [x] **AC-US2-05**: Codex CLI client returns `billingMode: "subscription"`
- [x] **AC-US2-06**: Gemini CLI client returns `billingMode: "free"` (free tier)
- [x] **AC-US2-07**: `GenerateResult` interface extended with `billingMode` field
- [x] **AC-US2-08**: `assembleBulkResult()` sums per-case costs into `totalCost` field
- [x] **AC-US2-09**: Sweep runner `aggregateRuns()` propagates real cost data

---

### US-003: Cost in StatsPanel (P1)
**Project**: vskill

**As a** skill developer
**I want** cost metrics in the statistics panel
**So that** I can understand my evaluation spending over time

**Acceptance Criteria**:
- [x] **AC-US3-01**: "Total Cost" summary card shows aggregate cost across all runs
- [x] **AC-US3-02**: "Avg Cost/Run" summary card shows average cost per benchmark run
- [x] **AC-US3-03**: Model performance table includes "Avg Cost" column
- [x] **AC-US3-04**: Cost trend line shows cost per data point over time
- [x] **AC-US3-05**: StatsResult type extended with `totalCost`, `costPerRun`, and per-model cost fields
- [x] **AC-US3-06**: Stats API endpoint returns cost data from history entries

---

### US-004: Cost in RunPanel & BenchmarkPage (P2)
**Project**: vskill

**As a** skill developer
**I want** cost estimates before runs and actual costs after completion
**So that** I can make informed decisions about running benchmarks

**Acceptance Criteria**:
- [x] **AC-US4-01**: Pre-run cost estimate displayed based on case count and model pricing
- [x] **AC-US4-02**: Per-case cost shown in RunPanel result cards after completion
- [x] **AC-US4-03**: Total cost shown in overall results summary
- [x] **AC-US4-04**: BenchmarkPage shows per-case cost next to duration and tokens
- [x] **AC-US4-05**: BenchmarkPage shows total cost in final results card

---

### US-005: Cost in HistoryPanel (P2)
**Project**: vskill

**As a** skill developer
**I want** cost per run in my benchmark history
**So that** I can track spending across runs

**Acceptance Criteria**:
- [x] **AC-US5-01**: Timeline entries show cost alongside model and pass rate
- [x] **AC-US5-02**: Detail view shows cost breakdown
- [x] **AC-US5-03**: HistorySummary type extended with cost field
- [x] **AC-US5-04**: Comparison view shows cost difference between runs

---

### US-006: Cost Formatting (P1)
**Project**: vskill

**As a** skill developer
**I want** cost values displayed consistently across all panels
**So that** cost information is easy to read and compare

**Acceptance Criteria**:
- [x] **AC-US6-01**: `formatCost()` utility formats costs as "$0.0042" for small values, "$1.23" for larger
- [x] **AC-US6-02**: Shows "N/A" when cost is null (no token data available)
- [x] **AC-US6-03**: Shows "Free" badge for free providers (Ollama, Gemini free tier)
- [x] **AC-US6-04**: Shows "Subscription" badge for CLI subscription providers (Claude Max, Codex/ChatGPT)
- [x] **AC-US6-05**: Input vs output token breakdown displayed where data is available

---

### US-007: Real-Time Panel Updates (P2)
**Project**: vskill

**As a** skill developer
**I want** dashboard panels to auto-refresh when new data is available
**So that** I don't need to manually reload after running benchmarks

**Acceptance Criteria**:
- [x] **AC-US7-01**: Server-side EventEmitter fires on data changes (benchmark complete, history written, leaderboard updated)
- [x] **AC-US7-02**: SSE endpoint `GET /api/events` streams data change notifications to the client
- [x] **AC-US7-03**: StatsPanel auto-refreshes when benchmark completes
- [x] **AC-US7-04**: HistoryPanel auto-refreshes when new history entry is written
- [x] **AC-US7-05**: LeaderboardPanel auto-refreshes when sweep completes
- [x] **AC-US7-06**: Existing benchmark SSE flow is NOT broken

---

### US-008: Client-Side Caching (P3)
**Project**: vskill

**As a** skill developer
**I want** fast panel switches without unnecessary API calls
**So that** the dashboard feels responsive and doesn't waste resources

**Acceptance Criteria**:
- [x] **AC-US8-01**: SWR cache with 30-second TTL for API responses
- [x] **AC-US8-02**: Duplicate in-flight requests are deduplicated (same key returns same promise)
- [x] **AC-US8-03**: Cache is invalidated by SSE data events from US-007
- [x] **AC-US8-04**: StatsPanel, HistoryPanel, LeaderboardPanel use SWR instead of raw useEffect+fetch

## Functional Requirements

### FR-001: Pricing Table Accuracy
Pricing data reflects current provider rates. Each entry includes `updatedAt` date. Stale entries (>90 days) flaggable in UI.

### FR-002: Non-Breaking Changes
All changes backwards-compatible. Existing LeaderboardPanel cost display (works for OpenRouter) continues to work. CLI providers degrade gracefully to "N/A" when token data unavailable.

### FR-003: Performance
Zero new external API calls — pricing is a local hardcoded table. Single persistent SSE connection for data events (not polling). SWR cache prevents redundant fetches.

## Success Criteria

- Cost shows for Anthropic API benchmarks (previously "N/A")
- StatsPanel displays at least 4 cost-related metrics
- Panels auto-refresh within 2 seconds of benchmark completion
- No regression in existing benchmark/sweep functionality

## Out of Scope

- Real-time cost monitoring for non-vskill usage (general CLI usage tracking)
- Parsing Gemini CLI protobuf conversation logs
- OpenRouter rate limit header parsing
- Cost budgeting/alerting features
- Automatic pricing table updates from provider APIs

## Dependencies

- Existing SSE infrastructure in `src/eval-ui/src/sse.ts` and `src/eval-server/sse-helpers.ts`
- Existing benchmark runner and sweep runner
- Existing StatsPanel, HistoryPanel, RunPanel, LeaderboardPanel components

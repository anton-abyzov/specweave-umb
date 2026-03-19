# Implementation Plan: Dashboard Cost Display & Real-Time Updates Redesign

## Overview

Cross-cutting server+client feature spanning 3 implementation phases: pricing engine foundation (server), cost display integration (UI), and real-time/caching layer. TDD enforced throughout.

## Architecture

### Components

- **Pricing Engine** (`src/eval/pricing.ts`): Centralized pricing table + cost calculator. Pure functions, no side effects. Handles model alias resolution.
- **LLM Client Enhancement** (`src/eval/llm.ts`): Each provider's `generate()` computes cost via pricing engine. Adds `billingMode` to `GenerateResult`.
- **Cost Propagation** (`benchmark-runner.ts`, `sweep-runner.ts`): Sum per-case costs into bulk results. Extend `BenchmarkResult` with `totalCost`.
- **Stats API Extension** (`api-routes.ts`): Stats endpoint computes cost aggregates from history entries.
- **Cost Formatting** (`src/eval-ui/src/utils/formatCost.ts`): Consistent cost display: "$0.0042", "N/A", "Free", "Subscription".
- **Data Events** (`src/eval-server/data-events.ts`): Singleton EventEmitter + SSE endpoint for push notifications.
- **SWR Cache** (`src/eval-ui/src/hooks/useSWR.ts`): Minimal stale-while-revalidate with request deduplication.

### Data Model

**ModelPricing** (new type in pricing.ts):
```
{ inputPerMillion: number, outputPerMillion: number, updatedAt: string }
```

**GenerateResult** (extended in llm.ts):
```
+ billingMode: "per-token" | "subscription" | "free"
```

**BenchmarkResult** (extended):
```
+ totalCost?: number | null
```

**StatsResult** (extended in types.ts):
```
+ totalCost: number
+ costPerRun: number
+ modelStats[].avgCost: number
+ trendPoints[].cost: number
```

**HistorySummary** (extended in types.ts):
```
+ totalCost?: number | null
```

### API Contracts

- `GET /api/skills/:plugin/:skill/stats` — extended response with cost fields
- `GET /api/events` — NEW: SSE stream for data change notifications
  - Events: `benchmark:complete`, `history:written`, `leaderboard:updated`
  - Payload: `{ event: string, timestamp: string, plugin?: string, skill?: string }`

## Technology Stack

- **Language**: TypeScript (server + client)
- **Server**: Express (existing eval-server)
- **Client**: React + Vite (existing eval-ui)
- **Real-time**: SSE via Node.js `http.ServerResponse` (existing pattern)
- **No new dependencies** — everything built with Node.js stdlib + React

## Architecture Decisions

### ADR: Local pricing table vs API-fetched pricing
**Decision**: Hardcoded local pricing table with `updatedAt` dates.
**Rationale**: Zero external API calls, instant lookups, no rate limit risk. Pricing changes infrequently (quarterly). Manual updates are acceptable for a dev tool.
**Alternative rejected**: Fetching from provider APIs — adds latency, requires API keys, risk of rate limiting (the exact problem we just fixed with GitHub API).

### ADR: SSE vs WebSocket for data events
**Decision**: SSE (Server-Sent Events) via existing infrastructure.
**Rationale**: Server already uses SSE for benchmarks. SSE is simpler (HTTP, auto-reconnect, one-directional). WebSocket is overkill for push-only notifications in a single-user local tool.

### ADR: Custom SWR vs library (swr, react-query)
**Decision**: Custom minimal implementation (~60 lines).
**Rationale**: Only need cache + dedup + invalidation. Adding a dependency for 3 features is overkill. Keeps bundle small. No risk of version conflicts.

### ADR: Subscription billing mode badge
**Decision**: Show "Subscription" badge for Claude CLI (Max plan) and Codex CLI instead of per-call cost.
**Rationale**: CLI calls are included in subscription — per-call cost is $0 from user's perspective. But we also show "API-equivalent" cost when token data is available, so users understand the value.

## Implementation Phases

### Phase 1: Foundation (Upstream — must complete first)
- T-001: Pricing engine with tests (pricing.ts, pricing.test.ts)
- T-002: Cost formatting utility with tests (formatCost.ts)
- T-003: Extend GenerateResult with billingMode
- T-004: Integrate pricing engine into LLM clients

### Phase 2: Server-Side Propagation
- T-005: Extend BenchmarkResult type with totalCost
- T-006: Cost propagation in benchmark-runner (assembleBulkResult)
- T-007: Cost propagation in sweep-runner (aggregateRuns)
- T-008: Extend stats API with cost data
- T-009: Extend HistorySummary with cost

### Phase 3: UI Integration (depends on Phase 1+2)
- T-010: Extend frontend types (types.ts)
- T-011: Cost metrics in StatsPanel
- T-012: Cost in RunPanel (estimate + actual)
- T-013: Cost in BenchmarkPage
- T-014: Cost in HistoryPanel
- T-015: SSE data events server (data-events.ts + endpoint)
- T-016: useDataEvents hook + panel integration
- T-017: useSWR hook + panel integration

## Testing Strategy

- **Unit tests**: pricing.ts (cost calculation, fuzzy matching, billing modes), formatCost.ts (all formatting cases)
- **Integration tests**: LLM client cost propagation, benchmark-runner totalCost, stats API response
- **E2E tests**: Run benchmark → verify cost shows in StatsPanel, HistoryPanel, RunPanel

## Technical Challenges

### Challenge 1: CLI providers return no token data
**Solution**: Return `billingMode: "subscription"` or `"free"`, display badge instead of dollar amount. Keep `cost: null` and `inputTokens: null`.
**Risk**: Low — graceful degradation to "N/A" is already the current behavior.

### Challenge 2: Model name aliasing across providers
**Solution**: Fuzzy matching in `getProviderPricing()` — normalize aliases using existing maps in llm.ts (`CLAUDE_CLI_NORMALIZE`, `ANTHROPIC_NORMALIZE`), then match against pricing table keys. Unknown models return null cost.
**Risk**: Low — worst case is "N/A" for unrecognized models.

### Challenge 3: SSE connection lifecycle
**Solution**: Single connection per browser tab, auto-reconnect on drop. Use `EventSource` API for simplicity. Panels subscribe via callback refs (no state accumulation like existing useSSE — data events are triggers, not data).
**Risk**: Low — SSE auto-reconnects natively. Panels fall back to manual refresh if connection fails.

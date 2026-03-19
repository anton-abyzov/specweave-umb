# Tasks: Dashboard Cost Display & Real-Time Updates Redesign

## Phase 1: Foundation (Upstream)

### T-001: Create pricing engine
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-04, AC-US1-05, AC-US1-06 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-02, AC-US1-04, AC-US1-05, AC-US1-06

Create `src/eval/pricing.ts` with:
- `PRICING` table: Anthropic (opus/sonnet/haiku), OpenAI (o4-mini/gpt-4.1), Google (gemini-2.5-pro/flash) with inputPerMillion, outputPerMillion, updatedAt
- `calculateCost(provider, model, inputTokens, outputTokens): number | null`
- `estimateCost(provider, model, estInputTokens, estOutputTokens): number | null`
- `getProviderPricing(provider, model): ModelPricing | null` with fuzzy alias matching
- Model alias maps reusing patterns from llm.ts

**Test Plan**:
- Given Anthropic provider and claude-sonnet-4-6 model with 1000 input and 500 output tokens, When calculateCost is called, Then returns correct dollar amount ($0.0000105)
- Given alias "sonnet" for Anthropic, When getProviderPricing is called, Then resolves to claude-sonnet-4-6 pricing
- Given unknown model name, When calculateCost is called, Then returns null
- Given null inputTokens, When calculateCost is called, Then returns null
- Given Ollama provider, When calculateCost is called with any tokens, Then returns 0
- Given provider "anthropic", When estimateCost is called, Then returns estimate based on pricing table

---

### T-002: Create cost formatting utility
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04 | **Status**: [x] completed
**AC**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04

Create `src/eval-ui/src/utils/formatCost.ts` with:
- `formatCost(cost: number | null, billingMode?: string): string`
- `formatTokens(input: number | null, output: number | null): string`

**Test Plan**:
- Given cost=0.0042, When formatCost is called, Then returns "$0.0042"
- Given cost=1.23456, When formatCost is called, Then returns "$1.23"
- Given cost=null, When formatCost is called, Then returns "N/A"
- Given cost=0 and billingMode="free", When formatCost is called, Then returns "Free"
- Given cost=null and billingMode="subscription", When formatCost is called, Then returns "Subscription"
- Given input=1000 and output=500, When formatTokens is called, Then returns "1,000 in / 500 out"
- Given input=null, When formatTokens is called, Then returns "N/A"

---

### T-003: Add billingMode to GenerateResult
**User Story**: US-002 | **Satisfies ACs**: AC-US2-07 | **Status**: [x] completed
**AC**: AC-US2-07

Extend `GenerateResult` interface in `src/eval/llm.ts`:
- Add `billingMode: "per-token" | "subscription" | "free"` field
- Export `BillingMode` type

**Test Plan**:
- Given GenerateResult interface, When billingMode field is checked, Then it exists with correct union type

---

### T-004: Integrate pricing engine into LLM clients
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06 | **Status**: [x] completed
**AC**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06
**Depends on**: T-001, T-003

Update each provider in `src/eval/llm.ts`:
- `createAnthropicClient`: call `calculateCost("anthropic", model, inputTokens, outputTokens)`, set `billingMode: "per-token"`
- `createOpenRouterClient`: keep existing `total_cost`, fallback to `calculateCost()`, set `billingMode: "per-token"`
- `createOllamaClient`: set `cost: 0`, `billingMode: "free"`
- `createClaudeCliClient`: set `billingMode: "subscription"`
- `createCodexCliClient`: set `billingMode: "subscription"`
- `createGeminiCliClient`: set `billingMode: "free"`

**Test Plan**:
- Given Anthropic client with mocked response (input_tokens=1000, output_tokens=500), When generate is called, Then result.cost equals calculated amount and billingMode is "per-token"
- Given OpenRouter client with total_cost in response, When generate is called, Then result.cost uses total_cost value
- Given OpenRouter client with no total_cost, When generate is called, Then result.cost falls back to pricing calculation
- Given Ollama client, When generate is called, Then result.cost is 0 and billingMode is "free"
- Given Claude CLI client, When generate is called, Then result.billingMode is "subscription"

---

### T-005: Add getBillingMode function
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**AC**: AC-US1-03

Add `getBillingMode(provider: string): BillingMode` to `src/eval/pricing.ts`.

**Test Plan**:
- Given provider "anthropic", When getBillingMode is called, Then returns "per-token"
- Given provider "claude-cli", When getBillingMode is called, Then returns "subscription"
- Given provider "ollama", When getBillingMode is called, Then returns "free"
- Given provider "gemini-cli", When getBillingMode is called, Then returns "free"

---

## Phase 2: Server-Side Propagation

### T-006: Extend BenchmarkResult with totalCost
**User Story**: US-002 | **Satisfies ACs**: AC-US2-08 | **Status**: [x] completed
**AC**: AC-US2-08
**Depends on**: T-004

Update `src/eval/benchmark.ts` type and `src/eval-server/benchmark-runner.ts`:
- Add `totalCost?: number | null` to `BenchmarkResult`
- In `assembleBulkResult()`: sum `c.cost` from individual cases into `totalCost`

**Test Plan**:
- Given 3 cases with costs [0.01, 0.02, 0.03], When assembleBulkResult is called, Then totalCost equals 0.06
- Given cases with null costs, When assembleBulkResult is called, Then totalCost is null

---

### T-007: Cost propagation in sweep runner
**User Story**: US-002 | **Satisfies ACs**: AC-US2-09 | **Status**: [x] completed
**AC**: AC-US2-09
**Depends on**: T-006

Update `src/eval-server/sweep-runner.ts`:
- `aggregateRuns()` already reads `(c as any).cost` — verify it works with real cost data from T-004
- Ensure `ModelResult.cost` has accurate totals

**Test Plan**:
- Given sweep with 2 runs each containing cases with cost data, When aggregateRuns is called, Then cost.total and cost.perCase are calculated correctly
- Given sweep with null costs, When aggregateRuns is called, Then cost totals are 0

---

### T-008: Extend stats API with cost data
**User Story**: US-003 | **Satisfies ACs**: AC-US3-05, AC-US3-06 | **Status**: [x] completed
**AC**: AC-US3-05, AC-US3-06
**Depends on**: T-006

Update stats computation in `src/eval-server/api-routes.ts`:
- Read `totalCost` from history entries
- Compute `totalCost`, `costPerRun` aggregates
- Add `avgCost` to each `modelStats` entry
- Add `cost` to each `trendPoints` entry

**Test Plan**:
- Given history entries with totalCost values, When stats API is called, Then response includes totalCost and costPerRun
- Given history entries without cost data, When stats API is called, Then cost fields default to 0

---

### T-009: Extend HistorySummary with cost
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [x] completed
**AC**: AC-US5-03
**Depends on**: T-006

Update history listing in `src/eval-server/api-routes.ts` to include `totalCost` in `HistorySummary`.

**Test Plan**:
- Given history entry with totalCost=0.05, When history API is called, Then summary includes totalCost field

---

## Phase 3: UI Integration

### T-010: Extend frontend types
**User Story**: US-003, US-005 | **Satisfies ACs**: AC-US3-05, AC-US5-03 | **Status**: [x] completed
**AC**: AC-US3-05, AC-US5-03
**Depends on**: T-008, T-009

Update `src/eval-ui/src/types.ts`:
- Add cost fields to `StatsResult`, `HistorySummary`, `BenchmarkResult`, `BenchmarkCase`
- Add `billingMode` to types that need it

**Test Plan**:
- Given updated types, When TypeScript compiles, Then no type errors

---

### T-011: Cost metrics in StatsPanel
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04 | **Status**: [x] completed
**AC**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Depends on**: T-002, T-010

Update `src/eval-ui/src/components/StatsPanel.tsx`:
- Add "Total Cost" and "Avg Cost/Run" summary cards to the 4-card grid (make it 6 cards or 2 rows)
- Add "Avg Cost" column to model performance table
- Pass cost data to TrendLine if available

**Test Plan**:
- Given stats with totalCost=1.50, When StatsPanel renders, Then "Total Cost" card shows "$1.50"
- Given stats with costPerRun=0.05, When StatsPanel renders, Then "Avg Cost/Run" card shows "$0.05"
- Given model stats with avgCost, When table renders, Then cost column displays formatted values

---

### T-012: Cost in RunPanel
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [x] completed
**AC**: AC-US4-01, AC-US4-02, AC-US4-03
**Depends on**: T-002, T-010

Update `src/eval-ui/src/pages/workspace/RunPanel.tsx`:
- Pre-run: show estimated cost based on case count × model pricing
- Per-case: show cost in result cards
- Post-run: show total cost in summary

**Test Plan**:
- Given 5 cases with anthropic/sonnet model, When run panel displays estimate, Then shows approximate cost range
- Given completed benchmark with totalCost, When summary renders, Then total cost is displayed

---

### T-013: Cost in BenchmarkPage
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04, AC-US4-05 | **Status**: [x] completed
**AC**: AC-US4-04, AC-US4-05
**Depends on**: T-002, T-010

Update `src/eval-ui/src/pages/BenchmarkPage.tsx`:
- Show per-case cost next to duration and tokens
- Show total cost in final results card

**Test Plan**:
- Given case with cost=0.003, When case card renders, Then cost shows "$0.003"
- Given completed benchmark, When final results card renders, Then total cost is displayed

---

### T-014: Cost in HistoryPanel
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-04 | **Status**: [x] completed
**AC**: AC-US5-01, AC-US5-02, AC-US5-04
**Depends on**: T-002, T-010

Update `src/eval-ui/src/pages/workspace/HistoryPanel.tsx`:
- Timeline entries: show cost next to model and pass rate
- Detail view: show cost breakdown
- Compare view: show cost difference

**Test Plan**:
- Given history entry with totalCost=0.10, When timeline renders, Then cost shows "$0.10"
- Given two runs in comparison, When compare view renders, Then cost delta is shown

---

### T-015: SSE data events server
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-06 | **Status**: [x] completed
**AC**: AC-US7-01, AC-US7-02, AC-US7-06

Create `src/eval-server/data-events.ts`:
- Singleton `DataEventBus` using Node.js `EventEmitter`
- `emitDataEvent(event, payload)` function
- Wire into `writeHistoryEntry()`, `writeLeaderboard()`, `sendSSEDone()` in existing files

Add `GET /api/events` SSE endpoint in `src/eval-server/api-routes.ts`:
- Long-lived SSE connection
- Forwards DataEventBus events to connected clients
- Cleanup on client disconnect

**Test Plan**:
- Given DataEventBus, When emitDataEvent("benchmark:complete") is called, Then connected SSE clients receive the event
- Given existing benchmark run, When sendSSEDone completes, Then "benchmark:complete" event is emitted
- Given SSE client disconnects, When new events fire, Then no errors thrown

---

### T-016: useDataEvents hook + panel integration
**User Story**: US-007 | **Satisfies ACs**: AC-US7-03, AC-US7-04, AC-US7-05 | **Status**: [x] completed
**AC**: AC-US7-03, AC-US7-04, AC-US7-05
**Depends on**: T-015

Create `src/eval-ui/src/hooks/useDataEvents.ts`:
- `useDataEvents()` — connects to `GET /api/events` via `EventSource`
- `useOnDataEvent(event, callback)` — subscribes to specific events

Integrate in panels:
- StatsPanel: re-fetch on `benchmark:complete`
- HistoryPanel: re-fetch on `history:written`
- LeaderboardPanel: re-fetch on `leaderboard:updated`

**Test Plan**:
- Given benchmark completes and emits event, When StatsPanel is mounted, Then it re-fetches stats data
- Given SSE connection drops, When EventSource reconnects, Then panels resume receiving events

---

### T-017: useSWR hook + panel integration
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-02, AC-US8-03, AC-US8-04 | **Status**: [x] completed
**AC**: AC-US8-01, AC-US8-02, AC-US8-03, AC-US8-04
**Depends on**: T-016

Create `src/eval-ui/src/hooks/useSWR.ts`:
- `useSWR<T>(key, fetcher, opts?)` — cache + stale-while-revalidate + dedup
- 30s default TTL
- `mutate(key)` function for cache invalidation from data events

Replace in panels: StatsPanel, HistoryPanel, LeaderboardPanel switch from `useEffect+fetch` to `useSWR`.

**Test Plan**:
- Given useSWR with 30s TTL, When same key fetched within 30s, Then returns cached data without re-fetch
- Given two concurrent fetches for same key, When both start, Then only one network request is made
- Given data event triggers mutate(key), When panel next renders, Then fresh data is fetched

---

### T-018: Token breakdown display
**User Story**: US-006 | **Satisfies ACs**: AC-US6-05 | **Status**: [x] completed
**AC**: AC-US6-05
**Depends on**: T-002, T-010

Add input/output token breakdown display in BenchmarkPage and RunPanel where data is available:
- Show "1,234 in / 567 out" format using `formatTokens()`
- Only display when both inputTokens and outputTokens are non-null

**Test Plan**:
- Given case with inputTokens=1234 and outputTokens=567, When result renders, Then shows "1,234 in / 567 out"
- Given case with null tokens, When result renders, Then token breakdown is hidden

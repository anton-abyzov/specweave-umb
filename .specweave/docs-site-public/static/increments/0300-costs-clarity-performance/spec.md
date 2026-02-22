# 0300 - Costs Page Clarity & Performance Optimization

## Summary

Improve the SpecWeave dashboard Costs page and Overview page to clearly communicate that cost data comes from Claude Code session logs only, and dramatically improve backend performance by replacing the naive full-file-scan approach in CostAggregator with an incremental, cached architecture targeting sub-100ms response times. Additionally, virtualize the sessions table for smooth rendering of large datasets.

---

## User Stories

### US-001: Provider Source Clarity on Costs Page
**Project**: specweave

**As a** dashboard user
**I want** to see a clear header on the Costs page that states data comes from Claude Code
**So that** I understand the scope and source of the cost data I'm viewing

**Acceptance Criteria**:
- [x] **AC-US1-01**: Costs page displays a provider source header reading "Claude Code" with an appropriate icon/badge, replacing the current vague subscription banner
- [x] **AC-US1-02**: The header is always visible (not conditional on subscription plan), and subscription-specific details (plan amount, API-equivalent note) are shown as secondary info beneath it
- [x] **AC-US1-03**: A subtle "More providers coming soon" note appears at the bottom of the Costs page

### US-002: Provider Source Clarity on Overview Page
**Project**: specweave

**As a** dashboard user viewing the Overview page
**I want** the cost KPI card to indicate the data source is "Claude Code"
**So that** I don't confuse it with other potential billing sources

**Acceptance Criteria**:
- [x] **AC-US2-01**: The cost KPI card on the Overview page shows "Claude Code" as a source label (e.g., as a subtitle or tooltip)

### US-003: CostAggregator Performance - In-Memory Cache with Mtime Invalidation
**Project**: specweave

**As a** dashboard server
**I want** CostAggregator to cache parsed session data per-file, invalidating only when file mtime changes
**So that** repeated requests don't re-parse unchanged JSONL files

**Acceptance Criteria**:
- [x] **AC-US3-01**: CostAggregator maintains an in-memory Map of `filePath -> { mtime, parsedSummary }` that persists across requests
- [x] **AC-US3-02**: On each request, only files with changed mtime (or new files) are re-parsed; unchanged files use cached summaries
- [x] **AC-US3-03**: The response-level cache (currently 60s TTL) is replaced by this smarter per-file cache, so data is always fresh but parsing is minimal
- [x] **AC-US3-04**: Deleted files are evicted from the cache (stale entry cleanup)

### US-004: CostAggregator Performance - Incremental Session Parsing
**Project**: specweave

**As a** dashboard server
**I want** to only parse new or changed JSONL session files instead of all files on every request
**So that** response times scale with change frequency, not total file count

**Acceptance Criteria**:
- [x] **AC-US4-01**: `getTokenSummaries()` compares the current file list + mtimes against cached state and only parses the delta
- [x] **AC-US4-02**: Pre-aggregated totals (totalCost, totalTokens, totalSavings, sessionCount, modelBreakdown) are maintained incrementally, not recomputed from scratch
- [x] **AC-US4-03**: API response time for `/api/costs/summary` is under 100ms when no files have changed (warm cache)
- [x] **AC-US4-04**: API response time for `/api/costs/summary` is under 500ms on cold start with 200 session files

### US-005: Sessions Table Virtualization
**Project**: specweave

**As a** dashboard user
**I want** the sessions table on the Costs page to use virtualized rendering
**So that** the UI remains responsive even with hundreds of sessions

**Acceptance Criteria**:
- [x] **AC-US5-01**: The sessions table uses a virtualization approach (windowed rendering) that only renders visible rows plus a small buffer
- [x] **AC-US5-02**: Scroll performance is smooth (no jank) with 200+ sessions
- [x] **AC-US5-03**: Expanding a session row for detail view still works correctly within the virtualized list
- [x] **AC-US5-04**: Existing pagination is preserved or replaced by infinite scroll within the virtualized container

---

## Non-Functional Requirements

- **NFR-01**: No new runtime dependencies on the server side for caching (use native Node.js Map)
- **NFR-02**: Client-side virtualization may use a lightweight library (e.g., `@tanstack/react-virtual`) or be hand-rolled with IntersectionObserver
- **NFR-03**: All changes must be backward-compatible -- existing API contract (`CostsSummaryPayload`) must not break
- **NFR-04**: TDD mode: write tests first for CostAggregator cache logic

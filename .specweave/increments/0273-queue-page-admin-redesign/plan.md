# 0273 - Queue Page Admin Dashboard Redesign — Architecture Plan

## Current State

The `/queue` page (`src/app/queue/page.tsx`) is an 872-line client component with:
- **Data flow**: `GET /api/v1/submissions?limit=200` returns all submissions from KV-backed index; SSE via `useSubmissionStream` for real-time updates; polling fallback at 5s/30s
- **Layout**: Stat cards (4-grid) -> SSE status line -> Batch submit panel (admin) -> Grouped cards: Processing / Published / Rejected
- **Components**: `StatCard`, `SubmissionGroup`, `SubmissionCard`, `PipelineDots`, `ScoreBadge`, `Pulse`, `AdminQueueActions` (separate file)
- **Hooks**: `useSubmissionStream` (SSE), `useAdminStatus` (admin role check)
- **API**: KV-based submission index, NOT Prisma-backed for the main listing

## Architecture Decisions

### AD-01: Keep Single-File Component Structure
The current page is one large file. Rather than over-abstracting into many tiny files prematurely, we will extract only components that have genuine reuse potential or exceed 200 lines:
- `SubmissionTable` — the core table (extracted into `src/app/queue/SubmissionTable.tsx`)
- `QueueStatusBar` — status bar (extracted into `src/app/queue/QueueStatusBar.tsx`)
- `KeyboardShortcutOverlay` — help modal (extracted into `src/app/queue/KeyboardShortcutOverlay.tsx`)
- `StatCard` — stays inline (small)
- `AdminQueueActions` — already separate, unchanged

### AD-02: Server-Side Search via New API Endpoint
The existing `GET /api/v1/submissions` endpoint reads a KV-based submission index. For full-text search across skillName, repoUrl, and id, we add a new endpoint `GET /api/v1/submissions/search` that queries Prisma directly. This is admin-favored (authenticated users get richer search); the existing KV-based listing remains the default for non-search views to avoid hitting the DB on every page load.

### AD-03: URL-Driven State (Filter, Search, Page, Sort)
All UI state (filter, search query, page number, sort column/direction) is stored in URL search params via `useSearchParams()`. This makes pages bookmarkable and shareable.

### AD-04: Client-Side Sorting + Server-Side Pagination
- **Sorting**: Done client-side since each page loads max 100 rows. No API changes needed.
- **Pagination**: The existing `GET /api/v1/submissions` already accepts `limit`. We add `offset` param to support page-based navigation. The endpoint already returns `total`.
- **Filtering**: Done client-side from the loaded page data (filtering by state category).

### AD-05: Queue Status Integration
The queue health endpoint (`GET /api/v1/admin/queue/status`) already exists and returns `paused`, `health`, `stuck`, and `throughput` data. We fetch this on the queue page for admin users only (the endpoint requires REVIEWER role). Non-admin users see only SSE connection status.

## Component Architecture

```
QueuePage (page.tsx)
├── StatCard x5 (Total, Active, Published, Rejected, Avg Score)
│   └── onClick → setFilter(category) → update URL ?filter=
├── QueueStatusBar
│   ├── SSE connection dot (useSubmissionStream.connected)
│   ├── Queue health badge (from /admin/queue/status, admin only)
│   ├── Pause indicator
│   └── Last updated timestamp
├── Search Input (debounced, → /api/v1/submissions/search OR client filter)
├── Batch Submit Panel (admin only, unchanged)
├── SubmissionTable
│   ├── <thead> with sortable column headers
│   ├── <tbody> with submission rows
│   │   ├── Row click → navigate to /submit/{id}
│   │   ├── Repo column → GitHub link (stops propagation)
│   │   ├── State badge (reuse STATE_CONFIG)
│   │   ├── Score badge
│   │   ├── SSE flash animation
│   │   └── Actions column (AdminQueueActions for active + admin)
│   └── Pagination footer (prev/next + page size + range indicator)
└── KeyboardShortcutOverlay (modal, toggled by ?)
```

## API Changes

### New: `GET /api/v1/submissions/search`
```
Query params:
  q: string (required, min 2 chars)
  state: string (optional, filter by SubmissionState)
  limit: number (default 50, max 100)
  offset: number (default 0)

Response: { submissions: SubmissionSummary[], total: number }

Implementation:
  - Prisma query with OR across skillName/repoUrl/id using `contains` (mode: insensitive)
  - Optional state filter as AND condition
  - No auth required (public submissions are visible), but rate-limited
```

### Modified: `GET /api/v1/submissions`
```
Add support for:
  offset: number (default 0) — skip N submissions
  state: string (optional) — filter by state

Existing params preserved:
  limit: number (default 50, max 500)
```

## File Changes

| File | Change |
|------|--------|
| `src/app/queue/page.tsx` | Major rewrite: table layout, URL-driven state, keyboard shortcuts, status bar integration |
| `src/app/queue/SubmissionTable.tsx` | New: extracted table component |
| `src/app/queue/QueueStatusBar.tsx` | New: status bar component |
| `src/app/queue/KeyboardShortcutOverlay.tsx` | New: keyboard shortcut help modal |
| `src/app/queue/AdminQueueActions.tsx` | Minor: adapt to table cell context (remove card borders) |
| `src/app/api/v1/submissions/search/route.ts` | New: Prisma-backed search endpoint |
| `src/app/api/v1/submissions/route.ts` | Modified: add offset and state params |
| `src/app/queue/__tests__/page.test.tsx` | Major update: new tests for table, filters, search, pagination, keyboard |
| `src/app/queue/__tests__/SubmissionTable.test.tsx` | New: table component tests |
| `src/app/queue/__tests__/QueueStatusBar.test.tsx` | New: status bar tests |
| `src/app/queue/__tests__/KeyboardShortcutOverlay.test.tsx` | New: keyboard shortcut overlay tests |
| `src/app/api/v1/submissions/search/__tests__/route.test.ts` | New: search endpoint tests |

## Styling Approach

Continue using inline styles with CSS custom properties (consistent with entire codebase). No CSS modules or styled-components. All color values use existing design tokens (`var(--text)`, `var(--text-faint)`, `var(--text-muted)`, `var(--border)`, `var(--bg-subtle)`, `var(--btn-bg)`, `var(--btn-text)`, `var(--font-geist-mono)`).

## Risk Mitigation

1. **KV index consistency**: The existing submissions endpoint has a known issue with stale KV index for active submissions (it re-hydrates from individual keys). This behavior is preserved unchanged.
2. **Admin auth check**: Queue health data requires admin role. The component gracefully degrades for non-admin users (no status data shown except SSE connection).
3. **Search performance**: Prisma `contains` on unindexed text fields can be slow with many rows. Acceptable for v1 (expected <10k submissions). Consider Postgres full-text search (`@@`) or pg_trgm index later.

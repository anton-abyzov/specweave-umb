# Tasks: Dark-theme token migration followup

Parent: [0657-dark-theme-semantic-tokens](../0657-dark-theme-semantic-tokens/). Closed with known debt — this increment finishes the migration of files that were outside 0657's original inventory.

## Scope boundary

Target files (from 0657 round-3 code-review findings F-002, F-003, F-004, F-005):
- `src/app/admin/queue/page.tsx`
- `src/app/admin/queue/components.tsx`
- `src/app/admin/queue/styles.ts`
- `src/app/queue/QueueStatusBar.tsx`

No other files should be modified. Use tokens already defined in `src/app/globals.css` + `STATUS_VARS` in `src/lib/status-intent.ts`. Do NOT introduce new tokens.

## Phase 1: Migration

### T-001: Migrate admin/queue/page.tsx status hex to tokens
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [ ] pending
**Test Plan**: Given 15 hex literals in `admin/queue/page.tsx` (lines ~446–710 per round-3 review) → When each is replaced with the appropriate `var(--status-*)` token based on semantic intent (tab indicators, StatCards, running-total totals) → Then `grep -E '#[0-9A-Fa-f]{6}' src/app/admin/queue/page.tsx | grep -v 'var(--'` returns zero non-fallback hits AND the page renders identically in manual smoke test.

### T-002: Migrate admin/queue/components.tsx (SseIndicator, HealthBadge, PauseToggle, StuckRow, StatCard, ThroughputChart, ProcessingTimeChart, DLQRow)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [ ] pending
**Test Plan**: Given 40+ hex literals across 8 components in `admin/queue/components.tsx` → When each is replaced with `STATUS_VARS[intent].*` or `var(--status-*-*)` based on the component's semantic role (health = success/warning/danger; SSE connected = success, disconnected = neutral; charts use success for processed, danger for failed, warning for retried) → Then grep for `#[0-9A-Fa-f]{6}` in the file returns zero hits outside `#FFFFFF` foreground and unit tests (if any) still pass.

### T-003: Migrate admin/queue/styles.ts (pausedBanner, errorStyle, button styles)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [ ] pending
**Test Plan**: Given `pausedBanner`, `errorStyle`, and action button styles in `admin/queue/styles.ts` still use hardcoded hex → When they are converted to `STATUS_VARS.warning`, `STATUS_VARS.danger`, and `STATUS_VARS.*.solid` (for destructive buttons with white fg) → Then the paused banner reads "paused" warning-amber in both themes, error states read danger-red in both themes, and destructive buttons pass WCAG AA.

### T-004: Migrate queue/QueueStatusBar.tsx SSE dot + HEALTH_COLORS fallback
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [ ] pending
**Test Plan**: Given SSE dot at line 82 uses hardcoded hex and `HEALTH_COLORS` fallback at lines 97–98 uses hardcoded hex → When SSE dot uses `var(--status-success-text)` when connected / `var(--status-neutral-text)` when not, and `HEALTH_COLORS` fallback uses `{ bg: STATUS_VARS.neutral.bg, color: STATUS_VARS.neutral.text }` → Then grep for hex in the file returns zero hits.

## Phase 2: Verification

### T-005: Global grep + WCAG AA smoke test
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05, AC-US1-06 | **Status**: [ ] pending
**Test Plan**: Given T-001 through T-004 landed → When the global grep `grep -rEn '#[0-9A-Fa-f]{6}' src/app/admin/queue/ src/app/queue/QueueStatusBar.tsx | grep -v 'var(--' | grep -v '__tests__'` is run from vskill-platform root → Then it returns zero hits except intentional `#FFFFFF` foregrounds paired with `--status-*-solid` backgrounds AND a dark-mode rendering of the admin queue page shows destructive Purge/Block buttons with ≥ 4.5:1 contrast (spot-check via browser devtools or a computed-style assertion).

### T-006: Regression run + coverage gate
**User Story**: US-001 | **Satisfies ACs**: all | **Status**: [ ] pending
**Test Plan**: Given all migration tasks landed → When `source ~/.nvm/nvm.sh && nvm use 20 && npx vitest run` is run from `repositories/anton-abyzov/vskill-platform` → Then pass count is ≥ 2806 (0657-closure baseline), zero NEW tsc errors are introduced, and no queue-test regression appears.

# Tasks: Dark Theme Semantic Tokens

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), sonnet (default), opus (complex)

---

## Phase 1: Foundation (US-001) — COMPLETED

### T-001: Add semantic status tokens to globals.css
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] completed

Add 15 `--status-{intent}-{text|bg|border}` tokens to `:root` (light values) and `[data-theme="dark"]` (dark values). Add `--link-accent` and raise `--text-faint` in dark mode.

**Test Plan**:
- **File**: `src/app/__tests__/globals-tokens.test.ts`
- **TC-001**: Given globals.css loaded — When checking `:root` — Then 15 `--status-*` tokens present with correct light hex values
- **TC-002**: Given globals.css loaded — When checking `[data-theme="dark"]` — Then 15 `--status-*` tokens present with correct dark rgba/hex values
- **TC-003**: Given dark mode — When reading `--link-accent` — Then value is `#2DD4BF`
- **TC-004**: Given dark mode — When reading `--text-faint` — Then value is `#8B949E`

---

### T-002: Create src/lib/status-intent.ts with scoreIntent() and STATUS_VARS
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05, AC-US1-06, AC-US1-07, AC-US1-08
**Status**: [x] completed

Export `StatusIntent` type, `scoreIntent(score, thresholds?)` pure function (>=80 success, >=60 warning, <60 danger — note spec says 60 mid, plan says 50, use spec thresholds: >=80 success, >=60 warning), and `STATUS_VARS` / `INTENT_VAR_MAP` record mapping intents to `var(--status-*)` strings.

**Test Plan**:
- **File**: `src/lib/__tests__/status-intent.test.ts`
- **TC-001**: Given score 100 — When scoreIntent(100) — Then returns "success"
- **TC-002**: Given score 80 — When scoreIntent(80) — Then returns "success"
- **TC-003**: Given score 79 — When scoreIntent(79) — Then returns "warning"
- **TC-004**: Given score 60 — When scoreIntent(60) — Then returns "warning"
- **TC-005**: Given score 59 — When scoreIntent(59) — Then returns "danger"
- **TC-006**: Given score 0 — When scoreIntent(0) — Then returns "danger"
- **TC-007**: Given intent "success" — When STATUS_VARS["success"].text — Then equals "var(--status-success-text)"
- **TC-008**: Given intent "danger" — When INTENT_VAR_MAP["danger"].bg — Then equals "var(--status-danger-bg)"
- **TC-009**: Given all 5 intents — When checking STATUS_VARS keys — Then all have text/bg/border entries

**Dependencies**: T-001

---

## Phase 2: Shared Components Migration (US-002) — [P]

### T-003: Migrate VerdictBadge.tsx — VERDICT_COLORS and SEVERITY_COLORS
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02
**Status**: [ ] Not Started

Replace hardcoded hex in `VERDICT_COLORS` and `SEVERITY_COLORS` maps with `var(--status-*)` tokens. `CountCell` severity-based coloring uses same tokens.

**Test Plan**:
- **File**: `src/app/components/__tests__/VerdictBadge.test.tsx` (update or create)
- **TC-001**: Given verdict "PASS" — When rendered — Then color style contains `var(--status-success-text)`
- **TC-002**: Given verdict "FAIL" — When rendered — Then color style contains `var(--status-danger-text)`
- **TC-003**: Given verdict "CONCERNS" — When rendered — Then color style contains `var(--status-warning-text)`
- **TC-004**: Given severity "critical" in CountCell — When rendered — Then color contains `var(--status-danger-text)`
- **TC-005**: Given severity "medium" in CountCell — When rendered — Then color contains `var(--status-warning-text)`

**Dependencies**: T-001

---

### T-004: Migrate EvalScoreDisplay.tsx — score-based coloring via scoreIntent()
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03
**Status**: [ ] Not Started

Replace hardcoded hex score thresholds with `scoreIntent()` + `STATUS_VARS`. Replace `VERDICT_RING_COLORS` hardcoded hex with `var(--status-*)` tokens.

**Test Plan**:
- **File**: `src/app/components/eval/__tests__/EvalScoreDisplay.test.tsx` (update or create)
- **TC-001**: Given score 85 — When EvalScoreDisplay rendered — Then color style contains `var(--status-success-text)`
- **TC-002**: Given score 65 — When EvalScoreDisplay rendered — Then color style contains `var(--status-warning-text)`
- **TC-003**: Given score 40 — When EvalScoreDisplay rendered — Then color style contains `var(--status-danger-text)`
- **TC-004**: Given verdict "PASS" — When rendered — Then ring color contains `var(--status-success-text)`
- **TC-005**: Given delta > 15 — When rendered — Then delta color contains `var(--status-success-text)` (or success variant)

**Dependencies**: T-001, T-002

---

### T-005: Migrate EvalCaseCard.tsx — pass/fail case indicators
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04
**Status**: [ ] Not Started

Replace hardcoded hex for pass/fail case indicators with `var(--status-success-*)` and `var(--status-danger-*)` tokens.

**Test Plan**:
- **File**: `src/app/components/eval/__tests__/EvalCaseCard.test.tsx` (update or create)
- **TC-001**: Given case result "pass" — When EvalCaseCard rendered — Then indicator color contains `var(--status-success-text)`
- **TC-002**: Given case result "fail" — When EvalCaseCard rendered — Then indicator color contains `var(--status-danger-text)`
- **TC-003**: Given case result "warn" — When EvalCaseCard rendered — Then indicator color contains `var(--status-warning-text)`

**Dependencies**: T-001

---

### T-006: Migrate EvalVerdictBadge.tsx — verdict display tokens
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05
**Status**: [ ] Not Started

Replace hardcoded hex in verdict color map with `var(--status-*)` tokens.

**Test Plan**:
- **File**: `src/app/components/eval/__tests__/EvalVerdictBadge.test.tsx` (update existing)
- **TC-001**: Given verdict "pass" — When rendered — Then badge color contains `var(--status-success-text)`
- **TC-002**: Given verdict "fail" — When rendered — Then badge color contains `var(--status-danger-text)`
- **TC-003**: Given verdict "ineffective" — When rendered — Then badge color contains `var(--status-neutral-text)`

**Dependencies**: T-001

---

### T-007: Migrate UsefulnessIndicator.tsx — usefulness level coloring
**User Story**: US-002 | **Satisfies ACs**: AC-US2-06
**Status**: [ ] Not Started

Replace hardcoded hex for usefulness levels with `var(--status-*)` tokens.

**Test Plan**:
- **File**: `src/app/components/eval/__tests__/UsefulnessIndicator.test.tsx` (update existing)
- **TC-001**: Given usefulness "high" — When rendered — Then color contains `var(--status-success-text)`
- **TC-002**: Given usefulness "low" — When rendered — Then color contains `var(--status-danger-text)` or `var(--status-warning-text)`
- **TC-003**: Given usefulness "neutral" — When rendered — Then color contains `var(--status-neutral-text)`

**Dependencies**: T-001

---

### T-008: Migrate SearchPalette.tsx — status colors in search results
**User Story**: US-002 | **Satisfies ACs**: AC-US2-07
**Status**: [ ] Not Started

Audit and replace any hardcoded status hex in SearchPalette.tsx with `var(--status-*)` tokens.

**Test Plan**:
- **File**: `src/app/components/__tests__/SearchPalette.test.tsx` (update or create)
- **TC-001**: Given search palette rendered with status items — When checking style attributes — Then no hardcoded status hex (#DC2626, #065F46, #B45309, #1D4ED8) present
- **TC-002**: Given skill with warning state — When rendered in palette — Then color contains `var(--status-warning-text)`

**Dependencies**: T-001

---

### T-009: Migrate RepoHealthBadge.tsx — health indicator tokens
**User Story**: US-002 | **Satisfies ACs**: AC-US2-08, AC-US2-09
**Status**: [ ] Not Started

Replace hardcoded hex health indicator colors with `var(--status-*)` tokens.

**Test Plan**:
- **File**: `src/app/skills/[owner]/[repo]/[skill]/__tests__/RepoHealthBadge.test.tsx` (create)
- **TC-001**: Given health "healthy" — When RepoHealthBadge rendered — Then color contains `var(--status-success-text)`
- **TC-002**: Given health "degraded" — When rendered — Then color contains `var(--status-warning-text)`
- **TC-003**: Given health "down" — When rendered — Then color contains `var(--status-danger-text)`

**Dependencies**: T-001

---

## Phase 3: Public Pages Migration (US-003) — [P]

### T-010: Migrate skill detail page.tsx — remaining hardcoded hex
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-07
**Status**: [ ] Not Started

Replace remaining hardcoded status hex in `src/app/skills/[owner]/[repo]/[skill]/page.tsx` with `var(--status-*)` tokens. Use `scoreIntent()` for score-based coloring.

**Test Plan**:
- **File**: `src/app/skills/[owner]/[repo]/[skill]/__tests__/SkillPage.status.test.tsx` (create)
- **TC-001**: Given skill page with cert score 90 — When rendered — Then score color contains `var(--status-success-text)`
- **TC-002**: Given skill page with cert score 65 — When rendered — Then score color contains `var(--status-warning-text)`
- **TC-003**: Given skill page with cert score 40 — When rendered — Then score color contains `var(--status-danger-text)`

**Dependencies**: T-001, T-002

---

### T-011: Migrate security/page.tsx — pass/fail and severity badge tokens
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-07
**Status**: [ ] Not Started

Replace hardcoded hex in `src/app/skills/[owner]/[repo]/[skill]/security/page.tsx` with `var(--status-*)` tokens for pass/fail indicators and severity badges.

**Test Plan**:
- **File**: `src/app/skills/[owner]/[repo]/[skill]/security/__tests__/SecurityPage.test.tsx` (create)
- **TC-001**: Given security check "pass" — When rendered — Then indicator color contains `var(--status-success-text)`
- **TC-002**: Given severity "critical" — When rendered — Then color contains `var(--status-danger-text)`
- **TC-003**: Given severity "medium" — When rendered — Then color contains `var(--status-warning-text)`

**Dependencies**: T-001

---

### T-012: Migrate submit/page.tsx and submit/[id]/page.tsx — submission status tokens
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US3-04, AC-US3-07
**Status**: [ ] Not Started

Replace hardcoded status hex in both submit pages with `var(--status-*)` tokens.

**Test Plan**:
- **File**: `src/app/submit/__tests__/SubmitPage.status.test.tsx` (create)
- **TC-001**: Given submission status "pending" — When rendered — Then status color contains `var(--status-warning-text)`
- **TC-002**: Given submission status "approved" — When rendered — Then color contains `var(--status-success-text)`
- **TC-003**: Given submission status "rejected" — When rendered — Then color contains `var(--status-danger-text)`

**Dependencies**: T-001

---

### T-013: Migrate RejectedSkillView.tsx and PublisherSkillsList.tsx
**User Story**: US-003 | **Satisfies ACs**: AC-US3-05, AC-US3-06, AC-US3-07
**Status**: [ ] Not Started

Replace hardcoded status hex in RejectedSkillView.tsx and PublisherSkillsList.tsx with `var(--status-*)` tokens.

**Test Plan**:
- **File**: `src/app/skills/[owner]/[repo]/[skill]/__tests__/RejectedSkillView.test.tsx` (create or update)
- **TC-001**: Given rejected skill view — When rendered — Then rejection indicator contains `var(--status-danger-text)`
- **TC-002**: Given publisher skill list with blocked skill — When rendered — Then status contains `var(--status-danger-text)`
- **TC-003**: Given publisher skill list with pending skill — When rendered — Then status contains `var(--status-warning-text)`

**Dependencies**: T-001

---

## Phase 4: Trust Pages Migration (US-004) — [P]

### T-014: Migrate VerifiedSkillsTab.tsx — verification status tokens
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-07
**Status**: [ ] Not Started

Replace hardcoded status hex in `src/app/trust/VerifiedSkillsTab.tsx` with `var(--status-*)` tokens. Use `scoreIntent()` where score-based coloring applies.

**Test Plan**:
- **File**: `src/app/trust/__tests__/VerifiedSkillsTab.test.tsx` (update existing)
- **TC-001**: Given verified skill — When VerifiedSkillsTab rendered — Then verification badge color contains `var(--status-success-text)`
- **TC-002**: Given skill with cert score 85 — When rendered — Then score color contains `var(--status-success-text)`
- **TC-003**: Given skill with cert score 55 — When rendered — Then score color contains `var(--status-danger-text)`

**Dependencies**: T-001, T-002

---

### T-015: Migrate ReportsTab.tsx — report severity/status tokens
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US4-07
**Status**: [ ] Not Started

Replace hardcoded status hex in `src/app/trust/ReportsTab.tsx` with `var(--status-*)` tokens.

**Test Plan**:
- **File**: `src/app/trust/__tests__/ReportsTab.test.tsx` (update existing)
- **TC-001**: Given report severity "critical" — When ReportsTab rendered — Then badge color contains `var(--status-danger-text)`
- **TC-002**: Given report severity "medium" — When rendered — Then badge color contains `var(--status-warning-text)`
- **TC-003**: Given report status "resolved" — When rendered — Then color contains `var(--status-success-text)`

**Dependencies**: T-001

---

### T-016: Migrate FindingsList.tsx — finding severity tokens
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03, AC-US4-07
**Status**: [ ] Not Started

Replace hardcoded status hex in `src/app/trust/FindingsList.tsx` with `var(--status-*)` tokens.

**Test Plan**:
- **File**: `src/app/trust/__tests__/FindingsList.test.tsx` (create)
- **TC-001**: Given finding severity "high" — When FindingsList rendered — Then indicator color contains `var(--status-danger-text)`
- **TC-002**: Given finding severity "low" — When rendered — Then color contains `var(--status-info-text)`
- **TC-003**: Given finding severity "medium" — When rendered — Then color contains `var(--status-warning-text)`

**Dependencies**: T-001

---

### T-017: Migrate BlockedSkillsTab.tsx — blocked/warning state tokens
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04, AC-US4-07
**Status**: [ ] Not Started

Replace hardcoded status hex in `src/app/trust/BlockedSkillsTab.tsx` with `var(--status-*)` tokens.

**Test Plan**:
- **File**: `src/app/trust/__tests__/BlockedSkillsTab.test.tsx` (update existing)
- **TC-001**: Given blocked skill — When BlockedSkillsTab rendered — Then status color contains `var(--status-danger-text)`
- **TC-002**: Given tainted skill — When rendered — Then color contains `var(--status-warning-text)`

**Dependencies**: T-001

---

### T-018: Migrate RejectedSkillsTab.tsx — rejection state tokens
**User Story**: US-004 | **Satisfies ACs**: AC-US4-05, AC-US4-07
**Status**: [ ] Not Started

Replace hardcoded status hex in `src/app/trust/RejectedSkillsTab.tsx` with `var(--status-*)` tokens.

**Test Plan**:
- **File**: `src/app/trust/__tests__/RejectedSkillsTab.test.tsx` (update existing)
- **TC-001**: Given rejected skill — When RejectedSkillsTab rendered — Then rejection indicator contains `var(--status-danger-text)`
- **TC-002**: Given withdrawn skill — When rendered — Then color contains `var(--status-neutral-text)`

**Dependencies**: T-001

---

### T-019: Migrate TrustTierDistribution.tsx — hardcoded status hex
**User Story**: US-004 | **Satisfies ACs**: AC-US4-06, AC-US4-07
**Status**: [ ] Not Started

Audit `src/app/trust/TrustTierDistribution.tsx` for any hardcoded status hex (not `--trust-t*` which is already done) and replace with `var(--status-*)` tokens.

**Test Plan**:
- **File**: `src/app/trust/__tests__/TrustTierDistribution.refresh.test.tsx` (update existing)
- **TC-001**: Given TrustTierDistribution rendered — When checking style attributes — Then no hardcoded status hex (#DC2626, #B45309, #065F46, #1D4ED8) present
- **TC-002**: Given distribution data — When rendered — Then tier colors use `var(--trust-t*)` or `var(--status-*)` only

**Dependencies**: T-001

---

## Phase 5: Queue Pages Migration (US-005) — [P]

### T-020: Migrate QueuePageClient.tsx — queue item status tokens
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-05
**Status**: [ ] Not Started

Replace hardcoded status hex in `src/app/queue/QueuePageClient.tsx` with `var(--status-*)` tokens.

**Test Plan**:
- **File**: `src/app/queue/__tests__/QueuePageClient.test.tsx` (create)
- **TC-001**: Given queue item status "pending" — When QueuePageClient rendered — Then status color contains `var(--status-warning-text)`
- **TC-002**: Given queue item status "approved" — When rendered — Then color contains `var(--status-success-text)`
- **TC-003**: Given queue item status "rejected" — When rendered — Then color contains `var(--status-danger-text)`

**Dependencies**: T-001

---

### T-021: Migrate QueueStatusBar.tsx — healthy/degraded/down state tokens
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02, AC-US5-05
**Status**: [ ] Not Started

Replace hardcoded status hex in `src/app/queue/QueueStatusBar.tsx` with `var(--status-*)` tokens.

**Test Plan**:
- **File**: `src/app/queue/__tests__/QueueStatusBar.test.tsx` (create)
- **TC-001**: Given queue status "healthy" — When QueueStatusBar rendered — Then indicator color contains `var(--status-success-text)`
- **TC-002**: Given queue status "degraded" — When rendered — Then color contains `var(--status-warning-text)`
- **TC-003**: Given queue status "down" — When rendered — Then color contains `var(--status-danger-text)`

**Dependencies**: T-001

---

### T-022: Migrate SubmissionTable.tsx — submission state tokens
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03, AC-US5-05
**Status**: [ ] Not Started

Replace hardcoded status hex in `src/app/queue/SubmissionTable.tsx` with `var(--status-*)` tokens.

**Test Plan**:
- **File**: `src/app/queue/__tests__/SubmissionTable.test.tsx` (create)
- **TC-001**: Given submission state "evaluating" — When SubmissionTable rendered — Then status indicator contains `var(--status-info-text)`
- **TC-002**: Given submission state "approved" — When rendered — Then color contains `var(--status-success-text)`
- **TC-003**: Given submission state "blocked" — When rendered — Then color contains `var(--status-danger-text)`

**Dependencies**: T-001

---

### T-023: Migrate AdminQueueActions.tsx — action state tokens
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04, AC-US5-05
**Status**: [ ] Not Started

Replace hardcoded status hex in `src/app/queue/AdminQueueActions.tsx` with `var(--status-*)` tokens.

**Test Plan**:
- **File**: `src/app/queue/__tests__/AdminQueueActions.test.tsx` (create)
- **TC-001**: Given action "approve" — When AdminQueueActions rendered — Then action color contains `var(--status-success-text)`
- **TC-002**: Given action "reject" — When rendered — Then color contains `var(--status-danger-text)`

**Dependencies**: T-001

---

## Phase 6: Admin Pages Migration (US-006) — [P]

### T-024: Migrate admin/page.tsx — dashboard summary status tokens
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-09
**Status**: [ ] Not Started

Replace hardcoded status hex in `src/app/admin/page.tsx` with `var(--status-*)` tokens.

**Test Plan**:
- **File**: `src/app/admin/__tests__/AdminPage.status.test.tsx` (create)
- **TC-001**: Given admin page rendered — When checking status summary — Then no hardcoded status hex present in inline styles
- **TC-002**: Given metric with warning state — When rendered — Then color contains `var(--status-warning-text)`

**Dependencies**: T-001

---

### T-025: Migrate admin/dashboard/page.tsx — metric/status display tokens
**User Story**: US-006 | **Satisfies ACs**: AC-US6-02, AC-US6-09
**Status**: [ ] Not Started

Replace hardcoded status hex in `src/app/admin/dashboard/page.tsx` with `var(--status-*)` tokens.

**Test Plan**:
- **File**: `src/app/admin/dashboard/__tests__/DashboardPage.test.tsx` (create)
- **TC-001**: Given dashboard rendered — When checking metric colors — Then no hardcoded status hex present
- **TC-002**: Given health metric "degraded" — When rendered — Then color contains `var(--status-warning-text)`

**Dependencies**: T-001

---

### T-026: Migrate admin/submissions/page.tsx and admin/submissions/[id]/page.tsx
**User Story**: US-006 | **Satisfies ACs**: AC-US6-03, AC-US6-04, AC-US6-09
**Status**: [ ] Not Started

Replace hardcoded status hex in both admin submission pages with `var(--status-*)` tokens.

**Test Plan**:
- **File**: `src/app/admin/submissions/__tests__/AdminSubmissionsPage.test.tsx` (create)
- **TC-001**: Given submission list — When admin submissions page rendered — Then status badges use `var(--status-*)` tokens
- **TC-002**: Given submission detail — When rendered — Then status indicator contains `var(--status-*)` token

**Dependencies**: T-001

---

### T-027: Migrate admin/queue/page.tsx and admin/blocklist/page.tsx
**User Story**: US-006 | **Satisfies ACs**: AC-US6-05, AC-US6-06, AC-US6-09
**Status**: [ ] Not Started

Replace hardcoded status hex in admin queue and blocklist pages with `var(--status-*)` tokens.

**Test Plan**:
- **File**: `src/app/admin/queue/__tests__/AdminQueuePage.test.tsx` (create)
- **TC-001**: Given admin queue page rendered — When checking status indicators — Then no hardcoded status hex present
- **TC-002**: Given blocked entry — When admin blocklist rendered — Then block indicator contains `var(--status-danger-text)`
- **TC-003**: Given allowed entry — When rendered — Then color contains `var(--status-success-text)`

**Dependencies**: T-001

---

### T-028: Migrate admin/reports/page.tsx and admin/skills/page.tsx
**User Story**: US-006 | **Satisfies ACs**: AC-US6-07, AC-US6-08, AC-US6-09
**Status**: [ ] Not Started

Replace hardcoded status hex in admin reports and skills pages with `var(--status-*)` tokens.

**Test Plan**:
- **File**: `src/app/admin/reports/__tests__/AdminReportsPage.test.tsx` (create)
- **TC-001**: Given report with "critical" severity — When admin reports rendered — Then color contains `var(--status-danger-text)`
- **TC-002**: Given admin skills page — When rendered — Then skill status badges use `var(--status-*)` tokens

**Dependencies**: T-001

---

## Phase 7: Deduplication — Shared State Config (US-007)

### T-029: Create src/lib/submission-state-styles.ts with STATE_CONFIG
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02
**Status**: [ ] Not Started

Export `STATE_CONFIG` mapping all 8 submission states (pending, evaluating, approved, rejected, blocked, tainted, withdrawn, resubmitted) to `{ intent: StatusIntent; label: string }`.

**Test Plan**:
- **File**: `src/lib/__tests__/submission-state-styles.test.ts` (create)
- **TC-001**: Given STATE_CONFIG — When checking keys — Then all 8 states present (pending, evaluating, approved, rejected, blocked, tainted, withdrawn, resubmitted)
- **TC-002**: Given STATE_CONFIG["approved"] — When reading intent — Then equals "success"
- **TC-003**: Given STATE_CONFIG["rejected"] — When reading intent — Then equals "danger"
- **TC-004**: Given STATE_CONFIG["pending"] — When reading intent — Then equals "warning"
- **TC-005**: Given STATE_CONFIG["evaluating"] — When reading intent — Then equals "info"
- **TC-006**: Given STATE_CONFIG["tainted"] — When reading intent — Then equals "warning"
- **TC-007**: Given STATE_CONFIG["withdrawn"] — When reading intent — Then equals "neutral"
- **TC-008**: Given STATE_CONFIG["resubmitted"] — When reading intent — Then equals "info"
- **TC-009**: Given STATE_CONFIG["blocked"] — When reading intent — Then equals "danger"

**Dependencies**: T-001, T-002

---

### T-030: Refactor duplicated state-to-color maps to use STATE_CONFIG
**User Story**: US-007 | **Satisfies ACs**: AC-US7-03, AC-US7-04, AC-US7-05
**Status**: [ ] Not Started

Identify all files with duplicated submission state-to-color maps (at minimum: SubmissionTable.tsx, admin submissions pages, submit pages). Replace with `STATE_CONFIG` + `INTENT_VAR_MAP` / `STATUS_VARS` pattern. Verify no hardcoded hex remains for submission state colors.

**Test Plan**:
- **File**: Grep audit — `grep -rn "#DC2626\|#FEE2E2\|#D1FAE5\|#065F46\|#B45309\|#FEF3C7\|#1D4ED8\|#DBEAFE" src/` after migration
- **TC-001**: Given all migrated files — When grep for hardcoded status hex — Then zero matches
- **TC-002**: Given STATE_CONFIG import in SubmissionTable.tsx — When rendered with state "approved" — Then visual output matches pre-migration light mode appearance
- **TC-003**: Given STATE_CONFIG import in admin submissions pages — When rendered — Then no visual regressions in light mode

**Dependencies**: T-022, T-026, T-012, T-029

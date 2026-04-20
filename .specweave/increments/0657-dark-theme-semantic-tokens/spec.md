---
increment: 0657-dark-theme-semantic-tokens
title: "Dark Theme Semantic Tokens"
type: feature
priority: P1
status: active
created: 2026-04-03
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Dark Theme Semantic Tokens

## Overview

verified-skill.com dark theme fails WCAG AA contrast across ~32 files. Hardcoded light-mode hex colors (#065F46, #1D4ED8, #B45309, #DC2626) with opaque pastel backgrounds (#D1FAE5, #DBEAFE, #FEF3C7, #FEE2E2) become invisible on the dark background (#0D1117). This increment adds 15 semantic status CSS variable tokens, a scoreIntent() helper, and migrates all remaining files from hardcoded hex to var() references.

**Approach**: Semantic CSS Variable Token Layer -- zero runtime cost, fully incremental, extends the pattern already proven in TrustBadge/TierBadge migration.

**Brainstorm**: `.specweave/docs/brainstorms/2026-04-02-dark-theme-readability-audit.md`

## Prior Work (Already Completed)

- globals.css: --trust-t0..t4 and --tier-verified/certified/tainted tokens with dark overrides
- TrustBadge.tsx: Migrated to CSS variables
- TierBadge.tsx: Migrated to CSS variables + currentColor SVGs
- Skill detail page.tsx: Fixed back link and byline separator contrast
- TrustTierDisplay.test.tsx: Updated test assertions

## User Stories

### US-001: Foundation -- Semantic Status Tokens and Helper (P0)
**Project**: vskill-platform

**As a** developer
**I want** semantic status CSS variable tokens and a scoreIntent() helper
**So that** all status colors are theme-aware and score-to-intent mapping is consistent across files

**Acceptance Criteria**:
- [x] **AC-US1-01**: globals.css :root defines 15 status tokens (--status-{success|warning|danger|info|neutral}-{text|bg|border}) with light-mode values per token table
- [x] **AC-US1-02**: globals.css [data-theme="dark"] overrides all 15 tokens with dark-mode values per token table
- [x] **AC-US1-03**: globals.css defines --link-accent (#0D9488 light, #2DD4BF dark)
- [x] **AC-US1-04**: globals.css raises --text-faint from #7D8590 to #8B949E in dark mode (5.0:1 ratio)
- [x] **AC-US1-05**: lib/status-intent.ts exports scoreIntent(score: number): StatusIntent mapping scores to success/warning/danger
- [x] **AC-US1-06**: lib/status-intent.ts exports StatusIntent type and INTENT_VAR_MAP mapping intents to CSS variable names
- [x] **AC-US1-07**: scoreIntent() thresholds: >=80 success, >=60 warning, <60 danger
- [x] **AC-US1-08**: All 15 dark-mode text token values pass WCAG AA contrast (>=4.5:1) against #0D1117

---

### US-002: Shared Component Migration (P0)
**Project**: vskill-platform

**As a** user viewing skill evaluations and search results in dark mode
**I want** status badges and indicators to use theme-aware colors
**So that** they remain readable regardless of theme

**Acceptance Criteria**:
- [x] **AC-US2-01**: VerdictBadge.tsx VERDICT_COLORS and SeverityBadge SEVERITY_COLORS use --status-* tokens instead of hardcoded hex
- [x] **AC-US2-02**: CountCell in VerdictBadge.tsx uses status tokens for severity-based coloring
- [x] **AC-US2-03**: EvalScoreDisplay.tsx uses scoreIntent() + INTENT_VAR_MAP for score-based coloring
- [x] **AC-US2-04**: EvalCaseCard.tsx uses status tokens for pass/fail case indicators
- [x] **AC-US2-05**: EvalVerdictBadge.tsx uses status tokens for verdict display
- [x] **AC-US2-06**: UsefulnessIndicator.tsx uses status tokens for usefulness level coloring
- [x] **AC-US2-07**: SearchPalette.tsx uses status tokens for any hardcoded status colors
- [x] **AC-US2-08**: RepoHealthBadge.tsx uses status tokens for health indicators
- [x] **AC-US2-09**: All migrated components render correctly in both light and dark themes (no visual regression)

---

### US-003: Public Pages Migration (P1)
**Project**: vskill-platform

**As a** user browsing skills, security details, and submission pages in dark mode
**I want** all status indicators to be readable
**So that** I can assess skill safety without switching to light mode

**Acceptance Criteria**:
- [x] **AC-US3-01**: Skill detail page.tsx remaining hardcoded hex replaced with status tokens
- [x] **AC-US3-02**: Security page.tsx uses status tokens for pass/fail indicators and severity badges
- [x] **AC-US3-03**: submit/page.tsx uses status tokens for submission status indicators
- [x] **AC-US3-04**: submit/[id]/page.tsx uses status tokens for submission detail status colors
- [x] **AC-US3-05**: RejectedSkillView.tsx uses status tokens for rejection status display
- [x] **AC-US3-06**: publishers/[name]/PublisherSkillsList.tsx uses status tokens for skill status indicators
- [x] **AC-US3-07**: All public pages pass WCAG AA contrast in dark mode for status text

---

### US-004: Trust Pages Migration (P1)
**Project**: vskill-platform

**As a** trust page visitor in dark mode
**I want** trust metrics, findings, and skill lists to display with readable contrast
**So that** I can evaluate platform trust signals without eye strain

**Acceptance Criteria**:
- [x] **AC-US4-01**: VerifiedSkillsTab.tsx uses status tokens for verification status colors
- [x] **AC-US4-02**: ReportsTab.tsx uses status tokens for report severity/status colors
- [x] **AC-US4-03**: FindingsList.tsx uses status tokens for finding severity indicators
- [x] **AC-US4-04**: BlockedSkillsTab.tsx uses status tokens for blocked/warning states
- [x] **AC-US4-05**: RejectedSkillsTab.tsx uses status tokens for rejection states
- [x] **AC-US4-06**: TrustTierDistribution.tsx uses status tokens for any hardcoded status hex
- [x] **AC-US4-07**: All trust page status indicators pass WCAG AA in dark mode

---

### US-005: Queue Pages Migration (P1)
**Project**: vskill-platform

**As a** queue reviewer in dark mode
**I want** submission statuses, health indicators, and action states to be clearly distinguishable
**So that** I can triage submissions without misreading status

**Acceptance Criteria**:
- [x] **AC-US5-01**: QueuePageClient.tsx uses status tokens for queue item status colors
- [x] **AC-US5-02**: QueueStatusBar.tsx uses status tokens for healthy/degraded/down states
- [x] **AC-US5-03**: SubmissionTable.tsx uses status tokens for submission state indicators
- [x] **AC-US5-04**: AdminQueueActions.tsx uses status tokens for action state colors
- [x] **AC-US5-05**: All queue page status indicators pass WCAG AA in dark mode

---

### US-006: Admin Pages Migration (P2)
**Project**: vskill-platform

**As an** admin using the dashboard in dark mode
**I want** all status badges, metrics, and action indicators to maintain readable contrast
**So that** I can manage the platform efficiently in my preferred theme

**Acceptance Criteria**:
- [x] **AC-US6-01**: admin/page.tsx uses status tokens for dashboard summary status colors
- [x] **AC-US6-02**: admin/dashboard/page.tsx uses status tokens for metric/status displays
- [x] **AC-US6-03**: admin/submissions/page.tsx uses status tokens for submission list status colors
- [x] **AC-US6-04**: admin/submissions/[id]/page.tsx uses status tokens for submission detail status
- [x] **AC-US6-05**: admin/queue/page.tsx uses status tokens for queue status indicators
- [x] **AC-US6-06**: admin/blocklist/page.tsx uses status tokens for block/allow states
- [x] **AC-US6-07**: admin/reports/page.tsx uses status tokens for report severity colors
- [x] **AC-US6-08**: admin/skills/page.tsx uses status tokens for skill status indicators
- [x] **AC-US6-09**: All admin pages pass WCAG AA in dark mode

---

### US-007: Deduplication -- Shared State Config (P2)
**Project**: vskill-platform

**As a** developer maintaining submission state styling
**I want** a single source of truth for state-to-color mappings
**So that** style changes propagate consistently and duplicated mappings don't drift

**Acceptance Criteria**:
- [x] **AC-US7-01**: lib/submission-state-styles.ts exports STATE_CONFIG mapping submission states to StatusIntent values
- [x] **AC-US7-02**: STATE_CONFIG covers all states: pending, evaluating, approved, rejected, blocked, tainted, withdrawn, resubmitted
- [x] **AC-US7-03**: All files with duplicated state-to-color mappings import from submission-state-styles.ts
- [x] **AC-US7-04**: No hardcoded hex remains for submission state colors in any migrated file
- [x] **AC-US7-05**: Existing behavior is preserved -- no visual regressions in light mode

## Functional Requirements

### FR-001: Semantic Status Token Definitions
globals.css defines 15 CSS custom properties (5 intents x 3 properties) in :root with light-mode values and [data-theme="dark"] with dark-mode values. Token names follow --status-{intent}-{property} convention.

### FR-002: scoreIntent() Helper
lib/status-intent.ts provides a pure function mapping numeric scores to StatusIntent values (>=80 success, >=60 warning, <60 danger) and an INTENT_VAR_MAP constant for resolving intents to CSS variable references.

### FR-003: STATE_CONFIG Deduplication
lib/submission-state-styles.ts provides a single STATE_CONFIG mapping all submission states to their StatusIntent, replacing duplicated state-to-color logic across 4+ files.

### FR-004: Incremental File Migration
Each file is migrated independently by replacing hardcoded hex values with var(--status-*) references. Migration order: shared components, public pages, trust pages, queue pages, admin pages.

## Token Table

### Light Mode (:root)

| Token | Value | Usage |
|-------|-------|-------|
| --status-success-text | #065F46 | Pass, approved, healthy |
| --status-success-bg | #D1FAE5 | Success chip background |
| --status-success-border | #A7F3D0 | Success chip border |
| --status-warning-text | #B45309 | Pending, degraded, medium severity |
| --status-warning-bg | #FEF3C7 | Warning chip background |
| --status-warning-border | #FDE68A | Warning chip border |
| --status-danger-text | #DC2626 | Fail, rejected, critical/high severity |
| --status-danger-bg | #FEE2E2 | Danger chip background |
| --status-danger-border | #FECACA | Danger chip border |
| --status-info-text | #1D4ED8 | Running, info, low severity |
| --status-info-bg | #DBEAFE | Info chip background |
| --status-info-border | #BFDBFE | Info chip border |
| --status-neutral-text | #6B7280 | Timed out, unknown, withdrawn |
| --status-neutral-bg | #F3F4F6 | Neutral chip background |
| --status-neutral-border | #E5E7EB | Neutral chip border |
| --link-accent | #0D9488 | Inline link accent |

### Dark Mode ([data-theme="dark"])

| Token | Value | Contrast vs #0D1117 |
|-------|-------|---------------------|
| --status-success-text | #34D399 | 8.2:1 |
| --status-success-bg | rgba(52,211,153,0.12) | n/a (bg) |
| --status-success-border | rgba(52,211,153,0.25) | 3.1:1 (non-text) |
| --status-warning-text | #FBBF24 | 10.1:1 |
| --status-warning-bg | rgba(251,191,36,0.12) | n/a |
| --status-warning-border | rgba(251,191,36,0.25) | 3.2:1 |
| --status-danger-text | #F87171 | 5.6:1 |
| --status-danger-bg | rgba(248,113,113,0.12) | n/a |
| --status-danger-border | rgba(248,113,113,0.25) | 3.1:1 |
| --status-info-text | #60A5FA | 5.3:1 |
| --status-info-bg | rgba(96,165,250,0.12) | n/a |
| --status-info-border | rgba(96,165,250,0.25) | 3.0:1 |
| --status-neutral-text | #8B949E | 5.0:1 |
| --status-neutral-bg | rgba(139,148,158,0.12) | n/a |
| --status-neutral-border | rgba(139,148,158,0.25) | 3.0:1 |
| --link-accent | #2DD4BF | 8.7:1 |
| --text-faint | #8B949E | 5.0:1 |

## scoreIntent() Specification

```typescript
type StatusIntent = "success" | "warning" | "danger" | "info" | "neutral";

function scoreIntent(score: number): StatusIntent {
  if (score >= 80) return "success";
  if (score >= 60) return "warning";
  return "danger";
}

const INTENT_VAR_MAP: Record<StatusIntent, { text: string; bg: string; border: string }> = {
  success: { text: "var(--status-success-text)", bg: "var(--status-success-bg)", border: "var(--status-success-border)" },
  warning: { text: "var(--status-warning-text)", bg: "var(--status-warning-bg)", border: "var(--status-warning-border)" },
  danger:  { text: "var(--status-danger-text)",  bg: "var(--status-danger-bg)",  border: "var(--status-danger-border)"  },
  info:    { text: "var(--status-info-text)",    bg: "var(--status-info-bg)",    border: "var(--status-info-border)"    },
  neutral: { text: "var(--status-neutral-text)", bg: "var(--status-neutral-bg)", border: "var(--status-neutral-border)" },
};
```

## STATE_CONFIG Specification

```typescript
const STATE_CONFIG: Record<string, { intent: StatusIntent; label: string }> = {
  pending:     { intent: "warning", label: "Pending" },
  evaluating:  { intent: "info",    label: "Evaluating" },
  approved:    { intent: "success", label: "Approved" },
  rejected:    { intent: "danger",  label: "Rejected" },
  blocked:     { intent: "danger",  label: "Blocked" },
  tainted:     { intent: "warning", label: "Tainted" },
  withdrawn:   { intent: "neutral", label: "Withdrawn" },
  resubmitted: { intent: "info",    label: "Resubmitted" },
};
```

## Migration Rules

1. Replace hardcoded hex with `var(--status-{intent}-{property})` references
2. Replace `color-mix(in srgb, ${hex} 15%, transparent)` backgrounds with `var(--status-{intent}-bg)` -- the token bg values are pre-computed equivalents
3. Use `scoreIntent()` + `INTENT_VAR_MAP` where colors depend on numeric scores
4. Use `STATE_CONFIG` + `INTENT_VAR_MAP` where colors depend on submission state strings
5. Do NOT touch `lib/agent-branding.ts` or `lib/category-constants.ts` (decorative brand colors)
6. Do NOT change `--chart-*` variables (data visualization, not status)
7. Preserve all existing light-mode visual appearance -- dark mode improves, light mode stays identical

## File Inventory

### Shared Components (US-002): 7 files
- `src/app/components/VerdictBadge.tsx`
- `src/app/components/eval/EvalScoreDisplay.tsx`
- `src/app/components/eval/EvalCaseCard.tsx`
- `src/app/components/eval/EvalVerdictBadge.tsx`
- `src/app/components/eval/UsefulnessIndicator.tsx`
- `src/app/components/SearchPalette.tsx`
- `src/app/skills/[owner]/[repo]/[skill]/RepoHealthBadge.tsx`

### Public Pages (US-003): 6 files
- `src/app/skills/[owner]/[repo]/[skill]/page.tsx`
- `src/app/skills/[owner]/[repo]/[skill]/security/page.tsx`
- `src/app/skills/[owner]/[repo]/[skill]/RejectedSkillView.tsx`
- `src/app/submit/page.tsx`
- `src/app/submit/[id]/page.tsx`
- `src/app/publishers/[name]/PublisherSkillsList.tsx`

### Trust Pages (US-004): 6 files
- `src/app/trust/VerifiedSkillsTab.tsx`
- `src/app/trust/ReportsTab.tsx`
- `src/app/trust/FindingsList.tsx`
- `src/app/trust/BlockedSkillsTab.tsx`
- `src/app/trust/RejectedSkillsTab.tsx`
- `src/app/trust/TrustTierDistribution.tsx`

### Queue Pages (US-005): 4 files
- `src/app/queue/QueuePageClient.tsx`
- `src/app/queue/QueueStatusBar.tsx`
- `src/app/queue/SubmissionTable.tsx`
- `src/app/queue/AdminQueueActions.tsx`

### Admin Pages (US-006): 8 files
- `src/app/admin/page.tsx`
- `src/app/admin/dashboard/page.tsx`
- `src/app/admin/submissions/page.tsx`
- `src/app/admin/submissions/[id]/page.tsx`
- `src/app/admin/queue/page.tsx`
- `src/app/admin/blocklist/page.tsx`
- `src/app/admin/reports/page.tsx`
- `src/app/admin/skills/page.tsx`

## Success Criteria

- Zero hardcoded **status** hex/rgba remaining in migrated files inside this increment's File Inventory (grep verification, scoped to inventory). "Status" means colors representing the semantic intents `success | warning | danger | info | neutral`. Link colors (`--link-accent`), brand/decorative colors (admin-chrome, homepage gradients, tier-specific badges), and chart visualization colors are explicitly excluded per the Out of Scope list and are NOT in-scope for this grep.
- All dark-mode status text passes WCAG AA 4.5:1 contrast ratio
- All dark-mode status borders pass WCAG AA 3:1 non-text contrast ratio
- No light-mode visual regressions (before/after comparison)
- STATE_CONFIG eliminates all duplicated state-to-color mappings

**Reviewer guidance (closure pipeline):** The canonical grep for pass/fail is:
```
grep -rEn '#[0-9A-Fa-f]{3,8}\b|rgba?\([0-9 ,.]+\)' <files-in-File-Inventory> | grep -v 'var(--'
```
Matches in files outside the File Inventory, or matches representing link/brand/decorative intent inside inventory files, MUST NOT be treated as 0657 blockers. Admin queue subtree residuals are formally tracked in [0657E-dark-theme-followup](../0657E-dark-theme-followup/) (see tasks.md Notes block).

## Out of Scope

- Redesigning component layouts or structure
- Adding new UI components
- Migrating **link colors** (e.g. `#0D9488` teal) — use `--link-accent` token, separate migration pass
- Migrating **brand/decorative colors** (agent-branding, category-constants, admin-layout/admin-chrome, homepage gradients, studio/docs/learn page palettes)
- Migrating `src/app/admin/queue/*` subtree and `src/app/queue/QueueStatusBar.tsx` — tracked in 0657E
- Migrating `src/app/admin/installs/page.tsx`, `admin/reports/page.tsx`, `admin/layout.tsx`, `admin/page.tsx`, `admin/users/page.tsx` brand styling — not in File Inventory
- Migrating homepage components (`components/homepage/*`), studio page, learn/docs pages — public-facing brand surface, not status
- Adding ESLint rule blocking hardcoded hex (future increment)
- Adding @supports fallback for color-mix() (existing uses replaced, not extended)
- Changing chart-* visualization colors

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Light-mode visual regression | Low | Medium | Token light values match existing hardcoded hex exactly |
| Missed hardcoded hex in migrated file | Low | Low | Grep audit after each story completion |
| color-mix() removal breaks appearance | Low | Medium | Replace with pre-computed rgba() bg tokens, visually identical |

## Dependencies

- US-001 (tokens + helper) must complete before US-002 through US-006
- US-007 (deduplication) depends on US-003 and US-005 completing to identify all duplicated patterns
- No external dependencies

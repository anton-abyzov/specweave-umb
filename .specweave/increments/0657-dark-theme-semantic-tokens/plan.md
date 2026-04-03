# Architecture Plan: Dark Theme Semantic Tokens

## Overview

Fix dark theme readability across vskill-platform by introducing semantic CSS variable tokens in `globals.css`, creating a `scoreIntent()` helper, extracting shared status color maps, and migrating ~20 files from hardcoded hex to `var()` references. Zero runtime cost, zero visual change in light mode, full WCAG compliance in dark mode.

## Architecture

### Architecture Decision: CSS Custom Properties

| Option | Verdict | Reason |
|--------|---------|--------|
| **CSS custom properties** | **Chosen** | Zero runtime cost, already the project's pattern, works with SSR, no JS bundle impact |
| React context/provider | Rejected | Runtime overhead, requires provider wrapping, re-renders on theme change |
| Tailwind CSS | Rejected | Not in project tech stack, would add build complexity |
| CSS modules/classes | Rejected | More indirection than needed; inline styles + var() is the established pattern |

ADR reference: `0001-tech-stack.md` — project uses Next.js 15, CSS custom properties, no Tailwind.

### Components

#### 1. CSS Token Layer (`globals.css`)

New semantic tokens added to both `:root` and `[data-theme="dark"]` blocks.

**Naming convention**: `--status-{intent}-{role}` where intent = success|warning|danger|info|neutral, role = text|bg|border.

**Token table**:

| Token | Light | Dark | Use |
|-------|-------|------|-----|
| `--status-danger-text` | `#DC2626` | `#F87171` | Errors, critical severity, blocked |
| `--status-danger-bg` | `#FEE2E2` | `rgba(248, 113, 113, 0.12)` | Danger badge backgrounds |
| `--status-danger-border` | `rgba(220, 38, 38, 0.25)` | `rgba(248, 113, 113, 0.25)` | Danger badge borders |
| `--status-warning-text` | `#B45309` | `#FBBF24` | Medium severity, pending |
| `--status-warning-bg` | `#FEF3C7` | `rgba(251, 191, 36, 0.12)` | Warning backgrounds |
| `--status-warning-border` | `rgba(180, 83, 9, 0.25)` | `rgba(251, 191, 36, 0.25)` | Warning borders |
| `--status-success-text` | `#065F46` | `#34D399` | Approved, published, resolved |
| `--status-success-bg` | `#D1FAE5` | `rgba(52, 211, 153, 0.12)` | Success backgrounds |
| `--status-success-border` | `rgba(6, 95, 70, 0.25)` | `rgba(52, 211, 153, 0.25)` | Success borders |
| `--status-info-text` | `#1D4ED8` | `#60A5FA` | Informational, submitted |
| `--status-info-bg` | `#DBEAFE` | `rgba(96, 165, 250, 0.12)` | Info backgrounds |
| `--status-info-border` | `rgba(29, 78, 216, 0.25)` | `rgba(96, 165, 250, 0.25)` | Info borders |
| `--status-neutral-text` | `#475569` | `#8B949E` | Dismissed, inactive |
| `--status-neutral-bg` | `#F1F5F9` | `rgba(139, 148, 158, 0.12)` | Neutral backgrounds |
| `--status-neutral-border` | `rgba(71, 85, 105, 0.25)` | `rgba(139, 148, 158, 0.25)` | Neutral borders |
| `--status-high-text` | `#C2410C` | `#FB923C` | High severity (orange) |
| `--status-high-bg` | `#FFEDD5` | `rgba(251, 146, 60, 0.12)` | High severity bg |
| `--threat-purple-text` | `#7C3AED` | `#A78BFA` | Prompt injection |
| `--threat-purple-bg` | `#F3E8FF` | `rgba(167, 139, 250, 0.12)` | Prompt injection bg |
| `--threat-pink-text` | `#BE185D` | `#F472B6` | Malware distribution |
| `--threat-pink-bg` | `#FCE7F3` | `rgba(244, 114, 182, 0.12)` | Malware bg |
| `--link-accent` | `#0D9488` | `#2DD4BF` | Teal link color |
| `--interactive-primary` | `#6366F1` | `#818CF8` | Indigo interactive elements |
| `--interactive-primary-bg` | `rgba(99, 102, 241, 0.08)` | `rgba(129, 140, 248, 0.12)` | Indigo button bg |
| `--interactive-primary-border` | `rgba(99, 102, 241, 0.3)` | `rgba(129, 140, 248, 0.3)` | Indigo button border |
| `--score-high` | `#065F46` | `#34D399` | Score >= 80 |
| `--score-mid` | `#B45309` | `#FBBF24` | Score 50-79 |
| `--score-low` | `#DC2626` | `#F87171` | Score < 50 |

#### 2. `scoreIntent()` Helper (`src/lib/score-intent.ts`)

```typescript
export type StatusIntent = "success" | "warning" | "danger" | "info" | "neutral";

export const STATUS_VARS: Record<StatusIntent, { text: string; bg: string; border: string }> = {
  success: { text: "var(--status-success-text)", bg: "var(--status-success-bg)", border: "var(--status-success-border)" },
  warning: { text: "var(--status-warning-text)", bg: "var(--status-warning-bg)", border: "var(--status-warning-border)" },
  danger:  { text: "var(--status-danger-text)",  bg: "var(--status-danger-bg)",  border: "var(--status-danger-border)" },
  info:    { text: "var(--status-info-text)",    bg: "var(--status-info-bg)",    border: "var(--status-info-border)" },
  neutral: { text: "var(--status-neutral-text)", bg: "var(--status-neutral-bg)", border: "var(--status-neutral-border)" },
};

export function scoreIntent(score: number, thresholds?: { high?: number; mid?: number }): StatusIntent {
  const high = thresholds?.high ?? 80;
  const mid = thresholds?.mid ?? 50;
  if (score >= high) return "success";
  if (score >= mid) return "warning";
  return "danger";
}
```

- Pure function, zero dependencies, trivially testable
- Default thresholds (80/50) match existing `certScore >= 80 ? green : certScore >= 50 ? amber : red` pattern
- Returns intent name; caller picks `STATUS_VARS[intent].text` etc.

#### 3. Shared Status Color Maps (`src/lib/status-colors.ts`)

Consolidates duplicated color maps across 4+ files into one import:

```typescript
export const SEVERITY_BADGE_VARS = { critical, high, medium, low, info };
export const STATE_BADGE_VARS = { RECEIVED, TIER1_SCANNING, ..., SUBMITTED, UNDER_REVIEW, RESOLVED, DISMISSED };
export const VERDICT_BADGE_VARS = { PASS, CONCERNS, FAIL };
export const THREAT_BADGE_VARS = { "prompt-injection", "credential-theft", ... };
export const TIER_BADGE_VARS = { VERIFIED, CERTIFIED, TAINTED };
```

All maps use `var(--status-*)` references instead of hardcoded hex.

### Migration Pattern

**Before** (hardcoded hex, light-only):
```tsx
const SEVERITY_COLORS = { critical: { bg: "#FEE2E2", color: "#DC2626" } };
<span style={{ backgroundColor: c.bg, color: c.color }}>critical</span>
```

**After** (CSS var, theme-aware):
```tsx
import { SEVERITY_BADGE_VARS } from "@/lib/status-colors";
const c = SEVERITY_BADGE_VARS[severity] ?? SEVERITY_BADGE_VARS.info;
<span style={{ backgroundColor: c.bg, color: c.text }}>critical</span>
```

### Dependency Graph

```
globals.css (tokens)
    |-- score-intent.ts (STATUS_VARS references the tokens)
    |-- status-colors.ts (shared badge maps reference the tokens)
    |     |-- BlockedSkillsTab.tsx
    |     |-- FindingsList.tsx
    |     |-- VerifiedSkillsTab.tsx
    |     |-- ReportsTab.tsx
    |     |-- admin/dashboard/page.tsx
    |     +-- ... other consumers
    +-- TrustTierDistribution.tsx (uses --trust-t* vars directly)
```

No circular dependencies. All new modules are leaf dependencies.

## Technology Stack

- **Framework**: Next.js 15 (existing)
- **Styling**: CSS custom properties in `globals.css` (existing pattern)
- **Testing**: Vitest + React Testing Library (existing, TDD)
- **No new dependencies required**

## Implementation Phases

### Phase 1: Foundation (T-001 through T-003)
1. Add semantic tokens to `globals.css` (both `:root` and `[data-theme="dark"]`)
2. Create `score-intent.ts` with `scoreIntent()` + `STATUS_VARS`
3. Create `status-colors.ts` shared badge maps

### Phase 2: Trust Page Migration (T-004 through T-008)
4. Migrate `TrustTierDistribution.tsx` — use `--trust-t*` vars
5. Migrate `BlockedSkillsTab.tsx` — import shared maps
6. Migrate `FindingsList.tsx` — import shared maps
7. Migrate `VerifiedSkillsTab.tsx` — import shared maps + `scoreIntent()`
8. Migrate `ReportsTab.tsx` — import shared maps

### Phase 3: Admin Page Migration (T-009 through T-010)
9. Migrate `admin/dashboard/page.tsx` — import shared maps
10. Migrate `admin/installs/page.tsx` — replace hex colors

### Phase 4: Remaining Pages (T-011 through T-015)
11. Migrate `report/page.tsx` + `report/my-reports/page.tsx`
12. Migrate `submit/page.tsx` + `submit/[id]/page.tsx`
13. Migrate `skills/page.tsx`
14. Migrate `studio/page.tsx`
15. Migrate `components/CodeBlock.tsx`

## Testing Strategy

- **TDD**: Tests written before implementation changes
- **jsdom limitation**: Cannot resolve CSS variables; tests assert `var(--status-danger-text)` literal strings (proven pattern from `TrustTierDisplay.test.tsx` lines 84-116)
- **Unit tests**: `score-intent.test.ts` for pure function, `status-colors.test.ts` for map correctness
- **Integration tests**: Existing component tests updated to assert `var()` strings
- **Coverage target**: 90%

## Exclusions

- `global-error.tsx` — renders outside CSS cascade (bare HTML error boundary before stylesheets). Must use hardcoded values.
- `not-found.tsx`, `error.tsx` — use `--bg-code` dark surface where `#E6EDF3` text is correct in both themes.
- `color-mix()` compatibility — already used in project, no `@supports` fallback needed for tokens (they define direct values).

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Token naming collision | Low | Low | `--status-` prefix avoids conflict with existing `--admin-*`, `--trust-*` |
| Visual regression in light mode | Medium | Low | Tokens use identical hex values; zero visual change in light mode |
| Missing dark variant | Low | Medium | Systematic file-by-file migration with test coverage |
| Test breakage from hex->var() change | Medium | Low | Tests updated in same tasks; pattern proven in TrustBadge tests |

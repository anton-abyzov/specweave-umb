# Tasks: Versions tab empty-state guidance

All paths relative to `repositories/anton-abyzov/vskill/`.

## Phase 1 — RED

### T-001: RED — submit-url helper tests
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**File**: `src/eval-ui/src/utils/__tests__/submit-url.test.ts` (NEW)

**Test Plan**:
- No `repoUrl` → `"https://verified-skill.com/submit"`
- Valid GitHub URL → `"https://verified-skill.com/submit?repo=<encoded>"`
- Non-GitHub URL → bare `/submit` (defensive)
- URL with embedded credentials → bare `/submit`

### T-002: RED — empty-state component tests
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-04 | **Status**: [x] completed
**File**: `src/eval-ui/src/pages/workspace/__tests__/VersionHistoryPanel.empty-state.test.tsx` (NEW)

**Test Plan**:
- Source skill + empty versions → tree contains `data-testid="versions-empty-state-local"` + CTA `data-testid="versions-empty-state-cta"`
- Installed skill (origin="plugin") + empty → tree contains `data-testid="versions-empty-state-installed"` and no CTA
- CTA `href` contains encoded repoUrl
- CTA has `target="_blank"` + `rel="noopener noreferrer"`

## Phase 2 — GREEN

### T-003: GREEN — submit-url helper
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**File**: `src/eval-ui/src/utils/submit-url.ts` (NEW)

### T-004: GREEN — branched empty state in VersionHistoryPanel
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-04 | **Status**: [x] completed
**File**: `src/eval-ui/src/pages/workspace/VersionHistoryPanel.tsx`

Implementation: read `skill.origin` from `useStudio().skills.find(...)` (already done at line 115). Split empty branch into source vs installed.

## Phase 3 — Verify

### T-005: VERIFY — full suite + smoke
**Status**: [x] completed

1. `npx vitest run src/eval-ui` (UI suite green)
2. `npm run build` (TS clean)
3. Bump 0.5.110 → npm publish → restart studio
4. Smoke: `http://localhost:3162/#/skills/easychamp/greet-anton` → Versions tab → CTA visible

## Dependencies

- T-001 + T-002 parallel
- T-003 depends on T-001
- T-004 depends on T-002 + T-003
- T-005 depends on all

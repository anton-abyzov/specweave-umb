# 0848 Tasks

> Reconciled 2026-06-10: T-001/T-002/T-004/T-005 verified landed + wired (see code paths below). T-003/T-006/T-007 are implemented under increment **0874** (tiered-private-skills-paywall, workstream C).

### T-001: useSkillVisibility hook (desktop)
**AC**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Landed**: `vskill/src/eval-ui/src/hooks/useSkillRepoVisibility.ts` (resolveSkillRepoVisibility joins repoUrl↔connected repos; test `useSkillRepoVisibility.test.ts`).
**Test**: Given a SkillInfo with repoUrl matching a private connected repo → When the hook is read → Then it returns "private"; same skill matching a public repo → returns "public"; no match → "unknown".

### T-002: PrivateRepoChip component + SkillRow integration
**AC**: AC-US1-01, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Landed**: `vskill/src/eval-ui/src/components/PrivateRepoChip.tsx` + `SkillRow.tsx:207` (chip on `repoVisibility === 'private'`, data-testid `skill-row-private-chip`).

### T-003: Sidebar sub-grouping by visibility within Project section
**AC**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed (0874 workstream C)
**Test**: When AVAILABLE > Project has 2 private + 3 public skills → render two sub-headers. When only 1 visibility class present → no sub-header.

### T-004: Account skills tile color/icon hierarchy (web)
**AC**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Landed**: `vskill/src/eval-ui/src/components/account/ConnectedReposTable.tsx` (private/public VisibilitySection split, lock/globe glyphs), mounted via `AccountShell.tsx:380`.

### T-005: Public catalog "You have N private skills" banner (web)
**AC**: AC-US4-01 | **Status**: [x] completed

### T-006: Publisher profile private-skills footer (web)
**AC**: AC-US4-02 | **Status**: [x] completed (0874 workstream C)
**Test**: /publishers/[name] viewed by the publisher renders the footer when they have private skills; viewed by anonymous → no footer.

### T-007: MarketplaceDrawer "Your private plugins" section (desktop)
**AC**: AC-US5-01 | **Status**: [x] completed (0874 workstream C)
**Test**: MarketplaceDrawer with 2 private-repo plugins renders a top section with amber tint above the marketplace list.

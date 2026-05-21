# 0848 Tasks

### T-001: useSkillVisibility hook (desktop)
**AC**: AC-US1-01, AC-US1-02 | **Status**: [ ] pending
**Test**: Given a SkillInfo with repoUrl matching a private connected repo → When the hook is read → Then it returns "private"; same skill matching a public repo → returns "public"; no match → "unknown".

### T-002: PrivateRepoChip component + SkillRow integration
**AC**: AC-US1-01, AC-US1-03, AC-US1-04 | **Status**: [ ] pending
**Test**: SkillRow renders `[data-testid="skill-row-private-chip"]` only when visibility === "private". aria-label mentions "private repo".

### T-003: Sidebar sub-grouping by visibility within Project section
**AC**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [ ] pending
**Test**: When AVAILABLE > Project has 2 private + 3 public skills → render two sub-headers. When only 1 visibility class present → no sub-header.

### T-004: Account skills tile color/icon hierarchy (web)
**AC**: AC-US3-01, AC-US3-02 | **Status**: [ ] pending
**Test**: /account/skills public tile has neutral surface + globe icon; private tile has amber tint + lock icon.

### T-005: Public catalog "You have N private skills" banner (web)
**AC**: AC-US4-01 | **Status**: [ ] pending
**Test**: GET /skills as signed-in user with N>0 private skills → renders banner; N=0 → no banner; unauthenticated → no banner.

### T-006: Publisher profile private-skills footer (web)
**AC**: AC-US4-02 | **Status**: [ ] pending
**Test**: /publishers/[name] viewed by the publisher renders the footer when they have private skills; viewed by anonymous → no footer.

### T-007: MarketplaceDrawer "Your private plugins" section (desktop)
**AC**: AC-US5-01 | **Status**: [ ] pending
**Test**: MarketplaceDrawer with 2 private-repo plugins renders a top section with amber tint above the marketplace list.

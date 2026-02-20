# Tasks — 0250: Universal Skill Discovery Pipeline

## Phase 1: Discovery Provider Framework

### T-001: DiscoveryProvider interface and SourceRegistry
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given a SourceRegistry with 2 registered providers → When `discoverAll()` is called → Then results from both providers are yielded

### T-002: GitHub broad search provider
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-05 | **Status**: [x] completed
**Test**: Given GitHub provider with queries `filename:SKILL.md`, `path:.claude/commands` → When `discover()` runs → Then repos are yielded as `GitHubRepoInfo` with dedup

### T-003: skills.sh provider
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-05 | **Status**: [x] completed
**Test**: Given skills.sh HTML/API response with repo links → When `discover()` runs → Then GitHub repo URLs are extracted and normalized to `GitHubRepoInfo`

### T-004: npm registry provider
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Test**: Given npm search results for `claude-code-skill` keyword → When `discover()` runs → Then packages with GitHub repos are normalized to `GitHubRepoInfo`

### T-005: Scanner config for enabled sources
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06 | **Status**: [x] completed
**Test**: Given config with `sources: ["github", "npm"]` (skills.sh disabled) → When scanner starts → Then only GitHub and npm providers run

## Phase 2: Content Fetching

### T-006: Fetch SKILL.md from discovered repos
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-04 | **Status**: [x] completed
**Test**: Given a discovered submission → When content fetch runs → Then SKILL.md raw content is stored on the submission record

### T-007: Handle missing SKILL.md
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**Test**: Given a repo where SKILL.md returns 404 → When content fetch runs → Then submission is marked `tier1_failed` with reason "SKILL.md not found"

## Phase 3: Security Scoring

### T-008: Wire scanSkillContent to fetched content
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test**: Given fetched SKILL.md content → When Tier 1 scan runs → Then `tier1Result` is populated with score, findings count, and pass/fail

### T-009: Auto-advance based on score threshold
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US3-04 | **Status**: [x] completed
**Test**: Given Tier 1 score >= 70 → Then status becomes `tier1_passed` | Given score < 70 → Then status becomes `tier1_failed`

## Phase 4: Integration

### T-010: Wire providers into scanner worker loop
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given scanner worker starts → When scan cycle runs → Then all enabled providers are called and results feed into submission queue

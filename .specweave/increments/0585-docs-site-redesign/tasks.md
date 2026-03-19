---
increment: 0585-docs-site-redesign
---

# Tasks: Redesign SpecWeave Documentation Site

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed

## Dependency Summary

```
T-001 through T-015 (Phase 1, sidebar)  ─┐
T-016 (Phase 2, features trim)           ├──> T-017 through T-021 (Phase 4) ──> T-022 (Phase 5)
T-003 through T-013 (Phase 3, dashboard) ─┘
```

Phases 1, 2, 3 are parallelizable. Phase 4 depends on all three. Phase 5 is the final gate.

---

## Phase 1: Sidebar Restructure (sidebars.ts)

### T-001: Add orphaned command pages to Commands section
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed
**Test**: Given `sidebars.ts` is updated → When the docs site builds → Then `commands/abandon`, `commands/pause`, `commands/resume`, `commands/status` appear in the Commands section of the sidebar

### T-002: Add individual orphaned items to existing categories
**User Story**: US-001 | **Satisfies ACs**: AC-US1-07, AC-US1-08, AC-US1-09, AC-US1-10, AC-US1-14, AC-US1-15 | **Status**: [x] completed
**Test**: Given `sidebars.ts` is updated → When the sidebar is inspected → Then `skills/skill-contradiction-resolution` is in Skills, `enterprise/knowledge-transfer-migration` is in Enterprise Migration, `integrations/generic-ai-tools` is in Integrations, `overview/ai-revolution-context` is in Overview, `guides/core-concepts/who-benefits-from-living-docs` is in Core Concepts, and `api/index` and `examples/index` appear as standalone items

### T-003: Add Sync Deep Dives subcategory under Integrations
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test**: Given `sidebars.ts` is updated → When the sidebar is inspected → Then a "Sync Deep Dives" subcategory (collapsed: true) under Integrations contains all 9 orphaned sync guides: `guides/sync-configuration`, `guides/sync-strategies`, `guides/spec-bidirectional-sync`, `guides/spec-commit-sync`, `guides/status-sync-guide`, `guides/status-sync-migration`, `guides/multi-project-sync-architecture`, `guides/umbrella-sync-routing`, `guides/hierarchy-mapping`

### T-004: Add Migration Guides subcategory under Reference
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, AC-US1-06 | **Status**: [x] completed
**Test**: Given `sidebars.ts` is updated → When the sidebar is inspected → Then "Migration Guides" subcategory (collapsed: true) under Reference contains `guides/migration-v024`, `guides/migration-v031-project-fields`, and `reference/changelog`

### T-005: Add Advanced Topics subcategory under Guides
**User Story**: US-001 | **Satisfies ACs**: AC-US1-11 | **Status**: [x] completed
**Test**: Given `sidebars.ts` is updated → When the sidebar is inspected → Then "Advanced Topics" subcategory (collapsed: true) under Guides contains all 11 files: `guides/plugin-management`, `guides/lazy-plugin-loading`, `guides/deployment-platforms`, `guides/github-action-setup`, `guides/project-specific-tasks`, `guides/repository-selection`, `guides/increment-status-reference`, `guides/scheduling-and-planning`, `guides/specs-organization-guide`, `guides/meta-capability`, `guides/deep-interview-mode`

### T-006: Add Learning & Comparison subcategory under Guides
**User Story**: US-001 | **Satisfies ACs**: AC-US1-11 | **Status**: [x] completed
**Test**: Given `sidebars.ts` is updated → When the sidebar is inspected → Then "Learning & Comparison" subcategory (collapsed: true) under Guides contains `guides/specweave-learning-journey`, `guides/specweave-vs-speckit`, `guides/ai-coding-benchmarks`, `guides/why-verified-skill-matters`

### T-007: Add Platform-Specific subcategory under Guides
**User Story**: US-001 | **Satisfies ACs**: AC-US1-11 | **Status**: [x] completed
**Test**: Given `sidebars.ts` is updated → When the sidebar is inspected → Then "Platform-Specific" subcategory (collapsed: true) under Guides contains `guides/mobile/react-native-setup-guide`, `guides/openclaw-agent-setup`, `guides/ado-multi-project-migration`

### T-008: Add remaining orphaned guides as direct items under Guides
**User Story**: US-001 | **Satisfies ACs**: AC-US1-11 | **Status**: [x] completed
**Test**: Given `sidebars.ts` is updated → When the sidebar is inspected → Then `guides/agent-skills-extensibility-analysis`, `guides/command-reference-by-priority`, `guides/life-automation`, `guides/multilingual-guide` appear as direct items in the Guides section

### T-009: Add Dashboard & Observability top-level category to docsSidebar
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-12 | **Status**: [x] completed
**Test**: Given all 10 dashboard docs exist (Phase 3) → When `sidebars.ts` is updated → Then a "Dashboard & Observability" top-level category (collapsed: true) appears after Agent Teams, contains `guides/analytics-dashboard` as entry point plus all 10 new dashboard page doc IDs

---

## Phase 2: Features Page Trim

### T-010: Trim overview/features.md to ~150 lines
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [x] completed
**Test**: Given `overview/features.md` is 605 lines → When it is rewritten → Then the file is ≤200 lines, each feature section has a 2-3 sentence summary with a "Learn more" link to the relevant detail page, no feature is removed from the page entirely, and all internal links resolve to existing pages

---

## Phase 3: Dashboard Documentation (10 new files)

### T-011: Create guides/dashboard/errors.md and guides/dashboard/sync.md
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-05, AC-US3-06 | **Status**: [x] completed
**Test**: Given `ErrorsPage.tsx` and `SyncPage.tsx` sources exist → When both files are created → Then `errors.md` documents error grouping/KPI cards/timeline and `sync.md` documents platform connection/per-repo sync/permissions; both have valid frontmatter and are ≤150 lines

### T-012: Create guides/dashboard/activity.md and guides/dashboard/config.md
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-05, AC-US3-06 | **Status**: [x] completed
**Test**: Given `ActivityPage.tsx` and `ConfigPage.tsx` sources exist → When both files are created → Then `activity.md` documents event feed/category filters/SSE and `config.md` documents live editing/validation/save-reset; both have valid frontmatter and are ≤150 lines

### T-013: Create guides/dashboard/services.md and guides/dashboard/notifications.md
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-05, AC-US3-06 | **Status**: [x] completed
**Test**: Given `ServicesPage.tsx` and `NotificationsPage.tsx` sources exist → When both files are created → Then `services.md` documents service monitoring/port detection/start-stop and `notifications.md` documents feed/dismiss/severity filters; both have valid frontmatter and are ≤150 lines

### T-014: Create guides/dashboard/marketplace.md and guides/dashboard/plugins.md
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-05, AC-US3-06 | **Status**: [x] completed
**Test**: Given `MarketplacePage.tsx` and `PluginsPage.tsx` sources exist → When both files are created → Then `marketplace.md` documents scanner/approve-reject/security scores and `plugins.md` documents installed plugins/usage stats/LSP status; both have valid frontmatter and are ≤150 lines

### T-015: Create guides/dashboard/agents.md and guides/dashboard/hooks.md
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-05, AC-US3-06 | **Status**: [x] completed
**Test**: Given `AgentsPage.tsx` and `HooksPage.tsx` sources exist → When both files are created → Then `agents.md` documents lifecycle tracking/session filtering/SSE and `hooks.md` documents hook event log/event type filters/consecutive collapsing; both have valid frontmatter and are ≤150 lines

---

## Phase 4: Cross-Linking Pass

### T-016: Add dashboard page links to analytics-dashboard.md
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed
**Test**: Given all 10 new dashboard pages exist → When `guides/analytics-dashboard.md` is updated → Then it contains a "Dashboard Pages" section with links to each of the 10 new capability pages

### T-017: Add Related footers to 9 sync guides
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [x] completed
**Test**: Given Phase 1 sidebar changes are complete → When each of the 9 sync guides is updated → Then each file has a "Related" footer linking to `guides/integrations/external-tools-overview` and 1-2 relevant sibling sync guides

### T-018: Add changelog links to migration guides
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03 | **Status**: [x] completed
**Test**: Given `reference/changelog` is in the sidebar → When `guides/migration-v024` and `guides/migration-v031-project-fields` are updated → Then each file contains a link to `reference/changelog`

### T-019: Verify features page has 15+ detail page links
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04, AC-US4-05 | **Status**: [x] completed
**Test**: Given T-010 (features page trim) is complete → When the trimmed `overview/features.md` is reviewed → Then it contains at least 15 distinct internal links to detail pages and no circular-only navigation exists

---

## Phase 5: Build Verification

### T-020: Run npm run build and verify clean output
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05 | **Status**: [x] completed
**Test**: Given all phases 1-4 are complete → When `npm run build` is run in `docs-site/` → Then exit code is 0, no broken internal links are reported, all 10 new dashboard pages render without warnings, all new sidebar categories appear without errors, and no duplicate doc IDs exist

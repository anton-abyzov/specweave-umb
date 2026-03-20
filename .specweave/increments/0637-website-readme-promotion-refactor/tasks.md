# Tasks: Website & README Promotion Refactor

## Phase 1: New Homepage Components

### T-001: Create WhySpecFirstSection component
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [ ] not started
**Test**: Given homepage loads → When user scrolls to Why Spec-First section → Then comparison table renders with 5 competitors and 6 capability rows

### T-002: Create ShowcaseSection component
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04 | **Status**: [ ] not started
**Test**: Given homepage loads → When user scrolls to Showcase → Then production app cards and stats row render

### T-003: Create TopSkillsSection component
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [ ] not started
**Test**: Given homepage loads → When user scrolls to Top Skills → Then 8 skill cards render with CTA to verified-skill.com

## Phase 2: Homepage Assembly

### T-004: Update HeroSection messaging
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [ ] not started
**Test**: Given homepage loads → When hero renders → Then headline is "Stop Prompting. Start Specifying." and badge bar shows 4 metrics
**Dependencies**: None

### T-005: Restructure index.tsx section order
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02 | **Status**: [ ] not started
**Test**: Given homepage loads → When all sections render → Then 9 sections appear in correct order and removed sections are absent
**Dependencies**: T-001, T-002, T-003, T-004

### T-006: Verify Docusaurus build
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [ ] not started
**Test**: Given all components updated → When `npm run build` executes → Then build completes without errors
**Dependencies**: T-005

## Phase 3: README Rewrite

### T-007: Rewrite GitHub README.md
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04, AC-US6-05, AC-US6-06 | **Status**: [ ] not started
**Test**: Given README is rewritten → When rendered on GitHub → Then badges display, comparison table renders, quickstart has 5 lines or fewer

## Phase 4: Docs Enhancement

### T-008: Add mermaid diagrams to hierarchy-mapping.md
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04 | **Status**: [ ] not started
**Test**: Given hierarchy-mapping.md updated → When rendered in Docusaurus → Then 4 mermaid diagrams render correctly

### T-009: Create metadata-reference.md
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-02, AC-US8-03 | **Status**: [ ] not started
**Test**: Given metadata-reference.md created → When built by Docusaurus → Then page renders with all field documentation

### T-010: Update sidebars.ts
**User Story**: US-008 | **Satisfies ACs**: AC-US8-04 | **Status**: [ ] not started
**Test**: Given sidebar updated → When navigating Reference section → Then metadata-reference appears in sidebar
**Dependencies**: T-009

## Phase 5: Verification

### T-011: Full build and verification
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [ ] not started
**Test**: Given all changes complete → When `npm run build` executes → Then build passes, no broken links, all sections render
**Dependencies**: T-006, T-007, T-008, T-010

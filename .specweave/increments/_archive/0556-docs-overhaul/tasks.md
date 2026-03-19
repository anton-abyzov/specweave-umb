---
increment: 0556-docs-overhaul
title: "Documentation Site Overhaul"
generated: 2026-03-17
---

# Tasks: Documentation Site Overhaul

## Phase 1: Scripted Prefix Replacement

### T-001: Replace all /specweave: prefix instances with /sw:
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01
**Status**: [x] Completed
**Test**: Given `docs/` contains 784 `/specweave:` instances across 90 files → When `sed -i '' 's|/specweave:|/sw:|g'` runs against all `.md`/`.mdx` files → Then `grep -r '/specweave:' docs/ --include='*.md' --include='*.mdx' | wc -l` returns 0 and `npx docusaurus build` exits 0

---

## Phase 2: File Deletion

### T-002: Delete non-documentation files (scripts/, YouTube scripts, audit docs, Kafka tutorials)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01
**Status**: [x] Completed
**Test**: Given `docs/scripts/`, `docs/DOCUMENTATION-AUDIT-2025-11-25.md`, `docs/DOCUMENTATION-RESTRUCTURE-PLAN.md`, three `youtube-tutorial-script*.md` files, and four `kafka-*.md` guides exist → When all are deleted and sidebar references removed → Then `find docs/ \( -name 'DOCUMENTATION-*' -o -name 'youtube-tutorial*' -o -name 'kafka-*' \) | wc -l` returns 0 and `npx docusaurus build` exits 0

### T-003: Delete duplicate root files and learn/ directory; update sidebars.ts
**User Story**: US-002, US-003 | **Satisfies ACs**: AC-US2-01, AC-US3-03
**Status**: [x] Completed
**Test**: Given `docs/intro.md`, `docs/quick-start.md`, `docs/features.md`, and entire `docs/learn/` (10 files) exist with `learnSidebar` defined in sidebars.ts → When all are deleted and `learnSidebar` removed from sidebars.ts → Then `[ -d docs/learn ]` returns false, `grep 'learnSidebar' sidebars.ts` returns empty, and `npx docusaurus build` exits 0

### T-004: Prune glossary to ~20 SpecWeave-specific terms
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-02
**Status**: [x] Completed
**Test**: Given the glossary directory contains ~83 files including generic terms (api.md, cli.md, docker.md, react.md, kubernetes.md, terraform.md, etc.) → When ~63 generic term files are deleted and each retained entry contains term, one-sentence definition, and a link to a relevant docs page → Then `ls docs/glossary/terms/ | wc -l` returns ≤ 22 and `npx docusaurus build` exits 0

---

## Phase 3: Ghost Plugin / Command Removal + Statistics Reconciliation

### T-005: Remove ghost plugin references from all docs pages
**User Story**: US-002, US-004 | **Satisfies ACs**: AC-US2-02, AC-US4-01, AC-US4-03
**Status**: [x] Completed
**Test**: Given 12 ghost plugins are referenced across docs and the canonical plugin list is 13 (8 SpecWeave core + 5 vskill) → When non-existent plugin references are removed or corrected → Then every documented plugin entry includes name, description, skill count, and install status, and `npx docusaurus build` exits 0

### T-006: Remove ghost command references from all docs pages
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03
**Status**: [x] Completed
**Test**: Given 9 ghost CLI commands are referenced in docs → When each command reference is cross-checked against `specweave --help` output and non-existent commands are removed → Then zero docs pages reference an unimplemented CLI command and `npx docusaurus build` exits 0

### T-007: Rewrite plugins-ecosystem page and fix all numeric statistics
**User Story**: US-004, US-005 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US5-01, AC-US5-02, AC-US5-03
**Status**: [x] Completed
**Test**: Given docs claim 19-24 plugins and 100-136 skills across multiple pages → When `docs/overview/plugins-ecosystem.md` is rewritten to state 13 plugins / ~48 built-in skills / 99,680+ community skills, and all other occurrences are updated to match → Then `grep -rn '\b\(19\|24\|100\|136\)\s*plugin' docs/ --include='*.md' | wc -l` returns 0 and `npx docusaurus build` exits 0

### T-008: Fix plugin naming consistency and stale frontend: skill references
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03
**Status**: [x] Completed
**Test**: Given plugin names use inconsistent casing and 25+ stale `frontend:` skill references exist → When all plugin names are normalized to match the canonical registry and each `frontend:` reference maps to a valid skill or is replaced with a deprecation note → Then `grep -rn 'frontend:' docs/ --include='*.md' | wc -l` returns ≤ 5 (only valid references remain) and `npx docusaurus build` exits 0

---

## Phase 4: Content Consolidation + Redirect Map

### T-009: Merge getting-started pages into single canonical page
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01
**Status**: [x] Completed
**Test**: Given 5 getting-started pages exist (`getting-started/index.md`, `guides/getting-started/quickstart.md`, `guides/getting-started/installation.md`, `guides/getting-started/nvm-global-packages-fix.md`, and the already-queued `quick-start.md`) → When content is merged into `getting-started/index.md`, non-canonical files deleted, and sidebar updated → Then exactly 1 getting-started page exists and `npx docusaurus build` exits 0

### T-010: Merge remaining duplicate page groups
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02
**Status**: [x] Completed
**Test**: Given duplicate groups exist (compliance 3 pages, cost-tracking 3 pages, living-docs 3 pages, extensible-skills 4 pages, agent-teams 2 pages, sync 4 pages, external-tools 3 pages) → When each group is merged into its canonical target (per plan.md Phase 4 table), non-canonical files deleted, and sidebars.ts updated → Then each topic has exactly 1 canonical page and `npx docusaurus build` exits 0

### T-011: Build complete redirect map in docusaurus.config.ts
**User Story**: US-009 | **Satisfies ACs**: AC-US9-01, AC-US9-02, AC-US9-03
**Status**: [x] Completed
**Test**: Given pages were deleted and merged across Phases 2-4 → When all removed URLs (learn/*, merged non-canonical pages, deleted root files, deleted glossary generic terms, deleted kafka/youtube files) are added as redirect entries in `@docusaurus/plugin-client-redirects` config → Then every `from` path in the redirect array no longer exists as a file in `docs/`, every `/docs/learn/*` path redirects to `/docs/academy/fundamentals/*` or `/docs/academy`, and `npx docusaurus build` exits 0

---

## Phase 5: Sidebar Restructure and Page Template

### T-012: Restructure sidebars.ts to 9 top-level categories; update navbar and footer labels
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02
**Status**: [x] Completed
**Test**: Given sidebars.ts defines 11 sidebars and the footer label reads "Skills Reference (100+)" → When sidebars.ts is rewritten to 6 sidebars with docsSidebar containing exactly 9 top-level categories at max 2 depth, and the footer label is updated to "Skills Reference (~48)" → Then `grep -c '"label"' sidebars.ts` top-level count equals 9 for docsSidebar, no item nests deeper than 2 levels, and `npx docusaurus build` exits 0

### T-013: Create page template file and document contribution convention
**User Story**: US-006 | **Satisfies ACs**: AC-US6-03
**Status**: [x] Completed
**Test**: Given no enforced page template exists → When `docs/_page-template.md` is created with the structure Title (h1) > Subtitle (frontmatter description) > Intro paragraph > Sections (h2/h3) > Next Steps, and the convention is noted in CONTRIBUTING.md → Then `[ -f docs/_page-template.md ]` returns true and the file contains all five structural elements and `npx docusaurus build` exits 0

---

## Phase 6: CSS and Design Fixes

### T-014: Scope CSS transitions and add footer CSS custom property overrides
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02
**Status**: [x] Completed
**Test**: Given `custom.css` applies a `transition` rule on the `*` selector causing page-load layout shift, and the footer uses hardcoded dark colors → When the `*` block is replaced with a scoped selector list (a, button, .navbar, .menu__link, etc.) and `.footer--dark` overrides are added using `--sw-*` CSS custom properties → Then `grep -n '^\* {' src/css/custom.css` returns empty, `grep 'footer--dark' src/css/custom.css` returns the override block, and `npx docusaurus build` exits 0

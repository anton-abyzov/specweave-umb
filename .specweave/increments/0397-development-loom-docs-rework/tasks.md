# Tasks: Development Loom Documentation Site Rework — Phase 1

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Design Token System

### T-001: Create CSS design token system
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: Given tokens.css exists → When loaded → Then all --sw-* variables defined for light and dark mode
- Create `src/css/tokens.css` with refined indigo-purple palette (primary-500: #6b58b8)
- Define semantic colors, neutral grays, typography (Inter + JetBrains Mono), spacing, radius, shadows
- Full dark mode overrides via `[data-theme='dark']`
- Map to Infima `--ifm-*` variables

### T-002: Refactor custom.css to use tokens
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test**: Given custom.css → When inspected → Then no hard-coded color values, all use var(--sw-*)
- Replace ~40+ hard-coded color values with token references
- Remove ~600 lines homepage-specific CSS
- Keep: navbar, cards, links, code blocks, tables, mermaid, admonitions

### T-003: Add Inter font
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed
**Test**: Given page loads → When inspecting body → Then font-family includes Inter
- Add Google Fonts link in `docusaurus.config.ts` headTags
- Add preconnect for fonts.gstatic.com

## Phase 2: Custom MDX Components

### T-004: Create MDXComponents provider
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [x] completed
**Test**: Given any MDX page → When using <Note> → Then component renders without import
- Create `src/theme/MDXComponents.tsx` re-exporting defaults + custom components

### T-005: Build Callout components
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test**: Given <Note title="X">content</Note> → Then renders icon, title, content with blue accent
- Create `src/components/Callouts/index.tsx` + `Callouts.module.css`
- Note (blue), Tip (purple), Warning (amber), Info (blue) variants

### T-006: Build Steps and CardGroup components
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test**: Given <Steps><Step title="X">content</Step></Steps> → Then renders numbered steps with connector
- Create `src/components/Steps/` with CSS counter pattern
- Create `src/components/CardGroup/` with responsive grid

### T-007: Build Accordion component
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] completed
**Test**: Given <Accordion title="X">content</Accordion> → Then renders collapsible with chevron animation
- Native details/summary for a11y
- Chevron rotation on open

## Phase 3: Admonitions & Search

### T-008: CSS-only admonition override
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test**: Given :::tip block → Then renders with 3px left border, tinted bg, rounded corners
- Override `.theme-admonition` variants in custom.css
- No component swizzle needed

### T-009: Install local search with Cmd+K
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [ ] not started
**Test**: Given Cmd+K pressed → When typing → Then search modal shows results from docs and blog
- Install `@easyops-cn/docusaurus-search-local`
- Configure in docusaurus.config.ts as theme
- Style search modal in custom.css
**Dependencies**: None

## Phase 4: Homepage & Cleanup

### T-010: Strip competing intro.md
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04 | **Status**: [ ] not started
**Test**: Given /docs/intro visited → Then redirects to /docs/overview/introduction
- Strip `docs/intro.md` from 349→~30 lines
- Add redirect in client-redirects config

### T-011: Rework homepage with Loom metaphor
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02 | **Status**: [ ] not started
**Test**: Given homepage loaded → Then shows "The Development Loom" subtitle, design tokens
- Update hero with Loom subtitle
- Use design tokens for all colors
- Use frontend designer skill for professional polish

### T-012: Delete unused HomepageFeatures
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [ ] not started
**Test**: Given src/components/HomepageFeatures/ → Then directory does not exist
- Delete `src/components/HomepageFeatures/` (unused)

## Phase 5: Verification

### T-013: Build verification and visual QA
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02 | **Status**: [ ] not started
**Test**: Given `npm run build` → Then zero errors, dark mode works, search works
- Run build
- Verify: homepage, dark mode, Cmd+K search, admonitions, Inter font
- Check /docs/intro redirect

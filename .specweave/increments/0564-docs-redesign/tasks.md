# Tasks: Redesign Verified Skill Documentation

**Increment**: 0564-docs-redesign
**Project**: vskill-platform
**Test Mode**: TDD | Coverage Target: 90%

## AC Reference (derived from plan.md)

- **AC-US1-01**: `docs/nav.ts` exports typed `DOCS_NAV` constant with all 4 sections and 7 items
- **AC-US1-02**: `docs/layout.tsx` wraps all `/docs/**` routes via Next.js App Router layout
- **AC-US1-03**: `DocsLayout.tsx` renders three-column CSS grid (sidebar 240px + 1fr + TOC 200px)
- **AC-US1-04**: Sidebar shows active page indicator via `usePathname()` comparison
- **AC-US1-05**: Sidebar sections are collapsible with `defaultOpen` state from nav config
- **AC-US1-06**: TOC is auto-generated from `h2[id]` and `h3[id]` in rendered page via DOM query
- **AC-US1-07**: TOC scroll-spy highlights active heading using `IntersectionObserver`
- **AC-US1-08**: Mobile (<768px) sidebar becomes hamburger overlay; TOC is hidden
- **AC-US1-09**: Tablet (768-1080px) TOC column is hidden; two-column grid remains
- **AC-US2-01**: `DocCard` component renders title, description, href, optional badge with arrow
- **AC-US2-02**: `StepList` component renders numbered steps with vertical connecting line
- **AC-US2-03**: `TabGroup` component renders tab strip and shows only active tab's children
- **AC-US3-01**: `docs/page.tsx` redesigned to use `DocCard` components for all section links
- **AC-US3-02**: `docs/getting-started/page.tsx` has heading IDs and uses shared components; no inline breadcrumb
- **AC-US3-03**: `docs/security-guidelines/page.tsx` has heading IDs and uses shared components; no inline breadcrumb
- **AC-US4-01**: `docs/cli-reference/page.tsx` page exists with full command reference content
- **AC-US4-02**: `docs/plugins/page.tsx` page exists with plugin system documentation
- **AC-US4-03**: `docs/submitting/page.tsx` page exists with submission guide using `StepList`
- **AC-US4-04**: `docs/faq/page.tsx` page exists with FAQ content
- **AC-US5-01**: All CSS classes for sidebar/TOC hover+active states added to `globals.css`
- **AC-US5-02**: Responsive breakpoints at 1080px and 768px produce correct layout shifts
- **AC-US5-03**: All docs pages pass visual QA — no layout overflow or broken styles

---

## US-001: Docs Infrastructure (Navigation Config + Layout Shell)

**As a** developer navigating the docs site
**I want** a persistent sidebar and TOC that wrap all documentation pages
**So that** I can orient myself and navigate without full page reloads

---

### T-001: Create navigation config (`docs/nav.ts`)

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01
**Status**: [ ] Not Started
**Test**: Given the nav config module is imported → When `DOCS_NAV` is accessed → Then it exports an array of 4 `NavSection` objects containing exactly 7 nav items with correct `href`, `title`, and `badge` fields

**Implementation**:
- Create `repositories/anton-abyzov/vskill-platform/src/app/docs/nav.ts`
- Export `NavItem` and `NavSection` TypeScript interfaces
- Export `DOCS_NAV` constant matching the structure in `plan.md` AD-4
- Include badge `"v0.4.16"` on Getting Started item

---

### T-002: Add CSS classes for docs layout to `globals.css`

**User Story**: US-001 | **Satisfies ACs**: AC-US5-01, AC-US5-02
**Status**: [ ] Not Started
**Test**: Given the globals.css file is loaded → When a sidebar link has class `docs-sidebar-link active` → Then it receives `font-weight: 600` and `background-color: var(--bg-hover)`; and when viewport is <768px the `.docs-hamburger` is visible and `.docs-sidebar-col` is hidden

**Implementation**:
- Append to `repositories/anton-abyzov/vskill-platform/src/app/globals.css`
- Add `.docs-sidebar-link`, `.docs-sidebar-link:hover`, `.docs-sidebar-link.active`
- Add `.docs-toc-link`, `.docs-toc-link:hover`, `.docs-toc-link.active`
- Add `.docs-sidebar-section`, `.docs-sidebar-section:hover`
- Add `@media (max-width: 1080px)` — hide `.docs-toc-col`, two-column grid
- Add `@media (max-width: 768px)` — hide `.docs-sidebar-col`, single column, show `.docs-hamburger`

---

### T-003: Create `DocsLayout.tsx` (client component)

**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07, AC-US1-08, AC-US1-09
**Status**: [ ] Not Started
**Test**: Given `DocsLayout` renders with a child page containing `<h2 id="intro">` and `<h2 id="usage">` → When the component mounts → Then the right TOC column lists both headings; and when the current pathname matches a nav item's `href` → Then that item receives the `active` CSS class

**Implementation**:
- Create `repositories/anton-abyzov/vskill-platform/src/app/docs/DocsLayout.tsx` with `"use client"`
- CSS grid: `grid-template-columns: 240px minmax(0, 1fr) 200px` with class `docs-grid`
- Sidebar: render `DOCS_NAV` sections, each section collapsible via `sectionState` record
- Active link: use `usePathname()` to compare against each item's `href`
- TOC: `useEffect` on mount — `querySelectorAll('h2[id], h3[id]')` in content area; build `tocItems` state array
- TOC scroll-spy: `IntersectionObserver` updates `activeHeading` string state
- Mobile: hamburger button with `display: none` default, overlay sidebar at <768px breakpoint
- Apply `.docs-sidebar-link`, `.docs-toc-link` classes from T-002

---

### T-004: Create `docs/layout.tsx` (server layout wrapper)

**User Story**: US-001 | **Satisfies ACs**: AC-US1-02
**Status**: [ ] Not Started
**Test**: Given a request to any `/docs/**` route → When Next.js resolves the layout chain → Then `DocsLayout` wraps the page content (sidebar and TOC columns are present in the HTML response)

**Implementation**:
- Create `repositories/anton-abyzov/vskill-platform/src/app/docs/layout.tsx`
- Server component (no `"use client"`)
- Import and render `<DocsLayout>{children}</DocsLayout>`
- Export default `Layout` function accepting `{ children: React.ReactNode }`

---

## US-002: Shared Documentation Components

**As a** developer authoring docs pages
**I want** reusable `DocCard`, `StepList`, and `TabGroup` components
**So that** pages share consistent visual patterns without duplicating markup

---

### T-005: Create `DocCard` component

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01
**Status**: [ ] Not Started
**Test**: Given `<DocCard title="CLI Reference" description="All commands" href="/docs/cli-reference" badge="NEW" />` → When rendered → Then the output contains an anchor with `href="/docs/cli-reference"`, the title text, description text, a badge element with text "NEW", and a right-arrow indicator

**Implementation**:
- Create `repositories/anton-abyzov/vskill-platform/src/components/DocCard.tsx`
- Server component (no `"use client"`)
- Props: `{ title, description, href, badge?, badgeColor? }`
- Use `.doc-card` CSS class (already in globals.css) for hover state
- Render badge only when `badge` prop is defined
- Include right-arrow (`→` or SVG) at trailing edge

---

### T-006: Create `StepList` component

**User Story**: US-002 | **Satisfies ACs**: AC-US2-02
**Status**: [ ] Not Started
**Test**: Given `<StepList steps={[{title:"Install", content:<p>run npm</p>}, {title:"Configure", content:<p>edit config</p>}]} />` → When rendered → Then the output contains exactly 2 step blocks, each with a numbered circle (1, 2), a title, and its content; and a vertical connecting line element is present

**Implementation**:
- Create `repositories/anton-abyzov/vskill-platform/src/components/StepList.tsx`
- Server component (no `"use client"`)
- Props: `{ steps: Array<{ title: string; content: React.ReactNode }> }`
- Render numbered circles with `var(--text-faint)` border
- Render vertical line behind circles (absolutely positioned pseudo-element or inline div)
- Monospace font, terminal aesthetic matching existing components

---

### T-007: Create `TabGroup` component

**User Story**: US-002 | **Satisfies ACs**: AC-US2-03
**Status**: [ ] Not Started
**Test**: Given `<TabGroup tabs={["npm", "yarn"]}><div>npm content</div><div>yarn content</div></TabGroup>` → When the "yarn" tab button is clicked → Then only the yarn content child is visible and the "yarn" tab button has `border-bottom: 2px solid var(--text)`; initially the first tab is active

**Implementation**:
- Create `repositories/anton-abyzov/vskill-platform/src/components/TabGroup.tsx` with `"use client"`
- Props: `{ tabs: string[]; children: React.ReactNode[] }`
- State: `activeIndex: number` defaulting to 0
- Tab strip: horizontal buttons, active tab gets `border-bottom: 2px solid var(--text)`
- Inactive tabs use `color: var(--text-muted)`
- Render only `children[activeIndex]`
- Monospace font consistent with design system

---

## US-003: Redesigned Existing Pages

**As a** developer reading existing documentation
**I want** the getting-started, security-guidelines, and index pages to use the new shared components and layout
**So that** all docs pages have consistent navigation and component usage

---

### T-008: Redesign `docs/page.tsx` (docs index)

**User Story**: US-003 | **Satisfies ACs**: AC-US3-01
**Status**: [ ] Not Started
**Test**: Given a request to `/docs` → When the page renders → Then `DocCard` components are used for all section links (no inline card markup), and the page content uses `DOCS_NAV` sections as organizational reference

**Implementation**:
- Edit `repositories/anton-abyzov/vskill-platform/src/app/docs/page.tsx`
- Replace inline card markup with `<DocCard>` components
- Remove any inline breadcrumb or nav that duplicates `DocsLayout`'s sidebar
- Add `id` attributes to section headings for TOC compatibility
- Export `metadata` with appropriate title and description

---

### T-009: Migrate `docs/getting-started/page.tsx`

**User Story**: US-003 | **Satisfies ACs**: AC-US3-02
**Status**: [ ] Not Started
**Test**: Given a request to `/docs/getting-started` → When the page renders → Then all `h2` and `h3` elements have `id` attributes matching their heading text (slugified), no inline breadcrumb or standalone nav element exists, and existing `CodeBlock`/`Callout` components are preserved

**Implementation**:
- Edit `repositories/anton-abyzov/vskill-platform/src/app/docs/getting-started/page.tsx`
- Add `id` attributes to all `<h2>` and `<h3>` headings
- Remove any inline breadcrumb nav markup (now handled by `DocsLayout`)
- Keep existing `CodeBlock`, `Callout`, `TerminalBlock` usages unchanged
- Export `metadata` with title and description

---

### T-010: Migrate `docs/security-guidelines/page.tsx`

**User Story**: US-003 | **Satisfies ACs**: AC-US3-03
**Status**: [ ] Not Started
**Test**: Given a request to `/docs/security-guidelines` → When the page renders → Then all `h2` and `h3` elements have `id` attributes, no inline breadcrumb nav exists, and `VerdictBadge`/`SeverityBadge` components are preserved

**Implementation**:
- Edit `repositories/anton-abyzov/vskill-platform/src/app/docs/security-guidelines/page.tsx`
- Add `id` attributes to all `<h2>` and `<h3>` headings
- Remove any inline breadcrumb nav markup
- Preserve existing `VerdictBadge`, `SeverityBadge`, `Callout` usages
- Export `metadata` with title and description

---

## US-004: New Documentation Pages

**As a** developer evaluating or using Verified Skill
**I want** dedicated pages for CLI reference, plugins, submitting skills, and FAQ
**So that** I can find authoritative information without searching external sources

---

### T-011: Create `docs/cli-reference/page.tsx`

**User Story**: US-004 | **Satisfies ACs**: AC-US4-01
**Status**: [ ] Not Started
**Test**: Given a request to `/docs/cli-reference` → When the page renders → Then the page contains sections for `vskill install`, `vskill list`, `vskill remove`, and `vskill update` commands, each with a `<CodeBlock>` showing usage syntax, and all `h2` elements have `id` attributes

**Implementation**:
- Create `repositories/anton-abyzov/vskill-platform/src/app/docs/cli-reference/page.tsx`
- Server component; export `metadata`
- Use `<CodeBlock>` for command syntax examples (language `"bash"`)
- Use `<Callout>` for tips/warnings
- Add `id` to all `<h2>` and `<h3>` headings for TOC
- Cover: install, list, remove, update, info, search commands

---

### T-012: Create `docs/plugins/page.tsx`

**User Story**: US-004 | **Satisfies ACs**: AC-US4-02
**Status**: [ ] Not Started
**Test**: Given a request to `/docs/plugins` → When the page renders → Then the page contains a section explaining the plugin system, at least one `<TabGroup>` showing install commands for different package managers, and a `<DocCard>` grid linking to related pages

**Implementation**:
- Create `repositories/anton-abyzov/vskill-platform/src/app/docs/plugins/page.tsx`
- Server component; export `metadata`
- Use `<TabGroup>` for npm/yarn/pnpm install tabs
- Document: what plugins are, how to discover them, how they activate
- Use `<CodeBlock>` for code examples, `<Callout>` for notes
- Add heading `id` attributes throughout

---

### T-013: Create `docs/submitting/page.tsx`

**User Story**: US-004 | **Satisfies ACs**: AC-US4-03
**Status**: [ ] Not Started
**Test**: Given a request to `/docs/submitting` → When the page renders → Then a `<StepList>` component is present with at least 4 steps covering the submission workflow (prepare, test, submit, review), and each step has a title and descriptive content

**Implementation**:
- Create `repositories/anton-abyzov/vskill-platform/src/app/docs/submitting/page.tsx`
- Server component; export `metadata`
- Use `<StepList>` as the primary content structure
- Steps: prepare skill, write tests, run security check, submit via CLI, await review
- Use `<Callout>` for requirements/warnings
- Add heading `id` attributes for TOC

---

### T-014: Create `docs/faq/page.tsx`

**User Story**: US-004 | **Satisfies ACs**: AC-US4-04
**Status**: [ ] Not Started
**Test**: Given a request to `/docs/faq` → When the page renders → Then the page contains at least 6 question/answer pairs organized under `h2` sections, each `h2` has an `id` attribute, and the page includes a `<Callout>` pointing users to the support channel

**Implementation**:
- Create `repositories/anton-abyzov/vskill-platform/src/app/docs/faq/page.tsx`
- Server component; export `metadata`
- Organize Q&A under `h2` sections with `id` attributes
- Cover: pricing, skill compatibility, update cadence, security review process, private skills, support
- Use `<Callout variant="info">` at bottom with support link

---

## US-005: Visual QA and Responsive Polish

**As a** user on any screen size
**I want** the docs layout to display correctly on desktop, tablet, and mobile
**So that** the documentation is readable and navigable on all devices

---

### T-015: Responsive layout verification and fix pass

**User Story**: US-005 | **Satisfies ACs**: AC-US5-02, AC-US5-03
**Status**: [ ] Not Started
**Test**: Given the docs site running locally → When viewport is resized to 1200px, 900px, and 375px → Then at 1200px all three columns are visible; at 900px the TOC column is hidden and sidebar remains; at 375px the sidebar is hidden and a hamburger button is visible; no horizontal overflow occurs at any breakpoint

**Implementation**:
- Start dev server and verify all pages at three breakpoints
- Fix any overflow issues in `DocsLayout.tsx` or `globals.css`
- Confirm hamburger opens/closes sidebar overlay without body scroll escape
- Confirm TOC scroll-spy activates correct heading on scroll
- Confirm active sidebar link updates on navigation between docs pages

---

### T-016: End-to-end navigation smoke test

**User Story**: US-005 | **Satisfies ACs**: AC-US1-02, AC-US1-04, AC-US5-03
**Status**: [ ] Not Started
**Test**: Given the docs site is running → When a user clicks each of the 7 nav items in the sidebar → Then each target page loads without error, the sidebar active indicator moves to the clicked item, the TOC populates with that page's headings, and the breadcrumb trail reflects the current page's section

**Implementation**:
- Write Playwright E2E test at `repositories/anton-abyzov/vskill-platform/e2e/docs-navigation.spec.ts`
- Test: visit `/docs`, click each sidebar link, assert URL changes and active class updates
- Test: on `/docs/getting-started`, verify TOC items match page `h2` headings
- Test: resize to mobile, open hamburger, click a link, assert sidebar closes and page navigates
- Run: `npx playwright test e2e/docs-navigation.spec.ts`

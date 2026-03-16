---
increment: 0477-homepage-studio-nav-redesign
generated_by: sw:test-aware-planner
test_mode: TDD
coverage_target: 90
by_user_story:
  US-001: [T-001, T-002]
  US-002: [T-003, T-004]
  US-003: [T-005, T-006]
  US-004: [T-007]
  US-005: [T-008, T-009, T-010]
  US-006: [T-011]
  US-007: [T-012, T-013]
---

# Tasks — 0477 Homepage Simplification, Studio Landing Page, and Navigation Restructure

## User Story: US-001 — Shared VideoPlayer Component

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Tasks**: 2 total, 0 completed

---

### T-001: Create VideoPlayer component with play/pause overlay and eager/lazy loading

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed

**Test Plan**:
- **Given** a VideoPlayer rendered with `mp4`, `webm`, and `ariaLabel` props with default lazy mode
- **When** the component mounts
- **Then** a `<video>` element has `autoPlay`, `muted`, `loop`, `playsInline`; sources are absent until IntersectionObserver fires; play/pause button with aria-label is rendered; button border uses `accentColor`; `className` applied to wrapper

**Test Plan (eager)**:
- **Given** VideoPlayer with `eager={true}`
- **When** component mounts
- **Then** `<source>` elements for mp4 and webm are present immediately without IntersectionObserver

**Test Plan (cleanup)**:
- **Given** a mounted lazy VideoPlayer
- **When** component unmounts
- **Then** `IntersectionObserver.disconnect` is called

**Test Cases**:
1. **Unit**: `src/app/components/shared/__tests__/VideoPlayer.test.tsx`
   - `rendersVideoElementWithCorrectAttributes()`: video has autoPlay, muted, loop, playsInline; play/pause button present
   - `lazyLoadDoesNotSetSourcesBeforeIntersection()`: sources absent before observer fires; present after entry fires
   - `eagerPropSetsSourcesImmediately()`: sources present on first render when `eager={true}`
   - `accentColorAppliesToButtonBorder()`: button border-color matches prop value
   - `classNameAppliedToWrapper()`: root div has className
   - `disconnectsObserverOnUnmount()`: `disconnect` spy called after `cleanup()`
   - **Coverage Target**: 95%

**Implementation**:
1. Create `src/app/components/shared/VideoPlayer.tsx` as `"use client"` component
2. Define `VideoPlayerProps` (mp4, webm, ariaLabel, accentColor?, className?, eager?)
3. Use `useRef<HTMLVideoElement>` + `useState(isPlaying)`; `useEffect` sets up IntersectionObserver (rootMargin `200px`) or sets sources immediately if `eager`; return disconnect cleanup
4. Render `<video autoPlay muted loop playsInline>` with conditional `<source>` elements; overlay play/pause button with accent border
5. Create `src/app/components/shared/__tests__/VideoPlayer.test.tsx`; mock IntersectionObserver via `vi.hoisted()`

---

### T-002: Create CopyButton shared component

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed

**Test Plan**:
- **Given** a CopyButton rendered with a `command` prop
- **When** the component renders
- **Then** the command text is visible
- **When** the button is clicked
- **Then** `navigator.clipboard.writeText` is called with the command string and "copied" feedback is shown

**Test Cases**:
1. **Unit**: `src/app/components/shared/__tests__/CopyButton.test.tsx`
   - `rendersCommandText()`: command string visible in DOM
   - `clickCallsClipboardWriteText()`: clipboard mock called with correct value
   - `showsCopiedFeedbackAfterClick()`: "copied" indicator appears post-click
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/app/components/shared/CopyButton.tsx` as `"use client"` component
2. Accept `command: string` prop; `useState(copied)` resets via `setTimeout` after 2s
3. Mock `navigator.clipboard.writeText` in tests via `vi.hoisted()`
4. Create `src/app/components/shared/__tests__/CopyButton.test.tsx`

---

## User Story: US-002 — Studio Landing Page

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Tasks**: 2 total, 0 completed

---

### T-003: Create /studio page with hero, video demo, feature cards, and getting-started steps

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed

**Test Plan**:
- **Given** a visitor navigating to `/studio`
- **When** the page renders
- **Then** heading "Skill Studio" is present; the tagline "Test skills with BDD assertions, run benchmarks against any LLM, and track quality over time" is visible; CopyButton for `npx vskill studio` is rendered; VideoPlayer receives `/video/skill-studio.mp4` and `/video/skill-studio.webm`; 4 feature cards (BDD Tests, A/B Compare, Any Model, 100% Local) with correct accent colors are present; 3 getting-started steps with CLI commands are present

**Test Cases**:
1. **Unit**: `src/app/studio/__tests__/page.test.tsx`
   - `rendersHeadingAndTagline()`: "Skill Studio" heading + full tagline text visible
   - `rendersCopyButtonForNpxCommand()`: CopyButton with `npx vskill studio` rendered
   - `rendersVideoPlayerWithStudioSources()`: VideoPlayer receives studio mp4/webm paths
   - `rendersFourFeatureCards()`: BDD Tests, A/B Compare, Any Model, 100% Local all present
   - `rendersThreeGettingStartedSteps()`: 3 numbered step items visible
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/app/studio/page.tsx` as server component (no `"use client"`)
2. Hero: h1 "Skill Studio", tagline paragraph, `<CopyButton command="npx vskill studio" />`
3. Video section: `<VideoPlayer mp4="/video/skill-studio.mp4" webm="/video/skill-studio.webm" ariaLabel="Skill Studio demo" />`
4. Features: 4 cards (BDD Tests/green, A/B Compare/blue, Any Model/purple, 100% Local/cyan)
5. Getting started: 3 numbered steps each with CopyButton
6. Create `src/app/studio/__tests__/page.test.tsx`; mock VideoPlayer and CopyButton via `vi.mock()` + `vi.hoisted()`

---

### T-004: Add SEO metadata export to /studio page

**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [x] completed

**Test Plan**:
- **Given** the /studio page module
- **When** the exported `metadata` object is inspected
- **Then** it contains `title`, `description`, `openGraph.title`, `openGraph.description`, `openGraph.url`, `twitter.title`, `twitter.description`

**Test Cases**:
1. **Unit**: `src/app/studio/__tests__/page.test.tsx` (extended)
   - `exportsMetadataWithTitle()`: `metadata.title` is defined and non-empty
   - `exportsOgAndTwitterFields()`: openGraph and twitter card fields present with correct keys
   - **Coverage Target**: 90%

**Implementation**:
1. Add `export const metadata: Metadata` to `src/app/studio/page.tsx`
2. Include title, description, openGraph (title, description, url), twitter (title, description, card: "summary_large_image")
3. Import `Metadata` from `next`
4. Import and assert `metadata` in the existing studio test file

---

## User Story: US-003 — Navigation Restructure — Desktop

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Tasks**: 2 total, 0 completed

---

### T-005: Update desktop nav to Skills, Studio, Publishers, Trust, Docs — remove Queue and Submit

**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed

**Test Plan**:
- **Given** the root layout rendered
- **When** inspecting the desktop navigation section
- **Then** links Skills, Studio, Publishers, Trust, Docs are present; Queue and Submit links are absent; Studio anchor href is `/studio`

**Test Cases**:
1. **Unit**: `src/app/__tests__/layout.test.tsx`
   - `desktopNavContainsFiveLinks()`: Skills, Studio, Publishers, Trust, Docs present by text
   - `studioLinksToStudioRoute()`: anchor with text "Studio" has href `/studio`
   - `desktopNavDoesNotContainQueueOrSubmit()`: no "Queue" or "Submit" link text in nav
   - **Coverage Target**: 85%

**Implementation**:
1. Open `src/app/layout.tsx`; replace nav link list with: Skills (`/skills`), Studio (`/studio`), Publishers (`/publishers`), Trust (`/trust`), Docs (external)
2. Remove Queue and Submit from nav
3. Create `src/app/__tests__/layout.test.tsx`; mock `SearchPalette` and `MobileNav` via `vi.mock()` + `vi.hoisted()`

---

### T-006: Add Studio to footer; retain Queue and Submit in footer

**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x] completed

**Test Plan**:
- **Given** the root layout rendered
- **When** inspecting the footer
- **Then** a Studio link is present; Queue and Submit links are present; all existing footer links are retained

**Test Cases**:
1. **Unit**: `src/app/__tests__/layout.test.tsx` (extended)
   - `footerContainsStudioLink()`: footer element has link with text "Studio"
   - `footerRetainsQueueAndSubmit()`: footer has "Queue" and "Submit" links
   - **Coverage Target**: 85%

**Implementation**:
1. In `src/app/layout.tsx` footer section, add Studio link (e.g., between Skills and Publishers)
2. Confirm Queue and Submit remain in footer
3. Add footer assertions to `src/app/__tests__/layout.test.tsx`

---

## User Story: US-004 — Navigation Restructure — Mobile

**Linked ACs**: AC-US4-01, AC-US4-02
**Tasks**: 1 total, 0 completed

---

### T-007: Update MobileNav to Skills, Studio, Publishers, Trust, Docs, GitHub — remove Queue and Submit

**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02 | **Status**: [x] completed

**Test Plan**:
- **Given** MobileNav rendered with menu open
- **When** inspecting the link list
- **Then** links appear in order: Skills, Studio, Publishers, Trust, Docs, GitHub; Queue and Submit are absent; Studio href is `/studio`

**Test Plan (close on tap)**:
- **Given** mobile menu is open
- **When** Studio link is clicked
- **Then** close handler is invoked

**Test Cases**:
1. **Unit**: `src/app/components/__tests__/MobileNav.test.tsx`
   - `showsCorrectLinksInOrder()`: six links present with correct text in DOM order
   - `noQueueOrSubmitLinks()`: "Queue" and "Submit" text absent
   - `studioLinkHrefIsCorrect()`: Studio anchor href is `/studio`
   - `tappingStudioLinkClosesMenu()`: close handler called on Studio click
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/app/components/MobileNav.tsx`; update link array: Skills, Studio, Publishers, Trust, Docs, GitHub
2. Remove Queue and Submit entries; ensure each link calls the close handler onClick
3. Create `src/app/components/__tests__/MobileNav.test.tsx`; mock `next/link` via `vi.mock()` + `vi.hoisted()`

---

## User Story: US-005 — Homepage Simplification

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05, AC-US5-06
**Tasks**: 3 total, 0 completed

---

### T-008: Create HeroSearch component with conditional auto-focus and openSearch dispatch

**User Story**: US-005 | **Satisfies ACs**: AC-US5-02, AC-US5-03, AC-US5-04 | **Status**: [x] completed

**Test Plan**:
- **Given** HeroSearch rendered on a non-touch device (`matchMedia('(hover: hover)').matches === true`)
- **When** component mounts
- **Then** the input element receives focus

**Test Plan (touch)**:
- **Given** HeroSearch rendered on a touch device (`matchMedia('(hover: hover)').matches === false`)
- **When** component mounts
- **Then** the input does NOT receive focus

**Test Plan (dispatch)**:
- **Given** the HeroSearch input
- **When** user types a query
- **Then** `openSearch` CustomEvent is dispatched on window with the query detail

**Test Plan (placeholder)**:
- **Given** HeroSearch rendered
- **When** inspecting the input
- **Then** placeholder is "Search 90,000+ verified skills..."

**Test Cases**:
1. **Unit**: `src/app/components/home/__tests__/HeroSearch.test.tsx`
   - `autoFocusesOnNonTouchDevice()`: `document.activeElement` is the input after mount
   - `doesNotAutoFocusOnTouchDevice()`: `document.activeElement` is not the input after mount
   - `dispatchesOpenSearchOnInput()`: `window.dispatchEvent` spy called with `openSearch` CustomEvent
   - `placeholderMatchesSpec()`: input placeholder is "Search 90,000+ verified skills..."
   - **Coverage Target**: 95%

**Implementation**:
1. Create `src/app/components/home/HeroSearch.tsx` as `"use client"` component
2. `useRef<HTMLInputElement>`; `useEffect` checks `window.matchMedia('(hover: hover)').matches`; if true, calls `ref.current?.focus()`
3. `onChange` dispatches `new CustomEvent('openSearch', { detail: { query: value } })` on window
4. Render `<input ref={ref} placeholder="Search 90,000+ verified skills..." />`
5. Mock `window.matchMedia` in tests via `vi.hoisted()` with configurable `matches`
6. Create `src/app/components/home/__tests__/HeroSearch.test.tsx`

---

### T-009: Rewrite homepage page.tsx to search-first layout with agent strip

**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-05, AC-US5-06 | **Status**: [x] completed

**Test Plan**:
- **Given** the homepage rendered
- **When** inspecting the DOM
- **Then** tagline "Install AI skills you can trust" is present; HeroSearch is rendered; CategoryNav and TrendingSkillsSection appear below the hero; compact agent strip with count text and 6 agent icons is visible

**Test Plan (removed sections)**:
- **Given** the homepage rendered
- **When** querying for old section identifiers
- **Then** HomepageDemoHero, role cards, SkillStudioSection, MarketDashboard, full agent badge grid are absent

**Test Cases**:
1. **Unit**: `src/app/__tests__/page.test.tsx`
   - `rendersHeroTagline()`: "Install AI skills you can trust" text present
   - `rendersHeroSearch()`: mocked HeroSearch component present
   - `rendersCategoryNavAndTrending()`: mocked CategoryNav and TrendingSkillsSection present
   - `rendersCompactAgentStrip()`: "Works with" + agent count text visible; 6 agent icon elements present
   - `doesNotRenderRemovedSections()`: HomepageDemoHero, SkillStudioSection, MarketDashboard absent
   - **Coverage Target**: 85%

**Implementation**:
1. Rewrite `src/app/page.tsx` from ~300 to ~100 lines; keep `export const dynamic = "force-dynamic"` and `getHomeStats()` call
2. Hero: compact header ("Install AI skills you can trust" tagline + stat callout), `<HeroSearch />`
3. Below: `<CategoryNav stats={stats} />`, `<TrendingSkillsSection stats={stats} />`
4. Agent strip: "Works with N agents" + first 6 `FEATURED_AGENTS` icons + "+M more" text (inline, ~15 lines)
5. Mock all child components in test; assert agent strip text contains count

---

### T-010: Move FEATURED_AGENTS and MORE_AGENTS to agent-branding lib

**User Story**: US-005 | **Satisfies ACs**: AC-US5-05 | **Status**: [x] completed

**Test Plan**:
- **Given** `@/lib/agent-branding` module
- **When** imported
- **Then** it exports `FEATURED_AGENTS` and `MORE_AGENTS` arrays alongside existing `AGENT_COLORS` and `AGENT_ICONS`

**Test Cases**:
1. **Unit**: `src/lib/__tests__/agent-branding.test.ts`
   - `exportsFeaturedAndMoreAgentsArrays()`: both arrays are non-empty
   - `agentStripMathIsCorrect()`: first 6 from FEATURED_AGENTS used for icons; remaining count derived from arrays
   - **Coverage Target**: 85%

**Implementation**:
1. Open `src/lib/agent-branding.ts`; add exports for `FEATURED_AGENTS` and `MORE_AGENTS` (move from page.tsx or add if absent)
2. Verify `AGENT_COLORS` and `AGENT_ICONS` are already exported
3. Update `src/app/page.tsx` import to pull `FEATURED_AGENTS`, `MORE_AGENTS` from `@/lib/agent-branding`
4. Create `src/lib/__tests__/agent-branding.test.ts`

---

## User Story: US-006 — Homepage SEO Structured Data

**Linked ACs**: AC-US6-01, AC-US6-02
**Tasks**: 1 total, 0 completed

---

### T-011: Add JSON-LD SearchAction structured data to homepage

**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02 | **Status**: [x] completed

**Test Plan**:
- **Given** the homepage rendered
- **When** querying for `<script type="application/ld+json">`
- **Then** the tag exists; parsed JSON has `@type: "WebSite"`, `@context: "https://schema.org"`, `potentialAction.@type: "SearchAction"`, `potentialAction.target.urlTemplate` containing `/skills?q={search_term_string}`, `query-input: "required name=search_term_string"`

**Test Cases**:
1. **Unit**: `src/app/__tests__/page.test.tsx` (extended)
   - `rendersJsonLdScriptTag()`: `script[type="application/ld+json"]` present in DOM
   - `jsonLdContainsWebSiteSchema()`: parsed JSON has `@type: "WebSite"`, `@context`, `name`, `url`
   - `jsonLdSearchActionIsValid()`: `potentialAction.target.urlTemplate` includes `/skills?q={search_term_string}`
   - `jsonLdQueryInputField()`: `query-input` is `"required name=search_term_string"`
   - **Coverage Target**: 90%

**Implementation**:
1. In `src/app/page.tsx`, define `jsonLd` constant per plan AD-6 schema
2. Render `<script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />`
3. Extend `src/app/__tests__/page.test.tsx` to query the script tag, parse its content, and assert all fields

---

## User Story: US-007 — Dead Code Cleanup

**Linked ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04
**Tasks**: 2 total, 0 completed

---

### T-012: Delete HomepageDemoHero, SkillStudioSection, MarketDashboard and remove unused HomeSkeleton exports

**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02 | **Status**: [x] completed

**Test Plan**:
- **Given** cleanup is complete
- **When** checking the filesystem and HomeSkeleton.tsx
- **Then** `HomepageDemoHero.tsx`, `SkillStudioSection.tsx`, and `MarketDashboard.tsx` do not exist; `HomeSkeleton.tsx` no longer exports `HeroStatsSkeleton`, `DashboardSkeleton`, or `InlineStatsSkeleton`

**Test Cases**:
1. **Compiler gate**: `npx tsc --noEmit` exits 0 (no dangling imports)
2. **Regression**: existing test suite passes unchanged
   - **Coverage Target**: N/A (deletion verified by compiler + test suite)

**Implementation**:
1. Confirm `HomepageDemoHero.tsx` has no remaining imports (`grep -r "HomepageDemoHero" src/`); delete file
2. Confirm `SkillStudioSection.tsx` has no remaining imports; delete file
3. Confirm `MarketDashboard.tsx` has no remaining imports; delete `src/app/components/home/MarketDashboard.tsx`
4. Open `src/app/components/home/HomeSkeleton.tsx`; remove `HeroStatsSkeleton`, `DashboardSkeleton`, `InlineStatsSkeleton` exports if no imports found
5. Run `npx tsc --noEmit`; fix any errors before marking done

---

### T-013: Verify full test suite passes and zero TypeScript errors after cleanup

**User Story**: US-007 | **Satisfies ACs**: AC-US7-03, AC-US7-04 | **Status**: [x] completed

**Test Plan**:
- **Given** all cleanup tasks (T-012) are complete
- **When** running `npx tsc --noEmit` then `npx vitest run` from the vskill-platform root
- **Then** TypeScript reports zero errors; all tests pass; no regressions

**Test Cases**:
1. **Integration**: `npx tsc --noEmit` exits 0
2. **Integration**: `npx vitest run` exits 0 with zero failing tests; overall coverage >= 90%
   - **Coverage Target**: 90% overall

**Implementation**:
1. Run `cd repositories/anton-abyzov/vskill-platform && npx tsc --noEmit`; fix any remaining type errors
2. Run `npx vitest run`; address any regressions
3. Mark T-013 complete only after both commands exit 0

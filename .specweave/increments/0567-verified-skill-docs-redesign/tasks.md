---
increment: 0567-verified-skill-docs-redesign
title: "Verified Skill Docs Redesign + Video Learning Section"
generated: 2026-03-18
test_mode: TDD
coverage_target: 90
---

# Tasks: Verified Skill Docs Redesign + Video Learning Section

## Phase 1: Readability (US-001, US-002)

### T-001: Add --surface-* CSS tokens and fix --text-faint in globals.css
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] Completed
**Test**: Given `globals.css` in vskill-platform, when the `:root` block is updated, then `--surface-card` is `#FFFFFF`, `--surface-card-text` is `#111111`, `--surface-dark` aliases the old `--card-bg` value, `--text-faint` resolves to `#767676` (4.54:1 on white), legacy `--card-bg` remains as `var(--surface-dark)` so dark-mode variables are unchanged, and a contrast-ratio assertion test confirms each new token meets WCAG AA (4.5:1 minimum) against its paired background.

**Test Plan**:
- **Unit** (vitest): CSS-parse test reads `globals.css`, extracts hex values for `--surface-card`, `--surface-card-text`, `--text-faint`, asserts contrast ratios using the `wcag-contrast` npm utility.
  - Given `--surface-card: #FFFFFF` + `--surface-card-text: #111111` → assert ratio >= 4.5
  - Given `--text-faint: #767676` on `#FFFFFF` → assert ratio >= 4.5
  - Given `[data-theme="dark"]` block → assert `--surface-card` is still `#161B22` (dark mode unchanged)
- **Integration** (Playwright + axe): Load `/docs/getting-started` in light mode, run `axe-core` against the page, assert zero color-contrast violations.

---

### T-002: Add .prose utility class to globals.css
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] Completed
**Test**: Given `globals.css`, when the `.prose` class is added, then `.prose` sets `font-family: var(--font-geist-sans)` and `font-size: 0.9375rem`, `.prose code` and `.prose pre` override back to `var(--font-geist-mono)`, and a CSS-parse unit test confirms no other existing rule is mutated.

**Test Plan**:
- **Unit** (vitest): CSS-parse test reads `globals.css` and asserts:
  - `.prose` contains `font-family: var(--font-geist-sans)`
  - `.prose` contains `font-size: 0.9375rem`
  - `.prose code` contains `font-family: var(--font-geist-mono)`
  - `.prose pre` contains `font-family: var(--font-geist-mono)`
- **Integration** (Playwright): Load `/docs/getting-started`, query a `<p>` inside `.prose`, call `getComputedStyle`, assert `fontFamily` resolves to a value containing "Geist Sans" and `fontSize` equals "15px".

---

### T-003: Apply .prose wrapper in DocsLayout.tsx
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] Completed
**Test**: Given `DocsLayout.tsx` in vskill-platform, when `{children}` is wrapped in `<div className="prose">`, then a unit snapshot test confirms the wrapper div is present in the rendered output and does not affect sidebar or header elements outside the main content area.

**Test Plan**:
- **Unit** (vitest + RTL): Snapshot of `DocsLayout` — assert rendered output contains `<div class="prose">` wrapping children, sidebar elements are NOT inside `.prose`.
- **Integration** (Playwright): Load `/docs/cli-reference`, assert `document.querySelector('.prose p')` has computed `fontFamily` containing "Geist" (not mono-only).

---

## Phase 2: /learn Hub (US-003, US-004, US-005)

### T-004: Create Video type definitions and helper functions in src/lib/learn/videos.ts
**User Story**: US-003, US-005 | **Satisfies ACs**: AC-US5-01, AC-US3-02
**Status**: [x] Completed
**Test**: Given `src/lib/learn/videos.ts` in vskill-platform, when the `Video` interface and helper functions are defined, then `getVideo("nonexistent")` returns `undefined`, `getVideosByCategory("getting-started")` returns only entries matching that category, and `getFeaturedVideos()` returns a non-empty array when at least one entry carries a featured flag.

**Test Plan**:
- **Unit** (vitest): Import helpers from `videos.ts` with a mock `VIDEOS` array:
  - `getVideo("slug-a")` → returns the entry with `slug === "slug-a"`
  - `getVideo("missing")` → returns `undefined`
  - `getVideosByCategory("cli-deep-dive")` with mixed-category mock → returns only matching entries
  - `getFeaturedVideos()` with zero featured entries → returns `[]`
- **Unit**: TypeScript compilation check — `Video` interface fields are all typed correctly (no `any`).

---

### T-005: Populate video-data.ts with at least 3 published entries and placeholder thumbnails
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-04, AC-US5-05
**Status**: [x] Completed
**Test**: Given `src/lib/learn/video-data.ts`, when the `VIDEOS` array is read, then at least 3 entries have `status: "published"`, each published entry has a `sources.mp4` path under `/video/learn/`, a unit test asserts every entry passes schema validation (no missing required fields), and file-size checks confirm individual MP4s are each under 15 MB and the total `public/video/learn/` directory is under 200 MB.

**Test Plan**:
- **Unit** (vitest): Iterate `VIDEOS`, assert for each entry: `slug` is non-empty string, `title` is non-empty string, `duration` is positive number, `category` is one of the valid `VideoCategory` values, `thumbnail` starts with `/learn/thumbnails/`, `sources.mp4` starts with `/video/learn/`.
- **Unit**: Assert `VIDEOS.filter(v => v.status === "published").length >= 3`.
- **Integration** (Bash in CI): `du -sm public/video/learn/ | awk '$1 > 200 { exit 1 }'` — fails build if over 200 MB. Per-file: `find public/video/learn/ -name "*.mp4" -size +15M | grep . && exit 1 || exit 0`.

---

### T-006: Build VideoCard component (thumbnail, title, duration badge, difficulty indicator)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US5-02, AC-US5-03
**Status**: [x] Completed
**Test**: Given `VideoCard` rendered with a published video's props, when the component mounts, then it displays a `<picture>` with WebP/JPEG sources and non-empty `alt` text, a duration badge formatted as "MM:SS", a difficulty indicator element, and a play overlay button; when the video fails to load, then the card shows "Video unavailable — coming soon" text without throwing.

**Test Plan**:
- **Unit** (vitest + RTL):
  - Render `<VideoCard slug="test" title="Test" thumbnail="/t.webp" duration={154} category="getting-started" difficulty="beginner" status="published" />` → assert `picture` present, `img[alt]` non-empty, text "02:34" present, play button `role="button"` present.
  - Render with `status="coming-soon"` → assert play button NOT present, "Coming Soon" overlay present.
  - Simulate video load error → assert "Video unavailable" text visible.
- **Snapshot** (RTL): Snapshot test for published and coming-soon variants.
- **A11y** (axe): Run axe on rendered card → zero violations (alt text, button roles, focus-visible).

---

### T-007: Build VideoGrid and CategoryFilter components
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02
**Status**: [x] Completed
**Test**: Given `VideoGrid` with a mixed-category `VIDEOS` array and `CategoryFilter` showing tabs "vskill", "SpecWeave", "Workflows", when the "SpecWeave" tab is clicked, then only VideoCard components with `category` matching "specweave-integration" are rendered and other category cards are not in the DOM.

**Test Plan**:
- **Unit** (vitest + RTL):
  - Render `<CategoryFilter activeCategory={null} onSelect={fn} />` → assert three tab buttons render with labels "vskill", "SpecWeave", "Workflows".
  - Click "SpecWeave" tab → assert `onSelect` called with `"specweave-integration"`.
  - Render `<VideoGrid videos={mockVideos} activeCategory="getting-started" />` with 5 items, 2 matching → assert 2 `VideoCard` components rendered.
  - Render with `activeCategory` for which no videos exist → assert "No videos yet" message visible.
- **Integration** (Playwright): Navigate to `/learn`, click "SpecWeave" tab, assert grid shows only SpecWeave-category cards.

---

### T-008: Build /learn page.tsx with SSR, URL-param tab state, and bundle size gate
**User Story**: US-003, US-005 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-04, AC-US3-05
**Status**: [x] Completed
**Test**: Given the `/learn` route, when the page loads with no query params, then all published videos render server-side; when `?category=security` is appended, then only security-category cards render on first paint; the VideoPlayer module is NOT present in the initial JS bundle (confirmed by bundle analysis); and total transferred HTML + CSS + JS is under 200 KB.

**Test Plan**:
- **Unit** (vitest): Test the server component's `searchParams` filtering logic with mock params — `category=getting-started` returns only getting-started videos; no `category` param returns all.
- **Bundle** (next build analysis): Run `ANALYZE=true next build`, assert VideoPlayer chunk is NOT listed in the `/learn` page's initial JS manifest.
- **Performance** (Playwright Lighthouse): Load `/learn`, assert Lighthouse performance score >= 90 and total transferred bytes (HTML + CSS + JS) < 200 KB.
- **Integration** (Playwright): Load `/learn?category=security`, assert only security cards in DOM before any JS interaction.

---

### T-009: Add VideoPlayer lazy-loading via next/dynamic on VideoCard click
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02, AC-US5-03, AC-US3-04
**Status**: [x] completed
**Test**: Given a published VideoCard on `/learn`, when the user clicks the play overlay, then the VideoPlayer component loads dynamically (not present before click), playback begins, and when a video file returns a 404, then the card reverts to showing the thumbnail with "Video unavailable — coming soon" text.

**Test Plan**:
- **Unit** (vitest + RTL): Mock `next/dynamic` to verify VideoCard uses dynamic import for VideoPlayer. Assert VideoPlayer is not rendered on initial mount, only after clicking play.
- **Integration** (Playwright):
  - Load `/learn`, assert no `<video>` element in DOM before click.
  - Click first play button, assert `<video>` element appears within 3 seconds.
  - Mock video src to 404 via route intercept, click play, assert "Video unavailable" fallback visible.

---

### T-010: Build "Coming Soon" overlay with inline email capture form
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-05
**Status**: [x] completed
**Test**: Given a VideoCard with `status: "coming-soon"`, when the component renders, then a "Coming Soon" overlay covers the thumbnail and no play button is shown; when the user clicks "Get Notified", then an email input and submit button appear inline; when the form is submitted with an empty email, then a validation error message is shown and no fetch request is made.

**Test Plan**:
- **Unit** (vitest + RTL):
  - Render `<VideoCard status="coming-soon" ... />` → assert "Coming Soon" text visible, play button absent.
  - Click "Get Notified" → assert email input and submit button appear.
  - Submit with empty input → assert error message visible, `fetch` not called (mock via `vi.fn()`).
  - Submit with invalid email "notanemail" → assert error message visible.
  - Submit with valid email "user@example.com" → assert `fetch` called once with correct payload.

---

### T-011: Build POST /api/learn/notify endpoint with Prisma upsert and SendGrid double opt-in
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03, AC-US4-04, AC-US4-05
**Status**: [x] completed
**Test**: Given a POST to `/api/learn/notify` with `{ email: "user@example.com", videoSlug: "getting-started-101" }`, when the handler runs, then a row is upserted into `video_notifications`, a SendGrid double opt-in email is dispatched, and a 200 response with `{ ok: true }` is returned; when the same email+slug is submitted again, then `{ ok: true, message: "already-subscribed" }` is returned with no duplicate DB row and no second email sent.

**Test Plan**:
- **Unit** (vitest): Mock Prisma client and `@sendgrid/mail.send`. Call handler directly:
  - Valid payload → assert `prisma.videoNotification.upsert` called with correct args, `mail.send` called with double opt-in template.
  - Missing `email` field → assert 400 response.
  - Invalid email format → assert 400 response.
  - Duplicate (same email+slug) → assert `mail.send` NOT called again, 200 with `already-subscribed`.
- **Integration** (Playwright): Form flow on a coming-soon card with a test email → assert 200 from API (use test SendGrid key in CI env).

---

### T-012: Create Remotion TitleCard, PluginBrowse, SpecWeaveWorkflow, SecurityScan scenes
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-04
**Status**: [x] completed
**Test**: Given the four new Remotion scene files registered in `Root.tsx`, when `npx remotion compositions` is run, then composition IDs `Learn101TitleCard`, `Learn101Plugins`, `Learn101SpecWeave`, and `Learn101Security` all appear in the output; when a still is rendered for `Learn101TitleCard`, a `.webp` file is produced with exit code 0 and file size > 0.

**Test Plan**:
- **Unit** (vitest + RTL): Import each scene component and render with default props — assert no thrown errors, root element present.
- **Integration** (Bash): `npx remotion compositions` → assert stdout contains all four composition IDs.
- **Integration** (Bash): `npx remotion still Learn101TitleCard --output /tmp/title-card-test.webp --image-format=webp` → assert exit code 0 and file exists.

---

### T-013: Generate WebP thumbnails and commit to public/learn/thumbnails/
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US3-03
**Status**: [x] completed
**Test**: Given the `generate-thumbnails` npm script, when it runs for each published video entry in `video-data.ts`, then a `.webp` file is created at `public/learn/thumbnails/{slug}.webp` for every published video, each file is between 10 KB and 500 KB, and the script exits with code 0.

**Test Plan**:
- **Unit** (vitest): Test the script's iteration logic with mock `VIDEOS` array — assert it generates the correct `remotion still` command string for each entry including the correct output path.
- **Integration** (Bash): Run `npm run generate-thumbnails` in vskill-platform, assert each expected `.webp` file exists in `public/learn/thumbnails/`, assert each file is a valid WebP (`file -b` output contains "WebP").

---

## Phase 3: IA Restructure (US-006, US-007)

### T-014: Update docs-nav.ts with spec-aligned groups in vskill-platform
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03
**Status**: [x] completed
**Test**: Given `src/app/docs/docs-nav.ts`, when the `DOCS_NAV` array is updated with spec-aligned groups (Overview, Quickstart, Core Concepts, Skills, Workflows, Integrations, Reference, FAQ), then every existing doc URL is still present as an `href` in the nav tree with no URL changes, and a unit test confirms each group label matches the spec hierarchy (not Diataxis names).

**Test Plan**:
- **Unit** (vitest): Import `DOCS_NAV`, flatten all `href` values recursively, assert all 7 existing URLs present: `/docs`, `/docs/getting-started`, `/docs/cli-reference`, `/docs/security-guidelines`, `/docs/plugins`, `/docs/submitting`, `/docs/faq`. Assert top-level `label` values include "Overview", "Tutorials", "How-to Guides", "Reference", "Explanation".
- **Integration** (Playwright): Navigate to each of the 7 doc URLs, assert HTTP 200, assert sidebar visible with at least one group expanded.

---

### T-015: Verify active page highlighting and ancestor group expansion in DocsLayout sidebar
**User Story**: US-006 | **Satisfies ACs**: AC-US6-03
**Status**: [x] completed
**Test**: Given a user on `/docs/cli-reference`, when the sidebar renders, then the "CLI Reference" item has an active highlight applied and the "Reference" parent group is in an expanded state with children visible.

**Test Plan**:
- **Unit** (vitest + RTL): Render `<DocsLayout>` with mocked `usePathname` returning `/docs/cli-reference`, assert the NavItem for "CLI Reference" has `aria-current="page"` or active CSS class, assert the "Reference" group's children container has `display !== "none"`.
- **Integration** (Playwright): Navigate to `/docs/cli-reference`, assert sidebar link for "CLI Reference" has `aria-current="page"`, assert "Reference" group expanded (children visible).

---

### T-016: Add "Related resources" section to doc page footers
**User Story**: US-006 | **Satisfies ACs**: AC-US6-04
**Status**: [x] completed
**Test**: Given a doc page with related resource links configured, when the page renders, then a "Related resources" section appears below main content with at least one link; given a doc page with no related resources configured, then no "Related resources" section is rendered.

**Test Plan**:
- **Unit** (vitest + RTL): Render mock doc page with `relatedResources={[{ label: "FAQ", href: "/docs/faq" }]}` → assert "Related resources" heading and the link present. Render with `relatedResources={[]}` → assert "Related resources" heading absent.
- **Integration** (Playwright): Load `/docs/getting-started`, assert heading containing "Related resources" is visible with at least one link beneath it.

---

### T-017: Update Docusaurus sidebars.ts with Diataxis hierarchy in specweave docs-site
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04
**Status**: [x] completed
**Test**: Given `repositories/anton-abyzov/specweave/docs-site/sidebars.ts`, when the config is updated, then primary sidebar groups are Overview, Quickstart, Core Concepts, Skills, Workflows, Integrations, Reference, FAQ; Academy content appears as a "Learn" top-nav item; all existing page IDs remain in the sidebar tree; `themeConfig.navbar.items` has 4 or fewer items including Docs, Learn, Enterprise, Blog.

**Test Plan**:
- **Unit** (vitest): Parse exported `sidebars` object, flatten all `id` values recursively, load snapshot of all pre-existing doc page IDs, assert every pre-existing ID is still present.
- **Unit**: Parse `themeConfig.navbar.items`, assert `length <= 4`, assert labels include "Docs" and "Learn".
- **Integration** (Bash): Run `yarn build` (or `npm run build`) in `docs-site/`, assert exit code 0 and no "broken link" warnings in build output.

---

### T-018: Run automated link checker to verify zero broken URLs post-restructure
**User Story**: US-006, US-007 | **Satisfies ACs**: AC-US6-02, AC-US7-03
**Status**: [x] completed
**Test**: Given both vskill-platform and specweave docs-site after the IA restructure, when a link checker runs against all internal nav hrefs, then zero 404 responses are returned for any previously-existing doc URL.

**Test Plan**:
- **Integration** (Playwright): For vskill-platform, navigate to each of the 7 doc URLs, assert `response.status() === 200` for each.
- **Integration** (Docusaurus build): Assert `docs-site` build completes with no broken link errors. Run `linkinator` against the built static site if available in CI.

---

## Phase 4: Contextual Video (US-008, US-009, US-010)

### T-019: Add relatedDocs, relatedDocSlug, and specBriefSlug fields to Video interface and data entries
**User Story**: US-008, US-010 | **Satisfies ACs**: AC-US8-01, AC-US10-01, AC-US10-04
**Status**: [x] completed
**Test**: Given `src/lib/learn/videos.ts` with `relatedDocs?: string[]`, `relatedDocSlug?: string`, and `specBriefSlug?: string` on the `Video` interface, and at least one `video-data.ts` entry populated with both fields, then `getRelatedDocsForPage("/docs/getting-started")` returns all video entries whose `relatedDocs` array includes that slug, and a unit test confirms schema validation passes for all entries.

**Test Plan**:
- **Unit** (vitest): Test `getRelatedDocsForPage("/docs/getting-started")` with mock data → returns correct subset.
- **Unit**: Iterate all `VIDEOS` entries, assert any entry with `relatedDocs` contains only valid string paths (starts with "/docs/").
- **Unit**: Assert at least 1 video entry has both `relatedDocSlug` and `specBriefSlug` populated.

---

### T-020: Build RelatedVideos sidebar widget for vskill-platform doc pages
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-02, AC-US8-03, AC-US8-04
**Status**: [x] completed
**Test**: Given a doc page whose slug matches the `relatedDocs` array of two video entries, when the sidebar renders, then a "Related Videos" widget appears with two thumbnail links; clicking a thumbnail navigates to `/learn?play={slug}`; given a doc page with no matching videos, then no "Related Videos" widget is rendered; given a video whose thumbnail fails to load, a text-only fallback link with the video title is shown.

**Test Plan**:
- **Unit** (vitest + RTL):
  - Render `<RelatedVideosWidget docSlug="/docs/getting-started" videos={mockMatchingVideos} />` → assert "Related Videos" heading, 2 thumbnail `<img>` elements, each wrapped in `<a href="/learn?play=...">`.
  - Render with `videos={[]}` → assert component returns `null` (not rendered).
  - Simulate `img` `onError` → assert text fallback link with video title appears.
- **Integration** (Playwright): Load a doc page with related videos configured, assert "Related Videos" widget visible in sidebar. Load a doc page with no related videos, assert widget absent.

---

### T-021: Add "Read More" and depth-layer links to VideoCard and video detail pages
**User Story**: US-010 | **Satisfies ACs**: AC-US10-01, AC-US10-02, AC-US10-03, AC-US10-04
**Status**: [x] completed
**Test**: Given a VideoCard where both `relatedDocSlug` and `specBriefSlug` are set, when the card renders, then a "Read More" link to the doc page and a "View Spec Brief" link are present in the card footer; given a doc page reached from a video link, then a "View Spec Brief" link is present if `specBriefSlug` is set; given the Video → Doc → Spec Brief chain, each page includes a back-link or breadcrumb to the previous layer.

**Test Plan**:
- **Unit** (vitest + RTL):
  - Render `<VideoCard relatedDocSlug="/docs/getting-started" specBriefSlug="/docs/spec-brief" ... />` → assert `<a href="/docs/getting-started">Read More</a>` and `<a href="/docs/spec-brief">View Spec Brief</a>` both present.
  - Render without `relatedDocSlug` → assert "Read More" link absent.
  - Render without `specBriefSlug` → assert "View Spec Brief" link absent.
- **Integration** (Playwright): Load `/learn`, find a card with `relatedDocSlug` set, click "Read More", assert navigation to doc page, assert "View Spec Brief" link present on doc page.

---

### T-022: Build VideoEmbed component for Docusaurus docs-site
**User Story**: US-009 | **Satisfies ACs**: AC-US9-01, AC-US9-02, AC-US9-03, AC-US9-04
**Status**: [x] completed
**Test**: Given `<VideoEmbed src="https://verified-skill.com/video/learn/foo.mp4" thumbnail="https://verified-skill.com/learn/thumbnails/foo.webp" title="Foo" duration={90} />` mounted in a Docusaurus MDX page, when the component mounts, then a thumbnail and play overlay are visible and no `<video>` element is in the DOM; when the play button is clicked, then a `<video src="https://...foo.mp4">` element replaces the thumbnail using a direct `src` attribute (no CORS fetch); when the video src errors, "Video unavailable — coming soon" text is shown with the thumbnail as background.

**Test Plan**:
- **Unit** (vitest + RTL in docs-site package):
  - Render `<VideoEmbed ... />` → assert `<img>` thumbnail visible, `<video>` absent, play button present.
  - Click play → assert `<video>` element present with `src` equal to the full absolute URL.
  - Assert `<video>` uses `src` attribute directly (not `fetch`), so no CORS preflight applies.
  - Simulate video `error` event → assert "Video unavailable" text visible.
- **Integration** (Playwright against Docusaurus dev server): Load a page with `<VideoEmbed>`, assert thumbnail visible, click play, assert `<video>` appears and no console CORS errors.

---

### T-023: Add WebP thumbnail `<picture>` fallback to VideoCard and VideoEmbed
**User Story**: US-003, US-009 | **Satisfies ACs**: AC-US3-03, AC-US9-02
**Status**: [x] completed
**Test**: Given a VideoCard or VideoEmbed component, when the thumbnail markup renders, then it uses a `<picture>` element with `<source type="image/webp">` and an `<img>` fallback with a `.jpg` src, and the `img` element always has a non-empty `alt` attribute.

**Test Plan**:
- **Unit** (vitest + RTL):
  - Render `<VideoCard thumbnail="/learn/thumbnails/foo.webp" title="Foo" ... />` → assert `<picture>` present with `<source type="image/webp" srcSet="...webp">` and `<img src="...jpg">`.
  - Assert `<img alt>` is a non-empty string.
  - Render `<VideoEmbed thumbnail="https://verified-skill.com/learn/thumbnails/foo.webp" ... />` → same `<picture>` assertions.
- **A11y** (axe): Run axe on both rendered components, assert zero "image-alt" violations.

---

### T-024: Add keyboard navigation and focus-visible styles for VideoCard grid
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03
**Status**: [x] Completed
**Test**: Given the VideoCard grid on `/learn`, when a user navigates using only the keyboard, then each VideoCard receives a visible focus ring via `:focus-visible`, pressing Enter on a published card triggers play, and category filter pills are reachable and activatable via keyboard.

**Test Plan**:
- **Unit** (vitest + RTL): Render VideoGrid, simulate Tab keydown, assert focus moves to the first VideoCard `<a>` or `<button>`. Simulate Enter on a card → assert play handler called.
- **A11y** (axe + Playwright): Load `/learn`, run axe-core, assert zero focus-visible or keyboard violations. Use `page.keyboard.press("Tab")` to navigate cards, assert `document.activeElement` moves correctly.

---

### T-025: E2E integration suite verifying all 42 ACs across both repos
**User Story**: US-001 through US-010 | **Satisfies ACs**: AC-US1-01 through AC-US10-04
**Status**: [ ] Not Started
**Test**: Given the full application running locally, when the Playwright E2E suite runs, then every AC scenario in spec.md has a passing test assertion, zero WCAG AA color-contrast violations are reported on doc pages, the `/learn` page Lighthouse score is >= 90, and the link checker reports zero 404s for all existing doc URLs.

**Test Plan**:
- **E2E** (Playwright) organized by user story:
  - US-001: Load `/docs` in light mode, run axe color-contrast check → zero violations.
  - US-002: Load `/docs/getting-started`, assert `.prose p` computed font is Geist Sans at 15px.
  - US-003: Load `/learn`, assert three category tabs; filter by category; assert correct card count; assert `/learn` transferred payload < 200 KB.
  - US-004: Click "Get Notified" on a coming-soon card, submit valid email, assert success confirmation.
  - US-005: Click play on published video card, assert `<video>` loads within 3 s.
  - US-006: Load each of the 7 doc URLs, assert 200 and Diataxis sidebar groups visible; assert active page highlighted.
  - US-007: Build docs-site, assert all sidebar groups and nav items present and build exits 0.
  - US-008: Load a doc page with related videos, assert "Related Videos" widget visible in sidebar.
  - US-009: Load a Docusaurus page with `<VideoEmbed>`, click play, assert no CORS errors in console.
  - US-010: Load `/learn`, click "Read More" on a video card, follow to doc, assert "View Spec Brief" link present.
- **Performance** (Lighthouse CI): Run against `/learn` → assert score >= 90 and total bytes < 200 KB.

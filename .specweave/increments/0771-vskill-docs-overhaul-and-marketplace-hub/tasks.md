---
increment: 0771-vskill-docs-overhaul-and-marketplace-hub
generated: 2026-04-26
total_tasks: 47
phases: 5
---

# Tasks — vskill docs overhaul + marketplace hub

## Phase 1 — Foundations (Track F + Track C, run in parallel)

### T-001: Extend sync-agents-json.cjs to write generated-counts.ts
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/scripts/sync-agents-json.cjs` (modify)
  - `repositories/anton-abyzov/vskill-platform/src/lib/generated-counts.ts` (new, build-generated)
**Test Plan** (BDD, REQUIRED):
  Given `sync-agents-json.cjs` runs against the vskill source tree
  When it completes the prebuild step
  Then `src/lib/generated-counts.ts` exists and exports a `COUNTS` const with exactly 6 typed fields: `agentPlatforms`, `plugins`, `skills`, `scanPatterns`, `vskillVersion`, `specWeaveVersion` — all non-zero, all matching filesystem counts within ±1
**Estimated effort**: M

---

### T-002: Add specWeaveVersion cache logic to count generator
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/scripts/sync-agents-json.cjs` (modify)
  - `repositories/anton-abyzov/vskill-platform/scripts/.specweave-version-cache.json` (new, gitignored)
**Test Plan** (BDD, REQUIRED):
  Given `npm view specweave version` would fail (offline / network down)
  When the prebuild script runs
  Then it reads the cached version from `.specweave-version-cache.json` and writes a valid `specWeaveVersion` field instead of crashing; the cache is refreshed on successful network calls
**Estimated effort**: S

---

### T-003: Replace hardcoded counts in layout.tsx and FeatureAgentEcosystem.tsx
**User Story**: US-006 | **Satisfies ACs**: AC-US6-02
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/layout.tsx` (modify — 3 OG/Twitter strings)
  - `repositories/anton-abyzov/vskill-platform/src/app/components/homepage/FeatureAgentEcosystem.tsx` (modify)
**Test Plan** (BDD, REQUIRED):
  Given `src/lib/generated-counts.ts` exports `COUNTS`
  When `layout.tsx` is built
  Then the OG `og:description` and Twitter card strings reference `COUNTS.scanPatterns` and `COUNTS.agentPlatforms` template literals; no literal "52" or "53" string appears in those three lines
**Estimated effort**: S

---

### T-004: Replace hardcoded counts in docs pages (3 files)
**User Story**: US-006 | **Satisfies ACs**: AC-US6-02
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/docs/page.tsx` (modify)
  - `repositories/anton-abyzov/vskill-platform/src/app/docs/cli-reference/page.tsx` (modify)
  - `repositories/anton-abyzov/vskill-platform/src/app/docs/getting-started/page.tsx` (modify)
**Test Plan** (BDD, REQUIRED):
  Given `generated-counts.ts` is present
  When these three docs pages are rendered
  Then the SpecWeave version badge in `docs/page.tsx` shows `COUNTS.specWeaveVersion`, both version badges in `cli-reference` and `getting-started` show `COUNTS.vskillVersion`; no hardcoded version strings remain in those files
**Estimated effort**: S

---

### T-005: Write vitest unit test for generated-counts script
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/generated-counts.test.ts` (new)
**Test Plan** (BDD, REQUIRED):
  Given a known fixture vskill source directory with 2 plugin dirs, 3 SKILL.md files, and a controlled patterns.ts with 5 `id: "..."` lines
  When the count-generation logic is exercised
  Then `plugins === 2`, `skills === 3`, `scanPatterns === 5`, and `agentPlatforms` matches the TOTAL_AGENTS value in the fixture `agents.json`
**Estimated effort**: S

---

### T-006: Add sync-readme-badges.cjs to vskill repo
**User Story**: US-006 | **Satisfies ACs**: AC-US6-03
**Status**: [ ] pending
**Project**: vskill
**Files**:
  - `repositories/anton-abyzov/vskill/scripts/sync-readme-badges.cjs` (new, ~30 LOC)
**Test Plan** (BDD, REQUIRED):
  Given a fixture `README.md` with shields.io badge URLs containing stale counts (plugins=5, skills=10, agents=40, patterns=30)
  When `node scripts/sync-readme-badges.cjs` runs against the fixture
  Then the badge URLs in the fixture README are rewritten in-place to match the current filesystem counts without altering surrounding markdown
**Estimated effort**: S

---

### T-007: Wire prepublishOnly guard in vskill package.json
**User Story**: US-006 | **Satisfies ACs**: AC-US6-04
**Status**: [ ] pending
**Project**: vskill
**Files**:
  - `repositories/anton-abyzov/vskill/package.json` (modify — prepublishOnly chain)
**Test Plan** (BDD, REQUIRED):
  Given `npm publish --dry-run` is executed in the vskill repo
  When `sync-readme-badges.cjs` has already been run and README.md is clean
  Then the full chain `build → build:eval-ui → sync-readme-badges → git diff --exit-code README.md` exits 0; if README.md is stale, `git diff --exit-code` exits non-zero and publish fails
**Estimated effort**: S

---

### T-008: Sidebar active-state styling in DocsLayout.tsx
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/components/DocsLayout.tsx` (modify — NavLink active styles, lines ~30-60)
**Test Plan** (BDD, REQUIRED):
  Given a user navigates to `/docs/cli-reference`
  When the docs sidebar renders
  Then the "CLI Reference" link has a 2px left border in `var(--code-green)` and a `var(--bg-hover)` background, while all other sidebar links have neither; a Playwright snapshot of `[data-active="true"]` vs `[data-active="false"]` link elements shows visually distinct states
**Estimated effort**: S

---

### T-009: TOC depth-aware indentation in DocsLayout.tsx
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/components/DocsLayout.tsx` (modify — TocItem type + indent logic)
**Test Plan** (BDD, REQUIRED):
  Given a docs page with h2, h3, and h4 headings
  When the TOC renders
  Then h2 items have `padding-left: 0rem`, h3 items `0.75rem`, h4 items `1.5rem`; the `TocItem` type includes `level: 1 | 2 | 3`
**Estimated effort**: S

---

### T-010: TOC IntersectionObserver scroll-spy in DocsLayout.tsx
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/components/DocsLayout.tsx` (modify — TOC component, scroll-spy wiring)
**Test Plan** (BDD, REQUIRED):
  Given a user opens a long docs page and scrolls past the second h2 heading
  When `IntersectionObserver` fires
  Then the TOC item corresponding to that heading gains the 2px `--code-green` left bar and a `transform: translateY()` animation moves the indicator; no `scroll` event listener is registered (verified via Playwright `page.evaluate(() => getEventListeners(window).scroll)` returning empty)
**Estimated effort**: M

---

### T-011: Vitest tests for sidebar and TOC (existing + new)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/components/__tests__/docs-sidebar.test.tsx` (modify — ensure existing passes + add level assertions)
  - `repositories/anton-abyzov/vskill-platform/src/app/__tests__/docs-nav.test.ts` (verify still passes)
**Test Plan** (BDD, REQUIRED):
  Given the existing vitest suite for `docs-sidebar.test.tsx` and `docs-nav.test.ts`
  When `npm run test` executes
  Then both suites pass; additionally a new assertion in `docs-sidebar.test.tsx` verifies that a `TocItem` with `level: 2` receives `padding-left: 0.75rem` in the rendered output
**Estimated effort**: S

---

## Phase 2 — Code visualization (Track D — Shiki backbone)

### T-012: Install Shiki and create singleton highlighter
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/package.json` (modify — add `shiki`)
  - `repositories/anton-abyzov/vskill-platform/src/lib/shiki.ts` (new)
**Test Plan** (BDD, REQUIRED):
  Given the singleton `getShikiHighlighter()` is called twice in the same process
  When both calls resolve
  Then both return the same instance reference (singleton pattern); the highlighter has exactly two themes registered: `github-dark` and `github-light`; no other theme appears in the loaded bundle
**Estimated effort**: S

---

### T-013: Refactor CodeBlock.tsx to use Shiki SSR
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/components/CodeBlock.tsx` (modify)
**Test Plan** (BDD, REQUIRED):
  Given a `<CodeBlock lang="typescript">` wrapping a code snippet with a function declaration
  When the component renders server-side
  Then the output HTML contains `<span>` elements with inline color styles from Shiki tokens; the copy button is still present with its existing `aria-label`; line numbers render at `opacity: 0.4`; hovering a line adds `background: rgba(255,255,255,0.03)`
**Estimated effort**: M

---

### T-014: Dual-theme CSS wiring for Shiki (github-dark / github-light)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/globals.css` (modify — add `[data-theme="dark"] pre` / `[data-theme="light"] pre` token selectors)
  - `repositories/anton-abyzov/vskill-platform/src/app/components/CodeBlock.tsx` (modify — `data-theme` attribute on `pre`)
**Test Plan** (BDD, REQUIRED):
  Given the site is rendered in dark theme (`html[data-theme="dark"]`)
  When a `<CodeBlock>` is visible on screen
  Then the token color for a string literal is the `github-dark` value; switching to light theme (`html[data-theme="light"]`) makes the same token render the `github-light` value without a page reload
**Estimated effort**: S

---

### T-015: E2E code-highlight spec and Lighthouse Performance gate
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/tests/e2e/code-highlight.spec.ts` (new)
**Test Plan** (BDD, REQUIRED):
  Given the vskill-platform build is run with Shiki integrated
  When Playwright visits a code-heavy docs page
  Then (a) `pre code span` elements contain `style="color:..."` attributes from Shiki output, (b) both light and dark theme token colors are present in DOM, (c) Lighthouse Performance score on `/` is recorded and must not drop more than 5 points vs the pre-Shiki baseline captured at task start
**Estimated effort**: M

---

### T-016: Homepage hero font wiring via next/font
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/layout.tsx` (modify — add display font via next/font/google)
**Test Plan** (BDD, REQUIRED):
  Given `JetBrains_Mono` (Display weight) is loaded via `next/font/google` with `display: 'swap'` and only the h1-weight subset
  When the root layout renders
  Then the CSS variable for the display font is defined; CLS < 0.05 on `/` measured via Lighthouse; only the h1-weight variant is preloaded (verified by inspecting `<link rel="preload">` tags in the HTML head)
**Estimated effort**: S

---

### T-017: Homepage hero h1 typography and SVG atmosphere
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/page.tsx` (modify — hero section)
**Test Plan** (BDD, REQUIRED):
  Given the homepage renders
  When a user views the hero section
  Then the h1 font-size is `3.25rem` (not the previous `2.25rem`), `text-wrap: balance` is applied, a dotted/grid SVG with a radial fade gradient is positioned behind the hero text, and the display font applies to the h1 only (all other text remains unaffected)
**Estimated effort**: M

---

## Phase 3 — Content as data (Track A — MDX migration)

### T-018: Install MDX dependencies and configure next.config.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/package.json` (modify — add `@next/mdx`, `@mdx-js/react`, `@mdx-js/loader`, `gray-matter`, `rehype-pretty-code`)
  - `repositories/anton-abyzov/vskill-platform/next.config.ts` (modify — wrap with `withMDX()`, extend `pageExtensions` to include `'mdx'`)
**Test Plan** (BDD, REQUIRED):
  Given `next.config.ts` wraps the config with `withMDX()` and `pageExtensions: ['ts', 'tsx', 'mdx']`
  When `npm run build` executes
  Then the build succeeds and Next.js recognises `.mdx` files as page routes without errors; `@next/mdx` is listed in `package.json` dependencies
**Estimated effort**: S

---

### T-019: Create mdx-components.tsx at project root
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/mdx-components.tsx` (new — at project root, not inside src/)
**Test Plan** (BDD, REQUIRED):
  Given `mdx-components.tsx` exports `useMDXComponents` mapping `code` to `CodeBlock`, `Callout`, `FlagTable`, `SectionHeading`, `Prose`, `InlineCode`, `TabGroup`
  When an `.mdx` file uses a fenced code block and a `<Callout>` component
  Then the rendered HTML uses the `CodeBlock` component with Shiki highlighting and the `Callout` component with its SVG icon, not generic `<pre>` or `<blockquote>` elements
**Estimated effort**: S

---

### T-020: Write mdx-components.test.tsx unit test
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/__tests__/mdx-components.test.tsx` (new)
**Test Plan** (BDD, REQUIRED):
  Given each MDX-mapped component (`CodeBlock`, `Callout`, `FlagTable`, `SectionHeading`, `Prose`, `InlineCode`, `TabGroup`) is rendered both via direct JSX and via the MDX component map
  When vitest compares both outputs via snapshot
  Then both snapshot outputs are identical for each component; the test covers all 7 mapped components
**Estimated effort**: M

---

### T-021: Define frontmatter spec and generate-docs-nav.ts script
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/scripts/generate-docs-nav.ts` (new)
  - `repositories/anton-abyzov/vskill-platform/src/app/docs/generated-nav.ts` (new, build-generated)
  - `repositories/anton-abyzov/vskill-platform/package.json` (modify — add `prebuild` entry for generate-docs-nav)
**Test Plan** (BDD, REQUIRED):
  Given two `.mdx` files exist under `src/app/docs/` with `title` and `toc[]` frontmatter
  When `generate-docs-nav.ts` runs at prebuild
  Then `src/app/docs/generated-nav.ts` exports a typed array where each entry contains `slug`, `title`, and `toc` fields matching the frontmatter; running it twice produces an identical (idempotent) output
**Estimated effort**: M

---

### T-022: Convert security-guidelines/page.tsx to page.mdx
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/docs/security-guidelines/page.tsx` (delete)
  - `repositories/anton-abyzov/vskill-platform/src/app/docs/security-guidelines/page.mdx` (new, ~250 LOC)
**Test Plan** (BDD, REQUIRED):
  Given `page.mdx` replaces the 723-line `page.tsx` at the same URL slug
  When Playwright visits `/docs/security-guidelines` after the migration
  Then (a) the page renders without 500 errors, (b) all section headings and code blocks present in the JSX version are present in the MDX output, (c) a Playwright pixel-diff vs the pre-migration baseline screenshot shows < 5% difference
**Estimated effort**: L

---

### T-023: Convert cli-reference/page.tsx to page.mdx
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/docs/cli-reference/page.tsx` (delete)
  - `repositories/anton-abyzov/vskill-platform/src/app/docs/cli-reference/page.mdx` (new, ~180 LOC)
**Test Plan** (BDD, REQUIRED):
  Given `page.mdx` replaces the 372-line `page.tsx` at the same URL slug
  When Playwright visits `/docs/cli-reference` after the migration
  Then (a) the page renders without 500 errors, (b) all CLI flags and code examples from the JSX version appear in the MDX output, (c) a Playwright pixel-diff vs the pre-migration baseline shows < 5% difference; the `COUNTS.vskillVersion` import renders the correct version string
**Estimated effort**: L

---

### T-024: Install Pagefind and add postbuild index generation
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/package.json` (modify — add `pagefind` devDep + `postbuild` script)
  - `repositories/anton-abyzov/vskill-platform/public/pagefind/` (output dir, gitignored except `.gitkeep`)
**Test Plan** (BDD, REQUIRED):
  Given `npm run build` completes for vskill-platform
  When the `postbuild` step runs `pagefind --site <validated-path>`
  Then `public/pagefind/pagefind.js` and `public/pagefind/pagefind.wasm` are generated; the index contains at least one entry; running Pagefind again on the same output is idempotent (no error on second run)
**Estimated effort**: M

---

### T-025: Mount ⌘K Pagefind palette in DocsLayout.tsx
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/components/DocsLayout.tsx` (modify — add Pagefind palette mount)
**Test Plan** (BDD, REQUIRED):
  Given a user is on any docs page and presses `⌘K` (or `Ctrl+K`)
  When the palette opens
  Then querying "scan" returns ≥1 result, "tier" returns ≥1 result, "install" returns ≥1 result; the palette closes on `Escape`; no `pagefind.js` network request fires until the palette is opened for the first time (lazy-load verified via Playwright `page.on('request')`)
**Estimated effort**: M

---

### T-026: E2E pixel-diff tests for MDX pages
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/tests/e2e/docs-mdx.spec.ts` (new)
**Test Plan** (BDD, REQUIRED):
  Given pre-migration baseline screenshots are captured for `/docs/security-guidelines` and `/docs/cli-reference`
  When the E2E suite runs post-migration
  Then `toHaveScreenshot()` comparisons for both pages pass within the 5% pixel-diff tolerance; the test also asserts the page title matches the frontmatter `title` field
**Estimated effort**: M

---

### T-027: E2E Pagefind search spec
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/tests/e2e/pagefind-search.spec.ts` (new)
**Test Plan** (BDD, REQUIRED):
  Given the production build has been run and `public/pagefind/` is populated
  When Playwright opens `/docs/cli-reference`, triggers `⌘K`, and types "scan"
  Then the palette results list contains at least one item with a title and excerpt; repeating for "tier" and "install" also yields ≥1 result each; palette result items are keyboard-navigable
**Estimated effort**: S

---

### T-028: Update link-checker.test.ts allow-list for /marketplace
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/__tests__/link-checker.test.ts` (modify — extend allow-list)
**Test Plan** (BDD, REQUIRED):
  Given the link checker test suite runs after `/marketplace` is added to the sitemap and nav
  When `npm run test` executes
  Then `link-checker.test.ts` passes without false positives on `/marketplace`, `/insights`, `/learn`, and `/docs` URLs; no previously passing assertions are broken
**Estimated effort**: S

---

## Phase 4 — Visual identity ladder (Track E)

### T-029: Redesign three-tier verification cards on getting-started page
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/docs/getting-started/page.tsx` (modify — lines 158-176)
**Test Plan** (BDD, REQUIRED):
  Given a user visits `/docs/getting-started`
  When the three-tier verification cards render
  Then Scanned card has a flat outline only (no background fill), Verified card has a `--tier-verified-bg` tinted fill plus a `--code-green` inner box-shadow, Certified card has a `--tier-certified-bg` fill plus a gold `linear-gradient` border and a CSS `perspective` transform on `:hover`; a Playwright snapshot confirms ascending visual weight
**Estimated effort**: M

---

### T-030: Echo tier visual language in TrustBadge.tsx
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/components/TrustBadge.tsx` (modify)
**Test Plan** (BDD, REQUIRED):
  Given `TrustBadge` is rendered with `tier="verified"` and separately with `tier="certified"`
  When a Playwright snapshot is taken
  Then the Verified badge uses the same tinted fill + green glow as the getting-started card; the Certified badge uses the same gold gradient border; visual tokens are shared (same CSS variable references, no duplicated color values)
**Estimated effort**: S

---

### T-031: Echo tier visual language in trust/page.tsx
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/trust/page.tsx` (modify)
**Test Plan** (BDD, REQUIRED):
  Given a user visits `/trust`
  When the trust ladder section renders
  Then tier icons, backgrounds, and border styles visually match those on `/docs/getting-started` (same tokens, same ascending weight); a Playwright snapshot comparison between the two pages shows consistent tier representations
**Estimated effort**: S

---

### T-032: Replace TabGroup border-bottom with animated absolute underline
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/components/TabGroup.tsx` (modify)
**Test Plan** (BDD, REQUIRED):
  Given a `<TabGroup>` with three tabs is rendered
  When the user clicks the second tab
  Then a single `position: absolute` underline element translates from tab 1 to tab 2 via `transform: translateX()` with a CSS transition; no per-button `border-bottom` style exists in the rendered output; with `prefers-reduced-motion: reduce` active, the transition is instant (no animation)
**Estimated effort**: M

---

### T-033: DocCard layered shadow and featured prop
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/components/DocCard.tsx` (modify)
**Test Plan** (BDD, REQUIRED):
  Given `<DocCard>` is rendered without `featured` prop
  When the card is visible
  Then it has `box-shadow: 0 1px 0 inset rgba(255,255,255,0.05), 0 4px 16px -8px rgba(0,0,0,0.5)` in dark theme; given `<DocCard featured>` is rendered, it additionally has a `background-clip: padding-box` gradient border; a vitest snapshot captures both variants
**Estimated effort**: S

---

### T-034: Replace Callout Unicode glyphs with inline SVG
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/components/Callout.tsx` (modify)
**Test Plan** (BDD, REQUIRED):
  Given `<Callout type="info">`, `<Callout type="warning">`, and `<Callout type="danger">` are rendered
  When the DOM is inspected
  Then no Unicode codepoints U+2139, U+26A0, or U+2715 appear in text nodes; each callout contains an `<svg>` element matching the docs SVG icon family; the `danger` variant has a 1px tinted top-border and a soft inner glow
**Estimated effort**: S

---

### T-035: Light theme contrast tokens in globals.css
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/globals.css` (modify — light theme block)
**Test Plan** (BDD, REQUIRED):
  Given the site is rendered in light theme
  When a `DocCard` and a `Callout` are visible
  Then `--border` resolves to `#E0E0E0` (not the previous `#E5E5E5`), `--bg-subtle` to `#F5F5F5`, and card-style components have `box-shadow: inset 0 1px 0 rgba(255,255,255,0.6)` so they are visually distinct from the page background; WCAG AA contrast passes for sidebar active state text on `--bg-hover` in both themes
**Estimated effort**: S

---

### T-036: E2E visual regression for tier ladder and light theme
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/tests/e2e/tier-visual.spec.ts` (new)
**Test Plan** (BDD, REQUIRED):
  Given baseline screenshots are captured for `/docs/getting-started`, `/trust`, and a page embedding `TrustBadge`
  When Playwright runs the tier-visual spec post-Track-E
  Then all three pages pass `toHaveScreenshot()` within tolerance; the Scanned → Verified → Certified tier cards on `/docs/getting-started` show ascending visual weight (verified via element `box-shadow` and `background` computed style assertions); light theme does not cause cards to disappear into the background
**Estimated effort**: M

---

### T-037: E2E test for sidebar active state and scroll-spy
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/tests/e2e/docs-nav.spec.ts` (new)
**Test Plan** (BDD, REQUIRED):
  Given a user visits `/docs/cli-reference`
  When Playwright captures the sidebar
  Then the active link's computed `border-left` matches `2px solid var(--code-green)` and background matches `var(--bg-hover)`; scrolling the page to the second major heading updates the TOC active item within 500ms; the TOC active indicator changes position (verified via `element.getBoundingClientRect()` delta)
**Estimated effort**: M

---

## Phase 5 — Showcase surface (Track B — /marketplace)

### T-038: Create PluginEntry type and plugins.ts data file
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/marketplace/plugins.ts` (new)
**Test Plan** (BDD, REQUIRED):
  Given `plugins.ts` exports a `PLUGINS: PluginEntry[]` array
  When TypeScript compiles the file
  Then exactly 8 entries exist, each with required fields: `slug`, `name`, `tagline`, `description`, `tier`, `skills`, `agents`, `author`, `lastUpdated`, `version`, `accentColor`, `installCommand`; no TypeScript errors; `tier` is one of `'verified' | 'community'`
**Estimated effort**: M

---

### T-039: Create FeedEntry type and buildFeed function in feed.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/marketplace/feed.ts` (new)
**Test Plan** (BDD, REQUIRED):
  Given representative inputs: 2 article entries, 1 video entry, and 3 plugin entries (each producing a `release` kind entry)
  When `buildFeed({ articles, videos, plugins })` is called
  Then the output is a flat `FeedEntry[]` of length 6, sorted in reverse-chronological order by `publishedAt`, each entry has a non-empty `kind` field (`'article'`, `'video'`, or `'release'`), and the `source` field is present on release entries
**Estimated effort**: S

---

### T-040: Vitest unit test for marketplace feed merger
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/marketplace/__tests__/marketplace-feed.test.ts` (new)
**Test Plan** (BDD, REQUIRED):
  Given fixture inputs with a known chronological sequence of articles, videos, and releases
  When `buildFeed` processes them
  Then the first element in the result has the most recent `publishedAt`, the last has the oldest; entries of all three kinds appear in the merged output; a release entry's `title` matches the originating plugin's `name`
**Estimated effort**: S

---

### T-041: Build /marketplace/page.tsx hero and plugin grid (sections 1-3)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/marketplace/page.tsx` (new — sections 1-3: Hero, Featured Collection, All Plugins)
**Test Plan** (BDD, REQUIRED):
  Given `/marketplace` is visited
  When the page renders (server component, no client JS required)
  Then (a) the hero h1 and tier filter chips are present, (b) exactly one `<DocCard featured>` spotlight card is rendered, (c) the plugin grid contains exactly 8 `<DocCard>` entries each showing tier badge (`<TierBadge>`), agent icons from `AGENT_ICONS`, tagline, last-updated, and a `<CopyButton>` with the install command; all data sourced from `plugins.ts`
**Estimated effort**: M

---

### T-042: Add What's New feed, use-case strip, and Insights footer to /marketplace (sections 4-7)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/marketplace/page.tsx` (modify — sections 4-7)
**Test Plan** (BDD, REQUIRED):
  Given the feed data from `buildFeed()` is passed to the What's New section
  When Playwright renders `/marketplace`
  Then the "What's New" horizontal-scroll row shows feed items with kind-tagged badges (`Article`, `Video`, `Release`), items are in reverse-chronological order, the "Browse by use-case" taxonomy strip renders at least 3 use-case chips, the Trending Skills section reuses `<TrendingSkillsSection/>` unchanged, and the Insights footer grid shows 3 entries linking to `/insights/*` paths
**Estimated effort**: M

---

### T-043: Swap top nav and MobileNav from Insights to Marketplace
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/layout.tsx` (modify — nav link swap + footer /insights link)
  - `repositories/anton-abyzov/vskill-platform/src/app/components/MobileNav.tsx` (modify — nav link swap)
**Test Plan** (BDD, REQUIRED):
  Given any page on verified-skill.com renders after this change
  When Playwright checks the desktop nav (`nav a`) and mobile nav
  Then a link with text "Marketplace" pointing to `/marketplace` exists in both navs; no link with text "Insights" appears in primary nav; the footer "Resources" column contains an `<a href="/insights">` link; `/insights` resolves to a 200 response
**Estimated effort**: S

---

### T-044: Add sitemap entries and /docs/plugins redirect
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/sitemap.ts` (modify)
  - `repositories/anton-abyzov/vskill-platform/next.config.ts` (modify — add 301 redirect)
  - `repositories/anton-abyzov/vskill-platform/src/app/docs/plugins/page.tsx` (modify — collapse to server `redirect('/marketplace')`)
**Test Plan** (BDD, REQUIRED):
  Given the build is run with the updated `next.config.ts` and `sitemap.ts`
  When Playwright fetches `/sitemap.xml`
  Then `/marketplace` appears with priority `0.85`, `/insights` with `0.6`, `/learn` with `0.6`, `/docs` with `0.7`; fetching `/docs/plugins` returns HTTP 301 with `Location: /marketplace`; the backup `plugins/page.tsx` server redirect also triggers if the next.config redirect is somehow dropped
**Estimated effort**: S

---

### T-045: Vitest unit test for marketplace page rendering
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/marketplace/__tests__/marketplace.test.tsx` (new)
**Test Plan** (BDD, REQUIRED):
  Given the `marketplace/page.tsx` is rendered via vitest with React Testing Library
  When the render completes
  Then exactly 8 plugin card elements are present in the DOM, the "What's New" section contains items of all three kinds, the search input element is present, and no TypeScript or React runtime errors are thrown
**Estimated effort**: M

---

### T-046: E2E spec for /marketplace route
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - `repositories/anton-abyzov/vskill-platform/tests/e2e/marketplace.spec.ts` (new)
**Test Plan** (BDD, REQUIRED):
  Given the vskill-platform production build is running
  When Playwright executes the marketplace spec
  Then (a) `/marketplace` renders 8 plugin cards with visible tier badges, (b) desktop nav shows "Marketplace" not "Insights", (c) `response.status()` for `/docs/plugins` is 301 and `response.headers()['location']` is `/marketplace`, (d) footer contains `href="/insights"`, (e) sitemap XML includes `/marketplace` with the correct priority attribute
**Estimated effort**: M

---

### T-047: Final integration pass — npm run test + build gates
**User Story**: US-001, US-002, US-003, US-004, US-005, US-006 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US3-01, AC-US3-02, AC-US3-03, AC-US4-01, AC-US4-02, AC-US4-03, AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04
**Status**: [ ] pending
**Project**: vskill-platform
**Files**:
  - All modified files (verification pass — no new files created in this task)
**Test Plan** (BDD, REQUIRED):
  Given all prior tasks in Phases 1-5 are marked complete
  When `npm run test` (vitest) and `npm run test:e2e` (Playwright) run in vskill-platform, and `npm publish --dry-run` runs in the vskill repo
  Then all vitest suites pass (0 failures), all Playwright specs pass (0 failures), `npm publish --dry-run` exits 0, `npm run build` succeeds with Pagefind index generated, and Lighthouse Performance on `/` does not regress more than 5 points from the captured baseline
**Estimated effort**: M

---

## Verification

Closure-time gates (run as final checks before `/sw:done`, not numbered tasks):

- [ ] `npm run test` (vitest, vskill-platform) — all suites pass; `docs-nav.test.ts`, `link-checker.test.ts`, `docs-sidebar.test.tsx` still pass alongside new tests
- [ ] `npm run test:e2e` (Playwright, vskill-platform) — `marketplace.spec.ts`, `docs-mdx.spec.ts`, `pagefind-search.spec.ts`, `code-highlight.spec.ts`, `tier-visual.spec.ts`, `docs-nav.spec.ts` all pass
- [ ] `npm run build` (vskill-platform) — exits 0; `public/pagefind/pagefind.js` exists; `src/lib/generated-counts.ts` regenerated
- [ ] `npm publish --dry-run` (vskill) — prepublishOnly chain completes; `git diff --exit-code README.md` exits 0
- [ ] Lighthouse Performance on `/` — regression ≤ 5 points vs pre-change baseline; CLS < 0.05
- [ ] Manual: `/marketplace` UX review — 8 plugin cards, What's New feed, nav swap, tier filter chips
- [ ] Manual: Tier visual ladder on `/docs/getting-started` — ascending visual weight Scanned → Verified → Certified
- [ ] Manual: Light theme contrast across docs — DocCards and Callouts visually distinct from page background
- [ ] Manual: Hero typography on `/` — h1 at 3.25rem with display font, SVG atmosphere visible
- [ ] `git status` check in both repos — no unstaged generated files (run `npm run prebuild` in vskill-platform if `generated-counts.ts` is stale)

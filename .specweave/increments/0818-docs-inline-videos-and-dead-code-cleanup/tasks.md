---
increment: 0818-docs-inline-videos-and-dead-code-cleanup
generated: 2026-05-01
tasks: 15
ac_coverage: 21/21
---

# Tasks: Inline /watch videos on 4 /docs pages, delete dead VideoHero + orphan video assets, lift unique scene-kit components

## HARD DEPENDENCY BLOCK

**INC-C (0817) MUST be MERGED before any task beyond T-001 begins.**

INC-C delivers: `src/lib/learn/video-catalog.ts` (renamed from `video-data.ts`), `WatchVideoPlayer.tsx` (renamed from `LazyVideoPlayer.tsx`), the 4 rendered 101 videos at `public/video/watch/{getting-started-101,cli-commands-101,security-scan-101,plugin-marketplace-101}.{mp4,webm,vtt}`, thumbnails at `public/watch/thumbnails/<slug>.webp`, and the `captionsSrc` field on the `Video` catalog type.

Without INC-C: the catalog rename, player rename, and all 4 video files are absent. Every task in US-001 compiles against ghost paths. **Abort at T-001 if INC-C is not merged.**

INC-A (0810) and INC-B (0812) must also be merged — INC-A for scene-kit conventions consumed by US-003, INC-B for the `/docs/studio` inline-video precedent and `<track kind="captions">` wiring model.

All file paths are relative to `repositories/anton-abyzov/vskill-platform/` unless explicitly prefixed otherwise.

---

## US-001: Inline /watch videos at top of 4 /docs pages

### T-001: Precondition check — verify INC-A, INC-B, INC-C are fully merged
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [ ] pending

**Scope**:
- Read metadata.json for increments 0810, 0812, 0817 and confirm `status: "closed"` (or equivalent merged state)
- Confirm `repositories/anton-abyzov/vskill-platform/src/lib/learn/video-catalog.ts` exists and exports `VIDEOS`
- Confirm `repositories/anton-abyzov/vskill-platform/src/app/components/learn/WatchVideoPlayer.tsx` exists
- Confirm all 4 video sets exist: `public/video/watch/getting-started-101.{mp4,webm,vtt}`, `cli-commands-101.{mp4,webm,vtt}`, `security-scan-101.{mp4,webm,vtt}`, `plugin-marketplace-101.{mp4,webm,vtt}`
- Confirm thumbnails exist: `public/watch/thumbnails/{getting-started-101,cli-commands-101,security-scan-101,plugin-marketplace-101}.webp`
- If any precondition fails: ABORT and surface the gap to the user — do NOT proceed to T-002

**Test Plan** (BDD):
```
Given increment metadata and on-disk file paths are inspectable
When the precondition check runs at the start of INC-D implementation
Then INC-A, INC-B, and INC-C metadata show merged/closed status, video-catalog.ts exports VIDEOS, WatchVideoPlayer.tsx exists, and all 12 video files (4 slugs x {mp4,webm,vtt}) plus 4 WebP thumbnails are present on disk — OR the check aborts with a documented gap message if any are missing
```

---

### T-002: OQ-2 resolution — read post-INC-C WatchVideoPlayer prop signature and record actual props
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [ ] pending

**Scope**:
- Read `repositories/anton-abyzov/vskill-platform/src/app/components/learn/WatchVideoPlayer.tsx` (post-INC-C)
- Confirm or document the actual prop names: expected `{ slug, mp4, webm, poster, captionsSrc, ariaLabel }` per plan §4.3 and ADR 0817-01 §D3
- If props match the §4.3 draft exactly: record "OQ-2 resolved — props match plan §4.3" in this task's notes; no player changes needed
- If props differ: record the actual signature here, and note which props `DocVideoEmbed` must adapt to — do NOT refactor the player; `DocVideoEmbed` adapts to the player (per spec Out of Scope + plan §4.6)
- This resolution determines `DocVideoEmbed`'s body before T-004 writes it

**Test Plan** (BDD):
```
Given WatchVideoPlayer.tsx exists at the post-INC-C path
When the planner reads its TypeScript prop interface or PropTypes declaration
Then the actual prop names are recorded in the T-002 scope notes, and any mismatch with plan §4.3 is documented before DocVideoEmbed is written — ensuring the component body in T-004 compiles against the real player API, not a ghost signature
```

---

### T-003: OQ-1 disposition lock — confirm /docs/submitting default DEFER
**User Story**: US-001 | **Satisfies ACs**: AC-US1-08 | **Status**: [ ] pending

**Scope**:
- Lock the `/docs/submitting` disposition: **DEFAULT = DEFER** — no `DocVideoEmbed` on this page in this increment (per plan §6 and ADR D3)
- If the architect or user overrides at plan review to use `slug="plugin-marketplace-101"`: record the override here and add a 5th page edit + Vitest spec to T-009 scope
- Add a one-line comment to `repositories/anton-abyzov/vskill-platform/src/app/docs/submitting/page.tsx` recording the defer rationale (per plan §6): `// 2026-05-01 (INC-D 0818): no inline video this increment — submitting flow doesn't // 1:1 match plugin-marketplace-101 (consume vs. publish). Revisit when a // submitting-101 or publishing-101 video is rendered.`
- Record the chosen disposition ("DEFER confirmed" or "OVERRIDE: use plugin-marketplace-101") in this task's notes — this is the binding decision for T-009 and T-010

**Test Plan** (BDD):
```
Given the OQ-1 open question from spec.md with default disposition DEFER
When the planner reviews the /docs/submitting page content and the plugin-marketplace-101 video topic fit
Then the chosen disposition is locked and recorded here, the submitting page receives only the one-line defer comment (default path), and T-009 and T-010 scope reflect whether 4 or 5 pages are in play
```

---

### T-004: Build DocVideoEmbed server component
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-06 | **Status**: [ ] pending

**Scope**:
- Create `repositories/anton-abyzov/vskill-platform/src/app/components/docs/DocVideoEmbed.tsx`
- Server component — NO `"use client"` directive
- Props contract per plan §4.2: `{ slug: string; ctaLabel?: string; aspectRatio?: "16/9" | "21/9" }`
- Body: call `getVideo(slug)` from `@/lib/learn/videos` (catalog helper from INC-C)
- If no match: emit `console.warn` in `NODE_ENV !== "production"`, then `return null`
- If match: render `<WatchVideoPlayer>` with `mp4`, `webm`, `poster`, `captionsSrc`, `ariaLabel`, `slug` derived from the catalog entry (use actual prop names confirmed in T-002)
- Below player: render `<Link href={"/watch/" + slug}>{ctaLabel} →</Link>` using Next.js `Link`
- Wrapper: `<div className="doc-video-embed mb-8">`; CTA: `<p className="mt-2 text-sm">`
- Component is ~50–80 LOC — intentionally thin; no state, no effects, no `next/dynamic` wrapper (player already lazy per plan §4.1)
- Do NOT create the `docs/` components directory if it already exists; check first with `ls`

**Test Plan** (BDD):
```
Given the video-catalog.ts VIDEOS array contains a valid entry for slug "getting-started-101"
When DocVideoEmbed is rendered with slug="getting-started-101" in a server context
Then it returns a JSX tree containing a WatchVideoPlayer with mp4/webm/poster/captionsSrc/ariaLabel props derived from the catalog entry and a Next.js Link with href="/watch/getting-started-101" and text "Watch full episode →" — and when rendered with slug="does-not-exist" it returns null
```

---

### T-005: Write Vitest specs for DocVideoEmbed (TDD red to green)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-06 | **Status**: [ ] pending

**Scope**:
- Create `repositories/anton-abyzov/vskill-platform/src/app/components/docs/__tests__/DocVideoEmbed.test.tsx`
- Test 1 — catalog hit, happy path: mock `@/lib/learn/videos` to return a fixture entry for slug `"getting-started-101"`; render `<DocVideoEmbed slug="getting-started-101" />`; assert `<WatchVideoPlayer>` receives `mp4`, `webm`, `poster`, `captionsSrc`, `ariaLabel` props matching the fixture; assert `<Link>` exists with `href="/watch/getting-started-101"` and text `"Watch full episode →"`
- Test 2 — catalog miss (AC-US1-06): render `<DocVideoEmbed slug="does-not-exist" />`; assert rendered output is empty (no DOM nodes rendered); assert no Error thrown
- Test 3 — dev warn on miss: set `process.env.NODE_ENV = "development"`; spy on `console.warn`; render with missing slug; assert `console.warn` was called with a message containing the slug
- Test 4 — production silent: set `process.env.NODE_ENV = "production"`; render with missing slug; assert `console.warn` was NOT called
- Run `npx vitest run src/app/components/docs/__tests__/DocVideoEmbed.test.tsx` and confirm all tests pass (TDD green gate)

**Test Plan** (BDD):
```
Given DocVideoEmbed.tsx is implemented per T-004
When the Vitest spec suite runs with catalog hit and miss scenarios
Then all 4 test cases pass: happy-path props flow correctly, missing slug renders null without throwing, dev-mode emits console.warn, production-mode is silent — confirming the component contract (AC-US1-01 + AC-US1-06) is verifiable at the unit level
```

---

### T-006: Wire DocVideoEmbed into /docs/getting-started + page-level Vitest spec
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [ ] pending

**Scope**:
- Edit `repositories/anton-abyzov/vskill-platform/src/app/docs/getting-started/page.tsx`
- Add import: `import DocVideoEmbed from "@/components/docs/DocVideoEmbed"` (use the project's path alias — check existing imports for the alias pattern)
- Insert `<DocVideoEmbed slug="getting-started-101" />` as the FIRST JSX child of the page body — ABOVE all existing content including the `<h1>` (per plan §4.7)
- No existing topic content is removed or rewritten; the embed is purely additive
- Create or extend `src/app/docs/getting-started/__tests__/page.test.tsx`: assert that the first JSX child of the page component body is `<DocVideoEmbed>` with `slug="getting-started-101"`
- Run `npx vitest run` scoped to the page test and confirm green

**Test Plan** (BDD):
```
Given DocVideoEmbed exists (T-004) and video-catalog.ts has an entry for "getting-started-101"
When /docs/getting-started/page.tsx is rendered in a Vitest environment
Then the first child element of the page body is DocVideoEmbed with slug="getting-started-101", confirming the AC-US1-02 Vitest leg — and the page renders without errors with all prior content intact below the embed
```

---

### T-007: Wire DocVideoEmbed into /docs/cli-reference + page-level Vitest spec
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [ ] pending

**Scope**:
- Edit `repositories/anton-abyzov/vskill-platform/src/app/docs/cli-reference/page.tsx`
- Add import and insert `<DocVideoEmbed slug="cli-commands-101" />` as first JSX child of page body (same pattern as T-006)
- Create or extend `src/app/docs/cli-reference/__tests__/page.test.tsx`: assert first body child is `<DocVideoEmbed>` with `slug="cli-commands-101"`
- Run page test scoped to cli-reference and confirm green

**Test Plan** (BDD):
```
Given DocVideoEmbed exists and video-catalog.ts has an entry for "cli-commands-101"
When /docs/cli-reference/page.tsx is rendered in a Vitest environment
Then the first child element of the page body is DocVideoEmbed with slug="cli-commands-101" (AC-US1-03 Vitest leg), all prior CLI reference content is intact below the embed, and no new import or component errors are introduced
```

---

### T-008: Wire DocVideoEmbed into /docs/security-guidelines + page-level Vitest spec
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [ ] pending

**Scope**:
- Edit `repositories/anton-abyzov/vskill-platform/src/app/docs/security-guidelines/page.tsx`
- Add import and insert `<DocVideoEmbed slug="security-scan-101" />` as first JSX child of page body
- Create or extend `src/app/docs/security-guidelines/__tests__/page.test.tsx`: assert first body child is `<DocVideoEmbed>` with `slug="security-scan-101"`
- Run page test scoped to security-guidelines and confirm green

**Test Plan** (BDD):
```
Given DocVideoEmbed exists and video-catalog.ts has an entry for "security-scan-101"
When /docs/security-guidelines/page.tsx is rendered in a Vitest environment
Then the first child element of the page body is DocVideoEmbed with slug="security-scan-101" (AC-US1-04 Vitest leg), all prior security guidelines content is intact below the embed, and no import errors are introduced
```

---

### T-009: Wire DocVideoEmbed into /docs/plugins + page-level Vitest spec; apply OQ-1 disposition to /docs/submitting
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05, AC-US1-08 | **Status**: [ ] pending

**Scope**:
- Edit `repositories/anton-abyzov/vskill-platform/src/app/docs/plugins/page.tsx`
- Add import and insert `<DocVideoEmbed slug="plugin-marketplace-101" />` as first JSX child of page body
- Create or extend `src/app/docs/plugins/__tests__/page.test.tsx`: assert first body child is `<DocVideoEmbed>` with `slug="plugin-marketplace-101"`
- Apply OQ-1 disposition locked in T-003:
  - **Default DEFER**: `src/app/docs/submitting/page.tsx` already received the one-line defer comment in T-003; no further edits
  - **Override path**: if T-003 recorded an override, also insert `<DocVideoEmbed slug="plugin-marketplace-101" />` into `submitting/page.tsx` as first body child, and add a Vitest spec asserting it (same pattern as above)
- Run vitest for plugins page (and submitting if override) and confirm green

**Test Plan** (BDD):
```
Given DocVideoEmbed exists and video-catalog.ts has an entry for "plugin-marketplace-101"
When /docs/plugins/page.tsx is rendered in a Vitest environment
Then the first child element of the page body is DocVideoEmbed with slug="plugin-marketplace-101" (AC-US1-05 Vitest leg) — AND /docs/submitting/page.tsx is either unchanged with only the defer comment (default DEFER: no DocVideoEmbed present) or contains DocVideoEmbed with slug="plugin-marketplace-101" (override path), consistent with the disposition recorded in T-003 (AC-US1-08)
```

---

### T-010: Write Playwright E2E spec for all 4 docs pages — inline video, captions, "Watch full episode" link
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-07, AC-US1-08 | **Status**: [ ] pending

**Scope**:
- Create `repositories/anton-abyzov/vskill-platform/tests/e2e/docs-inline-video.spec.ts`
- For each of the 4 pages (`/docs/getting-started`, `/docs/cli-reference`, `/docs/security-guidelines`, `/docs/plugins`):
  - Load the page against `http://localhost:3000`
  - Assert `<video>` element is present and appears BEFORE the first `<h1>` in DOM order (AC-US1-02/03/04/05 Playwright leg)
  - Assert "Watch full episode" link exists with correct `href` (`/watch/<slug>`)
  - Assert `<track kind="captions">` exists with a non-empty `src` attribute
  - Assert the `.vtt` file returns HTTP 200 via `page.waitForResponse` (AC-US1-07)
- Add one test for `/docs/submitting`:
  - Default DEFER branch: assert NO `<video>` element is present on the page (AC-US1-08 default branch)
  - Override branch (if T-003 locked override): assert `<video>` IS present with `href="/watch/plugin-marketplace-101"`
- Run `npx playwright test tests/e2e/docs-inline-video.spec.ts` against a running local dev server and confirm all tests pass
- Note: local dev server MUST be running at `http://localhost:3000` before this task executes (per `feedback_video_local_preview.md`)

**Test Plan** (BDD):
```
Given the local dev server is running at http://localhost:3000 with all 4 DocVideoEmbed integrations live (T-006 through T-009 complete)
When the Playwright E2E suite navigates to /docs/getting-started, /docs/cli-reference, /docs/security-guidelines, /docs/plugins, and /docs/submitting
Then: each in-scope page has a <video> element appearing before the first <h1> in DOM order; each <track kind="captions"> has a non-empty src; each .vtt file returns HTTP 200; each "Watch full episode" link href matches /watch/<slug>; the /docs/submitting page has no <video> (default DEFER) — covering AC-US1-02/03/04/05 (Playwright leg), AC-US1-07, and AC-US1-08
```

---

## US-002: Delete dead VideoHero component + orphan video assets

### T-011: rg verification gate — confirm zero references to VideoHero and all 3 orphan assets
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03 | **Status**: [ ] pending

**Scope**:
- Run each rg invocation from plan §5.1 and capture stdout (zero lines = pass):
  - `rg "VideoHero" repositories/anton-abyzov/vskill-platform/src/`
  - `rg -F "ship-while-you-sleep" repositories/anton-abyzov/vskill-platform/`
  - `rg -F "ship-while-you-sleep.mp4" repositories/anton-abyzov/vskill-platform/`
  - `rg -F "specweave-promo" repositories/anton-abyzov/vskill-platform/`
  - `rg -F "specweave-promo.mp4" repositories/anton-abyzov/vskill-platform/`
  - `rg -F "specweave-promo.webm" repositories/anton-abyzov/vskill-platform/`
- AC-US2-01: if the VideoHero rg returns ANY match other than `VideoHero.tsx` or `VideoHero.test.tsx` themselves, ABORT US-002 and surface the reference for investigation
- AC-US2-03: for each asset rg, matches limited to the binary file itself (`public/video/`) are acceptable (self-reference); any match in `src/`, `*.tsx`, `*.ts`, `*.html`, `*.mdx`, `*.md`, or `*.json` is a BLOCK — investigate and resolve before proceeding
- Record all rg invocations and their exact outputs in the closure summary as evidence (FR-004 mandate)
- Only proceed to T-012 if ALL six rg checks return zero blocking references

**Test Plan** (BDD):
```
Given VideoHero.tsx has never been imported anywhere since its creation and the 3 orphan mp4/webm files were abandoned in Feb 2026
When the six rg commands scan the full vskill-platform working tree across src/, public/, and all *.{tsx,ts,html,mdx,md,json} extensions
Then each returns zero matches in active source files (self-references in public/ for the binary files are excluded), confirming the deletion is safe and providing the documented zero-references evidence required by AC-US2-01 and AC-US2-03
```

---

### T-012: Execute US-002 deletions — git rm 5 files, verify build + tests, record disk delta
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-04, AC-US2-05, AC-US2-06, AC-US2-07 | **Status**: [ ] pending

**Scope**:
- Step 1: Record baseline disk size — `du -sh repositories/anton-abyzov/vskill-platform/public/video/`
- Step 2: Commit 1 — `git rm src/app/components/homepage/VideoHero.tsx src/app/components/homepage/__tests__/VideoHero.test.tsx` with message `0818: remove unused VideoHero component + test` (AC-US2-02)
- Step 3: Commit 2 — `git rm public/video/ship-while-you-sleep.mp4` with message `0818: remove orphan ship-while-you-sleep.mp4 (~3 MB)` (AC-US2-04, partial)
- Step 4: Commit 3 — `git rm public/video/specweave-promo.mp4 public/video/specweave-promo.webm` with message `0818: remove orphan specweave-promo media (~5.5 MB)` (AC-US2-04, complete)
- Step 5: Run `npm run build` from `repositories/anton-abyzov/vskill-platform/` — must exit code 0 with no missing-module or missing-asset errors for the 4 deleted entities (AC-US2-06)
- Step 6: Run `npx vitest run` from same directory — must exit code 0; VideoHero.test.tsx must NOT appear in the test count (AC-US2-07)
- Step 7: Record post-deletion disk size — `du -sh public/video/` — compute delta; confirm delta >= 7.5 MB and <= 10 MB (AC-US2-05)
- Step 8: Run `find repositories/anton-abyzov/vskill-platform/src/app/components/homepage -name "VideoHero*"` — must return empty (AC-US2-02 verification)
- Record baseline size, post-deletion size, delta, and build/vitest exit codes in closure summary as evidence
- If build OR vitest fails at step 5/6: revert the failing commit via `git checkout HEAD -- <file>` and investigate (per plan §5.2 and §5.5)

**Test Plan** (BDD):
```
Given T-011 confirmed zero blocking references for all 5 files
When the 5 files are removed via git rm in 3 commits and npm run build + npx vitest run execute against the modified working tree
Then: VideoHero.tsx and VideoHero.test.tsx are absent from the filesystem (find returns empty); all 3 orphan video files are absent; npm run build exits 0 with no missing-module errors; npx vitest run exits 0 with VideoHero.test.tsx not in test counts; du -sh public/video/ shows a reduction of 7.5-10 MB — satisfying AC-US2-02, AC-US2-04, AC-US2-05, AC-US2-06, AC-US2-07
```

---

## US-003: Lift unique components from docs-site/remotion/ into scene-kit (optional, deferrable)

### T-013: Inspect docs-site/remotion/ — write scene-kit-lift-inspection.md
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [ ] pending

**Scope**:
- Run from umbrella repo root: `find repositories/anton-abyzov/specweave/docs-site/remotion/ -name "*.tsx" -type f`
- Read each `.tsx` file found
- Create directory `.specweave/increments/0818-docs-inline-videos-and-dead-code-cleanup/reports/` if it doesn't exist
- Write `.specweave/increments/0818-docs-inline-videos-and-dead-code-cleanup/reports/scene-kit-lift-inspection.md`
- For each component file, record: (a) file path, (b) exported component name(s), (c) whether an equivalent already exists in `src/remotion/scene-kit/` (name-match or behavior-match against the 12 existing primitives: BrowserChrome, TerminalFrame, TUIFrame, BigText, CommandTypewriter, CaptionBar, PillTag, MetricBar, SkillCard, AgentStrip, TransitionWipe + tokens.ts), (d) recommendation: `LIFT`, `SKIP`, or `DEFER` with one-sentence rationale
- Apply the 4 LIFT criteria from plan §7.3: unique behavior, brand-consistent (no inline hex or trivially migratable), reusable across videos, tested or trivially testable — ALL four must be met for LIFT; any failure means SKIP (duplicate) or DEFER (unique but risky)
- Suspected candidates per plan §7.2: `NumberTicker` (likely LIFT), `TypewriterText` (likely LIFT if API differs meaningfully from CommandTypewriter), `SectionTitle` (likely SKIP — probable BigText duplicate)
- The inspection report alone is a complete deliverable if all candidates are DEFER — do not lift until report is reviewed

**Test Plan** (BDD):
```
Given the docs-site/remotion/ directory was created before the scene-kit consolidation in INC-A
When each .tsx file under that path is read and compared against the 12 scene-kit primitives
Then scene-kit-lift-inspection.md is committed at .specweave/increments/0818-docs-inline-videos-and-dead-code-cleanup/reports/ with every component file enumerated, a LIFT/SKIP/DEFER recommendation with rationale for each, and — if all are SKIP or DEFER — a note recording "no components lifted; inspection is the deliverable" (AC-US3-01 satisfied in all branches)
```

---

### T-014: Apply lift decisions — lift LIFT candidates into scene-kit, then archive/delete docs-site/remotion/
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06 | **Status**: [ ] pending

**Scope**:
- Read the inspection report from T-013 and apply the decisions:

**Branch A — one or more LIFT candidates exist** (AC-US3-02 active):
- For each LIFT component:
  - Copy component body to `repositories/anton-abyzov/vskill-platform/src/remotion/scene-kit/<ComponentName>.tsx`
  - Apply scene-kit conventions: replace any hardcoded hex with imports from `scene-kit/tokens.ts` / `BRAND_COLORS`; ensure the public API surface is clean
  - Add export to `repositories/anton-abyzov/vskill-platform/src/remotion/scene-kit/index.ts`
  - Create sibling test at `src/remotion/scene-kit/__tests__/<ComponentName>.test.tsx` (jsdom mount + no-throw, mirroring existing scene-kit test pattern)
  - Run `npx vitest run src/remotion/scene-kit/__tests__/<ComponentName>.test.tsx` — must pass (AC-US3-06)
  - Verify lifted component is importable from the index: confirm entry in `src/remotion/scene-kit/index.ts` (AC-US3-06)

**Branch B — zero LIFT candidates (all SKIP or DEFER)** (AC-US3-05, AC-US3-02 vacuous):
- Record "no components lifted — all duplicates or deferred" in closure summary
- Proceed directly to archive step

**Archive step (default for both branches, per OQ-3)**:
- Run: `git mv repositories/anton-abyzov/specweave/docs-site/remotion repositories/anton-abyzov/specweave/docs-site/.archive/remotion-2026-05`
- If architect explicitly green-lit deletion at plan review: use `git rm -r` instead (alt path per OQ-3 — only when inspection shows zero unique components)
- Record which option was chosen and the rationale in closure summary (AC-US3-03)

**Skip-entirely path** (AC-US3-05 full defer — if inspection classifies all as DEFER due to risk OR user/architect rejects lift at plan review):
- Do NOT create files in scene-kit/, do NOT archive the directory
- Record "US-003 fully deferred — see inspection report for rationale" in closure summary
- Increment still closes COMPLETE (inspection report from T-013 IS the deliverable)

**Post-archive verification** (AC-US3-04, only if archive/delete ran):
- Run: `rg "docs-site/remotion" repositories/anton-abyzov/specweave/` — must return zero matches excluding `.archive/` paths
- Run: `npm run build` (or the canonical build command) in `repositories/anton-abyzov/specweave/docs-site/` — must exit code 0
- Capture exit code in closure summary as evidence

**Test Plan** (BDD):
```
Given the inspection report from T-013 classifies each component as LIFT, SKIP, or DEFER
When lift decisions are applied (LIFT components moved to scene-kit with tests, all others skipped/deferred)
Then: any LIFT components exist at src/remotion/scene-kit/<Name>.tsx with a passing sibling test and an export in index.ts; the legacy docs-site/remotion/ directory no longer exists at its original path (archived to .archive/remotion-2026-05 or deleted); rg "docs-site/remotion" returns zero active refs; docs-site npm run build exits 0 — satisfying AC-US3-02/03/04/06 (lift branch) or the inspection-only contract (AC-US3-05 defer branch)
```

---

## Verification & Closure

### T-015: Verification gates — screenshots, evidence capture, closure prep
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-07, AC-US2-05, AC-US2-06, AC-US2-07 | **Status**: [ ] pending

**Scope**:
- Start local dev server at `http://localhost:3000` (required by `feedback_video_local_preview.md`)
- Capture Claude Preview screenshots (or Playwright screenshots) of all 4 in-scope `/docs/*` pages showing the video embed at the top:
  - `http://localhost:3000/docs/getting-started`
  - `http://localhost:3000/docs/cli-reference`
  - `http://localhost:3000/docs/security-guidelines`
  - `http://localhost:3000/docs/plugins`
- Verify captions VTT 200 for each page via Playwright `waitForResponse` or Claude Preview `preview_network` (AC-US1-07 final confirmation)
- Assemble closure summary evidence:
  - All 6 rg invocations from T-011 with their zero-line outputs (AC-US2-01, AC-US2-03)
  - `du -sh public/video/` BEFORE and AFTER values and computed delta (AC-US2-05)
  - `npm run build` exit code 0 confirmation (AC-US2-06)
  - `npx vitest run` exit code 0 confirmation (AC-US2-07)
  - US-003 outcome: either list of lifted components + archive path, or "inspection-only deliverable" note
  - Screenshots of all 4 /docs pages from running local server
- Confirm ALL Vitest and Playwright tests are green (no regressions from any task in this increment)
- Surface closure summary to `/sw:done` — do NOT mark the increment done until local-preview screenshots are captured from a running dev server

**Test Plan** (BDD):
```
Given all tasks T-001 through T-014 are complete and the local dev server is running
When the closure verification checklist executes against http://localhost:3000
Then: screenshots of all 4 /docs pages confirm the video embed appears above the first heading; .vtt network responses confirm HTTP 200 with track src populated; rg evidence documents zero references for deleted files; du delta confirms 7.5-10 MB freed; build + vitest exit codes are 0; US-003 outcome is documented — providing the complete evidence package required before /sw:done can close the increment
```

---

## AC Coverage Matrix

| AC ID | Covered By |
|---|---|
| AC-US1-01 | T-001, T-002, T-004, T-005 |
| AC-US1-02 | T-006, T-010 |
| AC-US1-03 | T-007, T-010 |
| AC-US1-04 | T-008, T-010 |
| AC-US1-05 | T-009, T-010 |
| AC-US1-06 | T-004, T-005 |
| AC-US1-07 | T-010, T-015 |
| AC-US1-08 | T-003, T-009, T-010 |
| AC-US2-01 | T-011 |
| AC-US2-02 | T-012 |
| AC-US2-03 | T-011 |
| AC-US2-04 | T-012 |
| AC-US2-05 | T-012, T-015 |
| AC-US2-06 | T-012, T-015 |
| AC-US2-07 | T-012, T-015 |
| AC-US3-01 | T-013 |
| AC-US3-02 | T-014 |
| AC-US3-03 | T-014 |
| AC-US3-04 | T-014 |
| AC-US3-05 | T-014 |
| AC-US3-06 | T-014 |

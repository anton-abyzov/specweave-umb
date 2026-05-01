---
increment: 0818-docs-inline-videos-and-dead-code-cleanup
title: "Inline /watch videos on 4 /docs pages, delete dead VideoHero + orphan video assets, lift unique scene-kit components"
type: feature
priority: P2
status: planned
created: 2026-05-01
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Inline /watch videos on 4 /docs pages, delete dead VideoHero + orphan video assets, lift unique scene-kit components

## Overview

INC-D (final increment) of the verified-skill.com video overhaul (master plan: `~/.claude/plans/curried-beaming-summit.md`). Prior increments have shipped:

- **INC-A 0810** — `src/remotion/scene-kit/` foundation + token sync. **MERGED**.
- **INC-B 0812** — Refreshed `/studio` video + new `/docs/studio` section that **already inlines** the studio video at the top of the page using `ProductDemoCard` with a wired `<track kind="captions">`. **MERGED**.
- **INC-C 0817** — `/learn` → `/watch` IA rename + 4 broken Learn101 videos rendered with Sarah VO + new `skills-manager-overview` hero composition + real WebP thumbnails. Renames `src/lib/learn/video-data.ts` → `src/lib/learn/video-catalog.ts` and renames `LazyVideoPlayer.tsx` → `WatchVideoPlayer.tsx`. **IN FLIGHT — assumed merged before INC-D implementation begins.**

INC-D delivers three coordinated cleanup outcomes that close out the master plan:

1. **Inline `/watch` videos at the top of 4 `/docs/{topic}` pages** — `/docs/getting-started`, `/docs/cli-reference`, `/docs/security-guidelines`, `/docs/plugins` each render their matching 101-series `/watch` video above the existing topic content using a NEW thin `DocVideoEmbed` server component that mirrors the INC-B `/docs/studio` precedent. The 5th candidate page (`/docs/submitting`) is explicitly resolved in this spec — see Open Question OQ-1 — with the default disposition being **defer** (the marketplace flow on `plugin-marketplace-101` is the closest fit but not a strict 1:1 with the submission path).
2. **Delete dead code and orphan video assets** — `src/app/components/homepage/VideoHero.tsx` (~150 LOC, never imported), its sibling test `src/app/components/homepage/__tests__/VideoHero.test.tsx`, `public/video/ship-while-you-sleep.mp4` (~3 MB orphan from the Feb-2026 video-first homepage that has since been replaced), and `public/video/specweave-promo.mp4` + `specweave-promo.webm` (~5.5 MB combined orphan). Total disk savings ≈ 8.5 MB. Each deletion is gated on a documented zero-references check via `rg`.
3. **Optionally lift unique components from `repositories/anton-abyzov/specweave/docs-site/remotion/` into the shared scene-kit** — inspect for `NumberTicker`, `TypewriterText`, `SectionTitle` (and any other unique primitives), determine which are truly missing from `src/remotion/scene-kit/`, lift the unique ones, and then archive the `docs-site/remotion/` directory. This story is explicitly **deferrable** — if the inspection report shows any meaningful risk (component contracts that don't match scene-kit conventions, untested code, or coupling to docs-site-specific tokens) we ship the inspection report and defer the lift to a later increment.

The new `DocVideoEmbed` component is a thin server component that:

- Reads the canonical video catalog from `src/lib/learn/video-catalog.ts` (renamed from `video-data.ts` by INC-C — assumed final by the time this increment lands).
- Lazy-loads the existing `WatchVideoPlayer` client component (renamed from `LazyVideoPlayer.tsx` by INC-C) with poster image and VTT captions wired through.
- Renders a "Watch full episode" link to `/watch/{slug}` underneath the inline player.
- Falls back gracefully (renders nothing, no thrown error, no 500) when the slug argument is missing from the catalog — this is the documented contract for `/docs/submitting` if OQ-1 resolves to "defer" or if a `/docs` page references a slug that hasn't been rendered yet.

Brand decisions remain locked per memory `project_video_brand_decisions_2026_04.md`. Local-preview verification rule per memory `feedback_video_local_preview.md` applies (closure summary must include screenshots from a running local server, not "please go check it").

## User Stories

### US-001: Inline /watch videos at top of 4 /docs pages (P1 within increment)
**Project**: vskill-platform

**As a** docs reader landing on `/docs/getting-started`, `/docs/cli-reference`, `/docs/security-guidelines`, or `/docs/plugins`
**I want** the matching 101-series `/watch` video embedded at the top of the page (above the written content) with poster, captions, and a "Watch full episode" link
**So that** I can choose whether to absorb the topic via 60–90s of video or skim the written reference, matching the multi-modal pattern already shipping on `/docs/studio` in INC-B

**Acceptance Criteria**:
- [ ] **AC-US1-01**: A new `DocVideoEmbed` server component exists at `src/app/components/docs/DocVideoEmbed.tsx`, exports a default React component accepting at minimum `{ slug: string }`, reads the catalog from `src/lib/learn/video-catalog.ts` (using the `VIDEOS` export shipped by INC-C) at module load, lazy-loads `WatchVideoPlayer` (the renamed client component from INC-C, formerly `LazyVideoPlayer`) with `poster`, `vtt`, and `mp4`/`webm` props derived from the catalog entry, and renders a `Link` (or `<a>`) labelled "Watch full episode" with `href={"/watch/" + slug}` underneath the player.
- [ ] **AC-US1-02**: `src/app/docs/getting-started/page.tsx` renders `<DocVideoEmbed slug="getting-started-101" />` as the first child of the page body, ABOVE all existing topic content — verified by a Playwright snapshot of `/docs/getting-started` showing the video element appearing before the page's first body section, and by a Vitest spec asserting the first `DocVideoEmbed` JSX child of the page component has `slug="getting-started-101"`.
- [ ] **AC-US1-03**: `src/app/docs/cli-reference/page.tsx` renders `<DocVideoEmbed slug="cli-commands-101" />` at the top of the body — verified by the same Playwright + Vitest pattern as AC-US1-02 with `slug="cli-commands-101"`.
- [ ] **AC-US1-04**: `src/app/docs/security-guidelines/page.tsx` renders `<DocVideoEmbed slug="security-scan-101" />` at the top of the body — verified by the same Playwright + Vitest pattern as AC-US1-02 with `slug="security-scan-101"`.
- [ ] **AC-US1-05**: `src/app/docs/plugins/page.tsx` renders `<DocVideoEmbed slug="plugin-marketplace-101" />` at the top of the body — verified by the same Playwright + Vitest pattern as AC-US1-02 with `slug="plugin-marketplace-101"`.
- [ ] **AC-US1-06**: When `DocVideoEmbed` is rendered with a `slug` value that is NOT present in `VIDEOS` from `src/lib/learn/video-catalog.ts`, the component returns `null` (renders nothing) without throwing — verified by a Vitest spec that calls `render(<DocVideoEmbed slug="does-not-exist" />)` and asserts the rendered output is empty (no DOM nodes, no error logged) and that the request does not throw on the server (no 500 response).
- [ ] **AC-US1-07**: For each of the 4 pages above, when loaded against the local dev server (`http://localhost:3000/docs/<slug>`), DevTools network tab shows the matching `.vtt` (e.g. `/video/watch/getting-started-101.vtt`) returning HTTP 200 and the `<track kind="captions">` is wired with a non-empty `src` — verified by a Playwright network assertion or Claude Preview MCP `preview_network` snapshot, mirroring INC-B AC-US3-04.
- [ ] **AC-US1-08**: The `/docs/submitting` page disposition is documented in this increment's plan and applied: per the resolution of Open Question OQ-1 (default = **DEFER**, no `DocVideoEmbed` added to `/docs/submitting`), `src/app/docs/submitting/page.tsx` is unchanged in this increment OR — if OQ-1 resolves to "use plugin-marketplace-101" during plan review — receives a `<DocVideoEmbed slug="plugin-marketplace-101" />` with the same Playwright + Vitest verification as AC-US1-02. The chosen disposition is recorded in `plan.md` and a one-sentence rationale is committed in the page file as a comment.

---

### US-002: Delete dead VideoHero component + orphan video assets (P1 within increment)
**Project**: vskill-platform

**As a** maintainer of the `verified-skill.com` codebase
**I want** the unused `VideoHero` component, its test, and three orphan `.mp4`/`.webm` files removed from the working tree
**So that** new contributors aren't misled into thinking these assets are referenced from somewhere, the public/ folder shrinks by ~8.5 MB (faster CI clones, smaller deploy bundles), and the homepage code surface contains only what actually renders

**Acceptance Criteria**:
- [ ] **AC-US2-01**: `rg "VideoHero" repositories/anton-abyzov/vskill-platform/src/` returns zero matches BEFORE deletion (the closure summary commits the exact `rg` invocation and its zero-line output as evidence). If the grep returns ANY match other than the file being deleted itself or its test, the deletion is blocked and the matching reference is investigated first.
- [ ] **AC-US2-02**: After AC-US2-01 verification, `src/app/components/homepage/VideoHero.tsx` and `src/app/components/homepage/__tests__/VideoHero.test.tsx` are removed from the working tree via `git rm` — verified by `git status` showing both files as deleted (D) and `find repositories/anton-abyzov/vskill-platform/src/app/components/homepage -name "VideoHero*"` returning empty.
- [ ] **AC-US2-03**: For each orphan asset (`public/video/ship-while-you-sleep.mp4`, `public/video/specweave-promo.mp4`, `public/video/specweave-promo.webm`), running `rg -F "<filename>"` (with the filename without extension AND the full path variant) across `repositories/anton-abyzov/vskill-platform/src/`, `repositories/anton-abyzov/vskill-platform/public/` (excluding the file itself), and `repositories/anton-abyzov/vskill-platform/**/*.{tsx,ts,html,mdx,md}` returns zero references BEFORE deletion. The exact `rg` invocations and their zero-line outputs are committed in the closure summary as evidence.
- [ ] **AC-US2-04**: After AC-US2-03 verification, all three orphan files are removed via `git rm` — verified by `git status` showing the three files as deleted and `ls public/video/` not containing any of `ship-while-you-sleep.mp4`, `specweave-promo.mp4`, or `specweave-promo.webm`.
- [ ] **AC-US2-05**: Disk-size delta is documented and falls in the expected range: `du -sh public/video/` measured BEFORE and AFTER the deletions, with the delta ≥ 7.5 MB and ≤ 10 MB (target ≈ 8.5 MB; range covers filesystem block-size variation). Both measurements and the computed delta are recorded in the closure summary.
- [ ] **AC-US2-06**: `npm run build` succeeds in `repositories/anton-abyzov/vskill-platform/` AFTER the deletions complete — verified by the build command exiting with code 0 and producing the standard Next.js `.next/` and `.open-next/` outputs. The build log shows no missing-module or missing-asset errors referencing any of the four deleted entities.
- [ ] **AC-US2-07**: `npx vitest run` passes in `repositories/anton-abyzov/vskill-platform/` AFTER the deletions — verified by the vitest exit code 0 with the previously-existing `VideoHero.test.tsx` correctly removed (and not appearing in test counts) and no other tests broken by the missing `VideoHero` symbol.

---

### US-003: Lift unique components from docs-site/remotion/ into scene-kit (optional, deferrable, P2)
**Project**: vskill-platform

**As a** Remotion contributor maintaining the canonical scene-kit at `src/remotion/scene-kit/`
**I want** any unique primitives from the legacy `repositories/anton-abyzov/specweave/docs-site/remotion/` directory consolidated into the shared scene-kit (and the legacy directory archived afterward)
**So that** there is exactly one source of truth for video primitives across the project — and conversely, if all components in the legacy directory are duplicates of what scene-kit already ships, we still archive the legacy directory to remove the duplication risk

**Acceptance Criteria**:
- [ ] **AC-US3-01**: An inspection report is committed to `.specweave/increments/0818-docs-inline-videos-and-dead-code-cleanup/reports/scene-kit-lift-inspection.md`. The report enumerates every `.tsx` component file under `repositories/anton-abyzov/specweave/docs-site/remotion/`, and for each component records: (a) the file path, (b) the exported component name(s), (c) whether an equivalent already exists in `src/remotion/scene-kit/` (by name or by behavior), and (d) a recommendation of one of `LIFT` (unique, lift to scene-kit), `SKIP` (duplicate of existing scene-kit primitive), or `DEFER` (lifting carries risk — coupling, untested, or contract drift).
- [ ] **AC-US3-02**: If the inspection identifies any `LIFT` candidates among the named suspects (`NumberTicker`, `TypewriterText`, `SectionTitle`) OR any other unique components, each lifted component is moved to `src/remotion/scene-kit/<ComponentName>.tsx` with the standard scene-kit conventions applied: tokens imported from `scene-kit/tokens.ts` (no inline hex), public API surface exported from `src/remotion/scene-kit/index.ts`, and a sibling test under `src/remotion/scene-kit/__tests__/<ComponentName>.test.tsx`. If the inspection identifies ZERO `LIFT` candidates (everything is `SKIP` or `DEFER`), this AC is satisfied vacuously and the closure summary records "no components lifted, all duplicates or deferred".
- [ ] **AC-US3-03**: After lift decisions are applied, the legacy directory `repositories/anton-abyzov/specweave/docs-site/remotion/` is either (a) moved to `repositories/anton-abyzov/specweave/docs-site/.archive/remotion-2026-05/` (preserving git history via `git mv`), OR (b) deleted via `git rm -r` if the directory is fully redundant after the lift. The closure summary records which option was chosen and why. The original path no longer exists in the working tree.
- [ ] **AC-US3-04**: After the archive/delete in AC-US3-03, `rg "docs-site/remotion" repositories/anton-abyzov/specweave/` returns zero references in active source files (excluding `.archive/`), and the docs-site build (`npm run build` or the canonical docs-site command, whichever applies) in `repositories/anton-abyzov/specweave/docs-site/` exits with code 0 — verified by capturing the exit code in the closure summary.
- [ ] **AC-US3-05**: This story is explicitly opt-out at plan-review time: if the inspection report (AC-US3-01) classifies all components as `DEFER` due to risk OR the user/architect rejects the lift during plan review, the implementation phase produces ONLY the inspection report (AC-US3-01) and skips AC-US3-02, AC-US3-03, AC-US3-04. In this deferred mode, the increment's status remains "complete" because the inspection IS the deliverable, and a follow-up increment is recorded under "Out of Scope" of the next planned increment (or a brainstorm note) capturing the deferred lift work.
- [ ] **AC-US3-06**: If any components are lifted (AC-US3-02 produced new files), `npx vitest run` for the scene-kit tests passes including the new sibling test files, AND a single representative consumer of scene-kit (e.g. one of the existing `src/remotion/scenes/*/script.ts`-driven compositions) is shown by `rg` to be importable without needing the lifted component path to be rewritten — i.e. the new lifted components are exported from `src/remotion/scene-kit/index.ts` so existing import patterns continue to work.

## Functional Requirements

### FR-001: `DocVideoEmbed` server component contract
`src/app/components/docs/DocVideoEmbed.tsx` is a Next.js server component (no `"use client"` directive) that accepts `{ slug: string }` and reads `VIDEOS` from `src/lib/learn/video-catalog.ts`. It looks up the entry by `slug`. If no match: returns `null`. If match: lazy-loads `WatchVideoPlayer` (via `next/dynamic` or React `lazy` + `Suspense`, whichever is consistent with how `/docs/studio` already lazy-loads its player in INC-B) and renders the player with `poster`, `vtt`, `mp4`, `webm` props derived from the catalog entry. Below the player, render a `<Link href={"/watch/" + slug}>Watch full episode</Link>` (Next.js `Link` for client-side navigation). The exact `WatchVideoPlayer` prop names are confirmed by the planner during plan.md generation against the post-INC-C player file (see OQ-2).

### FR-002: Page-level integration
For each of the 4 in-scope pages (`/docs/getting-started`, `/docs/cli-reference`, `/docs/security-guidelines`, `/docs/plugins`), the existing `page.tsx` is edited to import `DocVideoEmbed` from `@/components/docs/DocVideoEmbed` (or the project's resolved alias) and place it as the first JSX child of the page body, ABOVE all current content. No existing topic content is removed or rewritten in this increment — the embed is purely additive at the top of the page. The 5th page (`/docs/submitting`) follows the OQ-1 resolution per AC-US1-08.

### FR-003: Catalog as single source of truth
`DocVideoEmbed` MUST NOT hard-code video paths or thumbnails. All asset paths are derived from the `VIDEOS` array in `src/lib/learn/video-catalog.ts`. If the catalog entry's shape lacks any field needed by `WatchVideoPlayer`, the planner extends the catalog type (with the change tracked in `plan.md`) rather than hard-coding paths in the embed component.

### FR-004: Pre-deletion grep verification (US-002)
Every deletion in US-002 is gated on a documented `rg` invocation that returns zero references. The grep covers the full vskill-platform working tree (`src/`, `public/`, and source files including `*.tsx`, `*.ts`, `*.html`, `*.mdx`, `*.md`, and `*.json` to catch any stale catalog references). The grep output (or its zero-line emptiness) is captured in the closure summary as evidence. If a grep returns a non-zero match, the deletion is blocked until the matching reference is either removed or shown to be a comment / false-positive (with documented justification).

### FR-005: Build + test verification gate (US-002)
After all four deletions land, `npm run build` and `npx vitest run` MUST both exit zero. Failures here block closure regardless of grep cleanliness — if a deletion breaks something the grep missed, the failed build is the authoritative signal and the deletion is reverted or the missing reference is fixed.

### FR-006: Inspection-first sequencing for US-003
US-003 implementation begins with the inspection report (AC-US3-01). Lift / skip / defer decisions are made AFTER the report is reviewed (architect or user gate). The implementer MUST NOT lift components before the inspection is committed and reviewed — this prevents accidentally lifting duplicates or risky code.

### FR-007: Archive preserves git history
If US-003 archives the legacy directory rather than deleting it (AC-US3-03 option a), the move uses `git mv` so the legacy directory's git history is preserved at the new archive path. The archive folder name follows the convention `.archive/remotion-YYYY-MM/` so future archive operations don't collide.

## Success Criteria

- All 4 in-scope `/docs/*` pages render their matching `/watch` video at the top, with poster, captions wired (VTT 200), and a working "Watch full episode" link to `/watch/{slug}`. Verified locally on `http://localhost:3000` per the local-preview rule.
- The 5th page (`/docs/submitting`) disposition is documented and applied (default DEFER, OR `plugin-marketplace-101` per OQ-1 resolution).
- `VideoHero.tsx` + its test + the three orphan `.mp4`/`.webm` files are removed; `du -sh public/video/` confirms ≥ 7.5 MB reduction; `npm run build` and `npx vitest run` are green.
- US-003 either ships the inspection report + lift + archive, OR ships the inspection report alone with explicit defer reasoning.
- Closure summary includes `rg` evidence (US-002), build log excerpts, disk-size delta, and Claude Preview screenshots of all 4 in-scope `/docs/*` pages with the new video at the top (per `feedback_video_local_preview.md`).
- All AC-tagged tests pass: `npx vitest run` and `npx playwright test` (where applicable to the Playwright scenarios in US-001).

## Out of Scope

- **Inline videos on any `/docs/*` page beyond the 4 confirmed in scope** (`getting-started`, `cli-reference`, `security-guidelines`, `plugins`). `/docs/submitting` is explicitly handled via OQ-1 with default DEFER. Other pages — `/docs/quickstart`, `/docs/faq`, `/docs/integrations/*`, etc. — are not in scope.
- **Homepage hero refresh / replacement / re-design** — separate future increment per master plan.
- **Rendering any new videos** — all 5 referenced videos (`getting-started-101`, `cli-commands-101`, `security-scan-101`, `plugin-marketplace-101`, `skills-manager-overview`) are rendered by INC-C and assumed available before this increment ships. INC-D does not invoke Remotion render at all.
- **`specweave-workflow-101` video** — deferred indefinitely, stays `status: "coming-soon"` in `video-catalog.ts`.
- **`studio-tour` long-form `/watch` entry** — deferred per master plan; the `/studio` inline already exists from INC-B.
- **`/watch` library page edits** — INC-C ships and stabilizes `/watch`; this increment does not re-touch `src/app/watch/`.
- **YouTube re-uploads or R2 / CDN sync** — closure ships the page edits and orphan deletions only; CDN promotion is a separate ops step.
- **Modifying `src/remotion/scene-kit/` beyond US-003 lifts** — no other scene-kit changes (no new primitives unrelated to the lift, no token edits, no breaking API changes).
- **Modifying `WatchVideoPlayer` beyond what `DocVideoEmbed` requires as a caller** — if the player needs a new prop to support inline `/docs/*` usage, the prop addition lives in this increment, but no broader player refactor.
- **Auto-generating `/docs/{slug}` ↔ `/watch/{slug}` mapping for future videos** — this increment hardcodes 4 mappings; an auto-mapping helper is a future increment if the matrix grows.

## Dependencies

- **INC-A (0810) — MERGED**: `src/remotion/scene-kit/` (consumed by US-003 lift target), `BRAND_COLORS`, scene-kit conventions for new components.
- **INC-B (0812) — MERGED**: `/docs/studio` precedent for inline-video pattern, `<track kind="captions">` wiring at `src/app/components/shared/VideoPlayer.tsx`, `ProductDemoCard` props surface (`captionsSrc`, `mp4`, etc.) referenced as the architectural model for `DocVideoEmbed`.
- **INC-C (0817) — IN FLIGHT, MUST MERGE BEFORE INC-D IMPLEMENTATION**: `src/lib/learn/video-catalog.ts` (renamed from `video-data.ts`), `WatchVideoPlayer` (renamed from `LazyVideoPlayer.tsx`), the 4 rendered 101-series videos under `public/video/watch/`, and the `skills-manager-overview` composition. INC-D's US-001 cannot ship until INC-C lands these renames and renders.
- **Local dev server** at `http://localhost:3000` for the Playwright + preview verification.
- **`rg` (ripgrep)** available in the build environment for the FR-004 pre-deletion grep gates.
- **Brand decisions locked**: memory `project_video_brand_decisions_2026_04.md`.
- **Local-preview verification rule**: memory `feedback_video_local_preview.md`.
- **Sequencing**: this increment closes the master plan `~/.claude/plans/curried-beaming-summit.md` for the 4-part video overhaul. No dependent increments are queued behind it.

## Open Questions

- **OQ-1**: Should `/docs/submitting` get an inline video, and if so, which slug? The submission flow on `/docs/submitting` overlaps thematically with `plugin-marketplace-101` (which covers the marketplace browse/install/publish flow) but is not a strict 1:1 — the submitting page is more about *contributing to* the marketplace whereas the video is more about *consuming* it. **Default disposition: DEFER** (no embed on `/docs/submitting` in this increment; revisit when a `submitting-101` or `publishing-101` video is rendered in a future increment). **Alternative resolution accepted at plan review: use `plugin-marketplace-101`** if the architect or user judges the overlap close enough. The chosen disposition is locked into AC-US1-08 and into `plan.md` before implementation begins.
- **OQ-2**: Does `WatchVideoPlayer` (renamed from `LazyVideoPlayer` in INC-C) expose the prop surface (`poster`, `vtt`, `mp4`, `webm`) that `DocVideoEmbed` needs, or does INC-D need to extend the player's prop signature? **Resolution path**: the planner reads the post-INC-C `WatchVideoPlayer.tsx` during `plan.md` generation and either (a) confirms the props match and FR-001 is unchanged, or (b) records a player-prop-extension task in `tasks.md` with the new prop names. This is a planning-phase resolution, not a spec-phase ambiguity.
- **OQ-3**: For US-003, if the inspection report finds zero unique components (everything in `docs-site/remotion/` duplicates scene-kit), should we still archive the legacy directory or just delete it outright? **Default disposition: ARCHIVE** (preserves git history at low cost, lets us un-archive if a future need surfaces). DELETE is acceptable if the architect explicitly green-lights it during plan review.

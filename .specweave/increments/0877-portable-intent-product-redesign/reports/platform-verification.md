# Verified Skills product redesign — verification

Commit: `a1815ec` (`0877: redesign skills discovery around usefulness and evidence`). Worktree: `/tmp/vskill-platform-0877-product`. Production preview: `http://127.0.0.1:3097` during this run. No deployment performed by this lane.

## Delivered behavior

The homepage now separates discovery, source/security inspection, and usefulness evaluation. Its interactive evidence guide supports keyboard navigation. The catalog anchor, live search dialog, categories, and trending API consumers remain in place. Navigation exposes methodology, Studio, docs, and secondary resources. `/methodology` explains the evidence limits and links to primary sources. `/skill-studio` permanently redirects to the canonical `/studio`.

Studio retains published platform-aware desktop downloads, CLI installation, the walkthrough, captions, and chapter seeking. The existing recording is explicitly identified as vskill 1.0.13. The walkthrough uses bundled native video assets, avoiding the former embedded-player dependency. Product copy distinguishes a local workspace from remote model-provider calls and removes guarantees of no data egress or universal model support.

The Kie-generated inspection illustration is optimized to a 138,532-byte WebP. Responsive warm-neutral/ink styling, dark-theme handling, mobile navigation, and reduced-motion compatibility were visually checked. The product illustration is decorative, not presented as a real evaluation result.

## Executed checks

- `npm run build`: passed, including the final build run through the T-05 ledger command. Output: `task-T-05.log` in this reports directory.
- Nine focused Vitest files: 54 tests passed on dependencies restored with `npm ci`. Includes evidence-guide keyboard navigation, search autofocus behavior, navigation, sitemap, and Studio content. Log: `artifacts/platform-redesign/tests-locked.log`.
- Targeted coverage for `EvidenceGuide.tsx` and `HeroSearch.tsx`: 98.39% lines/statements, 92% branches, 77.77% functions. This is component coverage, not full-application coverage. HTML/data: `artifacts/platform-coverage/`.
- Production-build Playwright: 2 tests passed. Covers desktop evidence tabs/keyboard, search open/escape, catalog anchor, canonical Studio redirect, loaded native video and chapter seeking, methodology route, and mobile navigation/overflow. Log: `artifacts/platform-redesign/e2e-final.log`.
- Browser automation used explicit `headless: true`, `PWDEBUG=0`, `PLAYWRIGHT_HTML_OPEN=never`; no visible browser or personal browser was used.
- Final screenshots: `artifacts/platform-redesign/`. Selected desktop/mobile homepage, Studio, methodology and dark-theme captures were inspected; final mobile homepage fold and video contrast/poster were rechecked after adjustments.

## Existing limits, not passing checks

`npx tsc --noEmit --pretty false` reports 314 errors across existing application/test code. No new product component appears in that output; the unchanged nullable `searchParams` expression in the modified trust page still appears. A follow-up comparison checked out the pre-change commit `54535ca` in a separate worktree and reused identical installed dependencies. Running both source trees with identical nonincremental TypeScript configuration (excluding generated `.next`/`.open-next` files and generated `next-env.d.ts`) gave 291 baseline diagnostics and 290 redesign diagnostics. Matching by file, diagnostic code, and message after normalizing absolute paths found no added source diagnostic. The original 314-result full check includes generated artifacts and is not claimed to be an exact baseline count. Both source logs and parsed diagnostic lists are preserved under `artifacts/platform-redesign/`. The project already configures Next to ignore build-time TypeScript errors. This redesign does not claim a clean whole-project typecheck.

`CI=1 npm run lint` exits 1 because the repository has no configured ESLint setup and Next prompts interactively. No lint rule was weakened or test deleted. Logs: `artifacts/platform-redesign/types.log` and `lint.log`.

The local preview has no production database/KV bindings. Existing catalog fallback statistics are therefore shown and dynamic category/trending data are empty. The local end-to-end check verifies the search interaction, not a successful query against production catalog data. Verify real catalog queries after deployment. Production APIs and database schemas were not changed.

The build expects the sibling vskill checkout to generate supported-agent data; this worktree used a local node_modules/vskill symlink to the existing checkout. The generated SpecWeave version-only change was restored after builds. The initial UI commit changed no dependency manifest or lockfile. The later CI repair pins the accessibility runner in devDependencies and the lockfile; existing dependency versions remain unchanged.

## CI repair follow-up

The original PR 68 private-repo E2E workflow failed before dependency installation because its cache and working-directory paths assumed an umbrella checkout. The workflow now runs from the standalone repository root on Node 22, checks out pinned companion vskill source for build-time agent/count generation, and enforces noninteractive headless Playwright settings. The existing 0826 suite is retained: test discovery lists 46 tests across eight files. The product E2E still passes (2 tests) with the shared headless configuration. Remote CI results are tracked separately; test discovery is not execution.

The local pre-commit scanner flagged the workflow’s pre-existing disposable `vskill` PostgreSQL test credentials as a secret URI. The original file and complete staged diff were inspected to confirm the URI was unchanged and local to the CI service. The documented false-positive commit path was used for this CI-only change; no production secret was introduced.

## T18: CI presentation contracts and contrast

The full unit CI run at `85096d0` executed 5,817 passing, 6 failing and 14 skipped tests. The failures were obsolete homepage assertions (a removed mock heading, a walkthrough now routed to Studio, and the removed six-icon strip) plus a source-regex assertion requiring the old four-color Studio feature array. Updated assertions check the real H1, catalog link, canonical Studio links, three evidence tabs, retained category/search components and JSON-LD. Recording colors are still checked against the shared light/dark application tokens; their obsolete marketing-feature dependency was removed. No runtime test was deleted or skipped.

The exact H1 assertion initially failed because JSX line breaks visually separated words without text-node spaces. The markup now preserves word spacing for accessible names and copying. A headless axe sweep initially found low-contrast search/copy hints and Studio download metadata on warm surfaces, plus the Studio keyboard shortcut on its tinted button. Product hints inherit the product's readable muted color; the shortcut uses the existing readable navigation token.

Verification after those changes:

- `npm run build`: passed.
- Twelve focused Vitest files: 75 tests passed, including all changed contracts and existing navigation, Studio, search and keyboard tests.
- Production-build Playwright product flow: 2 passed, 0 retries.
- Headless axe on `/`, `/methodology`, and `/studio`, at 1440px and 390px in both light and dark modes: all 12 combinations have zero serious/critical violations under WCAG 2 A/AA and WCAG 2.1 A/AA tags. This threshold does not claim a full manual accessibility certification.

Before/after axe JSON, repeatable script, full unit CI failure log, focused green output, build and E2E logs are preserved in `artifacts/platform-redesign/0877-*` and `product-axe.cjs`. The repaired 0826 workflow has reached actual private-repository tests; its independent final result remains to be reported.

## T25: populated catalog preflight

The local preview does not have production catalog bindings, so its accessibility result could not cover populated category/trending rows. A separate **synthetic preflight**, without modifying the public site, copied current public category/trending DOM into the local product catalog container and applied the reviewed product stylesheet. It found inherited repository-link contrast3.71:1 and positive-momentum contrast2.51:1 in light mode. The dark scan badge also measured4.17:1.

Commit `495f0fa` adds seven lines scoped to `.product-catalog-data`: outbound repository links and positive momentum use the product accent, and the dark scan-badge indigo is lightened. The same populated-DOM check now reports zero serious/critical violations at1440/390px in both themes. This is additional preflight evidence, **not a deployed-data verification**; the final release check must exercise real production catalog data. No source/API/catalog behavior or badge label changed.

## T26: authenticated account control

The repaired authenticated0826 suite exposed `button-name` on the existing avatar fallback. Commit `1673da8` adds `aria-label="Account menu"` without changing authentication or interaction behavior. Two rendered regressions, covering both a present and missing avatar, first failed on the unnamed control. After the one-attribute fix, those checks verify its accessible name, menu relationship, expanded state, account-settings link and Escape dismissal. Both new tests plus14 existing account-page tests pass. Full exact-head CI and release verification follow separately.

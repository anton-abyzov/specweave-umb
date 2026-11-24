# Verify — 0877-portable-intent-product-redesign

PASS · 2026-09-14T18:46:17.567Z · commands from explicit

## Commands

### `cd /tmp/specweave-0877-root && node scripts/lint-skills.mjs && node scripts/lint-docs-refs.mjs` → exit 0 (0s)

```
lint-skills: 37 files clean
docs-refs: OK — 154 pages, 10 skills, 80 CLI commands.
```

### `cd /tmp/specweave-0877-root/docs-site && npx vitest run src/__tests__/docusaurus-config.test.ts src/__tests__/sidebars.test.ts src/theme/Footer/__tests__/Footer.test.tsx` → exit 0 (1s)

```

 RUN  v4.0.18 /private/tmp/specweave-0877-root/docs-site

 ✓ src/__tests__/docusaurus-config.test.ts (4 tests) 2ms
 ✓ src/__tests__/sidebars.test.ts (7 tests) 3ms
 ✓ src/theme/Footer/__tests__/Footer.test.tsx (5 tests) 39ms

 Test Files  3 passed (3)
      Tests  16 passed (16)
   Start at  14:46:13
   Duration  669ms (transform 186ms, setup 290ms, import 275ms, tests 44ms, environment 952ms)
```

### `cd /tmp/specweave-0877-root && node scripts/release/preflight-publish.mjs` → exit 0 (3s)

```
[preflight] ok — tarball carries 4125 entries including bin/specweave.js, the dist/ modules bin imports, dist/dashboard/** and both plugin manifests
```

## Acceptance criteria

8/8 checked

| AC | Done | Text |
|---|---|---|
| AC-01 | x | Research report distinguishes sourced facts from product hypotheses and records business value, rejected alternatives, integrations strategy, and kill criteria. |
| AC-02 | x | Dashboard reads current ledger tasks and plain acceptance criteria, refreshes on authoritative file changes, and shows accurate completion/evidence. |
| AC-03 | x | Work board supports persistent intent items with optional increment links, clear summaries, state movement by drag/drop and accessible controls, plus honest harness/model/effort execution history. |
| AC-04 | x | SpecWeave website presents portable intent and verified progress through a responsive, layered design with useful generated graphics and working navigation. |
| AC-05 | x | Verified Skills website presents scoped expertise, provenance, security evidence, and measured usefulness honestly through a responsive, layered design. |
| AC-06 | x | vskill cleanup and removal respect scope, preserve unrelated global installations, and include regression coverage. |
| AC-07 | x | Personal/project skill inventory, reversible removals, retained expertise, and recovery manifest are documented; unnecessary hooks are removed or made optional without losing supported handoffs. |
| AC-08 | x | Relevant builds, tests, lint, coverage and headless E2E pass; failures outside scope are recorded accurately; review findings resolved; release/install/deploy evidence is recorded. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | codex-root | Committed research; both supplied OpenAI sources read; prim… |  |
| T-02 | done | codex-dashboard | specweave b3d5df405; npx vitest run tests/unit/dashboard: 2… |  |
| T-03 | done | codex-root | 1489f3891; root build pass; 186 hooks/doctor tests pass; sk… |  |
| T-04 | done | codex-skills | 8ce135ed236759c38f65a09b68f8550128ff6497; full npm test -- … |  |
| T-05 | done | codex-product | cd /tmp/vskill-platform-0877-product && npm run build → exi… |  |
| T-06 | done | codex-root | Final source5d9a91cb; all task PRs merged; SpecWeave2.1.0/v… |  |
| T-07 | done | codex-sync | 2776db874c37f493bd28bbbb9cd0f9e57ad04a4d; 894 broad sync te… |  |
| T-08 | done | codex-sync | 30d272e60; 25 files 225 dashboard tests pass; full build an… |  |
| T-09 | done | codex-root | 6c98afff8; three supported session-ID regressions failed fi… |  |
| T-10 | done | codex-dashboard | vskill 010a49a; failing ownership test first 3 red; 6 targe… |  |
| T-11 | done | codex-product | 85096d0; repaired standalone checkout/Node 22/headless CI, … |  |
| T-12 | done | codex-dashboard | SpecWeave cost identity commit; 25 dashboard test files 230… |  |
| T-13 | done | codex-product | cd /tmp/specweave-0877-intent-context && npx vitest run tes… |  |
| T-14 | done | codex-sync | 92039676b; 61 unit and 31 CLI E2E pass with CI=true GITHUB_… |  |
| T-15 | done | codex-root | 9a9edda86;6hook tests pass;CI logs confirm invalid Windows … |  |
| T-16 | done | codex-dashboard | specweave 188aa2c63; 2 regressions failed first; 17 work-bo… |  |
| T-17 | done | codex-skills | vskill source 0e18781; local installed version 1.1.1; rebui… |  |
| T-18 | done | codex-product | e2fe683; npm run build passed; 75 focused Vitest tests pass… |  |
| T-19 | done | codex-dashboard | specweave 4bc26e486; 2 portable regressions and existing te… |  |
| T-20 | done | codex-dashboard | specweave ecaa15073; 3 relocation/path regressions failed f… |  |
| T-21 | done | codex-product | 51032632b3da86de89ee262b257735109c9f21a6; independently rev… |  |
| T-22 | done | codex-product | e6b45b0; root independent review approved; local production… |  |
| T-23 | done | codex-dashboard | specweave c502b35d6; final docs build passed; 7 headless en… |  |
| T-24 | done | codex-skills | source 8052b9bd9; installed CLI 2.1.0; Codex + all 4 Claude… |  |
| T-25 | done | codex-product | 495f0fa; root independent review approved; populated public… |  |
| T-26 | done | codex-product | 1673da8; root independent approval;2 accessible-name/state/… |  |
| T-27 | done | codex-dashboard | specweave 6a2750ac2; exactly6docs,4current guides and2histo… |  |
| T-28 | done | codex-root | 59fd2c4d5; reproduced current CI ENOENT in lifecycle-pointe… |  |
| T-29 | done | codex-product | 51032632b3da86de89ee262b257735109c9f21a6; independently rev… |  |
| T-30 | done | codex-dashboard | vskill-platform52eabeb; populatedSSR2redregressionsfirst;23… |  |
| T-31 | done | codex-root | 991f29e0b; independent core review approved corrected seman… |  |
| T-32 | done | codex-skills | 3a41c2882ecbe71a7510c1f8b476ab20583c2de1; unchanged focused… |  |
| T-33 | done | codex-product | 9d3e59216; strict docs npm build passed; explicit-headless1… |  |
| T-34 | done | codex-root | 5a5c5a9f0; public HTML report deployed in Pages34882131675 … |  |
| T-35 | done | codex-core | dc7db569e; exact CI README sync red exit1 for two relative … |  |
| T-36 | done | codex-root | fb727eaab; two regressions failed before repair;16focusedte… |  |

36/36 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open

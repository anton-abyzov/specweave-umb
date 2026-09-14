# 0877 tasks

<!-- SW:BOARD -->
| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | codex-root | Committed research; both supplied OpenAI sources read; prim… |  |
| T-02 | done | codex-dashboard | specweave b3d5df405; npx vitest run tests/unit/dashboard: 2… |  |
| T-03 | done | codex-root | 1489f3891; root build pass; 186 hooks/doctor tests pass; sk… |  |
| T-04 | done | codex-skills | 8ce135ed236759c38f65a09b68f8550128ff6497; full npm test -- … |  |
| T-05 | done | codex-product | cd /tmp/vskill-platform-0877-product && npm run build → exi… |  |
| T-06 | claimed | codex-root |  |  |
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
| T-21 | claimed | codex-product |  |  |
| T-22 | done | codex-product | e6b45b0; root independent review approved; local production… |  |
| T-23 | done | codex-dashboard | specweave c502b35d6; final docs build passed; 7 headless en… |  |
| T-24 | done | codex-skills | source 8052b9bd9; installed CLI 2.1.0; Codex + all 4 Claude… |  |
| T-25 | done | codex-product | 495f0fa; root independent review approved; populated public… |  |
| T-26 | done | codex-product | 1673da8; root independent approval;2 accessible-name/state/… |  |
| T-27 | done | codex-dashboard | specweave 6a2750ac2; exactly6docs,4current guides and2histo… |  |
| T-28 | done | codex-root | 59fd2c4d5; reproduced current CI ENOENT in lifecycle-pointe… |  |
| T-29 | claimed | codex-product |  |  |

26/29 done · 0 skipped · 3 claimed · 0 blocked · 0 stale · 0 open
<!-- /SW:BOARD -->

### T-01 Research and product decisions
- AC: AC-01 | Files: reports/research.md, reports/brainstorm.md | Test: manual: verify sources and explicitly label hypotheses
- [x] done by codex-root 2026-09-14T06:52:07.927Z — Committed research; both supplied OpenAI sources read; primary source comparisons, hypotheses, rejected alternatives an…

### T-02 Live intent dashboard and authoritative progress
- AC: AC-02, AC-03 | Files: specweave/src/dashboard/, specweave/tests/dashboard/, specweave/tests/unit/dashboard/, specweave/tests/e2e/dashboard/, specweave/src/core/intent/, specweave/src/cli/commands/intent.ts, specweave/bin/specweave.js | Test: cd /tmp/specweave-0877-dashboard && npx vitest run tests/unit/dashboard
- [x] done by codex-dashboard 2026-09-14T06:18:02.180Z — specweave b3d5df405; npx vitest run tests/unit/dashboard: 24 files, 182 tests passed; npm run build and client tsc pass…

### T-03 SpecWeave product site and focused hooks
- AC: AC-04, AC-07 | Files: specweave/docs-site/, specweave/README.md, specweave/plugins/, specweave/src/templates/, specweave/src/core/doctor/checkers/hooks-checker.ts, specweave/tests/unit/hooks/, specweave/tests/unit/core/doctor/ | Test: cd /tmp/specweave-0877-root && npm run build && npm run lint:skills
- [x] done by codex-root 2026-09-14T06:10:28.034Z — 1489f3891; root build pass; 186 hooks/doctor tests pass; skill/docs lint pass; docs build and 5 footer tests pass; prod…

### T-04 Scoped vskill maintenance and personal cleanup
- AC: AC-06, AC-07 | Files: vskill/src/, vskill/tests/, reports/skills-audit.md, reports/cleanup-manifest.json | Test: cd /tmp/vskill-0877-skills && npm test
- [x] done by codex-skills 2026-09-14T06:08:57.642Z — 8ce135ed236759c38f65a09b68f8550128ff6497; full npm test -- --maxWorkers=4 under Node 22 exited 0: 623 files, 6158 passe…

### T-05 Verified Skills product site
- AC: AC-05 | Files: vskill-platform/src/app/, vskill-platform/src/components/, vskill-platform/public/, vskill-platform/tests/ | Test: cd /tmp/vskill-platform-0877-product && npm run build
- [x] done by codex-product 2026-09-14T06:13:53.029Z — cd /tmp/vskill-platform-0877-product && npm run build → exit 0 log: .specweave/increments/0877-portable-intent-product-…

### T-06 Review verification releases and report
- AC: AC-08 | Files: reports/, specweave/package.json, specweave/package-lock.json, specweave/CHANGELOG.md, specweave/.claude-plugin/, specweave/plugins/specweave/.claude-plugin/plugin.json, vskill/package.json, vskill/package-lock.json, vskill/CHANGELOG.md, vskill/.github/workflows/npm-release.yml, AGENTS.md | Test: manual: independent review; builds and headless E2E; registry and deployment verification
- [ ] claimed by codex-root since 2026-09-14T06:15:51.331Z

### T-07 Visible integration failures
- AC: AC-01, AC-08 | Files: specweave/src/sync/external-change-puller.ts, specweave/src/cli/commands/sync.ts, specweave/tests/unit/sync/, specweave/tests/unit/cli/commands/sync* | Test: manual: regression tests distinguish unavailable provider from no changes and retain successful partial results
- [x] done by codex-sync 2026-09-14T06:18:59.384Z — 2776db874c37f493bd28bbbb9cd0f9e57ad04a4d; 894 broad sync tests and 27 final targeted tests pass; npm run build and tsc …

### T-09 Preserve supported session IDs in hook fast path
- AC: AC-07, AC-08 | Files: specweave/plugins/specweave/hooks/run.mjs, specweave/tests/unit/hooks/minimal-hooks.test.ts | Test: cd /tmp/specweave-0877-root && npx vitest run tests/unit/hooks
- [x] done by codex-root 2026-09-14T06:23:08.367Z — 6c98afff8; three supported session-ID regressions failed first; all hooks tests pass in reports/hook-session-id-green.l…

### T-08 Live native session refresh and independent dashboard review
- AC: AC-03, AC-08 | Files: specweave/src/dashboard/client/src/pages/WorkPage.tsx, specweave/src/dashboard/server/data/intent-store.ts, specweave/src/dashboard/server/data/dashboard-task-board.ts, specweave/src/dashboard/server/data/work-projection.ts, specweave/tests/dashboard/work-board.e2e.mjs, specweave/src/dashboard/server/data/dashboard-data-aggregator.ts, specweave/tests/unit/core/dashboard/dashboard-data-aggregator.test.ts, specweave/tests/unit/dashboard/work-board.test.ts, reports/dashboard-independent-review.md | Test: cd /tmp/specweave-0877-sync && npm run build && PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never node tests/dashboard/work-board.e2e.mjs
- [x] done by codex-sync 2026-09-14T06:27:40.976Z — 30d272e60; 25 files 225 dashboard tests pass; full build and client tsc pass; 13-flow built-server headless E2E includi…

### T-10 Preserve nested vskill installation ownership
- AC: AC-06, AC-08 | Files: vskill/src/commands/remove.ts, vskill/src/commands/cleanup.ts, vskill/src/lockfile/local-root.ts, vskill/src/commands/remove.test.ts, vskill/src/commands/__tests__/cleanup-scope.test.ts, vskill/src/lockfile/local-root.test.ts, vskill/src/commands/__tests__/remove-ownership.test.ts, reports/review-vskill.md, reports/review-vskill.json | Test: cd /tmp/vskill-0877-review && npx vitest run src/commands/remove.test.ts src/commands/__tests__/remove-ownership.test.ts src/commands/__tests__/cleanup-scope.test.ts src/lockfile/local-root.test.ts
- [x] done by codex-dashboard 2026-09-14T06:26:33.161Z — vskill 010a49a; failing ownership test first 3 red; 6 targeted test files 43 passed; npm run build passed; independent …

### T-11 Repair platform CI checkout paths and headless execution
- AC: AC-08 | Files: vskill-platform/.github/workflows/0826-e2e.yml, vskill-platform/playwright.config.ts, vskill-platform/package.json, vskill-platform/package-lock.json, reports/platform-verification.md, reports/platform-deployment.md | Test: manual: validate workflow paths, list retained 0826 tests, run headless product E2E, inspect CI after push
- [x] done by codex-product 2026-09-14T06:52:32.019Z — 85096d0; repaired standalone checkout/Node 22/headless CI, pinned axe without changing existing package versions, guard…

### T-12 Preserve model identity and unknown usage estimates
- AC: AC-03, AC-08 | Files: specweave/src/dashboard/server/data/cost-aggregator.ts, specweave/src/dashboard/server/data/dashboard-data-aggregator.ts, specweave/src/dashboard/types.ts, specweave/src/dashboard/client/src/pages/CostsPage.tsx, specweave/src/dashboard/client/src/pages/OverviewPage.tsx, specweave/tests/unit/dashboard/cost-aggregator*.test.ts, specweave/tests/unit/core/dashboard/dashboard-data-aggregator.test.ts, specweave/tests/dashboard/cost-honesty.e2e.mjs | Test: cd /tmp/specweave-0877-dashboard && npx vitest run tests/unit/dashboard tests/unit/core/dashboard/dashboard-data-aggregator.test.ts
- [x] done by codex-dashboard 2026-09-14T06:32:47.115Z — SpecWeave cost identity commit; 25 dashboard test files 230 passed; npm build and client tsc passed; headless cost-hone…

### T-13 Make lightweight intents portable across sessions
- AC: AC-03, AC-07, AC-08 | Files: specweave/src/core/session/work-handoff.ts, specweave/src/core/session/work-handoff.test.ts, specweave/src/core/hooks/handlers/session-start.ts, specweave/src/core/hooks/handlers/session-start.test.ts, specweave/src/templates/AGENTS.md.template, specweave/src/templates/CLAUDE.md.template, specweave/src/core/intent/, specweave/tests/unit/hooks/ | Test: manual: regression tests fail first and pass after portable intent discovery; build succeeds
- [x] done by codex-product 2026-09-14T06:39:17.200Z — cd /tmp/specweave-0877-intent-context && npx vitest run tests/unit/hooks/lightweight-intents.test.ts src/core/session/w…

### T-15 Portable hook fixture and documentation readiness
- AC: AC-08 | Files: specweave/tests/unit/hooks/minimal-hooks.test.ts, specweave/.github/workflows/docs-build.yml | Test: manual: preserve session-ID regression coverage with Windows-valid names; wait for documented HTTP server readiness before crawling
- [x] done by codex-root 2026-09-14T06:36:55.353Z — 9a9edda86;6hook tests pass;CI logs confirm invalid Windows colon fixture and HTTP readiness race; all assertions retain…

### T-14 Portable CI paths and deterministic init fixtures
- AC: AC-08 | Files: specweave/tests/unit/sync/sync-throttle-wiring.test.ts, specweave/tests/unit/cli/commands/init-*.test.ts, specweave/tests/unit/core/validation/project-validation.test.ts, specweave/tests/e2e/cli/, specweave/tests/e2e/lifecycle/, specweave/tests/fixtures/git-hooks/pre-commit-1x.template, reports/ci-portability.md | Test: manual: reproduce CI failures with CI=1; preserve assertions and run affected unit/E2E suites
- [x] done by codex-sync 2026-09-14T06:44:03.610Z — 92039676b; 61 unit and 31 CLI E2E pass with CI=true GITHUB_ACTIONS=true canonical TMPDIR; 31 E2E also pass default work…

### T-16 Isolate corrupt intent snapshots and reject unsafe writes
- AC: AC-02, AC-03, AC-08 | Files: specweave/src/dashboard/server/data/intent-store.ts, specweave/tests/unit/dashboard/work-board.test.ts | Test: cd /tmp/specweave-0877-dashboard && npx vitest run tests/unit/dashboard/work-board.test.ts && npm run build
- [x] done by codex-dashboard 2026-09-14T06:38:44.540Z — specweave 188aa2c63; 2 regressions failed first; 17 work-board tests passed including malformed snapshots, execution ti…

### T-18 Validate the redesigned UI and repair contrast
- AC: AC-05, AC-08 | Files: vskill-platform/src/app/product.css, vskill-platform/src/app/page.tsx, vskill-platform/src/app/studio/components/FindNavButton.tsx, vskill-platform/src/app/__tests__/page.test.tsx, vskill-platform/src/remotion/scene-kit/__tests__/tokens.test.ts, vskill-platform/src/remotion/scene-kit/tokens.ts, reports/platform-verification.md | Test: manual: updated presentation contracts pass; headless axe has zero serious/critical violations across desktop/mobile product pages; production build and product E2E pass
- [x] done by codex-product 2026-09-14T06:54:20.245Z — e2fe683; npm run build passed; 75 focused Vitest tests passed; 2 production product E2E passed; headless axe12 route/vi…

### T-17 Install and verify packaged vskill 1.1.1 locally
- AC: AC-08 | Files: reports/vskill-local-install.md, reports/vskill-local-install-*, user-global vskill package registration | Test: manual: preserve rollback package and link evidence; verify installed vskill 1.1.1 and packaged Skill Studio in headless browser
- [x] done by codex-skills 2026-09-14T06:52:38.465Z — vskill source 0e18781; local installed version 1.1.1; rebuilt tarball preflight passed; packaged UI health/content/deta…

### T-19 Keep portable context and dashboard snapshot validation consistent
- AC: AC-03, AC-08 | Files: specweave/src/core/intent/types.ts, specweave/src/core/intent/validation.ts, specweave/src/core/intent/portable-context.ts, specweave/src/dashboard/work-types.ts, specweave/src/dashboard/server/data/intent-store.ts, specweave/tests/unit/hooks/lightweight-intents.test.ts, specweave/src/templates/AGENTS.md.template, specweave/src/templates/CLAUDE.md.template, reports/review-final-portability.md | Test: cd /tmp/specweave-0877-portability && npx vitest run tests/unit/hooks/lightweight-intents.test.ts tests/unit/hooks/minimal-hooks.test.ts tests/unit/dashboard/work-board.test.ts tests/unit/cli/helpers/init/instruction-templates.test.ts && npm run build
- [x] done by codex-dashboard 2026-09-14T06:53:24.275Z — specweave 4bc26e486; 2 portable regressions and existing template limit failed first; 4 focused files 47 tests passed; …

### T-20 Keep owned handoff pointers valid after project relocation
- AC: AC-03, AC-07, AC-08 | Files: specweave/src/core/hooks/handlers/session-start.ts, specweave/src/core/session/work-handoff.ts, specweave/src/core/session/handoff-pointer.ts, specweave/tests/unit/hooks/lightweight-intents.test.ts, specweave/src/core/session/work-handoff.test.ts, reports/review-final-portability.md | Test: cd /tmp/specweave-0877-portability && npx vitest run tests/unit/hooks/lightweight-intents.test.ts src/core/session/work-handoff.test.ts && npm run build
- [x] done by codex-dashboard 2026-09-14T06:53:24.710Z — specweave ecaa15073; 3 relocation/path regressions failed first; 26 focused handoff tests passed; final 11 lightweight …

### T-21 Release and verify the redesigned Verified Skills site
- AC: AC-05, AC-08 | Files: reports/platform-deployment.md, reports/platform-verification.md, reports/artifacts/platform-redesign/ | Test: manual: independent root approval, exact-head unit CI green, normal PR merge, fresh Worker build plus queue-health build/deployment checks, explicit-headless production catalog/Studio/video/mobile and axe verification
- [ ] claimed by codex-product since 2026-09-14T06:54:58.051Z

### T-22 Provide authenticated disposable CI fixtures
- AC: AC-08 | Files: vskill-platform/.github/workflows/0826-e2e.yml, reports/platform-deployment.md | Test: manual: confirm original trace sign-in500/missingJWT prerequisite; ephemeral masked signing key plus sign-in200 readiness, unchanged production auth/tests; inspect new E2E execution
- [x] done by codex-product 2026-09-14T07:04:02.262Z — e6b45b0; root independent review approved; local production probe absent-key500/no cookie, ephemeral-key200/cookie; wor…

### T-24 Install SpecWeave 2.1.0 and refresh native plugins
- AC: AC-02, AC-08 | Files: reports/specweave-local-install*, user-global SpecWeave package, Codex/Claude sw plugin caches and registrations | Test: manual: preserve private rollback archive; verify installed CLI 2.1.0, both native plugin manifests and exact SessionStart/Stop hook set, independent user hooks unchanged, packaged dashboard startup
- [x] done by codex-skills 2026-09-14T07:10:28.249Z — source 8052b9bd9; installed CLI 2.1.0; Codex + all 4 Claude sw registrations actual2.1.0 caches with SessionStart/Stop …

### T-23 Repair published documentation navigation
- AC: AC-05, AC-08 | Files: specweave/docs-site/, specweave/README.md, reports/docs-link-cleanup.md | Test: manual: docs production build and unchanged headless local HTTP link crawl; inspect entrypoint and inherited broken destinations
- [x] done by codex-dashboard 2026-09-14T07:10:23.457Z — specweave c502b35d6; final docs build passed; 7 headless entrypoints passed; unchanged full link crawl434->6, zero loca…

### T-25 Preserve contrast when live catalog data is populated
- AC: AC-05, AC-08 | Files: vskill-platform/src/app/product.css, reports/platform-verification.md, reports/artifacts/platform-redesign/ | Test: manual: data-rich headless preflight reproduces repository-link/momentum contrast failure then passes desktop/mobile light/dark with scoped overrides; final build and production checks
- [x] done by codex-product 2026-09-14T07:10:18.859Z — 495f0fa; root independent review approved; populated public-DOM synthetic axe preflight4 combinations passed after repr…

### T-26 Name the authenticated account menu control
- AC: AC-05, AC-08 | Files: vskill-platform/src/components/UserMenu.tsx, vskill-platform/src/components/__tests__/UserMenu.test.tsx, reports/platform-verification.md | Test: manual: accessible-name/state regression fails first then passes; final Worker build and exact-head CI verification
- [x] done by codex-product 2026-09-14T07:19:26.291Z — 1673da8; root independent approval;2 accessible-name/state/Escape regressions failed first;16 account tests passed; fin…

### T-27 Align current dashboard and model guides with 2.1 behavior
- AC: AC-03, AC-05, AC-07, AC-08 | Files: specweave/docs-site/docs/guides/model-selection.md, specweave/docs-site/docs/guides/analytics-dashboard.md, specweave/docs-site/docs/reference/cost-tracking.md, specweave/docs-site/docs/guides/dashboard/hooks.md, specweave/docs-site/docs/academy/specweave-essentials/08-ai-model-selection.md, specweave/docs-site/docs/glossary/terms/intelligent-model-selection.md, reports/docs-2.1-semantics.md | Test: manual: verify prose against shipped source, production docs build, headless HTTP200 and content checks for all six updated routes
- [x] done by codex-dashboard 2026-09-14T07:15:57.495Z — specweave 6a2750ac2; exactly6docs,4current guides and2historical notices; source-verified prose; final production docs …

### T-28 Align lifecycle E2E with portable handoff pointer contract
- AC: AC-08 | Files: specweave/tests/e2e/lifecycle/closure-2.0.e2e.ts, reports/lifecycle-pointer-contract.md | Test: cd /tmp/specweave-0877-root && npx vitest run --config vitest.e2e.config.ts tests/e2e/lifecycle/closure-2.0.e2e.ts
- [x] done by codex-root 2026-09-14T07:25:37.955Z — 59fd2c4d5; reproduced current CI ENOENT in lifecycle-pointer-red.log; required relative pointer and exact fixture-root …

### T-29 Preserve chapter selection during cold video loading
- AC: AC-05, AC-08 | Files: vskill-platform/src/app/components/shared/ProductDemoCard.tsx, vskill-platform/src/app/components/shared/__tests__/ProductDemoCard.test.tsx, vskill-platform/tests/e2e/product-evidence.spec.ts, reports/platform-verification.md, reports/platform-deployment.md | Test: manual: reproduce cold metadata chapter jump failure, failing-first regression then native headless cold-load E2E; independently reviewed hotfix build/deploy/live checks
- [ ] claimed by codex-product since 2026-09-14T07:26:55.682Z

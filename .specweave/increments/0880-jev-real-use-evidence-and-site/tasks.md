# Tasks

<!-- SW:BOARD -->
| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | easychamp | cd /Users/antonabyzov/Projects/sw-easychamp/repositories/an… |  |
| T-02 | done | site | cd /Users/antonabyzov/Projects/github/specweave-umb/reposit… |  |
| T-03 | done | graphics | node .specweave/increments/0880-jev-real-use-evidence-and-s… |  |
| T-04 | claimed | release |  |  |
| T-05 | done | graphics | cd /Users/antonabyzov/Projects/github/specweave-umb/reposit… |  |
| T-06 | done | site | export PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/… |  |
| T-07 | done | graphics | cd /Users/antonabyzov/Projects/github/specweave-umb/reposit… |  |
| T-08 | done | site | python3 .specweave/increments/0880-jev-real-use-evidence-an… |  |
| T-09 | done | graphics | cd /Users/antonabyzov/Projects/github/specweave-umb/reposit… |  |
| T-10 | done | site | cd /Users/antonabyzov/Projects/github/specweave-umb/reposit… |  |
| T-11 | done | release | gh run view 35683432093 --repo anton-abyzov/specweave --jso… |  |
| T-12 | done | graphics | cd /Users/antonabyzov/Projects/github/specweave-umb/reposit… |  |

11/12 done · 0 skipped · 1 claimed · 0 blocked · 0 stale · 0 open
<!-- /SW:BOARD -->

### T-01 EasyChamp Jev integration and reproducible evaluation
- AC: AC-01, AC-02, AC-06 | Files: EasyChamp ec-chat-api Jev integration/tests/scripts, reports/easychamp*, scripts/easychamp* | Test: manual: agent supplies real pytest and live evaluation commands
- [x] done by easychamp 2026-09-22T03:05:44.918Z — cd /Users/antonabyzov/Projects/sw-easychamp/repositories/anton-abyzov/0880-jev-easychamp && .venv/bin/python -m pytest …

### T-02 Evidence-led mobile-first SpecWeave website
- AC: AC-03, AC-05, AC-06 | Files: specweave/docs-site/src, specweave/docs-site/docs/guides/jev-system-one.md, specweave/docs-site/static/evidence, specweave/docs-site/tests, reports/site*, scripts/site* | Test: manual: site build and headless Playwright checks
- [x] done by site 2026-09-22T03:04:44.378Z — cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0880-site && export PATH=/Users/antonabyz…

### T-03 Premium graphics and Jev risk audit
- AC: AC-04, AC-06 | Files: specweave/docs-site/static/img/jev, reports/graphics*, reports/jev-audit*, scripts/graphics* | Test: manual: image inspection and documented code evidence
- [x] done by graphics 2026-09-22T02:56:58.732Z — node .specweave/increments/0880-jev-real-use-evidence-and-site/scripts/jev-audit-repro.cjs → exit 0 log: .specweave/inc…

### T-04 Integrated verification deploy release install
- AC: AC-05, AC-06 | Files: specweave/package.json, specweave/package-lock.json, specweave/CHANGELOG.md, specweave version metadata, reports/release*, reports/verification*, handoff.md | Test: manual: production HTTP/headless proof and installed package version
- [ ] claimed by release since 2026-09-22T02:52:07.892Z

### T-05 Fix verified Jev secret handling and guard validation
- AC: AC-02, AC-05, AC-06 | Files: specweave/src/core/jev/client.ts, specweave/src/core/jev/decide.ts, specweave/src/core/jev/browse.ts, specweave/src/core/session/handoff-secret-scrub.ts, specweave/src/**/handoff-secret-scrub.ts, specweave/tests/unit/jev, specweave/tests/unit/**/handoff-secret-scrub*, reports/jev-fixes* | Test: manual: regression tests and Jev focused coverage
- [x] done by graphics 2026-09-22T03:05:49.742Z — cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0880-graphics && PATH=/Users/antonabyzov/…

### T-06 Independent safety review and evidence endpoint checks
- AC: AC-03, AC-05, AC-06 | Files: specweave/docs-site/tests/jev-mobile.mjs, specweave/docs-site/src/pages/jev.tsx, reports/review*, reports/site-review* | Test: manual: headless evidence endpoints and independent safety review
- [x] done by site 2026-09-22T03:10:50.065Z — export PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH && cd /Users/antonabyzov/Projects/github/specweave…

### T-07 Close independently found shell quoting bypass
- AC: AC-05, AC-06 | Files: specweave/src/core/jev/decide.ts, specweave/tests/unit/jev/decide.test.ts, specweave/tests/unit/commands/jev-command.test.ts, reports/jev-prefilter-review* | Test: manual: quoted and escaped command regression tests
- [x] done by graphics 2026-09-22T03:10:11.850Z — cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0880-graphics && PATH=/Users/antonabyzov/…

### T-08 Publish exact EasyChamp evidence provenance
- AC: AC-01, AC-03, AC-05 | Files: specweave/docs-site/static/evidence/jev-easychamp-replay.json, specweave/docs-site/static/evidence/jev-easychamp-agent-comparison.json, reports/site-provenance* | Test: manual: public evidence matches refreshed reports with unchanged metrics
- [x] done by site 2026-09-22T03:13:12.630Z — python3 .specweave/increments/0880-jev-real-use-evidence-and-site/reports/site-provenance-check.py → exit 0 log: .specw…

### T-09 Verify and repair npm release installability
- AC: AC-05 | Files: specweave/.github/workflows/release.yml, specweave/scripts/release, specweave/tests/unit/release, reports/release-packaging* | Test: manual: published manifest, clean install and CLI execution
- [x] done by graphics 2026-09-22T03:28:19.284Z — cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0880-graphics && PATH=/Users/antonabyzov/…

### T-10 Check new canonical links against the candidate site
- AC: AC-03, AC-05 | Files: specweave/.github/workflows/docs-build.yml, specweave/docs-site/docusaurus.config.ts, specweave/docs-site/scripts, specweave/docs-site/tests, reports/site-ci* | Test: manual: link checker validates candidate routes and catches missing routes
- [x] done by site 2026-09-22T03:24:12.454Z — cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0880-site && PATH=/Users/antonabyzov/.nvm…

### T-11 Provision headless Chromium for required safety tests
- AC: AC-05, AC-06 | Files: specweave/.github/workflows/test.yml, reports/verification-ci* | Test: manual: headless network boundary tests and remote unit CI
- [x] done by release 2026-09-22T03:37:09.247Z — gh run view 35683432093 --repo anton-abyzov/specweave --json conclusion --jq .conclusion | python3 -c "import sys; asse…

### T-12 Retry interrupted registry response bodies
- AC: AC-05 | Files: specweave/scripts/release/verify-package-install.mjs, specweave/tests/unit/release/installability.test.ts, reports/release-packaging* | Test: node 22 release installability regression suite
- [x] done by graphics 2026-09-22T03:30:53.797Z — cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0880-graphics && PATH=/Users/antonabyzov/…

# Tasks

<!-- SW:BOARD -->
| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | codex-0881 | cd /tmp/specweave-0881-root && npx vitest run tests/unit/pr… |  |
| T-02 | done | codex-0881 | cd /tmp/specweave-0881-root && npx vitest run tests/unit/ad… |  |
| T-03 | done | codex-0881 | cd /tmp/specweave-0881-root && PATH=/Users/antonabyzov/.nvm… |  |
| T-04 | done | codex-0881 | cd /tmp/specweave-0881-root && PATH=/Users/antonabyzov/.nvm… |  |
| T-05 | done | codex-0881 | cd /tmp/specweave-0881-root && PATH=/Users/antonabyzov/.nvm… |  |
| T-06 | done | codex-0881 | cd /tmp/specweave-0881-root && export PATH=/Users/antonabyz… |  |
| T-07 | claimed | codex-0881 |  |  |

6/7 done · 0 skipped · 1 claimed · 0 blocked · 0 stale · 0 open
<!-- /SW:BOARD -->

### T-01 Project hub contract, store and portable briefs
- AC: AC-01, AC-02, AC-03, AC-04 | Files: src/core/project-hub/, tests/unit/project-hub/ | Test: cd /tmp/specweave-0881-root && npx vitest run tests/unit/project-hub
- [x] done by codex-0881 2026-09-22T03:13:53.511Z — cd /tmp/specweave-0881-root && npx vitest run tests/unit/project-hub → exit 0 log: .specweave/increments/0881-portable-…

### T-02 CLI, portable project skill and Codex installation
- AC: AC-01, AC-02, AC-06 | Files: bin/, src/cli/commands/project.ts, src/adapters/codex/, plugins/specweave/skills/project/, src/templates/AGENTS.md.template, src/dashboard/server/data/intent-store.ts, tests/unit/adapters/codex-adapter.test.ts, tests/unit/refresh-plugins-adapter.test.ts, tests/unit/cli/commands/project.test.ts, scripts/lint-skills.mjs | Test: cd /tmp/specweave-0881-root && npx vitest run tests/unit/adapters/codex-adapter.test.ts tests/unit/cli/commands/project.test.ts tests/unit/refresh-plugins-adapter.test.ts
- [x] done by codex-0881 2026-09-22T03:22:32.058Z — cd /tmp/specweave-0881-root && npx vitest run tests/unit/adapters/codex-adapter.test.ts tests/unit/cli/commands/project…
**Dependencies**: T-01

### T-03 Project hub dashboard and responsive verification
- AC: AC-05 | Files: src/dashboard/server/routes/project-hub-routes.ts, src/dashboard/server/dashboard-server.ts, src/dashboard/client/src/pages/ProjectHubPage.tsx, src/dashboard/client/src/pages/project-hub.css, src/dashboard/client/src/App.tsx, src/dashboard/client/src/components/layout/Sidebar.tsx, tests/unit/dashboard/project-hub-routes.test.ts, scripts/e2e/project-hub-e2e.mjs | Test: cd /tmp/specweave-0881-root && npx vitest run tests/unit/dashboard/project-hub-routes.test.ts && npm run build
- [x] done by codex-0881 2026-09-22T03:38:55.298Z — cd /tmp/specweave-0881-root && PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH npx vitest run tests/unit/…
**Dependencies**: T-01

### T-04 Documentation, package, install and release validation
- AC: AC-07 | Files: AGENTS.md, .agents/skills/sw-*/, .specweave/project/hub.json, .specweave/intents/board.jsonl, README.md, docs-site/docs/guides/portable-projects.md, docs-site/sidebars.ts, package.json, package-lock.json, CHANGELOG.md, plugins/specweave/.claude-plugin/plugin.json, .claude-plugin/marketplace.json, .specweave/increments/0881-portable-project-hub/ | Test: cd /tmp/specweave-0881-root && npm run lint:skills && npm run lint:docs-refs && node scripts/e2e/project-hub-e2e.mjs
- [x] done by codex-0881 2026-09-22T03:46:51.147Z — cd /tmp/specweave-0881-root && PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH npm run lint:skills && PAT…
**Dependencies**: T-02, T-03

### T-05 Independent review fixes and regression checks
- AC: AC-01, AC-04, AC-05, AC-06, AC-07 | Files: bin/, scripts/lint-docs-refs.mjs, src/cli/commands/project.ts, plugins/specweave/marketplace.json, src/core/project-hub/, src/dashboard/client/src/pages/ProjectHubPage.tsx, src/dashboard/server/routes/project-hub-routes.ts, src/templates/AGENTS.md.template, tests/unit/cli/commands/project.test.ts, tests/unit/project-hub/, tests/unit/dashboard/project-hub-routes.test.ts, tests/unit/cli/helpers/init/instruction-templates.test.ts, tests/unit/build/version-alignment.test.ts, src/utils/native-skill-installer.ts, src/utils/plugin-copier.ts, src/adapters/codex/, src/adapters/registry.yaml, tests/unit/native-skill-installer.test.ts | Test: cd /tmp/specweave-0881-root && npx vitest run tests/unit/project-hub tests/unit/cli/commands/project.test.ts tests/unit/dashboard/project-hub-routes.test.ts tests/unit/cli/helpers/init/instruction-templates.test.ts tests/unit/build/version-alignment.test.ts
- [x] done by codex-0881 2026-09-22T03:39:48.547Z — cd /tmp/specweave-0881-root && PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH npx vitest run tests/unit/…

### T-06 Consolidate dashboard with the current website design system
- AC: AC-05, AC-08 | Files: src/styles/, src/dashboard/client/, docs-site/src/pages/continuity.module.css, scripts/e2e/project-hub-e2e.mjs, scripts/e2e/brand-parity.mjs, tests/unit/dashboard/ | Test: cd /tmp/specweave-0881-root && npm run build && node scripts/e2e/project-hub-e2e.mjs --browser && node scripts/e2e/brand-parity.mjs
- [x] done by codex-0881 2026-09-22T05:07:58.338Z — cd /tmp/specweave-0881-root && export PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH PWDEBUG=0 PLAYWRIGH…

### T-07 Publish stable release, push repositories and verify installation
- AC: AC-07, AC-09 | Files: README.md, CHANGELOG.md, package.json, package-lock.json, .claude-plugin/marketplace.json, plugins/specweave/.claude-plugin/plugin.json, plugins/specweave/skills/project/, .specweave/increments/0881-portable-project-hub/, scripts/release/, .github/workflows/, docs-site/docusaurus.config.ts, bin/, src/cli/, src/core/doctor/, src/core/living-docs/, src/core/lsp/, src/utils/, tests/unit/, scripts/e2e/bounded-scans.mjs | Test: cd /tmp/specweave-0881-root && npm run validate:versions && npm run release:preflight
- [ ] claimed by codex-0881 since 2026-09-22T04:46:48.981Z

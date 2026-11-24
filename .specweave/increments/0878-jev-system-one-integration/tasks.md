# Tasks — 0878 Jev integration

<!-- SW:BOARD -->
| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | claude | cd repositories/anton-abyzov/specweave && npx vitest run te… |  |
| T-02 | done | claude | cd repositories/anton-abyzov/specweave && npx vitest run te… |  |
| T-03 | done | claude | cd repositories/anton-abyzov/specweave && npx vitest run te… |  |
| T-04 | done | claude | cd repositories/anton-abyzov/specweave && node scripts/lint… |  |
| T-05 | done | claude | cd repositories/anton-abyzov/specweave && npx vitest run te… |  |
| T-06 | done | claude | cd repositories/anton-abyzov/specweave && npx vitest run te… |  |
| T-07 | done | claude | node .specweave/increments/0878-jev-system-one-integration/… |  |
| T-08 | done | claude | specweave jev doctor → exit 0 log: .specweave/increments/08… |  |
| T-09 | done | claude | test -s .specweave/increments/0878-jev-system-one-integrati… |  |

9/9 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
<!-- /SW:BOARD -->

### T-01 Core client, config, question catalog, decisions, usage ledger
- AC: AC-01, AC-02, AC-03, AC-04, AC-09 | Files: repositories/anton-abyzov/specweave/src/core/jev/index.ts, repositories/anton-abyzov/specweave/src/core/jev/client.ts, repositories/anton-abyzov/specweave/src/core/jev/config.ts, repositories/anton-abyzov/specweave/src/core/jev/questions.ts, repositories/anton-abyzov/specweave/src/core/jev/decide.ts, repositories/anton-abyzov/specweave/src/core/jev/usage.ts, repositories/anton-abyzov/specweave/src/core/jev/browse.ts, repositories/anton-abyzov/specweave/tests/unit/jev/client.test.ts, repositories/anton-abyzov/specweave/tests/unit/jev/decide.test.ts, repositories/anton-abyzov/specweave/tests/unit/jev/config.test.ts | Test: cd repositories/anton-abyzov/specweave && npx vitest run tests/unit/jev --config vitest.unit.config.ts
- [x] done by claude 2026-09-21T18:57:27.198Z — cd repositories/anton-abyzov/specweave && npx vitest run tests/unit/jev --config vitest.unit.config.ts → exit 0 log: .s…

### T-02 `specweave jev` CLI command
- AC: AC-01, AC-02, AC-03, AC-04, AC-09 | Files: repositories/anton-abyzov/specweave/src/cli/commands/jev.ts, repositories/anton-abyzov/specweave/src/cli/commands/jev-helpers.ts, repositories/anton-abyzov/specweave/bin/specweave.js, repositories/anton-abyzov/specweave/tests/unit/commands/jev-command.test.ts | Test: cd repositories/anton-abyzov/specweave && npx vitest run tests/unit/commands/jev-command.test.ts --config vitest.unit.config.ts
- [x] done by claude 2026-09-21T18:57:28.028Z — cd repositories/anton-abyzov/specweave && npx vitest run tests/unit/commands/jev-command.test.ts --config vitest.unit.c…

### T-03 Opt-in Bash guard hook
- AC: AC-05 | Files: repositories/anton-abyzov/specweave/plugins/specweave/hooks/hooks.json, repositories/anton-abyzov/specweave/plugins/specweave/hooks/run.mjs, repositories/anton-abyzov/specweave/src/core/hooks/handlers/pre-tool-use.ts, repositories/anton-abyzov/specweave/tests/unit/hooks/jev-bash-guard.test.ts, repositories/anton-abyzov/specweave/tests/unit/hooks/hook-wiring-parity.test.ts, repositories/anton-abyzov/specweave/tests/unit/hooks/run-mjs.test.ts | Test: cd repositories/anton-abyzov/specweave && npx vitest run tests/unit/hooks --config vitest.unit.config.ts
- [x] done by claude 2026-09-21T18:57:36.442Z — cd repositories/anton-abyzov/specweave && npx vitest run tests/unit/hooks --config vitest.unit.config.ts → exit 0 log: …

### T-04 Skills, templates, docs
- AC: AC-08 | Files: repositories/anton-abyzov/specweave/plugins/specweave/skills/jev/SKILL.md, repositories/anton-abyzov/specweave/skills/sw-jev/SKILL.md, repositories/anton-abyzov/specweave/skills/README.md, repositories/anton-abyzov/specweave/src/templates/CLAUDE.md.template, repositories/anton-abyzov/specweave/src/templates/AGENTS.md.template, repositories/anton-abyzov/specweave/src/cli/helpers/init/instruction-file-writer.ts, repositories/anton-abyzov/specweave/plugins/specweave/PLUGIN.md, repositories/anton-abyzov/specweave/plugins/specweave/.claude-plugin/plugin.json, repositories/anton-abyzov/specweave/README.md, repositories/anton-abyzov/specweave/tests/unit/skills/standalone-skills.test.ts, repositories/anton-abyzov/specweave/docs-site/docs/guides/jev-system-one.md, repositories/anton-abyzov/specweave/docs-site/sidebars.ts, repositories/anton-abyzov/specweave/scripts/lint-skills.mjs | Test: cd repositories/anton-abyzov/specweave && node scripts/lint-skills.mjs && node scripts/lint-standalone-skills.mjs && npx vitest run tests/unit/skills tests/unit/cli/helpers/init --config vitest.unit.config.ts
- [x] done by claude 2026-09-21T18:57:42.794Z — cd repositories/anton-abyzov/specweave && node scripts/lint-skills.mjs && node scripts/lint-standalone-skills.mjs && np…

### T-05 Headless browser delegation loop
- AC: AC-06 | Files: repositories/anton-abyzov/specweave/src/core/jev/browse.ts, repositories/anton-abyzov/specweave/tests/unit/jev/browse.test.ts | Test: cd repositories/anton-abyzov/specweave && npx vitest run tests/unit/jev/browse.test.ts --config vitest.unit.config.ts
- [x] done by claude 2026-09-21T18:57:45.772Z — cd repositories/anton-abyzov/specweave && npx vitest run tests/unit/jev/browse.test.ts --config vitest.unit.config.ts →…

### T-06 Integrations: config schema, model tier routing, completion evaluator
- AC: AC-07 | Files: repositories/anton-abyzov/specweave/src/core/config/types.ts, repositories/anton-abyzov/specweave/src/utils/model-selection.ts, repositories/anton-abyzov/specweave/src/core/auto/completion-evaluator.ts, repositories/anton-abyzov/specweave/tests/unit/jev/integrations.test.ts | Test: cd repositories/anton-abyzov/specweave && npx vitest run tests/unit/jev/integrations.test.ts tests/unit/auto --config vitest.unit.config.ts
- [x] done by claude 2026-09-21T18:57:46.780Z — cd repositories/anton-abyzov/specweave && npx vitest run tests/unit/jev/integrations.test.ts tests/unit/auto --config v…

### T-07 Bench: EasyChamp, vskill crawl, inbox triage
- AC: AC-10 | Files: .specweave/increments/0878-jev-system-one-integration/scripts/jev-bench.mjs, .specweave/increments/0878-jev-system-one-integration/reports/jev-bench.json, .specweave/increments/0878-jev-system-one-integration/reports/jev-bench.md | Test: node .specweave/increments/0878-jev-system-one-integration/scripts/jev-bench.mjs --dry-run
- [x] done by claude 2026-09-21T18:57:47.174Z — node .specweave/increments/0878-jev-system-one-integration/scripts/jev-bench.mjs --dry-run → exit 0 log: .specweave/inc…

### T-08 Release 2.2.0, global install, live verification
- AC: AC-11 | Files: repositories/anton-abyzov/specweave/CHANGELOG.md, repositories/anton-abyzov/specweave/package.json, repositories/anton-abyzov/specweave/.claude-plugin/marketplace.json, .specweave/config.json | Test: specweave jev doctor
- [x] done by claude 2026-09-21T19:15:23.266Z — specweave jev doctor → exit 0 log: .specweave/increments/0878-jev-system-one-integration/reports/task-T-08.log Jev (Typ…

### T-09 HTML report
- AC: AC-12 | Files: .specweave/increments/0878-jev-system-one-integration/reports/jev-report.html | Test: test -s .specweave/increments/0878-jev-system-one-integration/reports/jev-report.html
- [x] done by claude 2026-09-21T19:07:46.769Z — test -s .specweave/increments/0878-jev-system-one-integration/reports/jev-report.html → exit 0 log: .specweave/incremen…

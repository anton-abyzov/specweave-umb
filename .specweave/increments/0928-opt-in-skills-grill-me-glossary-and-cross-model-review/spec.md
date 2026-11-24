# 0928 Opt-in skills, grill-me, glossary and cross-model review

## Problem

SpecWeave installs 11 skills into every project, several restating each other (auto, done and team repeat sw-do; brainstorm holds the interview), plus 5 generic `skills-optional/` skills nobody installs. There is no way to turn a skill on or off. The two practices that work best with agents, per Matt Pocock's October 16, 2026 interview and the `mattpocock/skills` repo, are missing: a relentless "grill me" interview and a ubiquitous-language glossary (what "Order" means in the business, the database and the code). Reviews run in the same model family that wrote the code. Research: `~/Projects/github/studio-research-notes/specweave-rethink-2026-10-17.md`.

## Scope

In: a skill catalog with core and opt-in skills, `specweave skills`, `sw-grill-me`, `sw-glossary`, `specweave glossary check`, `specweave review` (cross-model), folding auto and team into sw-do, deleting sw-brainstorm, sw-team and `skills-optional/`, docs naming the method "intent-first development". Out: renaming the product, npm package or repo; the honest close gate and spec-model changes from the October 16 grill.

## Acceptance Criteria

- [ ] AC-01: A fresh `specweave init` installs exactly the core skills (increment, do, auto, done, review, handoff) into `.claude/skills/` and `.agents/skills/`, and the Claude Code plugin ships only those.
- [ ] AC-02: `specweave skills enable grill-me glossary` records them under `skills.enabled` in `.specweave/config.json` and installs `sw-grill-me` and `sw-glossary`; `disable` removes SpecWeave's copies; `skills list` shows each skill's state and the reason; a core skill cannot be disabled.
- [ ] AC-03: Detected skills install with no config: sync (a tracker configured), project (`hub.json`), jev (`jev.enabled`), glossary (`GLOSSARY.md`), grill-me (`planning.deepInterview: deep`), unless listed under `skills.disabled`.
- [ ] AC-04: `specweave update` removes SpecWeave-owned copies of retired skills (sw-brainstorm, sw-team) and of optional skills no longer enabled, and never removes a user's own `sw-*` folder.
- [ ] AC-05: sw-do covers unattended runs and parallel lanes; sw-auto is a short user-invoked entry to it; sw-brainstorm, sw-team and `skills-optional/` are gone; no runtime message names a removed skill.
- [ ] AC-06: sw-grill-me asks in rounds, each question with a recommended answer, and records Decisions; sw-glossary interviews the user and writes GLOSSARY.md entries with Business, Data, Code and UI levels; both pass `lint:standalone-skills`.
- [ ] AC-07: `specweave glossary check` lists _Avoid_ words used as identifiers and Data/Code pointers that no longer resolve, with file:line; exit 0, or 1 with `--strict` when anything is found.
- [ ] AC-08: `specweave review` builds a brief from the increment (ACs, task Files, diff range, author family from the ledger), runs a reviewer from another model family (default Codex `gpt-6.1-sol` when Claude wrote the code), writes `reports/review-<reviewer>.md`, appends a ledger note, and exits 0 for ship, 3 for fix first, 1 on error; `--brief` only prints the brief.
- [ ] AC-09: The docs call the method "intent-first development", list the new skill set and the opt-in commands, and rename nothing else.

## Approach

`skills/catalog.json` becomes the one list of skills (core and optional, with detect rules). `generate-skills.mjs` writes core skills to `plugins/specweave/skills/`, optional ones to `plugins/specweave/skills-optional/` (shipped, not loaded by the plugin), and the catalog to `plugins/specweave/skills-catalog.json`. `installProjectSkills` resolves the enabled set from the catalog and config and prunes SpecWeave-owned copies of everything else. The reviewer runs a configured CLI command with the brief on stdin; SpecWeave holds no model keys and hooks stay offline.

## Decisions

### Asked
- D-01 Product, package and repo name → keep SpecWeave (user, October 17, 2026); nothing is renamed.
- D-02 Method name for the docs → "intent-first development" (user, October 17, 2026), replacing "spec-driven development".
### Defaulted (change any before sw-do)
- D-03 Grill skill name → `sw-grill-me`, because 2.x `sw:grill` meant code review and the doctor still maps it to sw:review.
- D-04 Opt-in store → `skills.enabled` and `skills.disabled` in `.specweave/config.json`; the plugin ships core skills only.
- D-05 sw-done stays a skill: the sw-closer agent and about 15 runtime messages invoke it, and closing in a fresh context is its own step.
- D-06 Reviewer → an external CLI command per reviewer (`codex exec`, `claude -p`), overridable in `review.reviewers`; `review.crossModel` only tells sw-review and sw-done to call it unprompted.
- D-07 Glossary entry → `### Term`, a definition, then `- Avoid:`, `- Data:`, `- Code:`, `- UI:` lines; Pocock's `**Term**:` and `_Avoid_:` format is parsed too.
### Open
- none

## Tasks

### T-01 Skill catalog and opt-in install
- AC: AC-01, AC-02, AC-03, AC-04 | Files: repositories/anton-abyzov/specweave/skills/catalog.json, repositories/anton-abyzov/specweave/scripts/build/generate-skills.mjs, repositories/anton-abyzov/specweave/src/core/skills/, repositories/anton-abyzov/specweave/src/cli/commands/skills.ts, repositories/anton-abyzov/specweave/src/cli/commands/init.ts, repositories/anton-abyzov/specweave/src/cli/commands/update.ts, repositories/anton-abyzov/specweave/src/cli/commands/refresh-plugins.ts, repositories/anton-abyzov/specweave/src/core/config/types.ts, repositories/anton-abyzov/specweave/bin/specweave.js, repositories/anton-abyzov/specweave/scripts/completions/, repositories/anton-abyzov/specweave/tests/unit/skills/, repositories/anton-abyzov/specweave/tests/unit/core/skills/, repositories/anton-abyzov/specweave/tests/unit/cli/commands/ | Test: cd repositories/anton-abyzov/specweave && npx vitest run tests/unit/skills tests/unit/cli/commands/skills.test.ts

### T-02 Skill content and runtime messages
- AC: AC-05, AC-06 | Files: repositories/anton-abyzov/specweave/skills/, repositories/anton-abyzov/specweave/skills-optional/, repositories/anton-abyzov/specweave/plugins/specweave/, repositories/anton-abyzov/specweave/src/core/hooks/handlers/stop.ts, repositories/anton-abyzov/specweave/src/core/increment/template-creator.ts, repositories/anton-abyzov/specweave/src/cli/commands/create-increment.ts, repositories/anton-abyzov/specweave/src/templates/, repositories/anton-abyzov/specweave/src/cli/helpers/init/instruction-file-writer.ts, repositories/anton-abyzov/specweave/src/cli/commands/jev-helpers.ts, repositories/anton-abyzov/specweave/CHANGELOG.md, repositories/anton-abyzov/specweave/tests/unit/cli/helpers/init/, repositories/anton-abyzov/specweave/tests/unit/core/hooks/handlers/stop.test.ts, repositories/anton-abyzov/specweave/scripts/lint-skills.mjs, repositories/anton-abyzov/specweave/scripts/lint-standalone-skills.mjs | Test: cd repositories/anton-abyzov/specweave && npm run lint:standalone-skills && npm run lint:skills && node scripts/build/generate-skills.mjs --check

### T-03 Glossary check
- AC: AC-07 | Files: repositories/anton-abyzov/specweave/src/core/glossary/, repositories/anton-abyzov/specweave/src/cli/commands/glossary.ts, repositories/anton-abyzov/specweave/tests/unit/glossary/ | Test: cd repositories/anton-abyzov/specweave && npx vitest run tests/unit/glossary

### T-04 Cross-model review command
- AC: AC-08 | Files: repositories/anton-abyzov/specweave/src/core/review/, repositories/anton-abyzov/specweave/src/cli/commands/review.ts, repositories/anton-abyzov/specweave/skills/sw-review/SKILL.md, repositories/anton-abyzov/specweave/skills/sw-done/SKILL.md, repositories/anton-abyzov/specweave/src/core/tasks/closure-gate.ts, repositories/anton-abyzov/specweave/tests/unit/review/ | Test: cd repositories/anton-abyzov/specweave && npx vitest run tests/unit/review

### T-05 Docs: intent-first development and the new skills
- AC: AC-09 | Files: repositories/anton-abyzov/specweave/docs-site/docs/, repositories/anton-abyzov/specweave/README.md | Test: cd repositories/anton-abyzov/specweave/docs-site && npm run build

### T-06 Cross-model review of this increment and PRs
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09 | Files: .specweave/increments/0928-opt-in-skills-grill-me-glossary-and-cross-model-review/reports/ | Test: a GPT-6.1-Sol review with every critical and high finding fixed, then the skills/CLI PR and the docs PR open against develop

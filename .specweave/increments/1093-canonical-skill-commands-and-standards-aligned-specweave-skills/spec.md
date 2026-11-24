# Canonical skill commands and standards-aligned SpecWeave skills

## Problem

The SpecWithCode composer lists a skill as `/skill:Sw Do`: a `/skill:` prefix (Pi's syntax, which no other provider accepts) followed by a title-cased name with a space. Picking it inserts `$sw:do`, so the label is neither the text that runs nor something a person can type. Typed by hand, `/sw:do 0042` reaches a Codex thread as plain text: on October 27, 2026, codex-cli 0.162.1 answered `NONE` to a typed `/sw:review` and loaded the skill for `$sw:review`. Plugin skills carry an "App" badge that hides that they come from a plugin. Typing `/continue` also lists sw-do and sw-handoff, because both name "continue" as a trigger.

On the SpecWeave side, `sw-grill-me` (the pre-implementation interview the user looks for) is opt-in and installs only as a project copy at the SpecWeave root. Threads start inside child repositories, where Claude Code and Codex stop looking for project skills at that repository's root, and the plugin they do load carries only core skills, so grill-me is unreachable there. Every skill also puts `version:` at the top level of its frontmatter, which the Agent Skills spec does not define and strict validators reject, and only sw-auto has Codex display metadata ("SpecWeave auto"), so Codex shows "Sw Do" beside it.

## Scope

In: composer and coordinator skill rows, insertion and send in specwithcode-dev; grill-me promoted to core, frontmatter and `agents/openai.yaml` changes, trigger wording, validators, docs and changelog in specweave.

In (added October 27): per-harness coordinator menus and Copilot ACP skill dispatch; the verified-skill.com version reader (vskill-platform).

In (added October 27, from 1091's installed check): vskill plugin installs keep `name:` equal to the folder; composer skill lists rescan after outside installs.

Out: project-wake (1091, its own owner), `/continue` and other continuation code, any release, restart or global reinstall, the iOS composer, Claude.ai uploads.

## Acceptance Criteria

- [ ] AC-01: A skill row in the `/` and `$` menus of the chat and coordinator composers leads with the exact invocation (`$sw:do`); a provider display name that differs from the title-cased id follows it, muted; plugin skills carry a "Plugin" badge.
- [ ] AC-02: A message that opens with `/<id>`, where id is exactly one of the selected provider's runnable skills and no composer, app or provider command has that name, is sent as `$<id>` with its arguments; anything else is sent as typed.
- [ ] AC-03: `sw-grill-me` ships in the plugin and in every project as a core skill; `specweave skills enable grill-me` exits 0 and says it is core; `disable grill-me` is refused; projects that listed it under `skills.enabled` keep working.
- [ ] AC-04: Every source skill keeps its version under `metadata.version`, has `agents/openai.yaml` with a "SpecWeave <Name>" display name (sw-auto keeps `allow_implicit_invocation: false`), and sw-do and sw-handoff no longer list "continue"; the generated plugin and project copies match the sources (`generate-skills --check`).
- [ ] AC-05: Docs and the skills README state the run syntax per tool, the core and optional lists, and which frontmatter keys are spec fields and which are extensions.
- [ ] AC-06: Focused tests, typecheck and a headless screenshot of the composer menu pass; a fresh-context review finds no unresolved critical or high issue.
- [ ] AC-08: verified-skill.com reads a skill's version from `metadata.version` as well as a root `version:` (publish, upsert, rescan, update scanner) and stamps a missing version as `metadata.version`, so registry copies of spec-form skills never regain a root `version:`.
- [ ] AC-07: The coordinator and chat `/` menus list only the selected harness's skills (Claude Code, Codex, Copilot, Antigravity), and a typed `/<id>` becomes a skill mention only for that harness; Copilot's ACP skill commands (input hint "instructions for the skill") list as skills and reach Copilot as `/<id>`.
- [ ] AC-09: Installing a plugin skill with vskill keeps its frontmatter `name:` equal to its folder (never `plugin/skill`), plugin lock entries record their skill folders, and `vskill doctor` warns that Codex ignores an existing namespaced name.
- [ ] AC-10: A skill installed outside the app appears in a new thread's composer `$` and `/skill:` lists without Settings › Skills › Rescan: a plain refresh rescans a cwd's skill snapshot once it is a minute old or came from the boot cache, and opening a thread asks for that refresh.

## Approach

App: `providerSkillInvocation` and `providerSkillDistinctDisplayName` in client-runtime `providerSkills.ts` feed the menu; `leadingSlashAsSkillMention` plus web `resolveLeadingSkillCommand` run once at send in ChatView (through the composer handle) and in the coordinator draft submit. The server path is unchanged: every adapter already dispatches `$id`.

SpecWeave: catalog moves grill-me to core and drops the `deep-interview` detect rule; the generator moves the plugin copy; the version validator reads `metadata.version`; the obsolete stamp script that wrote generated copies is deleted; the portability lint counts lines after the frontmatter.

Rejected: aliasing `/sw-do` to `sw:do` (a guessed alias, not a provider contract); server-side slash rewriting (adapters do not know which `/name` the provider expands); adding `name:` to plugin copies (plugin hosts derive the id from the folder, and Codex behavior with a frontmatter name is undocumented); dropping `argument-hint` and `disable-model-invocation` (they drive Claude Code autocomplete and keep sw-auto from starting on its own).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Menu label → the `$id` the pick inserts, because it is the one form every provider dispatches and the one the composer chip shows.
- D-02 grill-me → core, reversing 0928's opt-in, because opt-in copies never reach child-repository threads and the user asked where the interview skill went.
- D-03 Plugin badge → "Plugin" instead of "App" (same source kind, clearer word).
### Open
- none

## Tasks

### T-01 Composer shows and sends canonical skill invocations
- AC: AC-01, AC-02 | Files: specwithcode-dev `packages/client-runtime/src/providerSkills.ts`, `apps/web/src/providerSkillSearch.ts`, `apps/web/src/components/chat/ComposerCommandMenu.tsx`, `apps/web/src/components/chat/ChatComposer.tsx`, `apps/web/src/components/ChatView.tsx`, `apps/web/src/components/studio/CoordinatorSlashMenu.tsx`, `apps/web/src/components/studio/CoordinatorComposer.tsx` and their tests | Test: `node node_modules/vite-plus/bin/vp test run packages/client-runtime/src/providerSkills.test.ts apps/web/src/providerSkillSearch.test.ts apps/web/src/components/chat/ComposerCommandMenu.test.tsx apps/web/src/components/chat/composerSlashCommandSearch.test.ts apps/web/src/components/studio/CoordinatorSlashMenu.test.ts`

### T-02 SpecWeave skills: grill-me core, spec-aligned frontmatter, Codex metadata
- AC: AC-03, AC-04 | Files: specweave `skills/`, `plugins/specweave/`, `src/core/skills/catalog.ts`, `src/cli/commands/skills.ts`, `scripts/validation/validate-skill-versions.cjs`, `scripts/lint-standalone-skills.mjs`, tests | Test: `npx vitest run tests/unit/core/skills tests/unit/cli/commands/skills.test.ts tests/unit/skills`

### T-03 Docs, changelog and run syntax
- AC: AC-05 | Files: specweave `README.md`, `skills/README.md`, `docs-site/docs/`, `CHANGELOG.md` | Test: `npm run lint:skills && npm run lint:standalone-skills`

### T-04 Headless menu proof, PRs and exact-head CI
- AC: AC-01, AC-06 | Files: none | Test: headless screenshot under `/Users/antonabyzov/.specwithcode/m4/evidence/skill-consolidation/`

### T-06 Per-harness skill menus and Copilot skill dispatch
- AC: AC-07 | Files: specwithcode-dev `apps/server/src/provider/acp/AcpRegistryProbe.ts`, `apps/server/src/orchestration-v2/Adapters/AcpAdapterV2.ts`, `apps/server/src/orchestration-v2/Adapters/AcpRegistryAdapterV2.ts`, `apps/web/src/components/studio/CoordinatorHarnesses.testkit.ts`, `apps/web/tests/skill-commands/` and their tests | Test: `node node_modules/vite-plus/bin/vp test run apps/server/src/provider/acp/AcpRegistryProbe.test.ts apps/server/src/orchestration-v2/Adapters/AcpRegistryAdapterV2.test.ts apps/web/src/components/studio/CoordinatorSlashMenu.test.ts`

### T-07 Registry reads metadata.version
- AC: AC-08 | Files: vskill-platform `src/lib/skill-md/inject-version-if-missing.ts`, `src/lib/frontmatter-parser.ts` and their tests | Test: `npx vitest run src/lib/skill-md/__tests__/inject-version-if-missing.test.ts src/lib/__tests__/frontmatter-parser.test.ts src/lib/skill-update`

### T-08 Installed skill name equals its folder (vskill)
- AC: AC-09 | Files: vskill `src/commands/add.ts`, `src/commands/doctor.ts`, `src/lockfile/types.ts` and their tests | Test: `npx vitest run src/commands/add.test.ts src/commands/doctor.test.ts src/commands/__tests__/doctor-namespace.test.ts`

### T-09 Composer skill lists pick up outside installs
- AC: AC-10 | Files: specwithcode-dev `apps/server/src/provider/ProviderRegistry.ts`, `apps/web/src/components/chat/ChatComposer.tsx` and the registry test | Test: `node node_modules/vite-plus/bin/vp test run apps/server/src/provider/ProviderRegistry.test.ts`

### T-05 Verify and close 1093
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10 | Files: none | Test: `specweave verify 1093-canonical-skill-commands-and-standards-aligned-specweave-skills`

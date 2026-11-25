# 1486 Skill deprecation that names the replacement

## Problem

MCP servers can now ship skills, run Tasks and ask the user (November 2026 MCP upgrades). An audit of all 122 skills in vskill and SpecWeave found that no CLI-wrapper skill can be deprecated yet: no MCP replacement works on Claude, Codex, Copilot and Antigravity without per-host setup. When one can, there is no way to deprecate a skill with a pointer:

- SKILL.md has no deprecation field.
- vskill-platform's `Skill.isDeprecated` delists the skill and shows no message.
- `SkillVersion.deprecated` and `SkillVersion.deprecationMsg` exist in the schema (migration `20260423132315_versioning_v2_phase1`), but nothing reads or writes them.
- SpecWeave's `skills/catalog.json` has only a `retired` list, and `update` deletes those skills.

Old installs never hear about a deprecation, because nothing reads the source's current metadata.

## Scope

In: the SKILL.md metadata contract; vskill CLI notices (`install`, `update`, `outdated`, `info`, `list`, `doctor`); platform publish writing the existing `SkillVersion` columns, plus a Deprecated badge on the skill page; SpecWeave catalog `deprecated` overlay and validator; deprecating vskill `task-skill-announcer`; pointer edits in `gws` and `blotato`; releases of all three.

Out: removing any skill (owner's call). Removal candidates are listed in the report only: hi-atlantis, tiktokpost, stub-skill-76f6713e, and whether stripe-refund-auditor moves to fixtures. Also out: new DB columns, data migrations, and setting `Skill.isDeprecated`.

## Acceptance Criteria

- [ ] AC-01: A skill marks itself deprecated with flat string keys under `metadata` only. No new top-level keys and no nesting: the Agent Skills spec treats metadata as string-to-string, and the version already lives in `metadata.version` per increment 1093. The keys are `metadata: { version: "1.0.4", deprecated: "true", deprecated-message: "...", replaced-by: "none | mcp:<server>[:tool] | <owner>/<repo>/<skill>", deprecated-since: "1.0.4" }`. Its description starts with "DEPRECATED: <one line>." and the body keeps a short redirect.
- [ ] AC-02: `vskill install`, `update`, `outdated`, `info` and `list` print the message and the replacement. `vskill doctor` reports deprecated as a warning, not an error.
- [ ] AC-03: Old installs learn about it. Installs read GitHub main, so `vskill outdated` and `vskill doctor` read the source's current metadata and flag an installed copy even when that copy predates the field. Nothing is removed or overwritten automatically.
- [ ] AC-04: On publish, vskill-platform copies `metadata.deprecated` into the existing `SkillVersion.deprecated`. It writes the message plus replacedBy into the existing `deprecationMsg` as "<message> Replaced by: <replacedBy>.". No new column, no data migration, and `Skill.isDeprecated` is not set. The skill page shows a "Deprecated" badge with the message. If any of this needs a migration, stop and ask the owner.
- [ ] AC-05: A deprecated skill still loads and is listed on Claude, Codex, Copilot and Antigravity, checked in each host's skill list on this machine. Its name stays equal to its folder, because Codex silently drops a skill whose name differs.
- [ ] AC-06: SpecWeave `skills/catalog.json` gains `deprecated: [{name, replacedBy, message}]` next to `retired`. `specweave update` prints the notice and keeps the file. `scripts/validation/validate-skill-versions.cjs` accepts the four flat metadata keys.
- [ ] AC-07: vskill `plugins/frontend/skills/task-skill-announcer` is deprecated with this mechanism: replaced-by `none`, message "A smoke-test fixture, not a user skill; moved to e2e fixtures.". The version goes to 1.0.5, not 1.0.4 (see D-02). A copy goes to vskill `e2e/fixtures/skills/task-skill-announcer`, and the standalone create-skill test (`useCreateSkill.standalone.test.ts`) points at the fixture.
- [ ] AC-08: `gws` and `blotato` get pointer edits, not deprecation, with a version bump only. Each says an MCP route exists where the host has it configured (`gws mcp -s <services>`; Blotato's MCP mode), and the skill stays the fallback.

## Approach

**Contract (AC-01).** One block-style `metadata` mapping holds five flat string keys: `version`, `deprecated` (the string `"true"`), `deprecated-message`, `replaced-by` and `deprecated-since`. Three parsers read these keys and must agree:

- vskill: a line regex over direct children of `metadata`, the same approach as `versionFields`.
- Platform: an allowlist regex like `frontmatter-parser.ts`.
- SpecWeave validator: YAML.

All three use the same fixture cases: valid, a YAML boolean `true` (refused by the validator with "quote it", read as deprecated by the CLI), nested (refused), missing message, and a bad `replaced-by` shape.

**vskill.**

1. Add `src/lib/deprecation.ts` with three functions:
   - `readDeprecation(content)` returns `{message, replacedBy, since}` or null. For combined plugin content it reads every frontmatter block.
   - `formatDeprecation(name, d)` gives one line: "<name> is deprecated since X: <message> Replaced by: <r>."
   - `fetchUpstreamSkillMds(entry, name)`:
     - Single GitHub entries read `sourceSkillPath`, or the conventional paths, through `fetchGitHubFlat` with `resolveCommit: false`.
     - `github-plugin` and `marketplace` entries resolve the plugin path from `.claude-plugin/marketplace.json`, then fetch raw `<path>/skills/<dir>/SKILL.md` for each `<dir>/SKILL.md` in `entry.files`. This uses raw files only, with no Trees API call.
     - Pinned entries and entries without a sha are included, unlike `githubSourceChanges`.
2. `outdated`: read upstream deprecations for all public GitHub and plugin entries in parallel, plus local SKILL.md. Print notices before the "All skills are up to date" return, with no change to the exit code. `--json` gains `deprecated: {message, replacedBy, since}` per result and also lists deprecated skills that have no update.
3. `update`: print the notice from fetched content and from the local copy, before the plugin skip at `update.ts:411` and before "already up to date". Never write anything because of it.
4. `install` (`add.ts`): add a one-line notice after each `runTier1Scan` on single-skill, registry, plugin-dir and repo-plugin paths. `add.ts` is already 3,449 lines, so the logic lives in the new module.
5. `info`: parse `detail.content` when the registry returns it. Otherwise fetch the source SKILL.md from `repoUrl` plus `skillPath`. Fall back to the platform's new `deprecated` and `deprecationMsg` fields when they are present.
6. `list`: read each installed SKILL.md (`resolveInstallPath`), mark deprecated rows, and print notices below the table. `--json` gains `deprecated`.
7. `doctor`:
   - New kind `deprecated` with warning severity, never fixable, ignored by `--fix`.
   - The local check runs in `scanScope`. The upstream check runs only in `doctorCommand`, outside the pure `runDoctor`, with a 5 s timeout and a silent skip when offline.
   - The exit code ignores deprecated-only reports (D-03).
8. Skill edits:
   - task-skill-announcer goes to 1.0.5 with a DEPRECATED description and a body redirect.
   - Copy it as a fixture (name stays equal to folder) and point the standalone test at the fixture path.
   - gws goes to 1.0.5 and blotato to 1.0.2, each with an MCP pointer paragraph.
   - Bump the frontend, google-workspace and marketing plugin versions in `.claude-plugin/marketplace.json` and each `plugin.json`, because plugin installs version off the manifest.
   - Fix the README line 133 table.

**vskill-platform.**

1. Add `src/lib/skill-md/deprecation.ts` with `deprecationColumns(content)`, which returns `{deprecated: true, deprecationMsg}` or `{}`.
2. `outbox-writer.ts` derives the columns from `extraData.content` when the caller did not set `deprecated`. That covers submission publish and `createSkillWithVersion`. `scanner.ts` passes `deprecationColumns(fetchedContent)` explicitly, because it stores no content. The private publishing service gets the same spread.
3. `getSkillVersions` selects `deprecated` and `deprecationMsg`. The page renders a new `DeprecatedNotice` from `versions[0]`, kept separate from the existing `DeprecationBanner` (which belongs to `isDeprecated`). It is not suppressed by `recentlyPublished`, and Install stays visible.
4. The detail API adds `deprecated` and `deprecationMsg` from the latest version.

The release order matters: the platform ships before the vskill SKILL.md bump reaches main. Otherwise the old code writes the 1.0.5 row unflagged.

**SpecWeave.**

1. `catalog.ts` gains `deprecated: {name, replacedBy, message}[]` (default `[]`) as an overlay: the name stays in `core` or `optional`, so install keeps it.
2. `update` prints a notice for each deprecated skill installed in the project (`sw-<name>` in `.claude/skills` or `.agents/skills`) and never removes it. The shipped list stays empty, so tests use a fixture catalog.
3. The validator checks the four keys when present: string values, `deprecated` exactly `"true"` or `"false"`, the `replaced-by` shape, `deprecated-since` SemVer, and no nesting.
4. Regenerate `plugins/specweave/skills-catalog.json`.

**Release order.** Platform first (`--no-migrate`), then vskill (npm plus desktop), then SpecWeave patch. After the vskill merge, republish task-skill-announcer, gws and blotato on the platform and take a headless screenshot of the skill page.

Rejected: a nested `metadata.deprecation:` mapping (breaks string-to-string metadata); top-level keys (refused by strict hosts); a new `replacedBy` column (needs a migration).

Risks:
- The platform scanner may not pick up the vskill push quickly. Republishing through the submit path covers it.
- `add.ts` is over the 1,500-line rule already. This change adds only one-line calls.

## Decisions

### Asked

- none (the brief settled the contract)

### Defaulted (change any before sw-do)

- D-01 `deprecated` is the string `"true"`. The validator refuses an unquoted YAML boolean with "quote it". The CLI and platform still read an unquoted `true` as deprecated, to be lenient with old content.
- D-02 task-skill-announcer goes to 1.0.5, not 1.0.4: verified-skill.com has held a 1.0.4 row for it since April 27, 2026, and `(skillId, version)` is unique, so 1.0.4 cannot carry the flag. For the same reason gws goes to 1.0.5 (platform at 1.0.4) and blotato to 1.0.2 (platform at 1.0.1). `deprecated-since` matches the new version.
- D-03 `vskill doctor` exit code: a report whose only issues are `deprecated` exits 0. Other issues keep today's exit 1.
- D-04 Only block-style `metadata` is read, matching `versionFields`. The flow-style object in AC-01 describes the keys, not the YAML layout.
- D-05 Notices go to stderr under `--json`, so stdout stays parseable.
- D-06 Upstream reads use raw.githubusercontent.com only, with a 5 s timeout. Offline or rate-limited means no claim.
- D-07 (lead review, November 25, 2026) The deprecated task-skill-announcer keeps an inert notice: its description no longer carries the broad "run, invoke or test the task skill" triggers, so existing installs see the notice and future bulk installs get a skill that only answers an explicit `/task-skill-announcer`. A test loads the e2e fixture through the Studio frontmatter parser, not just its name.
- D-08 (lead review) AC-06 stays: `specweave update` consumes `catalog.deprecated` (notices, and installed deprecated copies are never rewritten or removed) and the validator consumes the four metadata keys. It reads only local files, so no network bound is needed. The list ships empty: no sw-* skill is deprecated or changed.

### Open

- none

## Tasks

### T-01 vskill deprecation contract module

- AC: AC-01, AC-03 | Files: repositories/anton-abyzov/vskill/src/lib/deprecation.ts, repositories/anton-abyzov/vskill/src/lib/__tests__/deprecation.test.ts | Test: cd repositories/anton-abyzov/vskill && npx vitest run src/lib/__tests__/deprecation.test.ts

### T-02 vskill commands print the notice

- AC: AC-02, AC-03 | Files: repositories/anton-abyzov/vskill/src/commands/outdated.ts, repositories/anton-abyzov/vskill/src/commands/update.ts, repositories/anton-abyzov/vskill/src/commands/add.ts, repositories/anton-abyzov/vskill/src/commands/info.ts, repositories/anton-abyzov/vskill/src/commands/list.ts, repositories/anton-abyzov/vskill/src/commands/doctor.ts, repositories/anton-abyzov/vskill/src/api/client.ts, repositories/anton-abyzov/vskill/src/commands/__tests__/deprecation-notices.test.ts | Test: cd repositories/anton-abyzov/vskill && npx vitest run src/commands/__tests__/deprecation-notices.test.ts src/commands/doctor.test.ts src/commands/outdated.test.ts

### T-03 Deprecate task-skill-announcer, add the fixture, pointer edits

- AC: AC-01, AC-07, AC-08 | Files: repositories/anton-abyzov/vskill/plugins/frontend/skills/task-skill-announcer/SKILL.md, repositories/anton-abyzov/vskill/e2e/fixtures/skills/task-skill-announcer/SKILL.md, repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/__tests__/useCreateSkill.standalone.test.ts, repositories/anton-abyzov/vskill/plugins/google-workspace/skills/gws/SKILL.md, repositories/anton-abyzov/vskill/plugins/marketing/skills/blotato/SKILL.md, repositories/anton-abyzov/vskill/.claude-plugin/marketplace.json, repositories/anton-abyzov/vskill/plugins/frontend/.claude-plugin/plugin.json, repositories/anton-abyzov/vskill/plugins/google-workspace/.claude-plugin/plugin.json, repositories/anton-abyzov/vskill/plugins/marketing/.claude-plugin/plugin.json, repositories/anton-abyzov/vskill/README.md | Test: cd repositories/anton-abyzov/vskill && npx vitest run src/eval-ui/src/hooks/__tests__/useCreateSkill.standalone.test.ts && npm run lint:skills-spec

### T-04 Platform writes the existing SkillVersion columns and shows the badge

- AC: AC-04 | Files: repositories/anton-abyzov/vskill-platform/src/lib/skill-md/deprecation.ts, repositories/anton-abyzov/vskill-platform/src/lib/skill-md/__tests__/deprecation.test.ts, repositories/anton-abyzov/vskill-platform/src/lib/skill-update/outbox-writer.ts, repositories/anton-abyzov/vskill-platform/src/lib/skill-update/scanner.ts, repositories/anton-abyzov/vskill-platform/src/lib/private-publishing/service.ts, repositories/anton-abyzov/vskill-platform/src/lib/data.ts, repositories/anton-abyzov/vskill-platform/src/app/skills/[owner]/[repo]/[skill]/page.tsx, repositories/anton-abyzov/vskill-platform/src/app/skills/[owner]/[repo]/[skill]/DeprecatedNotice.tsx, repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/[owner]/[repo]/[skill]/route.ts, repositories/anton-abyzov/vskill-platform/src/app/skills/[owner]/[repo]/[skill]/__tests__/page.deprecated.test.tsx | Test: cd repositories/anton-abyzov/vskill-platform && npx vitest run src/lib/skill-md/__tests__/deprecation.test.ts src/app/skills/[owner]/[repo]/[skill]/__tests__/page.deprecated.test.tsx src/lib/skill-update

### T-05 SpecWeave catalog deprecated overlay, update notice, validator

- AC: AC-06 | Files: repositories/anton-abyzov/specweave/src/core/skills/catalog.ts, repositories/anton-abyzov/specweave/src/core/skills/project-skills.ts, repositories/anton-abyzov/specweave/src/cli/commands/update.ts, repositories/anton-abyzov/specweave/skills/catalog.json, repositories/anton-abyzov/specweave/plugins/specweave/skills-catalog.json, repositories/anton-abyzov/specweave/scripts/validation/validate-skill-versions.cjs, repositories/anton-abyzov/specweave/tests/unit/core/skills/catalog-deprecated.test.ts, repositories/anton-abyzov/specweave/tests/unit/scripts/validate-skill-versions-deprecation.test.ts | Test: cd repositories/anton-abyzov/specweave && npx vitest run tests/unit/core/skills/catalog-deprecated.test.ts tests/unit/scripts/validate-skill-versions-deprecation.test.ts && node scripts/validation/validate-skill-versions.cjs

### T-06 Host loading check on this machine

- AC: AC-05 | Files: .specweave/increments/1486-skill-deprecation-pointer/reports/host-loading.md | Test: test -s .specweave/increments/1486-skill-deprecation-pointer/reports/host-loading.md

### T-07 Review, merge, release, screenshot

- AC: AC-02, AC-04, AC-07 | Files: .specweave/increments/1486-skill-deprecation-pointer/reports/skill-page-deprecated.png, .specweave/increments/1486-skill-deprecation-pointer/reports/release.md | Test: test -s .specweave/increments/1486-skill-deprecation-pointer/reports/skill-page-deprecated.png && test -s .specweave/increments/1486-skill-deprecation-pointer/reports/release.md

Verify and close 1486.

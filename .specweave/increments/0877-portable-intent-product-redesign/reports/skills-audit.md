# Personal skills and vskill maintenance audit — 0877

Audited 2026-09-14. User authorized autonomous cleanup. Scope: personal and project skills in `.agents/skills`, `.codex/skills`, `.claude/skills`; registered harness paths were then inspected for the exact obsolete names. No plugin caches, domain expertise sources, credentials, or personal content were deleted.

## Completed cleanup

48 obsolete installed locations removed after a byte-preserving backup. Five targeted operations used the built, fixed vskill CLI; one already archived directory and two residual/dangling symlinks required explicit filesystem cleanup. Source fixtures remain intact. Four obsolete project lock entries and one stale skills.sh archive entry were removed.

| Skill / artifact | Locations | Reason | What remains |
|---|---:|---|---|
| `greet-anton` | 13 | Forces a formal greeting before every action; conflicts with current explicit communication preferences and adds no expertise | Original skill repository and backup |
| `tiny-test-plugin` | 6 | Test-only 0853 fixture leaked into active harness discovery | `.specweave/increments/0853-verify-runtime-vskill/fixtures/tiny-skill-source` |
| Malformed `postiz` wrapper | 14 | Every copy contains only 64 bytes: a frontmatter description and unresolved `../../SKILL.md` pointer | Actual Postiz plugin caches and domain posting skills |
| Project `obsidian-brain` | 12 | Old v1.1 project override shadows global v1.4 and prescribes obsolete `CronCreate` workflow | Global v1.4 skill and harness links |
| Personal `my-skill` | 1 | Body exactly duplicates `cold-email`; frontmatter omits name and hardcodes `model: opus` | Correctly named `cold-email`, including references |
| Broken project `remotion-best-practices` link | 1 | Points to nonexistent project target | Working personal Remotion skill |
| Archived Excalidraw skill | 1 | `_archive` lives inside skill discovery; supposedly retired skill remained in session catalog | Backup outside all discovery roots |

`cleanup-manifest.json` records all 48 absolute paths, backup paths, file hashes, symlink targets, reasons, actions, and exact CLI results. All five CLI commands exited 0. Retained actual Codex Postiz plugin and original 0853 fixture were checked after removal.

## Inventory

Counts include nested skills and symlink references. They are not a token-usage estimate: most harnesses load descriptions first and full skill bodies on demand. Plugin caches were deliberately excluded from this six-root physical inventory.

| Root | Before references | After references |
|---|---:|---:|
| `~/.agents/skills` | 58 | 56 |
| `~/.codex/skills` | 12 | 12 |
| `~/.claude/skills` | 54 | 54 |
| Project `.agents/skills` | 18 | 16 |
| Project `.codex/skills` | 19 | 15 |
| Project `.claude/skills` | 19 | 15 |
| Total | 180 | 168 |

Physical `SKILL.md` files: 129 → 119. Distinct frontmatter names, with missing name counted as one: 85 → 80. The 48 removed locations exceed the six-root reduction because obsolete names also existed in Aider, Antigravity, Cursor, Gemini, Kiro, Pi, OpenCode, OpenClaw, Windsurf and other harness paths. The manifest is the location-level authority; `skills-inventory-after.json` lists every retained skill reference, canonical path, size and SHA-256.

`vskill list` originally showed only 20 entries from the project lock. Separate user registries contained 21 entries in `~/.agents/vskill.lock`, four in `~/vskill.lock`, and two in `~/.agents/.skill-lock.json`. A project-only lock listing is not a complete inventory. No claim was made that the existing `list --installed` command detects every manually installed skill.

## Retained expertise and preferences

- Preserved all 23 App Store Connect skills: concrete CLI usage, signing, release, localization, submission and pricing knowledge.
- Preserved Kie.ai, HyperFrames adapters and production video guidance, image providers, frontend design, document/PDF/presentation tools and testing expertise.
- Preserved EasyChamp, futsal highlight workflows, tax/invoicing, resume, Obsidian, npm OTP and Tauri release knowledge. These contain local procedures and facts a stronger model cannot infer safely.
- Preserved chosen caveman style and companion skills. A model capability change does not cancel the user's explicit style preference.
- Preserved divergent social-media skills for now: six references resolve to five different bodies, roughly 79–115k characters. They are not exact duplicates. Deleting one blindly would discard accumulated platform-specific instructions. Consolidation needs a content merge and outcome tests, then narrower triggers and references.
- Preserved the long project `skill-creator`: it includes evaluation procedures beyond the smaller system skill. Length alone is insufficient evidence of no value.

No generic skill was removed merely because a newer model exists. Removal criteria were demonstrable duplication, malformed content, obsolete shadowing, broken discovery or explicit preference conflict.

## vskill correctness changes

Initial `vskill cleanup --dry-run` proposed uninstalling valid `sw@specweave`, `codex@openai-codex`, `caveman@caveman` and `stripe@claude-plugins-official` registrations because it compared user scope with the current project lock. The real command also recursively deleted global plugin caches missing from that project lock.

The fixed command reads user and project ownership separately, including legacy home lockfiles. Cached plugins and anything recorded in Claude's installed-plugin registry survive even when absent from vskill locks. An unreadable registry stops cleanup. Shared caches and unrelated marketplace manifests are preserved; no blanket cache GC or implicit global manifest rewrite remains. Dry-run now says what would change and explicitly says no changes were made. On this machine, the fixed dry-run proposes zero removals.

`vskill remove --global` now preserves the project lock and project plugin registrations; `--local` preserves user registrations. Plugin provenance is resolved per scope, including a plain project skill sharing a name with a global marketplace plugin. Legacy home-lock installs are supported. Nested commands use the resolved project root for filesystem deletion and plugin CLI working directory, matching the lockfile root.

No new Skill Studio UI or broad inventory command was introduced in this lane. Studio has its own removal routes; they were inspected, not silently assumed to share CLI behavior. The existing UI still needs a future unified scope/provenance inventory if all installer surfaces are to report identical state.

## Hook observations supplied to product redesign

Installed Codex `sw` exposes SessionStart, PreToolUse, Stop and PreCompact. Its cached launcher is already locally adapted with live deadlines and a private Git index for compaction work, so removing that protection before replacement would be a regression.

`~/.codex/log/hook-health.jsonl` recorded 150 PreCompact deadline expirations at approximately eight seconds, two compaction index-resolution failures, four SessionStart deadlines, two invalid worker outputs and two worker failures. The observed compaction deadlines alone total approximately 20 minutes of waiting across recorded events. Successes are not logged; this is not a failure rate. Hook product changes are handled in the SpecWeave lane, not by this cleanup.

## Validation

Regression-first checks reproduced seven initial scope/ownership failures, then mixed-source and nested-root/legacy-lock failures. Final scoped suite: 29 tests passing. Focused coverage: 91.01% lines, 91.26% branches, 100% functions; cleanup.ts has 100% line coverage. TypeScript build passes and `git diff --check` is clean.

Full suite exposed environment issues unrelated to changed files. Homebrew Node 26 enables native Web Storage that conflicts with Vitest 3/jsdom; disabling that feature removed 140 failures, but six real-SSE tests still failed under Node 26. Installed Node 22 passes those same SSE tests unchanged. An initial full Node 22 run passed 6,154 tests with one batch-judge timeout under parallel load and one pre-existing ModelList test teardown timer error. Final full run under Node 22 with four workers passed: **623 test files, 6,158 tests passed, three pre-existing skipped** (6,161 total), exit 0. Runtime was 61.61 seconds. No assertions were weakened or skipped; existing dry-run wording assertions were updated to require accurate preview language.

Logs: `vskill-scoped-coverage.log`, `vskill-node26-tests.log`, `vskill-node26-no-webstorage-tests.log`, `vskill-node22-initial-tests.log`, and `vskill-tests-final.log`.

Source commit: `8ce135e` — `0877: preserve scope and ownership during skill maintenance`. No package version bumped; root release lane coordinates publication.

## Recovery

Backup root: `/Users/antonabyzov/.codex/skill-backups/0877` (mode 0700), outside all skill discovery roots. Original bytes and symlink targets were compared against backup before removal. `cleanup-manifest.json` exists both in this report directory and beside the backup.

To restore only a selected name, run `python3 /Users/antonabyzov/.codex/skill-backups/0877/restore.py NAME`. With no name arguments, the script restores all 48 locations. It refuses to overwrite current files, preserves symlinks, and merges missing saved lock entries instead of overwriting newer lockfiles. Restart harness sessions to refresh their already-loaded skill catalogs after any cleanup or restoration.

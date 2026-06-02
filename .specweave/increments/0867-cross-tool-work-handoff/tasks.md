---
increment: 0867-cross-tool-work-handoff
title: "Cross-Tool Work Handoff"
generated: 2026-06-01
test_mode: TDD
---

# Tasks: Cross-Tool Work Handoff

## Foundation: Doc Format + Secret Scrub

### T-001: Implement handoff-doc-format.ts (single-source renderer)
**User Story**: US-001, US-002, US-005, US-006 | **Satisfies ACs**: AC-US1-02, AC-US2-04, AC-US5-02, AC-US5-03, AC-US5-04, AC-US6-02, AC-US6-05 | **Status**: [x] completed
**Test Plan**: Given a `HandoffDocInput` object with increment metadata and git state → When `renderHandoffDoc(input)` is called → Then it returns a markdown string with: (1) absolute doc path as plain text first, (2) clickable markdown link, (3) `.diff` path, (4) fenced paste-prompt between `BEGIN HANDOFF`/`END HANDOFF` markers, (5) per-tool "find your session" tips block, (6) `Doc format v1` footer marker, (7) Redaction section with per-pattern counts and heuristic disclaimer; `--inline` mode embeds the full scrubbed body inside the paste-prompt

### T-002: Implement handoff-secret-scrub.ts (regex redaction)
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-04, AC-US6-05 | **Status**: [x] completed
**Test Plan**: Given a string containing `sk-abc123`, `ghp_xyz`, `Bearer tok`, `password=secret`, `AKIAIOSFODNN7EXAMPLE` → When `scrubSecrets(text)` is called → Then all matches are replaced with `[REDACTED-<type>]` markers and a `{ [pattern]: count }` counts map is returned; Given a clean string → Then counts map is empty and text is unchanged; Given the function is called with the full pattern set → Then all 12 patterns (`sk-`, `ghp_`, `gho_`, `ghs_`, `AKIA`, `ASIA`, `-----BEGIN`, `vsk_`, `xox[bap]-`, `Bearer `, `password=`, `api_key=`) are exercised

## Git State Capture

### T-003: Implement handoff-git-state.ts (branch/sha/status/stat + diff dump)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [x] completed
**Test Plan**: Given a git repo with staged and unstaged changes → When `captureGitState(repoRoot, diffOutputPath)` is called → Then it returns `{ branch, shortSha, statusPorcelain, diffStat }` and writes `git diff HEAD` concatenated with `git diff --cached` to the given diffOutputPath; Given no uncommitted changes → Then diffStat is empty string and diff file is written with empty content; Given `git` is absent from PATH → Then function returns a degraded object with all fields empty and does not throw; Given changes are present → Then the returned object includes a `hasUncommittedChanges: true` flag and the doc includes an uncommitted-warning string

## Core Builder

### T-004: Implement work-handoff.ts — workspace detection + getActive() 0/1/2+ cases
**User Story**: US-001, US-003, US-007 | **Satisfies ACs**: AC-US1-03, AC-US1-04, AC-US1-06, AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Test Plan**: Given a SpecWeave workspace with exactly 1 active increment → When `buildWorkHandoff(repoRoot, {})` is called → Then it detects the workspace via `resolveEffectiveRoot()` + `active-increment.json` (not raw dir test) and proceeds with increment reads; Given 0 active increments → Then it produces a git+config-only doc noting "no active increment" and writes to `.specweave/state/handoff-latest.md`; Given 2+ active increments with no explicit `incrementId` → Then it throws an error listing the candidate ids; Given `resolveEffectiveRoot()` returns a path with a stale `.specweave/` dir but empty/missing `active-increment.json` → Then it is classified as non-SpecWeave (no increment reads attempted); Non-SpecWeave path writes to `.handoff/HANDOFF.md` + `.handoff/handoff.diff` and self-creates `.handoff/.gitignore` with contents `*`

### T-005: Implement work-handoff.ts — increment content assembly + acSyncEvents + ambient rules
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05, AC-US1-07 | **Status**: [x] completed
**Test Plan**: Given a SpecWeave workspace with a valid active increment → When `buildWorkHandoff` runs → Then the doc contains the active increment id + status, current task, next pending task, done/pending task counts with percentage (via `parseTasksWithUSLinks` + `calculateProgressFromTasksFile`), `acSyncEvents` AC/task drift from `metadata.json`, key decisions from `plan.md`, and ambient rules from `config.json` (testMode, coverageTarget, WIP limit); Given `MetadataManager.exists()` returns false → Then metadata reads are skipped (no side-effecting lazy-create); Given the command is run twice → Then the same files are overwritten (idempotent), and no network calls are made

### T-006: Implement work-handoff.ts — ownership sentinel + doc write paths
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04, AC-US3-05 | **Status**: [x] completed
**Test Plan**: Given a non-SpecWeave repo with a root `./HANDOFF.md` that lacks the `Doc format v1` footer → When `buildWorkHandoff` is called → Then it writes to `.handoff/HANDOFF.md` instead and does not overwrite the foreign file; Given a root `./HANDOFF.md` that contains `Doc format v1` → Then it overwrites in-place (treated as a prior handoff); Regardless of which path is chosen → The absolute path of the written file is the first line in stdout output

## CLI Command

### T-007: Implement src/cli/commands/handoff.ts + bin/specweave.js registration
**User Story**: US-001, US-005 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04 | **Status**: [x] completed
**Test Plan**: Given the CLI subcommand `specweave handoff [incrementId] [--reason --summary --next --gotcha --decision] [--inline] [--out <path>]` is invoked → When parsing succeeds → Then `handoffCommand(opts)` is called with the parsed options; Given `--inline` is passed → Then the paste-prompt embeds the full scrubbed doc between `BEGIN HANDOFF`/`END HANDOFF` markers; Given no options → Then output order is: (1) absolute path plain text, (2) clickable link, (3) `.diff` path, (4) fenced paste-prompt, (5) per-tool tips; Verify commander wiring in `bin/specweave.js` uses a lazy `import('../dist/src/cli/commands/handoff.js')` identical to `create-increment` pattern; Given `--inline` / `--clipboard` → Then the paste-prompt instructs the resuming agent to STOP if the doc path does not exist on the current machine

### T-008: Per-tool resume command matrix — verified strings in handoff-doc-format.ts
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02 | **Status**: [x] completed
**Test Plan**: Given the `renderHandoffDoc` per-tool block → When rendered → Then it contains exactly these commands: `claude -r <uuid>`, `codex resume <uuid>` and `codex resume --last` (no `--continue`), `opencode -s <id>` and `opencode --session <id>`, `/chat resume <tag>` for Gemini, Antigravity Agent Manager instruction, `aider --restore-chat-history`; The Claude double-dash munge rule is present with an explicit example (`.../specweave-umb/.claude-worktrees/...` → `-...-specweave-umb--claude-worktrees-...`); These strings are the inputs to `cross-tool-commands.test.ts` pin assertions

## Gitignore Extension

### T-009: Extend gitignore-generator.ts with .handoff/ and handoff-latest.*
**User Story**: US-006 | **Satisfies ACs**: AC-US6-03, AC-US6-04 | **Status**: [x] completed
**Test Plan**: Given the `GITIGNORE_ENTRIES.specweave` array in `src/cli/helpers/init/gitignore-generator.ts:417` → When inspected after edit → Then it contains `.handoff/` and `.specweave/state/handoff-latest.*`; Given the non-SpecWeave path runs → Then `.handoff/.gitignore` is written with content `*`; No `git add` hint is printed by the CLI command

## Rename: handoff-context.ts → install-handoff-context.ts

### T-010: Rename src/core/session/handoff-context.ts to install-handoff-context.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test Plan**: Given `handoff-context.ts` has zero importers (verified) → When renamed to `install-handoff-context.ts` → Then `grep -r "handoff-context"` in the repo returns no matches; `npx vitest run` continues to pass after rename (no broken imports)

## PreCompact Hook Handler

### T-011: Implement src/core/hooks/handlers/pre-compact.ts + register in hook-router.ts
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04, AC-US7-05 | **Status**: [x] completed
**Test Plan**: Given `HANDLERS` in `hook-router.ts` has no `pre-compact` entry today → When the new handler is registered → Then `hookRouter('pre-compact', stdin)` routes to it instead of `getSafeDefault`; Given the handler runs → Then it calls `buildWorkHandoff` with up to 5 short string fields (reason, summary, next, gotcha, decision) parsed from stdin JSON → writes a doc byte-compatible with the CLI output; Given a `stop-handoff` handler is registered gated on a session flag → Then it fires only when the flag is present, not on every turn-end; Verify `plugins/specweave/hooks/hooks.json` does NOT need structural changes (PreCompact + Stop arrays already dispatch to `specweave hook pre-compact`/`stop`)

## Plugin Command + Skill

### T-012: Create plugins/specweave/commands/handoff.md
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test Plan**: Given `plugins/specweave/commands/handoff.md` is created with correct frontmatter (`description`, `argument-hint`) → When loaded by the SpecWeave plugin runtime → Then `/sw:handoff [incrementId]` is a recognized command; The command body shells to `specweave handoff` and surfaces the 3 outputs (abs path, diff path, paste-prompt) in the correct order; Format mirrors `next.md` / `progress.md` structure

### T-013: Create plugins/specweave/skills/handoff/SKILL.md (flat dir, sw/handoff namespace)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test Plan**: Given `plugins/specweave/skills/handoff/SKILL.md` is created → When invoked as `/sw:handoff` by directory name → Then the skill triggers the handoff workflow; The SKILL.md frontmatter has `name: sw/handoff` (namespaced per flat-dir convention); The skill documents the doc format and trigger phrases

## vskill Self-Contained Skill

### T-014: Create vskill skills/handoff/SKILL.md (self-contained, template inlined, version 1.0.0)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [x] completed
**Test Plan**: Given `skills/handoff/SKILL.md` in the vskill repo exists → When `emitSkill()` distributes it → Then it writes exactly one `SKILL.md` per agent target and copies no sibling files; Given `specweave` is NOT on PATH → Then the skill uses `git` capture + a short interview to build a byte-compatible `.handoff/HANDOFF.md`; Given `specweave` IS on PATH → Then the skill calls `specweave handoff` as an accelerator; The frontmatter `version` is `"1.0.0"` and slug `handoff` has no collision in the agent registry; Given the template is inlined in the skill body → Then the resulting doc has the same `Doc format v1` footer marker and same paste-prompt structure as the CLI output

## Tests

### T-015: work-handoff.test.ts — full scenario coverage
**User Story**: US-001, US-003, US-004, US-006 | **Satisfies ACs**: AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07, AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US6-01, AC-US6-02, AC-US6-05 | **Status**: [x] completed
**Test Plan**: Given temp fixtures for each case → When each test runs → Then:
- 1 active increment: doc contains id/status/current task/next task/AC counts+%/`acSyncEvents`/plan decisions/config ambient rules
- 0 active: git+config-only doc noting "no active increment"
- 2+ active without explicit id: error listing candidate ids
- Non-SpecWeave: `.handoff/HANDOFF.md` + `.handoff/.gitignore`=`*` created
- Uncommitted edits: `.diff` file written with combined diff content, inline stat shown, uncommitted warning present
- `acSyncEvents` drift: surfaced from mocked `metadata.json`
- Secret scrub: planted `sk-abc`, `ghp_xyz`, `Bearer tok` in both free-text and diff → replaced with `[REDACTED-*]`, per-pattern counts in Redaction section, heuristic disclaimer present
- Stale `.specweave/` dir with empty `active-increment.json`: classified as non-SpecWeave
- Ownership sentinel: foreign `./HANDOFF.md` without `Doc format v1` → writes to `.handoff/HANDOFF.md`

### T-016: cross-tool-commands.test.ts — pin test for per-tool resume strings
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-05 | **Status**: [x] completed
**Test Plan**: Given the resume command strings extracted from `handoff-doc-format.ts` → When the pin test asserts them → Then: `claude -r <uuid>` pattern matches (with double-dash munge example verified), `codex resume <uuid>` and `codex resume --last` present (no `--continue`), `opencode -s <id>` and `opencode --session <id>` present, `/chat resume <tag>` Gemini, Antigravity Agent Manager string, `aider --restore-chat-history`; Any future drift in these strings causes the test to fail at build time

### T-017: Format-parity check — CLI doc vs vskill inlined template
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-04 | **Status**: [x] completed
**Test Plan**: Given `handoff-doc-format.ts` renders a doc and the inlined vskill template is extracted → When both are rendered with the same inputs → Then they produce docs with: same section headers in same order, same `Doc format v1` footer marker, same paste-prompt `BEGIN HANDOFF`/`END HANDOFF` delimiters; Test fails if the vskill template diverges structurally from the CLI renderer

## Documentation

### T-018: Create living-doc page docs/.../handoff.md + ADR
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-02, AC-US8-03, AC-US8-04 | **Status**: [x] completed
**Test Plan**: Given `docs/.../handoff.md` is created → When reviewed → Then it contains: (1) the full 10-tool cross-tool matrix table (Claude Code, Codex, OpenCode, Gemini, Antigravity, Cursor, Aider, Cline/Roo, Windsurf, SpecWeave) with columns Tool/session-storage-path/find-current-session/native-resume-cmd/export-transferable; (2) lead card "Works in 8+ tools"; (3) headline "Run out of tokens? Hand off your work to any AI tool — pick up exactly where you left off, uncommitted edits and all."; (4) the four differentiator moats (uncommitted edits captured, token-crash survival, secret-scrubbed+gitignored, cross-machine `--inline`); (5) long-tail SEO keywords including "switch from Claude Code to Codex mid-task", "out of tokens Claude continue elsewhere", "opencode export session", "continue AI session on another machine", "portable AI context handoff"; ADR written to `.specweave/docs/internal/architecture/adr/0867-01-portable-handoff-document-as-cross-tool-context-boundary.md`

## Parser Root-Fix (discovered during 0867 — authorized scope extension)

### T-019: Fix parseTasksWithUSLinks same-line field drop + regression tests
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed
**Test Plan**: Given a tasks.md line combining `**User Story**: … | **Satisfies ACs**: … | **Status**: [x] …` → When `parseTasksWithUSLinks` runs → Then ALL THREE fields parse (status no longer dropped); Given the multi-line format (each field on its own line) → Then it still parses unchanged; Regression tests added in `tests/unit/generators/task-parser.test.ts` for both layouts + a Priority-then-Status combined line (value must not swallow the next `|` segment); Full `task-parser` + `us-progress-tracker` + `completion-validator` suites stay green; `work-handoff.ts` reverted from its checkbox workaround to `calculateProgressFromTasksFile`. ROOT CAUSE: field regexes were `^`-anchored and the userStory match early-`continue`d past same-line fields (task-parser.ts). FIX: unanchor field regexes + accumulate all same-line field matches before `continue`. IMPACT: sw:progress / closure gates / acSyncEvents previously under-reported completion as 0% on the canonical one-line format codebase-wide.

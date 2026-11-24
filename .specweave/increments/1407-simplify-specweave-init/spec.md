# Simplify specweave init

## Problem

`specweave init` grew into a wizard. In 3.1.25 it runs 19 steps across about 8,000 lines, asks between 5 and 15 questions in a terminal, and does things nobody asked for: it commits the person's whole folder, moves their files, offers to delete a parent folder's `.specweave`, and turns sync on from a Git remote. A re-run is not safe: it resets `config.json` to defaults. SpecWithCode refuses folders without Git, or runs `git init` itself when the person clicks "Set up Git and SpecWeave" (1392).

Evidence: `reports/2026-11-18-specweave-init-today-inventory-1d2af0-1e8dce.md` (steps table, 12 defects, seven scratch runs), `reports/reviews/2026-11-18-code-review-xhigh.md` (50 findings), `reports/reviews/2026-11-18-muse-proposal-round-1.md` and `-round-2.md` (adversarial reviews of this proposal).

## Scope

In:

1. The inventory of what init does today (report).
2. A proposal for a much simpler init, reviewed, sent to Anton to accept.
3. Small bug fixes that do not depend on the proposal (PR #2302).
4. After Anton accepts: the redesign itself.

Out: the app's SpecWeave step in onboarding (1387, 1396) and its Git step (1392); what the tool adapters write; `sync setup` beyond a sentence in its help.

## Proposal

`specweave init [folder]` becomes one path with no questions, safe to run any number of times.

### What it does

1. **Checks first, writes nothing yet.** An unknown `--adapter` is refused; values of the ignored flags are not checked. Refused, each in one line naming the reason: the home directory; the system temp folder itself (folders inside it, such as `mktemp -d`, are allowed); a folder below another SpecWeave project (an ancestor with `.specweave/config.json`), naming that project; a linked Git worktree whose effective SpecWeave root (resolved through its main checkout, as `specweave status` already does) is somewhere else, naming that root, or, when there is none, naming the main checkout; a `config.json` that is a symlink or not a JSON object (the only refusals `--force` overrides, by backing up `.specweave` and starting over). An ancestor `.specweave` without a config, `~/.specweave` included, is ignored and never deleted. The "suspicious path" guard goes.
2. **`.specweave/`**: `increments/`, `state/` (empty, gitignored), `memory/MEMORY.md` (only when missing; never rewritten), `config.json` (rewritten only when its content changes). Keys already in the config win; defaults fill only what is missing, one level deep. The defaults are the shape `ensureConfigFile` writes in PR #2302 (`testing.commands`, `limits`, `planning`, `auto: {maxTurns, maxSessionAge, requireTests}`, `livingDocs`, `workspace`, `lsp: {enabled: true}`), with no top-level `sync` block; each registered `workspace.repos` entry keeps its usual `sync: {}`. 1.x keys stay for `specweave update` to migrate. `workspace`: `name`, `rootRepo` and any other key the project set are kept; `repos` keeps every entry as it is and appends checkouts found up to three folders deep that are not listed yet; while checkouts are registered, a missing `repository.umbrellaRepo` is filled with `true`. A deeper checkout in a folder without Git is neither registered nor named. Nothing is removed, so an entry deleted by hand comes back while its checkout is still there.
3. **`AGENTS.md` and `CLAUDE.md`**: created, or only the managed block updated, under the project name saved in the config (the folder name only for a new config), so a re-run through a linked worktree or another path changes nothing. `README.md` only when the folder has none.
4. **`.gitignore` and `.gitattributes`**: a `.gitignore`, new or existing, gets only SpecWeave's own lines when they are missing (`.specweave/state/`, logs, backups and the like). Init no longer decides what a project's language or framework should ignore: no stack detection, no template of other people's rules, no backup file. The static template is deleted.
5. **The `sw-*` skills** in `.claude/skills/` and `.agents/skills/`. These folders are managed: an edit inside a core skill is replaced on the next run, as today.
6. **Files for the recorded tool**, through its adapter, when the tool is not Claude Code. For Claude Code, `.claude/settings.json` on a first run only, so `specweave autocompact off --project` sticks. A first run is one where `config.json` did not exist when the run started; a `--force` fresh start counts as one.

Steps 3 to 6 read the config step 2 wrote to disk; no signatures change. Writing it early means another `specweave` command started meanwhile finds the right project.

Output: 12 lines or fewer when piped, naming what was created, updated or left alone, and the next command. Adapter output is captured; an adapter's problems appear among the summary's warning lines (four at most).

### Git

Init never creates or changes a Git repository: no `git init`, no `git add`, no commit. No Git process runs, for any tool. It reads only `.git` files and folders: whether one is above the folder and, for a linked worktree, its main checkout (step 1). The one exception is `--git-hooks`, an explicit opt-in that writes a pre-commit hook into `.git/hooks/`. In a folder without Git init prints one hint line and exits 0.

### The tool

Recorded, never asked: `--adapter` when given, else the tool already saved in the config, else `SPECWEAVE_TOOL` when it names a known tool, else Claude Code. No folder or file detection: today's adapter checks treat any `AGENTS.md` as Codex, Gemini or Antigravity. `SPECWEAVE_TOOL` names the agent running now (the app sets it per thread), so the agent that runs the first init sets the project's tool until `--adapter` changes it; an unknown value such as `grok` or `pi` is ignored. An unknown saved tool gets one warning line and is replaced in the config by the next choice.

### What leaves init

| Today | After |
|---|---|
| `git init`, `git add .`, commit | Gone (see Git above) |
| Language question, 9 translations | English output. `--language` is accepted and ignored: it never changed a file |
| Tool question (17 tools) | Recorded by the rule above |
| Start empty / restructure / clone / copy menus | `specweave init`, then `specweave get owner/repo`. Restructure and copy-local are deleted with no successor |
| Root repo question, sync switched on from a remote, `repository.provider` filled from the remote | Nothing is granted or detected at init: a new config says `provider: "local"`. `specweave sync setup` in a terminal is the only way to connect a tracker |
| Empty `repositories/` folder | Created by `specweave get` with the first repository |
| Copying skills out of `~/.claude/plugins/cache` | Gone; `specweave refresh-plugins` is the per-tool path |
| "Remove stale .specweave in a parent folder?" | Gone |
| Fresh start prompt | `--force` keeps its one meaning: back up `.specweave`, then start over. It no longer passes any guard; the temp guard narrows to the temp folder itself, and a project inside another one is refused without an escape |
| skill-creator download switch | Gone from init and from `update-instructions` |
| About 50 lines of output | 12 at most |
| `specweave get` runs init in each repository it registers | Not any more: a registered repository belongs to the workspace's plan. Outside a workspace the clone sits inside the project, where init refuses, so `get` runs no init anywhere; `--no-init` is accepted and ignored |

### Flags

| Flag | After |
|---|---|
| `[folder]`, `-n/--name`, `-a/--adapter`, `-f/--force`, `--git-hooks` | Kept |
| `-q/--quick`, `--non-interactive` | Kept, no effect: nothing asks |
| `-l/--language`, `-t/--template`, `--tech-stack`, `--full`, `--force-refresh` | Accepted with any value and ignored until 4.0 |

### Re-run

A re-run is the first run again. Run twice in a row on the same version it changes no file's content (`config.json` is not even rewritten). After a deleted `AGENTS.md`, `CLAUDE.md`, skill or `.gitattributes`, or an interrupted run, it restores them; `.claude/settings.json` is written on a first run only, so a deleted one stays deleted. This covers a CLI re-run; the app skips init once a config exists, and changing that belongs to the onboarding thread.

### SpecWithCode

`init --quick --adapter claude` and `npx --yes specweave@3` stay valid, and success stays "exit 0 plus a regular `.specweave/config.json`". The file list the app shows stays true, README included. It ships as 3.2.0, which installed apps, and anyone running `npx specweave@3`, pick up at once through the `@3` range (D-05). After that the app can stop refusing folders without Git; that is the onboarding thread's change.

### How it is built

Init becomes a thin caller of the writers `specweave update` already uses and tests: `applyInstructionTemplate`, `ensureSpecweaveGitignoreEntries`, `ensureGitattributes`, `installProjectSkills`, and the config fill from PR #2302. Two PRs. The first switches init to that path, removes the questions, Git and sync defaults, and in the same diff rewrites or deletes the tests that pin the old behaviour (`init-multirepo`, `init-repo-clone-flow`, `init-workspace-config`, `init-integration`, `init-path-resolution`, `init-config-validation` and the helper suites they lean on), so it is large on the test side. The second deletes the helpers nothing calls any more (about 3,000 lines) and their unit tests; it changes no behaviour. `specweave get` stops calling init in a cloned repository; that call cannot succeed today.

## Acceptance Criteria

Now:

- [ ] AC-01: The inventory report lists every init step with what it asks, writes and how it fails, each checked by a run.
- [ ] AC-02: The proposal is reviewed by the code-review skill and by Muse Wonderful at xhigh, and Anton has it to accept.
- [ ] AC-03: A re-run of init keeps every key already in `.specweave/config.json` (test commands, tracker, `repository` including `provider: "local"`, sync, lsp, tool, `workspace.rootRepo`, 1.x keys, custom keys). A config that is not a JSON object stops init with one line and exit 1 before anything is written.
- [ ] AC-04: An unknown `--adapter` exits 1 with one line before anything is written or removed, `--force` included.
- [ ] AC-05: Init in a subfolder of a Git repository creates no nested repository and no commit (today a subfolder init commits into a new nested repository); `.specweave` in that subfolder is still allowed. A home folder kept as a repository does not count, and a leaked `GIT_DIR` is ignored.
- [ ] AC-13: A fresh start whose backup fails deletes nothing and exits 1; two fresh starts on one day leave two backups.
- [ ] AC-14: Prisma and Drizzle migrations are not ignored, by the generator or the template; a `.gitignore` that needs no change gets no backup file. Lines an older init already wrote stay until the redesign.

After Anton accepts:

- [ ] AC-06: Init asks nothing in a terminal.
- [ ] AC-07: A second run right after the first, same version, changes no file: every file is byte-identical and none is added. Checked for Claude Code, Codex and Cursor on Linux CI and, through `.github/workflows/init-crossplatform.yml`, on Windows and macOS.
- [ ] AC-08: Init starts no Git process for any tool (a fake `git` on `PATH` is never run for Claude Code, Codex and Cursor). In a folder without Git it exits 0 and creates no `.git`. In a repository it adds no commit and stages nothing.
- [ ] AC-09: After `AGENTS.md`, a skill folder or `.gitattributes` is deleted, a CLI re-run restores it.
- [ ] AC-10: `specweave init --quick --adapter claude` exits 0 and leaves a regular `.specweave/config.json`; every flag in the Flags table is accepted.
- [ ] AC-11: Init writes no `sync` key and no `repositories/`, reads nothing under `~/.claude`, and writes nothing outside steps 2 to 6 (each adapter's files are listed in the footprint test) and `.git/hooks/` under `--git-hooks`.
- [ ] AC-12: Piped output is 12 lines or fewer.
- [ ] AC-15: Each refusal in step 1 exits 1 with one line and leaves the folder as it was, including a linked worktree with a gitignored `.specweave` in its main checkout and a symlinked `config.json`; an ancestor `.specweave` without a config does not block and is not deleted; `init` inside a `mktemp -d` folder works.

## Approach

Fix PR #2302 (branch `fix/1407-init-rerun-safety`, `repositories/anton-abyzov/specweave`): `ensureConfigFile` replaces the unconditional `createConfigFile` at `src/cli/commands/init.ts:496`, and the block after it stops replacing `repository`, `workspace`, `lsp` and `sync` and keeps 1.x keys; a config that is not a JSON object is refused before any write; the saved tool wins over detection; `--adapter` is validated at the top of `initCommand`; `git rev-parse --show-toplevel` (with `GIT_DIR` cleared, home exempt) replaces the `.git` existence check, so a subfolder init also makes no commit; the home guard covers `init <path>`; `smart-reinit.ts` stops on a failed backup and names backups by time; the gitignore generator and template stop ignoring Prisma and Drizzle migrations and write `.gitignore.backup` only on change. Muse review of the diff, green CI, squash merge, patch release through `bash scripts/release/release.sh`.

Redesign: as in "How it is built".

Rejected: a guided interactive mode beside the quiet one (two paths is how the defects got in); a new `initProject` written from scratch (the writers `update` uses already do it and are tested); sending "start over" to `specweave uninstall` (it leaves the skills and settings behind and edits a global lock file).

Risks: CLI users who relied on the first commit, on init switching sync on from a remote, on stack-specific `.gitignore` rules for new projects, or on the copy-local menu; Windows projects with their own `.gitattributes` may show line-ending churn (AC-07 now has a Windows leg); every `@3` user gets 3.2.0 at once. Two-init races are not locked: the writers are content-addressed, so a lost race writes the same bytes.

## Decisions

### Asked
- D-01 Does init touch Git at all? → **Never** (Anton, November 18, 2026): it never creates or changes a repository; read-only checks only, plus the `--git-hooks` opt-in.
- D-05 Version → **3.2.0** inside the `@3` range (Anton, November 18, 2026).

### Defaulted (change any before sw-do)
- D-02 No questions at all, English output only.
- D-03 `--force` means fresh start with a backup and nothing else; it overrides only the symlinked and unreadable `config.json` refusals, which it repairs by starting over.
- D-04 `README.md` is still written when the folder has none, so the app's file list stays true.
- D-06 Sync is never switched on by init.
- D-07 `.gitignore` gets only SpecWeave's own lines; the static template and stack detection go.

### Open
- none

## Tasks

### T-01 Inventory report
- AC: AC-01 | Files: .specweave/increments/1407-simplify-specweave-init/reports/2026-11-18-specweave-init-today-inventory-1d2af0-1e8dce.md | Test: test -s .specweave/increments/1407-simplify-specweave-init/reports/2026-11-18-specweave-init-today-inventory-1d2af0-1e8dce.md

### T-02 Proposal, both reviews, sent to Anton
- AC: AC-02 | Files: .specweave/increments/1407-simplify-specweave-init/spec.md, .specweave/increments/1407-simplify-specweave-init/reports/reviews/ | Test: ls .specweave/increments/1407-simplify-specweave-init/reports/reviews/

### T-03 Fix the re-run, adapter, Git, backup and gitignore bugs with tests
- AC: AC-03, AC-04, AC-05, AC-13, AC-14 | Files: repositories/anton-abyzov/specweave/src/cli/commands/init.ts, repositories/anton-abyzov/specweave/src/cli/helpers/init/, repositories/anton-abyzov/specweave/src/adapters/adapter-loader.ts, repositories/anton-abyzov/specweave/tests/unit/cli/ | Test: npx vitest run tests/unit/cli/commands/init-rerun-safety.test.ts tests/unit/cli/helpers/init/fresh-start.test.ts tests/unit/cli/helpers/init/gitignore-generator.test.ts

### T-04 Review, merge and release the fixes
- AC: AC-03, AC-04, AC-05, AC-13, AC-14 | Files: repositories/anton-abyzov/specweave/CHANGELOG.md | Test: npm view specweave version

### T-05 Redesign PR 1: init calls the update writers, no questions, no Git (after D-01)
- AC: AC-06, AC-07, AC-08, AC-09, AC-11, AC-12, AC-15 | Files: repositories/anton-abyzov/specweave/src/cli/commands/init.ts, repositories/anton-abyzov/specweave/src/cli/commands/get.ts, repositories/anton-abyzov/specweave/src/cli/helpers/init/, repositories/anton-abyzov/specweave/src/adapters/adapter-base.ts, repositories/anton-abyzov/specweave/bin/specweave.js, repositories/anton-abyzov/specweave/scripts/completions/, repositories/anton-abyzov/specweave/tests/unit/cli/, repositories/anton-abyzov/specweave/tests/unit/adapters/, repositories/anton-abyzov/specweave/.github/workflows/init-crossplatform.yml, repositories/anton-abyzov/specweave/docs-site/docs/ | Test: npm run test:unit

### T-06 Redesign PR 2: delete the helpers nothing calls and their unit tests
- AC: AC-06 | Files: repositories/anton-abyzov/specweave/src/cli/helpers/init/, repositories/anton-abyzov/specweave/src/cli/commands/update-instructions.ts, repositories/anton-abyzov/specweave/tests/unit/cli/ | Test: npm run test:unit

### T-07 App contract check and release 3.2.0
- AC: AC-10 | Files: repositories/anton-abyzov/specweave/tests/unit/cli/commands/init-app-contract.test.ts, repositories/anton-abyzov/specweave/CHANGELOG.md | Test: npx vitest run tests/unit/cli/commands/init-app-contract.test.ts

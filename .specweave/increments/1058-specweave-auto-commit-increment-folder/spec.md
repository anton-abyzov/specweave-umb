# SpecWeave auto-commit increment folder

## Problem

On October 24, 2026 the umbrella repo `/Users/antonabyzov/Projects/github/specweave-umb` had 59 untracked increment folders and 19 modified tracked increment files. Specs, ledgers and claims for about two weeks of work never reached other machines until they were committed by hand in umbrella commit `9e460c23e`.

`specweave task claim|done|skip|block|release` and `specweave create-increment` write `.specweave/increments/<id>/spec.md`, `ledger.jsonl` and `metadata.json` and never commit them. `task done` only warns when the HEAD subject does not name the increment. `specweave handoff` pushes the branch when it is ahead and pushes a private-index snapshot of the whole working tree to `specweave-handoff` and `wip/<branch>`, but it never commits increment files to the branch itself, so a normal `git pull` elsewhere does not see them.

## Scope

In (anton-abyzov/specweave CLI):
- config keys `git.autoCommitIncrement` and `git.autoPushIncrement` in `.specweave/config.json`, both default off;
- a `--no-commit` flag on `task`, `create-increment` and `handoff`;
- a pathspec-only commit of the increment's own bookkeeping files after each of those commands, plus an optional fast-forward push;
- tests in temporary git repos, and docs.

Out: committing code, evidence, reports or any other file; changing `pushHandoff` snapshot behavior; any version bump, npm publish or merge.

## Acceptance Criteria

- [ ] AC-01: With no `git` block in `.specweave/config.json`, or with `git.autoCommitIncrement` not `true`, no command creates a commit. `--no-commit` on `task`, `card` (T-NN cards), `create-increment` and `handoff` skips the commit even when the key is on.
- [ ] AC-02: When on, `task claim|done|skip|block|release` (including `release --all-mine`), `create-increment` and `handoff` commit only that increment's own `spec.md`, `ledger.jsonl` and `metadata.json` that exist, plus `handoff.md` only when the repo already tracks it. New files are added with `git add -- <paths>`, then committed with `git commit --only -- <paths>`; an unrelated file staged before the command stays staged and out of the commit.
- [ ] AC-03: Nothing under the increment's `evidence/` or `reports/`, and no gitignored path, is ever staged or committed by the auto-commit.
- [ ] AC-04: The subject is one line under 72 characters, `NNNN: <action> T-xx` (for example `1058: done T-02`, `1058: release T-01, T-03`, `1058: create increment`, `1058: handoff`), with no body, trailers or emoji. Repo hooks run; `--no-verify` is never passed.
- [ ] AC-05: A failed or skipped commit (hook failure, `index.lock`, detached HEAD, no commits yet, a rebase, merge, cherry-pick, revert or bisect in progress, or a `handoff` whose branch push would land it on a differently named or local upstream) keeps the ledger write, prints one `warning:` line on stderr and the command exits as it would without auto-commit. A new file the command added to the index is taken back out when the commit fails.
- [ ] AC-06: With `git.autoPushIncrement: true`, a successful auto-commit is pushed to the current branch's upstream, using the upstream's remote from git config (whatever URL it holds, HTTPS or SSH), never with `--force`. It pushes only to a same-named branch on a real remote that is also the push remote, and only when every unpushed commit is an auto-commit (an auto subject and only `spec.md`, `ledger.jsonl`, `metadata.json` or `handoff.md` changed). No upstream, a local or differently named upstream, a diverged branch or other unpushed commits skip the push with a warning. Push failure is a warning, exit 0. Off by default. `handoff` leaves pushing to its own branch push (so `--no-push` still keeps everything local), and holds that branch push with a warning when the branch is ahead of a local or differently named upstream by auto-commits alone.
- [ ] AC-07: The `task done` traceability warning and the `HEAD <sha>` evidence skip auto-commit subjects, so they still point at the last work commit.
- [ ] AC-08: The CLI docs for tasks and handoff describe both keys, `--no-commit`, what is and is not committed, and the failure behavior.

## Approach

1. `src/core/increment/auto-commit.ts`: `readAutoCommitConfig(projectRoot)` (sync read like `readLeaseHours`), `autoCommitIncrement(projectRoot, incDir, { incrementId, action, tasks?, commit?, push?, alsoDirs? })` returning `{ status: 'off' | 'nothing' | 'committed' | 'skipped' | 'failed', sha?, subject?, warnings[] }`, `isAutoCommitSubject(subject)`. Git runs in the repo that contains the increment folder; paths come from `git rev-parse --show-toplevel --show-prefix` run in that folder, so symlinks and letter case match the index. `GIT_TERMINAL_PROMPT=0`.
2. Candidate paths are fixed file names at the top of the increment folder, so `evidence/` and `reports/` cannot match. Each untracked candidate passes `git check-ignore` before `git add`.
3. Pre-checks: inside a work tree, on a branch (`symbolic-ref`), HEAD exists, no `index.lock`, no `MERGE_HEAD`, `CHERRY_PICK_HEAD`, `REVERT_HEAD`, `BISECT_LOG`, `rebase-merge` or `rebase-apply` under `git rev-parse --git-path`.
4. Wire into `src/cli/commands/task.ts` (success paths only; JSON output gains `commit`), `src/cli/commands/create-increment.ts` (after hooks, includes a superseded increment's folder), and `src/core/session/work-handoff.ts` (after the doc is written, before `pushHandoff`, never for PreCompact checkpoints). `bin/specweave.js` adds `--no-commit`.
5. `src/core/config/types.ts`: `IncrementGitConfig` and `git` in `KNOWN_CONFIG_KEYS`.

Rejected: `git add -A .specweave/increments/<id>` (sweeps in evidence and reports); committing through a private index with `commit-tree` (skips the repo's hooks, which must run); auto-push on by default (the umbrella is public and pushes are outward-facing).

Fresh-context review (October 24, 2026) found: push could land a branch on a differently named upstream (`feat/x` tracking `origin/main`) and publish other unpushed commits; `task done` evidence looked back only 50 commits; a path typed in another letter case committed nothing silently; a failed `git rm --cached` went unreported; the AC-04 example disagreed with the code. All five are fixed with tests. A second fresh check found `git rm --cached` could stage a deletion after another lane committed the file, `--grep` matched body lines, and `check-ignore` quoted non-ASCII paths; fixed. A third (head `7038d4f`) found `handoff`'s own branch push could carry the auto-commit to a differently named upstream, handoff commit warnings missed stderr, and glob characters in folder names widened pathspecs; fixed with `callerPushesBranch`, stderr warnings and `:(literal)` pathspecs. A fourth (head `f9da0b2`) found the guard read the branch from `symbolic-ref --short`, which says `heads/<name>` when a tag shares the name, so `handoff` committed onto a differently named upstream; fixed by reading the full `refs/heads/` ref. The same round's notes are also fixed: a half-set upstream no longer false-skips, inherited `GIT_*_PATHSPECS` no longer break every commit, and `card` gains `--no-commit`. A fifth (head `75e6d27`) found the guard read the last `branch.<name>.merge` value while `@{u}` uses the first; both the guard and the push now read the upstream through `for-each-ref`, as git resolves it. A sixth (head `d81930d`) found a fetch refspec that files the upstream under another name (`refs/remotes/origin/team/*`) got past the guard, since `pushHandoff` pushes to the name it reads off `@{u}`; the guard now also requires the remote-tracking ref `refs/remotes/<remote>/<branch>`. Its notes are fixed too: an auto-commit must also touch only bookkeeping files, so a code commit with an auto subject is never pushed along, and an unfetched upstream says so. A seventh (head `5389d81`) found earlier `task`/`card` auto-commits still rode `handoff`'s branch push onto a differently named upstream after the handoff skipped its own commit; `autoCommitPushHold` now holds that branch push (`PushOptions.holdBranch`) when only auto-commits are unpushed. Its notes are fixed: auto-commit files must sit in an increment folder (with `--no-renames`), and `log.showSignature` no longer breaks the check.

Risk: a slow pre-commit hook makes every task command slower. Commits time out after 120 s and turn into a warning.

## Decisions

### Asked
- D-01: Opt-in, default off, with `--no-commit` → user directive (October 24, 2026).
- D-02: Never `--no-verify`; failures non-fatal; push ff-only and off by default → user directive.
### Defaulted (change any before sw-do)
- D-03: Key names `git.autoCommitIncrement` and `git.autoPushIncrement` under a new top-level `git` block (the existing `cicd.git` is branch naming for PR pushes; a separate block keeps the ledger behavior readable).
- D-04: The repo's default branch is `develop`; the lane branches from `origin/develop` and the PR targets `develop`.
- D-05: Only success paths commit. A lost race or refused claim still writes the ledger; the next successful command commits it, because the ledger file is cumulative.
### Open
- none

## Tasks

### T-01 Auto-commit helper and config keys
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: src/core/increment/auto-commit.ts, src/core/config/types.ts, tests/unit/core/increment/auto-commit.test.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave/feat-increment-autocommit && npx vitest run tests/unit/core/increment/auto-commit.test.ts

### T-02 Wire task, create-increment and handoff, plus --no-commit
- AC: AC-01, AC-02, AC-05, AC-06, AC-07 | Files: src/cli/commands/task.ts, src/cli/commands/create-increment.ts, src/cli/commands/handoff.ts, src/core/session/work-handoff.ts, bin/specweave.js, scripts/completions, tests/unit/cli/commands/increment-autocommit.test.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave/feat-increment-autocommit && npx vitest run tests/unit/cli/commands/increment-autocommit.test.ts

### T-03 Docs for tasks and handoff
- AC: AC-08 | Files: README.md, docs-site | Test: grep -rn "autoCommitIncrement" README.md docs-site/docs

### T-04 PR with green exact-head CI
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08 | Files: - | Test: gh pr checks <PR> --repo anton-abyzov/specweave

### T-05 Verify and close 1058
- AC: - | Files: .specweave/increments/1058-specweave-auto-commit-increment-folder | Test: specweave verify 1058

### T-06 Installed acceptance on the published CLI
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: .specweave/increments/1058-specweave-auto-commit-increment-folder/reports/installed-3.1.13-20261026 | Test: grep -q "36 checks: 36 pass, 0 fail" .specweave/increments/1058-specweave-auto-commit-increment-folder/reports/installed-3.1.13-20261026/results.txt

### T-07 Verify and close 1058 after installed acceptance
- AC: - | Files: .specweave/increments/1058-specweave-auto-commit-increment-folder | Test: specweave verify 1058

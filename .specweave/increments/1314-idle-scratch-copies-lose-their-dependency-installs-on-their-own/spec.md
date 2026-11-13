# Idle scratch copies lose their dependency installs on their own

## Problem

On the M4, `~/.specwithcode` reached 173 GB (2026-11-12). Worktrees held 2.5 MB of it. About 30 copies of the app repository in `m4/scratch` held most of the rest, each about 6 GB by `du` with its `node_modules`. With worktrees off, threads build in a copy beside the busy shared checkout, and nothing removes the copy afterwards: the hourly clone sweep removes only clean, merged git clones, a source tree without `.git` is "reported only, never removed", and a clone with untracked notes or no origin is kept for good. `specweave-studio clones sweep` answered "0 of 68 would be removed". No rule told agents to clean up their copy either.

## Scope

In: the hourly clone sweep and `specweave-studio clones sweep` remove the dependency installs of a copy they leave in place once it sat unused for a day; docs, changelog and an agent rule to clean up one's own copy. Out: removing the copies themselves, changing the rule that an open thread keeps its worktree, a new setting or UI, build outputs other than `node_modules`.

## Acceptance Criteria

- [ ] AC-01: An idle source tree without `.git`, and a kept clone of a registered repository, lose their `node_modules` folders after a day unused, and every other file stays.
- [ ] AC-02: The installs stay when a thread, agent session, terminal or process uses the copy, when anything outside the installs changed within the day, when the folder is not a package manager's install, and when any of that cannot be read.
- [ ] AC-03: `specweave-studio clones sweep` lists the installs of each kept copy with the reason, and the released app on the M4 shows the same plan.
- [ ] AC-04: Agents are told to remove their scratch copy, or its installs, when its pull request merges.

## Approach

`apps/server/src/mergedCloneSweep.ts` gets `decideDependencyPrune` and `pruneDependencies`; `storageCleanup.ts` `cleanMergedClones` calls them for every decision it does not remove, under the existing `storageCleanup.removeMergedClones` setting; `cli/clones.ts` prints them. Idle is judged by the newer of mtime and ctime of everything outside the installs, so a copy made a minute ago from an archive with old file times is not idle. Removal is async so the server's event loop stays free. Rejected: turning on `scratchAfterDays` by default (it removes whole folders, some hold evidence), and removing merged worktrees of open threads (deliberate rule since the 2026-10-26 incident).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Reuse `removeMergedClones` rather than add a setting: one switch for the one sweep.
- D-02 A clone with no origin or another origin qualifies by `package.json` name, but only installs a package manager can write again go (lockfile, state file or links only).
- D-03 The open-thread worktree rule stays as it is.
### Open
- none

## Tasks

### T-01 Dependency prune in the clone sweep, the hourly hook and the CLI
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/mergedCloneSweep.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/mergedCloneSweep.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/storageCleanup.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/cli/clones.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/cli/clones.test.ts | Test: cd apps/server && npx vp test run src/mergedCloneSweep.test.ts src/cli/clones.test.ts

### T-02 Docs, changelog and the agent rule
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/docs/operations/merged-clones.md, repositories/anton-abyzov/specwithcode-dev/CHANGELOG.md, repositories/anton-abyzov/specwithcode-dev/AGENTS.md, AGENTS.md | Test: grep -q "scratch copy" AGENTS.md

### T-03 Review, merge, release and check the released app on the M4
- AC: AC-03 | Files: .specweave/increments/1314-idle-scratch-copies-lose-their-dependency-installs-on-their-own/spec.md | Test: specweave-studio clones sweep --base-dir ~/.specwithcode/m4 --no-pull-requests | grep -q "dependency install"

### T-04 Verify and close 1314
- AC: AC-01 | Files: .specweave/increments/1314-idle-scratch-copies-lose-their-dependency-installs-on-their-own/spec.md | Test: specweave verify

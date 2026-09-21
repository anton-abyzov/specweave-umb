---
increment: 0879-refresh-plugins-walks-the-filesystem-from-cwd-when-no-project-is-found
title: refresh-plugins walks the filesystem from cwd when no project is found
type: bug
priority: P1
status: completed
created: 2026-09-21T00:00:00.000Z
test_mode: TDD
coverage_target: 60
---

# 0879 — refresh-plugins walks the filesystem from cwd when no project is found

**Project**: specweave (repositories/anton-abyzov/specweave, branch develop, 2.2.2)

## Problem

`specweave refresh-plugins` run from `$HOME` (no `.specweave/` anywhere upward) pinned one
CPU core at 99% for 6+ minutes with no output; `lsof` showed the node process holding `/`
open for reading on three fds. Run from the specweave-umb umbrella root the same command
finishes in about 4 s (`+ sw: installed (v2.2.2)`).

Root cause (confirmed by reading the code and by an emulated walk):

1. `refreshPluginsCommand` resolves the project root with `getProjectRoot()`
   (`src/utils/find-project-root.ts`), which returns `process.cwd()` when no
   `.specweave/config.json` is found in the cwd or any parent.
2. Step 0.5 then calls `cleanupLegacyLockfiles(projectRoot)`
   (`src/utils/cleanup-stale-plugins.ts`), whose `walkForFile` recurses over the
   whole tree under that root, skipping only `node_modules`, `.git` and `.specweave`,
   with no depth bound, and uses `statSync`, so it follows symlinks.
   `$HOME` holds `Google Drive -> Library/CloudStorage/...` and
   `ftb-edit -> /Volumes/SanDisk ExF/...`; an emulated walk of `$HOME` had visited
   158k directories after 20 s without finishing, and a walk from a temp dir holding a
   single `escape -> /System/Library` symlink visited 240k directories outside the start
   dir in 15 s. The published 2.2.2 binary run from that temp dir takes 9.6 s (7.8 s
   system time) versus 0.37 s one level down.
3. The same walk also deletes any `skills-lock.json` it finds (older than 5 s), so
   from `$HOME` it could delete files outside any project.

Evidence that this has happened before: `$HOME/skills-lock.json` (2026-08-26) and
`$HOME/vskill.lock` (2026-09-01) exist, written by earlier runs that fell back to cwd.

`resolveEffectiveRoot` / `resolveSpecweaveRoot` are not involved: `resolveSpecweaveRoot`
walks up at most 8 levels from the installed package, and `resolveEffectiveRoot` is not
called by this command.

## Scope

**In**: bail out of `refresh-plugins` with a clear message when no project is found;
bound `walkForFile` (never follow symlinks, depth limit); same guard for the
doctor/update stale-lockfile check; unit tests for the no-project case, the symlink
escape and the depth bound; black-box proof from a temp dir and from the umbrella.

**Out**: changing `getProjectRoot()` semantics for its other callers; a user-scope
"install sw globally without a project" mode; cleaning up the stray `$HOME` lockfiles.

## Acceptance Criteria

- [x] AC-01 From a directory with no `.specweave/config.json` in it or any parent, `specweave refresh-plugins` exits 1 within 2 s, prints a message naming the cwd and `.specweave/config.json` and pointing at `specweave init`, and performs no directory scan, plugin install, migration or settings write. `--quiet` suppresses the output but keeps `failed: 1` and exit code 1.
- [x] AC-02 `cleanupLegacyLockfiles` never follows symlinks and stops descending at depth 6 by default (`maxDepth` option); unit tests cover a symlinked directory pointing outside the tree and a lockfile one level past the bound.
- [x] AC-03 Inside a project the command behaves as before: from the umbrella root `sw` is reported active/installed in a few seconds; all existing refresh-plugins and cleanup-stale-lockfiles unit tests pass.
- [x] AC-04 `InstallationHealthChecker.checkStaleLockfiles` (used by `specweave update` / `doctor`) skips the scan when `projectRoot` is not inside a SpecWeave project.

## Approach

- **Files that change**: `src/utils/cleanup-stale-plugins.ts` (lstat, `maxDepth`, `DEFAULT_MAX_WALK_DEPTH`), `src/cli/commands/refresh-plugins.ts` (`findProjectRoot()` + bail-out), `src/utils/find-project-root.ts` (doc note on `getProjectRoot`), `src/core/doctor/checkers/installation-health-checker.ts` (guard), tests under `tests/unit/`.
- **Key decisions**: bail out rather than scan the cwd tree — from `$HOME` the cwd tree is the problem itself; native `claude plugin install` is global anyway, and `specweave init` is the documented entry point. Depth 6 is generous: legacy `skills-lock.json` only lived at a project root or `repositories/<org>/<repo>/` (depth 3). `lstatSync` keeps the injected `customFs` test seam working (tests spread the real `fs`).
- **Rejected alternatives**: keep the cwd fallback and only bound the walk — `$HOME` walk is still 158k+ dirs; make `getProjectRoot()` throw — too many callers rely on the fallback for config reads.
- **Risks**: a hook or script that ran `refresh-plugins` outside a project now gets exit 1 — no in-repo hook does (`plugins/specweave/hooks` has no such call; `update` runs from the project dir).

## Open questions

- None blocking.

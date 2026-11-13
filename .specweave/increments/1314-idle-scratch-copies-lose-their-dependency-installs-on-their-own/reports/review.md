# Review: 1314 idle scratch copies lose their dependency installs (PR 280, 936300a7)

- Reviewer model: Claude Sonnet 5.5 (fresh context, read-only)
- Subject: `anton-abyzov/specwithcode` PR 280, merged as `936300a7`, shipped in 1.0.270
- Verdict: **SHIP**. No Blocker and no Major. Six Minor findings, none loses a file that `pnpm install` cannot write again.

Line numbers are `apps/server/src/mergedCloneSweep.ts` at `936300a7` unless a path is given.

## Acceptance criteria

| AC | Result | Where |
| --- | --- | --- |
| AC-01 source tree without `.git` and kept clone lose `node_modules`, every other file stays | Met | `decideDependencyPrune` 690-771 runs for every non-`remove` decision (`storageCleanup.ts:1096-1114`, `cli/clones.ts:263-270`); `pruneDependencies` 786-817 removes only paths named `node_modules` |
| AC-02 installs stay when used, recently changed, not a package manager's install, or unreadable | Met, with the Minor gaps below | owners 729-739, cwd 741, open files 743, state files 752-761, tree age 762-764 (`changedAfter` 637-673), install shape 571-585 |
| AC-03 CLI lists installs with the reason; released app shows the same plan | Met in code (`cli/clones.ts` `dependencyLine`); evidence is thin (F-6) | |
| AC-04 agents told to clean up their scratch copy | Met | `AGENTS.md` focused-checks bullet in the PR diff |

## Findings

### Minor

**F-1. The "file open in it" check is top-level only, and the cwd check only sees processes inside the copy.**
`hasOpenFilesIn` runs `lsof +d` (line 302), which lists only entries directly in the folder, not `+D` recursive. `decideDependencyPrune` relies on it at 743-745 plus `processCwds` at 741. A process whose cwd is above the copy (a shell in the dated folder running `vite --root app`, or `node app/node_modules/.bin/...`) and that holds files deep in `node_modules` or `src` is not seen. A live thread or terminal in the dated folder is pinned (729-738), so this needs an external process. Result is a broken dev server after 24 h of no file changes, fixed by `pnpm install`. The doc table says "no file open in it", which overstates this.

**F-2. A source tree without `.git` skips the "tracked file" guard.**
The `git ls-files` check at 579-582 runs only when `kind === "clone"`. In an export, a force-added fixture `node_modules` that carries `.package-lock.json`/`.modules.yaml`, or holds only symlinks (`onlyLinks`, 615-629), would be deleted although it is source. Verified exposure in this repo: `.repos/alchemy-effect/.../test/fixtures/*/node_modules` is tracked, and it is protected only by two accidents, the hidden-folder skip at 566 (`.repos` is never entered) and `onlyLinks` rejecting real folders at 619-623. Another repository with such fixtures under a non-hidden folder is not protected.

**F-3. Lockfile is checked at the copy root only, but each nested install is accepted on its own state file.**
Line 574 requires a root lockfile; line 578 then accepts any `node_modules` with `.package-lock.json`, which every npm 7+ install writes. A nested npm project with its own `package.json` and no lockfile of its own (a docs or tools folder) loses its `node_modules` when the root has a `pnpm-lock.yaml`. Reinstall works but resolves new versions. The doc says "the copy has a lockfile", which matches the code, so this is intended, but it is weaker than "can write again".

**F-4. A cross-copy symlink into an idle install is not detected.**
Nothing checks whether another live copy links into this one's `node_modules` (a pattern `AGENTS.md` forbids but threads have used). The idle copy's install goes and the in-use copy breaks. Reinstall fixes it.

**F-5. Two short race windows between the idle check and the removal.**
Owners, processes and open files are read (729-745) before the walk of up to 200,000 entries (762). `pruneDependencies` decides again (790) and then removes each install in a loop (800-808) without a recheck between installs. A `rm` of several gigabytes takes seconds, and a thread or process that starts in that time is not noticed. Window is small, the copy has been idle for 24 h, and the damage is a reinstall.

**F-6. Test and evidence gaps.**
- The listed tests (`mergedCloneSweep.test.ts` in the PR diff) cover process list `null`, lsof `null`, recent state file, hand-made `node_modules`, symlinked `node_modules`, linked worktree. None covers an unreadable folder inside the tree (`changedAfter` 666-669) or the 200,000-entry limit (652), both named in AC-02 ("cannot be read").
- `reports/task-T-03.txt` shows `specweave-studio clones sweep ... | grep -q "dependency install"` exiting 0 with an `EPIPE` stack trace (grep closed the pipe on first match). It proves the phrase appears once; it does not show which copies would be pruned, or the same plan as the app.
- All four ACs are still `[ ]` in `spec.md`.

## What I checked and found safe

- **Removal target.** Only paths from `findDependencyInstalls` whose basename is `node_modules`, that are real folders, whose `realpath` equals themselves and that are inside the real copy (801-806). `fs.rm` unlinks symlinks inside without following them, so pnpm store links and `link:` targets are untouched.
- **Symlinks and traversal.** `findDependencyInstalls` skips symlinked directories and hidden folders (562-566); `findClones` never enters symlinks (184) and starts from a realpath'd root; `pruneDependencies` re-checks `tree === realpath(tree)`, `tree !== root` and `pathInside(root, tree)` (796-799). A symlinked `node_modules` is not an install.
- **Not a package manager's install.** Needs `package.json` beside it (565), a root lockfile (574) and a state file or links-only content (578). Hand-made folders are left. An unreadable lockfile check or state file means "not an install" (`existsSync`/`lstat` errors are false, 601-606).
- **Recent change.** Newest of mtime and ctime over everything outside installs (`changedAt`, `scratchPrune.ts:63`), so an archive extracted or `cp`'d with old file times counts as new. Hidden folders and `.git` are walked, only `node_modules` and `.git/objects` are opaque, and their own folder time still counts (664). Future-dated entries read as "changed". Install state files are checked separately (752-761).
- **Unreadable.** Any `lstat` or `readdir` error, a non-finite time, more than 200,000 entries, `processCwds === null` (Windows, lsof failure) or lsof `null` keeps the installs (652-669, 740, 744). In `findDependencyInstalls` an unreadable folder is skipped, but `changedAfter` then hits it and returns `unknown`.
- **In use.** Projects, non-archived threads, live sessions, project checkouts and, in the service, live terminals pin the copy, a folder inside it and a dated folder around it below the scan root, but not the scan root or above (729-738). The CLI context has no live terminals (`cli/clones.ts:230`), which the process cwd check covers on macOS and Linux and `null` covers on Windows.
- **Clones.** A clone with a registered origin passed the `.git`-is-a-folder check in `decideClone`; one with another or no origin must also have `.git` as a folder and a registered `package.json` name (696-713). Tracked files in a `node_modules` keep it (579-582). Unpushed commits, stashes and dirty trees are not touched since only `node_modules` goes.
- **Setting.** The same `removeMergedClones` switch is read again before pruning (`storageCleanup.ts:1105`), and the context is rebuilt right before (1106).
- **Event loop.** Walk and removal use `fs.promises`; only a few cheap `lstatSync`/`existsSync` calls are synchronous.

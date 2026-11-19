# Board shows each increment's current state and a not-done count

## Problem

Anton, November 19, 2026: "Make sure we always represent the current state of increment and give the number of increments that are not in the done state." He asked why the Board shows increments as Planned and not started when their work is merged.

The Board reads only the project folder (`apps/server/src/project/ProjectBoard.ts`, `incrementRootFor(workspaceRoot, null)`). With Use worktrees on, threads write `spec.md` and `ledger.jsonl` in their own worktrees and merge to the default branch. Nothing brings the project folder current, so its copy is often the oldest one.

Measured on the M4 on November 19, 2026 (`~/.specwithcode/m4/scratch/2026-11-19-increment-audit/state.json`, 784 increments, project folder 61 commits behind `origin/main` with 215 uncommitted paths, 45 thread worktrees):

- 5 increments are closed on `origin/main` or in a worktree but still open in the project folder: 1369, 1371, 1374, 1386, 1403.
- 20 increments are missing from the project folder: 9 open (1351, 1356, 1379, 1382, 1385, 1406, 1408, 1416, 1420) and 11 closed.
- 8 open increments have a newer copy outside the project folder: 1269, 1320, 1347, 1348, 1368, 1380, 1407, 1414.
- 2 project-folder stubs (a `metadata.json` with `status: planned`, no title, no spec) hide a copy with a spec: 1374 and 1407. 1407 has 7 of 7 tasks done on `origin/main` and reads Planned on the Board.
- For 28 open increments the newest copy is the project folder's own uncommitted or branch-only state (1387, 1398, 1344, 1383), so reading the default branch instead would be wrong too.

The Board also has no single number for the work that is left.

## Scope

In:
- the Board card and the increment view read each increment from its newest copy among the project folder, the linked worktrees Git registered for the project folder's repository, and the remote's default branch as last fetched;
- a few words on the card and in the view when the copy shown is not the project folder's;
- a not-done count in the Board header;
- one line when the project folder is behind its default branch.

Out:
- fetching, pulling, switching or writing in the project folder or any worktree (the Board only reads);
- other readers of the project folder's increments (thread plan cards, the increment picker, the project plan);
- the stale SpecWeave installs that stamp `testMode` and `coverageTarget` (the coordinator owns them) and the `metadata.json` stubs `MetadataManager.read` creates (recorded below).

## Acceptance Criteria

- [ ] AC-01: For each increment folder name the Board lists one card, built from one whole copy. Copies are ranked by this rule, first difference wins: (1) more recorded reopens (`metadata.reopened`); (2) closed (completed, or dropped) before open; (3) the longer ledger in bytes, since the ledger is append-only; (4) the later metadata time; (5) the project folder, then the remote branch, then worktrees by path. Two closed copies are not compared further: the project folder's is kept. A copy with a `spec.md` is taken before any copy without one, so a stub never hides a spec. Files are never mixed across copies, except that review records and reports in the project folder's copy are still listed.
- [ ] AC-02: The copies read are: the project folder; every linked worktree Git registered for its repository that has `.specweave/increments`; and the branch `refs/remotes/origin/HEAD` names (else `origin/main`, else `origin/master`) as last fetched, read from Git objects. Nothing is fetched, and no checkout is switched, written or locked. A project folder that is not the top of a Git checkout, has no remote branch, or whose Git read fails or times out still answers from the folders it can read.
- [ ] AC-03: The 1407 shape (project folder: only a `metadata.json` stub and `reports/`; remote branch: spec, 20-event ledger, 7 of 7 tasks, `active`) shows the remote copy's title, tasks and column, with the project folder's review records. The 1374 shape (stub against a closed copy) is counted as done. An increment that exists only in a worktree, or only on the remote branch, has a card. An increment whose project-folder copy has the longer ledger keeps that copy. An increment dropped in the project folder or on the remote branch, or in a worktree while it is open in both, stays off the board (D-02). An increment reopened on the remote branch shows open against a stale closed project-folder copy.
- [ ] AC-04: A card whose copy is not the project folder's carries `source` (`worktree` with the worktree's folder name, or `remote` with the branch name). The card and the increment view say it in a few words ("From worktree {name}", "From {branch}"), and the view adds when that branch was last fetched. The spec and reports of such a card open (a remote copy from a read-only cache outside the repository). Older servers send no `source` and nothing changes for them.
- [ ] AC-05: The Board header always shows how many increments are not done ("{count} not done": Planned plus Active plus In review), next to the column counts. It is the whole project's number, also while a search narrows the columns. With an older server it is the sum of the column counts.
- [ ] AC-06: When the project folder's checked-out commit is behind the remote default branch as last fetched, the Board shows one line with the count ("Project folder is {count} commits behind {branch}"). No line when it is level, ahead only, or unknown.
- [ ] AC-07: `ProjectBoard.test.ts` keeps "1,500 increments in under a second" for the project folder alone, and a second case holds the same bound with worktrees and a remote branch in play. Unchanged copies cost stats, not reads: a Git process runs only when the remote branch's commit changes, closed increments are not looked up in worktrees, and worktree folder listings are read again only when the folder changes.
- [ ] AC-08: A card's "last change" time is the copy's last ledger event or metadata time, not a file's modification time, so a fresh checkout does not make stale copies look new.
- [x] AC-09: A cross-family review says ship at the PR head. The PR is green and merged with a merge commit. The change is released, and headless screenshots of the Board before and after show the count and a card from another copy.

## Approach

- Contracts (`packages/contracts/src/projectBoard.ts`): optional `source` on `ProjectBoardCard`; optional `notDone` and `behind` (`{ ref, count, fetchedAt }`) on `ProjectBoardResult`; optional `source` detail on the increment view through its card.
- Server, new `apps/server/src/project/IncrementCopies.ts`: the three kinds of copy and the rank.
  - Worktrees: `registeredCheckouts([root])` (Git's own files, no process), minus the root, kept when they hold `.specweave/increments`. Each folder listing is cached by the folder's mtime.
  - Remote branch: the commit is resolved from files (`refs/remotes/origin/HEAD`, loose ref, `packed-refs`), with one `git rev-parse` as the fallback. Per commit: one `git ls-tree -r -l` under `.specweave/increments` and one `git cat-file --batch` for the `metadata.json` blobs, both cached (blobs by object id). Git runs with inherited `GIT_*` variables removed, `GIT_OPTIONAL_LOCKS=0`, no prompts and a 3-second budget.
  - A remote copy that wins is written once to `<state>/board-copies/<repository>/<content key>/.specweave/increments/<id>/` (plus the branch's `.specweave/config.json`), read-only, keyed by its blob ids, and removed when the branch no longer holds that content. Every existing reader (card detail, reviews, the increment view, the file viewer) then works on a real folder. Size and count bounds, plain path segments only, no links.
  - Pruning: an increment closed in the project folder or on the remote branch is settled between those two. Only the rest, and increments found only in worktrees, are looked up in worktrees (two stats per copy).
- Server, `ProjectBoard.ts`: `readProjectBoard` takes the copies, builds each card from the winning root, sets `source`, `notDone` and `behind`. `updatedAt` uses the ledger's last event time. `readBoardCard` takes the resolved copy.
- Server, `ProjectBoardIncrement.ts`: resolves the same copy for one increment, merges the project folder's reports into the list.
- Server, `ThreadIncrementProgressService.ts`: passes the state folder for the cache.
- Web: `BoardCard.tsx` and `BoardIncrementView.tsx` show the source words; `BoardPane.tsx` shows the not-done count and the behind line; `boardIncrementModel.ts` never offers "Plan it" for a card that has a source and a spec; phrases in all catalogs; the `project-board` fixture gets a sourced card.
- Rejected: reading only the default branch (wrong for 28 increments); running `git status` or a diff per worktree (a process per worktree per read); reading remote copies in memory through every reader (three readers and the file viewer are bound to folders).
- Risks: stats over many worktrees on each 30-second refresh (measured 9,450 stats in 145 ms on the M4 before pruning); ledger length is not a total order for ledgers that diverged in two worktrees.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: "Newest" is the rank in AC-01. Closed wins over a longer open ledger, because the complaint is merged work shown as open; a reopen is seen through `metadata.reopened`.
- D-02: Worktrees are not read for an increment the project folder or the remote branch already shows closed with a spec, for speed. A reopen or a drop made only in a worktree of such an increment shows once it reaches the project folder or the remote branch. A closed stub with no spec is always compared with the worktrees.
- D-03: Ledger length in bytes stands in for the event count, so comparing copies needs no ledger read.
- D-04: A remote copy is shown from a cache folder under the app's state folder, so its spec opens; edits there are not kept, and the source words say where it comes from.
- D-05: All linked worktrees of the repository count, also those of archived threads: the rule is about copies, not about who made them.
### Open
- none

## Known limits

- Found, not fixed here: two stale SpecWeave installs on the M4 (`/opt/homebrew/lib/node_modules/specweave` 3.1.4 and the Node 20.20.2 one, 3.0.14) stamp `testMode` and `coverageTarget` on any metadata read; 3.1.10 removed that. The coordinator owns them.
- Found, not fixed here: `MetadataManager.read` in SpecWeave creates a default `metadata.json` (`status: planned`, no title) in any increment folder that has none, also one that holds only `reports/`. Proposed fix: do not persist the default when `spec.md` is missing.
- Found: an umbrella launch with Use worktrees on and no `repositories` gives an empty folder with no Git; only `repositories: ["."]` works. An app-only thread cannot add the umbrella with `studio_worktree_add_repository`.
- The remote branch is as last fetched; the Board never fetches.
- The remote branch is found from Git's files (loose refs, `packed-refs`); `git rev-parse` answers, for `origin/HEAD`, then `origin/main`, then `origin/master`, only when `origin/HEAD` exists in a form the files do not resolve or the refs are kept in reftable; that answer is kept for 30 seconds. In a reftable repository the project folder's own commit is not read, so the Board shows no "behind" line there.
- Cached remote copies the branch no longer holds are removed once unused for 10 minutes. A copy removed under a reader that still holds the older branch is written again on that reader's next read.
- A project whose planning root is not the top of a Git checkout reads only its folders.

## Review

- Reviewer: openai (gpt-6.1-sol)
- Why not Muse: Muse Code stood at 99% of its usage until November 23, 2026 (`orchestrator_capabilities`, November 19). Anton's standing rule of November 18, 2026: "whenever Muse and Codex are both out, Copilot Enterprise with GPT-6.1 Sol, and no more asking."
- Depth: deep
- Required: yes

## Tasks

### T-01 Contracts: source, not-done count and behind line
- AC: AC-04, AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/projectBoard.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/project/ProjectBoard.test.ts

### T-02 Server: copies, rank, remote branch read and the Board
- AC: AC-01, AC-02, AC-03, AC-07, AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/project/IncrementCopies.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/IncrementCopies.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/incrementCopies.testkit.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectBoard.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectBoard.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ThreadIncrementProgressService.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/project/IncrementCopies.test.ts apps/server/src/project/ProjectBoard.test.ts

### T-03 Server: the increment view reads the same copy
- AC: AC-01, AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectBoardIncrement.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectBoardIncrement.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/project/ProjectBoardIncrement.test.ts

### T-04 Web: source words, not-done count, behind line
- AC: AC-04, AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/BoardPane.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/BoardCard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/BoardIncrementView.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectBoardModel.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/boardIncrementModel.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases, repositories/anton-abyzov/specwithcode/apps/web/tests/project-board | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/studio/shell/BoardPane.test.tsx src/components/studio/shell/BoardIncrementView.test.tsx src/studio/projectBoardModel.test.ts src/studio/boardIncrementModel.test.ts

### T-05 Review, merge, release and the headless screenshots
- AC: AC-09 | Files: none | Test: gh pr view 667 --repo anton-abyzov/specwithcode --json state --jq .state | grep -q MERGED && cd repositories/anton-abyzov/specwithcode && bash scripts/release/request-release.sh --released d006c3b3cac27b9eca191f249c22b40b4e4e3d17

# M4 slowness follow-ups: installed-app measurements and the 1307 gaps

## Problem

1305 shipped its core in PR 179 (`bf574d7837`, v1.0.246): the search indexer loop, trace volume, idle provider sessions, the two slow queries, idle renderer work, the heavy-check gate and the merged-clone sweep. Two pieces were left open and are moved here by the owner's decision of November 24, 2026 ("do recommended, yes! fixed"):

- 1305 T-08: before and after measurements on the installed M4 app for 1305 AC-01, AC-03, AC-04, AC-05, AC-06 and AC-07 were never taken on a quiet machine. The one reading on 1.0.247 under load showed server and window CPU at 46-56% and 43-44% of a core and 2 slow statements in 4.5 minutes.
- 1305 T-11: the gaps that 1307 listed (1307 was abandoned on November 19, 2026 and folded into 1305 T-11).

1305's own text for T-11, kept as written:

Folded in from 1307 (abandoned November 19, 2026, Anton approved). 1307's text follows.

PR 179 (merged as `bf574d7837`) stopped the search indexer loop but left gaps the owner asked for or the ship reviews found. Reviews: `reports/review-a6481cb285.md` and `review-255db411cb.md`.

1. The index still reads every file of an un-ignored `scratch/`, `.artifacts/` or nested clone on each rescan. fff 0.9.4 and 0.11.0 have no exclude option. On November 11, 2026 one such clone had 291,461 files.
2. Linux keeps fff's own watcher, so the git-status loop remains there.
3. The window makes about 2 `GET /api/studio/fleet/remote-workers` requests a second, each taking 1-3 s.
4. `providerSessionIdleMinutes` and `storageCleanup.removeMergedClones` have no Settings row.
5. Heavy-check gate: the shared verification copy can move between `checks copy` and `checks run`; a holder recorded under another hostname is never taken over; PID reuse is not detected on Windows.
6. Clone sweep: removes ignored files with a clone; scans tmp folders other homes share; archived threads do not protect a clone; removes nothing on Windows.
7. A `fs.watch` error leaves an index without refresh until its idle TTL.
8. Installed on the M4 (1.0.247, under load), the thread list still logged 2 slow statements in 4.5 minutes, and server and window CPU were 46-56% and 43-44% of a core. Readings on a quiet machine are owed (T-08).
9. The update page proof refuses every auto-vacuum database, so the M4 takes the full read (about 175 s) on every update; with an additive migration the refusal reads `schema` instead of `auto-vacuum`.

Done when (1307's AC-01 to AC-07):

- With an un-ignored 100,000-file clone under `<root>/scratch/`, a rescan of the root opens no file inside it.
- On Linux, 200 file changes in 1 s cause at most one rescan and no fff thread stays busy while idle.
- An idle window makes at most one remote-workers request every 10 s.
- Both settings can be changed in Settings on the machine they apply to.
- `checks run --expect-ref <commit>` refuses when the copy is on another commit; a dead holder is taken over after a hostname change; Windows detects PID reuse or refuses the lock with a clear message.
- The sweep keeps a clone holding ignored files outside dependency and build folders, scans tmp folders only when asked, and its docs state what happens to archived threads' clones and on Windows.
- After a watch error the index refreshes again on the next change.

Open decision (1307 D-01, same as D-06): how to keep the walk out of un-ignored folders: host fff in a child process with a private global ignore file, an upstream exclude option, or an in-tree `.ignore`.

## Scope

In: measurements on the installed M4 app against 1305's numbers, and the nine 1307 gaps above. Out: anything 1305 already delivered and verified.

## Acceptance Criteria

- [ ] AC-01: `reports/measurements.md` records, on the installed M4 app on a quiet machine, the readings for 1305 AC-01 (server CPU and fff samples), AC-03 (idle window CPU), AC-04 (idle trace MB per minute), AC-05 (idle Claude CLI children older than 20 minutes), AC-06 (slow-statement warnings over 30 minutes) and AC-07 (load average with three suites requested), each beside 1305's target, with the app version, date and the command used.
- [ ] AC-02: With an un-ignored 100,000-file clone under `<root>/scratch/`, a rescan of the root opens no file inside it (1307 AC-01).
- [ ] AC-03: On Linux, 200 file changes in 1 s cause at most one rescan and no fff thread stays busy while idle (1307 AC-02).
- [ ] AC-04: An idle window makes at most one remote-workers request every 10 s (1307 AC-03).
- [ ] AC-05: `providerSessionIdleMinutes` and `storageCleanup.removeMergedClones` can be changed in Settings on the machine they apply to (1307 AC-04).
- [ ] AC-06: `checks run --expect-ref <commit>` refuses when the copy is on another commit; a dead holder is taken over after a hostname change; Windows detects PID reuse or refuses the lock with a clear message (1307 AC-05).
- [ ] AC-07: The sweep keeps a clone holding ignored files outside dependency and build folders, scans tmp folders only when asked, and its docs state what happens to archived threads' clones and on Windows (1307 AC-06).
- [ ] AC-08: After a watch error the index refreshes again on the next change, and the update page proof no longer forces the full read on an auto-vacuum database with an additive migration (1307 AC-07 and gap 9).

## Approach

Measurements first (T-01), so the code work in T-02 targets what still misses on the installed app. T-02 starts with the open decision D-01. Heavy suites run only through `specweave-studio checks run` in a `specweave-studio checks copy` of the app.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- none
### Open
- D-01: how to keep the index walk out of un-ignored folders: host fff in a child process with a private global ignore file, an upstream exclude option, or an in-tree `.ignore` (carried from 1307 D-01 and 1305 D-06).

## Tasks

### T-01 Measure the installed app on the M4 (from 1305 T-08)
- AC: AC-01 | Files: .specweave/increments/1470-m4-slowness-follow-ups-installed-app-measurements-and-1307-gaps/reports/measurements.md | Test: test -s .specweave/increments/1470-m4-slowness-follow-ups-installed-app-measurements-and-1307-gaps/reports/measurements.md

### T-02 Search index walk exclusion and the 1307 follow-ups (from 1305 T-11)
- AC: AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/workspace/WorkspaceSearchIndex.ts, repositories/anton-abyzov/specwithcode/apps/server/src/workspace/WorkspaceSearchIndex.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/workspace/WorkspaceSearchRefresh.ts, repositories/anton-abyzov/specwithcode/apps/server/src/workspace/WorkspaceSearchRefresh.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src, repositories/anton-abyzov/specwithcode/packages/contracts/src/settings.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cli/checks.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cli/checks.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cli/heavyCheckLock.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cli/heavyCheckLock.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mergedCloneSweep.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mergedCloneSweep.test.ts, repositories/anton-abyzov/specwithcode/docs/operations/merged-clones.md, repositories/anton-abyzov/specwithcode/apps/server/src/serviceUpdate/ServiceUpdatePreparation.ts, repositories/anton-abyzov/specwithcode/apps/server/src/serviceUpdate/ServiceUpdatePreparation.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/workspace src/cli/checks.test.ts src/cli/heavyCheckLock.test.ts src/mergedCloneSweep.test.ts src/serviceUpdate/ServiceUpdatePreparation.test.ts

### T-03 Verify and close 1470
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08 | Files: .specweave/increments/1470-m4-slowness-follow-ups-installed-app-measurements-and-1307-gaps/spec.md | Test: specweave verify 1470-m4-slowness-follow-ups-installed-app-measurements-and-1307-gaps

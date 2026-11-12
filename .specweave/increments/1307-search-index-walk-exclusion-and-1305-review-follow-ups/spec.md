# Search index walk exclusion and 1305 review follow-ups

## Problem

Increment 1305 (PR 179, merged as `bf574d7837`) stopped the search indexer loop but left gaps the owner asked for or the ship reviews found. Reviews: `.specweave/increments/1305-m4-slowness-app-side-fixes-indexer-loop-window-cpu-trace-volume-idle-clis-slow-queries-check-gate-clone-cleanup/reports/review-a6481cb285.md` and `review-255db411cb.md`.

1. The index still reads every file of an un-ignored `scratch/`, `.artifacts/` or nested clone on each rescan. fff 0.9.4 and 0.11.0 have no exclude option. On November 11, 2026 one such clone had 291,461 files.
2. Linux keeps fff's own watcher, so the git-status loop remains there.
3. The window makes about 2 `GET /api/studio/fleet/remote-workers` requests a second, each taking 1-3 s.
4. `providerSessionIdleMinutes` and `storageCleanup.removeMergedClones` have no Settings row.
5. Heavy-check gate: the shared verification copy can move between `checks copy` and `checks run`; a holder recorded under another hostname is never taken over; PID reuse is not detected on Windows.
6. Clone sweep: removes ignored files with a clone; scans tmp folders other homes share; archived threads do not protect a clone; removes nothing on Windows.
7. A `fs.watch` error leaves an index without refresh until its idle TTL.

## Scope

In: the seven items above. Out: anything 1305 delivered.

## Acceptance Criteria

- [ ] AC-01: With an un-ignored 100,000-file clone under `<root>/scratch/`, a rescan of the root opens no file inside it.
- [ ] AC-02: On Linux, 200 file changes in 1 s cause at most one rescan and no fff thread stays busy while idle.
- [ ] AC-03: An idle window makes at most one remote-workers request every 10 s.
- [ ] AC-04: Both settings can be changed in Settings on the machine they apply to.
- [ ] AC-05: `checks run --expect-ref <commit>` refuses when the copy is on another commit; a dead holder is taken over after a hostname change; Windows detects PID reuse or refuses the lock with a clear message.
- [ ] AC-06: The sweep keeps a clone holding ignored files outside dependency and build folders, scans tmp folders only when asked, and its docs state what happens to archived threads' clones and on Windows.
- [ ] AC-07: After a watch error the index refreshes again on the next change.

## Approach

To be planned when this is picked up. For AC-01 the candidates are hosting fff in a child process with a private global ignore file, an upstream exclude option, or an in-tree `.ignore`; each needs a decision first (1305 D-06).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- none
### Open
- D-01 How to keep the walk out of un-ignored folders (see Approach).

## Tasks

### T-01 Plan the approach and split tasks
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07 | Files: .specweave/increments/1307-search-index-walk-exclusion-and-1305-review-follow-ups/spec.md | Test: test -s .specweave/increments/1307-search-index-walk-exclusion-and-1305-review-follow-ups/spec.md

### T-02 Verify and close 1307
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07 | Files: .specweave/increments/1307-search-index-walk-exclusion-and-1305-review-follow-ups/reports/close.md | Test: test -s .specweave/increments/1307-search-index-walk-exclusion-and-1305-review-follow-ups/reports/close.md

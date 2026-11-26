# 1491 Fleet update scripts read the database on Apple SQLite 3.54.0

## Problem

The app's update scripts in `scripts/studio-fleet` run under `/usr/bin/python3` (`ManagedUpdatesService.ts`, `fleetUpdate.ts`, `fleetDiskRoom.ts`, `studioServiceUpdates.ts`). On macOS 27 that Python carries Apple's SQLite 3.54.0, which behaves differently from stock SQLite 3.53.1 in two ways (measured on M5, November 26, 2026):

- A `mode=ro` open of a WAL-mode database whose `-shm` and `-wal` are both gone fails with "unable to open database file". A stopped service leaves its database in exactly that state, because Node's bundled SQLite removes both files on its last close. Stock SQLite opens it instead, and as a side effect creates `-shm` and `-wal`. So `live_database.connect`, which all 18 update modules use to read a database another process may hold, cannot read a stopped service's database on such a Mac.
- Apple's build keeps `-wal` and `-shm` after a read-write connection closes. Fixture databases written with it look like databases some process still has open.

Six fleet test files fail on `/usr/bin/python3` there (`test-page-continuity.py`, `test-preflight-disk.py`, `test-protected-tables-after-restart.py`, `test-rehearse-update.py`, `test-room-before-stop.py`, `test-update-admission.py`), and they fail the same way on main before any change. Four of them also passed on 3.53.1 only because of that side effect: an earlier "read-only" open had created `-shm`.

## Scope

In:
- `live_database.connect` reads a stopped WAL database on Apple's SQLite.
- Fixtures that model a stopped or a running service the way the service leaves its files.
- The six failing test files.

Out:
- Changing which Python the app runs.
- Stock SQLite's side files on a plain `mode=ro` open (unchanged).
- CI's macOS image.

## Acceptance Criteria

- [ ] AC-01: On `/usr/bin/python3` with Apple's SQLite 3.54.0, `live_database.connect` reads a WAL database whose service has closed it (only the main file on disk), and the connection refuses writes. The reader holds SQLite's WAL read locks, so a service that starts during the read cannot checkpoint over the pages it uses. A database with `-shm` on disk never takes that fallback, and one that a process holds without its `-wal` and `-shm` is refused.
- [ ] AC-02: The fleet suite (`scripts/studio-fleet/run-tests.sh`) passes on `/usr/bin/python3` (SQLite 3.54.0) and on a stock-SQLite Python 3.12 (3.53.1), including the six files above, in the gated checks copy with the server built.

## Approach

`live_database.connect` keeps its URI choice: `mode=ro&readonly_shm=1` when `-shm` exists, otherwise `mode=ro`. If that open fails with "unable to open database file" and neither `-shm` nor `-wal` exists, and no process holds a SHARED lock on the main file, it creates `-shm` and `-wal` empty (`O_CREAT|O_EXCL|O_NOFOLLOW`), which is what stock SQLite's first reader does. Just before the open it checks the new `-shm` is still empty: if so it opens plain `mode=ro`, and if another process has initialised it meanwhile it opens `mode=ro&readonly_shm=1` as for any shared index. The reader then takes SQLite's locks like any other connection. If a process does hold the file without its side files, the open is refused. The open is forced, with a schema read, inside a helper, so a lazy open cannot fail later at the caller.

A test support module, `scripts/studio-fleet/sqlite_fixture.py`, provides:
- `close(db)` ends a fixture's connection the way the service does: checkpoint, close, then remove `-wal` and `-shm`.
- `RunningService(path)` holds the database open in a child process, as the running service does, and makes writes from there. In-process writers share SQLite's per-file state with the test's readers and lock probes.

Fixtures that model a running service (the pre-stop room check, the admission read with a write during it) use `RunningService`. Fixtures that model a stopped service use `close`. `test-page-continuity.py` reads through `live_database.connect`, as production does, instead of a plain `mode=ro` URI.

Rejected:
- `mode=ro&immutable=1` (round 1 of review, GPT-6 Sol): it reads without locks. A service that starts mid-read checkpoints over the main file under it, which was measured on 3.54.0.
- Creating `-shm` and then opening with `readonly_shm=1`: a reader alone on an uninitialised `-shm` locks a starting service out ("database is locked"). Plain `mode=ro` on the created files does not; a writer that starts mid-read commits and checkpoints normally.
- A read-write connection with `query_only`: it can checkpoint and delete `-wal` at close, the hazard `live_database` exists to prevent.

Risk: a process that lost both its locks and its side files looks like no process at all, to this check as to stock SQLite. The empty side files stay behind after the read, as stock SQLite leaves them.

## Decisions

### Asked

- none (the user asked for the fix, done as recommended)

### Defaulted

- D-01 The fallback triggers only on "unable to open database file" with no `-shm` and no `-wal`. Stock SQLite keeps its current path (low blast radius).
- D-02 The fixtures change to match the service, not the assertions. Assertions that encode service behaviour stay as they are.
- D-03 The fallback leaves empty `-wal` and `-shm`, matching stock SQLite's reader (reversible).

### Open

- none

## Tasks

### T-01 Read a stopped database on Apple's SQLite, fixtures that match the service

- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/scripts/studio-fleet/live_database.py, repositories/anton-abyzov/specwithcode/scripts/studio-fleet/sqlite_fixture.py, repositories/anton-abyzov/specwithcode/scripts/studio-fleet/test-live-database.py, repositories/anton-abyzov/specwithcode/scripts/studio-fleet/test-page-continuity.py, repositories/anton-abyzov/specwithcode/scripts/studio-fleet/test-protected-tables-after-restart.py, repositories/anton-abyzov/specwithcode/scripts/studio-fleet/test-rehearse-update.py, repositories/anton-abyzov/specwithcode/scripts/studio-fleet/test-preflight-disk.py, repositories/anton-abyzov/specwithcode/scripts/studio-fleet/test-room-before-stop.py, repositories/anton-abyzov/specwithcode/scripts/studio-fleet/test-update-admission.py | Test: cd repositories/anton-abyzov/specwithcode/scripts/studio-fleet && /usr/bin/python3 -B test-live-database.py && /usr/bin/python3 -B test-update-admission.py

### T-02 Full fleet suite on both SQLite builds in the gated copy

- AC: AC-02 | Files: .specweave/increments/1491-fleet-update-scripts-read-the-database-on-apple-sqlite-3540/reports/fleet-both-sqlite.md | Test: grep -q "both builds pass" .specweave/increments/1491-fleet-update-scripts-read-the-database-on-apple-sqlite-3540/reports/fleet-both-sqlite.md

Verify and close 1491.

# Percy join safety copy holds only Percy's rows

## Problem

Before a Percy join links, each machine saves a database copy as a safety net (1448 AC-13; `ensureSeriesCopies` in `apps/server/src/project/personalShareLink.ts`, and the approved-plan link in `PersonalLinkService.ts`). Since 1499 that copy is the whole database. On m4 that is 18.8 GiB of free space on every join series, although a join changes only Percy's own rows and Undo restores from the much smaller `.percy.json` restore point (`personalRestorePoint.ts`). The owner chose the recommended option on November 27, 2026: the safety copy holds only the Percy project's rows (decision recorded in project memory `project_percy_join_database_copy.md`).

Also, a manual `db snapshot` and a Percy copy that target the same absent file can both pass the existence check. The second `renameSync` then silently replaces the first finished copy (`apps/server/src/persistence/liveDatabaseSnapshot.ts`).

## Scope

In: a scoped copy of one project's rows, used by both Percy copy callers; publishing every snapshot without replacing an existing file; tests. Out: Undo and restore points (unchanged); `db snapshot` stays a whole-database copy.

## Acceptance Criteria

- [ ] AC-01: The Percy safety copy is a SQLite file that holds, for every table of the live database with a `project_id` column, that table's schema and only the rows whose `project_id` is the Percy project's id, read in one consistent read transaction through `openLiveDatabaseReadOnly`. No other project's rows and no table without `project_id` are in it. It records which project and when.
- [ ] AC-02: Both Percy copy callers (`ensureSeriesCopies` and the approved-plan link in `PersonalLinkService.ts`) save the scoped copy. The 1499 guards still hold: one copy at a time, capped backoff, space check, own partial per attempt, check in a worker.
- [ ] AC-03: A finished copy, whole or scoped, is published only when its target does not exist. When another writer published there first, the copy fails with "already exists" and the other copy is kept, not replaced.
- [ ] AC-04: The scoped copy needs far less free space than the database: the check compares free space with the size of the rows it copies plus headroom, not with the whole database.

## Approach

- `apps/server/src/persistence/liveDatabaseSnapshot.ts`: `publishWithoutReplacing(partial, target)` hard-links the finished partial to the target (`linkSync` fails with EEXIST when the target exists), then removes the partial. On a volume without hard links it refuses the copy with a clear message instead (no rename fallback and no placeholder at the target: Node has no no-replace rename, and a placeholder could be taken for a copy or removed while its writer still renames over it; review rounds 1 to 3). `snapshotLiveDatabase` uses it. A retry reuses an existing copy only when it is a non-empty database with pages that passes `quick_check`.
- New `apps/server/src/persistence/projectRowsSnapshot.ts`: `snapshotProjectRows(dbPath, outputPath, projectId, options)`. It lists tables from `sqlite_master` with a `project_id` column (`PRAGMA table_info`), creates each with its original `CREATE TABLE` text in a fresh partial file, copies the matching rows in one read transaction (text as raw bytes cast back to text, so embedded NULs survive; a source that is not UTF-8 is refused before anything is written), adds a `swc_copy_info` table (project id, saved at, source `user_version`), checks the copy in the worker and publishes without replacing. It estimates the size from the matching rows' byte lengths before writing anything.
- `apps/server/src/project/personalLinkSnapshot.ts`: `snapshot(operationId, projectId)` and the default copy is `snapshotProjectRows`. The two callers pass the Percy project's id.
- Rejected: copying the whole database with a `WHERE` afterwards (needs the full size first); `ATTACH` from the live connection (the live database is never opened for writing anywhere but the service's own connection).

## Decisions

### Asked
- D-01 Whole database or Percy's rows in the safety copy → Percy's rows (owner, November 27, 2026, recommended option)
### Defaulted (change any before sw-do)
- D-02 "Percy's rows" means rows of tables with a `project_id` column equal to the Percy project's id. Thread messages and events are keyed by thread and stay out.
- D-03 Headroom for the scoped copy is the same `snapshotHeadroom` (at least 1 GiB) applied to the estimated row bytes.
### Open
- none

## Review

Reviewer: a non-Claude family other than Copilot (out of quota).

## Tasks

### T-01 Publish snapshots without replacing an existing file
- AC: AC-03 | Files: `repositories/anton-abyzov/specwithcode/apps/server/src/persistence/liveDatabaseSnapshot.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/persistence/liveDatabaseSnapshot.test.ts` | Test: `cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/persistence/liveDatabaseSnapshot.test.ts`

### T-02 Scoped copy of one project's rows, used for the Percy safety copy
- AC: AC-01, AC-02, AC-04 | Files: `repositories/anton-abyzov/specwithcode/apps/server/src/persistence/projectRowsSnapshot.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/persistence/projectRowsSnapshot.test.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/personalLinkSnapshot.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/personalLinkSnapshot.test.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/personalShareLink.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/PersonalLinkService.ts` | Test: `cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/persistence/projectRowsSnapshot.test.ts src/project/personalLinkSnapshot.test.ts src/project/personalShareLink.test.ts src/project/PersonalLinkService.test.ts`

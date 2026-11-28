# Percy join database copy stops filling the disk

## Problem

On m4 (November 27, 2026) the server kept starting the whole-database copy a Percy join saves before it links (1448 AC-13, `ensureSeriesCopies` in `apps/server/src/project/personalShareLink.ts`). Deleted-but-open `percy-join-*.sqlite.partial-16951` files held about 22 GiB, grew 1 to 2 GiB per retry, and the disk fell to 4.3 GiB free.

The descriptors were not leaked by a failed copy. They belong to copies that were still running:

1. `snapshotLiveDatabase` (`apps/server/src/persistence/liveDatabaseSnapshot.ts`) calls Node's `sqlite.backup()` with its default 100 pages per step. SQLite restarts a paged backup whenever another connection writes the source, and the service writes `statev2.sqlite` all the time, so an 18.8 GiB copy never finishes. Reproduced on Node 22.20: an 80 MB WAL database with a writer every 2 ms did not finish in 20 s at 100 pages per step, and finished in 6 s with `rate: -1`.
2. A peer aborts a `personal-share` call after 180 s (`apps/server/src/handoff/handoffPeers.ts:153`). The handler is interrupted and the engine lock released, but the backup promise keeps running. The next call starts another copy and first removes `<target>.partial-<pid>`, the same path the running copy writes, so every running copy keeps writing to an unlinked file.
3. Nothing checks free space first and nothing spaces out retries: each peer call starts another copy.

## Scope

In: the copy itself, the Percy snapshotter, the message a peer row shows, tests. Out: whether a join needs a whole-database copy at all (1448 AC-13 asks for one; recommendation recorded under Decisions), freeing the space the running m4 process holds (only its exit frees it; the owner decides the restart).

## Acceptance Criteria

- [x] AC-01: A database copy finishes while another connection keeps writing the database: the online backup copies every page in one step, so SQLite never restarts it.
- [x] AC-02: Before it creates any file, a copy checks the destination's free space and needs the database size plus headroom (the larger of 1 GiB and 10% of the size). Short of that it fails with a message naming the bytes needed and free, and leaves nothing behind.
- [x] AC-03: A failed copy leaves no partial file and no `-journal`; each attempt writes its own partial name, so starting one never removes a file another attempt is writing.
- [x] AC-04: At most one copy per target runs in a server process. A caller that arrives while it runs, including after the earlier caller was interrupted, waits for that copy instead of starting another; leftover partials of the target are removed only when no copy of it runs.
- [x] AC-05: After a failed copy, the next try waits one minute, doubling per failure up to one hour; a call before then fails at once with the last reason and when it tries again. A copy that failed for space tries again as soon as the space is there.
- [x] AC-06: The Percy peer row and the join error show the copy's reason (for example the space needed and free), not only "Could not save a copy of the database".

## Approach

- `liveDatabaseSnapshot.ts`: read `page_count * page_size` on the read-only source connection, compare with `statfsSync` of the target folder (an injectable probe for tests), throw `LiveDatabaseSpaceError` before creating any file; `backup(source, partial, { rate: -1 })`; partial `<target>.partial-<pid>-<random>`; the `finally` removes the partial and its suffixes on failure; export `removeStalePartials(target)`.
- `personalLinkSnapshot.ts`: `makePersonalLinkSnapshotter({ dir, dbPath, now, copy, roomFor })` with state shared per process (a module-level map keyed by resolved target, so the layer provided twice in `runtimeLayer.ts` still runs one copy). In-flight promise per target, removed only when it settles; failure record with backoff 60 s × 2^(n-1) capped at 3,600 s; space failures retry once `roomFor` says the space is there.
- `personalShareLink.ts`: the `snapshot` stage message appends the cause's message.
- Rejected: VACUUM INTO. It is synchronous in `node:sqlite` and would block the server's event loop for the whole copy; the one-step backup runs on the libuv pool (event loop measured at 98 ticks per second during a copy).
- Risk: a one-step backup holds one read snapshot for the copy, so the WAL cannot checkpoint past it and grows while it runs; the headroom covers that.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Keep the whole-database copy and fail closed when it cannot be saved (1448 AC-13). Recommendation for the owner: Undo restores from the Percy restore point (`<id>.percy.json`, `personalRestorePoint.ts`), which holds everything a join changes; the 18.8 GiB copy is a second safety net that costs the database's size in free space on every join series. Replace it with a copy of only the Percy project's rows, or drop it, in a follow-up once the owner agrees.
- D-02 Headroom is the larger of 1 GiB and 10% of the database size.
- D-03 Backoff starts at 1 minute and is capped at 1 hour, kept in memory (a restart retries at once).
### Later (1505, November 27, 2026)
- The Percy join copy is no longer a whole-database backup: 1505 D-01 (owner, recommended option) makes it a copy of the Percy project's rows only (`projectRowsSnapshot.ts`, `.rows.sqlite`). AC-01's one-step backup and AC-02's "database size" now apply to `db snapshot`; the Percy copy reads its rows in one read transaction and checks space against their size. AC-04 is stricter than written: one copy per process for any target, and a second target is refused at once. Copies are published only by hard link, never replacing another copy.
### Open
- none

## Review

Reviewer: a non-Claude family other than Copilot (out of quota).

## Tasks

### T-01 Copy in one step, check space first, own partial per attempt
- AC: AC-01, AC-02, AC-03 | Files: `repositories/anton-abyzov/specwithcode/apps/server/src/persistence/liveDatabaseSnapshot.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/persistence/liveDatabaseSnapshot.test.ts` | Test: `cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/persistence/liveDatabaseSnapshot.test.ts`

### T-02 One copy per target, capped backoff, reason shown on the peer row
- AC: AC-04, AC-05, AC-06 | Files: `repositories/anton-abyzov/specwithcode/apps/server/src/project/personalLinkSnapshot.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/personalLinkSnapshot.test.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/personalShareLink.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/personalShareLink.test.ts` | Test: `cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/project/personalLinkSnapshot.test.ts src/project/personalShareLink.test.ts`

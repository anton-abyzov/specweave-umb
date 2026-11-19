# Update install reports the real failure reason

## Problem

A failed desktop install says nothing useful. On Ministorm the .deb app has stayed on 1.0.76 since October 24, 2026: every Restart runs `dpkg -i` on an AppImage, dpkg refuses it, electron-updater runs `apt-get install -f`, which succeeds, and the app relaunches on the old version with no error. The one logged error, "Desktop updater install operation reported an error.", drops the cause.

The AppImage comes from the token path. With `gh` signed in, the feed is `private: true`, whose asset URLs end in an ID, so DebUpdater's `findFile` cannot see `.deb` and takes the first file not excluded by name.

Rescoped November 19, 2026 (approved by Anton that day). The desktop half above shipped on November 2: the .deb feed fix in 1.0.150 (`353872780`, `apps/desktop/src/updates/platformFeed.ts`, a .deb reads the feed without the sign-in) and the failure reason with the relaunch review in 1.0.153 (`59a71d2ac`, `installAttempt.ts`). The same gap remains in the service helper. On November 18, 2026 the M4's install of 1.0.361 (`updates/receipts/update-1.0.361-20261118T190331588596Z.json`) recorded `pageFallback: "Refused:auth-heartbeat:Protected rows or counts changed"`, fell to the full read, failed with `SpillFailed ... [Errno 28] Scratch volume is below its floor` (`rollback: held-for-safe-review`), and the agent held every later release until a held install was run by hand. The message comes from `auth_heartbeat.assert_only_auth_hash_changed` and names neither the key, the table nor the counts. The receipt's `stateBackup` was the only copy that could name the row, and 1.0.374's verified install pruned it: `superseded_receipts` (`release_retention.py`) turns a failed receipt's copy into a finished one as soon as a later install verifies. Increment 1414 (released in 1.0.376) gives the way out of the hold (Update now in the sidebar and Settings); this increment makes the next refusal say what changed and keeps the evidence.

## Scope

In: the failure reason in the sidebar and logs, a review at the next launch of whether the attempted version runs, and looking in the Linux journal for the installer's error (shipped in 1.0.153, confirmed by its tests here). On a protected-row refusal, the receipt names the differing proof key, and for counts each table with its before and after count, never row content. A failed install's state copy stays until someone marks it read, at most one per identity, with a documented command. A release.

Out: forcing an update on any machine (machines take the release on their own schedule; read back only where they did). Changing what the guarded-prestate or heartbeat proof accepts. Freeing scratch room for the full read. Showing a desktop app failure from another machine in this machine's fleet row. Service failures already reach that row through `ServerUpdateProgress`. Raw check and download errors stay generic, because HTTP errors may carry request details.

## Acceptance Criteria

- [ ] AC-01: The release carries #1188, so a .deb install downloads the .deb.
- [ ] AC-02: A failed install's state and log carry the updater's first line, with tokens removed.
- [ ] AC-03: A relaunch that still runs the old version records why, from the Linux journal when it has the installer's error, and says plainly when the machine left none.
- [ ] AC-04: The sidebar keeps saying why across later checks, until that version is reached.
- [ ] AC-05: The fix is in a published release, and the installed version is read back on each machine that updated itself; no machine is forced.
- [ ] AC-06: When the page proof refuses because a protected proof key differs, the refusal and the receipt's `pageFallback` name that key; for `counts`, each table whose count differs with its before and after count; for another protected table's hash, that table's name. No row content, identifier or hash value is written. The detail survives the full read failing afterwards.
- [ ] AC-07: The newest failed install's state copy per identity (a receipt with a failed result or a held rollback, naming `stateBackup`) is kept by the pre-copy prune, the after-install prune and space pruning, also after a later install verifies, until its receipt carries `stateBackupReadAt`. Only that one copy is kept; an older failed copy follows today's rules.
- [ ] AC-08: `python3 scripts/studio-fleet/state_backup_prune.py --mark-read <receipt>` stamps `stateBackupReadAt` under the installation lock, and `docs/studio/updates.md` says how to read the kept copy and release it.

## Approach

Helper side (new): `auth_heartbeat.assert_only_auth_hash_changed` appends the differing key and counts to its existing messages, so every matcher that reads them by prefix or substring keeps working and `pageFallback` (`update_apply._why`, 160 characters) carries it with no new receipt key (1414's `refusal_proof` accepts exactly five keys). `release_retention.unread_failure_copy` picks the one copy per identity; `state_backup_references` and `held_state_backups` hold it. `update.py` (1,462 lines) and `update_agent.py` (1,500) are not touched.

Desktop side (shipped): `apps/desktop/src/updates/installAttempt.ts` holds the records and the diagnosis. `DesktopUpdates.ts` writes the attempt before the quit and reviews it when the pollers start. The 1.0.76 app cannot fix itself because its updater has the bug, so Ministorm needs one `dpkg -i` of the new .deb.

## Review

- Reviewer: openai (gpt-6.1-sol)
- Depth: deep
- Required: yes

Muse and Codex are out (November 19, 2026); the standing fallback (Anton, November 18: "Yes, as a standing rule") is Copilot Enterprise `acpRegistry_copilot` with `gpt-6.1-sol`.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 "Read" is an explicit command that stamps the receipt (`stateBackupReadAt`), not a timer.
- D-02 At most one unread failed copy per identity, the newest; it can cost up to one database of disk. Its release command is in the docs. Naming the kept copy in a later room refusal is left out, since the room messages are matched by the agent.
- D-03 AC-05 no longer requires M4 and Ministorm on the release: forcing an update on a busy machine is not allowed, so closure needs the release and read-backs where machines updated themselves.
### Open
- none

## Tasks

### T-01 Reason in the install failure and the relaunch review

- AC: AC-02, AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/desktop/src/updates/installAttempt.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/updates/DesktopUpdates.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/sidebar/SidebarRestartToUpdate.logic.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/desktopUpdateState.ts | Test: `installAttempt.test.ts`, `DesktopUpdates.test.ts`

### T-02 Carry the .deb feed fix from #1188

- AC: AC-01 | Files: none | Test: `git log` of the release contains #1188

### T-05 Refusal names the protected key and counts

- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode/scripts/studio-fleet/auth_heartbeat.py, repositories/anton-abyzov/specwithcode/scripts/studio-fleet/test-refusal-detail.py | Test: `cd repositories/anton-abyzov/specwithcode/scripts/studio-fleet && python3 -B test-refusal-detail.py && python3 -B test-auth-read-consistency.py`

### T-06 Keep a failed install's state copy until it is read

- AC: AC-07, AC-08 | Files: repositories/anton-abyzov/specwithcode/scripts/studio-fleet/release_retention.py, repositories/anton-abyzov/specwithcode/scripts/studio-fleet/state_backup_prune.py, repositories/anton-abyzov/specwithcode/scripts/studio-fleet/test-unread-failure-copy.py, repositories/anton-abyzov/specwithcode/scripts/studio-fleet/test-state-backup-prune.py, repositories/anton-abyzov/specwithcode/docs/studio/updates.md | Test: `cd repositories/anton-abyzov/specwithcode/scripts/studio-fleet && python3 -B test-unread-failure-copy.py && python3 -B test-release-retention.py && python3 -B test-state-backup-prune.py`

### T-03 Release and read back

- AC: AC-05 | Files: none | Test: published release contains the merge; installed versions read on machines that updated themselves

### T-04 Verify and close 1168

- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08 | Files: none | Test: `specweave verify`

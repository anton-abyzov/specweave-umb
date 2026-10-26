# Pre-restart re-reads stay incremental while threads are busy

## Problem

The 1.0.88 install on M4 (October 26, 2026, receipt `~/.specwithcode/m4/updates/receipts/update-1.0.88-20261026T012927276260Z.json`) failed and rolled back: `beforeRead` 261 s, `prestateCheck` 254 s, `checkBeforeRestart` 257 s, so the helper ran out of its readiness budget before the restart ("Preparing the update took too long"). On the 1.0.86 install the same two checks took 8 s and 0.6 s.

Both checks re-read the database with `read_delta.reread`, which answers only when nothing but `auth_sessions` was written since the before read, in the same `-wal` generation, with the database file untouched; otherwise the full read (about 255 s on the 21.5 GB database) decides. A read-only sample of the live 1.0.86 service the same night showed it checkpointing into the database file and resetting its `-wal` every 5 to 45 s, writing `orchestration_events`, turn items, projection nodes and `scheduled_tasks`: ordinary thread activity. Any busy thread during the roughly five-minute window therefore costs two full reads, and the update fails on time. The helper code did not change between 1.0.86 and 1.0.88 (only #757's snapshot marker); the difference was load.

## Scope

In: the helper's two pre-restart re-reads (`prestateCheck` against the agent's snapshot, `checkBeforeRestart` against the before read) decide from what changed while threads keep writing; the full read stays the fallback. Receipt fields name which path ran and why a fallback happened.
Out: the before read itself and the agent's prestate read (one full read each is the base), the post-restart proof (0993), compaction (#757).

## Acceptance Criteria

- [ ] AC-01: From right before the before read until the mark, a held reader (0993 T-09's `after_proof` reader) keeps the before read's snapshot: no checkpoint copies past it and the `-wal` does not restart. The reader's snapshot is accepted as the before read's only when the read watermark shows no commit between the reader opening and the before read's transaction; otherwise the re-reads behave as today.
- [ ] AC-02: With the reader held, a re-read takes the pages of every frame after the snapshot (the whole log since it, the database file being written only up to the snapshot), maps them to tables with `dbstat`, re-reads touched small tables, and proves logs by row checks of touched leaves plus appended rows, against a reference image of the snapshot (the database file cloned, with each page that has a frame at or below the snapshot written back from its last such frame, cut to the snapshot's page count). Untouched tables reuse the before read.
- [ ] AC-03: A fixture with a node:sqlite writer appending events, turn items and scheduled task updates, and checkpointing past the autocheckpoint throughout the window, returns rows, carried rows and capture byte-identical to the full read for both re-reads, and refuses (full read decides) an old row updated or deleted, a table dropped, and a lost reader.
- [ ] AC-04: On M4's database clone with that writer running, `prestateCheck` and `checkBeforeRestart` each finish in under 15 s (today 254 s and 257 s), and the receipt records `deltaReads` with each path and fallback reason.
- [ ] AC-05: An installed release on M4 with threads active during the update keeps both checks under 15 s and verifies.

## Approach

Reuse 0993 T-09 (PR #763): `after_proof._Reader` for the pinned snapshot and the reference-image construction, `after_proof._Proof`'s table and leaf comparison with the live database in place of the stop clone. `read_delta.reread` gains the held path; `update.py` starts the reader before `before_mark`, hands it to `delta_since`, and the final mark reuses it instead of starting a second reader. Risk: the `-wal` grows while the reader holds (about 5 minutes of writes; measured 0.4 MB/s on M4); refuse and fall back above a size cap. Rejected: retrying installs only when idle (busy machines never update), a longer readiness budget (two full reads stay 8 minutes).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Separate increment from 0993: 0993 scopes the post-restart proof and lists the pre-restart reads as out.
### Open
- none

## Tasks

### T-01 Held reader from the before read through the mark
- AC: AC-01 | Files: repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/update.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/after_proof.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/test-after-proof.py | Test: cd repositories/anton-abyzov/specweave-studio/scripts/studio-fleet && python3 -B test-after-proof.py && python3 -B test-update.py

### T-02 Re-read by pages against the snapshot's reference image
- AC: AC-02, AC-03 | Files: repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/read_delta.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/test-update-read-delta.py, repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/update.py | Test: cd repositories/anton-abyzov/specweave-studio/scripts/studio-fleet && python3 -B test-update-read-delta.py && bash run-tests.sh --out "$(mktemp -d)"

### T-03 Measure on M4's clone and on an installed release
- AC: AC-04, AC-05 | Files: repositories/anton-abyzov/specweave-studio/docs/studio/updates.md | Test: python3 -B repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/test-update-read-delta.py --measure ~/.specwithcode/m4/userdata

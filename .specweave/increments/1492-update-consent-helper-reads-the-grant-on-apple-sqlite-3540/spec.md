# 1492 Update consent helper and rehearsal read a stopped database on Apple SQLite 3.54.0

## Problem

1491 made `live_database.connect` read a stopped service's database on Apple's SQLite 3.54.0 (`/usr/bin/python3` on macOS 27). Two update paths still opened the database with their own plain `mode=ro` URI, which 3.54.0 refuses with "unable to open database file" when a stopped service has left only the main file:

- `managed_updates.fresh_grant` reads the controller's grant from `auth_sessions`. On a stopped destination every status, check, enrolment and remote apply then fails as `unavailable`. Reproduced on 3.54.0; stock 3.53.1 reads it.
- `rehearse_update.protected` reads the rehearsal clone. A stopped source has no `-wal`, so the clone is the main file alone, and the rehearsal fails before it starts. Its test passed only because Apple's SQLite left a `-wal` beside the fixture.

## Scope

In: the two reads above and their tests.

Out:
- The grant check itself: same row, same subject, scope, expiry and revocation rules.
- The deliberate `immutable=1` reads of stopped databases and clones (`disk_room.py`, `update_apply.py`, `after_proof.py`), which work on both builds.

## Acceptance Criteria

- [ ] AC-01: On `/usr/bin/python3` (SQLite 3.54.0), the consent helper reads the grant of a stopped service's WAL database (only the main file on disk): status reports `not-enrolled`, enrolment succeeds, and a revoked grant is still refused as `unauthorized`.
- [ ] AC-02: On the same build, `rehearse_update.protected` reads a clone of a stopped source that has only its main file.
- [ ] AC-03: The fleet suite passes on `/usr/bin/python3` (3.54.0) and on uv Python 3.12 (3.53.1) in the gated checks copy with the server built.

## Approach

Both reads go through `live_database.connect`, which 1491 made work on every SQLite build. `live_database.py` already ships beside `managed_updates.py` in the updater set (`scripts/lib/studio-service-updater.ts`), so the reason for inlining the URI no longer holds. `rehearse_update.py` lives in `scripts/studio-fleet` with it.

The helper runs as the installation's owner (`installation_descriptor.owned_path` requires `os.getuid()`), so the empty side files that the fallback may create belong to the service's own user.

Tests:
- The helper's fixture database becomes a WAL database closed the way the service closes it (`sqlite_fixture.close`).
- A rehearsal unit test reads such a clone.

Rejected: keeping the inlined URI and copying the 1491 fallback into it. That would be two copies of the lock check and side-file creation.

## Decisions

### Asked

- none (the user asked to complete the open follow-up from 1491)

### Defaulted

- D-01 This changes only how the helper opens the database, not what it reads or decides, so it is not an auth change (reversible).

### Open

- none

## Tasks

### T-01 Read the grant and the clone through live_database
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/scripts/studio-fleet/managed_updates.py, repositories/anton-abyzov/specwithcode/scripts/studio-fleet/test-managed-updates.py, repositories/anton-abyzov/specwithcode/scripts/studio-fleet/rehearse_update.py, repositories/anton-abyzov/specwithcode/scripts/studio-fleet/test-rehearse-update.py | Test: cd repositories/anton-abyzov/specwithcode/scripts/studio-fleet && /usr/bin/python3 -B test-managed-updates.py && /usr/bin/python3 -B test-rehearse-update.py ProtectedRead

### T-02 Fleet suite on both SQLite builds
- AC: AC-03 | Files: .specweave/increments/1492-update-consent-helper-reads-the-grant-on-apple-sqlite-3540/reports/fleet-both-sqlite.md | Test: grep -q "both builds pass" .specweave/increments/1492-update-consent-helper-reads-the-grant-on-apple-sqlite-3540/reports/fleet-both-sqlite.md

Verify and close 1492.

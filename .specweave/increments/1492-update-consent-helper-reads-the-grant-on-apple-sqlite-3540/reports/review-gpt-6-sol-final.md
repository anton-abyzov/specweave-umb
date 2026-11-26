# Review: 1492 close
Verdict: ship
Reviewed commit: 5ddc104e8bf07eefcb677cf2005aadf1d3c65850
Reviewer context: fresh GPT-6-Sol session on Codex; reviewed the squash merge against `733992c8f04aec6e670bf5215bffb4a8d7ce31c7`.

## Findings

None.

## Acceptance criteria and evidence

- AC-01: `scripts/studio-fleet/managed_updates.py:87-112` opens the grant database through `live_database.connect` while preserving the session, subject, revocation, time, and scope checks. `test-managed-updates.py:176-194` asserts a main-file-only WAL fixture, `not-enrolled`, successful enrolment followed by `enrolled`, and `unauthorized` for a revoked grant. The full file passed 33 tests on each Python build. A connection failure is caught by `managed_updates.py:389-390` and returned as `unavailable`.
- AC-02: `scripts/studio-fleet/rehearse_update.py:110-128` opens the clone through `live_database.connect` and retains the protected-table digest logic. `test-rehearse-update.py:70-85` asserts a main-file-only WAL fixture and two rows read. `ProtectedRead` passed on each build.
- AC-03: `reports/fleet-both-sqlite.md` and its referenced `fleet-run.log`, `fleet-3.54.0.log`, and `fleet-3.53.1.log` show a server-built checks copy at `3b79c639`, 85 fleet tests run with zero failures on Apple's SQLite 3.54.0 and stock SQLite 3.53.1. The logs list two skipped startup acceptance proofs on each build. `reports/verify.md` and `verify.json` report 3/3 ACs met and green PR and server checks.

## Merge and spec check

`5ddc104e` has parent `733992c8f`. Its four-file patch equals the patch from that parent to reviewed PR head `3b79c639`; no extra files changed. Both commits have the same tree, `9c7525fb17847736d888f2adaf2093e2fdfc2f1b`. The focused tests and fleet suite ran on the local `3b79c639` checkout, which is therefore identical in content to the merged commit. `spec.md` describes the two read changes, preserved grant rules, regression tests, and both-build fleet check that shipped.

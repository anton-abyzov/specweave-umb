# One-click fast updates

## Problem

Updating SpecWithCode takes two presses and minutes of downtime. On 2026-10-20, updating M4 from 1.0.59 to 1.0.60 ran from the first press at 04:06:56 UTC to done at 04:14:03:
- Press 1 swapped and relaunched the Mac app. The relaunched app requested the service install 19 s later (04:07:30).
- The agent snapshotted at 04:07:39. update.py's preflight then failed with "Guarded prestate changed: rows", because the relaunched app had rewritten its own auth_sessions row (client_app_version 1.0.59 to 1.0.60) between the snapshot and the apply.
- The toast then sat on "Preparing to install", showing "Cancel update" and "Update now", until the user pressed again at 04:08:54.
- That second attempt took 5m09s. About 4m14s of it was service downtime (restart at 04:08:58, new process at 04:13:12), during which a 4.1 GB database backup was written (receipts and backups in ~/.specwithcode/m4/updates/receipts and ~/.specwithcode/backups).

The first attempt failed the same way on 1.0.49, 1.0.50, 1.0.53, 1.0.54 and 1.0.60. Update options are split between Settings and the toast. The toast and the sidebar both offer "Update now", and either one re-runs prepare. agent.log has no timestamps and receipts have no per-phase timings, so nobody can see where install time goes.

## Scope

In: [what this increment ships]. Out: [what it does not include].

## Acceptance Criteria

- [ ] AC-01: [Specific, testable criterion]
- [ ] AC-02: [Specific, testable criterion]

## Approach

[Files that change, in order; key decisions; rejected alternatives; risks.]

## Decisions

### Asked
- [D-01 question → answer (user), or "none"]
### Defaulted (change any before sw-do)
- [D-02 decision → default (reversible), or "none"]
### Open
- none

## Tasks

### T-01 [First task]
- AC: AC-01 | Files: [src/file.ts, tests/e2e/file.test.ts] | Test: [command that checks AC-01 as a user would]

### T-02 [Second task]
- AC: AC-02 | Files: [src/other.ts] | Test: [command]

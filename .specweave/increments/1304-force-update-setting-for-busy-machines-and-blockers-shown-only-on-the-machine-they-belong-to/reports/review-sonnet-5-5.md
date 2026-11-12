# Review: 1304, PR 175

Reviewer: independent Sonnet 5.5 sessions, fresh context, read-only. Three area reviews before the PR, then three rounds on the exact PR head.

## Before the PR: 1 SHIP, 2 NO-SHIP

- Server: SHIP with should-fix items. Fixed: a forced Linux install failed when the drain failed; settings read through an optional service could silently read off; a tautological test for AC-07.
- Agent and rollout: NO-SHIP. Blocker: a worker with a broken updater and the setting off was reported `deferred` with exit 0. Fixed: a host is left for later only on evidence that running work kept it; full deadlines kept; a deferred worker row carries its desktop app step.
- Settings UI and docs: NO-SHIP. Fixed: the Linux "off" text, contradictions in `docs/studio/releasing.md` and `docs/studio/updates.md`, settings access check, a stale switch after changing machines.

## Round 1, head `ddb8482472`: SHIP

Four should-fix items and three notes, all answered in `01a39e891b`: a Linux give-up without running work read "left for later"; the candidate channel could finalize with a required worker left for later; a machine older than the setting showed a chosen "off"; docs wording and the SSH route with `--worker-force`; a stale give-up from an earlier request; unreadable settings reported as a service older than the setting; the stale-wait sweep (kept, decision D-18).

## Round 2, head `01a39e891b`: SHIP

Every round 1 finding resolved. The reviewer ran `test-update-policy.py` (22), `test-fleet-rollout-pause-setting.py` (26), `test-update-agent-pause.py` (42), the server update tests (92), `UpdatePausePolicyRow.test.tsx` (15) and the release self-test (138 passed, 0 failed).

Notes, none blocking:

- `scripts/release/release-canary.sh:39`: a busy M1 or M3 with the setting off now stops a candidate release until it is quiet (decision D-15; the owner's call).
- `apps/server/src/serviceUpdate/ServiceUpdatePreparation.ts` is 1,509 lines against a 1,500 limit; it was 1,507 before.

## Round 3, head `e20f988f80` (main merged in): SHIP

The merge adds only main's 19 files; nothing of the reviewed change was lost; no interaction with PR #176.

## Outcome

PR head at merge was `ea77e95607`: `e20f988f80` plus main's PR #177 (four Claude adapter files and one changelog line), checked by file list and blobs. 21 checks passed on it. Merged as `82a81be658a4c26dc8d87581f06a89175190f58c`.

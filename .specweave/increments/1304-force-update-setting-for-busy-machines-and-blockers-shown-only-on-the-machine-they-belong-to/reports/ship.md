# 1304 ship record

Date: November 11, 2026 (EST).

## Delivered

- PR: https://github.com/anton-abyzov/specwithcode/pull/175, squash commit `82a81be658a4c26dc8d87581f06a89175190f58c` on `main` of `anton-abyzov/specwithcode`, merged at 10:59 PM EST. 56 files, +3,223 and -173.
- Umbrella: `scripts/release/release.sh` and its self-test (commit `3ea819eee`), the blocker rule routed to increment 1278 as AC-11 to AC-16 (commit `046586460`), report `reports/blocker-count-gate.md`.
- Release request: sent to the "Release all platforms in 3 hours" thread with the commit, scope, evidence and the rollout changes.

## Reviews

All by an independent Sonnet 5.5 reviewer, read-only, on the exact head.

| Head | Verdict | Outcome |
|---|---|---|
| before the PR (three areas) | 1 SHIP, 2 NO-SHIP | one blocker and the should-fix items fixed before the PR opened |
| `ddb8482472` | SHIP | four should-fix items and three notes, all answered in `01a39e891b` |
| `01a39e891b` | SHIP | every earlier finding resolved; two notes (D-15, file size) |
| `e20f988f80` (main merged in) | SHIP | the merge adds only main's files |

The merged tree equals PR head `ea77e95607`. It differs from `e20f988f80` only by main's PR #177 (four Claude adapter files and one changelog line), checked by comparing file lists and blobs.

## Checks

On the final content, in the scratch export `/Users/antonabyzov/.specwithcode/m4/scratch/2026-11-11-force-update/tree`:

- Fleet tests (`bash scripts/studio-fleet/run-tests.sh`): 83 run, 0 failed.
- Release self-test (`bash scripts/release/release.sh --self-test`): 138 passed, 0 failed.
- Server (`src/fleet src/serviceUpdate src/studioFleetHttp.test.ts src/cli src/serverSettings`): 129 files, 1,683 tests passed.
- Web (`src/components/settings src/i18n`): 134 files, 1,747 tests passed after main was merged in.
- Contracts: 73 files, 1,019 tests passed. Shared `updatePause.test.ts`: 4 passed. Client runtime `sharedSettings.test.ts`: 28 passed.
- Typecheck gate for contracts, shared, client-runtime, server, web and desktop: 0 new diagnostics.
- Headless fixture `apps/web/tests/machines-page/verify.mjs`: switch off, on, and a worker older than the setting. Screenshots beside this file: `pause-setting-off.png`, `pause-setting-on.png`, `pause-setting-old.png`.

CI on PR head `ea77e95607`: 21 checks passed. The iOS layout run (about 40 minutes) was still running at merge. It passed on `ddb8482472`, and the `apps/ios` tree is identical since (tree `65087bda8c`), so the merge did not wait for a third rerun while main kept moving.

One CI failure on the way: Android `MachineConnectionTest > aShortLivedConnectionBacksOffAndAStableOneDoesNot` failed once on `ddb8482472` and passed on rerun and on every later head. It is a timing test in a module this change does not touch.

## Decisions taken in review (spec D-14 to D-18)

- A machine older than the setting shows the switch locked with "update this machine first".
- The candidate release channel still needs M4, M1 and M3 verified before finalize: a required worker left for later stops it with exit 1, and `--resume` continues once it is quiet. Relaxing that is the owner's call.
- A worker reached over pinned SSH is never forced.
- A Linux wait that ended without running work is a failure, never "left for later".
- Unanswered questions are still closed and asked again after the restart, with the setting on or off.

## Left open

- After the M4 runs the release with this change: turn "Pause running work for updates" on for the M4 only (Anton's choice, D-07). The switch is on the M4's update card in Settings > General.
- Blocker badges counted once: increment 1278, AC-11 to AC-16.
- The Releases view has no `deferred` state of its own yet (D-12).
- `apps/server/src/serviceUpdate/ServiceUpdatePreparation.ts` is 1,509 lines; it was 1,507 before, over the 1,500 limit.
- `apps/web/src/components/settings/ConnectDeregisterHint.tsx` from PR #176 uses a phrase missing from the eight catalogs ("Open SpecWithCode Connect settings").
- The umbrella's `scripts/release/release-self-test.sh` has 31 failing worktree cleanup cases that fail the same way without this change.

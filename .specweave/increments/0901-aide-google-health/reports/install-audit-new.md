# 1.0.7 installation audit — 2026-10-13

Read-only observations of the existing installation owner. No claim, pickup, process signal, priority change, listener, service restart, provider run, database capture, or browser automation was performed. SpecWeave installed and npm stable were both 3.0.14. Artifact validation is recorded separately in `artifact-audit.md`.

## Current attempt and last observation

At 04:51:38 UTC, the current helper was still preparing the update; it had not restarted the service. The updater state remained `installing`, message `Installing Studio 1.0.7`, installed version `1.0.5`, last updated 04:36:17.069336 UTC. The receipt `~/.specweave-studio/m4/updates/receipts/update-1.0.7-20261013T043616983794Z.json` did not exist. This is not an installation success or terminal failure receipt.

| PID | Role | Elapsed | Accumulated CPU | State | RSS KiB |
|---|---|---:|---:|---|---:|
| 27954 | Existing updater owner | 21:13 | 0:00.73 | S | 5,872 |
| 43485 | Bound 1.0.7 apply helper | 15:21 | 0:16.71 | Rs | 233,744 |
| 66041 | Existing 1.0.5 service | 08:25:02 | 4:51.17 | S | 237,328 |

Installer child PID 63320 had exited by 04:50:58. Its parent apply helper remained alive. The private staging home `~/.local/share/specweave-studio/incoming/owned-update-stage-ap2vcdan` existed; the globally published release `~/.local/share/specweave-studio/releases/600a4c54e381cbaed29c` did not. The correct release directory uses the first 20 archive-SHA characters, without a trailing `7`.

The helper is bound to `~/.specweave-studio/m4/updates/helpers/1.0.7/studio-1.0.7-deployment-helpers-54aa7e7d7ba1/scripts/studio-fleet/update.py`. Its update/install script bytes matched the released source. Its archive SHA is `600a4c54e381cbaed29c7e530e19ae424e70ac80ba5da7d41104566b97951830`. The only optional apply flag observed was `--allow-existing-browser-heartbeat`.

## Phase evidence

- Apply started approximately 04:36:17; the installer child started 04:41:37.247, approximately 5m20s later. Source performs the initial complete snapshot and prestate comparison before starting that child. That duration is composite; it cannot be attributed solely to SQLite.
- At 04:46:58, child PID 63320 held an open file inside `.stage-63320/client/assets/`; its private release directory still had the `.stage-63320` suffix. This places it before the installer rename, during extraction or first validation.
- By 04:48:23, that private directory had been renamed to `600a4c54e381cbaed29c`. Source renames only after extraction and first full content verification, then performs another complete verification and exact file-set comparison. Child elapsed time was 6m46s.
- At 04:48:59, child PID 63320 had elapsed 7m22s but accumulated only 19.60s CPU. Apply PID 43485 had elapsed 12m42s and accumulated 9.40s CPU.
- At 04:50:58 the child had exited, while the apply helper and private stage remained. At 04:51:38 no globally published new release or prepared receipt existed.

## Native sample and I/O priority

A permitted, unprivileged `sample 63320 1 1` produced `install-stage-sample-63320.txt`: 859 samples over one second, 42.8 MB physical footprint, 122 MB peak. Collapsed hot leaves were `stat` 200 samples (23.3%), `_platform_strchr` 128 (14.9%), and Python evaluation/path/argument machinery. No SHA, JSON, SQLite, wait, or throttle symbol appeared. This supports filesystem metadata/path traversal at that instant; the native sample does not resolve Python source lines or establish kernel I/O throttling.

The updater launch agent `~/Library/LaunchAgents/com.specweave.studio.m4.updater.plist` has `LowPriorityIO = true` and `ProcessType = Standard`, with no explicit `Nice` or `BackgroundPriority`. All inspected updater/helper/installer/service PIDs returned nice 0 and Darwin background priority 0. Those results do **not** rule out the separate low-priority I/O policy. The combination of low CPU relative to elapsed time, metadata-heavy sample, and the launch-agent I/O setting makes I/O scheduling a credible cause; causation is not yet proven.

## Quantified data, without an overlapping benchmark

| Object | Count or byte size |
|---|---:|
| 1.0.5 runtime manifest | 7,479 entries: 7,440 regular files, 39 symlinks |
| 1.0.5 regular-file content | 352,270,967 bytes |
| 1.0.5 source maps | 113,765,924 bytes |
| 1.0.7 runtime manifest | 7,479 entries: 7,440 regular files, 39 symlinks |
| 1.0.7 regular-file content | 352,550,536 bytes |
| 1.0.7 source maps | 113,971,030 bytes |
| Live database | 154,255,360 bytes |
| Live database WAL | 4,313,672 bytes |

The saved prestate recorded 17,735 orchestration events, 3,529 projected turn items, 3,529 turn-item positions, 2,633 command receipts, 2,438 projected nodes, 968 project-memory rows, 968 project-memory revisions, and 503 projected messages. These counts came from existing evidence, not a new live database scan. No expensive bundle/full test or timing benchmark was run alongside the installer.

## Source cost and preserved safety requirements

Released `update.py` starts its apply timer before the initial snapshot. Each `_snapshot` performs `_service`'s complete old-release verification, protected-file hashes, `_read_state(..., include_database=True)`, other-listener observation, and quiescence capture. The database reader selects/serializes protected tables, then `database_continuity.capture_connection` independently selects all tables and computes typed and legacy hashes. This repeats protected-table reads and legacy hashes within the same read transaction.

`install.py` validates the archive SHA, archive graph and manifest, extracts, hashes every regular file, renames, and hashes/enumerates the complete release again. The caller then fully verifies the staged release, re-verifies the old release for upgrade validation, captures another full prestate, and `publish_release` re-verifies the staged release. Further full snapshots precede the prepared receipt and pointer changes. Repeated expensive reads occur before the next synchronous deadline check.

Observed apply budget was 1,500 seconds. Existing constants reserve 420 seconds and a further 300-second minimum readiness interval, leaving 780 seconds (13 minutes) for preparation before the pre-restart check. The last observation exceeded that allowance while still inside synchronous preparation. A prior 1.0.6 attempt failed at the pre-restart budget check with `Preparing the update took too long to leave time for the restart; nothing was changed`; another failed on `otherListeners` drift. Neither guard should be weakened.

## Lowest-risk next steps for the installer owner

1. Await the existing attempt's terminal receipt; do not edit its helper, run a competing installer, signal it, or change its priority.
2. After ownership coordination and fresh prestate, consider executing the unchanged, verified helper from a normal foreground process with the same budget, archive/manifest checks, listener/native-work guards, rollback, and readiness checks. Record its PID and final receipt. This tests the low-priority-I/O hypothesis without modifying update safety logic.
3. If source optimization is still necessary, reuse equivalent legacy capture results within one SQLite read transaction while preserving the exact hashes, typed-cell/schema proof and prestate behavior. Require focused equivalence and mutation regressions. Reusing artifacts must be anchored to the exact archive SHA and complete expected manifest, with path, symlink, content and file-set verification; version, size or mtime alone are insufficient.

1.0.7 artifact evidence already establishes the compiled approved Google client pair in both runtime and desktop, matching signatures/provenance, and no bundled Google refresh token. It does not establish a successful local installation, Google user consent, current service grants, or real Calendar/Gmail/Drive reads.

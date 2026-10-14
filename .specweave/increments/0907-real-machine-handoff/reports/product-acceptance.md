# Ordinary app handoff acceptance

Status: pending. Zero of six ordinary app routes are accepted. The earlier six manual continuation routes remain separately verified.

Manual UI acceptance is complete: Anton explicitly answered “Approve the handoff UI” after reviewing the desktop and mobile previews. That human reply was verified directly in the release chat and retained privately as `product-handoff-ui-human-acceptance.json`. It approves the shown screen; the six real route and runtime checks below remain required.

The source coordinator and worker ran on M4 for each project, inspected an intentionally unfinished diagnostic and recorded its decision and next step. These frozen root and nested commits define the work to continue:

| Project | Root commit | Nested commit | M1 | M3 |
| --- | --- | --- | --- | --- |
| EasyChamp | `c3041afc28be64c210f2930a3bbf3a349830f8d9` | `5f007a879326da7dd5308be44bacab1a008c42cd` | Pending | Pending |
| JobWeave | `2c1ee9044cb0552880cb7a8ffe410dfc33f2a43f` | `4c06374e06ec1d3ab8e740a3d20f08cdb5035043` | Pending | Pending |
| SpecWeave | `d070ef2a0cb78f8d6be1469cf15355ab16e5f220` | `3ec9650a889f1b71f081e63f0471e8503224c507` | Pending | Pending |

Each accepted route must originate from the ordinary native coordinator picker, identify the actual source and selected destination, publish the exact root and nested commits through the app, retain conversation and durable context, and launch a fresh destination worker. That worker must finish the diagnostic, pass the unchanged tests and commit its bounded change; the coordinator must then resume automatically. Runtime identities and preservation snapshots must bracket the actual actions.

The historical SpecWeave-to-M3 operation `23084e77-d203-4463-9f85-7fbc208d2299` transferred its code and context but was interrupted before any worker or edit. It remains failed and cannot be reused as an accepted route. The old usage-limit EasyChamp transfer is also excluded from ordinary handoff acceptance.

The historical preview changed four promisor clone Git configuration hashes. Its failed comparison stays retained. A byte-level historical audit and a fresh pre-corrected-candidate baseline are separate from the final candidate's strict before/after preservation check. Configuration values, credentials and raw private conversation receipts are not published in this report.

Private source, operation, UI, runtime and native-worker receipts live under `~/.local/share/specweave/fleet/handoff-proof-20261013`. The required acceptance command is `python3 scripts/fleet/verify-handoff-evidence.py --phase product-handoff`; it must fail until all six genuine route records and final preservation readbacks are present.


## Release continuity — 1.0.13

The released native app and all three managed hosts now use source `9cdc215c4171b441321aea65b4f6c8ba7ee2756c`. Publication, updater and installed-runtime evidence is recorded in `product-release.md`. The 1.0.13 successor evidence root is `/Volumes/SanDisk APFS/SpecWithCodeReleases/0907-113`; the earlier evidence root and every failed route remain historical records.

This release preparation accepts zero of the six routes. The frozen diagnostic source commits above and genuine subsequent source-checkpoint records remain distinct from the product release commit. T-08 still needs the exact six successful operation/native-worker records, context/code transfer proof, final commits, coordinator continuation and before/after preservation under the existing verifier.

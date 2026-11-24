---
title: "Finish sweep inventory, November 20, 2026"
thread: "thread:delegated-task:command%3Amcp%3A5203f9f6-1c70-4578-a8a9-fc4f6def2ca7%3Adelegate-task%3Acc1de104-0ef7-49db-940a-31d8f6471a86"
threadTitle: "Finish almost-done work across all machines"
savedAt: "2026-11-20T19:17:20.273Z"
date: November 20, 2026
machine: M5
status: inventory, before any action
---

# Finish sweep inventory, November 20, 2026

Taken on M5 before acting. m4 and linux-mini are being read by their own read-only workers; their sections are added when those report. m1 is not in the machine list and win has no copy of this project, so neither is inventoried.

## Machines

| Machine | State | Inventory |
|---|---|---|
| M5 | local | complete, below |
| m4 | ready, Claude at 100 % until November 21, Codex at 19 % | worker running, file `~/.specwithcode/m4/evidence/finish-sweep-2026-11-20/inventory-m4.md` |
| linux-mini | ready, Claude at 16 % | worker running, file `~/.specwithcode/ministorm/evidence/finish-sweep-2026-11-20/inventory-linux-mini.md` |
| win | ready, no project binding | not inventoried |
| m1 | not in the machine list; the release audit cannot reach it over Connect | not inventoried |

## Release state (`release.sh status --fetch`)

| Track | Released | Live check | Unreleased on the default branch |
|---|---|---|---|
| specweave | 3.2.2 | pass | 3 commits: #2314 pricing lists the team usage view, #2313 and #2312 test fixes |
| vskill-npm | 1.2.18 | pass | none |
| vskill-desktop | 1.0.73 | pass | none |
| platform | - | pass | none reported |
| studio (the app) | 1.0.405 | fail: m4 serves 1.0.404, M1 and M3 not readable | #779 coordinator messages between linked machines |

No app release run is in flight. The last two Release macOS runs ended green at 17:15 and 17:20 UTC.

## Open pull requests

### anton-abyzov/specwithcode (28)

Updated November 20, likely live owners (to confirm from m4):

| PR | Branch | Checks | Note |
|---|---|---|---|
| #798 | inc/1427-coordinator-messages-ui | running | 1427 |
| #797 | feat/1434-background-computer-use | running | review round 7 running on m4. Shares number 1434 with #792, different work |
| #795 | usage-by-machine | running | 1357, thread running on linux-mini |
| #792 | 1434-account-switch-cleanup | running | waits on the owner's Ship or Fix decision |
| #790 | codex/1433-gemini-cli-catalog | green | 1433 |
| #787 | fix/1428-denied-session-caches | green | 1428 |
| #785 | fix/thread-model-identity-20261120 | green | 1432 |
| #764 | 1360-packaged-skills-installer | green, draft | 1360 |

Quiet since November 15 to 19, no visible owner on M5:

| PR | Branch | Mergeable | Checks |
|---|---|---|---|
| #613 | 1339-cursor-usage-switch | unknown | green |
| #608 | copilot-signin-fresh-machine | conflicting | green |
| #606 | 1402-mcp-tab | conflicting | 2 failing |
| #568 | 1339-model-sources | conflicting | green |
| #549 | fix/release-stage-retries | unknown | green |
| #532 | 1339-fallback-regular-track | unknown | green |
| #515 | dependabot github-actions | unknown | 2 failing |
| #499 | fix/old-record-remove-once | conflicting | green |
| #489 | mobile-replies-show-modes | unknown | green |
| #475 | feat/1342-sheet-charts-on-grid | conflicting | green |
| #452 | fix/installer-signin-links-framing | conflicting | green |
| #446 | fix/codex-init-timeout-open-errors | conflicting | green |
| #443 | fix-credentials-manifest-windows-link | conflicting | green |
| #440 | fix/load-earlier-align | conflicting | green |
| #437 | reviewer-order-family-rule | unknown | green |
| #436 | fix/send-survives-socket-drop | mergeable | green |
| #434 | fix/file-editor-non-utf8 | conflicting | green |
| #432 | fix/revert-restores-exact-tree | mergeable | green |
| #410 | 1341-replies-show-modes | unknown | green |

Their green checks ran against a main that is now about 1,000 commits older, so none counts as green until its branch is updated and CI reruns.

### Other repositories

| Repository | PR | State |
|---|---|---|
| specweave | #2300 dev dependencies | green |
| specweave | #2299 glob 13.0.7 | 1 failing |
| specweave | #2298 Playwright 1.65.0 | green |
| specweave | #2275 DORA metrics | no checks, skip ci |
| vskill | #240 dev dependencies | 18 failing |
| vskill-platform | #220 prod dependencies | green |
| vskill-platform | #219 dev dependencies | 8 failing |
| vskill-platform | #218 cloudflare group | 1 failing |
| umbrella | #281 Complete team usage view increment 0898 | open |
| umbrella | #177 Release: vskill from origin, npm waits for publish run | open |

## Unpushed work on M5

### Umbrella `/Users/anton/Projects/github/specweave-umb`

- `main` is 20 commits ahead of and 213 behind `origin/main`. 19 of the 20 are not on origin: records for 1359, 1360, 1361, 1362, 1435, 1436, 1437.
- 69 uncommitted paths: 24 modified, 7 added, 38 untracked. They are other sessions' increment records (1296, 1317, 1319, 1320, 1326, 1328, 1332, 1333, 1334, 1335, 1338 to 1342, 1344, 1346 to 1349, 1353, 1360, 1434), release tooling edits (`scripts/release/release.sh`, `scripts/release/release-self-test.sh`, `.specweave/release/manifest.json`), and 28 thread reports under `.specweave/reports/threads/`. Ten of the paths also changed on origin. Several reports hold private notes (credentials moves, stream scripts) and the umbrella is public, so they are not pushed in this sweep.

### App `/Users/anton/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode`

Checked out on `1434-account-switch-cleanup` (owned by the live 1434 thread), clean, no stash. 85 local branches. Fourteen have commits on no remote:

| Branch | Commits only here | Last commit |
|---|---|---|
| 1339-copilot-usage | 1 | November 15 |
| 1341-replies-show-modes | 7 | November 14 |
| feat/1326-machine-card | 4 | November 15 |
| feat/1326-send-dialog-v2 | 6 | November 15 |
| feat/1338-project-board | 1 | November 15 |
| feat/1342-sheet-charts-on-grid | 1 | November 15 |
| fix-ports-integration | 3 | November 15 |
| fix/one-font-design-tokens | 2 | November 12 |
| pr242 | 4 | November 12 |
| release-windows-linux-retry | 3 | November 14 |
| review/pr-425 | 1 | November 14 |
| verify/ports-snapshot-1, -2, -3 | 1 each | November 14 to 15 |

Local `main` also carries 3 commits for 1360 that are on no remote under that name (the same work is PR #764 as a draft).

### Other repositories on M5

| Repository | Finding |
|---|---|
| specweave | `develop` clean, 37 behind. Local-only branches `docs/founders-300` (1 commit, November 1) and `fix/tutorial-step-code-wrap` (2 commits, October 25) |
| specweave-status | on `codex/1196-status-evidence`, pushed. Local-only branch `status-by-product` (1 commit, November 1) |
| vskill | `main` 2 behind, only `.DS_Store` files untracked |
| vskill-platform | `main` 27 behind, 2 generated files modified (`src/lib/generated-counts.ts`, `src/lib/generated-plugin-catalog.ts`) |

### Scratch on M5

`~/.specwithcode/m4/scratch` (8.6 GB, 27 folders carried from m4 naming, including `2026-11-20-1434-round-5` to `-13` owned by the live 1434 thread), `~/.specwithcode/m5/scratch` (5 folders from today), `~/.specwithcode/scratch` (553 MB). No git worktrees on M5 in any repository.

## Increments (read from umbrella `origin/main`)

755 increments: 603 completed, 26 abandoned, 120 active, 3 planned, 3 backlog.

### Every task recorded done, not closed (8)

| Increment | Title | Known blocker |
|---|---|---|
| 1073 | Show only active projects in pickers | review found bugs (sweep of November 12 to 15) |
| 1141 | Full Meta and Gemini provider support | review found bugs |
| 1193 | Chrome extension uploads files | review found bugs; needs device evidence |
| 1301 | Stale limit blocker | review found bugs |
| 1312 | Restart and update dialogs list running threads | one review on file, no verify result |
| 1315 | Aide is its own space | no verify, no review |
| 1320 | Reports stay in SpecWithCode | one review on file; newer verify result uncommitted on M5 |
| 1365 | Copy started from another machine's window | no verify, no review |

### One or two tasks left (58)

0927, 0967, 0970, 0979, 0987, 1005, 1007, 1009, 1025, 1029, 1034, 1036, 1047, 1072, 1074, 1076, 1078, 1079, 1081, 1086, 1088, 1091, 1095, 1097, 1101, 1102, 1103, 1108, 1112, 1118, 1138, 1142, 1149, 1150, 1151, 1153, 1154, 1156, 1157, 1160, 1162, 1165, 1174, 1184, 1186, 1188, 1189, 1190, 1192, 1207, 1213, 1241, 1258, 1293, 1306, 1308, 1309, 1335.

Most of these last moved between October 23 and November 3. The open task is usually the closing one (verify, review, release proof) or a claim left by a thread that ended.

### Further from done (57)

Includes increments whose work shipped but whose tasks were never recorded on origin (for example 1399 skills, 1424 chats without a project, 1326, 1319, 1328, 1342), the long-running 1390 (21 of 24) and 1427 (3 of 9, PR #798 open), and plans not started.

### Live owners, left alone

| Item | Owner | Waits on |
|---|---|---|
| 1434 account switch, PR #792 | its thread | the owner's Ship or Fix decision |
| 1434 background computer use, PR #797 | m4 thread, review round 7 running | review |
| 1435, 1436, 1437 | planned today, not built | build |
| 1357 usage by machine, PR #795 | linux-mini thread, running | build |
| 1390, 1427 | m4 thread "Rethink copies, sync and handing off work", running | build and review |
| 1360 skills installer, PR #764 draft | m4 thread "Skills installer branch publication" | to confirm |

## Plan

1. Push every local-only branch on M5 so nothing lives on one disk. Open a PR for the umbrella's 19 record commits.
2. Request an app release for #779.
3. After the machine workers report: update and merge the quiet PRs that turn green on current main, per owner map; route the rest to owners.
4. Close increments only where every task is done, the code is released, verify is green and a fresh review passes. M5 cannot run a strict close (no pnpm, system Python), so closes run on m4 or linux-mini.
5. Remove scratch copies and branches only where the PR merged or closed and no thread is bound.

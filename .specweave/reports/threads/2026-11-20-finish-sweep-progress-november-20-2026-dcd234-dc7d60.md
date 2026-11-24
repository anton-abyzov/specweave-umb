---
title: "Finish sweep progress, November 20, 2026"
thread: "thread:delegated-task:command%3Amcp%3A5203f9f6-1c70-4578-a8a9-fc4f6def2ca7%3Adelegate-task%3Acc1de104-0ef7-49db-940a-31d8f6471a86"
threadTitle: "Finish almost-done work across all machines"
savedAt: "2026-11-20T19:40:12.019Z"
date: November 20, 2026
machine: M5
status: in progress
---

# Finish sweep progress, November 20, 2026

Follows the inventory in `/Users/anton/Projects/github/specweave-umb/.specweave/reports/threads/2026-11-20-finish-sweep-inventory-november-20-2026-dcd234-66ec35.md`. This file records what the machine inventories added, what is done, and who holds the rest.

## What the machine inventories added

### m4

- 396 git copies. 302 items hold something worth keeping; 129 more are fixture-only copies.
- Umbrella checkout on `fix/coordinator-delegates-work`: 57 commits on no remote, 261 uncommitted paths.
- Branches with commits on no remote and no merged PR: 10 umbrella branches or worktrees and 15 app refs in the shared store (list in the m4 worker's reply).
- 48 clean checkouts whose PR merged or closed at the checked-out commit: 25 bound to completed or archived threads (90.7 GiB), 22 bound to failed, interrupted or cancelled threads (93.4 GiB), 1 unbound primary checkout. None is unbound, so none was removed. The owner is asked.
- m4 runs 1.0.401 with 1.0.405 staged, waiting for a quiet moment.
- `/Users/antonabyzov/Projects/sw-easychamp` holds 27 unpushed commits and 1,087 uncommitted paths. It is another project and outside this sweep.

### linux-mini

- Umbrella `/srv/work/github/specweave-umb`: 5 unpushed commits (increments numbered 1316 and 1317 that collide with other increments on origin), untracked increment folders 1351, 1353, 1356, 1357 absent from every remote, four more that may differ (1320, 1352, 1354, 1355), 2 stashes from October 29.
- 28 folders safe to remove (about 48 GiB): 21 worktrees, 6 scratch or verify clones, 1 with four orphaned test processes (kept).
- Service runs 1.0.401 while the desktop app is 1.0.405; a 1.0.349 launcher is still alive.

### Not inventoried

win (no copy of this project) and m1 (not in the machine list; the release audit cannot reach it).

## Done

| What | Result |
|---|---|
| M5 local-only branches | 17 pushed as `keep/m5-2026-11-20/<branch>`: 14 in anton-abyzov/specwithcode, 2 in anton-abyzov/specweave, 1 in anton-abyzov/specweave-status |
| Umbrella records from M5 (1359 to 1362, 1435 to 1437) | PR #283 merged as `97a1267ea` |
| specweave #2300, #2298 (dependencies) | merged |
| vskill-platform #220 (dependencies) | merged |
| specweave | 3.2.3 released and verified (m4 worker) |
| vskill-platform | deployed and verified (m4 worker) |
| App #790 (1433 Gemini CLI catalog) | merged at reviewed head `3ed57025` as `dd577da11` |
| App #785 (1432 pending model choices) | merged at reviewed head `d90eb548` as `5e374f8d2` |
| App #549, #436, #432 | branches updated onto current main; CI rerun |
| App release | requested, run 44800952403 in progress; it carries #779, #790, #785 if they are on main when it starts, else the queued run 44802008802 does |

## Running

| Lane | Machine | Thread | Scope |
|---|---|---|---|
| T3 port fixes | linux-mini | Finish the T3 port fix pull requests | #432, #436, #446, #434, #443, #452; records in 1347, 1348 |
| Model tracks | m4 | Finish the model tracks and machine alias pull requests | #532, #568, #613, #437, #499 |
| UI | m4 | Finish the replies, sheets, integrations and Copilot sign-in pull requests | #410, #489, #440, #475, #606, #608, #515 |
| Increment closes | linux-mini | Close finished increments in the umbrella | 8 with every task done, 58 with one or two left, 10 shipped without records |
| m4 durability | m4 | Unfinished work inventory on m4 | push unpublished branches and uncommitted increment records to `keep/m4-2026-11-20/` |
| linux-mini durability and cleanup | linux-mini | Unfinished work inventory on linux-mini | push keep refs, remove the 27 safe folders |

## Left to live owners

M5 may read but not message threads that belong to m4's or linux-mini's own coordinator, so these need a word from the M5 coordinator to the m4 coordinator.

| Item | Owner thread (m4 unless noted) | Next step |
|---|---|---|
| #790 merged, 1433 | Gemini CLI model availability | record tasks, close 1433 |
| #785 merged, 1432 | Thread provider and model identity | record tasks, close 1432 |
| #787, 1428 | Device approval popup and multiple phones | review at head `9997f601`, merge, close |
| #549 and umbrella #177 | Request and verify app releases | review and merge, or close as covered |
| #798, 1427 | Rethink copies, sync and handing off work | running; last verdict "fix first" |
| #797, 1434 background computer use | Computer use alongside human input | review round 8 running |
| #795, 1357 | Subscription usage by machine charts (linux-mini) | running |
| #764, 1360 | Skills installer branch publication; M5 keeps verification and closure | draft |
| umbrella #281, 0898 | Team usage view (0898) | open |
| 1435, 1436, 1437 | planned on M5 | build |

## Not acted on

- M5 umbrella: 69 uncommitted paths left as they are. `main` is still behind `origin/main`; a pull needs the other sessions' files settled first.
- Dependency PRs with failing checks: specweave #2299, vskill #240, vskill-platform #219 and #218.
- specweave #2275 (DORA metrics, skip ci).
- M5 scratch folders `~/.specwithcode/m4/scratch/2026-11-20-1434-round-*`: owned by the 1434 thread.

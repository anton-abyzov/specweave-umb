FIX FIRST
Verdict: fix first

## Round 2 disposition

Reviewed `anton-abyzov/specwithcode#653`, T-07, at `160f4c73552c3df04a8d0eca93a55c773e0b9743`. Fresh reviewer: GPT-6.2 Astra. All four prior blockers are fixed as reported. One new high-severity case remains: the result title respects an unread final status, but the repository row does not.

Source citations below are relative to `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-umb/1390-phase-2-sync-dialog/repositories/anton-abyzov/specwithcode`; component filenames in the table are under `apps/web/src/components/studio/`.

| Round 2 | Disposition and head evidence | Would the regression fail without the fix? |
|---|---|---|
| E-01: lost destination receipt | **Fixed.** `projectSyncDialog.logic.ts:1257–1273` treats `unreachable` inside a successful batch as unknown, keeps its detail, and does not change confirmed siblings. | Yes. `ProjectSyncDialog.test.tsx:608–650` requires `["unknown", "sent"]` and rejects “Stays.” The old renderer returned `stays`. |
| E-02: dispatch after close or regrant | **Fixed.** `ProjectSyncDialog.tsx:662–666,713–720,746–750,804–811` checks lifetime and generation before dispatching more work; a grant loss permanently stops that run. | Yes. `ProjectSyncDialog.test.tsx:561–606` releases an outstanding call after unmount or deny/regrant and checks subsequent calls. It also checks that a closed fetch does not start inventory. The old loop continued. |
| E-03: Add resumes the wrong move | **Fixed.** `ProjectMachineHandoff.tsx:1049–1057,1223–1231` preserves the old pointer and offers recovery separately. `useCopyDraft.ts:95–110` excludes unfinished pointers from fresh Add. | Yes. `HandoffFolderCopy.add.test.tsx:98–113` mounts the real child with a pending move and checks non-resumption and pointer preservation, with ordinary recovery as a control. `ProjectMachineHandoff.menu.test.tsx:344` covers the parent. |
| E-04: project title lacks evidence for every displayed path | **Fixed.** `ProjectSyncDialog.tsx:854–858` supplies every displayed path; `projectSyncDialog.logic.ts:580–601` requires unique covering path sets and matching readable, clean checkouts. | Yes. `ProjectSyncDialog.test.tsx:653–690` exercises omission on both machines and a duplicate on one. The old predicate accepted both cases. These tests assert the **title**, not the individual row in F-01. |

The test counterfactuals above are based on the old branches and the new assertions, not a local revert or mutation run.

## Blocking finding

**F-01 [high] An explicitly unread final checkout still gets a green “Up to date” check.** `apps/web/src/components/studio/ProjectSyncDialog.tsx:833–857` receives both final statuses but uses them only for `proven`. It constructs the rows without them. On an unrequested checkout, `apps/web/src/components/studio/projectSyncDialog.logic.ts:1026–1031` copies the plan sentence and its done flag; `apps/web/src/components/studio/ProjectSyncDialog.tsx:175–182` renders that flag as a green check.

**Scenario:** The nested checkout `tools/cli` is level at fetch time. Sync sends a ticked extra. Before the final status, Git can no longer read `tools/cli` on A. The server explicitly returns `{path:"tools/cli", branch:null, head:null, clean:false, unread:true}` (`apps/server/src/fleet/projectSyncFacts.ts:106–115`). This is not a missing reply or an inference about a concurrent edit. The latest answer says the checkout could not be read. A read-only probe of the head's actual `syncPlan`, `syncResultRows` and `statusesProveInSync` returned `proven:false` but A's cell was `branch:"main"`, `sentence:"Up to date"`, `done:true`, with no detail. AC-11 promise 4 forbids that claim.

**Minimal fix:** Carry explicitly unread `(side, path)` entries into result-row construction. For this no-move row, render “Could not be read. Not moved,” remove the stale branch, and set `done:false`. Where a run independently verified a move, preserve that historical receipt and distinguish it from unread current state. Add a dialog regression with a readable plan followed by an unread status; assert the affected cell, not just the heading, and leave the other machine's cell unchanged.

## Follow-up (non-blocking)

1. **AC-04 menu comparison:** `apps/web/src/studio/machineRowState.ts:76–94` counts the unread status above as a difference. Calling `machineSyncFact` with one readable root and one explicitly unread root returned “1 of 1 repositories differ.” Say the comparison could not be read instead of counting a difference. This does not claim a move or completion.
2. **T-18, already assigned:** `apps/web/src/components/studio/ProjectMoveOptions.tsx:338` still offers “Continue the coordinator here.” Its tests, folder-copy fixture and guide belong to T-18, not this gate. No E-05 through E-10 finding was reopened.

## What I verified

- Compared the previous head `f523f6cd03991e9fd062f2b8abb7d203143870b8` with its rebased counterpart `c34f4b5b0` and reviewed the branch-owned web delta from there. Did not attribute intervening main changes to T-07.
- **AC-10/11, move authority:** The merged wire contract puts `guardedFastForward` and `fetchId` on `projectSync.fetch`, **not** `projectSync.status` (`packages/contracts/src/projectSync.ts:178–201`). `apps/web/src/components/studio/projectSyncDialog.logic.ts:466–488,534–539,654–680` requires both fields from the same machine before constructing a move. Otherwise the proposed move becomes fetch-only with “Needs update.” `apps/web/src/components/studio/ProjectSyncDialog.tsx:660–666,754–770` passes that side's ID to inventory and run. The window neither chooses a new commit nor issues a Git write or a second origin fetch at run time. AC-11 promises 1–3 and 6 remain server-enforced; none of exclusions 1–5 was treated as a UI obligation.
- **AC-11 promises 4–5, AC-12/16:** `movedUnverified` takes precedence over reason and count; unread fetch facts yield a held row. Inventory `unreadDetail` suppresses placeholder counts; `onlyHereUnknown` produces an untickable unknown line. See `apps/web/src/components/studio/projectSyncDialog.logic.ts:252–276,297–311,743–775,990–1008`. `apps/web/src/components/studio/ProjectSyncDialog.test.tsx:917–1053` covers side-bound IDs, missing capability or ID, unverified moves, unread facts, and unknown inventory. The hole is specifically the later status reply. Compare all files and Check again remain available (`apps/web/src/components/studio/ProjectSyncDialog.tsx:947,1115–1124`).
- **AC-15 and retired assertions:** Inspected fresh Add versus recovery (E-03). The branch restored the Extra coordinator test block to main's wording in `150898d4a`; AC-05 was not used as a gate.
- **Evidence:** `/Users/antonabyzov/.specwithcode/m4/scratch/2026-11-18-1390-phase-2/red/red-sync-contract.txt` records seven pre-fix failures. Exact-head [Checks run 44532471422](https://github.com/anton-abyzov/specwithcode/actions/runs/44532471422) passed both web shards, typecheck, and the PR gate. The existing fixture log `/Users/antonabyzov/.specwithcode/m4/evidence/1390-phase-2/round8/verify-project-sync.log` reports 152 shots, no layout or language failures. I ran the two read-only function probes above, not a build or full suite. No code changes, installs, commits, PR comments or live database access.

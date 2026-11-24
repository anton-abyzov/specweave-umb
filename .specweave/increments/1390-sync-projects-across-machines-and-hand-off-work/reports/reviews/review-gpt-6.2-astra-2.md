<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=5fd289f7c8e198384173d6fd7c7e3e9e5ab62441 head=ba22422cf92d6218d5d81b80f95a3d48463fce1b at=2026-11-19T04:04:42.882Z -->
# Review: 1390 Phase 2 Sync dialog and Add to another machine
Verdict: fix first

Reviewer context: independent session. Reviewed `ba22422cf92d6218d5d81b80f95a3d48463fce1b` against `5fd289f7c8e198384173d6fd7c7e3e9e5ab62441` in `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-umb/1390-phase-2-sync-dialog/repositories/anton-abyzov/specwithcode`. Source citations below are relative to that checkout.

## D-01 [high] `apps/web/src/components/studio/ProjectSyncDialog.tsx:475` A missing receipt is reported as a failed transfer

If the receiver creates a branch and the connection drops before the reply, the window says the extras “were not sent.” The same happens when a newer literal makes a completed batch's reply undecodable. Lines 670–678 store only a failure, even for the batch already dispatched. The person cannot tell which items to check before trying again; a new send gets a new operation ID. Fix: keep the item identities and distinguish confirmed receipts, dispatched items with unknown outcomes, and later batches never attempted. For the uncertain batch say that it may have arrived and to check the destination.

## D-02 [high] `apps/web/src/components/studio/ProjectSyncDialog.tsx:975` An open plan outlives the grant that enabled it

Open a plan with both machines writable, then let the target's write grant change to read-only while the source stays writable. The menu hook recalculates `targets[].blocked`, but the dialog reads only `.machine` at line 555. Sync remains keyboard-activatable. Lines 637–645 can move the still-writable source checkout even as the target rejects its own call; if only the source needs moving, the target need not receive a run at all. The RPC guard protects each called machine, not the two-machine decision. Fix: pass the shown machine's live block too; invalidate the plan and its selections when either endpoint becomes blocked or changes identity, and gate work at dispatch, including subsequent extras batches. Test a grant change after the plan is displayed.

## D-03 [high] `apps/web/src/components/studio/projectSyncDialog.logic.ts:419` The plan ignores the newer machine's unread-state fact

The fetch reply contains repository facts, not planned steps. This window runs its own `planProjectSync` on them. Its contract does not read `stateUnread`, and its planner sees a zero uncommitted count as clean. For the specified newer reply with `stateUnread: true`, one commit behind, and no competing work, the window offers “Moves forward 1 commit.” When level it can say “Up to date.” The newer server will hold the checkout on recheck; the plan is still false. The zero-count `stepLine` test starts *after* planning and does not cover this wire path. Fix: accept the optional boolean in this head's compatible fetch schema and honor it when producing the plan; test decode → plan for present and absent facts.

## D-04 [high] `apps/web/src/components/studio/projectSyncDialog.logic.ts:476` “In sync” is inferred from completed actions, not equal checkouts

If one machine is on a clean `release` branch and the nested repository is missing on the other, a successful clone can check out the remote's default `main` branch at a different commit. The source cell is done (“Up to date”), the destination cell is done (“Cloned”), and there need be no extras or partial scan. The title now says the machines are in sync despite the displayed branches and different heads. Fast-forwarding different upstreams can produce the same error. Fix: use the neutral “Sync finished” unless fresh status from both sides establishes identical heads and clean trees for every path. Test the default-branch clone, not just two identical fixture heads.

## D-05 [medium] `apps/web/src/components/studio/projectSyncDialog.logic.ts:821` A result can name a branch the machine just said it is not on

Plan a fast-forward on `main`; detach the checkout before the run. The server re-reads it and returns `reason: "detached", branch: null`. The fallback restores `main` from the plan above “Not on a branch.” The no-reply path at lines 826–835 similarly labels a requested clone “Not there” even if it succeeded before the reply was lost. Fix: use the returned nullable branch as authoritative; represent unknown presence/branch separately from a confirmed missing checkout.

## D-06 [medium] `apps/web/src/components/studio/projectSyncDialog.logic.ts:932` The checked-out collision names the wrong branch

The source result's `branch` is the requested source branch. The receiver tests whether the *namespaced destination* branch is checked out (`apps/server/src/handoff/ExtrasReceiver.ts:223–228`). For `fix/menu` it is `swc/from-…/fix/menu`, not necessarily `fix/menu`, that is in use. The test asserts the incorrect source name. Fix: say the usual destination branch is checked out and name only the confirmed `arrivedAs`; do not infer the destination ref from the request or the window's machine nickname.

The plan has the same naming assumption at `apps/web/src/components/studio/projectSyncDialog.logic.ts:623`: it promises an exact ref from the display name. The sender supplies its own machine label (`apps/server/src/fleet/ProjectSyncExtras.ts:521`); the receiver makes it ref-safe and can append a suffix. A display nickname need not be that label. Describe the branch family before sending; show the exact ref from the receipt after sending.

## D-07 [medium] `apps/web/src/components/studio/useProjectSyncMenu.ts:97` A stale comparison is presented as current

Let both statuses expire, change the shown checkout, then reopen the menu. If the shown machine's read fails but the peer's succeeds, the store retains the shown machine's old status and marks it stale. The row compares both statuses, but checks only the peer's age and failure flag. It can say “Same as” without qualifying when that was last known. Fix: qualify the comparison using the older contributing sample whenever either side is stale, or say it could not be checked. Test a failed refresh on the shown side with a successful one on the peer.

## D-08 [medium] `apps/web/src/components/studio/useProjectSyncMenu.ts:140` A separate project is offered as a destination for extras it cannot receive

Two machines can independently register the same repository and appear together in the repository-grouped menu as “Separate project.” The target filter checks only folder, key and machine; it does not check membership. Fetch and Run address each selected registration, but the extras receiver requires a reciprocal project link and refuses the unlinked pair (`apps/server/src/handoff/ExtrasReceiver.ts:289–309`). A person can select extras, press Sync and move Git checkouts before finding out the requested transfer was unavailable from the outset. Fix: offer only linked project members for project Sync, or explicitly disable extras for an unlinked pair and offer Link first. This finding is a confirmed refusal, not a claim that data landed in the wrong folder.

## D-09 [medium] `apps/web/src/components/studio/projectSyncDialog.logic.ts:973` Extra refusals discard the peer's explanation

The shipped sender returns the peer's message in `detail` for both `needs-update` and `unreachable` (`apps/server/src/fleet/ProjectSyncExtras.ts:417,470–481`). The renderer computes that detail, then returns a fixed sentence for both reasons; neither the sentence nor its facts include it. A person sees only “could not be reached” even when the peer call supplied a more specific diagnostic. Fix: after the localized summary, show nonempty, nonduplicate detail once. This requires no new reason code or translation of raw server text.

## D-10 [medium] `apps/web/src/components/studio/MachineHandoffDialog.tsx:291` “Compare all files…” can declare the machines in sync after a partial copy

The measured-copy path selects its “in sync” title from the done stage and machine name. The done-stage notification carries no equality or check outcome (`apps/web/src/components/studio/handoffFolderCopyRules.ts:150–155`). The body explicitly supports an unstable source or failed check and advises syncing again. The heading and warning can therefore contradict each other. Fix: title this result “Copy finished” (or “Sync finished”) and let the existing warnings describe what remains. Test a done copy with a changed source file.

## D-11 [medium] `apps/web/src/components/studio/OrchestratorSwitcher.tsx:310` Closing Add loses the reason the new project was not linked

For example, conflicting notes produce a specific refusal. The done panel displays it, but only successful linking is saved; the refusal stays in component state (`apps/web/src/components/studio/useCopyLink.ts:48–72`). The separate-project row has only a generic explanation that the machine added the repository on its own. It neither names the conflict nor distinguishes a failed Add from an independent registration, contrary to AC-15. Fix: retain the outcome keyed to the exact source and destination projects, show its reason beside the existing Link action, and clear it after successful linking. Test closing Add and reopening the machine menu.

## D-12 [medium] `apps/web/src/components/studio/ProjectMachineHandoff.tsx:1039` Add can reopen a coordinator move instead

With an unfinished Git handoff saved for one machine, choosing Add for a different, missing machine turns off Add's filter, sets the intent to `move` and restores the handoff's target. The menu test explicitly expects Add to open the unfiltered handoff. The click itself does not move the coordinator, but it does not open the requested copy-only workflow. Fix: leave the recovery pointer intact and offer a distinctly labeled Resume action. If recovery must finish before Add, explain that without opening the move as if it were Add.

## D-13 [low] `apps/web/src/components/studio/HandoffCopyDone.tsx:137` Localized copy and link messages contain client-generated English

For example, `{problem}` can be “some files changed on … while copying” (`apps/web/src/components/studio/handoffCopyNotices.ts:224`); `{reason}` at line 251 can be “Project notes differ on …” (`apps/web/src/studio/projectLink.ts:703`). Translating the enclosing template leaves mixed-language output. Fix: pass translation keys and values for local reasons; preserve verbatim text only when supplied by a machine. Not a merge blocker by itself.

## D-14 [low] `apps/web/src/components/studio/ProjectSyncDialog.tsx:834` Disabled picker rows repeat the machine name

The row renders the label and then the full menu reason, for example “m1 / m1: Needs update · 1.4.2.” Fix: keep the full reason for the standalone menu action; use the reason without its subject under an already-labeled picker row.

## Answers to the five open points

1. **English slots:** nonblocking localization defect D-13. Raw server details may wait; the two client-generated examples are not part of that deferral.
2. **Real menu wiring:** yes, verified by reading. Opening the production menu calls `refreshSyncStatus` for open machines; the adapter addresses the selected environment and project and uses `projectSyncStatus`, guarded by `filesystem:read`. Fetch, Run and Send Extras require `source-control:write`; Inventory requires `orchestration:operate`. Neither the fixture nor this review is a live integration run. Correct routing does not fix D-02 or D-07.
3. **Connecting machine:** fine while the list settles. Loading is bounded; a machine still connecting is not an actionable destination. A fresh Add offers the Git download for a remote-backed project and only whole-folder copy without a remote. The pending-handoff exception is D-12, not a loading defect.
4. **Repeated picker name:** cosmetic, nonblocking; D-14.
5. **Folder-copy fixture rename:** no semantic risk found in the final reformat. It rewraps the same assertion; the label and path selectors inspected agree with the renamed fixture. I did not rerun it.

## Evidence and bounds

Read the accepted spec, base contract, exact diff, production RPC call sites and receiving Git code; compared tests and saved fixture screens against them. All eight Sync catalogs had the same 180 keys and matching placeholder names. The unreadable zero-count result itself renders its detail once, not “0 uncommitted files”; D-03 is the earlier fetch-to-plan path. Rechecking clears ordinary and override ticks. The name-flagged secret has no selectable override on the Sync path. The workspace remounts on the physical environment/project key; I found no cross-project cache-key substitution on a view switch. No test suite or fixture was run and no live transfer was attempted.

Saved visual evidence: [failed extras, 390 px](/Users/antonabyzov/.specwithcode/m4/evidence/1390-phase-2/round4/project-sync/result-extras-not-sent-light-390.png) and [machine picker, 390 px](/Users/antonabyzov/.specwithcode/m4/evidence/1390-phase-2/round4/project-sync/picker-dark-390.png).

**Deferred, not findings:** replacing canonical English matching with structured detail codes; translating new server sentences; included-commit counts and size before sending; sealed name-flagged secrets and newer-side indications; fuller scan-limit wording; “Commit on {source}…”. The accepted extras heading and existing “What comes along” defaults were not treated as defects.

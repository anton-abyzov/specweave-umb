# Switching the Connect account on a machine drops the previous account's machines and chats

## Problem

On November 20, 2026, Anton reported from Elena's M2 (window `SYN1-MAC-AABYZOVEXT`) that after the window's SpecWithCode Connect account changed from his to her designer account, the app still showed his machines. The photo was read locally only and was not uploaded or stored in the repository.

What the photo shows:

- The sidebar account button reads "Elena Abyzova".
- Projects > "On other machines" lists AI Resets, EasyChamp, First feature and fortnite-3js tagged m4, and firstproject tagged M5.
- Chats lists Anton's threads tagged m4 and M5 from today, yesterday and earlier, and "PercyAnton · m4".
- The open thread "AI Resets" runs on m4's coordinator with Full access, under the banner "m4 isn't answering. Retrying by itself", and the Threads panel reads "m4 isn't answering — the thread list may be incomplete. Cached threads may be out of date. Last answered 1m ago".
- A macOS prompt asks whether "SpecWithCode.app" may access data from other apps. It is unrelated.

What the code says (origin/main 73f3e642b):

- "m4 isn't answering" renders only for a machine still saved in the window's connection catalog (`apps/web/src/components/studio/ProjectExecutionHistory.tsx`). m4 was therefore still saved after the switch.
- On a switch, `managedAuth.tsx` removes only Connect (relay) routes, through `removeRelayEnvironments`. Routes learned through Connect go with them.
- A direct, LAN or Tailscale route the window paired keeps the machine. That includes fleet auto-pairing from the machine's own management token. The route carries a bearer credential with person access to that machine, and the cached shell and thread history stay in IndexedDB with it. A test asserted this survival (`registry.test.ts`, "keeps an environment that still has a LAN route").
- The catalog, the cache and the fleet file record no account.

Two further defects were confirmed by failing synthetic fixtures:

- A Connect route save that started under the previous account and finished after the cleanup was kept.
- One machine that failed to be removed interrupted the removal of the others.

What persists, and where:

| Kind | Where | After this increment |
|---|---|---|
| Machine names and nicknames, last-seen time | window local storage, server project members | stay (labels only) |
| Local chat history of a remote machine | window IndexedDB per machine | cleared when that machine is dropped |
| Window access to a remote machine (saved route and credential) | window connection catalog | dropped on a switch when the previous account saved it |
| Remote permission on the remote machine (approved device, paired session, worker grant) | the remote machine | unchanged; ended only on that machine (Settings > Machines) |

## Scope

In: the web and desktop window's connection catalog on a Connect account switch; the registry's Connect route removal; synthetic fixtures for a switch, late answers and a restart.

Out: revoking sessions or devices on the remote machines; the server fleet file and worker grants; project folders and copies on any machine; a sign-out without a new account (only Connect routes go, as today); clearing cached state when a host refuses access (PR #787, increment 1428/1431 on m4).

## Acceptance Criteria

- [ ] AC-01: When a window signs in as account B after account A, every machine the window saved while A was signed in is removed from the window, along with its routes, saved credential and cached projects and chats. Machines saved before this release count as A's. Machines saved while signed out, or by B, stay.
- [ ] AC-02: Signing out and later signing in as another account counts as a switch. Signing back in as the same account removes nothing.
- [ ] AC-03: A Connect route save that started before a switch's cleanup does not survive it, and one machine that cannot be removed does not stop the others.
- [ ] AC-04: A cleanup cut short by a failure or a restart is finished on the next start. Nothing runs before Connect has settled or before the saved list has loaded, and the window's own machine is never touched.
- [ ] AC-05: Removal touches only the window's saved connection and its cache. No project folder and no machine's own data is deleted. Dropped machines are skipped by automatic fleet pairing.

## Approach

1. `packages/client-runtime/src/connection/registry.ts`: a Connect route epoch, bumped by `removeRelayEnvironments`. A Connect save started in an older epoch is refused, or undone when it finishes. Each removal runs on its own, and the first failure is reported after all have run.
2. `packages/client-runtime/src/connection/accountOwners.ts`: a pure planner over the owner of each saved machine (account id, `""` for signed out, `"?"` for unknown) and the last settled account. The registry applies it (`setAccount`) under each machine's lease and an account lock, re-checking the account before any removal; a save started for an account that left (`forAccount`, captured before the pairing goes out) is refused under the lease, and every successful save records the current account as owner. A save is noted before the catalog write and its owner recorded after it; a save the app stopped in the middle of is settled at the next plan by whether its new route reached the catalog, and an owner record that cannot be stored stops the save (revised after GPT-6.2 Sol round 7). Owed removals keep the previous account recorded, so a restart finishes the switch. Revised after GPT-6.2 Sol round 4.
3. `apps/web/src/connection/platform.ts` keeps the owners in local storage (`apps/web/src/cloud/connectMachineOwners.ts`); `apps/web/src/cloud/ConnectMachineOwnersSync.tsx`, mounted in `ManagedRelayAuthProvider`, hands the settled account to the registry. Forgetting sets the fleet skip first, then removes the machine on this window only.
4. The registry tests are split into a harness, core tests and routes tests, because the file was over the 1,500-line limit.

Rejected alternatives:

- An account field in the catalog document: this needs a schema change to the desktop catalog file.
- Revoking the remote session from the window before dropping it: this is remote auth, not asked for.

Risks:

- Owners are kept in memory for the session and in local storage across restarts; a refused write is retried with the next change (revised after GPT-6.2 Sol round 8). A save's note carries a fingerprint of the exact routes it writes, so a save the app stopped in the middle of is settled by whether the catalog holds exactly those routes; a save that takes a machine from another account clears that account's cached projects, chats and drafts before it is written, so settling an identical re-save as the new account's exposes nothing (revised after GPT-6.2 Sol round 9). If a stored target ever read back differently, a landed save would settle as never landed and keep the earlier owner, the safe direction. A save of a machine the saving account's switch still owes a removal (another account's, whose removal failed or has not run yet) first finishes that removal, clearing the other account's cached projects, chats and drafts and its saved entry, then adds the machine as new; if the save then fails, the machine is gone as the switch intended (AC-01). No save takes over another account's entry, so recovery never has to tell an unwritten save from a landed one over the same routes. Saves cut short are settled only by the session's first plan, when the loaded entries match the catalog; a note left later waits for the next start (revised after GPT-6.2 Sol round 12). A save while signed out keeps the machine's existing owner; only a machine first added while signed out is marked signed-out (Sol round 11). The fingerprint covers routes only: a profile- or credential-only re-save that is cut short settles by its routes (revised after GPT-6.2 Sol round 10).
- A stale fleet list that still names a machine of A never saved on this window can pair it under B, until the list refreshes.
- On an account switch, a machine's cached projects and chats are cleared before its saved entry is removed. If that clear fails, or the app stops in between, the machine stays saved and owed, and the next start removes it again (revised after GPT-6.2 Sol round 6). A removal by hand keeps the earlier order, where a refused cache delete is logged and left until the machine is added again.
- Dropping uses a window-only removal (`keepRemote`): a managed SSH server on the other host keeps running, and its local tunnel ends when the app quits.
- On an upgraded window already signed in as B, machines saved earlier stay as unknown until the next switch. Elena's M2 keeps m4 and M5 until then, unless they are removed by hand.

Known limits at ship (GPT-6.2 Sol rounds 1 to 13): a save cut short by a defect (not a typed failure or an interruption) mid-session is settled only at the next start, and a switch before then plans that machine from its earlier owner; a catalog write that fails after the switch's removal leaves the machine removed (D-04); cached data whose clear storage refuses stays until the next removal of that machine.

## Decisions

### Asked
- D-01 After a switch, machines the window paired under the previous account: drop, keep, or hide only the chats → drop them on a switch, but never delete a folder with project data, in case there was a copy or sync (Anton, November 20, 2026).
- D-04 Same-route takeover after failed review rounds 11 and 12 → "Fix it first", then "Finish the removal first": a save of a machine another account still owns finishes the switch's removal, then saves it as new; if that save fails, the machine is gone as the switch intended (Anton, November 20, 2026).
- D-05 Ship after round 13's fixes without a fourteenth review round → "Merge and release" (Anton, November 20, 2026).
### Defaulted (change any before sw-do)
- D-02 A sign-out without a new account keeps today's rule (only Connect routes go) → default, reversible.
- D-03 Machines saved before this release count as the previous account's on the next switch, and are adopted as the signed-in account's when that account lists them on Connect → default.
### Open
- none

- D-90 Added from 1474 (November 25, 2026): upstream `dbee5a0af0` fixes the same file: an account switch whose route removal fails still activates the next account (`apps/web/src/cloud/managedAuth.tsx:111`), and `314a11498e` an offline launch that reads as signed out removes every Connect machine (`managedAuth.tsx:127`). Lane notes: 1474 `reports/lanes/d1-web.md`.

## Review

Reviewer order: Gemini 4 Neon (Copilot Enterprise), then GPT-6.2 Sol.

## Tasks

### T-01 Late Connect saves and partial failures on a switch
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/registry.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/registry.accountSwitch.test.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/registry.test.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/registry.routes.test.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/registry.testHarness.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run packages/client-runtime/src/connection/registry

### T-02 Drop the previous account's saved machines on a switch
- AC: AC-01, AC-02, AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/cloud/connectMachineOwners.ts, repositories/anton-abyzov/specwithcode/apps/web/src/cloud/connectMachineOwners.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/cloud/ConnectMachineOwnersSync.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/cloud/ConnectMachineOwnersSync.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/cloud/managedAuth.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/cloud/managedAuth.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/cloud/managedAuth.accountState.test.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/cloud/

### T-03 Review, release and verify the published build
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: .specweave/increments/1434-switching-the-connect-account-on-a-machine-drops-the-previous-accounts-machines-and-chats/reports/ | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run packages/client-runtime/src/connection/registry apps/web/src/cloud/

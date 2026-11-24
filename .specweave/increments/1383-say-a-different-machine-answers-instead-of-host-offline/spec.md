# Say a different machine answers instead of Host offline

## Problem

A saved machine whose address now answers as a different SpecWithCode is shown as plainly offline. Diagnosed on the M4 on November 17, 2026: linux-mini's saved fleet record (id `ministorm`) gets fleet status `identity-mismatch`. Its Connect tunnel returns Cloudflare 1033 and its Tailscale address answers HTTP 200 with a different environmentId (`apps/server/src/studioFleet.ts` `checkIdentity`, `apps/server/src/fleet/fleetTransport.ts`).

The server knows this. `studio_machine_list` says `identity_mismatch` and Settings > Machines handles it (`apps/web/src/components/settings/machinesSettings.logic.ts`). But the thread list says "Host offline", and the chat banner and composer say "linux-mini is offline · Retrying by itself". That is false: retrying never fixes it, the owner has to act in Settings > Machines.

Same cause, second symptom: `packages/client-runtime/src/state/archivedThreads.ts` sets one generic error when any machine's archive load fails, so the project shows "Archived threads could not be loaded. Retry resolved history" whenever one machine is down, without saying which.

## Scope

In: web wording for a down machine that the primary fleet snapshot marks `identity-mismatch`: thread rows and chips, the chat banner, the composer status line and orchestrator switcher label, the thread header machine chip, and the project's machine notice above its thread list (which also drops its Retry button for that machine). The archived-history notice skips machines already shown as not connected and names the machine(s) whose history failed. Focused unit tests.

Out: server identity checks, fleet pairing, re-adding or removing machines or grants, a new `MachineReachState` member in client-runtime, mobile wording. Surfaces left as they are: the increment board rows (`BoardThreads.tsx` passes no reach state today), the overview and capacity machine lists (`overviewMachines.ts`, `hostLimitsModel.ts`), the draft machine picker, and Settings > Machines, which already handles `identity-mismatch`.

## Acceptance Criteria

- [ ] AC-01: A thread row on a down machine that the fleet snapshot marks `identity-mismatch` says "Different machine at address" instead of "Host offline" (or any other down word).
- [ ] AC-02: The chat banner and the composer status line for that machine say "{machine}'s address now answers as a different SpecWithCode" with "Open Settings > Machines to fix it.", and never "Retrying by itself".
- [ ] AC-03: Without a fleet snapshot, or when the fleet does not mark the machine `identity-mismatch`, or while the machine is connected or only reconnecting, or when this device has no network, every word stays as today.
- [ ] AC-04: The archived-history notice does not show when every machine whose archive failed is already shown down.
- [ ] AC-05: When the archived-history notice shows, it names the machine(s) whose history failed.
- [ ] AC-06: New phrases go through the app's phrase translation, with entries in every phrase catalog.

## Approach

1. `apps/web/src/lib/machineStatus.ts`: `machineReachWords(state, phase, { identityMismatch })` returns identity-mismatch words (headline, short, no `next`, a new `action`) when the flag is set and the state is down and not `no-network`; `hostDownWord(state, identityMismatch)` returns "Different machine at address" the same way. `machineReachDetail` stays; the banner and composer append `action`.
2. `apps/web/src/studio/unreachableHosts.tsx`: the provider reads the primary fleet snapshot (`usePrimaryFleetSnapshot`, already polled by the shell's Connect reconciler) and publishes the set of `identity-mismatch` environment ids in a new context; `useHostIdentityMismatch(id)` and `useIdentityMismatchedHosts()` read it. A pure `identityMismatchedEnvironmentIds(snapshot)` holds the rule.
3. Callers pass the flag: `shellModel.threadStatusWord` (ThreadsPane, project thread cards), `environmentUnavailableBanner` (ChatView), `HostAdmissionContext.identityMismatch` for `composerHostStatus` and `hostDisconnectedLabel` (ProjectWorkspaceSurface).
4. Archived history: `ArchivedThreadSnapshotsState` gains `failedEnvironmentIds` (additive; `error` stays for mobile). A pure web helper `archivedHistoryNotice` (`apps/web/src/studio/archivedHistoryNotice.ts`) returns null when every failed machine is shown as not connected (down, reconnecting or connecting, so it does not flash during the reconnect grace), else "Resolved history from {machines} could not be loaded."; a machine with no name reads as "another machine", never its raw id. ProjectWorkspaceSurface renders it.

Tests run in the verification copy from `specweave-studio checks copy` (the worktree has no dependencies installed); evidence is in this increment's `reports/`.

Rejected: a new `identity-mismatch` reach state in client-runtime (the reach judgement is connection-only and shared with mobile; the fleet fact is a web-only overlay). Risk: a remote viewer without the primary fleet keeps today's words, which is the stated fallback.

## Decisions

### Asked
- none (the task fixed wording and scope)
### Defaulted (change any before sw-do)
- D-01 A "no-network" state on this device keeps "No network": the local cause comes first (reversible).
- D-02 The banner keeps "Last answered ..." before the action, since it is still true of the real machine (reversible).
### Open
- none

## Tasks

### T-01 Identity-mismatch words for row, banner and composer
- AC: AC-01, AC-02, AC-03, AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/lib/identityMismatchWords.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/threadMachine.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectExecutionHistory.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/ThreadLinkChip.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/lib/machineStatus.ts, repositories/anton-abyzov/specwithcode/apps/web/src/lib/machineStatus.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/unreachableHosts.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/shellModel.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectThreadCards.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectWorkspaceModel.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/environmentUnavailableBanner.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/ChatView.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/ThreadsPane.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectThreadCards.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases | Test: cd apps/web && node ../../node_modules/vite-plus/bin/vp test run --project unit src/lib/identityMismatchWords.test.ts src/lib/machineStatus.test.ts src/studio/shellModel.test.ts src/studio/projectWorkspaceModel.test.ts src/components/chat/threadMachine.test.ts src/components/ChatView.logic.test.ts src/components/studio/ComposerHostStatus.test.tsx src/components/studio/ProjectExecutionHistory.test.tsx src/i18n/i18n.test.ts

### T-02 Archived-history notice skips machines shown down and names the rest
- AC: AC-04, AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/studio/archivedHistoryNotice.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/archivedHistoryNotice.test.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/state/archivedThreads.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/state/archivedThreads.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/lib/archivedThreadsState.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx | Test: node node_modules/vite-plus/bin/vp test run packages/client-runtime/src/state/archivedThreads.test.ts && cd apps/web && node ../../node_modules/vite-plus/bin/vp test run --project unit src/studio/archivedHistoryNotice.test.ts

### T-03 Builds, typecheck, review, merge and release request
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode | Test: node node_modules/typescript/bin/tsc --noEmit --project apps/web/tsconfig.json && cd apps/web && node ../../node_modules/vite-plus/bin/vp build

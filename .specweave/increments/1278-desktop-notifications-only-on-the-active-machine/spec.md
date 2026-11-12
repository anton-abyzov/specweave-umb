# Desktop notifications only on the active machine

Repo: `anton-abyzov/specwithcode` (shared checkout `~/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode-dev`, base `main` at `35a82476b1`). Paths below are relative to that checkout.

## Problem

Anton, November 10, 2026:

> "Even when it pops up only for M4 coordinator, like the question, for example, it seems like I see notifications on all other machines, which might not be correct. At least when M4 is on, I believe I should only see it on the M4 machine, right?"

He is right, and it is by design today. Every desktop or web app alerts for every thread on every machine it is connected to:

1. Each app's catalog holds every machine it can reach: saved routes, fleet auto-pairing (`apps/web/src/studio/fleetAutoConnect.ts:164-186`), Connect routes and linked-project machines (`apps/web/src/cloud/ConnectRouteReconciler.tsx:116-151`). `environmentIdsAtom` is that list (`packages/client-runtime/src/state/presentation.ts:144-152`).
2. `ThreadNotificationCoordinator` mounts one `EnvironmentNotifications` per machine (`apps/web/src/components/ThreadNotificationCoordinator.tsx:157-164`), each with a live `subscribeShell` stream (`:186`, `packages/client-runtime/src/state/shell.ts:226-228`).
3. A new question, approval, plan, completion, failure or stall on any of them becomes a candidate (`ThreadNotificationCoordinator.tsx:351-375`).
4. The only gates are:
   - `isNotificationOwner()` (`:376`, `:403`; `apps/web/src/threadNotifications.ts:32`), which elects one window inside one desktop app (`apps/desktop/src/ipc/methods/notificationBadge.ts:96-106`);
   - the project notification level (`:379-388`);
   - `deliverNotificationOnce` (`apps/web/src/notificationHistory.ts:41-56`), which dedupes through `localStorage` and `navigator.locks`, so per device only.
5. An unfocused window then posts an OS notification through the desktop bridge (`ThreadNotificationCoordinator.tsx:552-589`) or `new Notification` (`:591-612`).

So an M4 coordinator question pops up on the M4, the Minisforum, the M1 and any browser tab with notifications connected, each once. Nothing reads which machine runs the thread or where the user is. A thread handed off to another machine (`executionState: "fenced"`, `packages/contracts/src/threadExecution.ts:27-30, 120-133`) is not filtered either, so its stale copy can alert too.

Phone pushes are separate and not part of the bug. Each machine's server publishes thread activity to the Connect relay (`apps/server/src/relay/AgentAwarenessRelay.ts:84, 211-221, 346`), and the relay pushes to every registered phone of the user (`infra/relay/src/agentActivity/AgentActivityPublisher.ts:57-105`, `agentActivityAlerts.ts:150-161`).

## What presence exists to reuse

Every server already knows which of its clients the user is in front of:

- Each web or desktop window reports `visible`, `focused` and `recentlyInteracted` to every connected machine every 25 s, with a 45 s lease (`apps/web/src/lib/backgroundActivityReporter.ts:29-31, 120-142, 233-245`). The phone reports `AppState` the same way (`apps/mobile/src/connection/background-activity.ts:50-78`).
- The server keeps these as `ClientActivityLease`s (`packages/contracts/src/background.ts:61-98`; `apps/server/src/ws.ts:2627-2640`). It drops them when the socket closes (`ws.ts:1419`) or expires (`apps/server/src/background/BackgroundPolicy.ts:345-364`). "Foreground" means `visible && (focused || recentlyInteracted)` (`BackgroundPolicy.ts:129-131`).
- `server.getBackgroundPolicy` returns the snapshot with all leases (`ws.ts:2643`). No client reads it today. The leases only gate background work.

Because every app that shows M4's threads also reports activity to M4, **M4's server already sees every device that could raise an M4 alert**. The election can run on the thread's own server. No new cross-machine presence channel is needed.

Gaps:

- A lease carries no interaction time and disappears 45 s after a device sleeps, so "most recently active" is unknown once everyone is idle.
- The server cannot tell which lease comes from its own machine.

## Scope

In:

- The thread's server elects one notification client from the activity leases it already holds.
- Desktop and web apps raise the OS popup and play the sound only when they are that client. Every other app counts the alert in its badge with no popup and no sound.
- Alerts from handed-off copies are suppressed.
- Old-server fallback, unit tests, a two-server proof, and the settings copy.

Out:

- Phone pushes, the relay, Live Activities, widgets and project notification levels. They stay as configured.
- A cross-machine presence service, and user-facing election settings beyond the copy line in AC-08.
- In-app toasts in a focused window. That window is the active client by definition.

## Acceptance Criteria

- [ ] AC-01: Each activity report adds `lastInteractionAt` (the last pointer, key, wheel or touch event, or for mobile the last time the app was active) and `hostEnvironmentId` (the reporting app's own primary environment, when it has one). Both fields are optional in the contract, so older clients and servers still interoperate.
- [ ] AC-02: The server keeps the latest `lastInteractionAt` per `clientId` for 8 hours after the lease ends. It is memory only and holds at most 64 entries. `server.getBackgroundPolicy` returns `notificationTarget: { clientId, reason } | null`, chosen in this order:
  1. the foreground desktop or web lease with the latest `lastInteractionAt` (`reason: "foreground"`);
  2. a foreground mobile lease, so no desktop pops up while the user is on the phone, which gets its relay push as today (`"phone"`, with a `clientId` no desktop matches);
  3. the desktop or web client with the latest `lastInteractionAt` in the retained window (`"recent"`);
  4. a live lease whose `hostEnvironmentId` is this server, meaning the app on the thread's own machine (`"owner"`);
  5. otherwise `null`.
- [ ] AC-03: Before posting a system notification or playing a sound for a thread on machine E, the app reads E's `notificationTarget`. It caches the target for 5 s per machine and refreshes it on every new candidate. It posts only when the target's `clientId` is its own `backgroundActivityClientId()`, with the project-window suffix stripped so that any window of the elected app counts. Window election inside that app (`isNotificationOwner`) still applies.
- [ ] AC-04: An app that is not the target posts no OS notification and plays no sound. It still counts the alert in its dock or taskbar badge and favicon badge, and the sidebar status is unchanged. The badge entry is withdrawn on the same events as today: answered, focus, or machine removed.
- [ ] AC-05: Fallback. When E's server is too old to return `notificationTarget`, or the read fails or times out after 1.5 s, only an app whose own primary environment is E alerts. When no such app is connected to E (a headless server, for example), every app alerts as today. A `null` target follows the same rule.
- [ ] AC-06: Thread copies whose `executionState` is `"fenced"`, or whose `executionMachineId` differs from the serving environment, never raise an alert, toast or badge entry. The running copy alerts once.
- [ ] AC-07: Scenario: M4 and Minisforum both run the app, both connected to M4. Anton last typed on the M4, and an M4 coordinator asks a question.
  - The M4 app pops up, if unfocused, and the Minisforum app only badges.
  - When he then moves his mouse on the Minisforum, the next M4 alert pops up on the Minisforum and only badges on the M4.
  - With both idle, the most recently used one pops up.
  - With the M4 asleep and the Minisforum the only recent client, the Minisforum pops up.
- [ ] AC-08: Settings > Notifications says "Shown on the device you are using. Your other computers show a badge." The notification test button still posts on the device it is pressed on.
- [ ] AC-09: Phone pushes are unchanged. No change in `apps/server/src/relay/`, `infra/relay/` or `apps/mobile`, and the relay tests pass.
- [ ] AC-10: Unit tests cover the election order and ties. Coordinator tests cover target, non-target, old server, timeout and fenced cases. A two-server headless proof shows exactly one OS-notification call across two apps for one question, plus the switch after interaction on the other device.
- [ ] AC-11 (from 1304 D-10): A blocker or "needs you" item has one owner machine: the machine of the coordinator that launched its thread (a remote worker known to that coordinator), else the thread's `ownerMachineId`, else the machine that serves it. One pure function decides it, with tests for a local thread, a handed-off thread and a remote worker.
- [ ] AC-12 (from 1304 D-10): An app raises an item, meaning it counts it in the sidebar project badge, the project page count and the Overview "Needs you" count and list, only when (a) its own machine is the item's owner, or (b) it is the `notificationTarget` of the server that serves the thread. With one person this is one app; the owner's app always counts its own.
- [ ] AC-13 (from 1304 D-10): An item an app does not raise stays visible in place: its row keeps "Blocked", "Answer needed" or the approval word in the Threads pane, the chat list (the "Needs you" filter still finds it) and the open thread, with its machine named. Overview shows one quiet line under "Needs you", "N more on <machine>, in use there", which scopes Overview to that machine. Nothing is hidden.
- [ ] AC-14 (from 1304 D-10, amends AC-04 and the Minisforum line of AC-07): An app that is neither the target nor the owner machine's app adds no dock, taskbar or favicon badge entry for the item. The target app and the owner machine's app badge. Popups and sound stay with the target alone.
- [ ] AC-15 (from 1304 D-10): Never hide on doubt. When the serving machine is too old to return `notificationTarget`, the read fails or times out, or the target is `null`, every app counts and badges the item as it does today. An item whose owner machine is unreachable from this app is raised here.
- [ ] AC-16 (from 1304 D-10): The phone is unchanged. Tests cover the raise rule (owner, target, neither, unknown target, unreachable owner), and the two-server proof shows one question counted in one app's sidebar badge and Overview while both apps still show its row.

## Approach

1. **Contracts.** `packages/contracts/src/background.ts`: add optional `lastInteractionAt` and `hostEnvironmentId` to `ClientActivityReportInput` and `ClientActivityLease`, and add `NotificationTarget` and an optional `notificationTarget` to `BackgroundPolicySnapshot`.
2. **Reporters.** `apps/web/src/lib/backgroundActivityReporter.ts` sends both fields. It already tracks `lastInteractionAtMs`, and the host is the platform or primary entry in the registry. `apps/mobile/src/connection/background-activity.ts` sends `lastInteractionAt` when `AppState` becomes active.
3. **Server election.** `apps/server/src/background/BackgroundPolicy.ts`: store the new lease fields, keep a retained last-interaction map, and add a pure `electNotificationTarget(leases, retained, selfEnvironmentId, now)` that feeds the snapshot. "Foreground" is the existing `isForegroundLease`, and ties go to the higher `updatedAt`, then to the lower `clientId`.
4. **Client gate.** `apps/web/src/notificationTarget.ts` (new) holds the per-environment cached read through `registry.run(E, request(serverGetBackgroundPolicy))` and returns `"post" | "badge-only"`. `ThreadNotificationCoordinator.tsx` calls it inside `deliverNotificationOnce`, right before the sound and OS-post branches (`:464`, `:519-552`). On `"badge-only"` it records the entry with `onNotification` using a no-op `close` and returns `true`, so the event is not retried. It also skips fenced copies next to the archived check at `:350`.
5. **Copy.** `apps/web/src/components/settings/NotificationSettings.tsx`.
6. **Proof.** A unit suite for `electNotificationTarget`, extended `ThreadNotificationCoordinator` tests, and `scripts/studio-logical-projects/notify-active.mjs`, modeled on `two-orchestrators.mjs`, run headless.

Rejected:

- **A global cross-machine "active device" record (hub or relay).** It adds a new channel, and it fails exactly when the machines lose contact. The thread's server already hears from every client that can alert for it.
- **Electing on each client from its own focus or idle state.** Two idle apps both conclude "not me", or both conclude "me". Only a shared view of the leases gives exactly one winner.
- **Notifying only on the owner machine.** Anton working on the Minisforum while the M4 runs a coordinator would never see a popup.

Risks:

- A 25 s report interval means a device switch takes up to 25 s to win the election. Interaction already triggers a debounced report through `requestReport`, so it is usually under 1 s. AC-07 checks this.
- A server restart clears the retained map. Election then falls back to the owner rule until someone interacts.

## Decisions

### Asked
- D-01 Where should desktop popups show? Only on the device the user is active on: the thread's owner machine when it is in use, otherwise the most recently active device. Other machines badge, and the phone stays as configured (user).
- D-07 Where should a thread's blocker show (asked in increment 1304 as its D-10, November 12, 2026)? One owner, counted once: it stays visible wherever the thread is opened, with its machine named; only the owner machine's app raises badges and "Needs you"; another app does only when the owner has nobody in front of it; the phone is unchanged (user). This narrows D-01's "other machines badge" to the owner machine's app (AC-14). The coordinator routed the count gate here so badges and popups read one election; the rule and the surfaces with their file lines are in `.specweave/increments/1304-force-update-setting-for-busy-machines-and-blockers-shown-only-on-the-machine-they-belong-to/reports/blocker-count-gate.md`.
### Defaulted (change any before sw-do)
- D-02 The election runs on the thread's own server from existing activity leases, with no new presence service (reversible).
- D-03 A foreground phone suppresses desktop popups but never takes over the "recent" slot once backgrounded, because a phone that has notifications off must not swallow every desktop popup (reversible).
- D-04 Fallback for an old or unreachable server is the app on the thread's own machine, then everyone (reversible).
- D-05 Handed-off (fenced) copies never alert (reversible).
- D-06 No "always notify on this device" override in this increment (reversible).
### Open
- none

## Tasks

### T-01 Contracts and reporters send interaction time and host
- AC: AC-01 | Files: packages/contracts/src/background.ts, apps/web/src/lib/backgroundActivityReporter.ts, apps/mobile/src/connection/background-activity.ts, apps/web/src/lib/backgroundActivityReporter.test.ts | Test: `npx vitest run apps/web/src/lib/backgroundActivityReporter.test.ts packages/contracts`

### T-02 Server elects the notification target
- AC: AC-02 | Files: apps/server/src/background/BackgroundPolicy.ts, apps/server/src/background/BackgroundPolicy.test.ts | Test: `npx vitest run apps/server/src/background`

### T-03 Desktop and web alert only when elected; fenced copies stay silent
- AC: AC-03, AC-04, AC-05, AC-06 | Files: apps/web/src/notificationTarget.ts, apps/web/src/components/ThreadNotificationCoordinator.tsx, apps/web/src/components/ThreadNotificationCoordinator.test.tsx | Test: `npx vitest run apps/web/src/components/ThreadNotificationCoordinator.test.tsx apps/web/src/notificationTarget.test.ts`

### T-04 Settings copy
- AC: AC-08 | Files: apps/web/src/components/settings/NotificationSettings.tsx | Test: `npx vitest run apps/web/src/components/settings`

### T-05 Two-server proof and phone non-regression
- AC: AC-07, AC-09, AC-10 | Files: scripts/studio-logical-projects/notify-active.mjs, docs/studio/logical-projects.md | Test: `node scripts/studio-logical-projects/notify-active.mjs && npx vitest run infra/relay`

### T-06 Owner machine and the raise rule
- AC: AC-11, AC-12, AC-15 | Files: packages/client-runtime/src/state/attentionOwner.ts, packages/client-runtime/src/state/attentionOwner.test.ts, packages/client-runtime/src/state/projectAttention.ts, apps/web/src/notificationTarget.ts | Test: `npx vitest run packages/client-runtime/src/state/attentionOwner.test.ts packages/client-runtime/src/state/projectAttention.test.ts`

### T-07 Counts and badges follow the raise rule; rows stay in place
- AC: AC-12, AC-13, AC-14, AC-16 | Files: apps/web/src/studio/useProjectAttention.ts, apps/web/src/components/studio/shell/StudioSidebar.tsx, apps/web/src/components/studio/StudioOverview.tsx, apps/web/src/studio/overviewModel.ts, apps/web/src/components/ThreadNotificationCoordinator.tsx, apps/web/tests/project-workspace/attention-fixture.tsx, scripts/studio-logical-projects/notify-active.mjs | Test: `npx vitest run apps/web/src/studio && node scripts/studio-logical-projects/notify-active.mjs`

---
title: "Remote SpecWithCode updates: why linux-mini gets an Update button and m1 does not"
thread: "thread:delegated-task:command%3Amcp%3A0e842ec5-d023-44ab-bab9-2f0c26e73cc4%3Adelegate-task%3A0f0156fc-cea3-491a-801d-a44d9dd49d45"
threadTitle: "Remote SpecWithCode updates per machine"
savedAt: "2026-11-23T08:10:06.822Z"
date: November 23, 2026
machine: M5
scope: research only, no code changed
code: repositories/anton-abyzov/specwithcode at 9363b068a (branch 1448-link-personal-assistant)
---

# Remote SpecWithCode updates

## Answer

Yes. When a window offers Update for another machine, pressing it installs the new release there and restarts SpecWithCode there. On linux-mini the server downloads the release, checks it, and the boot launcher switches over and restarts the service. On a desktop-managed machine (M5, win) the app there updates and relaunches. Running turns are stopped by the restart. They continue afterwards only if that machine's "Continue threads after restarts" setting is on. Terminals are closed.

From any window the remote Update row appears only for machines that advertise `serverSelfUpdate`. linux-mini (`boot-service`), M5 and win (`desktop-managed`) advertise it. m1 and m4 advertise nothing, because their service runs under the macOS update agent (`method: service-agent`). So no window ever offers them remotely. The cause is the install type, not Linux versus macOS: M5 is also a Mac, and m1's or m4's window would offer to update M5.

The m1 screenshot is m1's own window ("Window on m1" chip). "Update m1 now" is the local desktop button, which acts only on the window's own machine.

## 1. How a remote update is offered

| Condition | Where | Effect |
|---|---|---|
| Machine is in this window's environment list | `apps/web/src/components/sidebar/SidebarServerUpdate.tsx:36-65` | One footer row per connected server |
| Version behind | `SidebarServerUpdate.tsx:97-101`, `apps/web/src/versionSkew.ts:75-126` | Behind this app's version, or behind the newest release this app's feed downloaded or listed. Never for the window's own machine (it follows the app's update) |
| Update path advertised | `SidebarServerUpdate.tsx:121-125`, `versionSkew.ts:173-178` | Needs `serverSelfUpdate`, plus `desktopAppUpdate` when it is `desktop-managed`. Otherwise no row at all |
| How the server decides | `apps/server/src/environment/ServerEnvironment.ts:294-305`, `apps/server/src/cloud/selfUpdate.ts:45-51` | `desktop` mode gives `desktop-managed`, a service-launcher parent gives `boot-service`, anything else gives null |
| Dismissal | `SidebarServerUpdate.tsx:128`, `versionSkew.ts:199-251` | × hides the row per machine, target version and current version (localStorage, per window). A newer release brings it back |
| Busy machine | `apps/web/src/components/ServerUpdateAction.tsx:245-300` | Pressing Update first lists the running work there and offers Update now, Wait until quiet, or Later |
| "Pause running work for updates" | `apps/server/src/fleet/fleetUpdatePause.ts:1-11` | Applies only to the fleet request path (CLI and rollouts). A person's own Update is never gated |
| Team rules | `selfUpdate.ts:205-206` | A team update-feed rule can refuse it |

Live capabilities, read today from each machine's environment descriptor:

| Machine | OS | `serverSelfUpdate` | `fleetUpdateRequest` | Remote Update row possible? |
|---|---|---|---|---|
| M5 | macOS | desktop-managed (+ desktopAppUpdate) | n/a (local) | Yes, from other windows |
| m4 | macOS | none | true | No |
| m1 | macOS | none | true | No |
| linux-mini | Linux | boot-service | true | Yes |
| win | Windows | desktop-managed (+ desktopAppUpdate) | true, but `fleet update` refuses it ("installs updates through its SpecWithCode app") | Yes |

Settings > Machines already has an "Update all" button (`apps/web/src/components/settings/ConnectionsSettings.tsx:1956-1985`, `:4138`). It uses the same capability filter, so it skips m1 and m4 too. It also compares only against this app's version, not the newest release. The Mac "Updates for <machine>" card (`apps/web/src/components/settings/ManagedUpdatesSection.tsx:162-186`) only offers "Check for updates", and only after enrollment. It "does not download or install them."

## 2. What pressing Update does

**linux-mini (boot-service)**, `selfUpdate.ts:218-358`: it reports `downloading`, installs the exact release into the pinned runtime with checksum verification, and runs the new build's `__service-preflight` against the database. It then reports `installing` and asks the service launcher to switch over (`launcher.requestUpdate`, `:335`). The service restarts on the new version and the window reconnects ("Reconnected on specweave-studio@X", `ServerUpdateAction.tsx:147-152`). This needs nobody at the machine: it is a systemd user service with no prompts.

**Desktop-managed (M5, win)**, `selfUpdate.ts:207-216`: the app there runs its own update feed, downloads, and relaunches. The version is whatever that feed offers.

**Threads and terminals.** The restart cuts running turns and closes terminals. On startup, orphaned runs become cancelled and are continued with a "Continue where you left off" prompt. This happens only when "Continue threads after restarts" is on for that project on that machine (`apps/server/src/orchestration-v2/OrphanedRuns.ts:259-268`, `RestartContinuation.ts:139-142`). Questions closed for the update come back as cards.

Gap: no server sets the `serverUpdateThreadContinuation` capability. It is only declared in `packages/contracts/src/environment.ts:286`. So the button never sends `continueRunningThreads` (`ServerUpdateAction.tsx:138-140`), and the tooltip always says "Threads running there stop for the restart" (`apps/web/src/serverUpdateWording.ts:64-66`). The generic restart continuation above still applies, so the wording may undersell what happens. I have not verified this live.

**Macs with the update agent (m1, m4).** The only remote path is the CLI or a rollout: `specwithcode fleet update <machine> --version X` (`apps/server/src/cli/fleet.ts:556`, `apps/server/src/fleet/fleetUpdate.ts:1-33`, `:1124-1183`). Without `--no-hold` it drains and holds as Update now does, which is a forced request. With "Pause running work for updates" off, the machine refuses a forced request (`fleetUpdatePause.ts:41-42`). `--no-hold` leaves a request that installs once the machine is quiet. The agent installs only a release it downloaded and verified against SHA256SUMS, then restarts the service. The app follows: "The service updates first, then the app restarts on its own" (`SidebarRestartToUpdate.logic.ts:393`). Public macOS builds are Developer ID signed and notarized and use Squirrel.Mac (`docs/studio/updates.md:77`).

**Proof limits.** I found no evidence on a locked screen, a logged-out Mac or permission prompts during an unattended install. The launchd agent runs in the user's GUI domain, so the user very likely has to be logged in, but I did not test it.

## 3. Versions now (November 23, 2026)

| Machine | Service | App | Update state |
|---|---|---|---|
| M5 | 1.0.408 | 1.0.408 | 1.0.409 downloaded |
| m4 | 1.0.407 | not read | 1.0.409 downloaded; `waiting-for-quiet` (3 running tasks); pause setting off |
| m1 | 1.0.408 (installed 07:34 UTC today by a held request) | not read | 1.0.409 downloaded; `waiting-for-quiet` (1 open question); pause setting off |
| linux-mini | 1.0.407 | n/a | idle; offers no 1.0.409 yet (a boot service learns a target from the asking window) |
| win | 1.0.408 | desktop app | its app's own feed |

Sources: `specwithcode fleet update --status --json <machine>` (read-only), each machine's `/.well-known/studio/environment`, and M5's `server-runtime.json`.

Memory drift: `decision_update_pause_setting.md` says the pause setting is on for M4 only. Live m4 reports `pauseWorkForUpdates: false`.

## 4. Gaps and recommendations

1. **Remote update for agent-managed Macs in the UI.** The machines already expose `fleetUpdateRequest`. Teach the footer row and Settings > Machines to use it for machines without `serverSelfUpdate`, with a normal (quiet) request by default and the existing busy dialog for "Update now". This needs a client path to the fleet update endpoint and a scope check (`fleet:update`), so it is an increment, not a small fix.
2. **One "Machines and versions" table in Settings > Machines.** Show every machine's service and app version, whether it is downloaded or waiting for quiet (with the reason, such as "3 running tasks" or "1 open question"), the pause setting, the last install and its result, and one Update or Update when quiet button per row, plus "Update all when quiet". `fleet update --status` already returns all of these fields.
3. **"Update all" should target the newest release,** not only this app's version (`ConnectionsSettings.tsx:1974` calls the mismatch check without `newestRelease`).
4. **Advertise `serverUpdateThreadContinuation`,** or drop it, so the tooltip matches what happens after the restart.
5. **Give linux-mini a newer target on its own.** Today it only learns of a release from a window's feed, so its row read 1.0.408 while 1.0.409 existed.
6. **Name the blocker.** m1 waits on one open question. A row "m1 waits for 1 open question" with a link to it would end most silent waits.

Next step: create an increment for 1 and 2 ("Update any machine from Settings > Machines, with each machine's version and wait reason"), with 3 to 6 as tasks.

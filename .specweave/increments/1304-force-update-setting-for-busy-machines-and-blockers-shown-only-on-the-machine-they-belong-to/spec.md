# Force-update setting for busy machines, and blockers shown only on the machine they belong to

Repo: `anton-abyzov/specwithcode`, read at `origin/main` `05b4d5477e` (1.0.242). Product paths below are relative to `repositories/anton-abyzov/specwithcode-dev/`.

## Problem

Anton, November 11, 2026:

> "I believe for the plan view blocker, it should be like a configuration: whether we want to force these updates or not. By default, I would keep it as not forcing. Also, once we see a blocker, it should only be visible on that machine where this blocker is coming from, right? Or if this is a blocker in a thread, then it should be visible on the machine where the coordinator is running. We think that this... Maybe I am wrong."

What happened: the Minisforum (Linux) stayed on 1.0.236 through the 1.0.240 and 1.0.241 rollouts. Its "Build SpecOS on Linux" thread kept it busy for the whole 30-minute wait, nobody forced it, and the 1303 fix that needs a newer build there was held back. The release thread asked whether to force it, and that question reached Anton as a blocker in the M4 coordinator.

### Forcing exists in four places and no setting decides it

1. **Every Mac pauses running work by itself after 10 minutes.** An automatic service install that finds running work starts a grace (`pauseWorkAfterMinutes`, default 10, choices 10/30/60, no "never"). Then the update agent drains and holds the service and installs (`scripts/studio-fleet/update_agent_pause.py:186-225`, `:261-327`). Today's default is the opposite of what Anton asked for.
2. **The rollout always drains M4.** `fleet_rollout.py` passes `force=True` for M4 (`:1198`) and runs `service prepare-update --stop-work --hold` (`service_hold.py:128-129`).
3. **The fleet endpoint takes `mode: "force"` from the primary** and drains (macOS) or switches over at once (Linux) with no rule of the machine's own (`apps/server/src/fleet/fleetUpdate.ts:385-428`, `:542-562`, `:601-617`).
4. **A Linux worker never forces itself.** A normal install waits `BOOT_QUIET_MAX_MS` (30 minutes) and gives up as `busy`: "Ask again once it is quiet, or force the update" (`fleetUpdate.ts:272`, `:459-462`). That sentence is what sent the question to Anton.

Nothing counts missed rollouts, and the rollout has no "left for later" result: a required host that stays busy ends `not-updated`, the run ends `partial` with exit 1 (`fleet_rollout.py:1087-1092`, `:1299-1300`).

### Where blockers show today

Read from `packages/client-runtime` and `apps/web` (map in `reports/map-*.md`):

- A thread's "needs you" state (report **Blockers:** part, question card, approval, sign-in, held queue) is computed by the server that runs the thread and never copied. Each app subscribes to every machine it is paired with, so the Overview "Needs you" list, the "Blocked" word, the Threads pane, desktop notifications and the dock badge show the same thread in every app paired with that machine.
- No surface asks which machine runs the project's coordinator.
- A machine's own update state ("waiting for running work") shows only in the desktop app on that Mac. Other machines see it only when someone opens that machine's card in Settings > Machines. A Linux machine shows it nowhere.
- Phone pushes come from the thread's own server and ignore report blockers.

## Scope

In: one per-machine setting, off by default, that decides whether an update may pause running work; every automatic path obeys it (Mac update agent, Linux boot service, fleet endpoint, rollout); a "left for later" rollout result; the setting on each machine's update card; docs. Blocker placement: the analysis below, Anton's decision, and the count gate written into increment 1278 as acceptance criteria.

Out: a person's own Update now, Restart now or `specweave-studio update` (never gated); the desktop app's own restart-when-idle (it already never stops work); the SSH-only Linux rollout (`linux_rollout.py` never forces); OS notification election (1278 owns it); phone clients.

## Acceptance Criteria

- [ ] AC-01: A server setting `pauseWorkForUpdates` exists per machine and defaults to off, also on machines that update from an earlier release. It is never copied between machines.
- [ ] AC-02: On a Mac with the setting off, an automatic service install never pauses running work. It waits until the machine is quiet, publishes no pause time, and its status line says the update installs once running work finishes. With the setting on it behaves as before this change: it waits "Pause running work after", pauses, installs, and the turns continue.
- [ ] AC-03: A forced fleet update request to a machine with the setting off is refused before anything is stopped. The refusal names the setting and says the machine is left for later by its owner's choice. The machine's fleet update status reports the setting.
- [ ] AC-04: A Linux boot-service machine waits 30 minutes for quiet. With the setting off it then gives up as busy and names the setting. With it on it stops its work the way Update now does (turns interrupted for the update, open questions recorded), installs, and the turns continue.
- [ ] AC-05: The rollout asks M4's service for the setting. Off: M4 is held only when idle and nothing is interrupted. On: drained as before. A service too old to report the setting is treated as before this change.
- [ ] AC-06: A worker that is still busy when its wait ends, with the setting off, ends `deferred` with the reason. A deferred worker does not fail the run. Its wait is 30 minutes instead of 60.
- [ ] AC-07: Update now, Restart now and a hand-run `specweave-studio update` work with the setting off exactly as before.
- [ ] AC-08: With "Continue threads after restarts" off on a machine, no update pauses running work there, whatever the setting says, and the setting's row says why.
- [ ] AC-09: The setting is a switch on this machine's update card in Settings > General and on every machine's card in Settings > Machines. A card's switch changes only that machine. "Pause running work after" is disabled while the switch is off. Strings exist in all eight catalogs.
- [ ] AC-10: `docs/user/updating.md`, `docs/studio/releasing.md` and `CHANGELOG.md` describe the setting, its default and its bounds.
- [ ] AC-11: Blocker placement follows D-10: the owner rule, the raise rule and every surface are written down in `reports/blocker-count-gate.md` and are acceptance criteria AC-11 to AC-16 of increment 1278, which owns the presence election they need.

## Approach

One source of truth: the machine's own server setting. Everything else asks the server.

1. `packages/contracts/src/settings.ts`: `pauseWorkForUpdates`, boolean, decoding default `false`, in `ServerSettings` and `ServerSettingsPatch`. Not project-scoped and not in `sharedSettings.ts`.
2. `packages/shared/src/updatePause.ts` (new): `updatesMayPauseWork(settings)` = `pauseWorkForUpdates && continueThreadsAfterServerUpdate`. One rule for server and web (AC-08).
3. `packages/contracts/src/serviceUpdatePreparation.ts`, `apps/server/src/serviceUpdate/ServiceUpdatePreparation.ts`: every prepare answer carries `pauseWorkForUpdates` (the effective value). `service prepare-update --json` prints it, so Python needs no settings parser. `ServiceUpdatePreparation.ts` is at 1,507 lines; this adds one field in `report`, nothing else.
4. `packages/contracts/src/studioFleet.ts`, `apps/server/src/fleet/fleetUpdate.ts`: status carries `pauseWorkForUpdates`; a `force` request with the setting off is refused as `busy` with the message of AC-03 (a new refusal literal would not decode on an older primary); the boot-service install escalates after its quiet wait when the setting is on, with a drain first (AC-04).
5. `scripts/studio-fleet/service_hold.py`: `look()` returns the service's answer without stopping anything. `scripts/studio-fleet/update_policy.py` (new, added to `update_request.AGENT_FILES`): `pauses_work(answer)` returns True, False, or None for a service that does not report the setting.
6. `scripts/studio-fleet/update_agent_pause.py`: before it starts a grace, the agent looks; False ends the pass as waiting with no pause time (AC-02).
7. `scripts/studio-fleet/fleet_rollout.py` (1,470 lines, so only call sites): M4's hold becomes idle-only when the look says False (AC-05); a worker whose status says False gets a 30-minute deadline and ends `deferred` (AC-06). `rollout_record.py` and the JSON summary learn `deferred`.
8. Web: the switch on `ManagedUpdatesSection` (one component serves this machine in General and every machine in Settings > Machines), `UpdatePreferencesSection` copy and the disabled select, settings search, eight catalogs.
9. Docs and changelog.

Rejected:

- **A desktop preference in `updates/config.json`** beside `pauseWorkAfterMinutes`: Linux has no update agent and no writer for that file, and the Minisforum is the case that started this. Only the desktop bridge of the same machine can edit it.
- **Counting missed rollouts ("force after N missed windows")**: nothing stores rollout history across releases, a count depends on how often releases ship, and a clock is what the app already shows ("installs at 14:41").
- **A flag on the release script alone**: the Mac agent's own pause and the fleet endpoint would keep forcing.
- **Parsing `settings.json` from Python**: the file is sparse (defaults left out) and the scripts would need the defaults.

Risks: Macs that relied on the 10-minute pause now wait for quiet, so a machine that is never quiet stays on its version until someone presses Update now or turns the setting on. That is the asked-for default. The first rollout after this ships still drains M4 (its service predates the setting); the one after obeys M4's setting (D-07).

## Blocker placement: Anton's model against the code

| His statement | What the code does | Verdict |
|---|---|---|
| A machine-level blocker (this machine can't update while busy) shows on that machine | The waiting line shows only in that Mac's own desktop app. Nothing pushes it to other machines. A Linux machine shows it nowhere. It reached Anton only because an agent turned it into a question. | Agree. After this increment it is a setting, a `deferred` row in the rollout readback and a line on that machine's card, never a question. |
| A thread's blocker shows on the machine where its coordinator runs | Shown in every app paired with the thread's machine. No surface knows the coordinator's machine. | Agree on who owns it. Disagree on "only". |

Why not "only":

1. **An app is not one machine's screen.** The M4 app shows the Minisforum's threads because Anton drives that machine from the M4. The fortnite-3js coordinator runs on the Minisforum (1301), and he saw its Blocked state from his Mac. Hidden everywhere else, a blocker on a headless, asleep or closed machine is seen by nobody.
2. **A project can have a coordinator on each machine** (0969). "The coordinator's machine" is well defined for a worker a coordinator launched, not for the project.
3. **Plain chats have no coordinator.** They belong to the machine they run on.
4. **The phone is not a machine** and has to see everything.

Recommended instead: one owner, shown in place, counted once.

- Owner: the machine of the coordinator that launched the thread; the thread's own machine when there is none.
- The Blocked state stays visible wherever that thread or project is opened, with its machine named.
- Counts and attention (sidebar badge, Overview "Needs you", dock badge) are raised only by the app whose own machine is the owner. Another app raises them only when the owner has no app in front of a person (headless, asleep, closed), which is the election 1278 defines for OS popups. The phone is unchanged.

Anton chose this (D-10).

"Nobody in front of it" needs to know which app a person is using. Increment 1278 (desktop notifications only on the active machine, planned, not built, owned by its own thread) specifies exactly that: each app reports `hostEnvironmentId` and `lastInteractionAt`, and the thread's server elects one `notificationTarget` (1278 AC-01, AC-02). The count gate must read the same election, or popups and badges would disagree. So this part depends on 1278's election and is built on it, not beside it.

The coordinator routed it there (November 11, 2026): the count gate is 1278's AC-11 to AC-16 and its tasks T-06 and T-07. The rule, the surfaces with their file lines, and the one conflict with 1278's earlier answer ("other machines badge") are in `reports/blocker-count-gate.md`. This increment ships no blocker code.

## Decisions

### Asked
- D-10: Blocker placement: strict "only on the owner machine", or "one owner, shown in place, counted once"? → **One owner, counted once** (Anton, November 11, 2026). A blocker stays visible wherever its thread is opened, with its machine named. Only the owner machine's app raises badges and "Needs you"; another app does only when the owner has nobody in front of it. The phone is unchanged.
- D-07: M4 follows its own setting, so the rollout stops draining M4 unless the setting is on there. Turn it on for M4? → **On for the M4 only** (Anton, November 11, 2026). M1, M3 and the Minisforum stay off. The switch is turned on on the M4 once it runs a release that has the setting.

### Defaulted (change any before sw-do)
- D-01: The setting lives in the machine's server settings. It works on Linux, a paired machine can edit it, and the agent, the rollout and the fleet endpoint all read it from the service.
- D-02: The key is `pauseWorkForUpdates`, the label "Pause running work for updates". "Force" is rollout wording; the label says what happens to the work.
- D-03: Default off, also for existing installs. A saved "Pause running work after" choice is kept and applies once the switch is on.
- D-04: Bounds when on. Mac: wait "Pause running work after" (10, 30 or 60 minutes), at most one pause per version per hour, "Later" postpones an hour, a folder copy is never interrupted. Linux: wait 30 minutes, then pause. Both: turns are interrupted for the update and continue after it, open questions are recorded and asked again, and nothing pauses when "Continue threads after restarts" is off.
- D-05: No missed-window count (see Rejected).
- D-06: A person's own Update now is never gated.
- D-08: A service that does not report the setting predates it and is treated as before. One rule for the agent and the rollout.
- D-09: A deferred worker does not fail a rollout. A deferred M4 still ends the run with exit 1, because the stages after it need M4 on the version; its row says `deferred`, not `partial`.

### Open
- none

## Tasks

### T-01 Contracts and shared rule: the setting, the prepare answer, the fleet status
- AC: AC-01, AC-08 | Files: repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/settings.ts, repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/serviceUpdatePreparation.ts, repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/studioFleet.ts, repositories/anton-abyzov/specwithcode-dev/packages/shared/src/updatePause.ts, repositories/anton-abyzov/specwithcode-dev/packages/shared/src/updatePause.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Tests/SWCWireTests/Fixtures/serverSettings.default.json, repositories/anton-abyzov/specwithcode-dev/apps/android/wire/src/test/resources/fixtures/serverSettings.default.json | Test: cd "$HOME/.specwithcode/m4/scratch/2026-11-11-force-update/tree/packages/shared" && node ../../node_modules/vite-plus/bin/vp test run src/updatePause.test.ts

### T-02 Server: prepare answer, fleet endpoint refusal, Linux escalation
- AC: AC-03, AC-04, AC-07 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/serviceUpdate/ServiceUpdatePreparation.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/fleet/fleetUpdate.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/fleet/fleetUpdate.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/fleet/fleetUpdatePause.test.ts | Test: cd "$HOME/.specwithcode/m4/scratch/2026-11-11-force-update/tree/apps/server" && node ../../node_modules/vite-plus/bin/vp test run src/fleet/fleetUpdate.test.ts src/fleet/fleetUpdatePause.test.ts

### T-03 Update agent and rollout obey the setting
- AC: AC-02, AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode-dev/scripts/studio-fleet/service_hold.py, repositories/anton-abyzov/specwithcode-dev/scripts/studio-fleet/update_policy.py, repositories/anton-abyzov/specwithcode-dev/scripts/studio-fleet/update_request.py, repositories/anton-abyzov/specwithcode-dev/scripts/studio-fleet/update_agent_pause.py, repositories/anton-abyzov/specwithcode-dev/scripts/studio-fleet/fleet_rollout.py, repositories/anton-abyzov/specwithcode-dev/scripts/studio-fleet/rollout_record.py, repositories/anton-abyzov/specwithcode-dev/scripts/studio-fleet/test-update-policy.py, repositories/anton-abyzov/specwithcode-dev/scripts/studio-fleet/test-update-agent-pause.py, repositories/anton-abyzov/specwithcode-dev/scripts/studio-fleet/run-tests.sh | Test: cd "$HOME/.specwithcode/m4/scratch/2026-11-11-force-update/tree" && /usr/bin/python3 -B scripts/studio-fleet/test-update-policy.py && /usr/bin/python3 -B scripts/studio-fleet/test-update-agent-pause.py && /usr/bin/python3 -B scripts/studio-fleet/test-fleet-rollout.py && /usr/bin/python3 -B scripts/studio-fleet/test-fleet-rollout-idle.py

### T-04 Settings: the switch on each machine's update card
- AC: AC-09, AC-08 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/ManagedUpdatesSection.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/UpdatePausePolicyRow.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/UpdatePausePolicyRow.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/UpdatePreferencesSection.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/UpdatePreferencesSection.logic.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n | Test: cd "$HOME/.specwithcode/m4/scratch/2026-11-11-force-update/tree/apps/web" && node ../../node_modules/vite-plus/bin/vp test run --project unit src/components/settings/UpdatePausePolicyRow.test.tsx src/i18n

### T-05 Docs and changelog
- AC: AC-10 | Files: repositories/anton-abyzov/specwithcode-dev/docs/user/updating.md, repositories/anton-abyzov/specwithcode-dev/docs/studio/releasing.md, repositories/anton-abyzov/specwithcode-dev/CHANGELOG.md | Test: cd "$HOME/.specwithcode/m4/scratch/2026-11-11-force-update/tree" && grep -q "Pause running work for updates" docs/user/updating.md && grep -q "deferred" docs/studio/releasing.md && node node_modules/vite-plus/bin/vp fmt --check docs/user/updating.md docs/studio/releasing.md CHANGELOG.md

### T-06 Blocker placement: route the count gate to 1278
- AC: AC-11 | Files: .specweave/increments/1304-force-update-setting-for-busy-machines-and-blockers-shown-only-on-the-machine-they-belong-to/reports/blocker-count-gate.md, .specweave/increments/1278-desktop-notifications-only-on-the-active-machine/spec.md | Test: grep -q "AC-16 (from 1304 D-10)" .specweave/increments/1278-desktop-notifications-only-on-the-active-machine/spec.md && grep -q "Raise rule" .specweave/increments/1304-force-update-setting-for-busy-machines-and-blockers-shown-only-on-the-machine-they-belong-to/reports/blocker-count-gate.md

### T-07 Ship: PR, exact-head review, required CI, merge, release request
- AC: AC-01, AC-10 | Files: .specweave/increments/1304-force-update-setting-for-busy-machines-and-blockers-shown-only-on-the-machine-they-belong-to/reports/ship.md | Test: test -s .specweave/increments/1304-force-update-setting-for-busy-machines-and-blockers-shown-only-on-the-machine-they-belong-to/reports/ship.md

### T-08 Verify and close 1304
- AC: AC-10 | Files: .specweave/increments/1304-force-update-setting-for-busy-machines-and-blockers-shown-only-on-the-machine-they-belong-to/spec.md | Test: specweave task list 1304

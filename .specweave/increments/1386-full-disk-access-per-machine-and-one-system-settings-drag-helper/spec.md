# Full Disk Access per machine and one System Settings drag helper

## Problem

Agents can't read other apps' data on a Mac, and nothing in SpecWithCode helps the user fix it.

- On M5, a worker that was asked to list Chrome profiles got `PermissionError: [Errno 1] Operation not permitted: '/Users/anton/Library/Application Support/Google/Chrome/Local State'`. It then wrote a text blocker telling Anton to "turn on SpecWithCode" in Full Disk Access.
- Reproduced on M4 on November 18, 2026 from an agent shell. `head` on Chrome's `Local State` and `ls` on `~/Library/Mail`, `~/Library/Messages` and `~/Library/Safari` all return `Operation not permitted`.
- The TCC log for the Chrome read shows `kTCCServiceSystemPolicyAllFiles` (preflight), then `kTCCServiceSystemPolicyAppDataDetailed` (App Data, "access data from other apps").
- The log also shows who macOS holds responsible: `responsible_path=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node`, pid 61669. That is the launchd service (`node .../install/releases/<hash>/bin.mjs start`) that every agent runs under. It is not SpecWithCode.app.
- So the worker's advice was wrong. Granting SpecWithCode.app Full Disk Access does not reach agents, because macOS judges the agent host.
- The agent host has no stable identity to grant:
  - On M4 it is a shared Node binary (Team `HX7739G8FX`). A grant would give every Node script on the Mac full access and would end at the next Node upgrade.
  - In the boot-service plan (`apps/server/src/cloud/bootService.ts:1026`) it is `versions/<ver>/specweave-studio`, a new path on every version.
  - `bin.mjs` is "not signed at all".
- Anton also opened System Settings > Screen & System Audio Recording himself and added SpecWithCode through the "+" file picker. He saw no "Drag SpecWithCode here" helper.
- The helper does exist: `apps/desktop/src/permissions/MacPermissionHelper.ts`, since 1.0.5. It only opens when the app opens the pane itself, from three places:
  - computer use `requestPermission` (`MacComputerUse.ts`)
  - SnapShot setup (`DesktopSnapShot.ts:1315`, `:1403`)
  - the `openSystemSettings` IPC, whose only caller is the Safari import button in Settings > Integrations
- Why it did not appear for Anton is not verified. The likely path is that he followed a text instruction rather than an app button.
- The helper has four defects:
  1. `apps/desktop/src/ipc/methods/window.ts:371` passes the Safari Full Disk Access check as `isGranted` for every pane.
  2. `checkSystemPermission` (`window.ts:467`) ignores its pane argument.
  3. The helper's own grant check returns `false` for `full-disk-access` (`MacPermissionHelper.ts:14`), so it never closes by itself there.
  4. It can only drag SpecWithCode.app, never the agent host.

## Scope

In:
- A stable, signed agent host that macOS can be granted once.
- A per-machine "Full Disk Access for agents" status row with a deep link and a recheck.
- One shared drag helper for every TCC pane, with the four defects fixed.
- An agent-raised card when an agent is refused a protected path.
- Plain risk text.
- Windows and Linux behaviour.
- Docs.

Out:
- Granting anything without the user. No app can grant itself TCC access, and the app never edits TCC.db or runs `tccutil`.
- Keychain access (Chrome cookie decryption needs the Keychain, which is a separate prompt).
- A brokered, per-thread file reader (alternative B under Decisions).
- Microphone and Camera, which only the system prompt can grant.

## Acceptance Criteria

- [ ] AC-01: Agents run under one signed agent host whose TCC identity stays the same across SpecWithCode updates: bundle id, Developer ID team `NMCB2JZ7QG`, a designated requirement without version or hash. The TCC log shows `responsible_path` inside that host for an agent's file read.
- [ ] AC-02: After the user turns on Full Disk Access for the agent host and the service restarts, an agent on that Mac lists Chrome profiles (reads `Local State` and each profile's `Preferences`) and reads `~/Library/Mail`. The grant survives an update to the next SpecWithCode version with no new approval.
- [ ] AC-03: Settings > Machines shows a "Full Disk Access for agents" row in each Mac's readiness checklist, with one of three states:
  - Allowed (green).
  - Not allowed. It names what agents can't read and offers Open System Settings.
  - Allowed, restart needed. The grant exists but the running service started before it, so it offers Restart agents.

  The agent host's own probe on that machine sets the state and reaches Settings over RPC. On a remote Mac's card the row shows the status and the step to take on that Mac, with no deep link.
- [ ] AC-04: Open System Settings opens Privacy & Security > Full Disk Access with the drag helper. The helper offers the agent host to drag and closes by itself once the agent-host probe reports access. The row then rechecks every 2 s for up to 2 minutes and on window focus.
- [ ] AC-05: The service never restarts on its own after a grant. Restart agents runs now when no thread on that machine is running. Otherwise it offers "Restart when idle", which waits for the running threads.
- [ ] AC-06: One shared helper serves every pane the app sends the user to: Full Disk Access, App Data, Screen & System Audio Recording, Accessibility, Automation.
  - It deep-links to the pane, floats a draggable icon of the right item (SpecWithCode.app for computer use and SnapShot, the agent host for agent panes) inside the Settings window, and closes when that pane's grant is detected.
  - Panes that don't accept a drag get a one-line instruction in the same panel instead of the icon.
  - The four defects listed in Problem are fixed, with a test each.
- [ ] AC-07: Every place that tells the user to open a TCC pane goes through the helper. No UI string or agent prompt tells the user to open System Settings by hand.
- [ ] AC-08: An agent refused a protected path calls `request_access` with a new `permission` subject (`full-disk-access`) and a reason. The thread shows the existing card shell with the following:
  - "<Agent> needs Full Disk Access on <machine>" and the agent's reason
  - what it unlocks: Chrome and Safari profiles and history, Mail, Messages, Notes, Photos library, Time Machine, other apps' containers
  - the risk line: "Every agent on <machine>, in every project and with every provider, gets this until you turn it off in System Settings."
  - Open System Settings (opens the helper) and Not now

  There are no "this session" or "always" choices, because an OS grant can't be scoped per thread. The card resolves `allowed` when the probe sees the grant after a restart, `denied` on Not now, and `timed_out` after 10 minutes. A routing line in the orchestration prose replaces text blockers with this call.
- [ ] AC-09: Windows and Linux show no row and no card. `request_access` for `full-disk-access` returns `not_applicable` with the reason: same-user processes can already read other apps' data. Elevated (admin or root) access stays out of scope.
- [x] AC-10: The mockup is accepted by Anton before any code (accepted November 18, 2026).
- [ ] AC-13: Onboarding tells every new Mac user this option exists without forcing it: the existing first-run Access step gets an optional, collapsed "Full Disk Access for agents (optional)" item with what it unlocks, the security warning, "some tasks need it", and Open System Settings. Continue never depends on it, so release walkers keep passing unchanged. `docs/user/full-disk-access.md` is linked from it and from Settings.
- [ ] AC-11: `docs/user/computer-use.md` and a new `docs/user/full-disk-access.md` cover the row, the card, the risk and the drag helper, along with CHANGELOG Unreleased.
- [ ] AC-12: Shipped. The PR is reviewed and green, merged and released. AC-02 is verified on M4 and M5 in the released app.

## Approach

1. **Agent host identity (T-01, which gates everything else).** Run the service under a small signed helper bundle inside the app, for example `SpecWithCode.app/Contents/Library/Helpers/SpecWithCode Agents.app`. Its executable starts the pinned runtime and is registered as the launchd program (or through `SMAppService` with `BundleProgram`). TCC then attributes agent reads to `com.specweave.studio.agents`, a Developer ID requirement with no version, and the System Settings list shows a real name and icon. A spike on M4 must show three things in the TCC log: attribution to the helper, a working grant, and the grant surviving an update. The spike must also check whether the TCC responsibility chain (`responsible_path`) still points to the helper after the hand-off to Node. If it doesn't, the helper must host the runtime in-process, and T-01 grows. Rejected:
   - Granting the shared Node binary: too broad, and it breaks on a Node upgrade.
   - Granting SpecWithCode.app: it doesn't reach agents, as shown on M4.
2. **Probe (T-02).** The agent host stats and opens a protected path that always exists: `~/Library/Safari/CloudTabs.db`, with `~/Library/Mail` as the fallback. EPERM means not allowed. The result, plus the service start time compared with the grant time (shown as "restart needed"), is exposed as `machine.privacyAccess` over RPC, for local and remote machines.
3. **Shared helper (T-03).**
   - `MacPermission.ts` gains `app-data` and `automation` URLs.
   - `MacPermissionHelper.show` takes `{ pane, dragTarget: "app" | "agentHost", isGranted }`. Each pane gets its own `isGranted`: Screen Recording and Accessibility from Electron, Full Disk Access and App Data from the agent-host probe over RPC, Automation from the requested target app.
   - `checkSystemPermission` honours its pane.
   - For panes that don't accept a drag, the helper shows the instruction text instead of the icon.
4. **Settings row (T-04).** It lives in `MachineReadinessChecklist.tsx` under a new "Privacy access" heading. It is not a third worker-permission line, so `decision_machine_access_lines` (exactly two worker lines) still holds.
5. **Card (T-05).** Add `permission` to `AccessRequestSubjectKind`. `AccessRequestCard` gets a variant with the two OS-grant buttons and the risk line. `OrchestratorMcpService.requestAccess` waits on the probe. The routing line goes in the orchestration prose.
6. **Windows and Linux (T-06).** The platform gate in the RPC and the UI.
7. **Docs (T-07).**

Pane facts, to be rechecked on macOS 27 in T-01. "Observed" means seen in code or screenshots here.

| Pane | "+" picker | Drag an item in | Evidence |
|---|---|---|---|
| Screen & System Audio Recording | yes | yes | Observed: Anton's screenshot shows "+"; the helper has shipped drag for this pane since 1.0.5 |
| Accessibility | yes | yes | Observed: the shipped helper and computer-use flow |
| Full Disk Access | yes | to confirm on macOS 27 (bare executables and helper bundles) | Observed: deep link and helper wired for Safari import; drag not proven |
| App Data | to confirm | to confirm | The TCC log shows this service refusing the Chrome read; the list may only fill from the system prompt |
| Automation | no "+" | no; entries appear only after the system prompt, then the user toggles them | To confirm on macOS 27 |

Risks:
- Full Disk Access is machine-wide. Any agent, provider or prompt-injected instruction on that Mac can then read Mail, Messages and browser history. The row and the card say so, and it stays off until the user turns it on.
- A restart interrupts running threads (AC-05).
- If T-01 can't keep a stable responsible process, AC-02's "survives an update" fails, and alternative B becomes the fallback.

## Tasks

### T-01 Signed agent-host helper and TCC spike
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/cloud/bootService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/cloud/pinnedRuntime.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/install/macSelfInstall.ts, repositories/anton-abyzov/specwithcode/scripts/studio-projects/mac-signature.mjs | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/cloud/bootService.test.ts

### T-02 Agent-host privacy probe and machine.privacyAccess RPC
- AC: AC-03, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/system/privacyAccess.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/privacyAccess.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/system/privacyAccess.test.ts

### T-03 One drag helper for every TCC pane, four defects fixed
- AC: AC-04, AC-06, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/desktop/src/permissions/MacPermission.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/permissions/MacPermissionHelper.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/permissions/MacPermissions.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/ipc/methods/window.ts | Test: node node_modules/vite-plus/bin/vp test run apps/desktop/src/permissions/MacPermissionHelper.test.ts

### T-04 Full Disk Access row in the machine readiness checklist
- AC: AC-03, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/MachineReadinessChecklist.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/MachineReadinessChecklist.test.tsx | Test: cd apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/settings/MachineReadinessChecklist.test.tsx

### T-05 request_access permission subject, card variant, routing line
- AC: AC-08 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/accessRequest.ts, repositories/anton-abyzov/specwithcode/apps/server/src/access/accessGate.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/AccessRequestCard.tsx | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/access/accessGate.test.ts

### T-06 Windows and Linux: not_applicable, no row
- AC: AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/system/privacyAccess.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/system/privacyAccess.test.ts

### T-07 Docs and changelog
- AC: AC-11 | Files: repositories/anton-abyzov/specwithcode/docs/user/full-disk-access.md, repositories/anton-abyzov/specwithcode/docs/user/computer-use.md, repositories/anton-abyzov/specwithcode/CHANGELOG.md | Test: grep -q "Every agent on" repositories/anton-abyzov/specwithcode/docs/user/full-disk-access.md

### T-09 Optional Full Disk Access item in the first-run Access step
- AC: AC-13 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/AccessStep.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/AccessStep.test.tsx | Test: cd apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/onboarding/AccessStep.test.tsx

### T-08 Ship and verify on M4 and M5
- AC: AC-10, AC-12, AC-13 | Files: none | Test: specweave verify 1386-full-disk-access-per-machine-and-one-system-settings-drag-helper

## Decisions

### Asked
- D-01 → **A. Full Disk Access on the signed agent host** (Anton, November 18, 2026: "Yes, I like it. Go ahead and implement this fully."). Original question: how much access? Recommended **A. Full Disk Access on the signed agent host**. It is the "really full access" Anton asked for. Agents run arbitrary shell, so only an OS grant on their host lets `ls`, `sqlite3` and Python scripts work. It costs one approval per Mac, then survives updates. **B. Brokered reads** is the alternative: SpecWithCode.app holds Full Disk Access, and agents read protected files only through an MCP tool, with per-thread "this session or always" scopes that are actually enforced. B is safer and narrower, but agent shell commands still fail and every reader needs a new tool. Accepted.

### Defaulted (change any before sw-do)
- D-02: the row is a readiness-checklist row, not a third machine-access line (keeps `decision_machine_access_lines`).
- D-03: the card offers Open System Settings and Not now only, never "this session" or "always", because macOS can't scope the grant.
- D-04: no automatic service restart after a grant.
- D-05: off by default. First run mentions it as an optional, skippable item inside the existing Access step (Anton: the user "must know that this option exists" and treat it carefully). Agents raise the card when they hit a protected path.

### Open
- none

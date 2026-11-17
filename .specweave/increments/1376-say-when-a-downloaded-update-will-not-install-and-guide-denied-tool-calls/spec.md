# Say when a downloaded update will not install, and guide denied tool calls

## Problem

On November 17, 2026 the owner asked twice why a coordinator told him to "Restart this coordinator session with approval prompts enabled". The fix for the underlying fault (increment 1374, SpecWithCode 1.0.334) was merged and published, yet m4 kept running 1.0.329 with 1.0.334 downloaded beside it. Three things kept that from being visible:

- The m4 desktop app has "Install automatically" off. The update agent then stops at `downloaded` and never waits for quiet, so only the app's update button installs. The update card says "SpecWithCode 1.0.334 is downloaded." and Settings says "Version 1.0.334 is ready to install." Neither says it will stay uninstalled. The 1374 report itself told the owner it would install "after 10 quiet minutes".
- When a provider refuses to run the terminal bridge command at all (`tool denied: unsandboxed execution requires human approval, but approval prompts are disabled`), no SpecWithCode text reaches the model, so it invents a remedy. The bridge's own line for a blocked connection suggests "approving the request if one appears" and "switch the thread to Full access", which is wrong on a Full access thread whose prompts are off.
- The release runbook says each Mac's update agent installs a CI release on its next check. That is false while "Install automatically" is off, and `request-release.sh --released` proves publication, not installation.

Evidence: `.specweave/increments/1374-muse-code-threads-on-full-access-keep-full-access-after-a-resume/reports/2026-11-17-restart-demand-why-the-1374-fix-is-not-live-on-m-12c6e0-7f7ae4.md`.

## Scope

In: update-card and Settings wording when a service update is downloaded and "Install automatically" is known to be off; one sentence of denial guidance in the ACP fallback instructions; a corrected bridge line for a sandbox-blocked call; the release runbook's claim about installs; the wrong sentence in the 1374 report.

Out: changing the Muse fallback when a host refuses `:unrestricted` (recorded as an open product gap; no real host has taken that path and it was not probed here); the release workflow and the scripts a release run executes; turning "Install automatically" on for m4 or installing 1.0.334 there, which are the owner's choices.

## Acceptance Criteria

- [ ] AC-01: With a service update in status `downloaded` and the desktop preference `installAutomatically` equal to `false`, the Settings line reads that the version is downloaded, that "Install automatically" is off and that it installs only from Install now. With the preference `true`, unknown or absent, the line is unchanged ("... is ready to install.").
- [ ] AC-02: With the same state, the sidebar update card's description includes one sentence saying "Install automatically" is off on this machine and the update waits for Update now. It is absent when the preference is `true` or unknown, when only an app update is ready, and when the service is merely behind the app with nothing downloaded.
- [ ] AC-03: The ACP fallback instructions tell the agent that a denied or sandbox-blocked terminal call is not fixed by restarting the session, the app or the machine, to quote the denial exactly, and that the thread's access mode decides it. The sentence names no SpecWithCode version.
- [ ] AC-04: The bridge line for a blocked connection keeps the cause, the host and "Restarting the session or the app does not change that", no longer says "approving the request if one appears", and covers a thread that is already on Full access. It stays one line with no stack trace.
- [ ] AC-05: `docs/studio/releasing.md` says a published release is not an installed one, that a Mac with "Install automatically" off installs only from its update button or a rollout request, and that delivery is confirmed by reading the installed version back.
- [ ] AC-06: The 1374 report no longer says m4 updates "after 10 quiet minutes".

## Approach

Files, in order:

1. `apps/web/src/components/settings/UpdatePreferencesSection.logic.ts`: `describeServiceUpdate(state, preferences?)` takes the desktop preferences it already has in the component; the `downloaded` case branches on `preferences?.installAutomatically === false`. `UpdatePreferencesSection.tsx` passes `preferences`.
2. `apps/web/src/components/sidebar/SidebarRestartToUpdate.logic.ts`: `RestartToUpdateOptions.installAutomatically?: boolean`; the service branch adds the sentence only when the option is `false` and the service state is `downloaded`. `SidebarRestartToUpdate.tsx` keeps the value it already reads from `getUpdatePreferences` (`null` until read).
3. `apps/server/src/provider/StudioOrchestrationInstructions.ts`: one sentence appended to `STUDIO_CODE_ACP_FALLBACK_INSTRUCTIONS`. The adapter keeps the last sent instruction state in memory per session, so a resumed session gets the text again on its first turn after a service restart.
4. `apps/server/src/mcp/AcpMcpStdioBridge.ts`: `acpMcpCallFailureLine` wording.
5. `docs/studio/releasing.md`.

Decisions:

- Show the new text only when the preference is known to be `false`. The preference belongs to the desktop app on this machine and the service state to this machine's service, so they describe the same computer. A browser session has no desktop bridge and shows the old text.
- No locale entries: these lines are built from a version number and are not in the phrase catalogs today; a missing phrase falls back to English.
- The instruction sentence is version-neutral. "Update SpecWithCode" would be wrong advice on every version that already has the fix.

Rejected: installing automatically regardless of the switch (it is the owner's setting); failing a Muse open when the host keeps a sandboxed profile (reverses 1374's shipped behaviour on fixture evidence only).

Risk: the bridge line and the instruction are read by models, so wording changes behaviour without a test that can prove it. Tests pin the strings; the review reads them.

## Decisions

### Asked
- none

### Defaulted (change any before sw-do)
- D-01 Muse fallback on a refused `:unrestricted` stays as shipped in 1374 and is recorded in project memory `project_open_product_gaps.md` (reversible).
- D-02 m4 keeps "Install automatically" off until the owner says otherwise; the report asks him (reversible).

### Open
- none

## Tasks

### T-01 Settings and the update card say a downloaded update waits for the button
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/UpdatePreferencesSection.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/UpdatePreferencesSection.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/UpdatePreferencesSection.logic.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/sidebar/SidebarRestartToUpdate.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/sidebar/SidebarRestartToUpdate.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/sidebar/SidebarRestartToUpdate.logic.test.ts | Test: from `apps/web`, `node ../../node_modules/vite-plus/bin/vp test run src/components/settings/UpdatePreferencesSection.logic.test.ts src/components/sidebar/SidebarRestartToUpdate.logic.test.ts`

### T-02 Denied and sandbox-blocked terminal calls get guidance that names no restart
- AC: AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/provider/StudioOrchestrationInstructions.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/StudioOrchestrationInstructions.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/AcpMcpStdioBridge.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/AcpMcpStdioBridge.callFailure.test.ts | Test: from `apps/server`, `node ../../node_modules/vite-plus/bin/vp test run src/provider/StudioOrchestrationInstructions.test.ts src/mcp/AcpMcpStdioBridge.callFailure.test.ts`

### T-03 Runbook and report say published is not installed
- AC: AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode/docs/studio/releasing.md, .specweave/increments/1374-muse-code-threads-on-full-access-keep-full-access-after-a-resume/reports/2026-11-17-what-the-screenshot-shows-c2b8f2-d297cd.md | Test: `grep -c "10 quiet minutes" .specweave/increments/1374-muse-code-threads-on-full-access-keep-full-access-after-a-resume/reports/2026-11-17-what-the-screenshot-shows-c2b8f2-d297cd.md` prints 0 and `grep -c "published release is not an installed one" repositories/anton-abyzov/specwithcode/docs/studio/releasing.md` prints 1

### T-04 Review, merge and release
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/mcp/AcpMcpStdioBridge.ts | Test: PR checks green at the reviewed head; Muse Wonderful xhigh review `Verdict: ship` for that head; `bash scripts/release/request-release.sh --released <merge commit>` exits 0 with a version

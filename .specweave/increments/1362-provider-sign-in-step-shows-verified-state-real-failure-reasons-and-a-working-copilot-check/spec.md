# 1362 Provider sign-in step shows verified state, real failure reasons and a working Copilot check

## Problem

Anton added Gemini CLI and GitHub Copilot to m3 from another machine on November 20, 2026 (app 1.0.404) and could not tell what state either provider was in. Three photos are the evidence (`IMG_0195`, `IMG_0196`, `IMG_9588`).

- Gemini CLI: Google's page said "Authentication successful", the app said "The ACP agent could not complete sign-in." The agent's own reason is dropped at `apps/server/src/provider/acp/AcpRegistryAuth.ts:677` and logged nowhere, so nobody can act on it.
- GitHub Copilot: sign-in stopped at "Could not read which Copilot CLI version is installed." Copilot CLI 1.0.114 prints `GitHub Copilot CLI 1.0.114.` and `readCopilotVersion` does not accept the trailing period (reproduced on M5 with the pinned 1.0.114). Sign-in is impossible on that version.
- The box titled "Already on m3" lists the GitHub CLI sign-in. It reads as "Copilot is already signed in on m3" next to a "Retry sign-in" button.
- A failure message from an earlier attempt stays on screen after the provider is verified signed in.
- A provider the app has not read yet is shown as "No in-app sign-in advertised".
- "Retry sign-in" is offered when only an install or update can help, and "Skip for now" does not say what it leaves behind.

## Scope

In: the Sign in step of Add provider and the shared Account row (`ProviderAuthenticationSection`, also used by the machine readiness checklist); the Copilot version check; the reason shown and logged when an agent rejects sign-in.

Out: any new way of deciding that a provider is signed in (see D-01); Gemini account eligibility itself; changes to grants, credentials or the install recipe; a release.

## Acceptance Criteria

- [ ] AC-01: The Copilot version check reads `1.0.114` from `GitHub Copilot CLI 1.0.114.\nRun 'copilot update' to check for updates.` and device sign-in starts for that output.
- [ ] AC-02: When an agent rejects `authenticate` with an ACP request error, the failed state names the agent and carries its reason on one line of at most 300 characters, with emails masked, URL query strings removed and control characters stripped; the same sanitized text is logged. Any other failure of that call keeps a fixed text.
- [ ] AC-03: A provider already verified signed in on the selected machine shows "Signed in" and "Done" on the Sign in step, with no sign-in prompt, no earlier failure message and no "other sign-ins" box.
- [ ] AC-04: When a provider becomes verified signed in after a failed attempt, the earlier failure message disappears and the step offers "Done".
- [ ] AC-05: A provider that is installed on a remote machine but not signed in shows "Installed on <machine>. Not signed in yet." when the provider reported signed out or the last sign-in failed, and "Installed on <machine>. Sign-in not verified yet." when nothing was verified, with a "Sign in" button and "Skip for now" with one line saying the provider stays added on that machine and cannot run threads until signed in. It never shows "Done" or "Signed in".
- [ ] AC-06: Sign-in state the app cannot read (query error, or the provider missing from that machine's list) is shown as unknown with the machine name, never as "not installed" or "No in-app sign-in advertised".
- [ ] AC-07: A failure that only an install, update or enable can fix shows "Check again" instead of "Retry sign-in"; other failures keep "Retry sign-in". A server that does not send the flag keeps "Retry sign-in".
- [ ] AC-08: The Copilot box is titled "Other GitHub sign-ins on <machine>" and says they are not Copilot CLI's own sign-in; Copilot device-code sign-in, its hints and its existing tests still pass.
- [ ] AC-09: Headless screenshots of the three states (ready, late success, installed not signed in) for a remote machine are saved under the increment's `reports/`.

## Approach

1. `packages/contracts/src/providerSetup.ts`: optional `retryable` on `ProviderAuthState` (absent means retry may help).
2. `apps/server/src/provider/acp/CopilotDeviceAuthentication.ts`: `readCopilotVersion` accepts trailing punctuation.
3. `apps/server/src/provider/acp/AcpRegistryAuth.ts`: a `sanitizeAgentReason` helper; the agent branch surfaces and logs it; preflight and setup failures carry `unavailable`.
4. `apps/server/src/provider/ProviderAuthFlow.ts`: a failed flow publishes `retryable: false` when its error carries `unavailable`.
5. `apps/web/src/components/settings/providerSignInState.logic.ts` (new, pure): one derivation of `unknown | notInstalled | installed | checking | waiting | ready | failed` used by the Account row and the wizard footer.
6. `ProviderAuthenticationSection.tsx`, `ProviderWizardAuthenticationStep.tsx`, `CopilotSignInHints.tsx`: use it; new wording in all eight phrase files.
7. `apps/web/tests/provider-device-auth`: three more fixture scenarios and screenshots.

Rejected: checking readiness by starting a session before login. The driver deliberately treats a discovery session as no proof of sign-in (`AcpRegistryDriver.ts:556`), and the check would run through `start`, which stops running sessions.

Risk: the Account row is shared by every provider. The derivation keeps today's `signedIn` rule unchanged; only what is shown around it changes.

## Decisions

### Asked
- none

### Defaulted (change any before sw-do)
- D-01 "Verified ready" keeps its current meaning: an explicit sign-in the app verified, never a browser callback, an install or a discovery session. A CLI signed in outside the app still needs one sign-in click (for Gemini that click succeeds without a browser when its login is cached). Changing this is an auth change and needs Anton's decision.
- D-02 The agent's reason is shown, sanitized. Only the JSON-RPC message is used; process output is never shown.
- D-03 What counts as signed in is unchanged (D-01), so this is not an auth change: once review and CI are clean it merges and releases under the standing rule.
- D-04 A failed account change on a signed-in provider keeps its reason on screen until that row is closed; a failure from before the sign-in was verified is hidden.

### Open
- none

## Review

- Reviewer: Gemini 4 Neon on Copilot Enterprise, then GPT-6.2 Sol (decision of November 20, 2026). A first pass by Muse Wonder was started by the app's default order and is kept as extra input only.

## Tasks

### T-01 Copilot version check and agent failure reason on the server
- AC: AC-01, AC-02, AC-07 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/providerSetup.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/acp/CopilotDeviceAuthentication.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/acp/CopilotDeviceAuthentication.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/acp/AcpRegistryAuth.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/acp/AcpRegistryAuth.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/ProviderAuthFlow.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/provider/acp/CopilotDeviceAuthentication.test.ts apps/server/src/provider/acp/AcpRegistryAuth.test.ts apps/server/src/provider/ProviderAuthFlow.test.ts

### T-02 Sign-in states in the Account row, the wizard step and the Copilot box
- AC: AC-03, AC-04, AC-05, AC-06, AC-07, AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/providerSignInState.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/providerSignInState.logic.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProviderAuthenticationSection.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProviderAuthenticationSection.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProviderWizardAuthenticationStep.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProviderWizardAuthenticationStep.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/CopilotSignInHints.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/CopilotSignInHints.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases | Test: (from apps/web) node ../../node_modules/vite-plus/bin/vp test run src/components/settings/providerSignInState.logic.test.ts src/components/settings/ProviderAuthenticationSection.test.tsx src/components/settings/ProviderWizardAuthenticationStep.test.tsx src/components/settings/CopilotSignInHints.test.tsx src/i18n

### T-03 Headless screenshots of the three states
- AC: AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/web/tests/provider-device-auth | Test: node apps/web/tests/provider-device-auth/verify.mjs

### T-04 Verify and close 1362
- AC: AC-01, AC-09 | Files: .specweave/increments/1362-provider-sign-in-step-shows-verified-state-real-failure-reasons-and-a-working-copilot-check/reports | Test: specweave verify 1362

# A fair GitHub star prompt

## Problem

SpecWithCode is a public MIT repository, and stars are how other developers find it. Today the app asks only in two places a person has to go looking for: a dismissable link on the first-run screen and a button in Settings > About. People who use the app every day are never asked.

The owner asked for an in-app prompt that stops asking once the person stars and keeps coming back if they don't (November 25, 2026, after reading https://x.com/realchendahuang/status/2125416210120765799).

That post documents how T3 Code grew from 30k to 77k stars in 25 days with such a prompt, and what went wrong with it:

- It first asked after 5 prompts, once (pingdotgg/t3code#27832).
- It was then changed to wait for 30 seconds of idle time and to star from the server with whatever GitHub account that machine holds, followed by confetti (#29922, #29987).
- The repository's review bot flagged the server-side star, and it was merged without a second approval.
- A review (zhilsinger, November 6) showed two problems. On a shared or remote server it stars as someone else, and the account is never shown. The star path was not pinned to the repository, so any client with write scope could star any repository with the server's credential.
- The public reading of the result was "stars bought with a nag". The repository had 129 watchers against 77k stars, and the author had made a video against fake stars earlier that year.

"Keep asking until they star" is the same pressure in a slower form. GitHub's Acceptable Use Policies forbid inauthentic interactions and rank abuse, such as fake or incentivised stars. A prompt that keeps coming back invites exactly that reading.

## Scope

In:

- One calm card that asks for a star after real use, with three answers.
- A capped back-off.
- A read-only "already starred?" check through this machine's own GitHub sign-in.
- One state shared across the person's machines.
- A switch in Settings > About that turns the prompt off.

Out:

- Starring from the app or the server. The button opens the repository in the browser, where the person stars it as themselves.
- Rewards, gating, confetti and telemetry.
- The existing first-run link and the About button, which stay as they are.

## Acceptance Criteria

- [ ] AC-01: The card never shows on first run. It needs at least 5 threads where the person started a turn and at least 3 days since the first such turn on this device. It shows only while the window is focused and the person has been quiet for 15 seconds, never while they type. It never shows in the hosted app, which has no machine of its own.
- [ ] AC-02: The card reads "Enjoying SpecWithCode? A star on GitHub helps other developers find it." and has three buttons: "Star on GitHub", "Already starred" and "Not now". "Star on GitHub" opens https://github.com/anton-abyzov/specwithcode in the browser and never stars on the person's behalf.
- [ ] AC-03: After "Star on GitHub" or "Already starred", the app never asks again. Before the card shows, the app asks this machine's server whether its GitHub sign-in already starred the repository: `GET /user/starred/anton-abyzov/specwithcode`, read-only, with the repository fixed on the server. A yes also ends the asking, and no login or answer leaves the machine.
- [ ] AC-04: "Not now", or closing the card, waits 14 days before the second ask and 30 days before the third. After the third ask it never asks again.
- [ ] AC-05: Settings > About has an "Ask for a GitHub star" switch, on by default. Off ends the asking for good. Turning it back on starts a fresh three-ask budget, and the usage rules still apply.
- [ ] AC-06: The answer is one setting shared across the person's machines, so a star, an "Already starred", a "Not now" or Off on one machine stops the card on the others. It never raises the "settings differ between machines" warning.

## Approach

State lives in the server setting `githubStarPrompt` (`status`: `asking` | `starred` | `done` | `off`, `asks`: 0 to 3, `nextAskAt`: ISO time or null). It is listed among the shared server keys, so the existing sync writes it to every connected machine. A new quiet-key list keeps it out of the mismatch comparison, so a machine that missed a write never shows a warning. Use counts stay on the device in client settings (`githubStarUsage`: `firstUsedAt` and up to 5 thread keys).

Files that change:

- `packages/contracts/src/settings.ts`: the schema and patch keys.
- `packages/client-runtime/src/state/sharedSettings.ts`: the shared and quiet keys.
- `packages/contracts/src/gitHubCredentialCopy.ts`: the `gitHubCredential.starred` RPC, with no payload; the success is `starred` true, false or null.
- `apps/server/src/sourceControl/gitHubSignInRpc.ts`: the handler. It uses the saved token or `gh auth token` and honours a disabled github.com host. It reads 204 as yes, 404 as no, and anything else as unknown, with a 10 s timeout.
- `clientRpcPermissions.ts` and `RpcInstrumentation.ts`: scope and label.
- `apps/web/src/components/github/githubStarPrompt.logic.ts`: pure eligibility and back-off.
- `apps/web/src/components/github/GitHubStarPrompt.tsx`: the card and its mount.
- `ChatView.tsx`: records a started turn.
- `SettingsPanels.tsx` and `settingsSearch.ts`: the switch.

Rejected alternatives:

- "Keep asking until starred": it nags, reads as incentivised stars and risks the repository's standing. The budget is capped at 3.
- Starring from the server: it can star as the wrong account, and it is what the T3 Code review objected to.
- Asking after N prompts in one session: that is too early and interrupts work.

Risks: a machine that is offline during a write keeps its old state until the next write. At worst that is one extra ask on that machine, still inside the cap.

## Decisions

### Asked
- D-01: should the prompt keep asking until the person stars? → Asked by the owner as "keep coming up". Answered by the coordinator's brief: the fair version, with a hard cap of 3 asks and an Off switch (November 25, 2026).
### Defaulted (change any before sw-do)
- D-02: the usage bar is 5 threads with a started turn plus 3 days since first use → default (reversible constants in the logic file).
- D-03: the back-off is 14 days, then 30 days, then stop → default.
- D-04: "Star on GitHub" opens the browser and counts as done without verification, because the person is trusted → default.
### Open
- none

## Tasks

### T-01 Shared star state and the starred check
- AC: AC-03, AC-06 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/settings.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/gitHubCredentialCopy.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/clientRpcPermissions.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/state/sharedSettings.ts, repositories/anton-abyzov/specwithcode/apps/server/src/sourceControl/gitHubSignInRpc.ts, repositories/anton-abyzov/specwithcode/apps/server/src/sourceControl/gitHubStarred.ts, repositories/anton-abyzov/specwithcode/apps/server/src/sourceControl/gitHubStarred.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/observability/RpcInstrumentation.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vitest run src/sourceControl/gitHubStarred.test.ts

### T-02 Prompt logic, card and settings switch
- AC: AC-01, AC-02, AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/github/githubStarPrompt.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/github/githubStarPrompt.logic.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/github/GitHubStarPrompt.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/github/GitHubStarPrompt.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/ChatView.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/SettingsPanels.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/settingsSearch.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vitest run src/components/github

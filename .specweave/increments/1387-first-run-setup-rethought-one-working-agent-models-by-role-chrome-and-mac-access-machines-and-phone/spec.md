# First-run setup rethought: four stages, an Access list, Chrome pairing, one shared walker

After two review rounds this increment was cut to what first-run setup itself needs. Four parts moved to child increments with their criteria: Models to 1393, pairing with no code to paste to 1394, iPhone Mirroring to 1395, SpecWeave and the Board to 1396. AC numbers here did not change; a moved one says where it went. A fifth child, 1398, adds the first feature guide Anton asked for on November 18, 2026. One acceptance by Anton covers all six specs and the prototype.

## Problem

First run gets one agent running and imports projects. It says nothing about what a new user hits next: the browser, the Mac's permissions, the phone, which model does what, and what the Board is. All paths below are in `repositories/anton-abyzov/specwithcode` at `origin/main` `d65dffec9` (November 18, 2026). Three neighbours merged while this plan was written, and the text below counts them as today's app: 1386 put its Full Disk Access block at the end of the Access step (`apps/web/src/components/onboarding/AccessStep.tsx:78`), 1392 changed what the Projects step does with an empty folder (`ProjectsStep.tsx`), and 1391 rebuilt the Board. No other cited file changed since the first pin, `05a2cadba`.

- **Flow today.** Sign in, Agents, Access (only when Full access is recommended), Projects (`apps/web/src/components/onboarding/WelcomeWizard.tsx:55`, `:150-158`). The Access step is one question whose filled button and Enter accept Full access (`AccessStep.tsx`, increment 1294), with 1386's Full Disk Access block under it (`AccessStep.tsx:78`).
- **Chrome.** Signed-in browser work needs a Chrome profile paired with the SpecWithCode Browser extension. Setup never mentions it. Pairing lives in Settings > Chrome and on a card an agent raises after a `chrome_*` call already failed. On October 23, 2026 a scheduled watch got `profiles: []` (1026). On November 2, 2026 an invoice agent asked the user to pick among five unnamed browsers (1172). Gaps in today's flow:
  1. "Add to Chrome" is a plain link (`apps/web/src/components/settings/BrowserExtensionSettings.tsx:253`). It opens in the default browser, which may not be Chrome, and in whichever profile was used last.
  2. After install nothing opens. The icon sits behind Chrome's Extensions menu, and the steps say "Click the SpecWithCode icon in Chrome's toolbar". `onInstalled` only reconnects (`apps/chrome-extension/src/background.js:445`).
  3. A profile is named "Chrome" unless the user types a name (`background.js:75`, `:393`, `apps/server/src/browserExtension/relayHub.ts:174`). A second one becomes "Chrome (2)", and agents must then pass a name (`relayHub.ts:518`).
  4. The popup says to copy the code from "Settings › Chrome" only, and its name example is "EasyChamp admin", the owner's company, in a public extension (`apps/chrome-extension/src/popup.html`).
  5. Nothing in the app says why this is safer than Full Disk Access. The good sentence exists only in the popup's footer.
  6. Pairing never says which Chrome profile gets the extension. The desktop app can already list Chrome's profiles by name and open a link in one (`apps/desktop/src/preview/ExternalBrowsers.ts`, `listExternalBrowsers`, `openInExternalBrowser`), and pairing does not use it. An agent cannot list them at all: from the agent host, reading Chrome's `Local State` returns `Operation not permitted` without Full Disk Access (reproduced on M4, November 18, 2026; 1386 found the same on M5).
  7. One code pairs every profile, and nothing says so. An extension profile keeps one pairing (`background.js:394`), so pairing it with a second computer drops the first without a word. `docs/user/` has no page about Chrome pairing.
- **Mac permissions.** Screen Recording and Accessibility are asked for in the middle of the first computer-use task (`apps/web/src/components/computerUse/ComputerUsePermissions.tsx`). Full Disk Access is 1386's, and 1386 is merged: its block sits at the end of today's Access step (`AccessStep.tsx:78`, `FirstRunFullDiskAccess`).
- **iPhone.** Moved to 1395.
- **Models.** Moved to 1393.
- **SpecWeave and the Board.** Moved to 1396, which also has the record of what happened in "firstproject" on M5.
- **Machines and phone.** Built and released (1296, 1297, and 1327 in 1.0.342). It is the first step and stays as it is.
- **Walkers.** Eleven scripts click through setup, each with its own copy of the English button labels: `scripts/desktop-e2e/installed-e2e.mjs`, `scripts/desktop-e2e/nogit-chat-e2e.mjs`, `scripts/studio-fleet/test-startup.mjs`, `scripts/studio-projects/{acceptance,coordinator-quality,native-acceptance,tutorial-capture}.mjs`, `scripts/studio-verify/{headless-workflow,https-browser-diagnosis,lifecycle-controls,ui-acceptance}.mjs`. PR 228 added the Access step with green PR CI, and release 1.0.261 then failed twice. `.github/workflows/desktop-windows-linux.yml:33-45` now runs the real-app walk on PRs, but only for two first-run paths. The headless fixtures under `apps/web/tests/` run in no workflow: the web unit project includes only `src/**` (`apps/web/vite.config.ts:82`).

## Scope

In:
- A. The flow: four stages, one gate, what is optional.
- C. The Access step as a list: Files and commands, Your browser, Mac apps, with slots for 1386's Full Disk Access item and 1395's iPhone row.
- D. Chrome pairing by copying a code, made as short as today's extension allows, for one profile or several, and the extension's own fixes.
- G. One motion and illustration system for these screens.
- H. One shared setup walker, proven on PRs.
- Translations, user docs, CHANGELOG Unreleased.

Out:
- Models in the Agents step (1393). Pairing with no code to paste and the relay's origin rule (1394). iPhone Mirroring (1395). SpecWeave and the Board (1396).
- Any redesign of the sign-in and join step (1296, 1297) or of device approval (1327).
- Full Disk Access itself: host, probe, restart, its row's text and states (1386).
- A token per Chrome profile, or tokens that expire.
- Reopening setup for people who already finished it. iOS and Android apps.

## Acceptance Criteria

### A. The flow

- [ ] AC-01: The stage bar shows at most four stages in this order: Sign in (Computers where there is no Connect sign-in), Agents, Access, Projects. Access is in the bar, in Back and in Continue only when `accessRows` returns a row (AC-08). Once Access has been shown in a run it stays for that run, whatever happens to its rows.
- [ ] AC-02: One step has a gate. On Agents the filled button reads Continue once one agent is ready, and "Continue without an agent" otherwise, as today. Every other step is passed with one press that chooses nothing. Close and Escape work where `canClose` allows today (a local server and no import running, `WelcomeWizard.tsx:263`).
- [ ] AC-03: Passing every step on its neutral control writes one setting, `onboardingCompletedAt`. It saves no access mode and no model list, requests no pairing code, opens no System Settings pane and sets up no SpecWeave. A test asserts the RPC calls and settings writes of that walk.

### B. Models (Agents step)

- AC-04 to AC-07: moved to 1393.

### C. Access step

- [ ] AC-08: `accessRows(input)` is one pure function. Its input is the list of machines being set up (`setupIds`), each with whether it is this app's own machine, its platform, and whether `shouldRecommendFullAccess` held for it when the step opened or an answer was given in this run; plus whether the window is the desktop app (`window.desktopBridge` exists), plus one optional fact per machine that 1395 supplies, `iphoneMirroring`: `present`, `absent` or `unknown`, read through the desktop bridge. Absent, unknown and a missing value all hide the iPhone row, so the function stays pure and this increment ships without 1395. It returns the rows and the machines each acts on, and the stage shows only when it returns one. A table-driven test covers one machine, three machines, and each kind of window:

  | Row | Acts on | Shown when |
  |---|---|---|
  | Files and commands | each machine being set up for which the recommendation held | at least one such machine |
  | Your browser | this computer | the window is the desktop app and its own machine is being set up |
  | Mac apps | this Mac | the same, and `useComputerUsePermissionsAreLocal` holds (`ComputerUsePermissions.tsx:58`) |
  | Your iPhone | this Mac | added by 1395 |
  | Full Disk Access | per 1386 | 1386's rule |

  A browser tab, on this computer or any other, and the hosted page get only Files and commands. A tab cannot tell whether the server behind it is the same computer (a tunnel or a forwarded port looks like `localhost`), so only the desktop app, which runs on the machine it hosts, shows the rows that act on "this computer". Chrome and the Mac permissions stay reachable from a tab as today, in Settings > Chrome and on the computer-use card.
- [ ] AC-09: Each row has a live state and its own labelled action. One row is open at a time: opening one closes the other. The footer is Back and Continue, and Continue is the only filled button on the step. On every step change focus moves to the new step's neutral footer action, so Enter moves on. When that action is disabled because the step is busy (AC-36), focus goes to the step's heading, which carries `tabindex="-1"`, and moves to the neutral action when it is enabled again unless the person has moved focus since. No row starts selected, and Continue changes no permission, mode, pairing or grant. This replaces 1294's step, where the filled button and Enter accept Full access (D-01).
- [ ] AC-10: Files and commands:
  - Unanswered: "Use Full access" and "Keep Supervised" (or "Keep current access"), both outline buttons, with today's explanation behind "What it allows" (`FullAccessExplanation.tsx`). With several machines the row names them, as today's step does.
  - An answer saves as today (`useFullAccessRecommendation`) and does not leave the step. Today it does (`WelcomeWizard.tsx:325-345`).
  - Answered: one line, with Change while this run still holds the earlier modes. After a relaunch (AC-14) they are gone, so the line has no Change and says where the setting lives.
  - The row stays for the rest of the run after an answer, although `shouldRecommendFullAccess` turns false (`apps/web/src/onboarding/accessRecommendation.logic.ts:31`).
  - Left unanswered, nothing is recorded and the composer's recommendation can still ask.
  - `apps/web/tests/access-recommendation/verify.mjs` asserts the new behaviour: focus starts on Continue, and Enter leaves without an answer.
- [ ] AC-11: Mac apps is one row for Screen Recording and Accessibility. From the shared poll it reads: Allowed (both); Partly allowed, naming the one that is missing; Not allowed; Needs reopening; or Could not check, with Retry, when the poll fails. "Allow" expands the existing checklist unchanged, so the drag helper, Quit & Reopen and "Reset and ask again" for a stale grant (`ComputerUsePermissions.tsx:293`) all stay.
- [ ] AC-12: After Quit & Reopen from first run, setup reopens on Access for the same machines.
  - The checklist takes an optional `onBeforeRelaunch`. Only the first-run row passes it, so a relaunch from a thread's card leaves no marker (`ComputerUsePermissions.tsx:194`).
  - The marker is `{step, environmentId, setupIds, at}`. Quit & Reopen is a full relaunch (`lifecycle.relaunch`, `apps/desktop/src/ipc/methods/computerUse.ts:140`), so memory does not survive it. The main process writes the marker to `first-run-resume.json` in the app's user-data folder and waits for the write before it relaunches. `takeFirstRunResume` claims it by renaming the file and then reading it, so the first caller gets it and every later caller, in this process or the next, gets nothing. Tests: the marker written by one main-process instance is returned by a new one; a second take returns nothing; two windows asking at once get it once; a file older than 10 minutes or unreadable is deleted and returns nothing.
  - `WelcomeWizard` asks once, after its machines have loaded, and starts on that step with those machines only when the marker is under 10 minutes old, its `environmentId` is this window's own machine, every machine in `setupIds` is still listed, and setup is not finished. Otherwise setup starts as usual.
- [ ] AC-13: Full Disk Access is 1386's (its AC-13 and T-09). This increment writes none of its text or states. 1386 is merged, so this increment is the one that moves it: PR B renders 1386's `FirstRunFullDiskAccess` as the list's last row, with its states (Not allowed; Allowed, restart needed; Allowed), Restart agents and risk line unchanged.
- [ ] AC-14: Nothing skipped is lost. After setup, Chrome is in Settings > Chrome and on the Connect Chrome card, the Mac permissions are on the computer-use card, and Full access is in the composer. `docs/user/welcome-wizard.md` lists these.

### D. Chrome

- [ ] AC-15: Why. The row, Settings > Chrome and the Connect Chrome card show the same sentences from one set of strings.
  - Always under the row's heading: "Agents use only the Chrome profiles you pair, and only while they are paired."
  - When the row is open: "They work in the live browser, in a blue tab group you can pull a tab out of. They never read Chrome's files on disk, which Full Disk Access would open to every agent."
  - Beside the profile list, only where it shows: "SpecWithCode reads Chrome's profile names to show this list." (The desktop app reads Chrome's `Local State` for it, `apps/desktop/src/preview/BrowserImport/Sources.ts:585`.)
- [ ] AC-16: One profile or several.
  - Beside the profile list: "Pick the profile where the accounts agents need are signed in."
  - Once a profile is paired the row reads "Paired: {names}" and offers "Pair another profile", which runs the same steps, with: "One profile is enough when everything agents need is signed in there. Pair a second one for a work account or another brand's accounts. The browser tools never reach a profile you did not pair."
  - Pairing another profile on this computer never disconnects the first. With several paired, the row adds "Agents use the profile you name."
- [ ] AC-17: Row states, exactly, with the first that applies shown:
  - Loading. Machine offline. Turned off by team rules (`teamRulesToolLock`, `apps/web/src/components/settings/ChromeSettings.tsx:191`). Not allowed: the window's access cannot change this machine's settings, which is what requesting a code needs (`AuthAccessWriteScope`, `apps/server/src/browserExtension/BrowserExtension.ts:482-488`); this is checked before any action is offered. Chrome not found. None of these has an action.
  - Not set up. Waiting for Chrome. Waiting for your approval (a profile whose state is `pending`). Paired. Paired, not answering (paired and not connected). These have actions.
  - On a paired profile: "Update the extension" when its version is older than `bundledVersion`, and "not from the Chrome Web Store" when `fromStore` is false, as Settings shows today.
  - "Chrome not found" comes from `chromeInstalled` (`apps/server/src/browserBridge/chromeBridgeFacts.ts:67`, macOS only), added to `browserExtension.status` as an optional key. A server that does not send it counts as installed.
- [ ] AC-18: The copy path, which works with today's extension:
  - The profile list. T-07 starts with a check on a fresh macOS user account, recorded in `reports/chrome-profile-read.md`: what `listExternalBrowsers` returns from the installed app, and whether macOS asks to let SpecWithCode "access data from other apps". If it asks before a press, or returns nothing for a normal Chrome, there is no profile list on macOS and the next point applies everywhere.
  - Where the list works, in the desktop app, it is read once "Set up" is pressed and never when the step opens. The person picks a profile by Chrome's own name; with one profile there is no list. "Add to Chrome" opens the store page in that profile with `openInExternalBrowser`, not in the default browser.
  - When the list is empty or cannot be read: "Add to Chrome" is today's link with "It opens in the Chrome profile you used last. To pair another, switch to it in Chrome first."
  - "Copy code" requests the code and copies it in one press without showing it. "Show" reveals it for typing by hand. The code is this machine's standing pairing code, so the row says "Anyone with this code can pair a browser with this computer." When the row turns Paired, or after 120 s, the desktop app clears the clipboard if it still holds the code.
  - The row reads `browserExtension.status` every 3 s while it is open, turns to Paired within 3 s of a profile connecting, and closes its steps. Continue stays enabled the whole time.
  - The steps are one component that Settings > Chrome and the row both render.
- [ ] AC-19: The extension (next store version; `manifest.json` permissions unchanged):
  - On a first install, and only then (`onInstalled` with `reason === "install"`, not an update), it opens its own pairing page in that profile with the code field focused, so paste and Enter pair. Nobody has to find the icon. A test covers install, update and a browser update.
  - The page and the popup say "Copy the code from SpecWithCode: first-run setup, or Settings > Chrome."
  - There is no default name. The field starts empty with one-press suggestions Personal, Work and Agents, and Pair stays off until there is a name. Only one pairing tab is open at a time. "Chrome" and "EasyChamp admin" are gone from the UI and the defaults.
  - A profile already paired as "Chrome" or "Chrome (n)" shows "Give it a name agents can tell apart" in the app's list and in its popup.
  - A profile that is already paired says so before pairing again: "This profile is paired with {machine}. Pairing here replaces that."
- AC-20: moved to 1394.

### E. iPhone

- AC-21 to AC-23: moved to 1395.

### F. SpecWeave and the Board

- AC-24 to AC-31: moved to 1396.

### G. Design and motion

- [ ] AC-32: One motion system, CSS only, no new dependency. `apps/web/src/index.css` defines a soft spring for things that move (about 560 ms, 4% overshoot), a firmer one for small marks (8%), and a 150 ms ease for leaving. First run and the Access rows use only these. Rows follow their heading 40 ms apart and all have started within 300 ms. Leaving is faster than entering. A step plays its entrance the first time it is shown in a run; Back and a second visit use the 150 ms ease, and there is no blank gap between steps.
- [ ] AC-33: One picture per step, and each reacts once to what the person just did: machines joining one thread (Sign in), work passing to review and back (Agents), a thread pulling tight from the agent to each thing it may use (Access), folders becoming cards (Projects). The stage bar is one thread with a knot per stage. Pictures are inline SVG in theme tokens with no text inside, are `aria-hidden`, and use no lock, brain or "thinking" icon. From 880 px of dialog width the picture sits beside the step. From 620 px to 880 px it sits above it, at most 112 px tall. Below 620 px there is no picture. At 390 by 700 px the footer's action is visible without scrolling on every step with no row open.
- [ ] AC-34: Checks, in a headless fixture of the built screens:
  - The new motion changes only `transform`, `opacity`, an SVG stroke's dash offset, and a row's own height. Nothing animates the CSS `d` property or skews text, since the hosted page also runs in Safari.
  - Nothing new loops: five seconds after the last input no element marked `data-motion="setup"` has a running animation. The indeterminate marks that exist today (an agent installing) are not marked and are not judged.
  - With reduced motion nothing moves and every state is immediate, including the change between steps.
  - Opening a row moves only what is below it, and focus stays on the pressed control.
  - After Continue, focus is on the next step's neutral action, or on the step's heading while that action is disabled (AC-09), never on the page body. The fixture shows a busy step and asserts the heading has focus.
  - Screenshots at 390 px and 1280 px, light and dark, are saved in `reports/`, with no sideways scroll.
  - Tab order follows reading order, and focus is visible.
- [ ] AC-35: `reports/onboarding-prototype.html` and `reports/onboarding-tour.mp4` are the reference for layout, wording and motion of the Access step and the stage bar. A built screen that departs from them says why in its PR. The prototype marks what is only sketched: the bodies of Sign in and Projects, which this increment does not change, and the screens that belong to 1393, 1395, 1396 and 1398.
- [ ] AC-44: A named provider always shows its own mark (Anton, November 18, 2026). Wherever setup, the Models block or the first feature guide names an AI provider, an agent or a model, the provider's official mark is drawn beside the name through `ProviderLogo` (`apps/web/src/components/ProviderLogo.tsx`, brand from `providerBrandFor`, marks from `ProviderLogoMarks.tsx`): Claude Code and Claude models the Claude mark, Codex and GPT models the OpenAI mark, Muse Code and Muse models the Meta mark, and so on for every bundled brand. No generic glyph stands in for a provider, no mark is redrawn or generated, and a name with no bundled brand keeps the app's own fallback mark, never another provider's. The Agents step already does this through `ProviderInstanceIcon` (`AgentRows.tsx`); every new row and sentence follows it, including a sentence that names a provider as an example ("such as Codex or Muse Code"). Fixtures assert the mark by `[data-provider-logo]` and its brand, in light and dark. The prototype, the recording and the film draw the same marks, copied from `ProviderLogoMarks.tsx` at `c46e2efe5`. The children carry it as 1393 AC-09 and 1398 AC-18.

### H. Walkers

- [ ] AC-36: The contract.
  - The setup dialog carries `data-wizard-step="<id>"`, where id is the `WizardStep`: `start`, `connection`, `agents`, `access` or `import`.
  - `WizardStepFooter` marks the neutral action with `data-wizard-neutral`: "Use without an account" (Continue once signed in), Continue on `connection`, Continue or "Continue without an agent", Continue on `access` (before PR B: "Keep Supervised" or "Keep current access"), and "Do not import projects".
  - At most one enabled neutral control exists in the dialog at any time. None is allowed while a step is busy as today: joining a machine in `connection`, an install, an import, the middle of a sign-in. Pairing Chrome in Access is never busy: Continue stays enabled and leaving only stops the row's polling.
  - The dialog is the scope, because the footer is rendered outside the step through a portal (`WizardFrame.tsx:211`).
  - A unit test renders every step in its states and fails on two.
- [ ] AC-37: `scripts/studio-verify/first-run-walk.mjs` is the only code that clicks through setup, and the eleven scripts call it.
  - It reads the step id, waits up to 60 s per step for an enabled neutral control, presses it, records the ids, stops when the dialog is gone and fails after 12 steps.
  - On a timeout it fails naming the step id and the enabled buttons on screen.
  - A walk with the app in German passes.
  - A test fails when one of the eleven scripts does not import it, or when any file under `scripts/` other than that test holds one of these setup-only labels: "Use without an account", "Do not import projects", "Keep Supervised", "Keep current access", "Continue without an agent". Continue, Skip and Finish are not banned, since they exist outside setup.
- [ ] AC-38: What a PR proves.
  - The unit tests of AC-36 run in the web shards, and the walker's own tests run in the scripts package's `node --test 'studio-*/**/*.test.mjs'`.
  - "PR Gate (packages)" already installs a headless Chromium (`.github/workflows/checks.yml:153`). It gains one named step, "First-run fixtures", that runs `apps/web/tests/first-run-walk/verify.mjs` and `apps/web/tests/access-recommendation/verify.mjs`. The first drives the real wizard components with mocked RPC and a mocked desktop bridge. It catches contract and layout breaks. It cannot catch server or bridge breaks.
  - The real-app walk catches those. `desktop-windows-linux.yml` already builds the app and runs `installed-e2e.mjs` on Linux and Windows and `verify-built-app.mjs --mode fresh` on macOS. Its path list grows by `apps/web/src/onboarding/**`, `apps/web/src/components/computerUse/**`, `apps/web/src/components/settings/BrowserExtension*.tsx`, `apps/server/src/browserExtension/**`, `packages/contracts/src/browserExtension.ts`, `apps/desktop/src/preview/ExternalBrowsers.ts`, `scripts/studio-verify/first-run-walk.mjs` and `scripts/studio-fleet/test-startup.mjs`. Its three jobs are green on the head before PR A or PR B merges.
  - What is still not proven on a PR: a change elsewhere in `packages/shared` or `packages/contracts` that breaks setup. Listing those folders would build the desktop app on most PRs. Such a break is caught by the release's verify stage, which fails before anything is published.
- [ ] AC-39: PR A, the contract and the walker with setup unchanged, ships alone, and one app release proves it. The app release's own verify stage (`scripts/release/release-verify.sh` in the app repository) runs `verify-built-app.mjs --mode all` on the signed build and writes `receipt.json`. The proof is that receipt, copied to `reports/pr-a-release-receipt.json`: its `result` is `passed` and its `fresh` mode ran. The `upgraded` mode starts from a finished home and walks no setup, so it is not a risk here. PR B changes no walker script.

### Text, gate, review, shipping

- [ ] AC-40: New first-run strings go through `t` or `tx` with entries in de, es, fr, ja, ko, pt, ru and zh. Docs: `docs/user/welcome-wizard.md` (the four stages, what is optional), a new `docs/user/chrome.md` (why, one profile or several, pairing, that one code pairs every profile and Reset disconnects them all, that a profile holds one pairing, pause, unpair). CHANGELOG Unreleased has the entries.
- [ ] AC-41: Anton accepts this spec, the five child specs (1393 to 1396, and 1398), the prototype and the recording, and answers the decisions each asks, before any code in any of the six. The line "Accepted by Anton on <date>" under Decisions here records it, and each child's first task checks for it.
- [ ] AC-42: Muse Wonder Full 1.0 at Extra High, with full access, reviews three things: the six specs with the prototype; every PR at its head; and the whole built flow once this increment's PRs are released. For the last one a fresh install in a throwaway home is walked headless, with a screenshot of every step and state (light and dark, 390 px and 1280 px) and one recording, and judged for gaps, edge cases, consistency, how obvious each step is, and the quality of layout and motion. Every finding is fixed or answered in `reports/reviews/`.
- [ ] AC-43: Shipped. Each PR is green, reviewed, merged and released. Pairing a Chrome profile and allowing the Mac permissions are Anton's to press.

## Approach

### The flow

| # | Stage | Required? | What it settles | Change |
|---|---|---|---|---|
| 1 | Sign in | Optional, recommended | Connect account, this machine's link, main machine and its code, the phone | None |
| 2 | Agents | The one gate: one agent ready, or "Continue without an agent" | Agent install and sign-in | None here. 1393 adds the Models block |
| 3 | Access | Optional | **Files and commands, Your browser, Mac apps**, then 1395's iPhone row and 1386's item | A list with one neutral Continue |
| 4 | Projects | Optional | Import | None |
| later | Per project | Asked where a project is made, and when a plan is asked for | SpecWeave and its board | 1396 |

Why this order:
- Sign in first, because it links the machine and lists the others.
- Access comes after Agents, because Full access is recommended for the machines being set up, and the browser and the Mac are the next things an agent reaches for.
- SpecWeave is not a stage. Setup is per machine and SpecWeave is per repository, and at first run there may be no project yet.

Every grant is one labelled press: "Use Full access", "Allow", "Copy code". Continue and Enter never grant.

### The six increments

| Increment | What | Waits for |
|---|---|---|
| 1387 (this one) | Walker contract; the Access list; Chrome by copy; the extension's fixes; motion | Acceptance |
| 1393 | Models block in Agents | PR 532, and this increment's PR B |
| 1394 | Pairing with no code to paste; the relay accepts only the store extension | Its own spike, which can end it |
| 1395 | iPhone Mirroring row and examples | Its own proof on a real phone, and PR B |
| 1396 | SpecWeave when a project is made, when a plan is asked for, and on the Board | Nothing. It touches no first-run file |
| 1398 | First feature guide in a sample project: SpecWeave on, a plan, the Board, review, Done | Its own run by hand, which can end it; then 1396 and 1393, and PR 532 for the reviewer default. It is offered after setup and touches no first-run file |

### Order of work here

1. **PR A, walker contract (T-02 to T-04).** No change to setup. Released and proven by a release receipt before anything else in first run merges.
2. **PR B, the Access step (T-05 to T-09).** The Full Disk Access row is 1386's merged block, moved into the list, and the iPhone slot does not wait for 1395.
3. **PR C, the extension (T-10).** The update goes through store review, which takes days because of its `debugger` permission. The app keeps working with the current extension.
4. **Text, the whole-flow review, close (T-11 to T-13).**

### Rejected

- One stage per topic. That gives eight stages, and every stage is a walker hazard.
- A checklist after setup instead of rows in it. Anton asked for these in onboarding.
- Rows that start selected with one Continue. Enter would grant.
- Showing the browser and Mac rows in a browser tab that looks local. A forwarded port looks the same and points at another computer.
- A motion library. CSS springs do this, and the app has none today.
- Walkers that leave with Escape, or eleven updated label lists. The first proves nothing and the second is what failed in 1.0.261.
- One increment with five PRs. Two review rounds showed it could not be reviewed or shipped as one.

### Risks

- The Access step changes what Enter does (D-01). Nobody who answered already sees it again.
- The profile list may not be readable on a fresh Mac. AC-18 checks first and has a fallback that needs no list.
- The extension update needs store review. PR C can wait on it without holding the rest.
- `SignInFirstStep.tsx` belongs to the 1296 and 1297 thread. Only one attribute changes there, and that thread sees PR A before it merges.
- 1386 already edited `AccessStep.tsx` and is merged. PR B moves its block into the list without changing it (AC-13).
- 1392 (PR 570) changes what the Projects step does with an empty folder: it becomes a new Git repository through `projects.createNew`. This increment does not rewrite that step's import loop. PR A adds only its walker attributes there, rebased on 1392, and the walker leaves the step on its neutral control, so it never picks a folder. 1396 AC-22 adds one box to that row later.
- The app checkout is shared. Every PR is built in a `specweave-studio checks copy`.

## Decisions

Accepted by Anton on November 18, 2026. His words: "Yes, I really loved all of this." That accepts the six specs, the prototype and the recording, with the recommended answer to every asked decision: D-01 A here, 1396 D-01 A and D-02 A, 1395 D-01 A, 1394 D-01 A and D-02 A, 1398 D-01 A and D-02 A. In the same message he asked for two more things: a named AI provider always shows its correct icon (AC-44), and promotion videos for an English and a Russian audience (increment 1410).

### Asked
- D-01, for Anton: the Access step. Today its filled button and Enter turn on Full access (1294). With three or more things on the page, recommended **A. A list where each row has its own button, and Continue and Enter grant nothing.** B. Keep Full access as its own question first, with Enter accepting, and show the other rows after it. A is recommended because a default that grants one of several things is a surprise, and A gives the release walkers one rule for every step. A reverses what 1294 shipped. **Decided November 18, 2026: A.**
- D-02: moved to 1396 (SpecWeave's default, and asking before setting it up).
- D-03: moved to 1395 (posting from the phone).
- D-04: moved to 1394 (pairing with no code to paste, and the relay's origin rule). This increment ships the copy path either way. Later on November 18, 2026 Anton dropped "Pair in Chrome" (1394 D-01 is now B), so this copy path is the only way to pair a Chrome profile. The relay change of 1394 still ships.

### Defaulted (change any before sw-do)
- D-05: Four stages. The browser and the Mac inside Access; Models, iPhone and SpecWeave in their own increments.
- D-06: The sign-in, join and phone step is not changed.
- D-07: Full Disk Access is 1386's row. The Chrome row is where its safer alternative is explained.
- D-08: The rows that act on "this computer" show only in the desktop app. The Chrome profile is picked there where the list can be read; otherwise it is the one Chrome used last.
- D-09: A paired profile must have a name the user chose.
- D-10: No reminder after setup.
- D-11: "Cloth motion" is read as soft spring motion with follow-through, and "serial video with Meta Muse" as the adversarial review by Muse Wonder Full at Extra High.
- D-12: Six increments under one acceptance, not one increment with six PRs.
- D-13: The pairing code stays one per machine. The row says what it is and the clipboard is cleared after use.

### Open
- none

## Review

- Reviewer: meta (muse-wonder-full-1.0)
- Depth: deep
- Required: yes

Round 1 said "fix first" with eight blockers: `reports/reviews/review-r1-responses.md`. Round 2 said "fix first" with eight more and asked for the split: its text is `reports/reviews/review-r2.md` and the answers are `reports/reviews/review-r2-responses.md`.

## Tasks

### T-01 Acceptance: Anton accepts the six specs, the prototype and the decisions
- AC: AC-41 | Files: none | Test: grep -q "Accepted by Anton on" .specweave/increments/1387-first-run-setup-rethought-one-working-agent-models-by-role-chrome-and-mac-access-machines-and-phone/spec.md

### T-02 Step and neutral attributes, one shared walker, eleven scripts rewired
- AC: AC-36, AC-37 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/WizardFrame.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/WelcomeWizard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/SignInFirstStep.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/ConnectionStep.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/AgentsStep.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/AccessStep.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/ProjectsStep.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/WelcomeWizard.contract.test.tsx, repositories/anton-abyzov/specwithcode/scripts/studio-verify/first-run-walk.mjs, repositories/anton-abyzov/specwithcode/scripts/studio-verify/first-run-walk.test.mjs, repositories/anton-abyzov/specwithcode/scripts/desktop-e2e/installed-e2e.mjs, repositories/anton-abyzov/specwithcode/scripts/desktop-e2e/nogit-chat-e2e.mjs, repositories/anton-abyzov/specwithcode/scripts/studio-fleet/test-startup.mjs, repositories/anton-abyzov/specwithcode/scripts/studio-projects/acceptance.mjs, repositories/anton-abyzov/specwithcode/scripts/studio-projects/coordinator-quality.mjs, repositories/anton-abyzov/specwithcode/scripts/studio-projects/native-acceptance.mjs, repositories/anton-abyzov/specwithcode/scripts/studio-projects/native-acceptance.test.mjs, repositories/anton-abyzov/specwithcode/scripts/studio-projects/tutorial-capture.mjs, repositories/anton-abyzov/specwithcode/scripts/studio-verify/headless-workflow.mjs, repositories/anton-abyzov/specwithcode/scripts/studio-verify/https-browser-diagnosis.mjs, repositories/anton-abyzov/specwithcode/scripts/studio-verify/lifecycle-controls.mjs, repositories/anton-abyzov/specwithcode/scripts/studio-verify/ui-acceptance.mjs | Test: cd repositories/anton-abyzov/specwithcode && node --test scripts/studio-verify/first-run-walk.test.mjs scripts/studio-projects/native-acceptance.test.mjs && cd apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/onboarding

### T-03 The fixture walk as a named CI step, and the wider path list
- AC: AC-38 | Files: repositories/anton-abyzov/specwithcode/apps/web/tests/first-run-walk/index.html, repositories/anton-abyzov/specwithcode/apps/web/tests/first-run-walk/main.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/first-run-walk/mocks.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/first-run-walk/verify.mjs, repositories/anton-abyzov/specwithcode/apps/web/tests/first-run-walk/vite.config.ts, repositories/anton-abyzov/specwithcode/.github/workflows/checks.yml, repositories/anton-abyzov/specwithcode/.github/workflows/desktop-windows-linux.yml | Test: cd repositories/anton-abyzov/specwithcode && node apps/web/tests/first-run-walk/verify.mjs && grep -q "First-run fixtures" .github/workflows/checks.yml

### T-04 Ship PR A and keep the receipt of the release that verified it
- AC: AC-39 | Files: none | Test: python3 -c "import json,sys; r=json.load(open('.specweave/increments/1387-first-run-setup-rethought-one-working-agent-models-by-role-chrome-and-mac-access-machines-and-phone/reports/pr-a-release-receipt.json')); sys.exit(0 if r['result']=='passed' and 'fresh' in r['modes'] else 1)"

### T-05 Access step as a list, the Files and commands row, and the stage rule
- AC: AC-01, AC-02, AC-03, AC-08, AC-09, AC-10, AC-13 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/AccessStep.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/AccessRow.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/WelcomeWizard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/WizardFrame.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/WelcomeWizard.access.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/onboarding/accessRows.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/onboarding/accessRows.logic.test.ts, repositories/anton-abyzov/specwithcode/apps/web/tests/access-recommendation/main.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/access-recommendation/verify.mjs | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/onboarding/WelcomeWizard.access.test.tsx src/onboarding/accessRows.logic.test.ts && node tests/access-recommendation/verify.mjs

### T-06 Check on a fresh Mac account what the profile list returns
- AC: AC-18 | Files: none | Test: grep -Eq "^Result: (list works|no list)" .specweave/increments/1387-first-run-setup-rethought-one-working-agent-models-by-role-chrome-and-mac-access-machines-and-phone/reports/chrome-profile-read.md

### T-07 Your browser row: why, one or several, states, the copy path
- AC: AC-15, AC-16, AC-17, AC-18 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/BrowserExtensionSetup.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/BrowserExtensionSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ChromeConnectCard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/ChromeAccessRow.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/ChromeAccessRow.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/onboarding/chromeRowState.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/onboarding/chromeRowState.logic.test.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/browserExtension.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/ipc.ts, repositories/anton-abyzov/specwithcode/apps/server/src/browserExtension/BrowserExtension.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preload.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/ipc/channels.ts, repositories/anton-abyzov/specwithcode/apps/web/src/browser/externalBrowsers.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/onboarding/ChromeAccessRow.test.tsx src/onboarding/chromeRowState.logic.test.ts src/components/settings

### T-08 Mac apps row, and reopening on the same step for the same machines
- AC: AC-11, AC-12 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/MacAppsRow.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/MacAppsRow.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/WelcomeWizard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/WelcomeWizard.resume.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/computerUse/ComputerUsePermissions.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/onboarding/firstRunResume.ts, repositories/anton-abyzov/specwithcode/apps/web/src/onboarding/firstRunResume.test.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/ipc.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preload.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/ipc/channels.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/ipc/methods/computerUse.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/ipc/methods/computerUse.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/onboarding/MacAppsRow.test.tsx src/components/onboarding/WelcomeWizard.resume.test.tsx src/onboarding/firstRunResume.test.ts && cd ../desktop && node ../../node_modules/vite-plus/bin/vp test run src/ipc/methods/computerUse.test.ts

### T-09 Motion tokens, the four pictures, the thread stage bar, and their checks
- AC: AC-32, AC-33, AC-34, AC-35, AC-44 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/index.css, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/WizardFrame.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/StepPicture.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/StepPicture.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/first-run-walk/motion.mjs | Test: cd repositories/anton-abyzov/specwithcode && node apps/web/tests/first-run-walk/motion.mjs

### T-10 Extension: pairing page on first install, a chosen name, clearer words
- AC: AC-19 | Files: repositories/anton-abyzov/specwithcode/apps/chrome-extension/manifest.json, repositories/anton-abyzov/specwithcode/apps/chrome-extension/src/background.js, repositories/anton-abyzov/specwithcode/apps/chrome-extension/src/popup.html, repositories/anton-abyzov/specwithcode/apps/chrome-extension/src/popup.js, repositories/anton-abyzov/specwithcode/apps/chrome-extension/src/pair.html, repositories/anton-abyzov/specwithcode/apps/chrome-extension/src/pair.js, repositories/anton-abyzov/specwithcode/apps/chrome-extension/test/background.test.js, repositories/anton-abyzov/specwithcode/apps/chrome-extension/test/extension.test.js, repositories/anton-abyzov/specwithcode/apps/chrome-extension/store/SUBMISSION.md, repositories/anton-abyzov/specwithcode/apps/server/src/browserExtension/relayHub.ts, repositories/anton-abyzov/specwithcode/apps/server/src/browserExtension/extensionVersion.generated.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/chrome-extension && node ../../node_modules/vite-plus/bin/vp test run

### T-11 Translations, docs and the changelog
- AC: AC-14, AC-40 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/i18n/messages/en.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/messages/de.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/messages/es.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/messages/fr.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/messages/ja.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/messages/ko.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/messages/pt.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/messages/ru.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/messages/zh.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/de.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/es.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/fr.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ja.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ko.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/pt.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ru.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/zh.ts, repositories/anton-abyzov/specwithcode/docs/user/welcome-wizard.md, repositories/anton-abyzov/specwithcode/docs/user/chrome.md, repositories/anton-abyzov/specwithcode/CHANGELOG.md | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/i18n

### T-12 Review each PR, ship, then the whole-flow review of the released app
- AC: AC-42, AC-43 | Files: none | Test: ls .specweave/increments/1387-first-run-setup-rethought-one-working-agent-models-by-role-chrome-and-mac-access-machines-and-phone/reports/reviews/

### T-13 Verify and close 1387
- AC: AC-42, AC-43 | Files: none | Test: specweave verify 1387-first-run-setup-rethought-one-working-agent-models-by-role-chrome-and-mac-access-machines-and-phone

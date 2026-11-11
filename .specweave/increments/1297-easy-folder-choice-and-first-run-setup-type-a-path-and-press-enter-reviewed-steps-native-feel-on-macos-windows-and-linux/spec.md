# Easy folder choice and first-run setup: type a path and press Enter, reviewed steps, native feel on macOS, Windows and Linux

## Problem

Anton, November 11, 2026, with a photo of Add project on a new Mac: "When I create a project from a folder, you see a gap. I will have to choose the folder by opening a folder. There is no way to click Enter or whatever, so you must rethink and review all those initial onboarding steps (for example, when I use this machine as the main one or when I want to connect as well). Those UI elements must be in style for macOS, Linux, and Windows, rendered properly and nicely, with the best UI/UX… It must be easy to specify the folder when I'm using a new project from the folder."

The same day, with a photo of Settings > Machines on that Mac: "I tried to connect my phone to this new M2 device. I just saw I had to click on a button and load something for mobile connection in the section where it says Your Phone. In fact, the most appropriate and the most intuitive way is to use SpecWithCode Connect, and it seems like it's not so clear on the mobile application and on the web… It's not always so clear what to do, right?"

All paths below are in the SpecWithCode app, `repositories/anton-abyzov/specwithcode-dev`, read at `cf266b8344`.

**A. Choosing a folder.** The first photo is Add project > Local folder: the command palette's own browse list, which increment 1272 left out of scope when it rebuilt the New project picker.

1. To add a folder you must open it. A folder row only navigates (`apps/web/src/components/CommandPalette.logic.ts:570-581`); the folder you are inside is the choice, and nothing on screen says so.
2. A folder with no subfolders shows one ".." row and nothing else. The hint "Press Enter to create this folder…" exists only when the list has no rows at all (`apps/web/src/components/CommandPalette.tsx:4369-4372`), and no text ever says "Enter adds this folder".
3. The only confirm control is a 26 px outline chip "Add [Enter]" inside the input, out of the Tab order (`CommandPalette.tsx:4106-4110`). It reads as a keyboard hint, not a button.
4. Enter changes meaning without notice. With any row highlighted, by arrow keys or by the pointer resting on it, Enter opens that row and adding needs Cmd+Enter (`CommandPalette.tsx:3741`, `:3879-3882`, `:4239-4242`).
5. After Enter the panel shows one grey line while it looks for copies on other machines, and a second Enter returns silently (`CommandPalette.tsx:3238`).
6. The system folder dialog is a faint footer link, "Open in Finder" (`CommandPalette.tsx:4165-4174`). In New project it is offered on macOS only (`CommandPalette.tsx:1101-1113`). The dialog itself gets no title and no button label (`apps/desktop/src/electron/ElectronDialog.ts:107-127`).
7. There are no recent folders, places, Git or project marks in this list, and a folder cannot be dropped anywhere outside the chat composer (`apps/web/src/components/chat/folderDrop.ts` is the only consumer of `getPathForFile`).
8. In New project the typed path is hidden behind a small icon or the `/` key, has no completion and closes on blur (`apps/web/src/components/studio/FolderBrowser.tsx:279-302`, `:330-348`).
9. First run cannot take a folder at all. Its last step lists only projects found from Claude Code and Codex; with none found the one working button is "Do not import projects" (`apps/web/src/components/onboarding/WelcomeWizard.tsx:1734-1767`), and the person lands on "Add project", which opens the list above.

Not proven from code: on current `main`, Enter with a typed existing folder and no highlighted row does call the add (`CommandPalette.tsx:3879-3892`). Which of points 2 to 5 stopped Anton is the first task's job to find by reproducing the photo's state.

**B. First-run steps** (`WelcomeWizard.tsx`, 2,028 lines; `JoinMachineSteps.tsx`; `settings/FleetInvite.tsx`).

1. No progress bar on the first screen or on the join path (`WelcomeWizard.tsx:128`, `:324-334`).
2. Neither first choice is the default, and clicking "Start as a main machine" saves at once with no way back (`JoinMachineSteps.tsx:44-62`, `WelcomeWizard.tsx:343-346`).
3. Escape does nothing on any step (`WelcomeWizard.tsx:293-297`).
4. Sign-in to SpecWithCode Connect is a folded row marked "Optional", and opened it tells the person to run `specweave-studio connect` on each computer, including the one the app is running on (`WelcomeWizard.tsx:616-621`, `:670-672`).
5. Join path: after sign-in the step says "Now link this machine under Settings > Machines", which sits behind the dialog (`FleetInvite.tsx:824-830`). Enter does not submit the form (`FleetInvite.tsx:235-240`, `:424-432`). The last screen has no Done, and setup reopens on every launch while joined (`JoinMachineSteps.tsx:186-199`, `apps/web/src/onboarding/firstRun.logic.ts:140-142`).
6. The skip and back buttons sit in a different place on every step (`JoinMachineSteps.tsx:75-80`, `:144`, `:192-198`; `WelcomeWizard.tsx:1755-1758`).
7. The window cannot be dragged during first run: `/welcome` and the wizard declare no drag region.

**C. One look on three systems.** Windows and Linux share one branch for window chrome (`apps/desktop/src/window/DesktopWindow.ts:380-387`), and the web app knows only "Mac or not": no `data-platform`, no Linux helper, one root class for Windows (`apps/web/src/main.tsx:30-33`). So every dialog puts its default button last (`apps/web/src/components/ui/dialog.tsx:156`), prints the word "Enter" on a Mac (`CommandPalette.tsx:4137`), uses 6 px scrollbars everywhere (`apps/web/src/index.css:733-756`), names no Linux font (`apps/web/src/styles/base.css:167`), and offers the system folder dialog unevenly (A6).

**D. Connecting a phone.**

1. Settings > Machines puts "Your phones" third, under a four-step machine list. Once the machine is linked, the section has text and no button, so the only button in the phone area is "Pair a phone", the private QR fallback (`apps/web/src/components/settings/PhoneConnectSettings.tsx:184-190`, `PairPhoneSettings.tsx:209-220`). That is the button Anton pressed.
2. It says "sign in with the same account" and never names the account. It says iPhone only; an Android app exists.
3. In a browser the section is hidden and the QR flow becomes the primary button, with `specweave-studio pair --tailscale` as the instruction (`PhoneConnectSettings.tsx:44-46`, `PairPhoneSettings.tsx:194-196`, `:284-291`).
4. A phone browser that opens a machine's address gets "Pair with this environment" and a token field, with no Connect sign-in (`apps/web/src/components/auth/PairingRouteSurface.tsx:94-117`).
5. The iPhone app leads with Connect, but with no computers yet its steps differ from the desktop's, say "Mac" only, and wait for a tap on "Check again" (`apps/ios/SWCKit/Sources/SWCFeatures/Connect/ConnectViews.swift:55-77`). Every add entry after setup is "Pair with a link or QR code" (`Settings/GlobalSettingsSheet.swift:73`, `Machines/MachineViews.swift:14-39`).

**E. The Machines page.** It opens with a paragraph about agent permissions and has no summary of this machine and no next step (`apps/web/src/components/settings/MachinesSettings.tsx:200-242`). At most one primary button exists, and none once Connect is on. Visible text says "environment", "Local environment", "join line", "Network access or Tailscale HTTPS", "Manage relay permission". "Publish agent activity" says it works "without SpecWithCode Connect" while its switch is disabled unless signed in (`ConnectionsSettings.tsx:2008-2030`). Two command names appear, `specweave-studio` and `specwithcode`.

## Scope

In: the web and desktop app and the native iOS app.

- One address bar for choosing a folder, used by Add project > Local folder, New project, the clone destination and first run: typed or pasted path, Enter to confirm, completion, recent folders, drag and drop, and the system folder dialog on all three desktop systems.
- The first-run flow end to end: this machine as the main one, joining a main machine, sign-in to SpecWithCode Connect, and choosing projects.
- Platform conventions for macOS, Windows and Linux in these screens and in the shared dialog, wizard and key-label components.
- "Connect your phone" Connect-first on desktop, in a browser and in the iOS app.
- A readable Settings > Machines page that always shows the next step.
- Where the Help assistant's `HelpLink` goes on these screens.

Out: the Android app (it has the same gaps, `apps/android/.../MachinesScreen.kt:105-129`; follow-up); `apps/mobile`, which is not shipped; the join code, approval, whose-machine choice, Connect account on machine cards and the Command line card (1296); what Full access means and its step's content (1294); create and publish error texts and unreadable or symlinked folders (1286); the agent tool `studio_project_create` (1288); the Help assistant itself (1298); a QR code that signs the phone in; Change project folder; restyling every other screen to the new conventions; changing what any machine setting does.

### How this sits with the other increments

| Increment | Relation |
|---|---|
| 1272 (done) | **Builds on.** Its `FolderBrowser` becomes the list in Add project too, which 1272 left out. Its breadcrumb stays (AC-09). |
| 1286 | **Builds on, no duplicate.** The address bar's status line shows 1286's typed permission error and its creates-or-uses answer. Both edit `FolderBrowser.tsx`; whichever lands second rebases. |
| 1288 | **No overlap.** Agent creation has no UI here. Both use the machine's suggested projects folder as the "Projects" place. |
| 1294 | **Builds on; lands first.** Its Access step is stage 4 of the bar in AC-12 and takes the shared footer from AC-13 with no content change. This increment's wizard tasks start after 1294 merges, because both edit `WelcomeWizard.tsx`. |
| 1296 | **Builds on; folds two points into it.** The join step shows 1296's code panel; this increment owns only the step's frame (AC-17). The stale "Settings > Connections" text and the CLI name inside the join flow stay 1296's (its AC-21). The Machines page tasks here start after 1296's T-05 and T-07, which edit the same files. |
| 1298 | **Consumes.** Its `HelpLink` is placed per AC-43. |

## Acceptance Criteria

Choosing a folder:

- [ ] AC-01: Add project > Local folder shows a panel with an address bar that has focus, a system-dialog button, the 1272 folder list with Places and Recent, one line saying what will be added and on which machine, and a full-size primary button in the footer. The old ".." list is gone.
- [ ] AC-02: Enter always acts on the folder shown in the address bar, and the primary button names that action: "Add project", "Add <name>", "Create and add" for a folder that does not exist yet, "Open project" for a folder that is already one. No modifier key is ever needed to add. Up and Down put the highlighted folder into the bar; Tab or Right opens it; Left, or Backspace at a separator, goes to the parent. The pointer resting on a row changes nothing that Enter does.
- [ ] AC-03: Typing completes from the folders in the current directory like a browser address bar: the completion is selected, one Backspace removes it, and a name with no match is left alone. Matching ignores case on macOS and Windows machines.
- [ ] AC-04: Pasting takes what people copy: quoted paths, `file://` links, a trailing newline, shell-escaped spaces, `~`, and drive or UNC paths for a Windows machine. A path of the wrong kind for the target machine is refused in the bar with the reason, before any request.
- [ ] AC-05: Under the bar one status line states what the folder is: found (with "Git repository" or "empty"), will be created, not found on <machine>, cannot be read (1286's error), or already the project <title>. A folder with no subfolders says "No folders inside. <name> itself becomes the project."
- [ ] AC-06: Recent lists up to 5 folders per machine, newest first: folders added or chosen through any address bar, then parents of existing projects. It survives a restart, and a folder that is gone drops out when the list is read.
- [ ] AC-07: In the desktop app, dropping a folder from the file manager onto the panel fills the bar and adds nothing. A dropped file uses its folder and says so. When the target is another machine, or in a browser, the drop is refused with one sentence: type or paste the path instead.
- [ ] AC-08: The system-dialog button is a labelled button beside the bar on macOS, Windows and Linux when the target is this device (and WSL, as today): "Choose…" on macOS, "Browse…" on Windows and Linux, with Cmd+O or Ctrl+O. The dialog has the title "Choose a project folder", a confirm button that names the action, and opens in the folder shown. For another machine the button is disabled and says why.
- [ ] AC-09: New project and the clone destination use the same bar. Without focus it shows 1272's breadcrumb, each segment a button; a click on its empty part, `/`, Cmd+L or Ctrl+L, or a paste turns it into the editable path, and Escape turns it back.
- [ ] AC-10: Within 100 ms of Enter the primary button reads "Adding…" and is disabled; "Looking for copies on other machines…" shows in the status line; a second Enter is ignored with the button already showing why; a failure keeps the panel open with the reason.
- [ ] AC-11: The photo's state (an existing folder with no subfolders typed in full, then Enter) adds the project in the headless fixture and in the installed macOS app. The task report names the cause of the November 11 failure, or says it did not reproduce and on which build.

First run:

- [ ] AC-12: Every step shows the stage bar. Main path: This Mac, Connect, Agents, Access, Projects. Join path: This Mac, Sign in, Join. "Mac" reads "PC" on Windows and "computer" on Linux.
- [ ] AC-13: Every step has one footer: Back on the left (none on the first step), then the skip action and the primary action in the system's order. The primary shows the Enter key label, and Enter triggers it from anywhere in the step except a terminal. Focus starts on the first field that must be filled, else on the primary.
- [ ] AC-14: Escape and the close button do the same thing, wherever closing is allowed today: finish setup with nothing more chosen. While an import runs both are off and the footer says so.
- [ ] AC-15: The first step is two cards with "My main machine" preselected. Arrow keys choose, Enter continues, and nothing is saved until Continue. Back from the next step returns with the choice kept and no setting written twice.
- [ ] AC-16: The Connect step leads with sign-in. One "Sign in" signs in and links this machine, then reads "Linked as <email>". No terminal command is shown for the machine the app runs on. Each failure has its own text and action: sign-in did not load (Retry), signed in but not linked (reason, Try again), this window may not link it (where to do it). "Skip for now" continues; a pairing link is a secondary "Add a computer by pairing link".
- [ ] AC-17: On the join path, sign-in and linking happen in the dialog; nothing sends the person to Settings. The Join step shows 1296's join panel when that has shipped, otherwise today's form with Enter submitting it. The joined state has a primary "Done" that completes setup, and setup does not reopen on the next launch.
- [ ] AC-18: The Projects step takes a folder on this machine through the address bar, the system dialog or a drop, beside the found list and links to New empty project and Clone. With nothing found it still has a working primary once a folder is entered.
- [ ] AC-19: During first run the window can be dragged by its top strip on all three systems, and at the minimum window size (840 by 620) the dialog is clear of the traffic lights and caption buttons with its footer visible.
- [ ] AC-20: `WelcomeWizard.tsx` ends at or under 1,500 lines; each step is its own file.

Native feel:

- [ ] AC-21: `<html>` carries `data-platform` (`macos`, `windows`, `linux`) in the desktop app and in a browser. One module answers key labels, the modifier, the file manager's name, the system-dialog button label, the dialog button order and the word for the device. The screens in this increment ask it and never read `navigator.platform`.
- [ ] AC-22: Dialog and wizard footers put the default button last on macOS and Linux and first on Windows. Key labels are ↵, ⇥ and ⌘ on macOS, and Enter, Tab and Ctrl+ on Windows and Linux.
- [ ] AC-23: Windows uses Segoe UI Variable where installed; Linux uses the desktop's interface font with named fallbacks (Adwaita Sans, Cantarell, Ubuntu, Noto Sans). No key label or ellipsis renders as a missing-glyph box on any of the three.
- [ ] AC-24: Controls and dialogs take their corner radius from a per-system token (8 and 14 px on macOS, 4 and 8 on Windows, 6 and 12 on Linux). Scrollbars in the pickers stay thin overlays on macOS and are at least 10 px wide and visible while content overflows on Windows and Linux.
- [ ] AC-25: With Windows contrast themes (`forced-colors: active`) fields, rows, the selection, focus and primary buttons stay visible in the Add folder panel, the wizard and the Machines page.
- [ ] AC-26: New screens pass in light and dark at desktop width and 390 px under each `data-platform`: no horizontal scroll, no clipped text, focus visible on every control.
- [ ] AC-27: Evidence exists per system: fixture screenshots made on Windows and Linux runners with their real fonts, and installed-app screenshots on macOS, Linux and Windows. A system with no installed-app capture is recorded as a proof limit, not claimed.

Phone:

- [ ] AC-28: Settings > Machines > Your phone is one card with three steps and live state: this machine is on SpecWithCode Connect as <email>; get the app (a store code plus the names App Store and Google Play); sign in on the phone as <email>. It has at most one primary button, the one the state needs: Sign in, Turn on or Try again. While waiting it shows "Waiting for your phone…", and the phone's row appears within 10 seconds of the phone signing in, with no refresh.
- [ ] AC-29: The card says "phone", covers iPhone and Android, and names this machine by its kind and nickname.
- [ ] AC-30: Private QR pairing is one quiet row in the card, "Cannot use Connect? Pair over your own network", opening the existing dialog directly at the QR steps. Its preconditions name what to turn on and offer the button that does it. In no state is it the only button or the most prominent one in the phone area.
- [ ] AC-31: In a browser the card is shown, with its state read from the machine. When that window cannot change the state it says where to do it ("Open SpecWithCode on <machine>"). The QR flow is never the page's primary action.
- [ ] AC-32: A phone browser at a machine's address leads with "Sign in to SpecWithCode Connect" and "Get the phone app"; the code field sits under "I have a pairing code". The page does not say environment, backend, host or secret.
- [ ] AC-33: Once the first-run Connect step is linked, it shows the same three-step phone copy in one line with the account named.
- [ ] AC-34: iPhone app, signed in with no computers: the steps match the desktop card's wording, name the account and say Mac, Windows or Linux. The app looks again by itself every 3 seconds for 2 minutes, then every 15 seconds while the screen is visible, and on return to the foreground. A found computer appears without a tap; "Check again" stays.
- [ ] AC-35: iPhone app: the machines list and its empty state offer "Add a computer", a sheet that leads with Connect and keeps looking, with "Pair with a link or QR code instead" last. Signed out, its first action is "Sign in to SpecWithCode Connect".
- [ ] AC-36: iPhone app errors use plain words ("your private network", not "tailnet") and each names the next step.

Machines page:

- [ ] AC-37: The page opens with this machine: name, kind, role (main machine, helper for <machine>, or not set up), version state, and three facts: Connect, Phone, Other machines.
- [ ] AC-38: Exactly one Next step is highlighted, chosen in this order: sign in to SpecWithCode Connect; turn Connect on for this machine; add your phone; none ("You are set"). It holds the page's only primary button. "Not now" on the phone step hides it for this machine and is remembered.
- [ ] AC-39: Order: this machine, Your phone, Other machines (the cards, then "Add a machine" and "Join a main machine" as two entries with one sentence each), Who can run work here, then a folded Advanced with: run agents on this machine, network access, Tailscale, signed-in browsers and apps, saved connections, activity for phone notifications. Nothing that exists today is removed.
- [ ] AC-40: The page's visible text never says "environment" or "relay". Each switch row says what turning it off does. The activity row no longer contradicts its disabled state. One command name, `specwithcode`, appears on this page and in first run.
- [ ] AC-41: Every new string exists in all nine language files, and the page passes AC-26.

Help and docs:

- [ ] AC-42: `docs/user/install.md` and `docs/user/add-a-machine.md` describe the phone flow as the app now shows it, and no longer say that no phone app is published.
- [ ] AC-43: `HelpLink` (1298) is placed with these questions: Your phone card, "How do I connect my phone?"; Other machines, "How do I add another machine?"; first-run first step, "Main machine or helper: which one do I pick?"; Connect step, "What is SpecWithCode Connect?"; Join step, "How does joining work?"; Projects step and the Add folder panel, "What becomes a project?"; the phone-browser page, "How do I open my machine from a phone?". One per screen. Until 1298's component exists the slot renders nothing.

## Approach

Mockups (static HTML, not app code) and headless captures are in `reports/mockups/`. Names, folders, codes and emails in them are invented. `reports/mockups/index.html` is a before and after gallery with a system and theme switch.

- Each desktop view exists as `reports/mockups/{mac,win,linux}/<view>-{light,dark}.png`: 96 files. Phone views are in `reports/mockups/phone/`: 14 files.
- Folder choice: `folder-before`, `folder-after` (the photo's state), `folder-typing-after`, `folder-drop-after`, `newproject-after`.
- First run: `role-before` and `role-after`, `connect-before` and `connect-after`, `join-before` and `join-after`, `projects-before` and `projects-after`.
- Machines: `machines-before`, `machines-after` (linked, waiting for a phone), `machines-signedout-after`.
- Phone: `ios-before` and `ios-after`, `ios-add-before` and `ios-add-after`, `webphone-before` and `webphone-after`, `webphone-machines-after`.
- Source: `reports/mockups/mockup.html` (`?view=<name>&os=mac|win|linux&theme=light|dark`), `mockup.css`, `mockup.js`; captured by `reports/mockups/shoot.mjs`, which fails on clipped content, then shrunk by `reports/mockups/compress.py`.
- Proof limit: the Windows and Linux captures were rendered on a Mac with stand-in fonts (Selawik for Segoe UI, Ubuntu Sans). They show the conventions, not real font rendering; AC-27 covers that.

Design rules:

1. **Enter confirms what the address bar shows.** One rule replaces "Enter adds, unless a row is highlighted, then Cmd+Enter adds". Arrow keys change the bar, so the bar is always the truth, and the button repeats it in words.
2. **One picker.** Address bar on top, 1272's Places and list below, an outcome line, a footer with the primary. Add project, New project, clone and first run differ only in the button's label.
3. **One design, platform conventions.** The app keeps its own look. What follows the system is what a person notices when it is wrong: window controls, fonts, key names, button order, the file manager's name, path form, scrollbars and corner radius.
4. **One next step.** A screen about setup states the current state first, then one action with the only primary button.
5. **Connect first, QR last.** Every phone surface names the same three steps and the account; the private QR is a quiet fallback.

Changes, in order. Each numbered group can ship as its own pull request.

1. **Platform conventions.** New `apps/web/src/lib/platformConventions.ts` (pure, tested) and `data-platform` set in `apps/web/src/main.tsx`. `ui/kbd.tsx`, `ui/dialog.tsx` and `ui/wizard.tsx` read it for key labels and button order. `styles/base.css` gets the font stacks, radius tokens and Windows and Linux scrollbar rules behind `[data-platform]`. Existing screens change only through these shared components.
2. **Address bar.** New `apps/web/src/components/studio/pathField.logic.ts` (parse, complete, paste clean-up, recents merge; pure) and `PathField.tsx`. `FolderBrowser.tsx` gains a controlled selection so arrows can drive the bar, and its "Type a path" mode becomes the bar. Recents extend the per-machine store in `hooks/useProjectFolderChoice.tsx`.
3. **Add folder panel.** New `apps/web/src/components/studio/AddFolderPanel.tsx`, rendered by the palette where the browse rows were. The browse list code leaves `CommandPalette.tsx` (4,412 lines, over the 1,500 limit, so this must shrink it) and `CommandPalette.logic.ts`.
4. **System dialog and drop.** `PickFolderOptions` in `packages/contracts/src/ipc.ts` gains optional `title` and `buttonLabel`; `ElectronDialog.ts` passes them. Drop reuses `getPathForFile` through a helper moved out of `chat/folderDrop.ts`.
5. **First run, after 1294 merges.** Step files `RoleStep.tsx`, `ConnectStep.tsx`, `ProjectsStep.tsx` next to 1294's `AccessStep.tsx`; `WelcomeWizard.tsx` keeps the state machine. The role choice is held in state until Continue. Sign-in reuses the pending-link path the phone section already has (`PhoneConnect.logic.ts:37-41`). `routes/welcome.tsx` gets the drag strip.
6. **Machines and phone, after 1296's T-05 and T-07.** New `MachineSummary.tsx` and `machineNextStep.logic.ts` (pure). `PhoneConnectSettings.tsx` becomes the three-step card and stops hiding in a browser; `PairPhoneSettings.tsx` shrinks to the quiet row. The this-machine rows move out of `ConnectionsSettings.tsx` (4,444 lines) into `ThisMachineAdvanced.tsx`, and `MachinesSettings.tsx` sets the order. The store code points at a new `apps/marketing/src/pages/get.astro` that sends an iPhone to the App Store and Android to Google Play.
7. **Phone browser.** `PairingRouteSurface.tsx` leads with Connect sign-in.
8. **iOS.** `ConnectViews.swift`, `PairWelcomeView.swift`, `MachineViews.swift`, `GlobalSettingsSheet.swift`, `TransportError.swift`. The wording comes from the table in `reports/phone-copy.md`, written with task T-15, so desktop and phone cannot drift.
9. **HelpLink, docs, cross-system evidence.**

Rejected:

- **Three native skins** (Fluent, Adwaita, Aqua). Three designs to keep in step for a small gain; conventions fix what reads as foreign.
- **Dropping the folder list for a bare text field.** A remote machine has no system dialog, and the list is how people find a folder whose path they do not remember.
- **Making the system dialog the only way.** It cannot see another machine's disks, and Anton asked for Enter.
- **Auto-highlighting the first row**, as the rest of the palette does. It is what makes Enter ambiguous in a picker.
- **A QR code that signs the phone in.** It makes a Connect login transferable by camera; 1296 keeps keys, not sign-ins, as the credential.
- **A new closing "You are set" wizard step.** The Machines page's next step does that job without lengthening setup.
- **Editing `CommandPalette.tsx` in place.** The file is nearly three times the limit.

Risks:

- Auth: the Connect step signs in and links in one click. It reuses an existing path and adds no new credential, but Anton's manual acceptance is needed before release (project gate for auth and new UI).
- Three increments edit the wizard and the Machines files. Order is 1294, then this increment's first-run group; 1296's T-05 and T-07, then this increment's Machines group.
- Button order on Windows flips for every dialog that uses the shared footer. That is intended, and the fixture must cover a destructive dialog so the safe button keeps focus.
- Completion on a slow remote machine: listings are already cached per directory; the bar must never block typing on a request.
- Real Windows and Linux rendering can only be judged on those systems (AC-27).

## Decisions

### Asked
- none

### Defaulted (change any before sw-do)
- D-01 One design with platform conventions, not three native skins → yes (reversible).
- D-02 Enter always confirms the folder shown in the address bar; arrow keys fill the bar; Tab opens a folder → yes (reversible).
- D-03 Dialog buttons: default action last on macOS and Linux, first on Windows → yes (reversible).
- D-04 Corner radius per system, 8, 4 and 6 px → yes (reversible; one token).
- D-05 New project keeps 1272's breadcrumb and turns into the text field on focus → yes.
- D-06 The system dialog's confirm adds the folder at once in Add project and only fills the bar in New project and first run → yes (reversible).
- D-07 "My main machine" is preselected at first run, and the choice is saved on Continue → yes.
- D-08 Words: the page stays "Machines"; sentences use the device's kind (Mac, PC, computer) and its nickname; a joined machine is described as "a helper for a main machine", while the action keeps the name "Join a main machine" → yes (reversible).
- D-09 Phone copy says "phone" for iPhone and Android now; the Android app's own screens are a follow-up → yes.
- D-10 The store code points at one `/get` page that redirects by phone type → yes (reversible).
- D-11 "Not now" on the phone step is remembered per machine in client settings → yes (reversible).

### Open
- none

## Tasks

### T-01 Reproduce the photo: typed folder with no subfolders, then Enter
- AC: AC-11 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/tests/add-folder/index.html, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/add-folder/main.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/add-folder/mocks.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/add-folder/vite.config.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/add-folder/verify.mjs, .specweave/increments/1297-easy-folder-choice-and-first-run-setup-type-a-path-and-press-enter-reviewed-steps-native-feel-on-macos-windows-and-linux/reports/repro.md | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp build --config apps/web/tests/add-folder/vite.config.ts && node apps/web/tests/add-folder/verify.mjs "$PWD/.artifacts/add-folder" --baseline

### T-02 Platform conventions: one module, data-platform, key labels and button order
- AC: AC-21, AC-22 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/lib/platformConventions.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/lib/platformConventions.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/main.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/ui/kbd.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/ui/dialog.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/ui/wizard.tsx | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp test run apps/web/src/lib/platformConventions.test.ts

### T-03 Fonts, radius, scrollbars and contrast themes per system
- AC: AC-23, AC-24, AC-25 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/styles/base.css, repositories/anton-abyzov/specwithcode-dev/apps/web/src/index.css, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/dialog-chrome/verify.mjs | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp build --config apps/web/tests/dialog-chrome/vite.config.ts && node apps/web/tests/dialog-chrome/verify.mjs "$PWD/.artifacts/dialog-chrome"

### T-04 Address bar logic: parse, complete, paste clean-up, recents
- AC: AC-02, AC-03, AC-04, AC-06 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/pathField.logic.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/pathField.logic.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/hooks/useProjectFolderChoice.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/hooks/useProjectFolderChoice.test.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp test run apps/web/src/components/studio/pathField.logic.test.ts apps/web/src/hooks/useProjectFolderChoice.test.ts

### T-05 Address bar component and the folder list driven by it
- AC: AC-02, AC-03, AC-05, AC-09 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/PathField.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/PathField.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/FolderBrowser.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/folderBrowser.logic.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/NewProjectFolderPicker.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/NewProjectFolderPicker.test.tsx | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp test run apps/web/src/components/studio/PathField.test.tsx apps/web/src/components/studio/NewProjectFolderPicker.test.tsx

### T-06 Add folder panel replaces the palette's browse list
- AC: AC-01, AC-02, AC-05, AC-10 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/AddFolderPanel.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/AddFolderPanel.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/CommandPalette.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/CommandPalette.logic.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/CommandPalette.logic.test.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp test run apps/web/src/components/studio/AddFolderPanel.test.tsx apps/web/src/components/CommandPalette.logic.test.ts

### T-07 System folder dialog on all three systems, and drag and drop
- AC: AC-07, AC-08 | Files: repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/ipc.ts, repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/electron/ElectronDialog.ts, repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/electron/ElectronDialog.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/ipc/methods/window.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/localApi.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/lib/folderDrop.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/lib/folderDrop.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/folderDrop.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp test run apps/desktop/src/electron/ElectronDialog.test.ts apps/web/src/lib/folderDrop.test.ts apps/web/src/localApi.test.ts

### T-08 Add folder fixture: every state, three systems, light and dark, keyboard only
- AC: AC-01, AC-02, AC-07, AC-10, AC-11, AC-26 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/tests/add-folder/main.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/add-folder/mocks.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/add-folder/verify.mjs, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/project-folder-choice/verify.mjs, repositories/anton-abyzov/specwithcode-dev/AGENTS.md | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp build --config apps/web/tests/add-folder/vite.config.ts && node apps/web/tests/add-folder/verify.mjs "$PWD/.artifacts/add-folder" && node apps/web/tests/project-folder-choice/verify.mjs

### T-09 First-run frame: stage bar, one footer, Escape, focus, drag strip, steps in their own files
- AC: AC-12, AC-13, AC-14, AC-19, AC-20 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/onboarding/WelcomeWizard.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/onboarding/WizardFrame.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/onboarding/WizardFrame.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/onboarding/AgentsStep.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/onboarding/wizardFocus.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/routes/welcome.tsx | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp test run apps/web/src/components/onboarding/WizardFrame.test.tsx apps/web/src/components/onboarding/WelcomeWizard.test.tsx apps/web/src/components/onboarding/WelcomeWizard.terminal.test.tsx

### T-10 First step: two cards, a default, saved on Continue
- AC: AC-15 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/onboarding/RoleStep.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/onboarding/JoinMachineSteps.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/onboarding/WelcomeWizard.machineRole.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/onboarding/firstRun.logic.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp test run apps/web/src/components/onboarding/WelcomeWizard.machineRole.test.tsx

### T-11 Connect step and join path: sign in and link in one place, Done at the end
- AC: AC-16, AC-17, AC-33 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/onboarding/ConnectStep.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/onboarding/ConnectStep.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/onboarding/JoinMachineSteps.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/onboarding/connectSignIn.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/onboarding/firstRun.logic.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/onboarding/firstRun.logic.test.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp test run apps/web/src/components/onboarding/ConnectStep.test.tsx apps/web/src/onboarding/firstRun.logic.test.ts apps/web/src/components/settings/PhoneConnect.logic.test.ts

### T-12 Projects step takes a folder
- AC: AC-18 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/onboarding/ProjectsStep.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/onboarding/WelcomeWizard.import.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/NoProjectsHero.tsx | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp test run apps/web/src/components/onboarding/WelcomeWizard.import.test.tsx

### T-13 First-run fixture and nine languages
- AC: AC-12, AC-13, AC-19, AC-26, AC-41 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/tests/first-run-choice/main.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/first-run-choice/verify.mjs, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/messages/en.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/messages/de.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/messages/es.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/messages/fr.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/messages/ja.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/messages/ko.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/messages/pt.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/messages/ru.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/messages/zh.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp build --config apps/web/tests/first-run-choice/vite.config.ts && node apps/web/tests/first-run-choice/verify.mjs "$PWD/.artifacts/first-run" && node node_modules/vite-plus/bin/vp test run apps/web/src/i18n/i18n.test.ts

### T-14 Machines page: this machine first, one next step
- AC: AC-37, AC-38 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/machineNextStep.logic.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/machineNextStep.logic.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/MachineSummary.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/MachineSummary.test.tsx, repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/settings.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp test run apps/web/src/components/settings/machineNextStep.logic.test.ts apps/web/src/components/settings/MachineSummary.test.tsx

### T-15 Your phone card: three steps, live state, QR as a quiet row, shown in a browser
- AC: AC-28, AC-29, AC-30, AC-31 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/PhoneConnectSettings.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/PhoneConnect.logic.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/PhoneConnect.logic.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/PairPhoneSettings.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/PhoneSetupDialog.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/PhoneSetupDialog.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/PhoneDevicesSettings.tsx, repositories/anton-abyzov/specwithcode-dev/apps/marketing/src/pages/get.astro, .specweave/increments/1297-easy-folder-choice-and-first-run-setup-type-a-path-and-press-enter-reviewed-steps-native-feel-on-macos-windows-and-linux/reports/phone-copy.md | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp test run apps/web/src/components/settings/PhoneConnect.logic.test.ts apps/web/src/components/settings/PhoneSetupDialog.test.tsx apps/web/src/components/settings/PhoneDevices.logic.test.ts

### T-16 Machines page order, Advanced fold and plain words
- AC: AC-39, AC-40, AC-41 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/MachinesSettings.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/MachinesSettings.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/ConnectionsSettings.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/ThisMachineAdvanced.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/StudioFleetConnections.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n/phrases.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp test run apps/web/src/components/settings/MachinesSettings.test.tsx apps/web/src/components/settings/StudioFleetConnections.test.tsx apps/web/src/i18n/i18n.test.ts

### T-17 Phone browser at a machine's address leads with Connect
- AC: AC-32 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/auth/PairingRouteSurface.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/auth/PairingRouteSurface.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/routes/pair.tsx | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp test run apps/web/src/components/auth/PairingRouteSurface.test.tsx

### T-18 Machines and phone fixture: every state, three systems, light and dark, 390 px
- AC: AC-26, AC-28, AC-30, AC-31, AC-38, AC-39 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/tests/machines-page/main.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/machines-page/mocks.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/machines-page/verify.mjs, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/phone-setup/verify.py | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp build --config apps/web/tests/machines-page/vite.config.ts && node apps/web/tests/machines-page/verify.mjs "$PWD/.artifacts/machines-page"

### T-19 iPhone app: matching steps, looks by itself, Add a computer, plain errors
- AC: AC-34, AC-35, AC-36 | Files: repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Connect/ConnectViews.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Pairing/PairWelcomeView.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Pairing/PairMachineView.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Machines/MachineViews.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Settings/GlobalSettingsSheet.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCSync/Connect.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCTransport/TransportError.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Tests/SWCFeaturesTests/ConnectPhonesTests.swift | Test: cd repositories/anton-abyzov/specwithcode-dev/apps/ios && make test-core

### T-20 HelpLink placements
- AC: AC-43 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/AddFolderPanel.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/onboarding/RoleStep.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/onboarding/ConnectStep.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/onboarding/JoinMachineSteps.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/onboarding/ProjectsStep.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/PhoneConnectSettings.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/MachinesSettings.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/auth/PairingRouteSurface.tsx | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp test run apps/web/src/components/settings/MachinesSettings.test.tsx apps/web/src/components/onboarding/WizardFrame.test.tsx

### T-21 Docs: install, add a machine, your phone
- AC: AC-42 | Files: repositories/anton-abyzov/specwithcode-dev/docs/user/install.md, repositories/anton-abyzov/specwithcode-dev/docs/user/add-a-machine.md, repositories/anton-abyzov/specwithcode-dev/docs/user/devices.md | Test: cd repositories/anton-abyzov/specwithcode-dev && node scripts/studio-brand-audit.mjs

### T-22 Evidence on Windows, Linux and macOS
- AC: AC-27 | Files: repositories/anton-abyzov/specwithcode-dev/.github/workflows/ci.yml, .specweave/increments/1297-easy-folder-choice-and-first-run-setup-type-a-path-and-press-enter-reviewed-steps-native-feel-on-macos-windows-and-linux/reports/platform-evidence.md | Test: test -s .specweave/increments/1297-easy-folder-choice-and-first-run-setup-type-a-path-and-press-enter-reviewed-steps-native-feel-on-macos-windows-and-linux/reports/platform-evidence.md && grep -q "Windows" .specweave/increments/1297-easy-folder-choice-and-first-run-setup-type-a-path-and-press-enter-reviewed-steps-native-feel-on-macos-windows-and-linux/reports/platform-evidence.md

### T-23 Verify and close 1297
- AC: AC-01, AC-12, AC-21, AC-28, AC-37 | Files: .specweave/increments/1297-easy-folder-choice-and-first-run-setup-type-a-path-and-press-enter-reviewed-steps-native-feel-on-macos-windows-and-linux/spec.md | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/typescript/bin/tsc --noEmit --project apps/web/tsconfig.json && cd apps/web && node ../../node_modules/vite-plus/bin/vp build

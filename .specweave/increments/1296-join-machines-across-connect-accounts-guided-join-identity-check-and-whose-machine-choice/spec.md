# Join machines across Connect accounts: guided join, identity check and whose-machine choice

## Problem

On November 11, 2026 Anton tried to let Elena's Mac (her own SpecWithCode Connect account) start work on his Linux machine, the Minisforum (his account). It is supported, but the path failed and several things about it are unclear or too broad.

What happened:

1. On the Minisforum he ran `specwithcode fleet invite --coordinator <Elena's Mac environment ID>`. It printed a 400-character `swc-machine-…` line and "On your primary machine, run: `specwithcode fleet add …`". He photographed the terminal to carry the line across.
2. Elena's Mac has the desktop app but no `specwithcode` command: `zsh: command not found: specwithcode`.
3. She installed it with `npm i -g specwithcode`, as `docs/user/add-a-machine.md:206` says. npm serves 1.0.47, published October 18, 2026. Her app is 1.0.23x.
4. `fleet add` failed with "This is not a machine invitation. Make a new line on that machine (Invite this machine in its Settings > Connections, or `fleet invite`)…" and a stack trace.

Causes, read from the code:

- **Stale npm command.** Lines that carry a Connect address and a one-time credential (v2) arrived in 1.0.98 (`f890f37b00`). The 1.0.47 decoder accepts only the five v1 keys, so it rejects every current line as `invalid-code`. Publishing to npm is a manual step in `docs/studio/releasing.md:377-386` and is not part of `scripts/release/release.sh`. Nothing compares the command's version with the running app.
- **The desktop app installs no command.** The CLI is inside the app bundle (`docs/user/add-a-machine.md:182`) but nothing puts it on `PATH`, and the invite output leads with a terminal command instead of Settings > Machines > Add a machine.
- **The app tells people to run a command they do not have, and never says what it is.** The first-run setup shows `specweave-studio connect` and `specweave-studio pair` (`apps/web/src/components/onboarding/WelcomeWizard.tsx:671`, `:800`), under the product's old command name, and Add a machine shows `specwithcode connect link` (`StudioFleetConnections.tsx:1159`). None of these says whether the command is installed, offers to install it, or explains what it is for. `docs/user/` has no page about the command. The Linux installer and the fleet installer already write a `~/.local/bin` launcher that updates keep current (`apps/server/src/cli/shellLauncher.ts`, `shellLauncherRepoint.ts`); the desktop app's own install writes none.
- **Tailscale is named first.** With `--via auto`, the default in the CLI (`apps/server/src/cli/fleet.ts:192-196`) and the app (`apps/web/src/components/settings/FleetInvite.tsx:155`), `issueFleetInvitation` publishes on Tailscale first, then puts the tailnet address in the line's `url` and Connect in `connectUrl` (`apps/server/src/studioFleetInvite.ts:145-221`). The Minisforum's Connect address was healthy the whole time: it answered as the Minisforum on 1.0.233 when probed. Dialling is already Connect first (`fleetAddresses`, `apps/server/src/fleet/fleetTransport.ts:158-171`), so only the line, the printed text and the side effect of running `tailscale serve` are Tailscale first. Anton keeps Tailscale as a backup only.
- **No identity for the person.** The line names a UUID. Redeeming it checks a key proof and the one-time credential, never an account (`apps/server/src/studioFleetHttp.ts:573-652`). After a paste the main machine shows one status line, and the machine being added shows nothing: no name, no account, no approval (`StudioFleetConnections.tsx:400`). No machine card shows a Connect account, and Settings never shows the signed-in email.
- **Another person's machine is treated as the owner's own.** A redeemed line gives a one-year management session with every standard client scope plus `access:write`, `fleet:update` and `fleet:skills` (`apps/server/src/fleet/fleetRedemption.ts:24-29`). The adding machine's app then connects on its own and can open every project and chat on the machine. Its first work grant defaults to "My machine" (`WorkGrants.ts:351-353`): all provider sign-ins, linked projects, and routines once (`workGrantPolicy.ts:92-104`). So Elena's Mac can read Anton's projects on the Minisforum and spend his subscriptions unless he later finds Whose machine under Who can run work here.
- **A shared machine does not say whose work is whose.** The server records which main machine started each piece of work (`WorkOriginRecord`, `WorkGrants.ts:81-94`), but `apps/web` shows no "started from" label, filter or per-machine running count.
- **Smaller traps.** The line is spent before the main machine is checked, so a wrong ID costs a new line (`studioFleetHttp.ts:620-625`). The join dialog still says "Settings > Connections > Add a machine" (`FleetInvite.tsx:242`). CLI times are UTC ISO strings. Nothing warns that linking a machine to another Connect account changes its address, because the hostname is a hash of stage, Clerk user and environment (`infra/relay/src/deploymentConfig.ts:119-125`).

- **A fresh install warns about a service the user does not have.** Photo from Elena's Mac, November 11, 2026 at 9:05 AM: the Overview's Hosts & capacity card shows an amber "The local Switch service is unavailable." under "Independent capacity unknown · 0 eligible · 0 unverified". Switch is a separate local account-switching service the app reads at `http://127.0.0.1:8318` (`apps/server/src/studio/SwitchClient.ts:9`). When nothing answers there, `Capacity.ts:409-420` reports `switch-unavailable` and `CapacityFleet.tsx:239-240` shows it as a problem. A new user never installed Switch, so the first screen after setup looks broken and names a tool they have never heard of. Anton: "Why do I also see this on that message after my setup?"

- **A machine signed in at setup later says "Not signed in".** Photo from Elena's Mac, November 11, 2026 at 9:04 AM: the sidebar account button reads "Not signed in" although she signed in to Connect in the first-run setup. Anton: "it still showed that I need to sign in, which is kind of a nasty bug. Make sure… it's always updated, and we don't have to log in again or click this button again." Three things in the code produce this, and without her Mac's logs it is not known which one fired:
  - The button shows only this window's Clerk session, never the machine's link. A linked machine with no window session is labelled "Not signed in" (`apps/web/src/components/account/accountMenuModel.ts:53-62`), and the link state carries a user id but no name or email to show instead (`packages/contracts/src/environmentHttp.ts:651-665`).
  - The app signs the window out by itself. `ConnectSessionGuard` runs whenever the window is signed in and calls `signOut()` when listing machines is refused twice for "authentication" (`apps/web/src/cloud/ConnectSessionGuard.tsx:28-69`). That reason covers every token the relay rejects, including one that only looks expired because the computer's clock is off, and three failures that never reach the relay: a local key that will not load and two proof-creation errors (`packages/client-runtime/src/connection/errors.ts:38-47`, `:110-117`). The only trace is a `console.warn` in the window, which is gone after a restart.
  - The saved sign-in is one encrypted file, `clerk-tokens.json`, and the store deletes a value it cannot open (`apps/desktop/src/app/DesktopClerkTokenStorage.ts:25-35`). A refused or failed Keychain read after a restart or update signs the window out with no message.

Anton, November 11, 2026: "Why is it using Tailscale? Tailscale is only the backup. You must rework it… connect through Cloudflare, right? Through Clerk." And: "maybe we need to suggest installing this command line for a new machine, similar to SpecWeave." And: "how it's going to work when one Linux machine is going to be used by two different SWC Connect emails? How can I see on that machine what the projects are and what the execution is?"

## Scope

In: the join and add flows in the desktop and web app, the `fleet` CLI, the server's fleet auth, the Connect relay, the release tooling for the npm command, and the user docs for adding a machine.

- Joins go through SpecWithCode Connect first; Tailscale and the local network are fallbacks only.
- A short join code and an approval on the machine being added, showing the asking machine's name and Connect account.
- A "My machine" or "Someone else's machine" choice at approval, with a limited session for someone else's.
- The Connect account shown on machines, and a "started from" label, filter and running count on a shared machine.
- A one-click install of the `specwithcode` command from the app, version-aware CLI errors, and the npm command kept current.
- No Switch warning on a machine that never had Switch; the Overview's capacity card reads plainly on a fresh install.
- One Connect sign-in per machine that survives restarts and updates, shown from the machine's link, with no automatic sign-out.

Out: Clerk organizations, teams and seats; tunnel limits and billing per account; phone pairing; folder copy and handoff between accounts; the mobile apps; making the Connect sign-in itself the credential that controls a machine.

## Acceptance Criteria

Connect first:

- [ ] AC-01: On a machine linked to Connect whose address answers, `fleet invite` with no `--via` and the app's Join a main machine make a line whose first address is the Connect address, never run `tailscale serve`, and say "Reached through SpecWithCode Connect". A tailnet or local address is added only when this server is already published there, and is listed as a backup.
- [ ] AC-02: When the machine is not linked, both say so and offer to link (`specwithcode connect link`, or Settings > Machines) instead of falling back to Tailscale silently. `--via tailscale` and `--via auto` keep today's behaviour for people who ask for it.
- [ ] AC-03: A main machine on 1.0.98 or newer still accepts every line this increment makes, and adding a machine works with Tailscale stopped on both sides.

Join code and approval:

- [ ] AC-04: Join a main machine shows an 8-character code, valid 10 minutes and usable once, with no main machine ID to type. Add a machine on the main machine takes the code, shows the found machine's name, system, version and Connect account, and waits for approval there. The pasted join line stays available as "Paste a join line instead" for machines without internet.
- [ ] AC-05: The machine being added shows an approval with the asking machine's name, its Connect account as attested by the relay, a "Different Connect account" or "Same Connect account" mark, and three words that also appear on the asking machine. Nothing is granted until someone with Manage access on that machine approves. Decline, Escape and expiry grant nothing and say so on the asking machine.
- [ ] AC-06: Two machines on different Connect accounts complete a join with neither signing out or relinking. A main machine that is not linked to Connect can still join; the approval then reads "Not linked to Connect: identity not checked" and "My machine" is not preselected.
- [ ] AC-07: Add a machine lists machines on the same Connect account that are not added yet, each with Add. Add sends the same request and still needs approval on that machine.
- [ ] AC-08: The relay can attest identity only. No relay response contains a credential that a machine accepts, a join code guess is rate limited and locked after 5 misses, and a request whose words would differ (a different key than the one the relay named) is refused before the approval is shown.
- [ ] AC-09: On a machine with no screen, `specwithcode fleet join` prints the code, waits, then shows the same identity, words and choice in the terminal and takes the answer there.

Whose machine:

- [ ] AC-10: The approval asks "Whose machine is it" with "My machine" and "Someone else's machine". A different Connect account preselects "Someone else's machine". The primary button names the choice.
- [ ] AC-11: "Someone else's machine" grants only the projects and provider sign-ins picked in the approval (default: none of each until picked), no routines, a 30-day default lifetime, and one hop. Its session cannot pair browsers or phones, mint access for other machines, update the app or install skills there.
- [ ] AC-12: The app and agents of a "Someone else's" main machine can list and open only the projects in its grant and the threads it started. Any other project, thread, file or search result on that machine answers not found.
- [ ] AC-13: Changing Whose machine later under Who can run work here applies the same limits immediately, in both directions, without a new join.

Seeing a shared machine:

- [ ] AC-14: On a machine that others start work on, every thread and project started by another machine carries "from <machine>", the sidebar can filter by "Started here" and by each main machine, and the thread header says who started it, their Connect account, and which sign-in it runs on.
- [ ] AC-15: Who can run work here shows, per main machine, its Connect account, "Your machine" or "Someone else's", what it may use, and how many threads it is running now. A Stop there stops only that machine's threads.
- [ ] AC-16: Machine cards and the Connect row show the Connect account a machine is linked as. The email is sent only to machines that already hold access to it and in relay attestations, never in the public identity answer.
- [ ] AC-17: Linking a machine to a different Connect account first warns that its address changes and names the machines that use it.

Command line:

- [ ] AC-18: First-run setup installs the `specwithcode` command by default on every desktop install, main machine or joined, through a checked "Install the specwithcode command" option that can be unticked. Installing puts a launcher for the CLI inside the installed app at `~/.local/bin/specwithcode` (a `.cmd` in the user's app-data `bin` on Windows) and makes that folder part of the terminal's `PATH`, with no administrator password. A new terminal window then runs `specwithcode --version` and prints the app's version.
- [ ] AC-31: The option, the Settings card and every offer say in one or two sentences what the command is (this app driven from a terminal, talking to the app already running, no second copy and no separate sign-in), what it is needed for (adding or joining a machine over SSH or on a server with no screen, linking Connect from a terminal, pairing a phone, checking the background service, scripts and agents), what it is not needed for, and exactly what installing changes on disk. Each has a "What is this?" link to a new Command line page in the user docs, which lists the commands with one example each.
- [ ] AC-32: Settings > Machines has a Command line card showing "Installed, matches this app" or "Not installed" with Install command, plus Remove. It shows "Replace it" when another `specwithcode` is ahead of it on `PATH` or is older than the app.
- [ ] AC-33: Everywhere the app shows a `specwithcode` command to run on this machine, and the command is not installed here, the block carries "Install command" and "What is this?" beside Copy. No screen shows the old `specweave-studio` name.
- [ ] AC-34: An install made before this change is offered the command once, by a notice with Install command and Not now. Not now is remembered, and the Settings card stays available. Updates keep an installed launcher pointing at the current app, and uninstalling the app removes it and the `PATH` line it added.
- [ ] AC-19: A `specwithcode` command whose version differs from the running app's says both versions before doing anything that changes state, and for `fleet add` says nothing was sent and gives the two ways forward (the app's Add a machine, or Install command). No stack trace is printed for a refused line.
- [ ] AC-20: A line from a newer version is reported as "made by a newer SpecWithCode", not as "not a machine invitation". A line for a different main machine is refused before it is spent. Times are local, with the zone.
- [ ] AC-21: The invite output and the join dialog lead with "On the main machine, open Settings > Machines > Add a machine", with the terminal command second. The stale "Settings > Connections > Add a machine" text is gone.
- [ ] AC-22: `scripts/release/release.sh` publishes the npm `specwithcode` package for every stable release, `status` fails when npm's latest is behind the released version, and 1.0.47 and older carry an npm deprecation notice that names the fix.

Fresh install (from the test on Elena's Mac):

- [ ] AC-24: On a machine where the Switch service has never answered, the Overview shows no Switch warning and no amber notice. The host card lists each signed-in provider with the usage the model picker already shows, or "No providers signed in yet" with a Set up providers link when there are none.
- [ ] AC-25: "The local Switch service is unavailable", "timed out" and "could not be verified" appear only on a machine where Switch answered before, and then say what to do. On a machine without it the summary line does not read "Independent capacity unknown · 0 eligible · 0 unverified".

Stay signed in (from the test on Elena's Mac):

- [ ] AC-26: After one Connect sign-in on a machine, in first-run setup or in Settings, the sidebar account button shows that account after every restart, update, sleep and wake, in the main window and in project windows, with no click. Checked by relaunching the packaged app three times and by an update install.
- [ ] AC-27: A machine linked to Connect never shows "Not signed in". The button shows the linked account's name or email, stored with the link when it is made and filled in for existing links the next time the window is signed in. When only the window's own session is missing, the menu says "Sign in again to manage your account" and nothing else changes.
- [ ] AC-28: The app never signs a window out by itself. A relay refusal, a local key or proof error, a clock that is off, or a saved sign-in that cannot be read shows "Connect needs attention" with Retry, keeps the saved sign-in on disk, and retries on its own. Only the person's Sign out, or Clerk reporting the session ended, signs out.
- [ ] AC-29: Listing the machines on the account, join codes and the Connect rows in Settings read the machine's link, so they work when the window's session is missing.
- [ ] AC-30: Every time a window's Connect session ends or cannot be restored, the desktop log records when and why (the person signed out, Clerk ended it, the relay refused with its code, the saved sign-in was unreadable), with no token in the line.

Quality:

- [ ] AC-23: The new screens pass in light and dark at desktop width and 390 px with no horizontal scroll, work by keyboard with focus on the safe action, and every new string exists in all nine language files.

## Approach

Mockups (static HTML, not app code) and headless captures are in `reports/mockups/`. Names, codes and emails in them are invented.

- `reports/mockups/add-a-machine-light.png`, `reports/mockups/add-a-machine-dark.png`: main machine, same-account list and code entry.
- `reports/mockups/join-a-main-machine-light.png`, `reports/mockups/join-a-main-machine-dark.png`: machine being added, the code and its routes.
- `reports/mockups/approve-request-light.png`, `reports/mockups/approve-request-dark.png`, `reports/mockups/approve-request-phone-light.png`, `reports/mockups/approve-request-phone-dark.png`: the approval and the whose-machine choice.
- `reports/mockups/machines-after-light.png`, `reports/mockups/machines-after-dark.png`: Who can run work here with accounts, and the Connect row.
- `reports/mockups/shared-machine-threads-light.png`, `reports/mockups/shared-machine-threads-dark.png`: whose work is whose on a shared machine.
- `reports/mockups/command-line-light.png`, `reports/mockups/command-line-dark.png`: the Command line card with what it is and why, the error today and proposed, and the terminal join.
- `reports/mockups/command-setup-light.png`, `reports/mockups/command-setup-dark.png`: the first-run option, and the offer beside a command the app shows.
- Source: `reports/mockups/mockup.html` (`?view=add|join|approve|machines|threads|cli|setup&theme=light|dark`), captured with `reports/mockups/shoot.mjs`.

How it works today:

- The machine to add makes a line naming the main machine's environment ID. The main machine redeems it at `/api/studio/fleet/invitation/redeem` with a proof of its fleet key and gets a management token bound to that key. From then on every call is a key proof checked by the machine itself. Connect only supplies the address; the Clerk account is never checked.
- That is why two accounts already work, and why neither machine signs in again.

What changes, in order:

1. **Routes.** In `issueFleetInvitation`, the default route becomes Connect: the line's `url` is the Connect address. A tailnet address is included only when `tailscale serve` already publishes this server, using the existing `{url: tailnet, connectUrl}` shape so main machines from 1.0.98 keep working; they dial Connect first already. `auto` and `tailscale` stay as explicit choices. CLI and app text name Connect first.
2. **Relay attestation and join codes** (`infra/relay`, `packages/contracts/src/relay.ts`). A linked machine registers a join code with the relay, signed with its environment key. The relay stores only a hash of the code with the machine's environment ID, label, address and Clerk account, for 10 minutes. The main machine looks the code up and receives that record plus a short-lived statement, signed by the relay, of its own environment, fleet key thumbprint and Clerk account.
3. **Join request and approval** (`apps/server`). The main machine sends the statement and a proof of its fleet key straight to the other machine's address at a new `/api/studio/fleet/join-request`. That machine verifies the relay signature and the key, derives the three words from the code and both key thumbprints, and raises an approval. On approval it issues the session, bound to the asking key, which the asking machine collects with a key proof. The end state is the one a redeemed line gives today, so `fleet.json`, worker grants and reconnects are unchanged.
4. **Whose machine.** "My machine" issues today's management session. "Someone else's machine" issues a guest session: a new principal kind with no `access:write`, `fleet:update` or `fleet:skills`, and a read filter in the orchestration, project, file and search handlers that admits only granted projects and threads whose recorded origin is that machine. The first work grant is written from the approval's choices instead of `newGrantDefaults("self")`.
5. **Visibility.** The recorded work origin is added to the thread and project shells the server already sends, and the web app renders the chip, filter, header and running counts. The Connect account is read from the machine's link and sent in the authenticated fleet snapshot.
6. **Command line.** The desktop app writes a launcher in the same byte-exact format the Linux and fleet installers already write, so `repointShellLaunchers` keeps it current on every update (`~/.local/bin/specwithcode` on macOS and Linux; a `.cmd` in the user's app-data `bin` on Windows). It adds one marked line to the login shell's profile (`~/.zprofile`, `~/.bash_profile`, or the fish config) when that folder is not already on `PATH`, and removes only that line on Remove. The wizard option, the Settings card, the per-command offer and the one-time notice all call the same install, and share one explanation component. A new `docs/user/command-line.md` explains the command and lists what it can do. The CLI reads the running server's version before changing anything. `decodeFleetJoinCode` reports an unknown `v` separately. The redeem handler checks the main machine before spending the credential.
7. **npm.** A `publish-npm` stage in `scripts/release/release.sh` after the public release, a `status` check, and `npm deprecate` for versions that cannot read current lines.
8. **Fresh install.** The capacity service remembers whether Switch has ever answered on this machine. Until it has, a refused connection is "not installed", not an error: the snapshot carries the providers the registry already knows and no `error`, and `CapacityFleet` renders them without the notice.
9. **Stay signed in.** `CloudLink` stores the account's display name and email with the link and returns them in `EnvironmentCloudLinkStateResult`; the account menu reads them, so the button no longer depends on the window. `ConnectSessionGuard` stops calling `signOut()`: it sets a "needs attention" state and retries with backoff, and it ignores the three local errors. The token store wrapper keeps an unreadable file and reports it. Session-ending events go to the desktop log through the existing preload bridge.
10. **Docs.** `docs/user/add-a-machine.md` leads with the code flow and the app, and installs the npm command at the app's version.

Rejected:

- **Clerk sign-in as the credential.** One stolen Connect login would control every machine on the account, and two accounts could not join at all. Clerk identifies the person on the approval; keys stay the credential.
- **Auto-approve on the same account.** Same reason. One approval on the machine is the cost.
- **A third line version with a route order field.** Not needed: 1.0.98 already accepts a Connect-only line and dials Connect first.
- **Hiding other people's work by separate stores per account.** One machine has one store; filtering by recorded origin and grant is smaller and matches how grants already work.

Risks:

- The guest read filter touches many handlers. A missed one leaks project names. It needs a deny-by-default test over every method in `CLIENT_GUARDED_RPC_SCOPES`.
- This is an auth change. Anton's manual acceptance is required before release (project gate), on two real accounts.
- The relay becomes part of the join for the code flow. The pasted line keeps a path that needs no relay.
- `ws.ts` must not gain imports (TS2589); new handlers go in their own modules.

## Decisions

### Asked
- D-08 Bugs and improvements from the test on Elena's Mac → one so far (Anton, November 11, 2026): the "The local Switch service is unavailable" notice on her Overview after setup. Added as AC-24, AC-25 and T-11. Second item, same day: the sidebar read "Not signed in" after she had signed in during setup. Added as AC-26 to AC-30 and T-12. More may follow.

### Defaulted (change any before sw-do)
- D-01 Keys stay the credential; Clerk is shown as identity and attested by the relay → yes (reversible only before release).
- D-02 Same-account machines still need one approval on the machine → yes.
- D-03 A different Connect account preselects "Someone else's machine" with no sign-ins and no projects until picked → yes.
- D-04 Join code: 8 characters, 10 minutes, one use, 5 misses → yes.
- D-05 Guest access lasts 30 days by default, renewable from Who can run work here → yes.
- D-06 Existing joins are not changed or re-approved; Whose machine can be switched per row → yes.
- D-07 The command is installed by the app as a launcher to its own CLI, not from npm → yes.
- D-10 First-run setup installs the command by default, with the option visible and untickable (Anton, November 11, 2026: "Make sure that we install it when it's needed, maybe on initial setup") → on by default. It writes one file in the home folder and one line in the shell profile, both removable.
- D-11 Installs from before this change get one notice, not a silent install → yes.

### Open
- D-09 Publish the current release to npm now, before this increment ships, so `npm i -g specwithcode` stops serving 1.0.47. It needs the release owner; recommended yes.

## Tasks

### T-01 Connect-first lines and wording
- AC: AC-01, AC-02, AC-03, AC-21 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/studioFleetInvite.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/cli/fleet.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/FleetInvite.tsx, repositories/anton-abyzov/specwithcode-dev/apps/server/src/studioFleetInvite.test.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp test run apps/server/src/studioFleetInvite.test.ts apps/server/src/fleet/fleetTransport.test.ts

### T-02 Relay join codes and identity attestation
- AC: AC-04, AC-08 | Files: repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/relay.ts, repositories/anton-abyzov/specwithcode-dev/infra/relay/src/environments/JoinCodes.ts, repositories/anton-abyzov/specwithcode-dev/infra/relay/src/environments/JoinCodes.test.ts, repositories/anton-abyzov/specwithcode-dev/infra/relay/src/http/Api.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp test run infra/relay/src/environments/JoinCodes.test.ts

### T-03 Join request, matching words and approval on the server
- AC: AC-05, AC-06, AC-08, AC-20 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/fleet/joinRequest.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/fleet/joinRequest.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/studioFleetHttp.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/studioFleetJoin.ts, repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/studioFleet.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/joinRequest.test.ts apps/server/src/studioFleetJoin.test.ts

### T-04 Guest session and read filter for someone else's machine
- AC: AC-10, AC-11, AC-12, AC-13 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/auth/EnvironmentAuth.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/fleet/WorkGrants.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/fleet/workGrantPolicy.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/fleet/guestAccess.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/fleet/guestAccess.test.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/guestAccess.test.ts apps/server/src/fleet/WorkGrants.test.ts

### T-05 Add a machine, Join a main machine and the approval in the app
- AC: AC-04, AC-05, AC-07, AC-10, AC-23 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/StudioFleetConnections.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/FleetInvite.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/JoinApproval.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/join-machines/verify.mjs | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp build --config apps/web/tests/join-machines/vite.config.ts && node apps/web/tests/join-machines/verify.mjs "$PWD/.artifacts/join-machines"

### T-06 Terminal join for machines with no screen
- AC: AC-09 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/cli/fleet.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/cli/fleetJoin.test.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp test run apps/server/src/cli/fleetJoin.test.ts

### T-07 Started-from labels, filter, running counts and Connect account on machines
- AC: AC-14, AC-15, AC-16, AC-17 | Files: repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/orchestration.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/fleet/incomingMachines.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/threadLocation.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/MachineWorkGrants.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/MachinesSettings.tsx | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp test run apps/web/src/studio/threadLocation.test.ts apps/web/src/components/settings/MachineWorkGrants.test.tsx

### T-08 Install the command at setup, in Settings and beside every command, with its explanation
- AC: AC-18, AC-31, AC-32, AC-33, AC-34 | Files: repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/cliLauncher.ts, repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/cliLauncher.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/cli/shellLauncher.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/CommandLineCard.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/CommandLineCard.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/onboarding/WelcomeWizard.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/StudioFleetConnections.tsx, repositories/anton-abyzov/specwithcode-dev/docs/user/command-line.md | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp test run apps/desktop/src/cliLauncher.test.ts apps/server/src/cli/shellLauncher.test.ts apps/web/src/components/settings/CommandLineCard.test.tsx

### T-14 Version-aware CLI errors
- AC: AC-19, AC-20 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/cli/versionCheck.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/cli/versionCheck.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/cli/fleet.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp test run apps/server/src/cli/versionCheck.test.ts

### T-09 npm command published with every release
- AC: AC-22 | Files: repositories/anton-abyzov/specwithcode-dev/scripts/release/release.sh, repositories/anton-abyzov/specwithcode-dev/scripts/release/release-self-test.sh, repositories/anton-abyzov/specwithcode-dev/docs/studio/releasing.md | Test: cd repositories/anton-abyzov/specwithcode-dev && bash scripts/release/release-self-test.sh

### T-10 Docs and nine languages
- AC: AC-21, AC-23 | Files: repositories/anton-abyzov/specwithcode-dev/docs/user/add-a-machine.md, repositories/anton-abyzov/specwithcode-dev/docs/user/install.md, repositories/anton-abyzov/specwithcode-dev/apps/web/src/i18n | Test: cd repositories/anton-abyzov/specwithcode-dev && node scripts/studio-brand-audit.mjs

### T-11 No Switch warning on a machine without Switch
- AC: AC-24, AC-25 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/studio/Capacity.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/studio/Capacity.test.ts, repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/studio.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/CapacityFleet.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/CapacityFleet.test.tsx | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp test run apps/server/src/studio/Capacity.test.ts apps/web/src/components/studio/CapacityFleet.test.tsx

### T-12 One Connect sign-in per machine that stays
- AC: AC-26, AC-27, AC-28, AC-29, AC-30 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/cloud/ConnectSessionGuard.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/cloud/ConnectSessionGuard.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/account/accountMenuModel.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/account/accountMenuModel.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/clerk/ConnectSidebarAccountMenu.tsx, repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/app/DesktopClerkTokenStorage.ts, repositories/anton-abyzov/specwithcode-dev/apps/desktop/src/app/DesktopClerkTokenStorage.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/cloud/CloudLink.ts, repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/environmentHttp.ts | Test: cd repositories/anton-abyzov/specwithcode-dev && node node_modules/vite-plus/bin/vp test run apps/web/src/cloud/ConnectSessionGuard.test.ts apps/web/src/components/account/accountMenuModel.test.ts apps/desktop/src/app/DesktopClerkTokenStorage.test.ts apps/server/src/cloud/CloudLink.test.ts

### T-15 Two-account acceptance, verify and close 1296
- AC: AC-03, AC-06, AC-12, AC-26 | Files: .specweave/increments/1296-join-machines-across-connect-accounts-guided-join-identity-check-and-whose-machine-choice/reports/acceptance.md | Test: specweave verify 1296-join-machines-across-connect-accounts-guided-join-identity-check-and-whose-machine-choice

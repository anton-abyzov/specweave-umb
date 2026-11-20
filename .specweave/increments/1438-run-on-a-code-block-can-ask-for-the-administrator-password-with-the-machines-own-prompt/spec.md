# Run on a code block can ask for the administrator password with the machine's own prompt

## Problem

On November 20, 2026, in a thread on M5, an agent wrote a shell block with three `sudo` commands. The user pressed "Run on Anton M5MAX PRO". The panel under the block printed `Password:`, then `sudo: a password is required`, and showed "Stopped" with Run again and Clear. There was nowhere to type. The user copied the block into Terminal by hand. There the same block failed again with `PermissionError: [Errno 1] Operation not permitted: '/Library/Preferences/com.apple.networkextension.plist'`, and nothing explained why root was refused.

What the code does today (app checkout at branch `1434-account-switch-cleanup`, read only):

- `apps/web/src/components/chat/InlineShellRun.tsx` opens a terminal with `command` set. The server (`apps/server/src/terminal/Manager.ts`, `shellCandidateArgs`) starts the login shell with `-c <command>` on a real pty, so `sudo` does prompt on that pty.
- The panel renders the output as plain text. Its only write to the pty is Ctrl-C for Stop. So any command that waits for a password can only be stopped.
- Before running, the block asks for confirmation only under a mode stricter than Full access, or for a `fleet invite` on the wrong machine. A block that runs as administrator or rewrites `/Library` runs on one click under Full access.
- Nothing reads the result. "Operation not permitted" under root is shown as raw output.

Facts measured on M5 (macOS 27.2.1, sudo 1.9.17p2): `sudo -n true` fails with `sudo: a password is required`; `/etc/pam.d/sudo_local` does not exist, so Touch ID for sudo is off; System Integrity Protection is on. `man sudo`: the askpass helper runs only with `-A` or when there is no terminal, so setting `SUDO_ASKPASS` alone changes nothing on a pty.

## Scope

In: a code block that needs administrator rights can be run from its Run button on a Mac, with the password typed into a prompt macOS draws on that Mac. A confirmation that names administrator use and system paths before the run. A plain explanation when macOS refuses a file even as administrator. An "Open in Terminal" way out. Clear wording when the prompt cannot be shown (another device, Linux, Windows, no desktop session).

Out: typing a password anywhere inside SpecWithCode (see D-01). Turning on Touch ID for sudo (the app never edits `/etc/pam.d`). Agents' own shell tools: they still cannot use sudo with a password. Granting Full Disk Access (1386 owns that). A graphical prompt on Linux or Windows. Commands that ask for other input (a yes/no answer, an SSH passphrase).

## Acceptance Criteria

Before the run

- [ ] AC-01: A block that runs a command as administrator (`sudo` or `doas` as a command word, including after `&&`, `|`, `;` and in `$( )`) always asks before it runs, in every permission mode including Full access. The row says "Runs as administrator on <machine>" and gives Run and Cancel. A block that only mentions sudo in a comment or a quoted string does not ask.
- [ ] AC-02: When a block changes files under `/System`, `/Library`, `/etc`, `/private`, `/usr` (except `/usr/local`), `/bin`, `/sbin` or `/var`, or runs `defaults write` on a `/Library` domain, `launchctl bootstrap|bootout|enable|disable`, `csrutil`, `spctl`, `dscl` or `pfctl`, the same row lists up to three of those paths or commands and says "Changes system settings". A block that only reads them (`cat`, `ls`, `grep`, `plutil -p`, `defaults read`) does not get the row.
- [ ] AC-03: The existing behaviour stays for every other block: Full access runs on click, stricter modes ask with today's wording.

The password

- [ ] AC-04: On a Mac whose service runs in the user's desktop session, pressing Run on an administrator block shows one macOS password prompt on that Mac's screen before any line of the block runs. After a correct password the block runs to its end with no second prompt for at least 5 minutes, and each line keeps its own user: lines without `sudo` run as the signed-in user, `sudo -u <name>` runs as that name.
- [ ] AC-05: The prompt names SpecWithCode, the machine, the thread title, the device that pressed Run when it is not this Mac, and the block: up to 8 lines of it, the first 3 and then the lines that run as administrator, with a count of the lines left out and "Read the whole command in SpecWithCode first." The thread title and the device name come from the window that pressed Run and are not checked by the server. The title and the block are agent-written text: they reach the dialog as data with line breaks removed, never as script source.
- [ ] AC-06: The password never reaches a SpecWithCode process other than the helper sudo itself starts. It is absent from: the WebSocket, the terminal history file, the server log, the trace, the thread, and every provider request. Checked in tests with a stand-in `sudo` and a marker password, searching those places for the marker. Nobody but the user ever handles the real password: the real-machine check uses a throwaway administrator account.
- [ ] AC-07: Only `terminal.open` for a code-block run can start the prompt, and no tool an agent has calls it. Output text never starts it. Provider processes and agent shells never have the helper in their environment. After an elevated run ends, by finishing, failing, Stop or `exit`, the ticket is dropped and `sudo -n true` from an agent shell on that machine still fails. The real gate is the person: nothing runs as administrator until someone at that Mac types the password into a prompt that says who asked.
- [ ] AC-08: While the prompt is up the panel shows "Waiting for your password on <machine>" with Cancel. Cancel in the panel closes the prompt; Cancel in the prompt ends the run with "Password not given" and nothing from the block has run. Three wrong passwords end it with "Password not accepted".
- [ ] AC-09: When sudo needs no password (a `NOPASSWD` rule), no prompt appears and the block runs, on every platform. The exit code shown is the block's own. If a block runs so long that sudo asks again (after 5 minutes by default), the panel shows AC-16's offer instead of a bare `Password:`.

When the prompt cannot be shown

- [ ] AC-10: Run pressed from another device (another machine's window, a phone, a browser) still raises the prompt on the block's own Mac, and the panel on the pressing device says "Enter the password on <machine>'s screen". It times out after 2 minutes with "Nobody answered on <machine>" and nothing has run.
- [ ] AC-11: On Linux, Windows, or a Mac service with no desktop session (started over SSH), when sudo does need a password the block does not start. The panel says "This needs an administrator password. Run it in a terminal on <machine>." with Copy. No `Password:` line and no "Stopped".
- [ ] AC-12: On a Mac viewed from its own window, the panel also offers "Open in Terminal". It opens Terminal on that Mac and runs the block there, in the thread's folder. The panel says the output will stay in Terminal.

After the run

- [ ] AC-13: When a run on a Mac ends with a non-zero exit and its output contains "Operation not permitted", the panel adds one note under the output. If the 1386 probe says Full Disk Access is off for the service's host process: "macOS blocked a protected file. <host process> does not have Full Disk Access on <machine>." with the 1386 card's "Open System Settings". If the probe says it is on: "macOS blocked this file even for an administrator. Some system files are protected by macOS itself." The note never claims that turning the switch on will fix this command.
- [ ] AC-14: "Open in Terminal" states that Terminal has its own Full Disk Access switch, separate from SpecWithCode's.
- [ ] AC-16: A block the AC-01 check does not catch, because sudo is called inside a script (`./install.sh`, `brew install --cask`), no longer dead-ends. When its output stops at sudo's password line, the panel says "This command is asking for an administrator password" with "Stop and run again with the Mac's prompt" and "Open in Terminal". The prompt appears only after the person presses that button.

Compatibility

- [ ] AC-15: A window on a new build talking to an older server shows today's behaviour for administrator blocks plus the AC-01 row; it never sends a field the old server rejects. An old window talking to a new server runs blocks as today.

## Approach

How the prompt works (proven in T-01, see `reports/spike.md`):

1. `terminal.open` gains an optional `elevation` object that the window sets only when its classifier (AC-01) matched and the user confirmed, and only for servers reporting the `terminalElevationPrompt` capability. The server honours it only for code-block run terminals (`run-` ids). It does not need to trust the caller: the flag only makes sudo ask through the Mac's prompt, and nothing is elevated until a person there types the password.
2. The server writes a private folder (mode 0700) with a wrapper script, the block, a label file and a helper that asks with a macOS dialog (`osascript ... display dialog ... with hidden answer`) and prints the answer to sudo's pipe. The label (machine, thread title, asking device, start of the block) reaches the dialog as a file it reads, never as script source. Thread title and asking device come from the window; anyone who can open a terminal can already run anything as that user, so this adds no new reach.
3. The pty runs the wrapper: `sudo -n true`, else `SUDO_ASKPASS=<helper> sudo -A -v`, then the block unchanged in the same login shell, then `sudo -k`, and exits with the block's own code. sudo's ticket is tied to that pty, so the block's own `sudo` lines find it and no other shell does. `SUDO_ASKPASS` is set for that one command only.
4. The wrapper reports its state (waiting, started, cancelled, timeout, denied, unavailable) as an invisible terminal marker (OSC 7717) in the run's own output, which the panel reads. No new stream or RPC. Each marker carries a random value the window made for that run (16 to 64 letters and digits), and the first final state wins, so a block cannot print a state of its own (D-11).
5. Windows: the flag is ignored and the block runs as today. `sudo` on Windows raises the system's own approval prompt.

Files, in order: contracts (`packages/contracts/src/terminal.ts`: the `elevation` field and the marker; `environment.ts`: the capability); the classifier in `packages/shared`; a new server module `apps/server/src/terminal/elevatedRun.ts` (Manager.ts is 3,417 lines, over the 1,500 limit, so it gets one call and no new logic); "Open in Terminal" in `apps/server/src/terminal/openInTerminal.ts` (D-10); then `InlineShellRun.tsx`.

Rejected:

- Running the whole block through `osascript "do shell script ... with administrator privileges"`. It runs every line as root, including lines that had no `sudo`, so files end up owned by root and `sudo -u` targets change meaning.
- A password field in the panel, or passing keystrokes from the panel to the pty. The password would cross the WebSocket and, from another device, the Connect relay. Any command can print `Password:` to fish for it. 0979 AC-04 already ruled that root passwords never pass through the app.
- Wrapping `sudo` in a shell function that adds `-A`. It misses sudo called inside scripts.
- Editing `/etc/pam.d/sudo_local` to turn on Touch ID. It is a system file the user owns.

Risks: the dialog is drawn by `osascript`, so it has no Touch ID and looks like any script's dialog; T-01 checks whether a signed helper with the system authorization sheet is practical and records the answer. A service started by launchd may be unable to draw a dialog in some session types; T-01 measures the app-started and launchd-started cases on M5 and M4. If the ticket turns out not to be tied to the pty on this sudo build, AC-07 fails and the design changes before T-03.

Mockup: `reports/mockup.html` and `reports/mockup.png` in this folder (five states: confirm row, waiting, pressed from another device, no prompt available, blocked-file note).

## Decisions

### Asked
- D-01 Where may the password be typed? → only in the prompt macOS shows on the machine that runs the block; never inside SpecWithCode. From another device the prompt appears on that Mac and gives up after 2 minutes (user, November 20, 2026).

### Defaulted (change any before sw-do)
- D-02 Administrator and system-settings blocks ask before running even under Full access. 0936 D-01 says Full access never asks; that was about workers waiting on approvals, and this is a person's own click. Precedent: the `fleet invite` warning already asks under Full access.
- D-03 The ticket is dropped (`sudo -k`) when the block ends, so one password covers one run.
- D-04 Linux and Windows get the AC-11 message only. A graphical prompt there (pkexec, UAC) is a later increment.
- D-05 The blocked-file note (AC-13) is read from the output text. It only adds a note; it starts nothing.
- D-09 The app is built in a scratch copy (`~/.specwithcode/m5/scratch/2026-11-20-1438-admin-run/specwithcode`, branch `1438-admin-run`) because the shared checkout is on another thread's branch. Task Files name the repository path; tests run in the scratch copy.
- D-10 "Open in Terminal" is the same `terminal.open` call with `elevation.openIn: "terminal-app"`. The server writes the block to a private `.command` file that removes itself and opens it in Terminal, so the block starts there at once, in the thread's folder. No new RPC, and ws.ts is untouched.
- D-06 No offer to turn on Touch ID for sudo in this increment.
- D-08 The confirmation is the block's existing inline row, not the elevated access card (`AccessRequestCard`). That card grants something to remember ("this session", "always on this machine"); here nothing is granted or remembered, each run asks again. The Full Disk Access step in AC-13 does reuse the 1386 card.

- D-11 (review, November 20, 2026) The wrapper runs `sudo`, `uname`, `launchctl` and `osascript` by full path, so nothing on PATH stands in for them. Run folders are made with `mkdtemp` inside a parent that must be this user's own real folder with mode 0700; if the folder cannot be made safely the run reports "unavailable" and the block does not start. The ticket is dropped only when this run asked for it. Stop during the prompt ends the dialog and reads "cancelled".
- D-12 (review) Only `sudo`, `doas` and `sudoedit` go through the machine's prompt. `su`, `pkexec` and AppleScript's "with administrator privileges" are marked as administrator work and ask first, but they show their own prompt.
- D-13 (review, accepted) A run killed with SIGKILL cannot clean up: its ticket stays valid for that terminal only until sudo's own 5 minute limit, and its folder, which holds no secret, stays in the temporary folder.

### Open
- D-07 (measured in T-01) Is `/Library/Preferences/com.apple.networkextension.plist` unlocked by Full Disk Access or protected by macOS regardless? On M5 an agent shell could read it; the refused step was a write under root in Terminal. AC-13 is worded to hold either way.

## Tasks

### T-01 Prove the prompt and the ticket on real Macs
- AC: AC-04, AC-07, AC-09 | Files: .specweave/increments/1438-run-on-a-code-block-can-ask-for-the-administrator-password-with-the-machines-own-prompt/reports/spike.md, repositories/anton-abyzov/specwithcode/scripts/studio-verify/elevated-run-spike.sh | Test: bash repositories/anton-abyzov/specwithcode/scripts/studio-verify/elevated-run-spike.sh --check-report .specweave/increments/1438-run-on-a-code-block-can-ask-for-the-administrator-password-with-the-machines-own-prompt/reports/spike.md
- The user types the password once per case on M5. Records: the 1386 probe's own answer for Full Disk Access on M5; prompt shown from an app-started and a launchd-started service; ticket valid in the same pty and absent in another; `sudo -k` drops it; Touch ID sheet practical or not; D-07.

### T-02 Shared classifier and contract
- AC: AC-01, AC-02, AC-03, AC-15 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/shellRunElevation.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/shellRunElevation.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/package.json, repositories/anton-abyzov/specwithcode/packages/contracts/src/terminal.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/terminal.test.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/environment.ts | Test: pnpm --dir repositories/anton-abyzov/specwithcode/packages/shared test -- shellRunElevation

### T-03 Server: helper, prelude and run states
- AC: AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/terminal/elevatedRun.ts, repositories/anton-abyzov/specwithcode/apps/server/src/terminal/elevatedRun.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/terminal/Manager.ts, repositories/anton-abyzov/specwithcode/apps/server/src/environment/ServerEnvironment.ts | Test: pnpm --dir repositories/anton-abyzov/specwithcode/apps/server test -- src/terminal/elevatedRun.test.ts

### T-04 Server: Open in Terminal
- AC: AC-12 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/terminal/openInTerminal.ts, repositories/anton-abyzov/specwithcode/apps/server/src/terminal/openInTerminal.test.ts | Test: pnpm --dir repositories/anton-abyzov/specwithcode/apps/server test -- src/terminal/openInTerminal.test.ts
- Built as a variant of the same run (`elevation.openIn: "terminal-app"`), not a new RPC: see D-10.

### T-05 Window: confirm row, waiting states, notes
- AC: AC-01, AC-02, AC-03, AC-08, AC-10, AC-11, AC-12, AC-13, AC-14, AC-15, AC-16 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/InlineShellRun.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/InlineShellRun.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/shellCodeBlocks.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases | Test: pnpm --dir repositories/anton-abyzov/specwithcode/apps/web test -- src/components/chat/InlineShellRun.test.tsx

### T-06 Headless page check and a real run on M5
- AC: AC-04, AC-06, AC-08, AC-13 | Files: repositories/anton-abyzov/specwithcode/apps/web/tests/shell-code-run/main.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/shell-code-run/stubs.ts, repositories/anton-abyzov/specwithcode/apps/web/tests/shell-code-run/vite.config.ts, repositories/anton-abyzov/specwithcode/scripts/studio-verify/shell-code-run.mjs | Test: node repositories/anton-abyzov/specwithcode/scripts/studio-verify/shell-code-run.mjs ~/.specwithcode/m4/evidence/1438-elevated-run
- Then, on M5 with the released build: run the November 20 block from the screenshot, signed in to a throwaway administrator account whose password is the marker, give it in the prompt, and search the history file, server log and thread for the marker (AC-06). The user's own password is never used for this check.

### T-07 Verify and close 1438
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12, AC-13, AC-14, AC-15, AC-16 | Files: .specweave/increments/1438-run-on-a-code-block-can-ask-for-the-administrator-password-with-the-machines-own-prompt/reports/verify.md | Test: specweave verify 1438-run-on-a-code-block-can-ask-for-the-administrator-password-with-the-machines-own-prompt

# Credential rows check the tool is installed before offering a sign-in command

## Problem

Anton, November 16, 2026, on a fresh M5 after copying specweave-umb with "Copy to another machine…". The "Credentials this project uses" list gave him commands that could not work and statuses that never changed:

- Cloudflare said "Run this in a terminal: `wrangler login`", but wrangler was not installed there, so the command failed. vskill-platform declares `wrangler` in `devDependencies`; nothing global was needed.
- Google Cloud said "Its tool was not found" with no way forward.
- npm said "Check it yourself".
- After he signed in (Terminal `wrangler whoami` says logged in, `npm whoami` prints his name), "Check again" still left Cloudflare and npm on "Check it on Anton M5MAX PROLED yourself": those two rows have no check at all, so no click can change them. The "Not copied" line named `~/.wrangler/config/default.toml` and `~/.config/.wrangler/config/default.toml`, while wrangler on macOS keeps its sign-in in `~/Library/Preferences/.wrangler/config/default.toml`.

Code: `apps/server/src/projectCredentials/` (catalog, probe, scan, rpc), `apps/web/src/components/studio/CopyCredentialsChecklist.tsx`, fixtures in `apps/web/tests/folder-copy/stubs.tsx`.

## Scope

In: per row on the target machine, tool detection (the Terminal's PATH, the app's own tool folders, the project's own `node_modules/.bin` and declaring `package.json`); an install step and an "Install there" button when the tool is missing; where npm comes from; sign-in and verify commands that run as written (folder, `npx`, full path); real sign-in checks for Cloudflare, npm and SSH to known Git hosts, run with the Terminal's PATH; sign-in file checks as a fallback, with wrangler's macOS and `XDG_CONFIG_HOME` paths; "Check again" that re-runs every check on the target and shows a spinner and "Checked just now" per row.

Out: Windows (no check runs there today; rows stay as they are); a "Sign in there" that runs the sign-in for the person; installing tools without the person's click; showing an account name; Docker registry checks; new credentials in the list.

## Acceptance Criteria

- [ ] AC-01: The target machine reports, per credential, whether its tool is there and where: `terminal` (a new Terminal finds it: the login shell's PATH), `app` (only in SpecWithCode's own folders), `project` (the project's own copy: a folder whose `package.json` declares it and whose `node_modules/.bin` holds it) or `missing`. A tool that is present leaves the row as it is today.
- [ ] AC-02: A missing tool shows an install step before the sign-in command. A tool the project declares installs through the project (`cd <folder> && npm install`, with pnpm, yarn or bun picked from the lockfile); otherwise `npm install --global <package>` for npm-distributed tools, `brew install …` where Homebrew is there, and Google's installer for gcloud without Homebrew, with "open a new Terminal window" after it. A tool with no known install keeps today's sentence.
- [ ] AC-03: "Install there" shows only for a missing tool with an install command, to a connection that may operate that machine's terminal. It runs the target's own command in the terminal panel agent installs use, shows its log, and checks the row again when it ends.
- [ ] AC-04: The npm row says where npm comes from (the Node.js SpecWithCode installs; "Use these commands in Terminal" in Settings > General puts it on PATH) when a new Terminal would not find it, and gives a command that reaches the app's npm (its folder added to PATH first, since npm is a script that looks for `node` beside it).
- [ ] AC-05: Sign-in and verify commands run as written: `cd <folder> && npx wrangler login` then `npx wrangler whoami` for a project's own tool, the tool's folder added to PATH first for a tool a new Terminal would not find, the plain command otherwise. An install command is offered only when the helper it starts with (npm, npx, brew) is on the target. No command is built from text the project supplies except a folder path the target found under its own registered project, shell-quoted.
- [ ] AC-06: Cloudflare (`wrangler whoami`), npm (`npm whoami`), Google Cloud (`gcloud auth list`) and SSH (`ssh -T` to github.com, gitlab.com or bitbucket.org, only those, only when the project reaches them over SSH) are checked by running the tool on the target with the Terminal's PATH plus the app's folders, each with a time limit. A row is ready only when that run says so. The check gets the Terminal's proxy settings, key agent and the sign-in variables that one tool reads, so a sign-in through `CLOUDFLARE_API_TOKEN` or `GH_TOKEN` in a shell profile reads as it does in Terminal. A run that could not reach its service is no answer, not "not signed in". Nothing a tool prints is kept, returned, logged or shown.
- [ ] AC-07: A tool from inside a project never runs when the list opens: the project's own copy runs only after the person clicks "Check again" or "Install there", and the row says so. A tool on PATH whose real location is inside a registered project is still passed over, and no folder inside a registered project is on the PATH a check runs with.
- [ ] AC-08: When a check cannot answer, the target looks for the tool's sign-in file by name (never opened) and the row says a sign-in file is there but was not verified. The list of files includes `~/Library/Preferences/.wrangler/config/default.toml` and `$XDG_CONFIG_HOME/.wrangler/config/default.toml` when that is set; a file alone never makes a row ready.
- [ ] AC-09: "Check again" (the header's and a row's) re-runs the checks on the target machine, never a cached answer and never the source machine. Each checked row shows a spinner while it runs, then "Checked just now", then a relative time. A second click that finds the person signed in moves the row to Ready.
- [ ] AC-10: Old and new machines work together: a target from before this change answers without the new fields and rows look as today; a source from before it sends no project folders and the target falls back to PATH and app folders; every new wire field is optional and no existing literal set grows.

## Approach

Contracts (`packages/contracts/src/projectCredentials.ts`): optional `packages` and `sshHosts` on a scan row; optional `projectId`, `packages`, `sshHosts`, `projectTools` on the probe input; optional `tool` (name, state, folder, install, newShell, signIn, check, appPath) and `signInFile`, `ran` on a probe answer. `signIn` and `check` keep their short catalog text for older windows.

Server: `catalog.ts` gains a `tool` per entry (binary, npm package, Homebrew formula or cask, fallback installer) and probes for Cloudflare, npm and SSH; `tool.ts` (new) finds the tool and builds the commands; `probe.ts` runs the checks with the Terminal's PATH, matches wrangler's two fixed phrases in memory because it exits 0 signed out, pins the three Git hosts' keys so a first contact writes nothing to `known_hosts`, and caches a whole answer per credential and context; `scan.ts` records the folders whose `package.json` declares a tool and the known Git hosts reached over SSH; `rpc.ts` reads the login shell's PATH (fresh on "Check again") and resolves the target's own project folder from `projectId`.

Web: `CopyCredentialsChecklist.tsx` renders the install step, the npm note, the per-row spinner and checked time; `CopyCredentialInstall.tsx` (new) wraps the existing `AgentSetupPanel` for "Install there"; `HandoffCopyStepPanels.tsx` passes the copied project's id on Done.

Order with the SSH row rework (PR 495) and the copy-secrets fix (PR 498): both merged first, and this branch is rebased onto them. Here the SSH row gets only its readiness check, status words and "Check again" button; its steps and text are PR 495's (`CopySshKeySteps.tsx`). The known Git hosts travel as `sshHosts` on the row, apart from that PR's `sshTargets`.

After the first review: `machine.ts` (new) builds the machine the checks see, with project folders taken out of every list, and `terminalEnv.ts` (new) reads the login shell once per minute, shared and deduplicated. A project's `.npmrc` is never opened and npm is never run in the project folder (a project `.npmrc` can make npm load code), so npm's Ready is for its default registry and the list says so when the project has an `.npmrc`.

Rejected: a new install RPC with a closed list (eight registrations and no way to answer an installer's prompts; the terminal panel is the path agent installs and sign-ins already use, gated by `terminal:operate`). Running a project's own tool on open (a copied repository would run its code on the new machine unasked). Trusting sign-in files for Ready (a file can be stale; Anton's file sat in a third place).

Risks: checks now run tools from the person's PATH, including home folders, where the old check used fixed system folders only; the environment stays a short fixed list and project folders stay excluded. `npm whoami` and `wrangler whoami` ask the network, so offline reads as not signed in or unknown, as GitHub's check already does.

## Decisions

### Asked
- D-01 Install step, npm note, commands in the right folder, tests → as written by Anton, November 16, 2026
- D-02 Real checks with the Terminal's PATH, file checks as fallback, "Check again" re-runs with a spinner and checked time → as written by Anton, November 16, 2026
### Defaulted (change any before sw-do)
- D-03 "Install there" opens the terminal panel agent installs use, with the target's own command, instead of a new server-run install → default
- D-04 A project's own tool runs only after a click, not when the list opens → default
- D-05 No account name is shown; the row says Ready → default (the request allows a name, it does not ask for one)
- D-06 SSH is checked only against github.com, gitlab.com and bitbucket.org with pinned host keys; other servers stay "check it yourself" → default
- D-07 npm's Ready means its default registry; a project with an `.npmrc` gets a note under the ready rows instead of a check of that file's registry → default (the file is secret-classed and running npm in the project would run the project's settings)
- D-08 A check gets the Terminal's proxy, key agent and that tool's own sign-in variables, read from the login shell; values go to the tool only → default
- D-09 Commands for a tool a new Terminal would not find add its folder to PATH instead of naming the full path → default (the full path of a Node.js script fails without `node` on PATH)
- D-10 The SSH row is ready only when every place the project connects to is a known Git host that was checked; with a server from a script or another host it stays in the list with its steps and says what was not checked → default (a ready row would hide the steps for the places nobody asked)
- D-11 An install left running is known by its tool and its command, waited for by the row whether open or closed, and forgotten once the tool is found → default
- D-12 A project's own tool runs through `npm exec` where npm is there and npx is not; Google's installer is offered only where `curl` is; a Homebrew cask only on a Mac → default
- D-13 A target that has the check and could not run it reads "could not be checked. Try Check again."; update advice is only for a target without the check → default
### Open
- none

## Tasks

### T-01 Contracts: optional tool, install and check fields
- AC: AC-10 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/projectCredentials.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/projectCredentials.test.ts | Test: cd ~/.specwithcode/m4/verify/specwithcode/packages/contracts && specweave-studio checks run -- node ../../node_modules/vite-plus/bin/vp test run --config ../../vite.config.ts --dir . src/projectCredentials.test.ts

### T-02 Server: tool detection, install commands, real checks, file fallback
- AC: AC-01, AC-02, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/projectCredentials/catalog.ts, repositories/anton-abyzov/specwithcode/apps/server/src/projectCredentials/tool.ts, repositories/anton-abyzov/specwithcode/apps/server/src/projectCredentials/tool.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/projectCredentials/probe.ts, repositories/anton-abyzov/specwithcode/apps/server/src/projectCredentials/probe.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/projectCredentials/scan.ts, repositories/anton-abyzov/specwithcode/apps/server/src/projectCredentials/scan.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/projectCredentials/rpc.ts, repositories/anton-abyzov/specwithcode/apps/server/src/projectCredentials/machine.ts, repositories/anton-abyzov/specwithcode/apps/server/src/projectCredentials/machine.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/projectCredentials/terminalEnv.ts, repositories/anton-abyzov/specwithcode/apps/server/src/projectCredentials/terminalEnv.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/projectCredentials/manifest.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/projectCredentials/homeFiles.test.ts | Test: cd ~/.specwithcode/m4/verify/specwithcode/apps/server && specweave-studio checks run -- node ../../node_modules/vite-plus/bin/vp test run src/projectCredentials

### T-03 Web: install step, Install there, npm note, per-row check state
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-07, AC-08, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/CopyCredentialsChecklist.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/CopyCredentialsChecklist.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/CopyCredentialInstall.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/CopyCredentialInstall.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffCopyStepPanels.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/folder-copy/credentials.mjs, repositories/anton-abyzov/specwithcode/apps/web/tests/folder-copy/stubs.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/folder-copy/vite.config.ts, repositories/anton-abyzov/specwithcode/docs/studio/copy-credentials.md | Test: cd ~/.specwithcode/m4/verify/specwithcode/apps/web && specweave-studio checks run -- node ../../node_modules/vite-plus/bin/vp test run --project unit src/components/studio/CopyCredentialsChecklist.test.tsx

### T-04 PR, adversarial review, green CI, merge
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/projectCredentials/probe.ts | Test: gh pr view 500 -R anton-abyzov/specwithcode --json state -q .state | grep -x MERGED

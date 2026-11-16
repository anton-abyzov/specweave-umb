# Providers pick up a newly installed or signed-in CLI without a restart

## Problem

Settings > Providers on m3 shows Muse Code as "Not found · Muse Code did not start on this machine", with the detail "Not installed. Muse Code did not start on this machine. muse: installed binary is missing; rerun the installer. Sign in with muse here, then refresh Providers.", Command `~/.local/bin/muse` and a "Check again" button. Anton asked how the row refreshes once the CLI is installed and whether that is automatic.

What refreshes a provider today (app repository at `013d05387`):

| Trigger | What it does | Automatic |
|---|---|---|
| Check again (row) | `server.refreshProviders {instanceId}`: one live probe of that instance. It reuses the PATH read at server start. | No |
| "Checked just now" (header) | Refreshes every instance and its model list. Same stale PATH. | No |
| Find agents | A PATH search (`discover`). It returns `providers: []` and never re-probes a row that is already listed. | No |
| Health interval | Every 5 minutes (1 on Performance, 15 on Battery saver), only while a window is in the foreground. | Yes, slow |
| Sign-in probe | Every 5 s while a row is on screen, only for Claude, Codex and Muse, and only when `installed && auth != authenticated` (`makeManagedServerProvider.ts:420-423`). | Yes, but never for a not-installed row |
| Login file watch | Claude, Codex, Muse: a changed account in the login file re-probes. | Yes, sign-in only |

So a provider that is not installed is picked up only by a click or by the 5-minute timer. Four defects sit behind the screenshot:

1. Nothing re-probes a not-installed provider when its CLI appears.
2. The login shell's PATH is read once, in `fixPath()` at server start (`server.ts:1149`). A folder an installer adds to the shell profile is invisible until restart, and Check again does not re-read it. An instance with its own environment variables keeps a copy of PATH from when it was created (`ProviderInstanceEnvironment.ts:84`).
3. The Muse text stacks four instructions: the web headline "Not installed", the server's "did not start", the launcher's own stderr ("installed binary is missing; rerun the installer") and a fixed "Sign in with muse here, then refresh Providers." (`MuseConnection.ts:137`). The launcher was found; its program was missing.
4. A not-installed provider other than Claude and Codex gets only "Check again": no install command is shown anywhere for Grok, Muse, OpenCode or Pi.

## Scope

In: server-side automatic detection for every CLI and ACP provider (Claude, Codex, Grok, Muse, OpenCode, Pi, ACP registry agents run from a local command); login-shell PATH re-read; the install step in the provider row; one clear message for Muse; focus re-check on the Providers page; tests, a headless fixture and a live check on a private test server.

Out: Cursor (SDK only, never "not installed"), Antigravity and managed Codex (installed inside the app, which already re-reads when its install ends); the mobile app's provider list (it receives the same pushed status and needs no change); installing a CLI without the person's click; any read of Keychain or of a credential file.

## Acceptance Criteria

- [ ] AC-01: While a provider is on and its last check said not installed or failed to start, the server reads a mark of its command every 3 s when a client window is in the foreground. The mark is built from `stat` alone: the configured command path, or the command name in each PATH folder and each known installer folder, plus the files a driver names beside it. A changed mark runs the full check and publishes the result, so the row flips with no click and no restart.
- [ ] AC-02: The same mark is read again when a file changes in the folder that holds the command (a watch on that folder, 500 ms debounce), with no window in the foreground. A folder that cannot be watched leaves AC-01 in charge and nothing fails.
- [ ] AC-03: The mark never opens a file: a test file system that fails every read and directory listing still yields a mark. No code added here calls `security`, reads a login or credential file, or adds a Keychain access.
- [ ] AC-04: `server.refreshProviders` re-reads the login shell's PATH before it probes: always for Check again (`fresh`), the header refresh and a fresh Find agents, and otherwise only when a shell startup file changed since the last read. The read is asynchronous, one at a time, and limited to 5 s. New folders are merged into the server's PATH together with the known installer folders (`~/.local/bin` among them); nothing is removed. A provider instance with its own environment variables sees the new PATH unless it sets PATH itself.
- [ ] AC-05: The automatic loop in AC-01 notices a changed shell startup file, re-reads PATH, and then finds a CLI installed into a folder that was not on PATH at server start.
- [ ] AC-06: A not-installed row for Claude, Codex, Grok, Muse, OpenCode or Pi shows the install command for its machine's system, a Copy button, a "Run in terminal" button that runs it in the setup terminal on that machine, and the line "Waiting for the install. This page updates by itself." An ACP registry agent keeps "Install / update agent". A provider with no known command says to install it from its own site. Check again stays as a second button.
- [ ] AC-07: The server reports `cli: { state: "missing" | "broken", command, path? }` on a not-installed provider. "broken" (the file is there and does not start) reads "Installed, but it does not start" with one step, "Run its installer again", and the same command. The field is optional: an older server gets today's row, and an older window ignores it.
- [ ] AC-08: Muse messages name one cause and at most one next step, and never say "refresh Providers". The screenshot's case reads "Muse Code could not start: its installed binary is missing. Run the Muse Code installer again." A missing launcher, a file that is not executable, a sign-in failure and an unknown failure each have their own single sentence pair.
- [ ] AC-09: Opening Settings > Providers, or returning to its window, re-checks every row that is on and not ready, at most once every 10 s. Check again sends `fresh`.
- [ ] AC-10: Every new phrase is in all 8 phrase catalogs and `i18n.test.ts` passes. Removed phrases are removed from the catalogs.
- [ ] AC-11: A headless fixture renders the real status row in each new state (waiting for install, needs reinstall, no known command, registry agent, older server) in light and dark, with screenshots saved to the increment's `reports/`.
- [ ] AC-12: On a private test server with a throwaway home, a fake CLI dropped into a folder on PATH turns its row from "Not installed" to ready within 10 s with no click, and a second fake CLI installed into a new folder added to the shell profile does the same. Evidence is saved to `reports/`.
- [ ] AC-13: Muse Wonderful (`muse`, `muse-wonder-1.0`, xhigh) reviews the pull request adversarially, every finding is fixed or answered, CI is green, the pull request is merged and the release is requested.

## Approach

Server, in order:

1. `packages/shared/src/shell.ts`: an asynchronous `readEnvironmentFromLoginShellAsync` beside the synchronous reader, sharing its command builder and parser.
2. `apps/server/src/serverPath.ts` (new): `refreshServerPath({ force })`. It merges the known installer folders on every call, and reads the login shell again when forced or when the mark of the shell startup files changed. One read at a time; the last read is reused for 2 s. Windows goes through the existing `resolveWindowsEnvironment`.
3. `apps/server/src/provider/commandWatch.ts` (new): `commandCandidates`, `commandMark` (stat only) and `watchCommandFolders` (the pattern of `loginWatch.ts`).
4. `apps/server/src/provider/ProviderInstanceEnvironment.ts`: the merged environment reads PATH from the server's environment at use, unless the instance sets PATH.
5. `packages/contracts/src/server.ts`: optional `ServerProvider.cli`.
6. `apps/server/src/provider/makeManagedServerProvider.ts`: an optional `installProbe { command, environment, beside? }`. It stamps `cli` on a not-installed snapshot, runs the 3 s loop and the folder watch, and calls `refreshServerPath` before a triggered check. The mark taken at each full check is the baseline, so only a change triggers.
7. Drivers pass `installProbe`: Claude, Codex (CLI mode), Grok, Muse (beside: `.muse-version`), OpenCode, Pi and ACP registry agents whose runner is a local command.
8. `apps/server/src/provider/muse/MuseConnection.ts`: `museCheckFailure` rewritten to cause plus one step.
9. `ProviderRegistry.ts` gains `rereadPath`; the `server.refreshProviders` handler calls it through the registry it already holds, so `ws.ts` gets no new import (it sits at TypeScript's instantiation limit).

Web:

10. `apps/web/src/onboarding/providerReadiness.logic.ts`: `resolveAgentInstallCommand(agent, os)` over a wider table. `canInstallOnboardingAgent` stays Claude and Codex, so first-run setup is unchanged.
11. `providerStatus.ts`: the not-installed view reads `provider.cli`.
12. `ProviderStatusRow.tsx`: the install step (command, Copy, Run in terminal, waiting line), Check again with `fresh`.
13. `ProviderSettingsPanel.tsx`: `useLiveRefresh` over rows that are on and not ready.
14. Phrase catalogs, tests, the fixture under `apps/web/tests/provider-install-step/`, `docs/user/install.md`.

Install commands, each fetched and answering on November 16, 2026:

| Agent | macOS and Linux | Windows |
|---|---|---|
| Claude | `curl -fsSL https://claude.ai/install.sh \| bash` | `irm https://claude.ai/install.ps1 \| iex` |
| Codex | `curl -fsSL https://chatgpt.com/codex/install.sh \| sh` | `irm https://chatgpt.com/codex/install.ps1 \| iex` |
| Grok | `curl -fsSL https://x.ai/cli/install.sh \| bash` | `irm https://x.ai/cli/install.ps1 \| iex` |
| Muse Code | `curl -fsSL https://dev.meta.ai/install.sh \| bash` | `irm https://dev.meta.ai/install.ps1 \| iex` |
| OpenCode | `curl -fsSL https://opencode.ai/install \| bash` | `npm install -g opencode-ai` |
| Pi | `npm install -g @earendil-works/pi-coding-agent` | same |

Rejected: re-running the full check on a timer for not-installed rows (a process every few seconds for nothing); a recursive watch of every PATH folder per provider (hundreds of handles, and folders that do not exist yet cannot be watched); reading the login shell on every tick (up to 5 s of shell start-up each time); a new RPC (the existing one carries `fresh`).

Risks: a slow or broken shell profile (bounded by the 5 s limit, and the old PATH stays); a launcher whose program is repaired without any file near the launcher changing (covered by the focus re-check and Check again); `ws.ts` typecheck depth (no new import; checked with the typecheck gate at `--checkers 2`).

## Review

Reviewer: Muse Wonderful, provider `muse`, model `muse-wonder-1.0`, effort xhigh, adversarial (named by Anton).

## Decisions

### Asked
- none. Anton's request fixed the direction.

### Defaulted (change any before sw-do)
- D-01 "Watching the command path" is a folder watch plus a 3 s stat mark while a window is in the foreground. The mark is what decides; the watch only makes it prompt.
- D-02 A full check runs only when the mark changes, on window focus, or on a click. No timer spawns a CLI for a not-installed row.
- D-03 "Run in terminal" is the app's setup terminal on the provider's own machine, as Install is for Claude and Codex today. No outside terminal app is opened, so it also works for a remote machine.
- D-04 Install commands live in the web app, chosen by the machine's system, beside the Claude and Codex ones.
- D-05 The server's PATH only grows until restart.
- D-06 A program-missing Muse launcher stays `installed: false` with `cli.state: "broken"`, so older windows still read "Not installed".

### Open
- none

## Tasks

### T-01 Command mark, folder watch and PATH re-read
- AC: AC-01, AC-02, AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/shell.ts, repositories/anton-abyzov/specwithcode/apps/server/src/serverPath.ts, repositories/anton-abyzov/specwithcode/apps/server/src/serverPath.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/commandWatch.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/commandWatch.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/ProviderInstanceEnvironment.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/ProviderInstanceEnvironment.test.ts | Test: from the app worktree's `apps/server`, `node ../../node_modules/vite-plus/bin/vp test run src/serverPath.test.ts src/provider/commandWatch.test.ts src/provider/ProviderInstanceEnvironment.test.ts`

### T-02 Install probe in the managed provider, the `cli` field and the refresh handler
- AC: AC-01, AC-02, AC-04, AC-05, AC-07 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/server.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/makeManagedServerProvider.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/makeManagedServerProvider.installProbe.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/ProviderRegistry.ts, repositories/anton-abyzov/specwithcode/apps/server/src/ws.ts | Test: from `apps/server`, `node ../../node_modules/vite-plus/bin/vp test run src/provider/makeManagedServerProvider.installProbe.test.ts src/provider/ProviderRegistry.test.ts`

### T-03 Every CLI and ACP driver passes the probe; Muse says one thing
- AC: AC-01, AC-07, AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/provider/Drivers/ClaudeDriver.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/Drivers/CodexDriver.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/Drivers/GrokDriver.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/Drivers/MuseDriver.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/Drivers/OpenCodeDriver.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/Drivers/PiDriver.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/Drivers/AcpRegistryDriver.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/muse/MuseConnection.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/muse/MuseRuntime.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/Drivers/MuseDriver.test.ts | Test: from `apps/server`, `node ../../node_modules/vite-plus/bin/vp test run src/provider/muse src/provider/Drivers`

### T-04 The install step in the provider row, focus re-check and phrases
- AC: AC-06, AC-07, AC-09, AC-10 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/onboarding/providerReadiness.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/providerStatus.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/providerStatus.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProviderStatusRow.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProviderStatusRow.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProviderInstallStep.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProviderSettingsPanel.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ | Test: from `apps/web`, `node ../../node_modules/vite-plus/bin/vp test run src/components/settings src/onboarding src/i18n src/themeContrastClasses.test.ts`

### T-05 Headless fixture, live check on a private server, and the user guide
- AC: AC-11, AC-12 | Files: repositories/anton-abyzov/specwithcode/apps/web/tests/provider-install-step/, repositories/anton-abyzov/specwithcode/scripts/studio-verify/provider-install-detect.mjs, repositories/anton-abyzov/specwithcode/docs/user/install.md | Test: `node node_modules/vite-plus/bin/vp build --config apps/web/tests/provider-install-step/vite.config.ts && node apps/web/tests/provider-install-step/verify.mjs <reports dir>`, then `node scripts/studio-verify/provider-install-detect.mjs <reports dir>`

### T-06 Adversarial review, merge, release, verify and close
- AC: AC-13 | Files: .specweave/increments/1369-providers-pick-up-a-newly-installed-or-signed-in-cli-without-a-restart/reports/ | Test: `gh pr checks <pr> --repo anton-abyzov/specwithcode` green, then `bash scripts/release/request-release.sh --released <merge commit>`

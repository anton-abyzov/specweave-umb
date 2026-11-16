# Providers pick up a newly installed or signed-in CLI without a restart

## Problem

Settings > Providers on a second Mac shows Muse Code as "Not found · Muse Code did not start on this machine", with the detail "Not installed. Muse Code did not start on this machine. muse: installed binary is missing; rerun the installer. Sign in with muse here, then refresh Providers.", Command `~/.local/bin/muse` and a "Check again" button. Anton asked how the row refreshes once the CLI is installed and whether that is automatic.

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

Second case, reported on November 16, 2026 after Muse Code was installed on a second Mac: the row found `muse` 1.4.20 and said "Needs attention · Sign in with muse and refresh", while `muse` in a terminal on a second Mac was signed in to "Muse Code Max Usage". Reproduced on the main Mac with the same version and an empty Muse data folder:

5. The app decided "signed in" from the host's model list alone (`MuseDriver.ts`, `authenticated = models.length > 0`). `muse serve` lists models only from a catalog cached on disk, and only `muse exec` downloads that catalog; a served turn and the terminal app do not. A machine where `muse exec` never ran answers `model/list` with `source: "bundledCatalog"` and no models, exactly as a signed-out machine does. the second Mac has no such cache; m1, M5 and linux-mini list no Muse models either.
6. The fallback read of the plan, `muse usage --json`, changed shape in 1.4.20: the numbers moved from `usage` to `allowance`, stamped `asOfMs`. The parser found nothing, so the plan and its limits were dropped.

It is not a different home folder, a stale cache or an environment difference: the same check gives the same answer from a login shell.

## Scope

In: server-side automatic detection for every CLI and ACP provider (Claude, Codex, Grok, Muse, OpenCode, Pi, ACP registry agents run from a local command); login-shell PATH re-read; the install step in the provider row; one clear message for Muse; focus re-check on the Providers page; Muse Code's sign-in, plan and model list read from its own command line; tests, a headless fixture and a live check on a private test server.

Out: Cursor (SDK only, never "not installed"), Antigravity and managed Codex (installed inside the app, which already re-reads when its install ends); the mobile app's provider list (it receives the same pushed status and needs no change); installing a CLI without the person's click; any read of Keychain or of a credential file.

## Acceptance Criteria

- [ ] AC-01: While a provider is on and its last check said not installed (its command is missing, or is there and does not start), the server reads a mark of its command every 3 s when a client window is in the foreground. The mark is built from `stat` alone: the configured command path, or the command name in each PATH folder and each known installer folder, plus the files a driver names beside it. A changed mark runs the full check and publishes the result, so the row flips with no click and no restart.
- [ ] AC-02: The same mark is read again when a file changes in the folder that holds the command (a watch on that folder, 500 ms debounce), with no window in the foreground. A folder that cannot be watched leaves AC-01 in charge and nothing fails.
- [ ] AC-03: The mark is `stat` alone (files, and the folder a found command sits in): a test file system that fails every read and directory listing still yields a mark. Looking up the known installer folders may list version-manager folder names, as it does at server start; it reads no file. No code added here calls `security`, reads a login or credential file, or adds a Keychain access.
- [ ] AC-04: `server.refreshProviders` re-reads the login shell's PATH before it probes: always for Check again (`fresh`), the header refresh (`refreshModels`) and a fresh Find agents, and otherwise only when a shell startup file changed since server start or the last read. A shell that did not answer is asked again after a minute, or at once on a click. The read is asynchronous, one at a time, and limited to 5 s. New folders are merged into the server's PATH together with the known installer folders (`~/.local/bin` among them); nothing is removed. A provider instance with its own environment variables sees the new PATH unless it sets PATH itself.
- [ ] AC-05: The automatic loop in AC-01 notices a changed shell startup file, re-reads PATH, and then finds a CLI installed into a folder that was not on PATH at server start.
- [ ] AC-06: A not-installed row for Claude, Codex, Grok, Muse, OpenCode or Pi shows the install command for its machine's system, a Copy button, a "Run in terminal" button that runs it in the setup terminal on that machine, and the line "Waiting for the install. This page updates by itself." An ACP registry agent keeps "Install / update agent". A provider with no known command says to install it from its own site. Check again stays as a second button.
- [ ] AC-07: The server reports `cli: { state: "missing" | "broken", command, path? }` on a not-installed provider. "broken" (the file is there and does not start) reads "Installed, but it does not start" with one step, "Run its installer again", and the same command. The field is optional: an older server gets today's row, and an older window ignores it.
- [ ] AC-08: Muse messages name one cause and at most one next step, and never say "refresh Providers". The screenshot's case reads "Muse Code could not start: its installed binary is missing. Run the Muse Code installer again." A missing launcher, a file that is not executable, a sign-in failure and an unknown failure each have their own single sentence pair.
- [ ] AC-09: Opening Settings > Providers, or returning to its window, re-checks every row that is on and not ready, at most once every 10 s. Check again sends `fresh`.
- [ ] AC-10: Every new phrase is in all 8 phrase catalogs and `i18n.test.ts` passes. Removed phrases are removed from the catalogs.
- [ ] AC-11: A headless fixture renders the real status row in each new state (waiting for install, needs reinstall, no known command, registry agent, older server) in light and dark, with screenshots saved to the increment's `reports/`.
- [ ] AC-12: On a private test server with a throwaway home, a fake CLI dropped into a folder on PATH turns its row from "Not installed" to ready within 10 s with no click, and a second fake CLI installed into a new folder added to the shell profile does the same. Evidence is saved to `reports/`.
- [ ] AC-13: Muse Wonderful (`muse`, `muse-wonder-1.0`, xhigh) reviews the pull request adversarially, every finding is fixed or answered, CI is green, the pull request is merged and the release is requested.
- [ ] AC-14: A Muse Code check reads the account from `muse usage --json`: exit 0 with an answer is signed in, with the plan name as the sign-in's label and its session and week limits; "not logged in" is signed out, with the one line "Muse Code is not signed in. Run `muse login` in a terminal on this machine."; anything else decides nothing. The 1.4.20 `allowance` shape and the earlier `usage` shapes both parse. An API key route is not asked.
- [ ] AC-15: When the account is signed in and the host lists no models, the check has Muse Code download its model catalog once (`muse exec` with a model id no account has, in an empty folder of the app's own, 30 s limit: no turn runs), then asks a new host. It is asked again only on Check again, the header refresh, a changed login or a server restart, never on a timer.
- [ ] AC-16: Check again on a row passes `fresh` to the instance, so Muse Code's sign-in read and model list are taken again. On a private test server with the real `muse` and an empty Muse data folder, the row ends "Authenticated · Muse Code Max Usage" with its models. Evidence is saved to `reports/`.

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
- D-07 The model catalog download uses a refused request rather than a real turn: it costs nothing from the plan. It leaves one empty session in Muse Code's own list each time, which is why it is not repeated on a timer.
- D-08 The command line's word on the sign-in wins over a model list still cached from an earlier login.
- D-09 Every driver that runs a program a person installs passes the probe: Claude, Codex (CLI mode), Grok, Muse, OpenCode (local server), Pi, a local or overridden ACP registry command, and an Antigravity executable on PATH or set as a custom path. Cursor runs through an SDK inside the app and managed Codex through a runtime the app installs itself, so neither has a command to wait for.
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

### T-07 Muse Code sign-in, plan and model list from its own command line
- AC: AC-14, AC-15, AC-16 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/provider/muse/MuseAccount.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/muse/MuseAccount.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/muse/MuseDiscovery.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/Drivers/MuseDriver.ts, repositories/anton-abyzov/specwithcode/apps/server/src/ws.ts | Test: `node ../../node_modules/vite-plus/bin/vp test run src/provider/muse/MuseAccount.test.ts src/provider/muse/MuseDiscovery.test.ts src/provider/muse/MuseRuntime.test.ts src/provider/Drivers/MuseDriver.test.ts` (from `apps/server`)

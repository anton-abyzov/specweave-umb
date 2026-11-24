# SpecWeave setup finds Node.js on Windows

## Problem

On win (Windows 11, server 1.0.409), the Board's "See this project's work as a board" card says "SpecWeave needs Node.js, which this machine does not have. Install it here, then press Retry." Node.js v24.19.0 is installed and `node` runs in PowerShell. Retry shows the same card.

Cause, in `apps/server/src/project/SpecweaveSetup.ts`:

1. The server reads its PATH with `Config.String("PATH")`. Effect 4's default `ConfigProvider.fromEnv()` copies `process.env` into a plain object, which makes key lookup case-sensitive. Windows names the variable `Path`, so the lookup returns nothing. The search then skips every PATH folder, including `C:\Program Files\nodejs`, and finds no `node`, which sets `needs: "node"` and shows the card. A probe against effect 4.0.1 confirmed this: an env with only `Path` reads as `None`.
2. The copy is taken once, when the provider is first read, and `SpecweaveSetup` also reads PATH once when its layer is built. Folders added to the server's PATH later (by `fixPath`, `seedManagedToolPath`, `refreshServerPath`, or a Node.js installed while the app runs) never reach the lookup, so Retry fails the same way.

The same `Config.String("PATH")` read is in `fleetSkills.ts` (vskill lookup), `externalLauncher.ts`, `providerMaintenance.ts` and `bootService.ts`.

## Scope

In: one server-wide config provider that reads the live `process.env` and, on Windows, ignores the case of variable names. This fixes all five PATH readers. SpecWeave setup reads PATH on each press and refreshes the server's PATH first, so Retry picks up a newly installed Node.js. Windows' usual Node.js folders (`%ProgramFiles%\nodejs`, nvm-windows' `NVM_SYMLINK`, Volta under `%LOCALAPPDATA%`) join the fallback folders.

Out: the web card's wording, and Machine basics (its lookup reads the host environment directly and was not affected).

## Acceptance Criteria

- [x] AC-01: On Windows, a server whose environment names the variable `Path` (any case) reads it through `Config.String("PATH")`, and through `PATHEXT`/`APPDATA` in any case.
- [x] AC-02: The server's config provider reads `process.env` live: a variable set or changed after the provider was made is read on the next lookup.
- [x] AC-03: SpecWeave setup reads PATH on each press, so a `specweave` (or `node`) that appears on PATH after the service started is found without a restart, and Retry clears the Node.js card.
- [x] AC-04: On Windows, SpecWeave setup also looks in `%ProgramFiles%\nodejs`, `NVM_SYMLINK` and `%LOCALAPPDATA%\Volta\bin` when they are not on PATH.
- [ ] AC-05: After the release reaches win, the Board card there no longer says Node.js is missing.

## Approach

- New `apps/server/src/serverConfigProvider.ts`: `liveEnvConfigProvider(env, platform)` returns `ConfigProvider.fromEnvRecord` over `env` itself (live), wrapped on win32 in a read-only view whose lookups ignore key case. `binCli.ts` provides it at the root, so every `Config` read in the server goes through it.
- `SpecweaveSetup.ts`: read `PATH`, `APPDATA`, `PATHEXT` and the manager variables inside each run, not at layer build, and call `refreshServerPath({ force: true })` first (a person pressed the button).
- `nodeToolDirs.ts`: Windows-only folders from `ProgramFiles`, `NVM_SYMLINK` and `LOCALAPPDATA`.
- Rejected: patching each `Config.String("PATH")` call to also try `Path`. It fixes casing but not staleness, and leaves the next reader to repeat the bug.
- Risk: every `Config` read in the server becomes live. Only values that change while the server runs behave differently, and PATH is the one the server changes on purpose.

## Review

Codex GPT-6.2 Sol (Copilot Enterprise was at 100%). Round 1 ended when Codex's sign-in expired; its note (cached miss for 30 s) was fixed in `2d49ecbfa`. Round 2: typecheck blocker (ConfigError escaping `setUp`) and nvm order on Unix, both fixed in `29485e9fb`; the cached-miss test gap is not covered by a test. Windows CI: the new tests pass; 46 failures in files this change does not touch (ProjectSync, worktreeCleanupSweep, terminal, handoffGit and others) predate it.

Shipped in PR 837 (`a739fcde5`), release 1.0.415 (macOS, Windows, Linux) on November 24, 2026.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Fix at the config provider rather than per reader → provider (reversible).
- D-02 A setup press forces a PATH refresh (on Windows, two `reg query` calls; up to 5 s) → yes.
### Open
- none

## Tasks

### T-01 Live, case-insensitive server config provider
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/serverConfigProvider.ts, repositories/anton-abyzov/specwithcode/apps/server/src/serverConfigProvider.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/binCli.ts | Test: `pnpm --dir apps/server exec vitest run src/serverConfigProvider.test.ts`

### T-02 SpecWeave setup reads PATH per press and knows Windows Node folders
- AC: AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/project/SpecweaveSetup.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/SpecweaveSetup.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/nodeToolDirs.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/nodeToolDirs.test.ts | Test: `pnpm --dir apps/server exec vitest run src/project/SpecweaveSetup.test.ts src/project/nodeToolDirs.test.ts`

### T-03 Release and confirm on win
- AC: AC-05 | Files: none | Test: the Board card on win after the update

# Rescan for signed-in CLIs plus Pi and Cursor

## Problem

Slice 1 (0986, PR 559) turns on Grok and OpenCode at first startup only when the settings file never chose for them. Existing installs already persisted `enabled:false`, so they never benefit, and Pi and Cursor are not discovered at all. Proposal: /mnt/project-files/provider-auto-discovery.md (slice 2).

## Scope

In: a "Find agents" (Rescan) button in Settings > Providers that probes Grok, OpenCode, Pi and Cursor whether or not they are on, shows what it found, and offers one-click Turn on; Pi (0.80.5+, `pi --list-models`) and Cursor (`CURSOR_API_KEY` presence only) in startup discovery. Out: wizard, Copilot/Gemini, SpecWeave init/doctor, vskill (later slices).

## Acceptance Criteria

- [ ] AC-01: `server.rescanProviders` probes grok, opencode, pi and cursor regardless of their on/off state, with the startup probe's guarantees (stdin closed, CI=1, BROWSER=/usr/bin/false, hard timeouts, force-kill, no credential file read, Cursor by env presence only), runs one scan at a time, never writes settings, and returns per-driver state (ready, signed-out, outdated, not-installed, unknown) plus version.
- [ ] AC-02: Startup discovery also covers Pi (installed, 0.80.5 or newer, `--list-models` lists a model) and Cursor (`CURSOR_API_KEY` set); a Pi off that older files stored only as a stripped default is never overridden (Pi auto-enables at startup only on a fresh settings file).
- [ ] AC-03: Settings > Providers has a "Find agents" button; after a scan it lists each provider that is off with its state and a next step (Turn on, the login command, update Pi), and Turn on enables the provider through the normal settings write.

## Approach

- Contract: `packages/contracts/src/providerDiscovery.ts` (`server.rescanProviders`, own RPC group in rpc.ts).
- Server: generalize `providerDiscovery.ts` to a probe table over four drivers; `probePi` with the version gate and a `--list-models` parser; `probeCursor` by env presence; rescan handler with a semaphore; Pi added to persisted defaults and used-provider restore.
- Web: client-runtime command, a Find agents button and a results block in `ProviderSettingsPanel.tsx` (new small component file), Turn on via `updateProviderInstance`.
- Turn on from a scan is a normal user write (no autoEnabled record, no Undo notice), since the user clicked it.

## Decisions

### Asked
- D-01 Build slice 2 next → yes (Anton, 2026-10-21, "why are you blocked?" after the slice 1 merge)
### Defaulted (change any before sw-do)
- D-02 Rescan never turns anything on by itself; it offers Turn on per provider
- D-03 Pi auto-enables at startup only when the settings file did not exist, because older files dropped Pi's explicit off
### Open
- none

## Tasks

### T-01 Contract, probes and rescan handler
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specweave-studio/packages/contracts/src/providerDiscovery.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/provider/providerDiscovery.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/serverSettings.ts | Test: cd repositories/anton-abyzov/specweave-studio/apps/server && npx vp test run src/provider/providerDiscovery.test.ts src/serverSettings.test.ts

### T-02 Find agents button and results
- AC: AC-03 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/ProviderSettingsPanel.tsx, repositories/anton-abyzov/specweave-studio/packages/client-runtime/src/state/server.ts | Test: cd repositories/anton-abyzov/specweave-studio/apps/web && npx vp test run src/components/settings

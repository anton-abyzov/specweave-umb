# Grok and ACP Registry installs resolve without npm lifecycle scripts

## Problem

Turning on Grok on Anton's MacBook Pro M1Max (190) failed with "ACP Registry installed @xai-official/grok@1.0.78, but could not resolve its global command." The M1's `~/.npmrc` sets `ignore-scripts=true`, so npm skipped Grok's postinstall, which extracts the native binary into the managed `.grok-install/bin/grok`. Discovery then found no managed runtime and returned the generic error. Retry repeated the same install and failed the same way.

The same class hits every registry npm agent whose package needs its install script: `droid` (`node install.js`), `@kilocode/cli`, `@moonshot-ai/kimi-code`, `@minimax-ai/code`, `cline`. Every discovery miss (missing manifest, version mismatch, no bin entry, bin outside the prefix) produced the same message, so nobody could tell what to fix.

## Scope

In: managed npm installs run the chosen agent's lifecycle scripts even when the user's npm config ignores them; a discovery miss after install names the specific cause and the next step; Grok's message names `ignore-scripts` when its native binary is missing. Out: uv installs, binary archive installs, changing the user's npmrc.

## Acceptance Criteria

- [ ] AC-01: A managed npm install passes `--ignore-scripts=false` on the command line (above npmrc and env), so an agent whose postinstall builds its runtime (Grok) prepares on a machine with `ignore-scripts=true`.
- [ ] AC-02: When the package still cannot be resolved after install, the error names the cause (manifest missing or wrong version, no command in `bin`, command outside the npm prefix bin, Grok native binary missing) and what to do.

## Approach

`AcpRegistrySupport.ts`: managed `npm install --global` passes `--ignore-scripts=false`; a command-line flag beats both npmrc and `NPM_CONFIG_IGNORE_SCRIPTS`. The user explicitly asked to install and run this agent, and the install is confined to its managed prefix; the agent itself runs with the same trust. `discoverNpmGlobalPackage` reports why it missed through an inner inspect function; the post-install error uses that reason. Rejected: extracting Grok's binary in the engine (duplicates xAI's postinstall and does not help the other agents).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Managed installs override `ignore-scripts` → run the agent's own scripts (reversible)
### Open
- none

## Tasks

### T-01 Run lifecycle scripts for managed npm installs
- AC: AC-01 | Files: [apps/server/src/provider/acp/AcpRegistrySupport.ts, apps/server/src/provider/acp/testing/AcpRegistrySupport.npm.fixture.sh, apps/server/src/provider/acp/AcpRegistrySupport.test.ts] | Test: cd repositories/anton-abyzov/specwithcode-dev/apps/server && pnpm exec vp test run src/provider/acp/

### T-02 Specific error when an installed package cannot be resolved
- AC: AC-02 | Files: [apps/server/src/provider/acp/AcpRegistrySupport.ts, apps/server/src/provider/acp/AcpRegistrySupport.test.ts] | Test: cd repositories/anton-abyzov/specwithcode-dev/apps/server && pnpm exec vp test run src/provider/acp/

### T-03 Verify and close 1254
- AC: AC-01, AC-02 | Files: [] | Test: specweave verify 1254

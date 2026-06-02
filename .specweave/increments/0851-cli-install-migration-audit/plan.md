# Implementation Plan: CLI Install And Migration Audit

## Design

### Component: CLI Packaging And Install Harness
**Project**: specweave

Use `npm pack` plus an isolated `npm_config_prefix` temp directory to test the package as a user installs it. The harness must invoke the installed `bin/specweave.js`, not source imports, and must verify help/version/init from the installed package.

### Component: Init Workspace Flow
**Project**: specweave

Exercise the quick/non-interactive path through the real CLI in temp folders. For interactive-only migration logic, use focused tests around exported helpers first, then add a PTY smoke only where command behavior cannot be proven via public functions.

### Component: Repository Copy, Restructure, And Get Registration
**Project**: specweave

Keep the current `repositories/{org}/{repo}/` structure. Harden helper tests around `copyLocalPathIntoRepositories`, `restructureIntoRepositories`, and `specweave get`, then patch registration so current `workspace` config and legacy `umbrella` config are both supported.

### Component: Config Migration
**Project**: specweave

Find the config migration path producing repeated `v2.0 -> v3.0` messages. Persist migrations through one read-modify-write path and make no-op commands quiet after migration succeeds.

### Component: Release And Latest Verification
**Project**: specweave

After tests pass, push the branch and run the repo's release/deploy path that is actually configured. Verify newest behavior with `npm view specweave version` and a fresh isolated install of `specweave@latest`.

## Rationale

- Tests must run against the packaged CLI because install failures often hide behind source-tree success.
- Temp folders protect real workspaces while still exercising real git and npm behavior.
- Current init writes `workspace`, while `specweave get` still checks `umbrella`; the audit should close that compatibility gap.
- Optional setup must remain separate from first-run success. A user should be able to initialize now and connect sync/import/deploy later.

## Implementation Phases

### Phase 1: Reproduce And Capture Baseline

- Build the CLI.
- Pack and install it into an isolated prefix.
- Run empty-folder quick init.
- Run local helper tests for copy/restructure.
- Run `specweave get` against a temp workspace and local git fixture.
- Record baseline failures in `reports/test-report.md`.

### Phase 2: Patch The Broken Paths

- Fix package/install/init failures first.
- Fix workspace-schema registration for `specweave get`.
- Fix config migration persistence/noise.
- Fix command/help/next-step drift.
- Fix the increment creator emitting root `rubric.md` if confirmed in source tests.

### Phase 3: Verify And Ship

- Run targeted Vitest suites for changed modules.
- Run `npm run build`.
- Run smoke tests and pack-install matrix.
- Run coverage where practical before closure.
- Push the branch.
- Run deploy/publish path if credentials and scripts are available.
- Verify `specweave@latest` in a fresh isolated prefix after deployment/publish.

## Test Matrix

| Area | Command Or Test | Evidence |
| --- | --- | --- |
| Published latest | `npm view specweave version` | latest version recorded |
| Local package | `npm pack` + isolated prefix install | installed CLI runs |
| Empty init | `specweave init . --quick --adapter generic` | workspace scaffold verified |
| Existing folder quick | same command in non-empty temp folder | no implicit migration |
| Copy local | helper/integration test | `.git` and symlink skipped |
| Restructure | helper/integration test | only safe entries moved |
| Get local | `specweave get <temp-local-repo>` | config registration verified |
| Get remote no-init | `specweave get owner/repo --no-init` with mocked/fixture clone where needed | target path and config verified |
| Migration | legacy config fixture | one persisted migration |
| Release | repo-specific deploy/publish script | pushed and verified latest |

## Technical Risks

- Interactive prompts are hard to test in CI; prefer helper-level tests plus one PTY smoke if needed.
- Actual remote clones depend on network/auth; use local git fixtures for blocking tests and reserve live remote checks for final smoke.
- The umbrella-to-workspace transition may have multiple partial schemas; migration must preserve unknown fields.
- Existing worktree dirt in the umbrella root must not be staged with this increment unless directly related.

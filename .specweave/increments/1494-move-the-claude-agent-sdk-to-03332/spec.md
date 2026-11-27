# 1494 Move the Claude Agent SDK to 0.3.332

## Problem

`apps/server` pins `@anthropic-ai/claude-agent-sdk` `^0.3.276` (lock 0.3.276, `claudeCodeVersion` 2.1.276). The SDK side of the November 2026 MCP work (elicitation `property_order` in 0.3.299, MCP tasks in 0.3.319, SDK MCP server fixes in 0.3.323 to 0.3.330, `claude_code_version` on `initialize` in 0.3.296) is missing, while the CLI on the owner's machines is 2.1.331. Newest SDK on November 26, 2026: 0.3.332 (bundles 2.1.332).

Premise correction found while planning: the app never runs the SDK's bundled CLI. `pnpm-workspace.yaml` cuts all eight `@anthropic-ai/claude-agent-sdk-<platform>` packages ("The SDK always receives the user's Claude executable"), and `ClaudeSettings.binaryPath` decodes to `claude` when empty (`packages/contracts/src/settings.ts:835`, `:997`), so every thread passes `pathToClaudeCodeExecutable` = the user's `claude` on PATH. Which Claude Code a thread uses is set by the user's install, not by this bump.

## Scope

In: SDK version, lockfile and its reviewed-lock record, the release-age exclude pin, any edit the new types force, a changelog review, a live headless turn on `claude` from PATH. Out: shipping the SDK's native binaries, a minimum Claude Code version warning, the elicitation wiring owned by "MCP form questions in Claude threads".

## Acceptance Criteria

- [ ] AC-01: `apps/server` resolves `@anthropic-ai/claude-agent-sdk` 0.3.332 or later in `pnpm-lock.yaml`; `reports/sdk-changelog-review.md` lists every change between 0.3.276 and that version that touches our options, parsed messages (`system/init`, control requests, `task_*` events) or hooks, with how each is handled
- [ ] AC-02: server and web typecheck and the full server and web test suites pass through `specweave-studio checks run`
- [ ] AC-03: a headless Claude thread with `binaryPath` unset (so `claude` from PATH) starts on this branch's server code with the new SDK, lists studio-code tools, runs one and finishes a turn; `reports/live-turn.md` records the SDK version, the CLI version from `system/init`, and the SDK's unused `claudeCodeVersion`
- [ ] AC-04: the provider card shows the Claude Code version a thread will use (from `claude --version` on the same `binaryPath`); cited in `reports/sdk-changelog-review.md`

## Approach

1. `apps/server/package.json` `^0.3.332`; `pnpm-workspace.yaml` `minimumReleaseAgeExclude` pin 0.3.276 to 0.3.332 (two days old); platform overrides stay (0.3.332 lists the same eight optional packages).
2. `pnpm install --lockfile-only`; the lock diff must be the SDK entry only. Record it in `scripts/studio-toolchain/reviewed-lock-changes.json` with `propose-lock-changes.mjs` once the PR number exists, and update `LOCK_REVIEW_SHA256`.
3. Fix what typecheck finds. Known: `Query.setPermissionMode()` now resolves `{ mode } | undefined` (0.3.332), used at `ClaudeAdapterV2.ts:950`; keep any edit there minimal and note the overlap in the PR.
4. Live turn: run the adapter (or server) from the verification copy against a scratch home with the real `claude` and the studio-code MCP server.

Risk: the new SDK talks to whatever `claude` the user has. New argv flags (`--initialize-fields`, `--managed-settings-in-initialize`, `--channels`) are sent only for options we do not set; `--flag=value` (0.3.295) is standard option syntax.

## Decisions

### Asked
- none

### Defaulted (change any before sw-do)
- D-01 Keep the SDK's native binaries cut; "binaryPath unset" in AC-03 means `claude` on PATH (reversing the cut is the owner's call, ~200 MB per platform).
- D-02 Keep `mcpServersDelivery` at its default `argv`: `'initialize'` needs a CLI at least as new as the SDK, which the app cannot guarantee.
- D-03 A warning for an old `claude` on PATH is separate work.

### Open
- none

## Tasks

### T-01 Bump the SDK and lockfile
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/apps/server/package.json, repositories/anton-abyzov/specwithcode/pnpm-workspace.yaml, repositories/anton-abyzov/specwithcode/pnpm-lock.yaml, repositories/anton-abyzov/specwithcode/scripts/studio-toolchain/reviewed-lock-changes.json, repositories/anton-abyzov/specwithcode/scripts/studio-toolchain/preservation-audit.mjs, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.testkit.ts | Test: specweave-studio checks run -- node node_modules/typescript/bin/tsc --noEmit --project apps/server/tsconfig.json

### T-02 Changelog review and version display
- AC: AC-01, AC-04 | Files: .specweave/increments/1494-move-the-claude-agent-sdk-to-03332/reports/sdk-changelog-review.md | Test: test -s .specweave/increments/1494-move-the-claude-agent-sdk-to-03332/reports/sdk-changelog-review.md

### T-03 Full suites
- AC: AC-02 | Files: none | Test: specweave-studio checks run -- pnpm --filter @specweave-studio/server test && specweave-studio checks run -- pnpm --filter @specweave-studio/web test

### T-04 Live headless turn
- AC: AC-03 | Files: .specweave/increments/1494-move-the-claude-agent-sdk-to-03332/reports/live-turn.md | Test: test -s .specweave/increments/1494-move-the-claude-agent-sdk-to-03332/reports/live-turn.md

Verify and close 1494.

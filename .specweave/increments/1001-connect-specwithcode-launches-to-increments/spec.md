# Connect SpecWithCode launches to increments

## Problem

0996 made the CLI bind threads and added an opt-in edit guard, but most SpecWithCode work still never reaches an increment:

- Only the Claude and Codex adapters export `SPECWEAVE_STUDIO_THREAD_ID`; ACP (Copilot, Gemini, Grok, Antigravity, Muse), Pi and OpenCode threads never bind.
- `delegate_task`, `create_threads` and `studio_thread_launch` take no increment, so a coordinator cannot hand a worker its plan and workers do not inherit the parent's.
- SpecWithCode threads run in `~/.specwithcode/<machine>/worktrees/*`, outside the umbrella, so the CLI finds no project root there and the project-level edit hook never loads.
- A thread without a session id (Codex, Pi) cannot record `specweave small-fix`.
- The plan card has no "Open spec" action and threads that change code with no increment are invisible.

## Scope

In: CLI worktree-to-main-checkout resolution, thread-keyed small fixes, a user-level edit hook written by `specweave require-increment`; in `anton-abyzov/specwithcode-dev` one env helper at every spawn site, an `increment` field on the three launch tools with parent inheritance and a launch binding seed, coordinator instructions, an unplanned-work signal and plan card actions.

Out: a per-turn model file, `SPECWEAVE_SESSION_ID` for providers other than Claude, Codex `apply_patch` gating, a `studio://increment` scheme, schema migrations.

## Acceptance Criteria

- [ ] AC-01: From a Git worktree of a SpecWeave project (a `.git` file pointing into `<main>/.git/worktrees/`), the CLI resolves the main checkout's umbrella or project root, and the edit guard and hook launcher find the require marker there; submodule links are ignored.
- [ ] AC-02: With only `SPECWEAVE_STUDIO_THREAD_ID` set, `specweave small-fix "<why>"` records a thread-keyed marker and logs the thread, and later guarded edits in that project pass.
- [ ] AC-03: `specweave require-increment remind|enforce` also writes the edit hook group to the user's `~/.claude/settings.json` (keeping other hooks), `off` removes it, and status prints both paths.
- [ ] AC-04: Every SpecWithCode adapter that spawns a per-thread process sets `SPECWEAVE_STUDIO_THREAD_ID`, `SPECWEAVE_TOOL` and `SPECWEAVE_MODEL` (empty when unknown) for that thread; Cursor and OpenCode 2 are listed exceptions in the spawn-site test.
- [ ] AC-05: `delegate_task`, `create_threads` and `studio_thread_launch` accept `increment` (NNNN, folder, "new" or "none"); a resolved increment seeds the child's binding before its first turn without overwriting a CLI claim, appears in the result with its spec path and in the brief; workers inherit the caller's binding when omitted; under `enforce` a coordinator without `increment` is refused, under `remind` it gets a warning; a bad ref launches nothing.
- [ ] AC-06: Coordinator and tool instructions in SpecWeave projects tell the coordinator to pass `increment` and post the spec link.
- [ ] AC-07: The plan snapshot lists threads that changed code without an increment, small-fix or "none" link (excluding provider-native subagents); the plan card offers "Open spec" in the app viewer and Link/No-increment actions for unplanned threads, and the threads pane can filter them.

## Approach

CLI (`repositories/anton-abyzov/specweave`, PR #2131): `mainCheckoutOf(dir)` parses a worktree `.git` file with sync `fs`; `findEffectiveRoot` falls back to it, the guard compares projects through it, and `run.mjs`/`run-worker.mjs` inline the same function with a parity test. `small-fix` also writes `studio-<thread>` markers. `require-increment` calls `setProjectHook` on the home folder too.

App (`anton-abyzov/specwithcode-dev`, branch `feat/increment-connect`): `withSpecweaveAgentEnvironment` beside `withHeadlessBrowserEnvironment`; ACP gets a separate `agentEnvironment` merged last. `launchIncrement.ts` holds the resolve/inherit/gate rule and `ThreadIncrementProgress.ts` gains `resolveIncrementRef`, `writeLaunchBinding` (CLI v1 shape, `event: "studio-launch"`, never over a claim) and `readRequireIncrementMode`. `"none"` writes no link row. Unplanned threads come from file-change turn items minus bound, none-linked, small-fixed and provider-native children.

Rejected: a plugin-wide PreToolUse hook (reaches every user, reverses the 2.1 policy); changing the binding file format; a manual `none` link from launch (hides the thread from progress for good).

## Decisions

### Asked
- D-01 Turn on enforcement in the umbrella → yes (user, October 22, 2026); start with `remind`, then `enforce`.
### Defaulted (change any before sw-do)
- D-02 Edit hook location → user-level entry written by `require-increment`, opt-in.
- D-03 Coordinator gate → hard error under `enforce`, warning under `remind`.
- D-04 Closed increments → refused at launch.
- D-05 `SPECWEAVE_SESSION_ID` → left unset for providers other than Claude.
- D-06 Increments created from a SpecWithCode worktree → written to the main checkout's umbrella.
### Open
- none

## Tasks

### T-01 Resolve worktrees to their main checkout
- AC: AC-01 | Files: src/utils/main-checkout.ts, src/utils/find-project-root.ts, src/core/hooks/handlers/require-increment.ts, plugins/specweave/hooks/run.mjs, plugins/specweave/hooks/run-worker.mjs, tests/unit/utils/main-checkout.test.ts | Test: npx vitest run tests/unit/utils tests/unit/hooks tests/unit/core/hooks/require-increment.test.ts

### T-02 Thread-keyed small fixes
- AC: AC-02 | Files: src/cli/commands/small-fix.ts, src/core/hooks/handlers/require-increment.ts, plugins/specweave/hooks/run.mjs, tests/unit/cli/commands/small-fix.test.ts | Test: npx vitest run tests/unit/cli/commands/small-fix.test.ts tests/unit/core/hooks/require-increment.test.ts

### T-03 User-level edit hook from require-increment
- AC: AC-03 | Files: src/cli/commands/require-increment.ts, tests/unit/cli/commands/require-increment.test.ts | Test: npx vitest run tests/unit/cli/commands/require-increment.test.ts

### T-04 SpecWeave env at every SpecWithCode spawn site
- AC: AC-04 | Files: apps/server/src/provider/RuntimeInstructions.ts, apps/server/src/orchestration-v2/Adapters/*AdapterV2.ts, apps/server/src/provider/Drivers/MuseDriver.ts, apps/server/src/provider/Drivers/AntigravityDriver.ts, apps/server/src/provider/providerSpawnSites.test.ts | Test: bun run test apps/server/src/provider/providerSpawnSites.test.ts

### T-05 Increment on launch tools, binding seed and instructions
- AC: AC-05, AC-06 | Files: apps/server/src/project/ThreadIncrementProgress.ts, apps/server/src/project/launchIncrement.ts, packages/contracts/src/orchestratorMcp.ts, apps/server/src/mcp/OrchestratorMcpService.ts, apps/server/src/mcp/toolkits/project/handlers.ts, apps/server/src/mcp/toolkits/project/tools.ts, apps/server/src/orchestration-v2/ThreadLaunchService.ts, apps/server/src/provider/StudioOrchestrationInstructions.ts, apps/server/src/project/ProjectWorkspaceService.ts | Test: bun run test apps/server/src/project/ThreadIncrementProgress.test.ts apps/server/src/mcp/OrchestratorMcpService.test.ts

### T-06 Unplanned-work signal and plan card actions
- AC: AC-07 | Files: packages/contracts/src/threadIncrementProgress.ts, apps/server/src/project/ThreadIncrementProgressService.ts, apps/web/src/components/chat/ThreadPlanCard.tsx, apps/web/src/components/ChatView.tsx, apps/web/src/studio/threadPlanProgress.ts, apps/web/src/components/studio/PlanProgressChip.tsx, apps/web/src/components/studio/shell/ThreadsPane.tsx | Test: bun run test apps/server/src/project/ThreadIncrementProgressService.test.ts apps/web/src/studio/threadPlanProgress.test.ts

### T-07 Verify and close 1001
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07 | Files: none | Test: specweave verify 1001

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
- [ ] AC-08: Increments are recommended, never required: the "threads changed code without an increment" notice and row chips use neutral styling, the notice can be hidden per project with the choice surviving reloads, the Threads sort menu turns it back on, hiding also stops the plan card opening itself, per-thread "No increment needed" and `specweave small-fix` stay supported, and `remind` text says the change may proceed without one.
- [ ] AC-09: Codex shell commands receive `SPECWEAVE_STUDIO_THREAD_ID`, `SPECWEAVE_TOOL` and `SPECWEAVE_MODEL` for their thread even when the user's `shell_environment_policy` inherits only core variables, through `-c` config overrides on the thread's own app-server process that leave the user's config file and other `set` entries untouched; a real Codex child shell under `inherit = "core"` proves it, and a SpecWeave ledger write from that shell binds the right thread.
- [ ] AC-10: A SpecWeave claim, or a manual link, resolves in a registered checkout of the project's own repository (a linked Git worktree proven both ways, or the planning umbrella above it) even when the thread has no registered worktree; an unrelated sibling folder, a forged `.git` file and a submodule stay refused, and no other directory access widens.
- [ ] AC-11: The unplanned list counts only threads whose own or provider-native children's completed file changes, in runs that were not rolled back, touched files other than reports and specifications; report- or spec-only work is listed separately as documentation, and a provider checklist without an increment stays legitimate.
- [ ] AC-12: Thread rows and the plan card name a provider checklist as the agent's checklist and a linked increment by its number, so neither reads as the other, and the no-increment chip stays neutral; headless light and dark captures show both.
- [ ] AC-13: Dismissing the notice acknowledges, per project on this device, the threads it counts at that moment: the notice goes away and returns only when a thread that was not acknowledged changes code without an increment, counting and filtering only those. Acknowledged threads keep their row chip and their plan card with its unplanned header and Link/No-increment actions, and are never marked planned, linked or exempt. The sort menu switch still turns the notice off entirely; turning it back on clears that project's acknowledgments, so the full count shows again.

## Approach

CLI (`repositories/anton-abyzov/specweave`, PR #2131): `mainCheckoutOf(dir)` parses a worktree `.git` file with sync `fs`; `findEffectiveRoot` falls back to it, the guard compares projects through it, and `run.mjs`/`run-worker.mjs` inline the same function with a parity test. `small-fix` also writes `studio-<thread>` markers. `require-increment` calls `setProjectHook` on the home folder too.

App (`anton-abyzov/specwithcode-dev`, branch `feat/increment-connect`): `withSpecweaveAgentEnvironment` beside `withHeadlessBrowserEnvironment`; ACP gets a separate `agentEnvironment` merged last. `launchIncrement.ts` holds the resolve/inherit/gate rule and `ThreadIncrementProgress.ts` gains `resolveIncrementRef`, `writeLaunchBinding` (CLI v1 shape, `event: "studio-launch"`, never over a claim) and `readRequireIncrementMode`. `"none"` writes no link row. Unplanned threads come from file-change turn items minus bound, none-linked, small-fixed and provider-native children.

Binding repair (October 24, 2026, branch `fix/1001-increment-binding-transport`; root cause in `/Users/antonabyzov/.specwithcode/m4/evidence/optional-increments-1001/unplanned-root-cause-20261023.md`): Codex gets the identity as `-c shell_environment_policy.set.*` arguments on the thread's own app-server (one per thread, like its process environment; the model stays empty, and the exact-match replay fixtures for `thread/start` stay unchanged); `registeredCheckout.ts` proves a linked worktree of the project's repository; the unplanned query applies the rolled-back exclusion to native children and drops report/spec-only paths; chips say "Checklist" for provider todo lists.

Dismiss (October 24, 2026, Anton: "there should be a way to dismiss this message"): `unplannedNotice.ts` keeps a second device-local list, the acknowledged thread ids per `environment:project`, beside the existing hidden-projects list. The notice's × acknowledges the threads it currently counts. The notice counts unplanned threads minus acknowledged ones, so it comes back only for a thread it has not counted before. Nothing on the server changes; the unplanned evidence stays as it is.

Rejected: a plugin-wide PreToolUse hook (reaches every user, reverses the 2.1 policy); changing the binding file format; a manual `none` link from launch (hides the thread from progress for good).

## Decisions

### Asked
- D-01 Turn on enforcement in the umbrella → yes (user, October 22, 2026); start with `remind`, then `enforce`.
### Defaulted (change any before sw-do)
- D-02 Edit hook location → user-level entry written by `require-increment`, opt-in.
- D-03 Coordinator gate → hard error under `enforce`, warning under `remind`.
- D-04 Closed increments → refused at launch.
- D-05 `SPECWEAVE_SESSION_ID` → left unset for providers other than Claude.
- D-07 Increments are recommended, not mandatory (Anton, October 23, 2026): the umbrella stays on `remind`; `enforce` is a team opt-in only.
- D-06 Increments created from a SpecWithCode worktree → written to the main checkout's umbrella.
- D-08 External roots (October 24, 2026 repair) → only a linked Git worktree of the project's own repository, verified through its `.git` file and the repository's `worktrees/<name>/gitdir` back-link, without the Git CLI; arbitrary sibling folders stay refused. A thread keeps one current increment; additive history is out of scope.
- D-09 Dismiss scope (October 24, 2026) → acknowledgment is per thread, per project, on this device, like Hide and the pane's sort order. A thread that was already acknowledged and changes more code does not bring the notice back; "No increment needed" or a linked increment remains the durable per-thread answer. Syncing it across devices would need a server setting and is out of scope.
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

### T-08 Optional increments: informational, hideable notice
- AC: AC-08 | Files: apps/web/src/studio/unplannedNotice.ts, apps/web/src/components/studio/shell/UnplannedThreads.tsx, apps/web/src/components/studio/shell/ThreadsPane.tsx, apps/web/src/components/ChatView.tsx, apps/web/src/components/chat/ThreadPlanCard.tsx, src/core/hooks/handlers/require-increment.ts, src/templates/AGENTS.md.template | Test: node scripts/studio-verify/plan-progress.mjs

### T-07 Verify and close 1001
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08 | Files: none | Test: specweave verify 1001

### T-10 Carry SpecWeave identity through Codex's shell policy
- AC: AC-09 | Files: apps/server/src/orchestration-v2/Adapters/CodexAdapterV2.ts, apps/server/src/provider/RuntimeInstructions.ts, apps/server/src/orchestration-v2/Adapters/CodexAdapterV2.test.ts, apps/server/src/orchestration-v2/Adapters/CodexShellEnvironment.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/Adapters/CodexShellEnvironment.test.ts apps/server/src/orchestration-v2/Adapters/CodexAdapterV2.test.ts

### T-11 Accept registered checkouts of the project's repository
- AC: AC-10 | Files: apps/server/src/project/registeredCheckout.ts, apps/server/src/project/registeredCheckout.test.ts, apps/server/src/project/ThreadIncrementProgress.ts, apps/server/src/project/ThreadIncrementProgress.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/project/registeredCheckout.test.ts apps/server/src/project/ThreadIncrementProgress.test.ts

### T-12 Truthful unplanned detection
- AC: AC-11 | Files: apps/server/src/project/ThreadIncrementProgressService.ts, apps/server/src/project/ThreadIncrementProgressService.test.ts, packages/contracts/src/threadIncrementProgress.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/project/ThreadIncrementProgressService.test.ts

### T-13 Provider checklist versus linked increment in the UI
- AC: AC-12 | Files: apps/web/src/studio/threadPlanProgress.ts, apps/web/src/studio/threadPlanProgress.test.ts, apps/web/src/components/studio/PlanProgressChip.tsx, apps/web/src/components/studio/shell/UnplannedThreads.tsx, apps/web/src/components/chat/ThreadPlanCard.tsx, apps/web/tests/plan-progress/main.tsx, scripts/studio-verify/plan-progress.mjs | Test: node scripts/studio-verify/plan-progress.mjs

### T-14 Pull request and exact-head evidence for the release owner
- AC: AC-09, AC-10, AC-11, AC-12 | Files: none | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/Adapters/CodexShellEnvironment.test.ts apps/server/src/project/registeredCheckout.test.ts apps/server/src/project/ThreadIncrementProgress.test.ts apps/server/src/project/ThreadIncrementProgressService.test.ts apps/web/src/studio/threadPlanProgress.test.ts
- Deliver a reviewed pull request and evidence at its exact head to the "Complete screenshot sessions" release owner. No merge, release or install here.

### T-15 Dismiss the notice until another thread needs it
- AC: AC-13 | Files: apps/web/src/studio/unplannedNotice.ts, apps/web/src/studio/unplannedNotice.test.ts, apps/web/src/components/studio/shell/ThreadsPane.tsx, apps/web/src/components/studio/shell/UnplannedThreads.tsx, apps/web/src/components/ChatView.tsx, apps/web/tests/plan-progress/main.tsx, scripts/studio-verify/plan-progress.mjs, docs/studio/plan-progress.md | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/studio/unplannedNotice.test.ts

### T-16 How serious the unplanned count is, and what a handoff carries
- AC: AC-13 | Files: none | Test: test -s /Users/antonabyzov/.specwithcode/m4/evidence/optional-increments-1001/dismiss/seriousness.md
- Classify the threads the installed app counts against claims, specs, ledgers, branches and pushed work, without database access. Say what specs, ledgers and pushed commits carry to another tool or machine, and what still needs an explicit handoff.

### T-17 Updated pull request head for the release owner
- AC: AC-13 | Files: none | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/studio/unplannedNotice.test.ts apps/web/src/studio/threadPlanProgress.test.ts

### T-18 Base64 evidence frames are report data
- AC: AC-11 | Files: apps/server/src/project/ThreadIncrementProgressService.ts, apps/server/src/project/ThreadIncrementProgressService.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/project/ThreadIncrementProgressService.test.ts
- From the October 24, 2026 seriousness audit, some documentation-only threads still counted as unplanned because of base64 frames and capture scripts written next to their evidence. `.b64` now joins the report data extensions inside `reports` and `evidence` folders. Scripts (`.py`, `.sh`, `.mjs`) stay code, even beside evidence. A rule that treated scripts outside a thread's known roots as evidence was tried and rejected: a thread can edit another repo's `src/reports/view.ts`, and the existing test that requires that edit to count as code would fail. Dismiss (T-15) covers the remaining noise.

### T-09 Verify and close 1001 after installed optional-notice acceptance
- AC: AC-08, AC-13 | Files: none | Test: specweave verify 1001
- Also waits for T-10 to T-18 and installed evidence of the binding repair and Dismiss; T-09 stays the last task.
- The earlier T-07 installed acceptance predates T-08. After the existing release owner installs a build containing app PR #624 and PR #658 at `73fd60a48` (or a squash merge proven equal to it), run D1 to D13 of `/Users/antonabyzov/.specwithcode/m4/evidence/optional-increments-1001/binding-repair/t09-installed-acceptance.md` in the installed UI: Dismiss keeps row chips and plan cards and returns only for a thread it has not counted (AC-13), reload persistence, the sort menu switch hiding the notice, row chips and the self-opening plan card, and turning it back on restoring the full count (AC-08). Preserve the app's manual UI acceptance requirement. Record the installed version, source commit and screenshots separately from fixture evidence, then run verification, fresh-context review and completion.

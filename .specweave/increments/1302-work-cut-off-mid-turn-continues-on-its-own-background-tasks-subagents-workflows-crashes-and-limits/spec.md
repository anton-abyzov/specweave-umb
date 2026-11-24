# Work cut off mid-turn continues on its own: background tasks, subagents, Workflows, crashes and limits

## Problem

A thread that ends its turn with "I'll review the results when the workflow reports back" waits for a completion notice from the provider's own process. When that process dies (app update, service restart, crash, idle release, usage limit), the notice never comes and nothing starts a turn. The thread sits idle until a person asks "are you stuck?".

Evidence, November 11, 2026:

- "Build SpecOS on Linux" on linux-mini: a background Workflow (server and desktop-shell tracks) was cut by a session restart. The agent noticed only after Anton asked.
- On M4 the same day: the football passing sim build was resumed by hand after each update, a long worker stopped at the 1.0.235 restart, and limit fallbacks continued some threads and not others.
- The M4 database holds 4 runs from the last 24 hours with recorded lost background work and no later turn (`specweave-studio db query`, 15,600 runs scanned).

Root causes, read on `origin/main` at `c143906485` (paths under `apps/server/src/orchestration-v2/`):

1. **Lost background work is recorded, never acted on.** Startup recovery clears every roster and records the lost tasks on the latest run (`ProviderRuntimeRecoveryService.ts:434-497`), but writes a continuation effect only for a run that was still `running` (`RestartContinuation.ts:39-63`, comment: "must not wake a settled run"). `continueRestartedRun` and the orchestrator admission both refuse a settled source (`RestartContinuation.ts:157-163`, `Orchestrator.ts:5887-5895`). The note is prepended only to the next turn someone else starts (`ProviderTurnStartService.ts:1373-1391`).
2. **The live sweep settles and stops there.** `StrandedSubagents` settles native subagents whose process is gone and writes the same note with `effects: []` (`StrandedSubagents.ts:289-301`). It covers subagents only.
3. **A roster outlives its process while the service keeps running.** When the Claude CLI process exits between turns, `finalizeActiveTurnAfterQueryExit` returns without an event (`Adapters/ClaudeAdapterV2.ts:8469-8473`). When the idle pin expires after 4 hours the session is released with a log line (`ProviderSessionManager.ts:1236-1287`). The persisted roster keeps showing background shells and Workflows as waiting, and no sweep clears it.
4. **The provider tells the model only on the next turn.** Claude Code reports orphaned shells, agents and workflows ("orphaned by previous process exit", `task_notification` with reason `worker_restart`) when a resumed process starts, which needs a host-started turn. Codex has no orphan notice at all.
5. **Limits: resume at reset is off by default.** `autoResumeLimitedThreads` decodes to `false` (`packages/contracts/src/settings.ts:1874`). A limit stop with no fallback target with headroom arms nothing and waits for a person; that is the main reason fallbacks "continue some threads but not others".

## Scope

In: one server rule that starts a turn when a thread's awaited background work was lost; clearing rosters whose process is gone while the service runs; resume at reset on by default; user docs and changelog. It runs on every machine's own service, so Linux and Windows workers get it with the release.

Out: restarting native tasks inside the provider process (not possible: they die with it); a delegated child that fails on a limit reporting to its parent before its own recovery (follow-up); a coordinator held "blocked" after a limit (owned by another thread); Codex background terminals lost while the service keeps running (no roster exists to detect them); context overflows older than one hour.

## Acceptance Criteria

- [ ] AC-01: After a service restart, a thread whose turn had settled while a background shell, subagent or Workflow was still running gets one automatic turn that lists the lost work and tells the agent to check what landed and resume. Nobody sends a message.
- [ ] AC-02: The same happens while the service keeps running: a roster whose provider process is gone (process exit between turns, idle release) is cleared after two sweeps in a row agree, the lost tasks are recorded, and the thread gets the same automatic turn.
- [ ] AC-03: No automatic turn starts when a person stopped the run, when a later run or queued message exists, when the thread is archived, deleted, settled by a person, on another machine or a provider-native subagent, when it is a delegated task that is over or whose parent a person stopped, when an agent stopped the run, when its project is paused, archived, fenced or has "Continue threads after restart" off, when the run ended more than 24 hours ago, or while an update holds the service.
- [ ] AC-04: A thread is woken once per source run. Lost shells and monitors alone wake it once per person-started turn; lost subagents or Workflows wake it at most 3 times in a row without a person's message. At most 3 threads are woken per sweep, and a wake the provider failed before taking is sent once more after 3 minutes.
- [ ] AC-05: A limit stop with no fallback target resumes at the reset time by default (`autoResumeLimitedThreads` defaults to true); turning it off in Settings keeps such threads waiting.
- [ ] AC-06: The automatic turn reads "Resumed after restart" in the timeline, and for Claude Code names the native routes: SendMessage to the agent id, Workflow `resumeFromRunId`, the shell's output file.

## Approach

All product paths are from the umbrella root under `repositories/anton-abyzov/specwithcode-dev/`.

1. `apps/server/src/orchestration-v2/LostBackgroundWorkWake.ts` (new). A pure decision, `lostWorkWake`, over the thread's runs, provider turns, interrupt requests and messages; and a sweeper started once a minute (first sweep after startup recovery):
   - Step 1, dead rosters: a root provider thread with `pendingBackgroundTasks`, no run in progress and no live process (`session.liveBackgroundWork`, the check `StrandedSubagents` uses) on two sweeps in a row gets its roster cleared and `lostWorkNoteEvents` written.
   - Step 2, wake: for a thread whose latest started run is a settled note source (`isRestartNoteSource`) with nothing after it, dispatch `message.dispatch` with id `message:restart-continuation:<runId>`. The turn start prepends the recorded note itself (`pendingRestartCancelledBackgroundWork`), which also marks it delivered.
2. `ProjectionStore.ts`: recovery kind `lost-background-work` (SQL and in-memory), bounded to runs that ended in the last 24 hours plus threads with a roster.
3. `runtimeLayer.ts`: wire the sweeper next to the other recovery workers.
4. `packages/contracts/src/settings.ts`: `autoResumeLimitedThreads` default true.
5. `docs/user/updating.md`, `docs/user/thread-sidebar.md`, `CHANGELOG.md`: say what now continues by itself. The project-wake skill is not in this repository (it is installed under `~/.agents/skills`) and stays the manual sweep for what is older than 24 hours.
6. `getRecoveryThreadIds` takes an optional `since`, so the 24-hour bound follows the app's clock (the replay harness runs on a fixed clock).

Why derive in a sweep instead of writing an effect where the note is recorded: the note is written from four places (startup recovery, the stranded sweep, a Stop settlement, the provider event ingestor). A rule over persisted state covers all four and any later one, survives a restart between the note and the wake, and is idempotent by message id.

Rejected:

- Relaxing `continueRestartedRun` to accept settled sources: two admission sites carry refusal logic for pending effects of older versions, and the note continuation path would need its `settled` branch re-proved. A plain server message needs neither.
- Relying on Claude Code's own orphan notice: it fires only when a host starts a turn, and Codex has none.
- A SessionStart hook or `CLAUDE_CODE_RESUME_INTERRUPTED_TURN`: both act on an interrupted turn, and the stuck case is a completed one.

Risks: a thread that left a dev server running is woken once after a restart (bounded by AC-04, 24 hours and the project switch). First start on the new version wakes the threads whose work was lost in the last 24 hours; that is the wanted repair.

## Decisions

### Asked
- none. The request names the goal and rules; nothing critical was left open.

### Defaulted (change any before sw-do)
- D-01: Lost background work wakes a settled thread. This reverses the earlier "must not wake a settled run" rule on the owner's instruction of November 11, 2026 ("the work must continue on its own, with nobody asking are you stuck").
- D-02: The wake reuses `message:restart-continuation:<runId>`, so web and mobile show the existing "Resumed after restart" line, restart-delivery queue rules apply, and one source run can never get both a continuation and a wake.
- D-03: `autoResumeLimitedThreads` defaults to true. A value saved as off stays off; an install that never touched the switch now resumes at the reset. The per-project `autoResume` still turns it on for one project.
- D-04: Gate on the existing `continueThreadsAfterServerUpdate` switch instead of a new setting.
- D-05: Limits on wakes: 24 hours, once per source run, shells and monitors once, subagents and Workflows 3 in a row.
- D-07: After the round 1 review (NO-SHIP on `f1f218d20b`): shell-only losses still wake once, because the owner's goal names background commands; wakes are capped at 3 per sweep; a wake that failed before any provider turn is retried once, never for a usage limit, permission or validation failure; a delegated thread is woken only while its parent has an active task for it and was not stopped; the roster is re-read right before it is cleared.
- D-06: Work out of tree (the shared checkout is held by feat/1284-calm-model-picker): edits and tests in a scratch export of `origin/main`, commit through a temporary index.

### Open
- none

### Follow-ups from the round 2 review (SHIP on `afefa0fed0`, none blocking)
- A delegated child whose process dies while the service keeps running: clearing its roster lets the parent task finalize with the child's old "waiting" message, and the wake is then skipped. Fix: do not clear a delegated child's roster before the lost-work note reaches the parent.
- The wake does not check a pending `effect:restart-continuation:<run>`; in the first sweep both can dispatch and the agent gets two turns. Fix: re-read message ids right before dispatch and skip while that effect is pending.
- A run still preparing with no provider thread id does not block roster clearing.
- A source run that was a native maintenance command (`/compact`) can be woken; reuse `isNativeMaintenanceCommand`.
- The turn reads "Resumed after restart" when no restart happened.

## Tasks

### T-01 Wake rule and sweeper
- AC: AC-01, AC-03, AC-04, AC-06 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/LostBackgroundWorkWake.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/LostBackgroundWorkWake.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/ProjectionStore.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/ProjectionRecovery.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/runtimeLayer.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/testkit/OrchestratorReplayRestartBackgroundNote.integration.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/SettingsPanels.restore.test.tsx | Test: cd ~/.specwithcode/m4/scratch/2026-11-11-1302-cutoff/tree && node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/LostBackgroundWorkWake.test.ts apps/server/src/orchestration-v2/ProjectionRecovery.test.ts apps/server/src/orchestration-v2/testkit/OrchestratorReplayRestartBackgroundNote.integration.test.ts

### T-02 Clear rosters whose process is gone
- AC: AC-02 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/LostBackgroundWorkWake.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/LostBackgroundWorkWake.test.ts | Test: cd ~/.specwithcode/m4/scratch/2026-11-11-1302-cutoff/tree && node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/LostBackgroundWorkWake.test.ts

### T-03 Resume at reset by default
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/settings.ts | Test: cd ~/.specwithcode/m4/scratch/2026-11-11-1302-cutoff/tree && node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/UsageLimitRecoveryWorker.test.ts packages/contracts

### T-04 User docs and changelog
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode-dev/docs/user/updating.md, repositories/anton-abyzov/specwithcode-dev/docs/user/thread-sidebar.md, repositories/anton-abyzov/specwithcode-dev/CHANGELOG.md | Test: git -C repositories/anton-abyzov/specwithcode-dev show origin/main:CHANGELOG.md | grep -q "Work that is cut off now continues"

### T-05 Ship: PR, exact-head review, CI, merge, release request
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/LostBackgroundWorkWake.ts | Test: git -C repositories/anton-abyzov/specwithcode-dev fetch origin main --quiet && git -C repositories/anton-abyzov/specwithcode-dev cat-file -e origin/main:apps/server/src/orchestration-v2/LostBackgroundWorkWake.ts

### T-06 Verify and close 1302
- AC: AC-01 | Files: .specweave/increments/1302-work-cut-off-mid-turn-continues-on-its-own-background-tasks-subagents-workflows-crashes-and-limits/spec.md | Test: specweave verify 1302

# Data loss and hang fixes from the upstream review

## Problem

The upstream triage of November 14, 2026 (`.specweave/increments/1346-t3-code-changes-since-november-2/reports/2026-11-15-t3-code-triage-november-2-to-november-14-2026-bb97f4-af68df.md`, section 2) lists rows R1 to R15 as open in our tree at `013d05387`. Each loses a user's data, loses running work, or stops the app:

- R1: a duplicate plain variable row deletes a stored secret (`serverSettings.ts:1797-1806`).
- R2: four hung provider calls, or four title jobs, stop every thread (`EffectWorker.ts:1043-1052`).
- R3: a failed log write crashes the server and leaves the ownership lock behind (no `stdout`/`stderr` error handler).
- R4: `delegate_task` in wait mode outlives Node fetch's 300 s idle timeout, so the caller never learns the task id (`OrchestratorMcpService.ts:182`, `:3246-3262`).
- R6: a hung Codex `initialize` blocks every later Codex run; an unlisted Codex error code leaves the turn running (`CodexAdapterV2.ts:1975`, `schema.gen.ts:17886`).
- R7: the file editor saves non-UTF-8 files lossily and drops a BOM (`WorkspaceFileSystem.ts:427`).
- R8: a remote branch switch detaches HEAD silently; the branch picker stops a running turn (`GitVcsDriverCore.ts:4549`, `BranchToolbarBranchSelector.tsx:211`).
- R9: revert leaves files a new `.gitignore` hides and files staged before the first commit (`GitVcsDriver.ts:1341-1375`).
- R10: a chunk that fails after boot reloads forever (`chunkReloadGuard.ts:20`, `main.tsx:88`).
- R11: the ACP wire parser ends a session on a blank line and drops a final message without a newline; refused turns show as completed; "Always allow" cancels a turn that offers only allow-once (`packages/effect-acp/src/protocol.ts:151-166`, `AcpAdapterV2.ts:1321-1332`).
- R12: a failed delegate loses its report; Codex auto-compaction loops; background git takes the user's locks (`SubagentProjection.ts:227`, `CodexAdapterV2.ts:4819-4826`, `GitVcsDriverCore.ts:1378`, `:2987`, `:2387`).
- R13: storage cleanup removes worktrees that hold nested repositories or edits hidden from `git status` (`storageCleanup.ts:417-426`, `:565-583`).
- R14: a remote thread's relative image renders this machine's file (`packages/client-runtime/src/state/assets.ts:127-138`).
- R15: a send lost on a socket drop is never resent, and an unanswered send spins forever (`packages/client-runtime/src/operations/commands.ts:472`).

## Scope

In: hand ports of R1 to R4 and R6 to R15, each with a test that fails before the fix, in reviewable PRs, merged and released. R5 (`4c8cb0445d`, queue order) was added on November 14, 2026 after Anton decided to adopt it. Out: R16 (lost delegated results) is increment 1349.

## Acceptance Criteria

- [ ] AC-01: Saving settings with a plain row and a kept redacted sensitive row of the same name keeps the stored secret.
- [ ] AC-02: A provider call that never returns holds one effect slot at most and other threads' effects keep running; concurrent title generations are capped below the worker count.
- [ ] AC-03: An error on the server's stdout or stderr stream does not crash the process; shutdown still releases the ownership lock.
- [ ] AC-04: `delegate_task` in wait mode returns its task handle before 300 s; a steer or interrupt during the wait still upgrades the wake so the child's result reaches the parent.
- [ ] AC-05: A Codex `initialize` that never answers times out and the session is retired, so the next Codex run starts a fresh one; a `turn/completed` with an unlisted error code ends the turn as failed.
- [ ] AC-06: The file editor refuses to save a file that is not valid UTF-8 and says why; a UTF-8 file with a BOM keeps it.
- [ ] AC-07: Switching to a remote branch checks out a local tracking branch, never a detached HEAD; picking a branch that would change the worktree while a turn runs is refused with a notice and the turn keeps running.
- [ ] AC-08: Reverting a turn removes files a new `.gitignore` hides and unstages files staged before the first commit.
- [ ] AC-09: A lazy chunk that fails after boot reloads the page once per build at most, and Try again recovers.
- [ ] AC-10: The ACP parser skips blank lines and delivers a final message without a trailing newline; a refused or limit-stopped turn is shown failed with its reason; "Always allow" with only allow-once offered approves once and does not cancel.
- [ ] AC-11: A failed delegated task returns its child's final report with the error; a Codex turn that auto-compacts ends; status fetch does not write `FETCH_HEAD`, Changes totals do not take `index.lock`, and commit-message drafts write no objects into the repository.
- [ ] AC-12: Storage cleanup keeps a worktree that contains a nested repository or files marked assume-unchanged or skip-worktree with edits; two spellings of one checkout through a symlink count as one.
- [ ] AC-13: A relative Markdown image in a remote thread is read only from that thread's machine; it never falls back to a local file.
- [ ] AC-14: A send interrupted by a socket drop is resent after reconnect with the same command id, twice at most; each attempt the host never answers fails after 60 seconds, and the whole send (attempts plus waits for a reconnect) fails after 2 minutes with an error the composer shows. The first message of a new thread is not resent (D-07).
- [ ] AC-17: Queued runs are ordered by merging delegated completions and user messages by `requestedAt`, each kind keeping its `queuePosition` order, a tie going to the completion; a user's message on a busy coordinator no longer waits behind every delegated completion, and a delegated result that survives a restart-by-stop still runs ahead of the restart message. A dev-server run of a parent with three delegates and a queued message records the observed order in `reports/queue-order-live.md`.
- [ ] AC-15: Every port has a test that fails on the pre-fix code, recorded in `reports/red-green.md`; every PR has green CI and a ship verdict from another model family at its merged head; the fixes are in a release.
- [ ] AC-16: The public repository gains no mention of the upstream project in files, commits, branches or PR text.

## Approach

Same method as 1347: one app worktree, ports written in parallel on an integration branch with one owner per file, PR branches cut from `origin/main` by cherry-pick. A row already fixed in our tree gets its regression test only, with the evidence in `reports/red-green.md`.

PRs: (1) settings, logs and effect slots (R1 to R3), (2) delegate wait and failed-delegate report (R4, R12 part), (3) Codex (R6, R12 part), (4) git and revert (R8, R9, R12 part), (5) storage cleanup (R13), (6) file editor encoding (R7), (7) chunk reload and remote image (R10, R14), (8) send resend and timeout (R15), (9) ACP protocol (R11, plus 1347 AC-08).

Release: after the PRs merge, `bash scripts/release/request-release.sh --by "Port security and data-loss fixes"` in the app repository (the `--by` text becomes the public Actions run title, so it carries no upstream name), then `--released <commit>` to confirm.

Risks: R13 and R15 are medium (our cleanup and connection supervisor are our own designs). R2 changes effect worker scheduling for every thread.

## Review
- Reviewer: meta
- Depth: deep
- Required: yes

## Decisions

### Asked
- D-01 R5 queue order → adopt: "yes, adopt all, do what's recommended" (Anton, November 14, 2026, relayed from the upstream review thread). `QueuedRunOrder.test.ts` pinned inherited behaviour, not a decision of ours, so it is rewritten.
- D-02 Merge and release without asking → yes for this increment (user, November 14, 2026).
### Defaulted (change any before sw-do)
- D-03 A row that needs a design choice our code already made differently is adapted to our design, with the choice recorded here.
- D-07 (November 15, 2026) AC-14 reads as 60 seconds per attempt and 2 minutes for the whole send; the review of PR 436 judged that reading sound and asked for this wording. A new thread's first message goes through the launch path and is not resent, because a repeated launch is not provably idempotent (a root launch on a Scratch project can claim a second folder); a timed-out send retried by hand can still duplicate, since the composer does not keep the ids.
- D-08 (November 15, 2026) AC-03's clause "shutdown still releases the ownership lock" has no test that fails a write mid-run and then checks the lock. It is covered by two things together: `apps/server/src/bin.test.ts` proves the handler is installed on the real output streams of the server entry (so an EPIPE no longer ends the process through an unhandled error), and the existing shutdown tests prove an orderly shutdown releases the lock. The review of PR 431 accepted recording this instead of a new long-running test.
### Open
- none

## Tasks

### T-01 Settings secret kept, log write survives, effect slots bounded
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/serverSettings.ts, repositories/anton-abyzov/specwithcode/apps/server/src/bin.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/EffectWorker.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/serverSettings src/orchestration-v2/EffectWorker

### T-02 Delegate wait returns in time, failed delegate keeps its report
- AC: AC-04, AC-11 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/mcp/OrchestratorMcpService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/SubagentProjection.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/orchestration-v2/SubagentProjection src/mcp

### T-03 Codex initialize timeout, open error code, compaction loop
- AC: AC-05, AC-11 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/CodexAdapterV2.ts, repositories/anton-abyzov/specwithcode/packages/effect-codex-app-server/scripts/generate.ts, repositories/anton-abyzov/specwithcode/packages/effect-codex-app-server/src/_generated/schema.gen.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/orchestration-v2/Adapters/CodexAdapterV2

### T-04 Git: tracking branch on remote switch, full revert, no user locks
- AC: AC-07, AC-08, AC-11 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/vcs/GitVcsDriverCore.ts, repositories/anton-abyzov/specwithcode/apps/server/src/vcs/GitVcsDriver.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/BranchToolbarBranchSelector.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/vcs

### T-05 Storage cleanup keeps nested repositories and hidden edits
- AC: AC-12 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/storageCleanup.ts, repositories/anton-abyzov/specwithcode/apps/server/src/storageCleanup.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/storageCleanup

### T-06 File editor refuses lossy saves and keeps a BOM
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/workspace/WorkspaceFileSystem.ts, repositories/anton-abyzov/specwithcode/apps/server/src/workspace/WorkspaceFileSystem.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/workspace/WorkspaceFileSystem

### T-07 Chunk reload guard keyed by build, remote image stays on its machine
- AC: AC-09, AC-13 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/lib/chunkReloadGuard.ts, repositories/anton-abyzov/specwithcode/apps/web/src/main.tsx, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/state/assets.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/lib/chunkReloadGuard

### T-08 Sends survive a socket drop and time out after 60 seconds
- AC: AC-14 | Files: repositories/anton-abyzov/specwithcode/packages/client-runtime/src/operations/commands.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/rpc/client.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/supervisor.ts | Test: cd repositories/anton-abyzov/specwithcode/packages/client-runtime && npx vp test run src/operations

### T-09 ACP parser, refused turns, allow-once
- AC: AC-10 | Files: repositories/anton-abyzov/specwithcode/packages/effect-acp/src/protocol.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/AcpAdapterV2.ts | Test: cd repositories/anton-abyzov/specwithcode/packages/effect-acp && npx vp test run src/protocol

### T-12 Queue order: completions and messages merged by request time
- AC: AC-17 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/QueuedRunOrder.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/QueuedRunOrder.test.ts, .specweave/increments/1348-upstream-data-loss-and-hang-fixes/reports/queue-order-live.md | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/orchestration-v2/QueuedRunOrder

### T-10 Red-green evidence, reviews, merge and release
- AC: AC-15, AC-16 | Files: .specweave/increments/1348-upstream-data-loss-and-hang-fixes/reports/red-green.md | Test: test -s .specweave/increments/1348-upstream-data-loss-and-hang-fixes/reports/red-green.md

### T-11 Verify and close 1348
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12, AC-13, AC-14, AC-15, AC-16, AC-17 | Files: .specweave/increments/1348-upstream-data-loss-and-hang-fixes/ | Test: specweave verify 1348

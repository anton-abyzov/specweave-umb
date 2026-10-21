# 0980 failure-reporting gap: fix record (October 21, 2026)

Gap seen in the installed 1.0.66 scratch check (providers disabled): four routine runs
failed at provider setup ("This provider instance is disabled.") while the routine card
still showed "Last ran" with lastRunError null. Cause: a run was recorded as succeeded
once its message was dispatched; a later failed turn was never written back.

Fix: anton-abyzov/specwithcode-dev PR #574, squash-merged to main at
ad1ef90bb9980d375093d7096d830c62f6c61dff.
- apps/server/src/scheduledTasks/ScheduledTaskRunReactor.ts: on run.updated with status
  failed, reads the run's user message; when it carries scheduledTaskId, copies the run's
  last error item (or a fallback) to the routine.
- ScheduledTaskService.recordTurnFailure: flips only a succeeded row whose last_run_at is
  not later than the run's requestedAt; waits up to 2 minutes for the dispatch record.

Checks: ScheduledTaskService.turnFailure.test.ts 5 cases; scheduledTasks suite 94/94;
typecheck gate 0 new diagnostics; PR Gate success on fdd2ddced; fresh-context review: no
blocking findings.

Limits (not claimed):
- Not in any release yet (latest tag v1.0.66). Installed behaviour is unverified until the
  release owner ships a build containing ad1ef90bb9.
- No successful provider routine output is proven: providers stayed disabled in scratch.
- Failures emitted while the server is not running, or of requeued/continued runs, are
  not written back.

Verify scope: the 0980 command is the routines/scheduledTasks suite in the app worktree.
The umbrella's configured commands (specweave test:unit:fast, vskill, vskill-platform)
fail in repositories 0980 never touched (timeouts under load: pre-compact.test.ts,
session-start 670 > 300 ms), see reports/verify.md; they are excluded, not weakened.

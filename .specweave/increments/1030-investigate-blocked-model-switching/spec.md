# Investigate blocked model switching

## Problem

On October 23, 2026 at 12:32 PM EDT the worker "Verify Chrome extension pairing and routing" (PR #640, increment 1026, Claude Code Opus 5.5 High, full access) failed two turns in a row. Both were the coordinator's merge approval: run 11, and run 12 from the queue. Each failed in under a second with "Claude is still running background agents or commands, and this model or setting change would end them." Nobody had changed the model. Both runs carry the same selection as run 10 (`claude-opus-5-5`, effort high, thinking on, fastMode off).

Live evidence:

- The background work is real. The thread's `gh pr checks 640 --watch` shell (PID 3289 under zsh 97428) is still running because "PR Gate" is still pending.
- Its Claude CLI process (PID 72464) started at 11:35:47 AM EDT. It has `--add-dir` for `specweave` and attachments only.
- At 11:39:24 AM EDT the project gained the approved folder `specweave-studio` (`project.meta-updated`). PR #634 made such additive folder saves legal while threads run.
- Run 10 was a continuation and reused that process. Run 11 was a new prompt, so the adapter rebuilt its query core key. The new folder changed `queryCoreKey`, and `openQuery` in `apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts` refused to replace a process that runs background work.

Switching to another Claude model cannot help, because every model change also needs a new process and hits the same guard. The error's "model or setting change" wording sent the user hunting for a model problem that did not exist.

## Scope

In: let a Claude thread with live background work keep its process when the only change is newly approved project folders, and name the actual change in the refusal. Out: carrying model changes across a live CLI process; refusing folder removals (they still refuse, since narrowing access cannot wait); other providers; queueing a refused turn until background work ends.

## Acceptance Criteria

- [x] AC-01: With a background shell running, a turn whose only difference is an added project folder reuses the live Claude process and is delivered. The next turn after the background work ends opens a new process that has the folder.
- [x] AC-02: With a background shell running, a turn whose project folders lose an entry is still refused with `ClaudeBackgroundWorkBlocksQueryReplacementError`. So is a turn with a changed model or permission. Nothing is closed in either case.
- [x] AC-03: The refusal names what changed: a model change says "model change", and a folder or permission change says "folder or permission change", and both say "model, folder or permission change". It still tells the user to wait or press Stop.
- [x] AC-04: The live thread recovers without losing the running watcher. Its owner is told the cause and how to resume. PR #640 is not merged or released by this work.

## Approach

`ClaudeAdapterV2.ts` `openQuery`: record the opened process's project folders and a core key without them (`queryCoreBaseKey`) on `ClaudeLiveQueryContext`. In the background-work branch, reuse the process when the base key and selection match and the new folders are a superset of the opened ones. Log `claude.query.folder-grant-deferred`. Any other difference refuses, as before. `ClaudeBackgroundWorkBlocksQueryReplacementError` gets a `change: "model" | "settings"` field that selects the wording.

Rejected: restarting the process with the new folders, which kills the user's background work (the guard's whole point); applying the folders to the running process, since the adapter's SDK session exposes only `setModel`, `setPermissionMode`, `interrupt` and MCP reconnect.

Risk: until the background work ends, the process lacks the new folder. A widening only, so access never exceeds the grant.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Defer added folders rather than auto-restart (preserves running work).
- D-02: Live recovery is left to the thread owner and coordinator. This lane does not merge PR #640.
### Open
- none

## Tasks

### T-01 Defer added folders while background work runs
- AC: AC-01, AC-02, AC-03 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/bgwork-added-folders/apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/bgwork-added-folders/apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.test.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/bgwork-added-folders/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/orchestration-v2/Adapters/ClaudeAdapterV2.test.ts -t "background"

### T-02 Live recovery and owner notice
- AC: AC-04 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/bgwork-model-switch-20261023/report.md | Test: report.md records the watcher PID still alive, the owner notice, and the thread's next turn outcome

### T-03 Verify and close 1030
- AC: AC-01, AC-02, AC-03, AC-04 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/bgwork-model-switch-20261023/report.md | Test: specweave verify 1030-investigate-blocked-model-switching

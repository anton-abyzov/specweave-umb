# Investigate thread-not-found delivery failures

## Problem

On October 23, 2026 at 14:41 UTC the EasyChamp worker "DCFC dues proration + suspensions" could not deliver its hold-renewal acknowledgement to the audit owner "Complete EasyChamp handoff audit" and asked the user for the exact thread ID. The coordinator's notice ended with "Audit owner thread:delegated-task:command%3Amcp%3Ad25698a7-…%3Adelegate-task%3Aeasychamp-full-handoff-audit-20261022." The worker read `thread:` as a label and called `studio_thread_send` three times without it: the encoded ID, the decoded ID, and the bare command ID `mcp:d25698a7-…`. Each returned only `thread_not_found: Thread <id> was not found.` The audit thread existed the whole time (not archived, running on the M4, same project, same machine, full-access), and six other workers that kept the prefix delivered their acknowledgements to it within the same minute. So the cause was a malformed ID (a dropped prefix), not a stale, deleted, migrated or remote thread, a permission refusal or a discovery gap. The product defect is that the error gave the agent no way to recover: it names neither the thread it probably meant nor how to find it, so a recoverable typo became a user blocker.

## Scope

In: a near-miss suggestion in `thread_not_found` from the thread tools routed through `routeThread` (`studio_thread_read`, `studio_thread_send`, `studio_thread_wait`, `studio_thread_interrupt`), with a pure candidate generator in `packages/shared`. Out: silently acting on a guessed thread (access checks must see the thread the tool acts on), `studio_thread_update` and queue tools (they report not-found through other paths), rewriting thread IDs inside message text, prompt or tool-description changes, the one-time delivery recovery itself (done operationally, see Evidence).

## Acceptance Criteria

- [ ] AC-01: `studio_thread_send` / `studio_thread_read` given a thread ID missing its leading `thread:`, or a decoded delegated-task ID with or without the prefix, still fails with `thread_not_found` and its message names the existing thread (`Did you mean <exact id>?`).
- [ ] AC-02: The tool acts only on the ID it was given: nothing is sent to, read from or checked against a suggested thread, and work started from another machine under a work grant gets no suggestion.
- [ ] AC-03: When no near miss exists (for example a bare command ID `mcp:<uuid>`), the message tells the agent the ID is opaque and to find it with `studio_thread_search` or `studio_thread_list`.
- [ ] AC-04: The installed app shows the suggestion: on the first release containing the fix, a send to the prefix-less audit-style ID returns `Did you mean thread:…?`.

## Approach

`packages/shared/src/studioThreadLinks.ts` gains `threadIdNearMisses`: restore `thread:`, re-encode a delegated task's command ID (`thread:delegated-task:` + `encodeURIComponent(commandId)`, as `IdAllocator.deriveDelegatedTaskThread` builds it), strip quoting and trailing sentence punctuation. `apps/server/src/mcp/threadNotFoundHint.ts` looks the candidates up through `ThreadManagementService.getThreadShell` (existing, not deleted) and rewrites the failure message. `routeThread` in `apps/server/src/mcp/toolkits/orchestrator/remote.ts` applies it to local `thread_not_found` failures only.

Rejected: resolving the near miss silently. `McpToolAccess.writesThreads` checks modes on the ID passed (and skips a thread that does not exist) before the handler runs, so acting on a different ID would bypass that check.

Risk: a suggestion reveals that a near-miss thread ID exists. Local callers can already list and search every thread here; callers under a remote work grant get no suggestion.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Suggest, never retarget (security above convenience; one extra agent call).
- D-02: Only the four routed thread tools in this increment; other not-found paths later if they recur.
### Open
- none

## Tasks

### T-01 Near-miss thread ID candidates
- AC: AC-01, AC-03 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/thread-ref-not-found/packages/shared/src/studioThreadLinks.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/thread-ref-not-found/packages/shared/src/studioThreadLinks.test.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/thread-ref-not-found/packages/shared && node ../../node_modules/vite-plus/bin/vp test run src/studioThreadLinks.test.ts

### T-02 Actionable thread_not_found in routed thread tools
- AC: AC-01, AC-02, AC-03 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/thread-ref-not-found/apps/server/src/mcp/threadNotFoundHint.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/thread-ref-not-found/apps/server/src/mcp/toolkits/orchestrator/remote.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/thread-ref-not-found/apps/server/src/mcp/toolkits/orchestrator/remote.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/thread-ref-not-found/apps/server/src/mcp/threadNotFoundHint.test.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/thread-ref-not-found/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/mcp/toolkits/orchestrator/remote.test.ts src/mcp/threadNotFoundHint.test.ts

### T-03 Installed acceptance after release
- AC: AC-04 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/thread-not-found-20261023/report.md | Test: on the released app, studio_thread_send to the audit thread ID without `thread:` returns "Did you mean"

### T-04 Verify and close 1027
- AC: AC-01, AC-02, AC-03, AC-04 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/thread-not-found-20261023/report.md | Test: specweave verify 1027-investigate-thread-not-found-delivery-failures

## Evidence

Full trace, failed requests and recovery receipt: `/Users/antonabyzov/.specwithcode/m4/evidence/thread-not-found-20261023/report.md`.

# Start a fresh Claude session when the native one is gone

## Problem

On October 25, 2026, the thread "Shrink pre-update backup" failed every turn with "No conversation found with session ID: 8c0f8c57-6f48-464d-b936-6a0f5052188b". The transcript was never written; it was not pruned.

The October 23 "native session full" fallback minted the new id `8c0f8c57`. The only run on it was a 4 ms background-command notification wake (run 22). That wake never reached the CLI, but it was recorded as an accepted native turn, so the next turns resumed a session that never existed. Claude Code also prunes old transcripts, and a person can delete them, with the same effect.

Turn start already falls back to a fresh native session with a `full_thread_summary` handoff when `resumeThread` fails. Claude's `resumeThread` never failed, though. Inside a live provider session, a loaded thread is not even resumed. The CLI reports the missing session only after the query opens with `resume`, so every retry resumed the same missing id.

## Scope

In: Claude checks that the native transcript exists before a resume, both on a cold resume and for a thread the session already loaded. When it is gone, the check fails into the existing fallback. A "No conversation found" answer makes this process check again. Out: transcript recovery, other drivers, and not counting a wake that never reached the CLI as a native turn (follow-up F2).

## Acceptance Criteria

- [ ] AC-01: When the native session has taken an accepted turn (or has a conversation head), this live session has not opened it, the Claude home names a readable `projects` folder, and no `projects/*/<session id>.jsonl` exists, then `resumeThread` fails with `ProviderAdapterResumeThreadError` and logs `claude.native-session.missing`.
- [ ] AC-02: The turn then starts a fresh native session with the thread's history as a `provider_resume_fallback` handoff, using the existing path. It never resumes the missing id again, including inside a live provider session: a loaded thread whose native session took a turn goes through `verifyNativeThread`, and a "No conversation found" answer drops the id from the process's opened set.
- [ ] AC-03: All of these resume as before:
  - a transcript under any project folder;
  - a native session without an accepted turn;
  - a session this process opened;
  - a home with no `projects` folder, or one that cannot be listed;
  - a HOME the CLI would not use;
  - an environment that names no Claude home.
- [ ] AC-04: Turn start passes `nativeThreadHasTurns` to `resumeThread`, true only for an accepted attempt whose recorded native id is the provider thread's current one.
- [ ] AC-05: Focused tests pass (including a mutation check), the typecheck is clean for changed files, a fresh exact-head review returns SHIP, and CI is green. The merge owner merges it into 1.0.86.

## Approach

- `apps/server/src/orchestration-v2/ProviderAdapter.ts`: `resumeThread` input gains optional `nativeThreadHasTurns`.
- `apps/server/src/orchestration-v2/ProviderTurnStartService.ts`: `nativeSessionHasAcceptedTurn(projection, providerThread)` feeds it.
- `apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts`: `requireNativeTranscript` runs at the start of `resumeThread`. The home is `CLAUDE_CONFIG_DIR`, else `$HOME/.claude`, taken from the instance environment. The lookup reuses `findClaudeTranscript`.
- `apps/server/src/provider/Drivers/ClaudeTranscriptTransfer.ts`: exports `isClaudeSessionId`.

Rejected: classifying the CLI's "No conversation found" text at query time. The turn has already started by then, so the fallback cannot run without restructuring the 9,000-line adapter.

Risk: a false "missing" costs one fresh session plus a summary handoff instead of a full resume. To keep that rare, the check requires an accepted turn on the current native id. It fails open on any unreadable home or listing. It checks the cwd folder first and scans the others only on a miss.

Follow-up (review F2): a wake turn that never reaches the CLI should not record an accepted native turn. Until then, such a wake costs one extra summary on the next turn instead of a dead thread.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Search every project folder, not only the cwd slug → avoids false "missing" after a folder move (reversible).
### Open
- none

## Tasks

### T-01 Check the native transcript before a Claude resume
- AC: AC-01, AC-02, AC-03, AC-04 | Files: apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts, apps/server/src/orchestration-v2/ProviderTurnStartService.ts, apps/server/src/orchestration-v2/ProviderAdapter.ts | Test: `npx vp test run src/orchestration-v2/Adapters/ClaudeAdapterV2.test.ts -t "native session identity"` and `src/orchestration-v2/ProviderTurnStartService.test.ts` in apps/server

### T-02 Review, PR and CI
- AC: AC-05 | Files: PR on anton-abyzov/specwithcode-dev | Test: fresh exact-head review SHIP, CI green

### T-03 Verify and close 1076
- AC: AC-05 | Files: reports/ | Test: `specweave verify 1076-start-a-fresh-claude-session-when-the-native-one-is-gone`

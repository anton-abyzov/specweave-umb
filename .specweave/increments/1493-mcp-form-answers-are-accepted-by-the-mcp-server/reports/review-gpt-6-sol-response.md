# Response to GPT-6 Sol review of f4f458ec3

Fixed in app commit `e2402a5f0`.

**[high] Failed commit after Stop leaves the card pending: fixed.** On the "answer never arrived" path, the adapter now calls `beginClosingClaudeForm` again. If the commit failed during the wait, `forgetUncommittedFormAnswer` has already dropped the mark, so the card is closed and marked closing. A recorded answer keeps 1481 D-11.

Test: "closes the card when the answer's commit failed during the wait (1493)" in `apps/server/src/provider/ClaudeMcpElicitation.test.ts`.

**[high] A zoned default changes instant on Submit: fixed.**

- A default the person leaves as shown is sent exactly as the server gave it. That keeps both the offset and any fraction.
- An edited local time is written from the `Date` it makes: the earlier offset for a repeated hour, and the time it became for a skipped hour. The time and the offset always name the same instant.

Tests: "across a clock change (1493)" in `packages/shared/src/mcpElicitationDateTime.test.ts`, which sets `TZ` to America/New_York.

**[medium] Lint and format: lint not new; format fixed before push.**

- Lint: origin/main's `ClaudeMcpElicitation.test.ts` already has the same 12 `Effect.runPromise` calls, and this PR adds none (`git diff origin/main` shows 0 added). The whole file uses that 1481 pattern, and PR #929's gate passed with it.
- Format: the evidence came from `reports/gates.txt`, which was captured before formatting. `vp fmt --check` on all 13 touched files is clean at `e2402a5f0`.

Checks at `e2402a5f0` (`reports/gates-e2402a5f0.txt`):

- Focused tests: 69 of 69 pass.
- 37 of 37 pass in each of five time zones: Asia/Kolkata, America/St_Johns, Pacific/Chatham, UTC and America/New_York.
- Typecheck gate: "0 new diagnostics, passed".

# Response to round 3 (e2402a5f0, NO-SHIP)

**[high] A commit failure after grace still leaves a dead card pending: fixed in `9fb13b986`.**

When grace ends with the answer's commit still running, the adapter now calls `closeClaudeFormNowOrOnFailedCommit`, a single synchronous registry step. It closes the card at once if the commit already failed. Otherwise it keeps a closer, which outlives the call.

If that commit fails later, `forgetUncommittedFormAnswer` does two things in the same step: it marks the form closing, so any Submit queued behind the commit is refused, and it runs the closer, which emits the cancelled card. A commit that succeeds keeps 1481 D-11: the closer never runs.

Test: "closes the card when the answer's commit fails after the call ended (1493)".

Checks at `9fb13b986` (`reports/gates-9fb13b986.txt`):

- Focused tests: 70 of 70 pass.
- 37 of 37 pass in each of five time zones.
- `vp fmt --check` is clean.
- Typecheck gate: "0 new diagnostics, passed".

# Response to round 4 (9fb13b986, NO-SHIP)

**[high] The late-failure closer can fire after the stopped run's event stream has ended: fixed in `be39567bf`, by a different design.**

The closer is gone. When the grace ends and the answer's commit is still running, the call now waits for that commit's outcome before it ends:

- `markClaudeFormAnswerCommitted` (one orchestrator hook after an accepted commit) reports success.
- `forgetUncommittedFormAnswer` (on failure or a rejected receipt) reports failure. It also marks the form closing first, so a Submit queued behind the commit is refused.

On failure, the call closes the card itself with `closeCard`. That is the same stream, still owned by the live call, that the existing Stop and timer closes use. On success, the record is left as it is (1481 D-11). Nothing outlives the call, so there is no eviction or stale closer.

Tests:

- "waits past the grace for a commit still running, and closes the card if it fails (1493)"
- "leaves the record alone when a commit still running past the grace succeeds (1493)"
- The orchestrator test checks that a real commit reports "committed".

`Orchestrator.ts` now has 12 hook lines.

Checks at `be39567bf` (`reports/gates-be39567bf.txt`):

- Focused tests: 71 of 71 pass.
- 37 of 37 pass in each of five time zones.
- `vp fmt --check` is clean.
- Typecheck gate: "0 new diagnostics, passed".

# Response to round 5 (be39567bf, NO-SHIP)

**[high] A planning failure leaves the form call waiting forever: fixed.**

The three commit-path hooks are gone. The respond dispatch is now wrapped at its call site with `Effect.onExit`, which calls `ClaudeForms.settleFormAnswerDispatch(command, Exit.isSuccess(exit))`. Any exit settles the hand-off: success, a planning failure, a rejected receipt, a defect or an interruption. The adapter's wait is also capped (`commitOutcomeLimit`, 2 minutes); if the cap is reached, the card is left as the record says.

Tests:

- "settles a hand-off however its dispatch ends (1493)"
- "ends a call whose commit never settles, leaving the card as the record says (1493)"
- The successful-respond test shows the hook is wired.

**[high, plausible] Stopped-run ingestion closes while the call waits: confirmed, and fixed durably.**

I traced it: nothing in the orchestrator cancelled a pending `mcp-elicitation` request after Stop with a live session, and the adapter's late event is dropped once the run's subscription ends. This is also true of 1481's own Stop path.

A provider turn's end already cancels its pending native questions through the ingestor's own events (`dismissNativeUserInputs`, `getPendingNativeUserInputs`). That sweep now covers Claude forms and their `approval_request` cards too (`isDismissedAtTurnEnd` and `isDismissedTurnEndCard` in `ClaudeFormResponses.ts`; 8 changed lines in `ProjectionStore.ts`). A form already answered is not pending, so it is never swept (1481 D-11). The race between an answer and the sweep is covered by the existing test "preserves an answer committed after terminal normalization reads a pending question".

Test: "dismisses only native questions and Claude forms when a provider turn ends with %s" in `ProviderEventIngestor.test.ts`, for all five terminals. It covers a pending Claude form (cancelled), an answered Claude form (kept) and a Codex elicitation (kept).

Checks at `44abc282e` (`reports/gates-44abc282e.txt`):

- Focused tests: 10 files, 120 tests, all pass. The set adds `ProviderEventIngestor`, `ProviderTurnControlService`, `Orchestrator.questionAnswers` and `ProjectionControlReads`.
- 37 of 37 pass in each of five time zones.
- `vp fmt --check` is clean.
- Typecheck gate: "0 new diagnostics, passed".

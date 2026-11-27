# Review: 1493 MCP form answers are accepted by the MCP server
Verdict: fix first
Reviewed commit: f4f458ec3f302023dd61861099e7a1a8a65a26cc
Reviewer context: fresh Codex session, GPT-6-Sol

## [high] apps/server/src/provider/ClaudeMcpElicitation.ts:357 failed commit after Stop leaves the card pending
Submit sets the in-memory answered mark, then Stop sees it and enters the two-minute grace. If `commitCommand` fails or returns a rejected receipt, `forgetUncommittedFormAnswer` clears the mark, but `committed` remains true. At grace expiry, lines 379-386 return without `closeCard`; the card stays pending with no live adapter and a later Submit can be recorded as resolved. Recheck the mark after grace or notify the adapter of commit failure, then close the card when no answer was committed. Add a test with Stop between hand-off and failed commit.

## [high] packages/shared/src/mcpElicitationDateTime.ts:75 a zoned default can change instant on Submit
In `America/New_York`, `2026-11-01T01:30:00-05:00` displays as `2026-11-01T01:30`, then the local `Date` constructor selects `-04:00`; unchanged Submit sends an instant 60 minutes earlier. Lines 89-92 also drop fractional seconds from a default. Preserve the original zoned value while untouched, and handle ambiguous or nonexistent local times when edited. The DST case was reproduced in the required checks copy.

## [medium] apps/server/src/provider/ClaudeMcpElicitation.test.ts:411 new tests fail the lint gate
The new `Effect.runPromise` calls at lines 411 and 436 trigger `studio(no-manual-effect-runtime-in-tests)`. The gate report also shows format failures in `packages/shared/src/mcpElicitationDateTime.ts` and `packages/shared/src/mcpElicitationForm.test.ts`; a focused lint and format check reproduced them. Convert the tests to `it.effect(...)` and format the touched files before shipping.

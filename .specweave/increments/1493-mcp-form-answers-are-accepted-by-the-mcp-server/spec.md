# 1493 MCP form answers are accepted by the MCP server

## Problem

1481 shipped MCP form-mode questions in Claude threads (PR #929, `c283af4da`). A review of `76401dac4` ("fix before merge: 1 high, 4 medium, 3 low") was never recorded in 1481, and every finding still holds on main `d08bb72c4`.

The high one: a `date-time` field is drawn as `<input type="datetime-local">`, which gives `2026-11-25T10:00`. Our validator accepts it, and the MCP SDK 1.32.2 validator that `Server.elicitInput` runs rejects it (`data/at must match format "date-time"`, measured), so the server's tool call fails. The SDK also rejects February 30 and `24:00:00`, which `Date.parse` accepts.

The rest:

- The secret check skips number fields, so a PIN form is shown.
- Joined acronyms (`PINCode`, `APIToken`) are not split.
- A Submit just after Stop or the timer is acknowledged, then overwritten as cancelled.
- Formatted strings are checked trimmed but sent untrimmed.
- An optional multi-select with `minItems` can't be left empty.
- A failed commit leaves a card open with no call behind it.
- A zoned date-time default is hidden but still sent.
- No test pins that the stored effect carries only redacted answers.

## Scope

In: `packages/shared` form validation, the web form card, the Claude adapter's close path, the form hand-off registry, tests.

Out: phone and coordinator cards (1481 D-06), Codex elicitations, URL mode.

## Acceptance Criteria

- [ ] AC-01: A `date-time` answer from the card reaches the server as RFC 3339 with seconds and the local offset, and the MCP SDK 1.32.2 validator accepts it. A value without seconds or a zone, an impossible date, or an out-of-range time is refused with "Enter a date and time."
- [ ] AC-02: A date-time default with a zone shows in the card as the same instant in local time. A default the card can't show is not sent.
- [ ] AC-03: A form with a number or integer field named as a secret (`pin`, `PINCode`, `otp`, `APIToken`, `cvv`) is declined, like a text field. Select and boolean fields, whose values the server lists itself, are not refused for their name.
- [ ] AC-04: A string with a format is sent trimmed, and the SDK validator accepts it.
- [ ] AC-05: An optional multi-select with `minItems` left empty is left out of the content, with no error.
- [ ] AC-06: Once the adapter starts closing a card after Stop or the timer, an answer to it is refused with "This form was closed." and never recorded as resolved. An answer the app recorded first is passed on, as before.
- [ ] AC-07: When the commit of an answer fails or is rejected, its answered mark and hand-off are dropped, so a later Stop or the timer closes the card instead of leaving it pending with no call behind it. A committed answer that never arrives keeps 1481 D-11: the record is not overwritten.
- [ ] AC-08: A test fails if the committed `runtime-request.respond` effect carries raw answers.

## Approach

- **AC-01, AC-02:** new module `packages/shared/src/mcpElicitationDateTime.ts`:
  - `isRfc3339DateTime(value)`: a regex no looser than ajv-formats' full `date-time` (seconds and zone required, `T`/`Z` in either case, offset `±HH:MM`), plus day-of-month, hour, minute and second range checks.
  - `localInputToRfc3339(local, offsetMinutes?)`: `YYYY-MM-DDTHH:mm[:ss]` read as local time, returned with its offset.
  - `rfc3339ToLocalInput(value)`: the reverse, for defaults. Returns undefined when the value is unparseable.

  `mcpElicitationForm.ts` uses `isRfc3339DateTime` in `formatError`. The web card maps date-time defaults through `rfc3339ToLocalInput` (dropping unshowable ones) and values through `localInputToRfc3339` before `validateMcpElicitationContent`.
- **AC-03:** `findMcpElicitationSecretField` checks `text` and `number` fields, and `namesSecret` splits `([A-Z]+)([A-Z][a-z])` before the camelCase split.
- **AC-04, AC-05:** `checkField` returns the trimmed string when a format applies and checks lengths on it. An optional multi-select with nothing chosen returns `{}` before the `minItems` check.
- **AC-06, AC-07:** `ClaudeFormResponses.ts` gains a bounded `closing` set, plus `beginClosingClaudeForm(id)`. That function returns false when an answer was already recorded; otherwise it marks the form as closing.
  - `handOffClaudeFormAnswers` returns false for a closing form, and the orchestrator's existing hand-off line refuses the command with `FORM_CLOSED`. That takes 6 hook lines in `Orchestrator.ts`, over 1,500 lines.
  - `checkFormResponse` refuses a closing form before validating.
  - Both calls are synchronous, so whichever runs first wins.
  - The adapter calls `beginClosingClaudeForm` where it used to read `isClaudeFormAnswered`.
  - `forgetUncommittedFormAnswer(command)` drops the mark and hand-off when `commitCommand` fails (`tapError`) or returns a rejected receipt. That is 3 more hook lines in `Orchestrator.ts`, 10 in total.
  - The closing mark outlives the call (it is bounded at 200 like `closed`), so a Submit between the call ending and the cancelled update landing is still refused.
- **AC-08:** `Orchestrator.claudeForms.test.ts` asserts that the committed effect's `answers` equals `{ confirm: "[redacted]" }`.

Rejected:

- Moving the answered mark after `commitCommand`: the adapter must see it before the effect worker delivers the answer, and the commit is where the effect is queued.
- Closing the card on every undelivered path: that overwrites a committed record as cancelled, which reverses 1481 D-11.

## Decisions

### Asked

- none

### Defaulted (change any before sw-do)

- D-01 Secret check covers text and number fields only, not select, multi-select or boolean. Their values come from the server's own list, so the person can't type a secret into them (reversible).
- D-02 The card sends a date-time in the browser's local offset (`2026-11-25T10:00:00-08:00`), not UTC, so the server sees the time the person picked (reversible).
- D-03 A date-time default the card can't show is dropped, not sent unseen (reversible).
- D-04 A committed answer that never reaches the adapter keeps 1481 D-11: the card is not closed over the record. Only an answer whose commit failed or was rejected is forgotten (reversible).

### Open

- none

## Tasks

### T-01 Date-time, secret, trim and multi-select validation

- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/mcpElicitationDateTime.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/mcpElicitationDateTime.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/mcpElicitationForm.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/mcpElicitationForm.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/package.json, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/McpElicitationForm.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/McpElicitationForm.test.tsx, repositories/anton-abyzov/specwithcode/apps/server/src/provider/McpElicitationSdkValidator.test.ts | Test: node node_modules/vite-plus/bin/vp test run packages/shared/src/mcpElicitationDateTime.test.ts packages/shared/src/mcpElicitationForm.test.ts apps/web/src/components/chat/McpElicitationForm.test.tsx apps/server/src/provider/McpElicitationSdkValidator.test.ts

### T-02 Closing race and undelivered answers

- AC: AC-06, AC-07, AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ClaudeFormResponses.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Orchestrator.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Orchestrator.claudeForms.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/ClaudeMcpElicitation.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/ClaudeMcpElicitation.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/provider/ClaudeMcpElicitation.test.ts apps/server/src/orchestration-v2/Orchestrator.claudeForms.test.ts

Verify and close 1493.

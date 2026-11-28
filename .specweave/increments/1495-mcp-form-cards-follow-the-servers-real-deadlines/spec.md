# 1495 MCP form cards follow the server's real deadlines

## Problem

1481 and 1493 put MCP form questions on a card in Claude threads (released in v1.0.443 and v1.0.447). The Fable 5.2 review of the MCP plan (lead thread, November 27, 2026, notes in `/Users/anton/.specwithcode/m4/scratch/2026-11-24-mcp-video/research/08-fable-review.md`) found three gaps:

- **Probe coverage.** The only live probe server was legacy-only: SDK 1.32.2, which answers `server/discover` with `-32601`. Real servers ask differently:
  - GitHub's `delete_repository` asks through the 2026-07-28 `input_required` result.
  - Tasks ask through `tasks/update`.
  - URL requests use error `-32042`.

  Nobody has checked what reaches the card from these. Nobody has checked whether Tasks are on for the Agent SDK entrypoint either (the app ships `@anthropic-ai/claude-agent-sdk` `^0.3.276`).
- **Deadlines.** `UNATTENDED_MCP_ELICITATION_TIMEOUT_MS` is 30 minutes (`apps/server/src/provider/ClaudeMcpElicitation.ts:75`). Real deadlines are shorter:
  - GitHub's sealed `requestState` lasts 10 minutes.
  - HTTP MCP calls idle out at 5 minutes.
  - Claude Code's hook timeout is 10 minutes.

  When the SDK aborts the request, the card closes (`by: "stop"`), but no notice tells the person that the server stopped waiting.
- **URL-decline notices.** Claude Code advertises URL mode and retries `-32042` up to 3 times. The notice is keyed per request (`${nativeRequestId}:notice`), so one tool call can show three notices.

## Scope

In: a scratch probe server (outside every repository) on the current MCP SDK, the Claude adapter's form path, its notices and timeout, tests, and a probe report.

Out: opening links for URL mode (a separate owner decision), Codex and Copilot forms, studio-code on protocol 2026-07-28.

## Acceptance Criteria

- [ ] AC-01: A probe report records what reaches a Claude thread's card from a server on the current MCP SDK: an `input_required` form, a task's `tasks/update` question, and a `-32042` URL request. It states whether Tasks are on for the Agent SDK entrypoint the app ships.
- [ ] AC-02: When the SDK stops waiting for a form (its abort signal fires) and no answer is recorded, the card closes and the thread shows "`<server>` stopped waiting for an answer." A recorded answer keeps 1481 D-11.
- [ ] AC-03: The probe report records whether answering a form over HTTP works at 6 and at 11 minutes. The unattended timeout is no longer than the shortest real deadline that nothing signals (a signalled one closes the card through the SDK's abort, AC-02), and the spec says which deadline set it. On that timeout the server gets `cancel`.
- [ ] AC-04: One tool call that retries a URL request shows one URL-decline notice, not one per retry.

## Approach

- **AC-01, AC-03 probe:** use a scratch folder at `/Users/anton/.specwithcode/m4/scratch/2026-11-27-1495/probe/`, holding the current `@modelcontextprotocol/sdk` server with stdio and Streamable HTTP transports. It has three tools:
  - one asks through `input_required`;
  - one is a task that asks through `tasks/update`;
  - one returns `-32042`.

  It runs headless through the Claude Code CLI bundled with the Agent SDK bump (thread "Claude Agent SDK on a current Claude Code for MCP features"). T-01 starts on that bump's merge, or rebases onto it if it lands first. The installed Claude Code 2.1.331 is the comparison. It records the SDK messages, what the card shows, and the answers at 6 and 11 minutes over HTTP. Report: `reports/probe.md`.
- **AC-02:** in `ClaudeMcpElicitation.ts`, when the call ends with `by: "stop"` and the turn is not stopping, the adapter shows a new `stoppedWaitingNotice`. Telling an SDK abort apart from the person's Stop comes from the turn's own state.
- **AC-03:** set `UNATTENDED_MCP_ELICITATION_TIMEOUT_MS` to the shortest deadline the probe measures (expected 5 minutes, from the HTTP idle timeout), and update `unattendedTimeoutNotice` to match. Measured (D-03): 5 minutes, set by Claude Code's HTTP stream drop after about 356 s without keepalives.
- **AC-04:** key the URL-decline notice by the tool call (the SDK's tool use id if the elicitation carries it, otherwise the single running `mcp__<server>__*` call), so retries replace one notice. Measured (D-05): with no single such call, the request keys itself.

## Decisions

### Asked

- none

### Defaulted (change any before sw-do)

- D-01 This is a new increment, not tasks added to 1493. 1493 is merged, released and strictly verified (reversible).
- D-02 The unattended timeout follows the shortest measured deadline. An attended card has no timer of its own and closes when the SDK stops waiting (reversible).
- D-03 The deadline that sets the unattended timeout is the shortest one no server signals: Claude Code drops an HTTP call's stream after about 356 s without keepalives (`reports/probe.md`). The MCP TypeScript SDK's 60 s request timeout is shorter, but the server signals it, the SDK aborts, and the card closes with the stopped-waiting notice. A modern server's `requestState` (10 minutes at GitHub) is longer. Timeout: 5 minutes (reversible).

- D-04 An SDK abort is read as the server giving up unless the adapter marked the form's call as ended by the app (adversarial review rounds 1 and 2, November 28). The SDK's abort reason is always a bare `AbortError` (`reports/probe.md`), so the app records the cause itself. Stop and steer mark the forms open at that moment before they interrupt; every close of the CLI and the end of its output mark them too. An abort with no mark within 2 s shows the stopped-waiting note: a CLI crash ends the output about 2 ms after the abort. A turn that finishes on its own shows a pending note before its end. A failed commit after the server gave up shows the stopped-waiting note, because nothing was recorded (reversible).
- D-05 The URL note's tool-call match uses Claude Code 2.1.332's tool-name form of the server name, which also folds runs of `_` in `claude.ai` names. With two calls of the server running at once, the note is keyed by the request, so neither call's note replaces the other's (reversible).

### Open

- none

## Tasks

### T-01 Probe a current MCP server

- AC: AC-01, AC-03 | Files: .specweave/increments/1495-mcp-form-cards-follow-the-servers-real-deadlines/reports/probe.md | Test: grep -q "Tasks on the SDK entrypoint" .specweave/increments/1495-mcp-form-cards-follow-the-servers-real-deadlines/reports/probe.md

### T-02 Stopped-waiting notice, real timeout, one URL notice per call

- AC: AC-02, AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/provider/ClaudeMcpElicitation.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/ClaudeMcpElicitation.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/provider/ClaudeMcpElicitation.test.ts

### T-03 The adapter tells the module when the turn is stopping

- AC: AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.elicitation.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.elicitation.test.ts

Verify and close 1495.

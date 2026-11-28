# 1498 MCP servers can ask you to open a link in Claude threads

## Problem

MCP servers can ask the person to open a page, a URL-mode elicitation: a sign-in, an API-key page or a payment confirmation. Claude Code advertises URL mode, and servers use it directly or through error `-32042` (URL elicitation required). Claude Code retries that error up to 3 times. Today the Claude adapter declines every URL request with a notice (`apps/server/src/provider/ClaudeMcpElicitation.ts:293`, `urlModeNotice`). The server's tool call then fails, and the person never sees the page.

The owner approved URL mode for Claude threads first on November 26, 2026, answering the lead's decision card "URL mode: Yes, Claude threads first".

## Scope

In:
- the Claude adapter's URL path;
- a URL card in the web thread view;
- the open-link action through the existing `openExternal` bridge (`apps/web/src/localApi.ts`);
- lookalike and Punycode detection;
- one card per tool call across `-32042` retries;
- tests;
- a headless screenshot of the card.

Out:
- Codex and Copilot URL mode (they follow later);
- phone and coordinator cards (as in 1481 D-06);
- form-mode changes, which 1495 owns.

## Acceptance Criteria

- [ ] AC-01: A URL request in a Claude thread shows a card with:
  - the server name and its message;
  - the full URL, with the registrable domain highlighted;
  - the buttons Open link, I'm done, continue, Decline and Cancel.
- [ ] AC-02: The link opens in the system browser only when the person presses Open link. Nothing opens it automatically, not even when the card appears, or for an agent's answer, in Full access, or from an automatic responder.
- [ ] AC-03: A URL whose host has Punycode (`xn--`), mixes scripts, or is not `https` (other than `http://localhost`) shows a warning on the card. A URL that is not `http` or `https`, or that has user info (`user@host`), is declined with a notice and gets no card.
- [ ] AC-04:
  - "I'm done, continue" sends `accept`, Decline sends `decline`, and Cancel sends `cancel`.
  - An agent's answer is refused, and so is any answer in an unattended turn without a person.
  - An unattended turn declines the request with a notice.
  - Stop and the SDK's abort close the card, as in 1481 and 1495.
- [ ] AC-05: A tool call that retries `-32042` up to 3 times shows one card. A retry after the person answered gets that answer and no new card.
- [ ] AC-06: The URL path never reads, adds or sends a SpecWithCode sign-in, a Connect token or any credential. The open-link action passes only the server's URL to the system browser, unchanged.
- [ ] AC-07: A headless screenshot of the URL card, including the lookalike warning, is saved in `reports/`.

## Approach

- New module `apps/server/src/provider/ClaudeMcpUrlElicitation.ts`. It validates the URL (scheme, user info, Punycode and mixed scripts) and builds the card's request, node and item. It shares the closing gate in `ClaudeFormResponses.ts` and the turn-end sweep from 1493. `ClaudeMcpElicitation.ts` gets hook lines only.
- The registrable domain and the lookalike check go in a new shared module, `packages/shared/src/mcpElicitationUrl.ts`, which uses `URL` and `domainToUnicode`.
- The web card is a new `apps/web/src/components/chat/McpElicitationUrlCard.tsx`. Open link calls the existing `openExternal` with the URL string exactly as the server sent it.
- `checkFormResponse` in the orchestrator path gains a URL branch: only a person's `accept`, `decline` or `cancel` counts, with no answers. It refuses an agent's answer and anything in an unattended turn.
- Retries: the card is keyed by the tool call (the SDK's tool use id, or the server plus turn when there is none). The same key also drives 1495's one-notice rule.

Rejected:

- Opening the link from the server process: a link must open only on the person's press, in their own browser.
- Showing a shortened URL: the person must see exactly where it goes.

## Decisions

### Asked

- D-01 Allow URL mode? → Yes, Claude threads first (owner, November 26, 2026, on the lead's card).

### Defaulted (change any before sw-do)

- D-02 An unattended turn declines a URL request with a notice, and the card waits for no one (reversible).
- D-03 A plain `http` URL that is not localhost shows a warning but can still be opened (reversible).
- D-04 This increment starts after 1495, which owns the same adapter file (reversible).

### Open

- none

## Review

- Reviewer: GPT-6.2 Sol (Codex) on m4, four rounds, last verdict ship at `cb9ec6724`, its two remaining should-fixes fixed in `696b653fb` (T-09). Gemini 4 Neon was out of its monthly quota and Sol on M5 was at capacity, so the review ran on m4's Codex. Findings and responses: `reports/review.md`.

## Tasks

### T-01 URL validation and lookalike check

- AC: AC-03, AC-06 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/mcpElicitationUrl.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/mcpElicitationUrl.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/package.json | Test: node node_modules/vite-plus/bin/vp test run packages/shared/src/mcpElicitationUrl.test.ts

### T-02 Adapter, answer rules and retries

- AC: AC-02, AC-04, AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/provider/ClaudeMcpUrlElicitation.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/ClaudeMcpUrlElicitation.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/ClaudeMcpElicitation.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ClaudeFormResponses.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Orchestrator.claudeForms.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/provider/ClaudeMcpUrlElicitation.test.ts apps/server/src/orchestration-v2/Orchestrator.claudeForms.test.ts

### T-03 URL card and screenshot

- AC: AC-01, AC-02, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/McpElicitationUrlCard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/McpElicitationUrlCard.test.tsx, .specweave/increments/1498-mcp-servers-can-ask-you-to-open-a-link-in-claude-threads/reports/url-card.png | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/chat/McpElicitationUrlCard.test.tsx

### T-04 Link contract and the adapter's existing tests

- AC: AC-01, AC-05 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/mcpElicitation.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/ClaudeMcpElicitation.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/provider/ClaudeMcpElicitation.test.ts

### T-05 Route URL cards in the composer

- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ComposerPendingApprovalPanel.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ChatComposer.tsx | Test: node node_modules/typescript/bin/tsc --noEmit --project apps/web/tsconfig.json

### T-06 Review round 1 fixes

- AC: AC-02, AC-03, AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/mcpElicitationUrl.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/mcpElicitationUrl.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/ClaudeMcpUrlElicitation.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/ClaudeMcpUrlElicitation.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/ClaudeMcpElicitation.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ClaudeFormResponses.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Orchestrator.claudeForms.test.ts | Test: node node_modules/vite-plus/bin/vp test run packages/shared/src/mcpElicitationUrl.test.ts apps/server/src/provider/ClaudeMcpUrlElicitation.test.ts apps/server/src/orchestration-v2/Orchestrator.claudeForms.test.ts

### T-07 Review round 2 fixes

- AC: AC-03, AC-05 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/mcpElicitationUrl.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/mcpElicitationUrl.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/ClaudeMcpUrlElicitation.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/ClaudeMcpUrlElicitation.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/ClaudeMcpElicitation.ts | Test: node node_modules/vite-plus/bin/vp test run packages/shared/src/mcpElicitationUrl.test.ts apps/server/src/provider/ClaudeMcpUrlElicitation.test.ts

### T-08 Review round 3 fixes

- AC: AC-03, AC-06 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/mcpElicitationUrl.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/mcpElicitationUrl.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/ClaudeMcpUrlElicitation.ts | Test: node node_modules/vite-plus/bin/vp test run packages/shared/src/mcpElicitationUrl.test.ts

### T-09 Review round 4 fixes

- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/mcpElicitationUrl.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/mcpElicitationUrl.test.ts | Test: node node_modules/vite-plus/bin/vp test run packages/shared/src/mcpElicitationUrl.test.ts

Verify and close 1498.

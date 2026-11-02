# Agents lead to Chrome pairing before other browser tools

## Problem

On November 2, 2026 the user's Chrome profile showed "Not paired" in the SpecWithCode Browser popup. An agent preparing an invoice got `"profiles":[]` from `chrome_profiles` with a hint that only said to install and pair. It then started a separate `claude --chrome` process, hit "Multiple Chrome browsers are connected to this account", and asked the user to choose among 5 unnamed browsers. The skill it followed names Claude in Chrome, and nothing the app sent told agents that pairing comes first. The Connect Chrome card under the failed call spoke of testing or reconnecting, not of the pairing code.

## Scope

In: the words agents get from `chrome_profiles`, `chrome_*` not-connected errors and the shared instructions on every provider, and the Connect Chrome card. Out: pairing without the pasted code, hiding Claude in Chrome from a machine that has never paired, blocking a `claude --chrome` child process, and the user's personal skills.

## Acceptance Criteria

- [x] AC-01: With no profile connected, `chrome_profiles` tells the agent to stop and ask the user to pair, names Settings › Chrome and the popup, and forbids switching to another browser tool unless pairing is not possible or the extension has a real fault. Both the never-connected and the disconnected hint carry that rule.
- [x] AC-02: A `chrome_*` call with no profile fails with the same rule.
- [x] AC-03: The `chrome_profiles` description and the orchestration instructions, which reach every provider with the studio-code tools, put `chrome_*` ahead of Claude in Chrome, also where a skill names it.
- [x] AC-04: The Connect Chrome card tells the user to paste the pairing code from Settings › Chrome into the popup.

## Approach

`relayHub.ts` owns one `OTHER_BROWSERS_LAST` sentence, used by `resolveProfile` and by `noProfileHint` in `chromeTools.ts`. One orchestration bullet, placed beside the computer-use bullet that handles the same skill conflict, covers Claude, Codex, Cursor, Pi and ACP providers. The Claude `--no-chrome` logic stays as it is: it already applies once a machine has paired.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 A machine that has never paired keeps Claude in Chrome. Hiding it would remove the only browser for someone without the extension; the hint and instructions lead to pairing instead (reversible).
### Open
- none

## Tasks

### T-01 Pair-first hints and errors
- AC: AC-01, AC-02 | Files: apps/server/src/browserExtension/relayHub.ts, apps/server/src/browserExtension/chromeTools.ts, apps/server/src/browserExtension/chromeTools.test.ts | Test: (cd apps/server && pnpm exec vp test run src/browserExtension/chromeTools.test.ts)

### T-02 Tool description and instructions on every provider
- AC: AC-03 | Files: apps/server/src/mcp/toolkits/chrome/tools.ts, apps/server/src/provider/StudioOrchestrationInstructions.ts, apps/server/src/provider/StudioOrchestrationInstructions.test.ts | Test: (cd apps/server && pnpm exec vp test run src/provider/StudioOrchestrationInstructions.test.ts)

### T-03 Connect Chrome card says how to pair
- AC: AC-04 | Files: apps/web/src/components/chat/ChromeConnectCard.tsx, apps/web/src/components/chat/ChromeConnectCard.test.tsx | Test: (cd apps/web && pnpm exec vp test run src/components/chat/ChromeConnectCard.test.tsx)

### T-04 Verify and close 1172
- AC: AC-01, AC-02, AC-03, AC-04 | Files: none | Test: specweave verify 1172

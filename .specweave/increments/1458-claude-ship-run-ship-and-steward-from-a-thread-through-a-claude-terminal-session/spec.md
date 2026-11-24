# Claude Ship: run /ship and /steward from a thread through a Claude terminal session

## Problem

On November 23, 2026 Anthropic announced Claude Ship (beta). Its local part is two Claude Code commands: `/ship` commits, pushes and opens a GitHub pull request, reviews it with `/code-review`, then watches it and pushes fixes; `/steward` starts that watch on an open pull request. They need Claude Code 2.1.330 or later (`https://code.claude.com/docs/en/ship-command`).

Typing `/ship` in a SpecWithCode Claude thread fails today. The app drives Claude Code through the Agent SDK (`CLAUDE_CODE_ENTRYPOINT=sdk-ts`), and the CLI starts these commands only in an interactive terminal session or in Anthropic's own desktop and VS Code clients. A live probe through the SDK with Claude Code 2.1.331 got: "Nothing started. Claude Code's built-in /ship doesn't start in this kind of session. Run claude in a terminal, and type it there." The SDK's `slash_commands` list does not offer `ship` or `steward` either. The CLI also refuses a line that a program fills in or that came from an accepted suggestion. Evidence: `reports/rea-claude-ship.md`.

The org-level agents (Code Review, PR Steward, Claude Approvals) run on Anthropic's servers against GitHub and are set up in claude.ai admin settings. They need nothing from the app.

## Scope

In: when a person types `/ship` or `/steward` (with arguments) as their own message in a Claude thread, the app does not send it to the model. It opens a card that explains why, checks what it can, and opens a Claude Code terminal session in the thread's folder and terminal drawer: a fork of the thread's own conversation when it has one. The person then types the line themselves. The card shows the exact line with a copy button.

Out: the org agents and their settings; the CLI's own gh and git checks (Claude Code reports them in the terminal); typing or submitting the line for the person (the CLI refuses it); posing as Anthropic's desktop or VS Code client by setting `CLAUDE_CODE_ENTRYPOINT` (declined: it gets around a product gate on purpose); `/ship` from coordinator, worker, queued or phone-relayed messages.

## Acceptance Criteria

- [ ] AC-01: In a direct Claude thread, a sent draft that is only `/ship` or `/steward`, with or without their documented arguments (`low`…`max`, a PR number or URL, `+bot`, `stop`, `terms`), opens the Claude Ship card. No model turn starts and the draft stays in the composer. Other drafts (`/shipit`, `/ship` with attachments, the same text in a Codex or other thread, a coordinator-routed draft) are sent as before.
- [ ] AC-02: The card says the command runs in a Claude Code terminal session and why. It shows the exact line to type with a copy button. When it knows, it also shows: Claude Code older than 2.1.330 (blocking, with how to update), the thread in plan mode, or the thread on full access (the terminal session uses auto mode, because a watch does not start under bypass permissions). Windows says no watch starts there.
- [ ] AC-03: Open terminal opens a new terminal in the thread's drawer, in the thread's folder (worktree when it has one), with the thread's Claude provider instance environment (so the same account and `CLAUDE_CONFIG_DIR` apply). It runs the configured Claude binary with an explicit `--permission-mode`, and `--resume <session> --fork-session` when the thread has a Claude session. It clears the variables that mark a child or SDK session (`CLAUDECODE`, `CLAUDE_CODE_CHILD_SESSION`, `CLAUDE_CODE_ENTRYPOINT`, `CLAUDE_CODE_SESSION_ID`, `CLAUDE_AGENT_SDK_VERSION` and the other markers listed in Approach). The line is never typed into the terminal for the person.
- [ ] AC-04: The command line is safe for the shell: every value is single-quoted, and a session id or binary path that is not plain characters is refused, with a message, rather than run.
- [ ] AC-05: Headless screenshots of the card (fork, new session, outdated CLI) are saved in `reports/`, and focused unit tests cover parsing, the card's notes and the command builder.

## Approach

1. `apps/web/src/components/chat/claudeShip.logic.ts` (new, pure): `parseClaudeShipCommand(text)` → `{ command: "ship" | "steward", line }` or null. `claudeShipNotes(...)` → the card's notes and whether Open is allowed. `buildClaudeShipTerminalCommand({ binaryPath, sessionId, permissionMode })` → the shell string `env -u CLAUDECODE -u … '<binary>' --permission-mode '<mode>' [--resume '<id>' --fork-session]`. `claudeShipPermissionMode(runtimeMode)`: approval-required → `default`, auto-accept-edits → `acceptEdits`, auto and full-access → `auto`.
2. `apps/web/src/components/chat/ClaudeShipDialog.tsx` (new): the card, using the app's dialog and button components and tokens.
3. `apps/web/src/components/ChatView.tsx`: intercept next to the Codex `/feedback` intercept, which also runs only for direct thread sends (after the coordinator route). State for the open card. Open terminal reuses the drawer's own `openTerminal` and `storeNewTerminal` path with `command` and `providerInstanceId`. The session id comes from the thread's active provider thread's `nativeThreadRef`, the version from the Claude provider status, the binary from the instance's `binaryPath` (default `claude`, found through the login shell's PATH).

Env markers cleared: `CLAUDECODE`, `CLAUDE_CODE_CHILD_SESSION`, `CLAUDE_CODE_ENTRYPOINT`, `CLAUDE_CODE_SESSION_ID`, `CLAUDE_CODE_SESSION_ATTENDED`, `CLAUDE_CODE_SESSION_KIND`, `CLAUDE_CODE_MESSAGING_SOCKET`, `CLAUDE_CODE_MESSAGING_TOKEN`, `CLAUDE_CODE_CHILD_NOTES_DIR`, `CLAUDE_CODE_EXECPATH`, `CLAUDE_AGENT_SDK_VERSION`, `CLAUDE_PID`. They matter when the app server itself was started from a Claude session.

Rejected: a server RPC that opens the terminal (the web already has every input, and terminal open is already guarded by terminal write access); typing the line into the pty (the CLI refuses lines it did not see typed, and that would be a program acting as the person); entrypoint spoofing (above).

Risks: a fresh folder shows Claude Code's folder-trust prompt first, which the person answers. A watch needs the terminal to stay open, and closing the drawer's terminal ends it; the card says so. Proof limit: the push, review and watch run against GitHub on a real pull request and are not exercised here. The live pty probe shows the command starts in an interactive session.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Fork the thread's Claude session rather than start a new one → fork, so `/ship` writes the commit message from the thread's conversation (Claude's docs recommend the session where the change was made). A thread without a session gets a new one.
- D-02 Full access → open the terminal in `auto`, because the CLI starts no watch under `bypassPermissions`.
- D-03 No entry in the composer's slash menu this round; the intercept works on the typed line.
### Open
- none

## Tasks

### T-01 Parse, notes and terminal command logic
- AC: AC-01, AC-02, AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/claudeShip.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/claudeShip.logic.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/chat/claudeShip.logic.test.ts

### T-02 Claude Ship card and composer intercept
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ClaudeShipDialog.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ClaudeShipDialog.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/ChatView.tsx | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/chat/ClaudeShipDialog.test.tsx

### T-03 Headless screenshots and build
- AC: AC-05 | Files: .specweave/increments/1458-claude-ship-run-ship-and-steward-from-a-thread-through-a-claude-terminal-session/reports/ | Test: web build from apps/web plus web typecheck

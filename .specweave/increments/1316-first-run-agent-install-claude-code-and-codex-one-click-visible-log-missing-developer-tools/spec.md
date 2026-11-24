# First-run agent install: Claude Code and Codex one click, visible log, missing developer tools

## Problem

On a new Mac (the owner's M5, 2026-11-12, app 1.0.268) first-run setup's "Connect your agents" step listed only Codex. Claude Code sat in a grey "Not installed: Claude Code, Cursor, ..." line behind an "Install one" menu. Choosing it opened a terminal panel under the list with the command typed and waiting for Enter, so nothing appeared to happen and no log showed. macOS then put its "The git command requires the command line developer tools" prompt over the app, with no word from setup about Git.

Checked: the M5 answered over Connect and reported Claude as unavailable; its terminal said `zsh: command not found: claude`, so Claude Code was really missing and detection (which looks in `~/.local/bin`, Homebrew, npm, nvm, volta, bun) was right. Neither installer (`claude.ai/install.sh`, `chatgpt.com/codex/install.sh`) needs git; the prompt is macOS reacting to any `/usr/bin/git` call on a Mac without the developer tools.

## Scope

In: the Agents step of first-run setup in the app repository (anton-abyzov/specwithcode): row order, a Claude Code install row, an install that runs at once with a visible log and errors, sign-in that follows the install, a Git recommendation with a one-click install on a Mac, and the server's Git check. Out: finding and gating every place the server runs git on a Mac without developer tools; installers for other agents; Settings > Providers.

## Acceptance Criteria

- [ ] AC-01: Claude Code is the first row and Codex the second. A missing Claude Code has its own row with "Install and sign in", not a name in the "Not installed" line.
- [ ] AC-02: One click runs the install at once in a panel that scrolls into view and shows its output. A non-zero exit keeps the log open with the exit code and a Retry; exit 0 closes it and reads the machine again.
- [ ] AC-03: After a successful install Claude's sign-in starts with no second click in the desktop app.
- [ ] AC-04: A machine without Git shows a "Git, recommended" row. On a Mac its button asks macOS for the developer tools, the row follows the install, and setup can continue without it.
- [ ] AC-05: The server answers whether Git is there without running the `/usr/bin/git` shim on a Mac.

## Approach

- `packages/contracts/src/server.ts`: `AgentSearch.git` (`present` | `missing`, optional).
- `apps/server/src/provider/providerDiscovery.ts`: `probeGit` (`xcode-select -p` on a Mac, then a git outside `/usr/bin`; `git --version` elsewhere), reported with each search.
- `apps/web/src/onboarding/providerReadiness.logic.ts`: Claude first, `install` row kind.
- `apps/web/src/components/onboarding/AgentsStep.tsx`, `AgentRows.tsx`: install row, Git row, panel that runs its command at once and keeps a failed log.
- `apps/web/src/components/settings/ClaudeSignIn.tsx`: `autoStart`.
- `apps/web/src/components/ThreadTerminalDrawer.tsx`: `onSessionExited` gets the exit code.
- Rejected: a new RPC for the Git check (the agent search already runs on entry, on "Check again" and after an install, and old servers simply leave the field out).
- Risk: release-gate walkers click through setup; none of their buttons changed.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 The install runs at once instead of waiting for Enter; the command stays readable under "Show command".
- D-02 Git is recommended, never required to leave the step.
### Open
- none

## Tasks

### T-01 Agents step: Claude first, one-click install with log, Git row, server Git check
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/onboarding/AgentsStep.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/onboarding/AgentRows.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/onboarding/providerReadiness.logic.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/ClaudeSignIn.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/ThreadTerminalDrawer.tsx, repositories/anton-abyzov/specwithcode-dev/apps/server/src/provider/providerDiscovery.ts, repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/server.ts | Test: cd apps/web && pnpm exec vp test run --project unit src/onboarding src/components/onboarding src/i18n && cd ../server && pnpm exec vp test run src/provider/providerDiscovery.test.ts

### T-02 Review, merge, release and check the released app
- AC: AC-01, AC-02, AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/onboarding/AgentsStep.tsx | Test: bash scripts/release/request-release.sh --released <merge commit>

### T-03 Verify and close 1316
- AC: AC-01 | Files: .specweave/increments/1316-first-run-agent-install-claude-code-and-codex-one-click-visible-log-missing-developer-tools/spec.md | Test: specweave verify 1316-first-run-agent-install-claude-code-and-codex-one-click-visible-log-missing-developer-tools

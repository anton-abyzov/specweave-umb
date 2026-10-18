# Computer use permission guidance

## Problem

SpecWithCode's `computer_*` tools (specwithcode-dev #311, #328) run inside the desktop app, which needs macOS Screen Recording and Accessibility. When either is missing, the app opens System Settings, waits two minutes and returns a text error, so the thread only says it is "Blocked". On M4 both permissions are still off after 1.0.43 (Mouse speed thread, 2026-10-18). Nothing in the app shows the permission state, offers the macOS prompt again, or lets the user retry. Settings > Connections also shows Codex's old `computer-use` entry as "Disabled" and Claude Code as "Not found", which reads as "computer use is off" although neither entry is what agents use.

## Scope

In: desktop IPC to read and request the two permissions and to quit and reopen the app; a permission card in the thread (live, while an action waits; and under a failed action, with a retry); the same checklist under Settings > Agent computer access and on the Connections `computer-use` row; agent-facing error text that points to the card. Out: Windows/Linux computer use; changes to Codex's or Claude's own computer-use features.

## Acceptance Criteria

- [ ] AC-01: The desktop app reports Screen Recording and Accessibility status to the renderer and can show the macOS prompt, open the exact Privacy & Security pane with the drag helper, and quit and reopen itself.
- [ ] AC-02: While a computer-use action waits for a permission, the thread that asked shows a card above the composer with live status and Allow buttons; it disappears once the permission is granted and the action continues.
- [ ] AC-03: A computer-use tool that failed for a missing permission shows a card under it with live status, Allow buttons, a Quit & Reopen fallback, and once granted a button that asks the agent to try again.
- [ ] AC-04: Settings > Agent computer access and the Connections `computer-use` row show the permission checklist with Allow buttons and explain that SpecWithCode provides computer use for every agent.

## Approach

The grant belongs to SpecWithCode.app (Developer ID `com.specweave.studio`): the launchd service only brokers requests, and the app's main process runs screencapture/osascript, whose TCC responsible process is the app. Host requests carry the calling thread id so the renderer can show the card in that thread. Reuse `PermissionChecklist`, `usePermissionStatus`, `MacPermissions.showHelper` and the Chrome connect card pattern. Detection of failed actions is by the stable phrases in the desktop's permission errors.

## Open questions

- none

## Tasks

### T-01 Desktop permission IPC and thread-aware host requests
- AC: AC-01 | Files: packages/contracts/src/computerUse.ts, packages/contracts/src/ipc.ts, apps/desktop/src/computerUse/MacComputerUse.ts, apps/desktop/src/ipc/methods/computerUse.ts, apps/desktop/src/preload.ts, apps/server/src/computerUse/ComputerUseBroker.ts, apps/server/src/mcp/toolkits/computer/handlers.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/computerUse/ComputerUseBroker.test.ts

### T-02 Thread permission card, composer banner and retry
- AC: AC-02, AC-03 | Files: apps/web/src/components/computerUse/*, apps/web/src/state/computerUse.ts, apps/web/src/components/chat/MessagesTimeline.tsx, apps/web/src/components/ChatView.tsx, packages/client-runtime/src/work-log/presentation.ts | Test: node node_modules/vite-plus/bin/vp test run packages/client-runtime/src/work-log/presentation.test.ts apps/web/src/components/computerUse

### T-03 Settings and Connections checklist
- AC: AC-04 | Files: apps/web/src/components/settings/ProjectDefaultsSettings.tsx, apps/web/src/components/connections/ConnectionMatrix.tsx | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/connections/ConnectionMatrix.test.tsx

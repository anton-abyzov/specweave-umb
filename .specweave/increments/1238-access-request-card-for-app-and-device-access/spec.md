# Access request card for app and device access

## Problem

When an agent in SpecWithCode needs extra access, the user sees either a small "App access approval" label over a raw text box (`ComposerPendingApprovalPanel`) or the bare macOS permission checklist (`ComputerUsePermissions`). Neither says plainly what is asked, why, or for how long. Computer use is all-or-nothing per machine: once on, an agent may drive any app with no per-app consent. Device access is a single machine toggle; an agent that needs a simulator while it is off has no way to ask. None of this can be approved from the iPhone app.

## Scope

In: one access request card (title naming what is asked, the agent's one-sentence reason, each requested item with its real icon and what it may do, Allow / Deny for the whole set, scope "This thread" or "Always on this machine") on web/desktop and the native iOS app; a `request_access` agent tool; per-app consent for computer use (apps opened or controlled by an agent); per-device consent when an agent opens a simulator, and a way to ask for devices while Agent device access is off; a list of "Always" grants with Remove in Settings; docs and CHANGELOG.

Out: command and file-edit approvals (unchanged); provider-native `mcp-elicitation` approvals; folder access, work on another machine and moving SecretRequestCard onto the card (the data model leaves room for them: subject kinds `folder` and `machine`); the React Native app in apps/mobile (shows its generic row).

## Acceptance Criteria

- [ ] AC-01: An agent calling `request_access` with apps and/or devices and a reason gets a pending card in its thread; Allow with a scope returns `allowed` with that scope, Deny returns `denied`, an ended run returns `cancelled`, a timeout `timed_out`; already granted items are not asked again.
- [ ] AC-02: With computer use on, `computer_open` of an app or an input action (click, drag, scroll, type, key) on a frontmost app that is not allowed for the thread or machine raises the card for that app and proceeds only after Allow; Deny fails the action with a message telling the agent the user declined.
- [ ] AC-03: With Agent device access off, `device_open` on a device not allowed for the thread or machine raises a "Control <device>" card and opens it for the agent only after Allow; `request_access` for a device grants that device (thread or machine) without changing the setting. With Agent device access on, devices are never asked about.
- [ ] AC-04: The web/desktop card sits above the composer (owner's reference, 2026-11-04): accent tile, "<Agent> wants to use <App>", the reason, one chip per item with its real icon or glyph and an "All" tag, a note line, Deny and "Allow for this session" (thread scope) plus a quiet "Always allow on this machine"; the timeline keeps a one-line row, and answered cards collapse to a one-line outcome. It renders in light and dark at desktop and 390px widths. The macOS permission card uses the same look.
- [ ] AC-09: A thread waiting on an access card counts as waiting for the user in thread lists and on the iPhone; the coordinator shows it with a hand icon, the thread title, "Asking to use apps on your computer" (or the device/folder text) and View thread, plus the line "<thread> is waiting for you to allow access to <machine>, so it can <purpose>."
- [ ] AC-05: "Always on this machine" grants are listed under Settings → Integrations → Agent computer access (apps) and Devices (devices) with Remove.
- [ ] AC-06: The native iOS app decodes `access_request` items, shows the same card in the thread and answers it.
- [ ] AC-07: docs/user/computer-use.md, docs/user/devices.md and CHANGELOG Unreleased describe the card.
- [ ] AC-08: Shipped: PR reviewed and green, merged, released, and the card verified in the released app.

## Approach

Mirror the secret request flow, which already reaches every client as a persisted turn item:

1. Contracts: `packages/contracts/src/accessRequest.ts` (subject, scope, answer input, error), `access_request` turn item and internal `access_request.record` command in `orchestrationV2.ts`, `access.answerRequest` and `access.listGrants` / `access.revokeGrant` RPCs, `request_access` MCP input/result in `orchestratorMcp.ts`, new `appInfo` computer-use action.
2. Server: `apps/server/src/access/AccessGrants.ts` (thread and machine grants, persisted under the state dir) and `AccessRequests` (answer: validates, records, writes grants); Orchestrator dispatch; pending-card handling wherever pending secret cards are handled (orphaned runs, recovery, archive guard, deferred resolution, shell pending input); `OrchestratorMcpService.requestAccess` polls the card like `requestSecret`; computer and device handlers gate through it.
3. Desktop: `appInfo` resolves an app name to its bundle and a 64 px PNG icon (QuickLook thumbnail) so the card shows the real icon.
4. Web: `AccessRequestCard` in the timeline; grants list in Settings.
5. iOS: `TurnItem.AccessRequest`, `AccessRequestCard` SwiftUI view, `access.answerRequest` command.

Risks: the per-app gate adds one status round trip before input actions; existing threads that drive apps will see one card per app until the user picks "Always". Device tools hidden while access is off only appear at the agent's next turn after Allow.

## Decisions

### Asked
- none (owner approved the brief through the coordinator)
### Defaulted (change any before sw-do)
- D-01 Apps are asked for by default once computer use is on (no "allow every app" switch) → matches Claude's computer-use model; "Always on this machine" removes the prompt per app.
- D-02 Grant key for apps is the app's display name (what macOS reports as frontmost), not the bundle id → frontmost checks need no extra lookup.
- D-03 Screenshots and pointer moves are not gated → they change nothing in an app.
- D-05 The note line says what Allow lets the agent do, not "Your other windows will be hidden": SpecWithCode's computer use does not hide windows.
- D-06 The tile shows a shield, not a padlock: the repo's retired-icons guard bans padlock icons.
- D-04 Device consent is checked at `device_open` only; `agent-device` commands after open are not gated per call.
### Open
- none

## Tasks

### T-01 Contracts, grants and the request flow
- AC: AC-01 | Files: packages/contracts/src/accessRequest.ts, packages/contracts/src/orchestrationV2.ts, packages/contracts/src/orchestratorMcp.ts, packages/contracts/src/rpc.ts, apps/server/src/access/AccessGrants.ts, apps/server/src/access/AccessRequests.ts, apps/server/src/orchestration-v2/Orchestrator.ts, apps/server/src/mcp/OrchestratorMcpService.ts, apps/server/src/ws.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/access

### T-02 Per-app consent for computer use
- AC: AC-02 | Files: apps/server/src/mcp/toolkits/computer/handlers.ts, apps/desktop/src/computerUse/MacComputerUse.ts, packages/contracts/src/computerUse.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/access apps/server/src/computerUse

### T-03 Per-device consent
- AC: AC-03 | Files: apps/server/src/mcp/toolkits/device/handlers.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/mcp/toolkits/device

### T-04 Web card and Settings grants
- AC: AC-04, AC-05, AC-09 | Files: apps/web/src/components/chat/AccessRequestCard.tsx, packages/client-runtime/src/accessRequest.ts, apps/web/src/components/chat/MessagesTimeline.tsx, apps/web/tests/access-request/ | Test: node apps/web/tests/access-request/verify.mjs <report-dir>

### T-05 iOS card
- AC: AC-06 | Files: apps/ios/SWCKit/Sources/SWCWire/TurnItem.swift, apps/ios/SWCKit/Sources/SWCFeatures/AccessRequestCard.swift | Test: cd apps/ios/SWCKit && swift test --filter AccessRequest

### T-06 Docs and changelog
- AC: AC-07 | Files: docs/user/computer-use.md, docs/user/devices.md, CHANGELOG.md | Test: grep -q "Allow for this session" docs/user/computer-use.md && grep -q "request_access" docs/user/devices.md

### T-07 Ship
- AC: AC-08 | Files: none | Test: gh pr view --json state -q .state | grep -q MERGED

### T-08 Verify and close 1238
- AC: AC-08 | Files: none | Test: specweave verify 1238

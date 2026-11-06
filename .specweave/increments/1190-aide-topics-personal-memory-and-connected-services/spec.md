# 1190 Aide topics, personal memory and connected services

## Problem

Aide looks and behaves like a project. Its right pane says Threads, its memory tab says Project memory, and its prompt treats memory as project knowledge. The user's point on November 3, 2026: the concept is close to a project, but this agent's memory belongs to a person, its conversations are not "threads", and it should connect to more of that person's services (reference: ChatGPT's Customize screen, `/Users/antonabyzov/Downloads/Remove Glasses Only.png`, with Email, Calendar, Health and Finances rows).

Today Google access lives in Settings > Google account, other services need a hand-written MCP command plus a variable in the service's environment, and nothing in Aide shows what it can reach.

## Scope

In: the word Topics in Aide (web and iOS), memory framed as about the person, a Services tab in Aide's settings, one-click Notion and Todoist connections with a token kept in the app's secret store.

Out: a new data model for topics, Areas or Errands (superseded), direct Health or bank connections, moving Aide between machines, OAuth flows for new services, renaming threads in normal projects.

## Acceptance Criteria

- [ ] AC-01: In Aide, the right pane tab, its breadcrumb, its empty state, search, sort and filter labels, the + button and the coordinator notice say topic or Topics, and a normal project still says thread or Threads
- [ ] AC-02: Aide's composer reads "Ask Aide anything" once it has topics, and a normal project's placeholder is unchanged
- [ ] AC-03: A quiet pinned topic appears in a Pinned section above the status sections in Aide, and one that needs the user or is running stays in that status; a normal project shows no such section
- [ ] AC-04: Aide's prompt says its memory is about one person, tells it to save facts about the user under `user_` files, to say "topic" to the user, to continue a matching topic instead of starting a new one, to pin one the user calls ongoing, and to check connected services before saying it cannot reach one; a normal project's prompt has none of these lines
- [ ] AC-05: Aide's Memory tab is headed "About you" and says this memory stays on this machine; a normal project still says "Project memory"
- [ ] AC-06: Aide's settings have a Services tab and a normal project's settings do not
- [ ] AC-07: Services shows Email, Email drafts, Calendar and Drive with their real state for this assistant; a service the Google account granted has a switch, and one it has not links to Settings > Google account
- [ ] AC-08: Connecting Notion or Todoist from Services takes a token in a password field, saves a pinned-version command, stores the token only in the secret store, checks it, then lists the tools with none allowed until the user picks them
- [ ] AC-09: A token never appears in the connection record, the read result, tool descriptions or tool output, and revoking a connection deletes its stored tokens
- [ ] AC-10: A token can be set only for a variable that connection names, by a client with the same scope as saving a connection
- [ ] AC-11: Services shows Health and Finances as "No direct connection" with the working route, exporting to an approved folder, and links Browser to Settings > Chrome and Your own to Environment
- [ ] AC-12: Aide stays private to its machine: every existing refusal still holds, and stored tokens are not part of memory sync or handoff
- [ ] AC-13: On iOS the assistant's Threads button and overview heading say Topics, and a normal project still says Threads

## Approach

**Name: Topics.** The earlier concept split work into Areas and Errands, which needs a new data model and two nouns. The user has now said the concept is close to a project, so one noun for the one thing that exists wins. Topic fits both Taxes and Verizon email change, while Area fits only the first. Channel implies other people, and Aide is private. A pin gives the long-lived case: a pinned thread already never auto-settles.

No data change: a topic is a thread, with its ID, history and links unchanged. Vocabulary lives in one new file, `apps/web/src/studio/assistantTerms.ts`.

**Tokens.** Connections pass named variables from `process.env`, which a user cannot set from the app. The transport now takes values from the server secret store first, then the environment. A new RPC writes them; it goes in the same group as `nativeConnectionApply` because the core group is at TypeScript's depth limit. Redaction covers stored values too.

**Services.** Presets are data in `apps/web/src/studio/assistantServices.ts`, with pinned versions. `npx` needs Node on the machine; a failed check says so. Tools stay unallowed until picked, and calls keep the normal approval.

**Collisions.** PR 1254 changes `ProjectWorkspaceSurface.tsx`, `ProjectWorkspace.test.tsx` and the web `personalAssistant.ts`; PR 1247 changes `AideSetting.tsx` and settings. This work leaves `personalAssistant.ts` and `AideSetting.tsx` alone and keeps Surface edits to a few lines, rebasing on whichever merges first.

Rejected: Stripe preset, because `@stripe/mcp@0.3.3` did not answer `tools/list` in 90 seconds. Slack, because the official server is deprecated. A generic vault, because the secret store already exists.

## Decisions

### Asked

- D-01 Name → the user delegated it: "come up with ideas and implement it". Chose Topics.

### Defaulted (change any before sw-do)

- D-02 Presets → Notion and Todoist, the two official packages whose servers answered a real `tools/list` probe.
- D-03 Tokens stored server-side per project and connection, not per machine-wide name, so a token for Aide is not usable by another project.
- D-04 No tools allowed by default after a check; the user picks.
- D-05 Normal projects get the token RPC too but no UI for it; the server rule is not personal-only.

### Open

- none

## Tasks

### T-01 Stored connection tokens

- AC: AC-09, AC-10, AC-12 | Files: repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/projectConnections.ts, repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/projectConnectionRpc.ts, repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/rpc.ts, repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/clientRpcPermissions.ts, repositories/anton-abyzov/specwithcode-dev/packages/client-runtime/src/state/projectWorkspace.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/ProjectConnectionService.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/ProjectConnectionRpc.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/connections/ProjectConnectionTransport.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/connections/config.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/runtimeLayer.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/observability/RpcInstrumentation.ts | Test: cd apps/server && pnpm exec vp test run src/project/connections src/project/ProjectConnectionService.test.ts

### T-02 Aide's prompt

- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/ProjectWorkspaceService.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/ProjectWorkspaceService.test.ts | Test: cd apps/server && pnpm exec vp test run src/project/ProjectWorkspaceService.test.ts

### T-03 Topics in the web app

- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/assistantTerms.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/projectPaneModel.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/ProjectPaneBar.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/ThreadsPane.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/ProjectThreadHeader.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/StarterSuggestions.tsx | Test: cd apps/web && pnpm exec vp test run src/studio/assistantTerms.test.ts src/studio/shellModel.test.ts src/components/studio/shell

### T-04 Services tab and About you

- AC: AC-05, AC-06, AC-07, AC-08, AC-11 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/assistantServices.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/AssistantServices.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/panes.css, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/ProjectMemory.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/ProjectWorkspaceSettings.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/projectSettingsSearch.logic.ts | Test: cd apps/web && pnpm exec vp test run src/studio/assistantServices.test.ts src/components/studio/ProjectWorkspace.test.tsx

### T-05 Topics on iOS

- AC: AC-13 | Files: repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Chat/ChatView.swift, repositories/anton-abyzov/specwithcode-dev/apps/ios/SWCKit/Sources/SWCFeatures/Overview/ProjectOverviewView.swift | Test: swift test --package-path apps/ios/SWCKit

### T-06 Headless screens for the manual check

- AC: AC-01, AC-06 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/tests/project-workspace/aide-topics-check.mjs, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/project-workspace/mocks.tsx | Test: node apps/web/tests/project-workspace/aide-topics-check.mjs (with its fixture served, headless)

### T-07 Verify and close 1190

- AC: AC-01, AC-13 | Files: none | Test: specweave verify 1190-aide-topics-personal-memory-and-connected-services

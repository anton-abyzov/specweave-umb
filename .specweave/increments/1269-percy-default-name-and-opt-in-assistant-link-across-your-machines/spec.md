# Percy default name and opt-in assistant link across your machines

## Problem

On November 9, 2026 Anton set up a Windows machine. Naming the assistant there created a second personal assistant, listed next to the Mac one with a machine label. He expected one.

That is today's design, set by Anton on October 20, 2026 (increment 0981): one private assistant per machine, never shared. On the Windows server `projects.createNew` reaches `ManagedProjectFolders.createNamedProject` (`apps/server/src/project/ManagedProjectFolders.ts:658-694`), finds no personal project in that machine's database and creates one. The backstop guard (`apps/server/src/orchestration-v2/ProjectCommands.ts:649-660`) is per database too. The sidebar lists every connected machine's assistant with its machine label (`apps/web/src/components/studio/shell/StudioSidebar.tsx:855-922`) and offers "Set up here" whenever the current machine has none. Nothing at setup says another machine already has one, or that nothing carries over.

Three gaps follow:

- **Name.** "Aide" needs explaining every time. Anton wants "Percy" as the default. The name is just the project `title`; about 15 web strings, 25 iOS strings and 10 Android strings hardcode "Aide" instead of reading the title, so a renamed assistant still says "Aide" in places.
- **No way to have one assistant across your machines.** Personal memory is refused by every link and peer-sync path (`LinkedMemorySync.ts:266,475`, `LinkedPeerSync.ts:266,990`, `LinkedPeerRoute.ts:139`, `ProjectLink.ts:196-197,500`).
- **Protection is thinner than the privacy claim.** Personal memory is plaintext SQLite, tokens are 0600 `.bin` files (`apps/server/src/auth/ServerSecretStore.ts:246,283,287`), `studio_thread_read` and `studio_thread_search` do not refuse another project's agent reading personal threads on the same machine (`mcp/toolkits/orchestrator/handlers.ts:46-60,223`, `mcp/toolkits/thread/handlers.ts:159-184`), and project memory skips the scope check when there is no caller thread (`mcp/toolkits/projectMemory/handlers.ts:19`).

Research (code read plus REA of Claude Desktop, Claude Code, ChatGPT and Codex) is in `research/`. Claude and ChatGPT keep one assistant per account, synced only through their server, with project-scoped memory, an incognito or temporary mode, and tokens in the OS keystore on macOS. Their local agent memory (Claude Code, Codex) stays on the machine and starts empty on a second device. SpecWithCode has no account server, so the equivalent is an opt-in, owner-approved link between your own machines.

## Scope

In (`anton-abyzov/specwithcode`, plus `anton-abyzov/specweave` docs-site):

- Phase 1: Percy default name, title-driven copy on web, iOS, Android and server, one-time migration of the old default, docs. Ships on its own.
- Phase 2: same-machine read guards for personal threads and memory; macOS Keychain wrapping of server secrets.
- Phase 3 (after Phases 1-2 ship): opt-in personal link between two machines of the same owner, through a new narrow route.

Out: chat history, topics, routines, connections, OAuth tokens and files ever leaving their machine; merging or deleting existing assistants; linking assistants of different owners; SQLCipher; Windows DPAPI and Linux libsecret wrapping (follow-up); disk-encryption warnings.

## Acceptance Criteria

### Phase 1: Percy
- [ ] AC-01: A new assistant created from web, desktop, iOS or Android with the suggested name gets the title "Percy". `DEFAULT_PERSONAL_ASSISTANT_NAME` in `packages/contracts/src/project.ts:119` is "Percy"; iOS and Android send "Percy", never an empty name (older servers reject empty names).
- [ ] AC-02: After upgrade, every personal project titled exactly "Aide" (trimmed) is renamed to "Percy" through `project.meta.update`, once. Custom names are untouched. If a project is already named "Percy" the rename is skipped and logged, never failed.
- [ ] AC-03: The one-time marker is a numbered migration, so a user who renames back to "Aide" afterwards keeps that name across restarts.
- [ ] AC-04: No user-visible web, iOS, Android or server string hardcodes "Aide". Starter text, Services, Memory, topic prompt, pane words (`assistantTerms.ts` and its five callers), handoff refusals, set-up rows, sample (fixture) data and error copy use the assistant's title, or "your assistant" where none is in scope.
- [ ] AC-05: The eight locales interpolate the name in the two translated strings (`apps/web/src/i18n/phrases/*.ts`); `fr.ts:141` "Aider" is unchanged.
- [ ] AC-06: Internal identifiers (`aideEnabled`, `ChatTarget.aide`, `model.aide`, `hiddenAideRoute`, `AideBriefingSetup`, `kind:"personal"`, reason codes, test folders) are unchanged and existing `aideEnabled` values survive.
- [ ] AC-07: Setup on a machine whose fleet already shows another machine's assistant says, before naming, "Percy on <machine> stays there. This creates a separate Percy for this machine." Docs (repo `docs/studio/*`, `apps/ios`, `apps/android` READMEs, docs-site `docs/studio/projects.md`) say "your personal assistant (default name Percy)", one per machine.

### Phase 2: protection on one machine
- [ ] AC-08: `studio_thread_read` and `studio_thread_search` refuse personal-project threads to an agent thread of any other project, with or without a work grant.
- [ ] AC-09: Project memory calls without a caller thread follow the `projectKnowledge/handlers.ts:17` rule: allowed only for management credentials, listed explicitly; external MCP clients keep working through them.
- [ ] AC-10: On macOS, ServerSecretStore keeps a Keychain-wrapped copy, verifies it by reading back before removing the `.bin`, and fails closed on unwrap failure instead of regenerating keys. Pairing, signed URLs and connection tokens survive an upgrade and restart.

### Phase 3: opt-in link (after Phases 1-2 ship)
- [ ] AC-11: Linking is offered only between machines enrolled under the same owner credential, never across worker grants. Other owners' assistants are not offered.
- [ ] AC-12: A link is requested from one machine and approved by a person in the target machine's own UI. No MCP tool, agent thread or work grant can request or approve it. Both ends show machine label and key fingerprint.
- [ ] AC-13: A new route exports only title, icon, instructions and allowlisted memory files, after a secret and PII scan; no coordinator binding, plan, replica, turns, workspace root or takeover. A test asserts no secret names, connection rows or chat text are in an export.
- [ ] AC-14: A memory item marked "Keep on this machine" is never exported; incoming files that collide with it are renamed, and tombstones are sent only for files already exported.
- [ ] AC-15: Linking two existing assistants shows the conflicting files for review before the first sync; nothing is deleted or overwritten.
- [ ] AC-16: Unlink stops sync on both ends; each keeps its data; "Ask <machine> to delete what it received" applies on that machine's next connection. Link, approval, export (file names) and unlink are logged on both machines and shown in assistant settings.
- [ ] AC-17: Linked assistants show as one sidebar row with machine chips; unlinked ones as today.

## Approach

Phase 1 first, as one PR. `ManagedProjectFolders.createNamedProject` maps a literal "Aide" from clients older than the fixed build to "Percy" until a fixed end date (D-05). The migration is a numbered server migration that dispatches `project.meta.update` and records itself in `effect_sql_migrations`, so no key-value table is needed. Web copy takes the title from the personal project; `assistantTerms.paneWords(name)` gets a name argument.

Phase 2 reuses existing guards (`refuseMachinePrivate`, `projectKnowledge` caller rule). Keychain wrapping lands behind a setting, default on for macOS desktop, off for headless services until tested.

Phase 3 never reuses `ProjectLink`: its preview carries workspace root, fingerprint, replica, coordinator binding and 400-character message snippets (`ProjectLink.ts:470-530`), and `studio_project_link_accept` is agent-callable remotely (`fleet/RemoteStudioMcpClient.ts:50,76`). A dedicated `PersonalLinkRoute` reuses only the three-way memory merge (`linkedMemoryMerge.ts`, `linkedMemoryThreeWay.ts`) and the fleet transport (Tailscale HTTPS or Connect with DPoP).

Rejected: one assistant per fleet (overturns Anton's October 20 rule and turns every machine's chats into a merge problem); syncing chats and topics (machine paths and secrets); automatic linking; SQLCipher now (database migration cost for little gain over FileVault/BitLocker).

Risk, name: low. BrowserStack sells a visual-testing product called Percy (percy.io) and likely holds the US mark, and other PERCY filings exist in classes 9/42. As an in-app default the user can rename, never marketed as a product name, logo or domain, it does not conflict (`research/percy.md`).

## Decisions

### Asked
- D-01: Default name → "Percy" (Anton, November 9, 2026).
- D-02: Setup on a new machine whose fleet has another Percy → ask "Use Percy from <machine>" or "Separate Percy here", no default (Anton, November 9, 2026).
- D-03: A link shares name, icon, memory about you and instructions; chats, topics, routines, connections, tokens and files stay local (Anton, November 9, 2026).
- D-04: Build Phase 3, after Phases 1-2 ship (Anton, November 9, 2026).
### Defaulted (change any before sw-do)
- D-05: Old clients sending "Aide" map to "Percy" until January 31, 2027.
- D-06: Keystore wrapping ships macOS only first.
### Open
- none

## Tasks

### T-01 Percy default and create mapping
- AC: AC-01, AC-06 | Files: packages/contracts/src/project.ts, apps/server/src/project/ManagedProjectFolders.ts, apps/server/src/project/ManagedProjectFolders.test.ts | Test: vp test run apps/server/src/project/ManagedProjectFolders.test.ts

### T-02 One-time rename migration
- AC: AC-02, AC-03 | Files: apps/server/src/persistence/Migrations/, apps/server/src/project/PercyRename.test.ts | Test: vp test run apps/server/src/project/PercyRename.test.ts

### T-03 Web copy from the title, locales and setup line
- AC: AC-04, AC-05, AC-07 | Files: apps/web/src/studio/assistantTerms.ts, apps/web/src/studio/personalAssistant.ts, apps/web/src/components/studio/AssistantServices.tsx, apps/web/src/components/studio/ProjectMemory.tsx, apps/web/src/components/studio/ProjectWorkspaceSurface.tsx, apps/web/src/components/studio/shell/StudioSidebar.tsx, apps/web/src/components/settings/AideSetting.tsx, apps/web/src/components/settings/BrowserExtensionSettings.tsx, apps/web/src/i18n/phrases/*.ts, packages/contracts/src/settings.ts | Test: vp test run apps/web/src/studio apps/web/tests/aide-per-machine

### T-04 iOS and Android copy
- AC: AC-01, AC-04 | Files: apps/ios/SWCKit/Sources/SWCFeatures/**, apps/ios/SWCKit/Sources/SWCSync/{ShellSummaries,LiveEngine+Settings,SyncError,FixtureEngine}.swift, apps/android/**/sync/*.kt, apps/android/wire/src/test/resources/fixtures/*.json | Test: swift test (SWCKit) and ./gradlew test (Android)

### T-05 Server copy and docs
- AC: AC-04, AC-07 | Files: apps/server/src/mcp/personalChatBoundary.ts, docs/studio/*.md, apps/ios/README.md, apps/ios/docs/*.md, apps/android/README.md, specweave docs-site/docs/studio/projects.md | Test: grep -rn '"Aide' apps --include=*.ts --include=*.tsx --include=*.swift --include=*.kt returns only identifiers

### T-06 Same-machine read guards
- AC: AC-08, AC-09 | Files: apps/server/src/mcp/toolkits/orchestrator/handlers.ts, apps/server/src/mcp/toolkits/thread/handlers.ts, apps/server/src/mcp/toolkits/projectMemory/handlers.ts | Test: vp test run apps/server/src/mcp

### T-07 Keychain-wrapped secrets on macOS
- AC: AC-10 | Files: apps/server/src/auth/ServerSecretStore.ts, apps/server/src/auth/ServerSecretStore.test.ts | Test: vp test run apps/server/src/auth

### T-08 Personal link route, consent and audit (Phase 3)
- AC: AC-11, AC-12, AC-13, AC-16 | Files: apps/server/src/project/PersonalLinkRoute.ts, apps/server/src/project/PersonalLinkRoute.test.ts | Test: vp test run apps/server/src/project/PersonalLinkRoute.test.ts

### T-09 Keep-on-this-machine flag and conflict review (Phase 3)
- AC: AC-14, AC-15 | Files: apps/server/src/persistence/Migrations/, apps/server/src/project/ProjectWorkspaceService.ts, apps/web/src/components/studio/ProjectMemory.tsx | Test: vp test run apps/server/src/project

### T-10 Setup choice and linked sidebar row (Phase 3)
- AC: AC-11, AC-17 | Files: apps/web/src/studio/personalAssistant.ts, apps/web/src/components/studio/shell/StudioSidebar.tsx, apps/ios/SWCKit/Sources/SWCFeatures/RootView.swift | Test: vp test run apps/web/tests/aide-per-machine

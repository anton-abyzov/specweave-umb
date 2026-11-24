Findings are from `specwithcode-dev` at `76b2dd433f`, read-only, plus one local `specweave-studio db query`. [V] means I saw it in code, a document or the database; [I] means I inferred it.

**Main conclusions:**
- **Second assistant:** one assistant per machine is by design. The new Windows server creates its own personal project, and every client lists the assistants from all connected machines.
- **Name storage:** the assistant's name is just its project `title`. No field marks a name as default or custom, and about 15 user-visible strings hardcode "Aide" instead of using the title.
- **Encryption at rest:** none. Aide memory is plain SQLite and tokens are plain `.bin` files with 0600 permissions; the Keychain is not used.

## 1) Data model

- **Kind:** an assistant is a project whose `workspaceSettings.kind` (or `kind`) is `"personal"`. `isPersonalAssistantProject` checks this at `packages/shared/src/personalAssistant.ts:17`. [V]
- **Create command:** `createsPersonalAssistant(command)` returns true for `project.create` with `kind==="personal"` (`apps/server/src/orchestration-v2/ProjectCommands.ts:255`). [V]
- **Which assistant counts:** `machineAssistantOf` (`packages/shared/src/personalAssistant.ts:37`) picks the earliest-created, non-deleted personal project, including archived ones. Ties break by id. Later duplicates are kept and never merged. [V]
- **Guard:**
  - `ProjectService.dispatch` reads `machineAssistantOf(projects.list())` (`ProjectService.ts:517`). That is this server's own projects table only.
  - The planner rejects with `PersonalAssistantExistsError` when an assistant with a different id exists (`ProjectCommands.ts:195-206,651-657`). This maps to `assistant_exists`, whose message is "This machine already has its personal assistant…" (`ProjectService.ts:274,582`).
  - Concurrent creates are serialized by `PERSONAL_ASSISTANT_LOCK` (`ProjectService.ts:100,552-557`). [V]
- **Scope:** one assistant per server database, which means per `environmentId` (machine). It is not per user and not per fleet. [V for the per-database scope; I for "per environmentId", since each machine runs its own server and state.]
- **Create gate:** `aideEnabled` is a per-machine server setting (`packages/contracts/src/settings.ts:1844-1848`, default true). It is checked in `ProjectService.create` (`:676`) and in `ManagedProjectFolders.createNamedProject`, which returns the existing assistant when there is one (`ManagedProjectFolders.ts:157`). [V]
- **Clients:** the web setup step targets one environment (`apps/web/src/studio/personalAssistant.ts:79-98`). `findMachineAssistant` filters by `environmentId` (`:26`). [V]
- **Local DB on this Mac:** one live assistant, `5428ab1e…` titled "Aide" and created October 10, 2026. A personal project "Example Household" was deleted on October 28, 2026. [V]

## 2) Why a second assistant appears after linking Windows

- **Cause:** naming the assistant on Windows runs `project.create kind:"personal"` against the Windows server. That server's database has no personal project, so the guard passes and the project is created there. [I, from the code path]
- **StudioSidebar:**
  - It collects personal projects from every connected environment (`apps/web/src/components/studio/shell/StudioSidebar.tsx:855-868`).
  - It ranks them: this machine's assistant, then other machines' assistants, then pre-rule extras.
  - The row hint is `machineLabel`, plus "extra" for duplicates, once there is more than one environment (`:869-876`).
  - "Set up here" is offered whenever this client's primary environment has no assistant, even if another machine's assistant is listed (`:914-922`, `machineNeedsAssistantSetup` at `personalAssistant.ts:59`). [V]
- **Other surfaces:**
  - `Sidebar.tsx:2419-2427` and `LegacySidebar.tsx:3198` only apply the `aideEnabled` filter (`visibleWithAide`, `threadsVisibleWithAide`). [V]
  - `DraftMachinePicker.tsx:485-488` shows `PERSONAL_ASSISTANT_PER_MACHINE_LINE`: "Each machine has its own private assistant. Nothing transfers between them." [V]
  - Opening another machine's assistant shows `OtherMachineAssistantNotice` ("This assistant lives on {name}", `ProjectWorkspaceSurface.tsx:1696`). [V]
  - `hiddenAideRoute.ts` only redirects project or chat routes to Overview while `aideEnabled` is off. It plays no part in multiple machines. [V]
- **Unused helper:** `assistantDisplayTitle` ("Aide · machine", `personalAssistant.ts:101`) has no callers. [V]
- **iOS:** it keeps a single `model.aide` (`AppModel.swift:720`) with a machine subtitle (`DrawerView.swift:74`). [V]
- **By design?** Yes. Multiple assistants per fleet, one per machine, never merged, is the intent stated in comments and copy (`packages/shared/src/personalAssistant.ts:1-6`, `PERSONAL_ASSISTANT_PRIVATE_MESSAGE` at `:54`). [V]

## 3) Memory sync

- **Storage:** project memory lives in the server SQLite (`statev2`), in tables `project_memory` and `project_memory_revisions` (`ProjectWorkspaceService.ts:335-420`). [V]
- **Linked history:** per-file history and tombstones are in `<stateDir>/linked-memory/<hash>.json`, owner-only (`docs/studio/logical-projects.md:93`). [V]
- **Who syncs:**
  - `LinkedPeerSync.ts` runs server-to-server. Of each pair, the server with the lower `environmentId` drives, every 60 s, using digests then content (`LinkedPeerSync.ts:1-30`, `logical-projects.md:53-59`). [V]
  - The app also drives pairs the servers have not synced recently, through `projectLink.memoryExport` and `memoryMerge`. [V]
  - Merges use history and three-way logic in `linkedMemoryMerge.ts` and `linkedMemoryThreeWay.ts`. [V]
- **Transport:**
  - Calls go over the handoff peer route (`handoff/handoffPeers.ts`) and need a work grant on the peer. [V]
  - Allowed addresses are a Tailscale `*.ts.net` HTTPS name or a SpecWithCode Connect managed endpoint, never plain HTTP (`fleet/fleetOrigin.ts:1-7`). [V]
  - Over Tailscale the token is a plain bearer; over Connect it must be DPoP-bound (`fleet/fleetTransport.ts:7-11`). [V]
  - In transit this is TLS or WireGuard, or the Cloudflare tunnel for Connect (`docs/studio/security.md:15-18,51`). [V]
  - At rest there is no encryption: plain SQLite, with no SQLCipher or `PRAGMA key` anywhere in `apps/server`. [V]
- **Who can read project memory:**
  - Agent threads only read their own project's memory ("Project memory is scoped to the calling thread's project", `mcp/toolkits/projectMemory/handlers.ts` `boundProject`). [V]
  - Remote machines read only projects their work grant covers (`assertProjectReadable`). [V]
  - Knowledge indexes memory files plus `.specweave/` library folders (`docs/studio/project-knowledge.md:43-45`). [V]
- **Aide memory never syncs:**
  - `LinkedMemorySync.ts:266,475` fail `not_code_project` for a personal project. [V]
  - `LinkedPeerSync.ts:266,990` and `LinkedPeerRoute.ts:139` skip it. [V]
  - `ProjectLink.ts:196-197,500` refuse linking or reading goal, instructions and notes from another machine. [V]
  - Handoff, migrate and moves are refused too (`mcp/toolkits/orchestrator/migrate.ts:259-267`, `HandoffMoves.ts`). [V]
- **What "memory about you" is:** the same `project_memory` table, holding `user_<subject>.md` files per the coordinator prompt (`ProjectWorkspaceService.ts:213`). The UI says "It stays on this machine" (`ProjectMemory.tsx:321`). [V]
- **Where the rest lives:**
  - Topics are ordinary threads with relabelled wording (`assistantTerms.ts`). [V]
  - Briefings are scheduled tasks created by `AideBriefingSetup.ts` and stored in the database. [V for the setup; I for the database storage]
  - Services tab entries are `project_connections` rows, with tokens in ServerSecretStore keyed per project (`ProjectConnectionService.ts:76-120,302`). [V]
  - Google: the refresh token, client and state (including per-project service grants) are secrets `google-refresh-token[-id]`, `google-oauth-client` and `google-account-state` (`integrations/google/GoogleAccountService.ts:92-107`). [V]
  - All of this is machine-local. [V]

## 4) Protection boundaries

- **Chat boundary:** `personalChatBoundary.ts:11-45` stops generic agent sends (thread send/create, attachments, queue edits, delegate) from a different project into or out of a personal project. Same-project calls and external clients with no agent thread are exempt. Callers include `OrchestratorMcpService.ts:1504,1590,2286`, `thread/handlers.ts:99,146,212`, `attachment/handlers.ts:47` and `project/handlers.ts:512`. [V]
- **Outgoing work:** only the explicit `studio_project_route` with a `userAsked` quote (`project/route.ts:54-72`; `docs/studio/aide-chat-separation.md`). [V]
- **Work grants:**
  - `projectInGrant` returns false for a personal project, whatever the grant says (`fleet/workGrantPolicy.ts:204-225`). [V]
  - The grants snapshot never lists it (`workGrantsSnapshot.ts:36-47`). [V]
  - `refuseMachinePrivate` refuses any tool for a personal project under another machine's grant (`mcp/workGrantAccess.ts:324-342`), and outgoing sends from Aide to another machine are refused (`:345-362`). [V]
  - Remote personal creates are refused (`project/handlers.ts:871-876`). [V]
  - So workers and coordinators on other fleet machines cannot read Aide data. [V]
- **Same-machine coordinators of other projects:** they cannot read Aide memory (memory is caller-scoped) or post into its chat. [V]
- **Gaps:**
  - Reading Aide threads from a same-machine code project through `studio_thread_read` is not covered by the boundary, since the guard applies to sends only. [I]
  - An external MCP client with no caller thread passes the memory scope check. [I, from the `context.caller &&` condition]
  - A UI client paired with management credentials (desktop, browser, iPhone) can view any machine's Aide. That is exactly why other machines' assistants are listed. "Private" means not replicated, not invisible to the owner's paired clients. [I]
- **Secrets:** ServerSecretStore writes plaintext `<stateDir>/secrets/<name>.bin`, with the directory at 0700 and files at 0600 (`auth/ServerSecretStore.ts:186-197,246,283-287`). [V] There is no Keychain or DPAPI and no encryption. The only Keychain use is reading Cursor's login (`provider/cursorKeychainToken.ts`). [V] On Windows, chmod is largely a no-op, so the files rely on the user profile's permissions. [I]

## 5) Where "Aide" appears

**Default name constant:** `DEFAULT_PERSONAL_ASSISTANT_NAME = "Aide"` at `packages/contracts/src/project.ts:119`. It is used in `web/src/studio/projectCreation.ts:54` (empty name becomes "Aide"), `CommandPalette.tsx:3676` ("Name your assistant, or keep Aide") and `ProjectCreation.tsx:137`. [V]

**Name storage:** the name is the project `title` (`projection_projects.title`). There is no `assistantName` or is-default flag, so a custom name can only be told from the default by comparing the title to "Aide". [V]

**User-visible web strings that hardcode "Aide" instead of the title** [V]:
- `studio/assistantTerms.ts:8`: "Ask Aide anything", used by `StarterSuggestions.tsx:103`.
- `studio/assistantTerms.ts:11`: "the coordinator" is rewritten to "Aide".
- `AssistantServices.tsx:294`: "What Aide may use".
- `AssistantServices.tsx:352`: "The accounts Aide may use…".
- `ProjectMemory.tsx:321`: "What Aide knows about you…".
- `ProjectWorkspaceSurface.tsx:885`: "Ask Aide for a new topic…".
- `settings/AideSetting.tsx:28`: "Show Aide, a private assistant…".
- `BrowserExtensionSettings.tsx:395`: "Every chat, project thread and Aide on {machine}…".

**i18n:** `apps/web/src/i18n/phrases/{de,es,fr,ja,ko,pt,ru,zh}.ts` contain only the last two strings above (for example `ru.ts:550,1110`). The `fr.ts:141` hit is "Aider", which is unrelated. [V]

**Server text the agent or user can see** [V]:
- `mcp/personalChatBoundary.ts:7,9`: refusal messages.
- `ProjectService.ts:84`: "The personal assistant is turned off…". This one does not use the word Aide.
- `AideBriefingSetup.ts` and `routineTemplates`: no literal "Aide".

**iOS user-visible strings** [V]:
- `DrawerView.swift:74`, `SidebarView.swift:363` and `ColumnHeader.swift:53` use the literal "Aide" as the row or header title, so a renamed assistant still shows "Aide". That is a bug.
- `ShellSummaries.swift:627`: "Aide" as the fallback for an empty title.
- `LiveEngine+Settings.swift:142`: creates the assistant with name "Aide".
- `RootView.swift:245,292-302`: "Set up Aide", "Aide is your personal assistant…".
- `ChatView.swift:405,920`: "Ask Aide anything…".
- `PairWelcomeView.swift:53`: "Talk to Aide…".
- `SyncError.swift:59-63`.
- `DrawerContainer.swift:433-451` and `ProjectAvatar.swift:254`: preview and sample code.
- `FixtureEngine.swift`: fixtures only.

**Desktop:** no Aide strings in `apps/desktop/src`. [V]

**Internal identifiers that should not be renamed:**
- Settings key `aideEnabled` (contracts `settings.ts:1848`, iOS `AideSetting.swift`, `SWCWire/Settings.swift`).
- Hooks `useAideEnabled` and `useAideSettingSettled`.
- `visibleWithAide*`, `threadsVisibleWithAide`, `hiddenAideRoute.ts`, `useHiddenAideRoute` and `useHiddenAideThread`.
- `AideSetting.tsx` and `AideBriefingSetup.ts`.
- Scheduled-task `withAideSetting`.
- iOS `ChatTarget.aide` and `model.aide`.
- `kind:"personal"` and the error reason codes.
- Test fixtures in `apps/web/tests/aide-per-machine` and the iOS tests. [V]

**Repository docs:** `docs/studio/aide-chat-separation.md`, `docs/studio/google-account.md`, `docs/studio/project-orchestration.md`, `docs/research/coordinator-readiness-1022.md`, `apps/ios/README.md`, `apps/ios/docs/ARCHITECTURE.md`, `apps/ios/docs/IPHONE-DUO.md` and `apps/ios/docs/app-store.md`. [V]

**docs-site (`/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave/docs-site`):** no page uses the word "Aide". The only related page is `docs/studio/projects.md:24-28` ("Personal projects…", "our version of a personal assistant workspace"). The `i18n/fr/code.json` hit is French "Aide" (help), which is unrelated. [V]
**Bottom line:** the design's diagnosis of the Windows assistant holds up, but four of its plan details are wrong for HEAD `76b2dd433f`:

- **Empty name:** an empty assistant name can't reach the server. `projects.createNew` rejects it, so this needs a contract change, which contradicts "no schema change".
- **Migration marker:** there is no server-state store to hold `migrations.percyRename`.
- **Wrong citation:** the guard lines it cites are an error class.
- **Missed strings:** the rename list misses all of Android plus about 12 iOS strings.

Everything below was read directly in code or the live DB (VERIFIED) unless marked INFERRED.

## A) Current behavior

| Claim | Verdict | Evidence |
|---|---|---|
| Guard at `ProjectService.ts:517` | CONFIRMED | `const assistant = createsPersonalAssistant(command) ? machineAssistantOf(...)` at `apps/server/src/project/ProjectService.ts:517-519` |
| Guard at `ProjectCommands.ts:195-206` | WRONG | Those lines only declare `PersonalAssistantExistsError`. The check that fires is at `apps/server/src/orchestration-v2/ProjectCommands.ts:649-660`. |
| "Ran `project.create kind:personal`" | WRONG (incomplete) | Web (`apps/web/src/hooks/useNewProject.ts:49,103`) and iOS (`LiveEngine+Settings.swift:142`, `Rpc.swift:42`) call the RPC `projects.createNew`. It goes to `ManagedProjectFolders.createNamedProject`, which hands back an existing assistant without an error (`apps/server/src/project/ManagedProjectFolders.ts:658-660`) and only then dispatches the create (`:688-694`). That is the first guard. `ProjectCommands` is a backstop. |
| One assistant per server DB, which means per machine (`shared/personalAssistant.ts:1-6,37`) | CONFIRMED | Doc comment at 1-6, `machineAssistantOf` at 37-51. The local M4 DB has one live personal project, "Aide" (`5428ab1e…`, created October 10, 2026). The Windows cause is INFERRED, since the Windows DB wasn't queried. |
| No merge, no sync (`LinkedMemorySync.ts:266,475`, `LinkedPeerSync.ts:266,990`, `ProjectLink.ts:196-197,500`) | CONFIRMED | Every cited line refuses personal projects. `LinkedPeerRoute.ts:139` also refuses them. |
| Sidebar ranking (`StudioSidebar.tsx:855-876`) | CONFIRMED | Rank: own 0, other 1, extras +2 (`:860-866`). The machine label appears only when `environments.length > 1` (`:868-876`). |
| "Set up here" whenever this machine has no assistant (`StudioSidebar.tsx:914-922`, `personalAssistant.ts:59`) | CONFIRMED, two caveats | Line 59 is in `apps/web/src/studio/personalAssistant.ts`. The shared file is only 55 lines. Also gated on `aideEnabled` (`:915`). The label is "Set up here" only when more than one environment is connected, otherwise "Set up" (`:983`). |
| The only explanation is `DraftMachinePicker.tsx:485-488` | WRONG | The same constant also appears in `CommandPalette.tsx:2515`, `OtherMachineAssistantNotice.tsx:11` and the sidebar tooltip at `StudioSidebar.tsx:970`. It is defined at `apps/web/src/studio/personalAssistant.ts:17-18`. |

## C) Citations in the recommended design

**Confirmed:**
- `fleetOrigin.ts:1-7` and `fleetTransport.ts:7-11`: Tailscale `*.ts.net` or Connect with DPoP.
- `workGrantPolicy.ts:204-225`: `projectInGrant` returns false for personal projects at `:224`.
- `refuseMachinePrivate` at `mcp/workGrantAccess.ts:324-329`.
- `personalChatBoundary.ts:11-45`.
- The memory scope gap: `if (context.caller && context.caller.projectId !== projectId)` at `mcp/toolkits/projectMemory/handlers.ts:19`.
- The personal-thread read gap:
  - `studio_thread_read` (`mcp/toolkits/orchestrator/handlers.ts:223`) only calls `guardThread` (`:46-60`), which returns early when there is no work grant.
  - `studio_thread_search` (`mcp/toolkits/thread/handlers.ts:159-184`) has no same-machine personal filter.
- Google secret names at `GoogleAccountService.ts:92-107`.
- `apps/web/tests/aide-per-machine` exists.
- `assistantDisplayTitle` is unused outside its definition at `apps/web/src/studio/personalAssistant.ts:101`.

**Partly right:**
- `ServerSecretStore.ts:186-197` covers creating the 0700 directory. The 0600 `.bin` writes are at `:246`, `:283` and `:287`.
- `ProjectWorkspaceService.ts:335-420` holds the `project_memory` queries, but the table is defined in `persistence/Migrations/059_ProjectWorkspace.ts`. T-10 needs a new numbered migration. Live columns are `project_id`, `name`, `content`, `revision`, `updated_at` and `byte_length`.

## E) Rename claims

| Claim | Verdict | Evidence |
|---|---|---|
| `project.ts:119` `= "Percy"` | WRONG (the current value) | Today it reads `"Aide"`. It is consumed only on the web, at `projectCreation.ts:54`, `CommandPalette.tsx:3676` and `ProjectCreation.tsx:137` (those are CONFIRMED). The server never applies a default. |
| The server maps an empty name to the default, and iOS sends `""` (`LiveEngine+Settings.swift:142`) | WRONG as designed | `ProjectCreateNewInput.name` is `TrimmedNonEmptyString` (`packages/contracts/src/project.ts:832`) and `ProjectCreatePayload.title` is the same type (`:217`). A schema change is needed. An iOS build sending `""` would also be rejected by every older server. iOS should send `"Percy"` instead, and the server mapping should cover only `"Aide"`. |
| The migration dispatches `project.update` | WRONG (detail) | A rename runs as the server command `project.meta.update` (`ProjectCommands.ts:260-266`) and goes through `findNameOwner` (`ProjectService.ts:467-492`). If an existing project is already named "Percy", the rename can be refused. Needs a test (INFERRED). |
| The `migrations.percyRename` marker in server state needs no schema change | WRONG / UNVERIFIED | The live DB has no key-value or server-state table. The only state tables are `projection_state`, `orchestration_v2_projection_metadata`, `team_rules_settings_changes` and `effect_sql_migrations`. Either a numbered migration provides the one-shot marker, or a settings field has to be added. |
| `assistantTerms.ts:8,11` used by `StarterSuggestions.tsx:103` | CONFIRMED but understated | `paneWords` (the `the coordinator`→`Aide` rule at `:11`) is also used by `ThreadsPane.tsx:38`, `ProjectThreadHeader.tsx:54`, `ProjectPaneBar.tsx:30` and `ProjectExecutionHistory.tsx:2`. All of them need the name argument. |
| `AssistantServices.tsx:294,352`, `ProjectMemory.tsx:321`, `ProjectWorkspaceSurface.tsx:885`, `AideSetting.tsx:28`, `BrowserExtensionSettings.tsx:395` | CONFIRMED | |
| i18n: two strings per locale (e.g. `ru.ts:550,1110`); leave `fr.ts:141` | CONFIRMED | The other web Aide strings ("Ask Aide anything", Services, Memory, topic prompt) have no translations, so AC-05 covers only these two. |
| `personalChatBoundary.ts:7,9` | CONFIRMED | Those are the only user-visible server "Aide" strings. The rest are comments: `ScheduledTaskAdmission.ts:17,18,72`, `ManagedProjectFolders.ts:103,157`, `ProjectService.ts:82,88,675`, `ScheduledTaskService.ts:252`. |
| Coordinator prompt near `ProjectWorkspaceService.ts:213` | CONFIRMED: no literal name | The personal block at `:212-222` says "You are the user's personal assistant". It does not inject the title. |
| iOS `DrawerView:74`, `SidebarView:363`, `ColumnHeader:53`, `ShellSummaries:627`, `LiveEngine+Settings:142`, `RootView:245,292-302`, `ChatView:405,920`, `PairWelcomeView:53`, `SyncError:59-63`, `DrawerContainer:433-451`, `ProjectAvatar:254` | CONFIRMED | |
| Desktop: no strings | CONFIRMED | Only built files in `apps/desktop/dist-electron/*.map`. |
| docs-site `docs/studio/projects.md:24-28` | WRONG repo | It lives in the specweave repo: `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave/docs-site/docs/studio/projects.md`. Lines 24-28 are the "Personal projects" section, which never says "Aide". |
| Repo docs list | CONFIRMED, incomplete | Missing `apps/android/README.md` and `CHANGELOG.md:23,26,27` (the changelog can stay as history). |
| Identifiers to keep exist (`AideSetting.swift`, `ChatTarget.aide`, `model.aide`, `hiddenAideRoute.ts`, …) | CONFIRMED | |

## User-visible "Aide" strings the plan missed

**iOS:**
- `SidebarView.swift:374-375`: "Set up Aide", plus the avatar title.
- `DrawerView.swift:85` "Set up Aide", `:86` and `:102` avatar title "Aide", `:106` "Aide appears when your machines reconnect".
- `Handoff.swift:96,162`: "Aide stays private to its machine and cannot be handed off."
- `Overview/ProjectOverviewView.swift:260`: "Topics you ask Aide for show up here."
- `SWCSync/FixtureEngine.swift:470,473,477,478,946,1008`. These are user-visible: an unpaired user sees the sample model (`AppBootstrap.swift:45`), including "Hi, I'm Aide…".

**Android** (the plan misses it entirely):
- `sync/ShellSummaries.kt:443`: fallback title "Aide".
- `sync/LiveEngine.kt:244`: "Set up Aide in SpecWithCode on your computer."
- `sync/SyncError.kt:20,23,27`.
- `sync/FixtureSample.kt:31`.
- `sync/FixtureEngine.kt:348,350,357,362`.
- Test fixtures to update: `wire/src/test/resources/fixtures/{shellItems,rpcPayloads}.json`, `FixtureDecodeTest.kt`, `CommandEncodeTest.kt`, `FixtureEngineTest.kt`.

**Web:** the comment example at `apps/web/src/studio/personalAssistant.ts:100` (cosmetic), and the description at `packages/contracts/src/settings.ts:1844`.
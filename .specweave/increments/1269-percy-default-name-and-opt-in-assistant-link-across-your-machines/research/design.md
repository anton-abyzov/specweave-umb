# Percy: assistant scope across machines, and the rename from Aide

Code references point to `specwithcode-dev` at `76b2dd433f`. Paths are relative to that repo.

## A) Current behavior

When you named the assistant on Windows, the app ran `project.create kind:"personal"` against the Windows server. That server's database had no personal project, so the one-per-machine guard in `ProjectService.ts:517` and `ProjectCommands.ts:195-206` did not fire, and Windows created its own assistant. This is intended: the rule is one assistant per server database, which means one per machine (`packages/shared/src/personalAssistant.ts:1-6,37`). Assistants are never merged, and their data never syncs between machines (`LinkedMemorySync.ts:266,475`, `LinkedPeerSync.ts:266,990`, `ProjectLink.ts:196-197,500`). The sidebar collects personal projects from every connected machine and ranks them: this machine's, then other machines', then extras (`StudioSidebar.tsx:855-876`). Once more than one machine is connected, each row carries the machine label. "Set up here" appears whenever the current machine has no assistant, even if another machine's assistant is already in the list (`StudioSidebar.tsx:914-922`, `personalAssistant.ts:59`). The only place that explains this is one line in the draft machine picker: "Each machine has its own private assistant. Nothing transfers between them." (`DraftMachinePicker.tsx:485-488`).

## B) How Claude and OpenAI do it

| | Claude (claude.ai, Desktop) | Claude Code / Cowork | ChatGPT | Codex | SpecWithCode today |
|---|---|---|---|---|---|
| Memory scope | Account, plus a separate memory per project | Per repo or per account/org folder | Account, plus `memory_scope` per project | Per machine (`~/.codex/memories`) | Per machine (one personal project) |
| Sync | Server, follows sign-in | Local by default. Server sync exists but is flag-gated | Server | None | None for personal data |
| Local-only option | Incognito, per-chat off, "Use account memory" off per project | Local is the default | Temporary Chat, project-only memory | Everything is local | Everything is local |
| Protection at rest | Server-side. OAuth tokens in Keychain via safeStorage | Memory in plaintext `.md`. Tokens in Keychain | Server-side. Legacy app cache encrypted. EKM for Enterprise | Plaintext `.md` and SQLite. `auth.json` plaintext (keyring optional) | Plaintext SQLite. Secrets in 0600 `.bin` files |
| Second device | Same assistant after sign-in | Starts empty until files are copied or sync is on | Same assistant after sign-in | Starts empty | New, separate assistant |
| Isolation | Project memory never reads other projects | Secret scan blocks synced writes | Project-only memory blocks moves in and out | None | Strong: `personalChatBoundary`, grants refuse personal projects |

**What to take from this:** both vendors keep one identity per person, and that identity syncs only through their own server. Their local agent memory stays on the machine unless the user opts in. Tokens never travel; they sit in the OS keystore. SpecWithCode has no account server, so the equivalent is an opt-in link between the person's own machines, built on the existing peer sync. Personal data should travel only after explicit consent and only in categories the user chose, and secrets stay on the machine that holds them.

## C) Recommended design

**Identity.** Keep one personal project per machine as the storage unit, since every guard already assumes that. Add an opt-in *personal link* that groups several machines' assistants into one Percy for the same person. Linked assistants show as one sidebar row with machine chips. Assistants that are not linked keep the current per-machine rows.

**Opt-in flow.**
- **At setup on a new machine:** when another connected machine already has an assistant, the setup step (`apps/web/src/studio/personalAssistant.ts:79-98`) and iOS `RootView.swift:292-302` ask: "Use Percy from Mac" or "Start a separate assistant here". Neither option is preselected. Choosing the first still creates the local personal project, then requests the link.
- **Later:** add a "Link with Percy on <machine>" action in the assistant's settings, and a one-time card when two assistants from different machines are visible.
- **Consent on both ends:** the target machine has to approve, like `studio_project_link_accept`. A work grant is never enough.

**What is shared and what stays local:**

| Item | Linked default | Mechanism |
|---|---|---|
| Name and icon | Shared | Project title and icon via the link, last-writer-wins |
| Memory about you (`user_*.md` in `project_memory`) | Shared | `LinkedPeerSync` plus `linkedMemoryMerge.ts`/`linkedMemoryThreeWay.ts`, filtered to shareable files |
| Goal, instructions, notes | Shared | The existing `ProjectLink` paths, opened for `link.kind="personal"` |
| Topics and chat history | Local | Not synced. Other machines' topics can be listed read-only through the paired UI as they are today |
| Routines and briefings (`AideBriefingSetup.ts`) | Local | They run on the machine that created them, so briefings are never duplicated |
| Services tab entries and tokens (`project_connections`, ServerSecretStore), Google tokens and state (`GoogleAccountService.ts:92-107`) | Local, never sent | Excluded at the export layer, not only by the filter |
| Files and attachments | Local | Not synced |

**Data protection:**
- **In transit:** unchanged. Tailscale `*.ts.net` HTTPS or Connect with DPoP (`fleet/fleetOrigin.ts:1-7`, `fleet/fleetTransport.ts:7-11`).
- **Grant scope:** add a separate grant scope, `personal-link:<projectId>`. `projectInGrant` stays false for personal projects under any work grant (`fleet/workGrantPolicy.ts:204-225`). Only `LinkedPeerRoute` honors the new scope, and only for the memory export and merge calls. No tool access comes with it, so `refuseMachinePrivate` (`mcp/workGrantAccess.ts:324-362`) stays as it is.
- **Who can read:** coordinators and workers of other projects and other machines get nothing new. `personalChatBoundary.ts:11-45` stays unchanged.
- **Gaps to close:**
  - Make `studio_thread_read` and thread search refuse personal threads when the caller belongs to a different project.
  - Make the memory scope check deny a call with no caller thread unless the client holds management credentials. Today it is skipped by `context.caller &&`.
- **Secrets at rest:** wrap ServerSecretStore with an OS keystore key: Keychain on macOS, DPAPI on Windows, libsecret on Linux. Fall back to today's 0600 files and log a warning (`auth/ServerSecretStore.ts:186-197`). Secrets never enter link exports. Add an export-time assertion and a test for it.
- **Memory at rest:** SQLite stays plaintext and relies on FileVault or BitLocker. Settings shows a warning when disk encryption is off.
- **Per-item flag:** add `localOnly` on `project_memory` rows, with a "Keep on this machine" toggle in `ProjectMemory.tsx`. The digest and export skip those rows. Turning the flag on later sends a tombstone through linked history, so peers drop their copy.
- **Unlink:** stops sync right away and revokes the `personal-link` scope on both sides. Each machine keeps its current copy. Optionally, "Forget memory that came from <machine>" deletes rows whose last origin is that peer (the linked-history JSON already records origin).

**Migration for installs that already have two assistants.** Nothing changes until the user acts. The one-time card offers "Link Percy on Mac and Windows". On link:
- The user picks which name and icon to keep.
- Memory runs a three-way merge with an empty base. A file that differs on both sides is kept twice, as `name.md` and `name (Windows).md`. Nothing is deleted or overwritten.
- Topics, routines and connections stay where they are.
- Duplicate personal projects on one machine (extras from before the rule) are not touched.

**Settings that stay adjustable:**
- `aideEnabled` per machine, unchanged.
- Per link, toggles for which categories sync: name/icon, memory about you, instructions.
- `localOnly` per memory item.
- Unlink, and forget one machine's contributions.
- Several unlinked assistants remain allowed, for example a work laptop kept apart.

## D) Decisions for Anton

1. **What a new machine's setup asks.** (a) Today's behavior: always a separate assistant, with linking only later. (b) Ask "Use Percy from <machine>" or "Separate", with no default. (c) Link automatically. **Recommend (b).** It is opt-in and visible, and it removes the surprise you hit on Windows.
2. **What syncs once linked.** (a) Name only. (b) Name, icon, memory about you and instructions. (c) Also topics and chat history. **Recommend (b).** Chats can contain machine-specific paths and secrets, and syncing them would turn this into a merge problem for threads.
3. **Encryption at rest.** (a) Leave it to FileVault/BitLocker. (b) Keystore-wrapped secrets, plus a warning when disk encryption is off. (c) Also encrypt the personal memory tables (SQLCipher). **Recommend (b).** It covers the tokens, which are the dangerous part, without migrating the database.
4. **Routines and briefings when linked.** (a) Stay on the machine that created them. (b) One "home machine" runs them for the linked Percy. **Recommend (a)** for now, with each routine row labeled by its machine.

## E) Percy rename

**Risk:** low. Keep "Percy" an in-app default name the user can rename. Never market it as a product, never write "Percy by SpecWithCode", and avoid visual-testing wording or iconography next to it (BrowserStack sells a visual-testing product named Percy).

**Strings to change.** Replace the hardcoded name with the assistant's title. Use "Percy" only as the default constant.
- **Default constant:** `packages/contracts/src/project.ts:119` `DEFAULT_PERSONAL_ASSISTANT_NAME = "Percy"`. This flows into `apps/web/src/studio/projectCreation.ts:54`, `apps/web/src/components/CommandPalette.tsx:3676` and `apps/web/src/components/studio/ProjectCreation.tsx:137`.
- **Web, switched to the `{name}` title:**
  - `apps/web/src/studio/assistantTerms.ts:8,11`, used by `apps/web/src/components/studio/shell/StarterSuggestions.tsx:103`
  - `apps/web/src/components/studio/AssistantServices.tsx:294,352`
  - `apps/web/src/components/studio/ProjectMemory.tsx:321`
  - `apps/web/src/components/studio/ProjectWorkspaceSurface.tsx:885`
  - `apps/web/src/components/settings/AideSetting.tsx:28`. This is the settings toggle with no single assistant in scope, so it says "your assistant (Percy by default)".
  - `apps/web/src/components/settings/BrowserExtensionSettings.tsx:395`
  - i18n: `apps/web/src/i18n/phrases/{de,es,fr,ja,ko,pt,ru,zh}.ts`. Two strings each, with `{name}` interpolation (e.g. `ru.ts:550,1110`). Leave `fr.ts:141` ("Aider") alone.
  - Optional: wire up the unused `assistantDisplayTitle` (`apps/web/src/studio/personalAssistant.ts:101`) so its format is "<title> · <machine>".
- **Server:** `apps/server/src/mcp/personalChatBoundary.ts:7,9` should say "the personal assistant" instead of "Aide". Check the coordinator prompt near `apps/server/src/project/ProjectWorkspaceService.ts:213` for a literal name.
- **iOS:**
  - `apps/ios/SWCKit/Sources/SWCFeatures/Drawer/DrawerView.swift:74`, `.../Drawer/SidebarView.swift:363` and `.../Drawer/ColumnHeader.swift:53` must use the title. This also fixes the existing bug where a renamed assistant still shows "Aide".
  - `apps/ios/SWCKit/Sources/SWCSync/ShellSummaries.swift:627`: change the fallback to "Percy".
  - `apps/ios/SWCKit/Sources/SWCSync/LiveEngine+Settings.swift:142`: send an empty name so the server applies the default.
  - `apps/ios/SWCKit/Sources/SWCFeatures/RootView.swift:245,292-302`, `.../Chat/ChatView.swift:405,920`, `.../Pairing/PairWelcomeView.swift:53` and `apps/ios/SWCKit/Sources/SWCSync/SyncError.swift:59-63`.
  - Previews only: `DrawerContainer.swift:433-451` and `ProjectAvatar.swift:254`.
- **Desktop:** no strings.
- **Docs:**
  - `docs/studio/aide-chat-separation.md` (keep the file name), `docs/studio/google-account.md` and `docs/studio/project-orchestration.md`
  - `apps/ios/README.md`, `apps/ios/docs/ARCHITECTURE.md`, `apps/ios/docs/IPHONE-DUO.md` and `apps/ios/docs/app-store.md`
  - docs-site `docs/studio/projects.md:24-28`: mention "your assistant (default name Percy)".
  - Leave `docs/research/coordinator-readiness-1022.md` as it is, since it is a historical record.

**Identifiers to keep:** `aideEnabled`, `useAideEnabled`, `useAideSettingSettled`, `visibleWithAide*`, `threadsVisibleWithAide`, `hiddenAideRoute.ts`, `useHiddenAideRoute`, `useHiddenAideThread`, `AideSetting.tsx`/`.swift`, `AideBriefingSetup.ts`, `withAideSetting`, `ChatTarget.aide`, `model.aide`, `kind:"personal"`, the error reason codes, and test fixtures in `apps/web/tests/aide-per-machine`.

**Migration rule.** A personal project whose title is exactly `"Aide"` after trimming whitespace is treated as having the default name. Any other title is a custom name and stays as it is.
- On startup, the server runs a one-time migration that dispatches `project.update title:"Percy"` for each such project, so the change goes through the normal event log.
- It records `migrations.percyRename=done` in server state. A user who later renames the assistant back to "Aide" is therefore not reverted.
- During a transition window, the server also maps a `project.create kind:"personal"` with an empty name, or with the literal `"Aide"` from clients older than the fix, to "Percy". This covers older iOS builds that still send "Aide".
- There is no default/custom flag today. Exact-match plus the one-shot marker is enough, so no schema change is needed.

## F) Acceptance criteria and tasks

**Phase 1: Percy rename (ships on its own)**
- **AC-01:** a new assistant with an empty name gets the title "Percy" on web, desktop and iOS.
- **AC-02:** after upgrade, an existing personal project titled "Aide" shows "Percy" on every client. A custom-named one keeps its name.
- **AC-03:** the migration runs once. Renaming back to "Aide" after it ran persists across restarts.
- **AC-04:** no user-visible web, iOS or server string hardcodes "Aide". A renamed assistant's name appears in starter text, Services, Memory, the topic prompt and iOS drawer/sidebar/header rows.
- **AC-05:** the eight locales show the assistant's name through interpolation.
- **AC-06:** settings keys and internal identifiers are unchanged. Existing `aideEnabled` values survive.

**Phase 2: hardening (no sharing yet)**
- **AC-07:** `studio_thread_read` and search from a different project's agent thread on the same machine are refused for personal threads.
- **AC-08:** a memory call with no caller thread is denied unless the client holds management credentials.
- **AC-09:** where a keystore exists, ServerSecretStore writes keystore-wrapped secrets and transparently re-wraps existing `.bin` files. It falls back to the current behavior with a logged warning.
- **AC-10:** Settings warns when disk encryption is off.

**Phase 3: opt-in personal link**
- **AC-11:** setup on a machine whose fleet already has an assistant offers "Use Percy from <machine>" and "Separate", with no default.
- **AC-12:** a link needs approval on the target machine and grants only `personal-link:<projectId>`. Work grants still exclude personal projects.
- **AC-13:** once linked, the name, icon, `user_*.md` memory and instructions converge within 2 sync cycles. Topics, routines, connections, tokens and files never leave their machine. An export test asserts no secret names or connection rows are present.
- **AC-14:** a `localOnly` memory item is never exported. Setting the flag after a sync removes the peer's copy.
- **AC-15:** linking two existing assistants loses no file. Conflicts appear as `name (Machine).md`.
- **AC-16:** unlink stops sync and revokes the scope on both sides. Each side keeps its data. "Forget from <machine>" removes only rows that came from that peer.
- **AC-17:** linked assistants render as one sidebar row with machine chips. Unlinked ones render as today.

**Tasks**
- **T-01:** change the constant (`packages/contracts/src/project.ts:119`), add the server create mapping, and add tests.
- **T-02:** add the one-shot title migration in the server startup migrations with its marker, and a test for the rename-back case.
- **T-03:** switch the web strings to the title in the files listed in E, plus `assistantTerms.ts` taking a name argument.
- **T-04:** update the i18n phrase files in the eight locales.
- **T-05:** iOS: use the title in `DrawerView.swift:74`, `SidebarView.swift:363` and `ColumnHeader.swift:53`. Update the fallback, the create name and the copy in `RootView`, `ChatView`, `PairWelcomeView` and `SyncError`. Update the tests.
- **T-06:** server copy in `personalChatBoundary.ts:7,9` and the coordinator prompt check, plus the repo docs and docs-site `projects.md`.
- **T-07:** add the read guard for personal threads in the thread read and search handlers, and tighten the memory scope check in `mcp/toolkits/projectMemory/handlers.ts`.
- **T-08:** keystore wrapping in `auth/ServerSecretStore.ts` (Keychain, DPAPI, libsecret) with migration and fallback.
- **T-09:** add a disk-encryption status check and the Settings warning.
- **T-10:** add the `localOnly` column on `project_memory` (`ProjectWorkspaceService.ts:335-420`) and the toggle in `ProjectMemory.tsx`.
- **T-11:** add `link.kind="personal"`. Allow it in `ProjectLink.ts:196-197,500`, `LinkedMemorySync.ts:266,475`, `LinkedPeerSync.ts:266,990` and `LinkedPeerRoute.ts:139`, gated on the scope and the shareable-file filter.
- **T-12:** add the `personal-link` grant scope in `fleet/workGrantPolicy.ts` and `workGrantsSnapshot.ts`, honored only by `LinkedPeerRoute`.
- **T-13:** add an export allowlist and a no-secrets assertion test.
- **T-14:** setup choice in `apps/web/src/studio/personalAssistant.ts` and iOS `RootView.swift`. Add the link action and the one-time card in `StudioSidebar.tsx:855-922`. Update the `DraftMachinePicker.tsx:485-488` copy.
- **T-15:** link migration (empty-base merge, conflict file naming), unlink, and forget-from-peer.
- **T-16:** e2e tests in `apps/web/tests/aide-per-machine` for link, unlink and conflict.

Phase 1 (T-01 to T-06) is one small increment with no schema change. Phases 2 and 3 depend on decisions 1 to 3 in section D.
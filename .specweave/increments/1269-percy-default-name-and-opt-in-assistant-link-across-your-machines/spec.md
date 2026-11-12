# Percy: one assistant per person, a seat on each machine

## Problem

Anton, November 12, 2026: rethink the personal assistant across several machines. Several assistants on one machine should not be possible, and a fresh install should set the assistant up in one or two steps and join the person's existing one.

History: one private assistant per machine (October 20, 0981); "threads and orchestrator per machine, person memory shared" (November 3, never built); Percy as default name and an opt-in link (November 9). Seen since: naming the assistant on Windows made a second one; Minisforum nags "Set up here" although the M4 has Percy; on a fresh 1.0.233 install the iPhone drawer said "Aide" after the user named it "Percy".

Audit of `anton-abyzov/specwithcode` at 1.0.245 (`41df4a13`), November 12, 2026:

**Two assistants on one machine**
- G-01 Blocked in one database. Every create path ends in the decider guard (`apps/server/src/orchestration-v2/ProjectCommands.ts:648-659`) under one lock (`apps/server/src/project/ProjectService.ts:517-558`); kind cannot change (`ProjectCommands.ts:755-757`); there is no undelete.
- G-02 Open: a copied `userdata` folder (backup restore, Migration Assistant, disk clone). `environment-id` is a random file beside the database (`apps/server/src/environment/ServerEnvironment.ts:230-241`), so two machines answer as one and each one's assistant replaces the other in clients.
- G-03 Open: duplicates from before October 20 stay as "extra" rows; the only cleanup is Delete project, which also deletes that copy's memory. iOS shows no "extra" mark.
- G-04 By design: each profile (state dir) on one OS user is its own machine with its own assistant.

**Several machines of one person**
- G-05 No person identity between machines. `cloudUserId` (Connect account) stays local (`apps/server/src/cloud/CloudLink.ts:673,890`); "own machine" is only inferred from invitation pairings (`apps/server/src/fleet/workGrantPolicy.ts:79-96`).
- G-06 Memory about you, instructions, name and icon never sync; every link path refuses personal projects.
- G-07 Two machines with Google connected both create the 08:00 briefing (`apps/server/src/project/AideBriefingSetup.ts:81-113`); a laptop asleep at 08:00 skips it (`apps/server/src/scheduledTasks/Schedule.ts:129-170`) with no other machine taking over.
- G-08 Google needs a full new consent on each machine and nothing says it is already connected elsewhere (`apps/web/src/components/studio/AssistantServices.tsx:359`).
- G-09 Each client picks "the" assistant by a different rule: web prefers this machine (`apps/web/src/studio/personalAssistant.ts:118-138`), iOS the lowest environment id (`apps/ios/SWCKit/Sources/SWCSync/ShellSummaries.swift:114-137`), Android the lowest id among listed machines (`apps/android/sync/src/main/kotlin/com/specwithcode/sync/ShellSummaries.kt:102-152`). No picker on phones.
- G-10 The primary machine's `aideEnabled` hides every machine's assistant in the web (`apps/web/src/hooks/useSettings.ts:433-438`).
- G-11 One Telegram bot token on two machines: one poller wins, the other errors, no handling (`apps/server/src/channels/TelegramChannel.ts:455-480`).
- G-12 The assistant's machine offline or in Away mode: no fallback; the phone says "<Machine> is offline" (`apps/ios/SWCKit/Sources/SWCSync/LiveEngine+Sessions.swift:803-822`); Away keeps the assistant on the sleeping machine (`apps/server/src/away/AwayPlanner.ts:241-242,297-301`).
- G-13 First run never offers the assistant (`apps/web/src/components/onboarding/WelcomeWizard.tsx:339-370`); a machine that joins a fleet does not learn another one has it.

**Protection**
- G-14 Another project's agent on the same machine can read the assistant's threads through `studio_thread_read` and `studio_thread_search` (`apps/server/src/mcp/toolkits/orchestrator/handlers.ts:46-60`, `apps/server/src/mcp/toolkits/thread/handlers.ts:159-185`).
- G-15 A thread-less MCP client can read and write any project's memory, personal included (`apps/server/src/mcp/toolkits/projectMemory/handlers.ts:16-27`).
- G-16 Personal memory is plaintext SQLite and secrets are 0600 files (`apps/server/src/auth/ServerSecretStore.ts`).
- G-17 Unverified: whether a hub-brokered phone code can read another owner's assistant; `phoneMint` has no test (`apps/server/src/fleet/studioFleetHttp.ts:1066-1069`).

Earlier research (REA of Claude Desktop, Claude Code, ChatGPT and Codex) is in `research/`: both vendors keep one assistant per account synced through their server; their local agent memory stays on the machine. SpecWithCode has no account server holding user data, so the equivalent is a link between the person's own machines.

## Concept

One Percy per person. Each of the person's machines holds a **seat**: a local personal project with its own chats, files, service sign-ins and coordinator. Seats of one person form a **group** and share what makes Percy the same assistant.

| | Shared in the group | Stays on its machine |
|---|---|---|
| Identity | name, icon | |
| Knowledge | memory about you, instructions | items marked "Keep on this machine" |
| Work | | chats and topics, files, attachments |
| Services | which Google account is connected (the email only) | OAuth tokens, Telegram token, all secrets |
| Routines | one copy of each personal routine, run by the **home machine** | run history |

- **Home machine:** the seat that runs briefings and messaging and that phones open first. It is the first seat until the person picks another; if it has been offline for 15 minutes, the lowest-id online seat that has the needed sign-in runs due routines and says so.
- **This machine answers** on desktop and web. On a phone the home machine answers; when it is offline the phone offers the next online seat by name.
- **Another person's machine** (shared through a work grant, or another Connect account) is never offered, joined or merged. Its Percy stays its own.
- **Same person** means: machines paired by the owner's own invitation (`grantKindOf` own) and, when both are signed in to Connect, the same `cloudUserId`. A mismatch refuses the join.

**Accounts on one machine** (Anton asked, November 12, 2026)
- A machine belongs to one person: it links to one Connect account, and a second account is refused (`CloudLinkAccountMismatchError`, `apps/server/src/cloud/CloudLink.ts:652-671`). That account is the person Percy belongs to.
- Google accounts are sign-ins Percy uses, not people. One seat can hold several (1217; one refresh token each, `apps/server/src/integrations/google/GoogleAccountService.ts:93-107`), for example the owner's and a spouse's mailbox. All of them serve the owner's Percy; none creates a second assistant, and none is the join identity.
- A phone is a paired device of the person, not an account.
- Another person on the same computer gets their own Percy only with their own OS user or profile (its own state folder, so its own machine identity) and their own Connect account.

**Install from scratch**
1. First run, after "Join my machines" or Connect sign-in: "Your Percy is on <machine>. Use Percy here too" (preselected) or "Start a separate assistant" (under More options). With no Percy anywhere: "Set up Percy" with the name field.
2. Consent on the existing machine: one card, "<new machine> wants to use your Percy: Allow". The invitation can carry it ("Also share Percy", ticked when a person creates the invitation in Settings > Machines), which makes step 1 the only step.

No agent, MCP tool or work grant can request or allow a join.

## Scope

In (`anton-abyzov/specwithcode`, plus `anton-abyzov/specweave` docs-site), in three PRs:

- PR A: Percy default name and title-driven copy everywhere, no setup nag, the read guards (G-14, G-15).
- PR B: person identity, group join with consent, shared name, icon, memory and instructions, the first-run step, one assistant pick rule on every client (G-05, G-06, G-09, G-10, G-13).
- PR C: home machine, one briefing, Google hint, Telegram guard, offline fallback, copied-userdata notice, extras cleanup, Keychain (G-02, G-03, G-07, G-08, G-11, G-12, G-16, G-17).

Out: chats, topics, files and tokens ever leaving their machine; joining across owners; SQLCipher; Windows DPAPI and Linux libsecret (follow-up); a hosted copy of personal memory.

## Acceptance Criteria

### Phase 1: Percy
- [ ] AC-01: A new assistant created from web, desktop, iOS or Android with the suggested name gets the title "Percy". `DEFAULT_PERSONAL_ASSISTANT_NAME` in `packages/contracts/src/project.ts:119` is "Percy"; iOS and Android send "Percy", never an empty name (older servers reject empty names).
- [ ] AC-02: After upgrade, every personal project titled exactly "Aide" (trimmed) is renamed to "Percy" through `project.meta.update`, once. Custom names are untouched. If a project is already named "Percy" the rename is skipped and logged, never failed.
- [ ] AC-03: The one-time list is written by a numbered migration and drained at startup, so a user who renames back to "Aide" afterwards keeps that name across restarts.
- [ ] AC-04: No user-visible web, iOS, Android or server string hardcodes "Aide". Starter text, Services, Memory, topic prompt, pane words (`assistantTerms.ts` and its five callers), handoff refusals, set-up rows, sample (fixture) data and error copy use the assistant's title, or "your assistant" where none is in scope.
- [ ] AC-05: The eight locales interpolate the name in the two translated strings (`apps/web/src/i18n/phrases/*.ts`); `fr.ts:141` "Aider" is unchanged.
- [ ] AC-06: Internal identifiers (`aideEnabled`, `ChatTarget.aide`, `model.aide`, `hiddenAideRoute`, `AideBriefingSetup`, `kind:"personal"`, reason codes, test folders) are unchanged and existing `aideEnabled` values survive.
- [ ] AC-07: Setup on a machine whose fleet already shows another machine's assistant says, before naming, "Percy on <machine> stays there. This creates a separate Percy for this machine." Docs (repo `docs/studio/*`, `apps/ios`, `apps/android` READMEs, docs-site `docs/studio/projects.md`) say "your personal assistant (default name Percy)", one per machine.
- [ ] AC-18: With another machine's Percy listed and none on this machine, the sidebar shows no "Set up here" row; the other Percy's page keeps "Open this machine's assistant", and the command palette keeps setup. With no Percy anywhere, "Set up" shows as today. (Seen on Minisforum, November 11, 2026: 1.0.232, no personal project, `aideEnabled` default on, M4 connected.)
- [ ] AC-19: The user's chosen name always wins. On iPhone the drawer row, the iPad sidebar row and the column header show the personal project's title, as the chat header already does. (Seen on a fresh 1.0.233 install, November 11, 2026: assistant named "Percy", chat header "Percy", drawer root "Aide", from the literal at `apps/ios/SWCKit/Sources/SWCFeatures/Drawer/DrawerView.swift:74`, `SidebarView.swift:363` and `ColumnHeader.swift:53`.) A source test fails if an iOS view quotes the old or default name. Web and Android rows already read the title.

### Protection on one machine
- [ ] AC-08: `studio_thread_read` and `studio_thread_search` refuse personal-project threads to an agent thread of any other project, with or without a work grant. The assistant's own threads and the app UI still read them.
- [ ] AC-09: Project memory calls without a caller thread are allowed only to management credentials (the rule in `apps/server/src/mcp/toolkits/projectKnowledge/handlers.ts`); any other thread-less client is refused for a personal project.
- [ ] AC-10: On macOS, ServerSecretStore keeps a Keychain-wrapped copy, verifies it by reading back before removing the `.bin`, and fails closed on unwrap failure instead of regenerating keys. Pairing, signed URLs and connection tokens survive an upgrade and restart.

### One Percy across your machines
- [ ] AC-11: A join is offered only between machines of the same person (own invitation pairing; equal `cloudUserId` when both are signed in). Machines reached through a work grant or another account are never offered, and a `cloudUserId` mismatch refuses the join with a plain reason.
- [ ] AC-12: A join is requested from the new machine's UI and allowed by a person: a card on an existing seat, or "Also share Percy" on an invitation a person created. An MCP tool, agent thread or work grant can do neither. Both ends show machine name and key fingerprint.
- [ ] AC-13: A dedicated route exports only name, icon, instructions and memory files, after a secret scan; never coordinator binding, plan, replica, turns, workspace root, connection rows or secrets. A test asserts that.
- [ ] AC-14: A memory item marked "Keep on this machine" is never exported; an incoming file with the same name is kept beside it under the sender's machine name; tombstones go out only for files already exported.
- [ ] AC-15: Joining two existing seats shows the differing memory files for review before the first sync; nothing is deleted or overwritten without that review.
- [ ] AC-16: Leaving the group stops sync on both ends and keeps each seat's data; "Ask <machine> to delete what it received" applies at that machine's next connection. Join, allow, export (file names) and leave are logged on both machines and listed in Percy's settings.
- [ ] AC-17: Seats of one group render as one Percy row with machine chips in the web sidebar and one Percy on iOS and Android; seats outside the group render as today with their machine name.
- [ ] AC-20: After a join, name, icon, instructions and shared memory are equal on every online seat within two sync rounds (120 s), and an edit on any seat reaches the others.
- [ ] AC-21: First run offers Percy: "Use Percy here too" (preselected) when a same-person machine has one, "Set up Percy" otherwise; skipping leaves no nag (AC-18). With "Also share Percy" on the invitation the new machine has a joined seat after one click.
- [ ] AC-22: Web, iOS and Android pick the assistant by one shared rule: this machine's seat, else the home machine, else the lowest-id online seat; a phone can switch seats by name. A machine with the assistant switched off hides only its own seat.

### Home machine, services and safety nets
- [ ] AC-23: A group has one home machine, shown and changeable in Percy's settings. Each personal routine exists once and runs on the home machine: with Google connected on two seats, one briefing arrives. With the home machine offline for 15 minutes, the next eligible seat runs the due routine once and labels it.
- [ ] AC-24: Services on a seat without Google shows, for each Google account another seat holds, "Connected on <machine> as <email>. Sign in here to use it on this machine too"; no token leaves a machine.
- [ ] AC-25: A second seat given a Telegram bot token that another seat is polling refuses it with "This bot already answers on <machine>"; a 409 from Telegram stops the poller with that message instead of retrying.
- [ ] AC-26: On a phone, with the home machine offline, Percy opens on the next online seat and says which machine answers; with none online it says so and keeps the draft.
- [ ] AC-27: A server whose `userdata` came from another machine (stored host fingerprint differs) keeps running and shows one notice: "This data came from <other machine>. Make this a new machine", which issues a new environment id on confirmation. Containers and hosts without a stable fingerprint never see it.
- [ ] AC-28: An "extra" assistant row offers "Move its memory into Percy and remove it": memory files are copied with a review of conflicts, then the extra is deleted; iOS and Android never show extras as Percy.
- [ ] AC-29: A test covers `phoneMint`: a brokered phone session cannot list or read a personal project of a machine whose owner did not pair that phone.

## Approach

PR A is the prepared branch `percy-default-name` (scratch clone `/tmp/percy-prep`, on `origin/main` 41df4a13). Migrations cannot dispatch commands, so the rename is two steps: migration `075_PercyRenamePending` lists personal projects titled exactly "Aide" once into `percy_rename_pending`, and `apps/server/src/project/PercyRename.ts` renames each at startup through `project.meta.update`, deleting the row when handled (skip and log if "Percy" is taken; retry on failure). A later rename back to "Aide" stays. `ManagedProjectFolders.createNamedProject` maps "Aide" from older clients to "Percy" until January 31, 2027. The guards reuse `isPersonalAssistantProject` and the `projectKnowledge` caller rule.

PR B never reuses `ProjectLink`: its preview carries workspace root, fingerprint, replica, coordinator binding and message snippets (`apps/server/src/project/ProjectLink.ts`), and `studio_project_link_accept` is agent-callable from another machine. A dedicated `PersonalGroup` service and route reuse only the three-way memory merge (`linkedMemoryMerge.ts`, `linkedMemoryThreeWay.ts`) and the fleet transport (Connect with DPoP, or Tailscale HTTPS). Seats stay ordinary personal projects, so every existing guard (one per machine, no handoff, no migrate, Away keeps it) holds unchanged. The first-run step goes into `WelcomeWizard.tsx` after 1297's first-run tasks land, to avoid two increments editing one file.

PR C: the home machine is a field of the group record; `AideBriefingSetup` and `ScheduledTaskAdmission` ask it before creating or running a personal routine. The host fingerprint (IOPlatformUUID, `/etc/machine-id`, MachineGuid) is stored beside `environment-id`; a mismatch only raises the notice.

Rejected: one assistant per fleet stored on one machine (unreachable when that machine sleeps; chats would cross machines); syncing chats and topics (machine paths, secrets, thread merge); a new environment id generated automatically on a fingerprint mismatch (a container rebuild or a Migration Assistant move would silently drop every pairing); a hosted copy of personal memory (cost, and a new place for private data); SQLCipher now.

Risk, name: low. BrowserStack sells a visual-testing product called Percy (percy.io). As a renamable in-app default, never a product name, logo or domain, it does not conflict (`research/percy.md`).

## Decisions

### Asked
- D-01: Default name → "Percy" (Anton, November 9 and 11, 2026).
- D-02: On a new machine of yours with your Percy elsewhere, "Use Percy here too" is preselected and a separate assistant stays under More options (Anton, November 12, 2026; replaces the November 9 "ask, no default").
- D-03: The group shares name, icon, memory about you and instructions; chats, topics, connections, tokens and files stay local (Anton, November 9, 2026).
- D-04: Build the join after the rename and the protection fixes ship (Anton, November 9, 2026).
### Defaulted (change any before sw-do)
- D-05: Older clients sending "Aide" map to "Percy" until January 31, 2027.
- D-06: Keychain wrapping ships macOS only first, in PR C.
- D-07: Chats stay per machine (Anton's November 3 direction); phones list Percy topics from every seat in one list, each marked with its machine.
- D-08: Consent is one card on an existing seat, or "Also share Percy" on a person-made invitation. Never automatic from a grant.
- D-09: Home machine = the first seat; changeable; 15-minute offline takeover for due routines.
- D-10: Personal routines become group-wide and run once (changes D-03's "routines stay local", which caused double briefings).
- D-11: Copied `userdata` raises a notice with one button; the id is never changed automatically.
- D-12: Extras are folded in by the user from the row ("Move its memory into Percy and remove it"), never automatically.
- D-14: The join identity is the Connect account and the owner pairing only; connected Google accounts never decide whose Percy it is, and the group shares their email addresses as hints, per account.
- D-13: Same person = own invitation pairing, plus equal Connect account when both are signed in; 1296's cross-account joins never count as the same person.
### Open
- none

## Tasks

### T-01 Percy default and create mapping
- AC: AC-01, AC-06 | Files: packages/contracts/src/project.ts, apps/server/src/project/ManagedProjectFolders.ts, apps/server/src/project/ManagedProjectFolders.test.ts | Test: vp test run apps/server/src/project/ManagedProjectFolders.test.ts

### T-02 One-time rename migration
- AC: AC-02, AC-03 | Files: apps/server/src/persistence/Migrations/075_PercyRenamePending.ts, apps/server/src/project/PercyRename.ts, apps/server/src/project/PercyRename.test.ts | Test: vp test run apps/server/src/project/PercyRename.test.ts

### T-03 Web copy from the title, locales, setup line and no nag
- AC: AC-04, AC-05, AC-07, AC-18 | Files: apps/web/src/studio/assistantTerms.ts, apps/web/src/studio/personalAssistant.ts, apps/web/src/components/studio/shell/StudioSidebar.tsx, apps/web/src/components/studio/AssistantServices.tsx, apps/web/src/components/studio/ProjectMemory.tsx, apps/web/src/i18n/phrases/*.ts | Test: vp test run apps/web/src/studio apps/web/src/components/studio/shell/StudioSidebar.test.tsx

### T-04 iOS and Android copy, title always wins
- AC: AC-01, AC-04, AC-19 | Files: apps/ios/SWCKit/Sources/SWCFeatures/**, apps/ios/SWCKit/Sources/SWCSync/*.swift, apps/ios/SWCKit/Tests/SWCFeaturesTests/AssistantNameSourceTests.swift, apps/android/**/sync/*.kt | Test: swift test (apps/ios/SWCKit) and ./gradlew :sync:test :wire:test (apps/android)

### T-05 Server copy and docs
- AC: AC-04, AC-07 | Files: apps/server/src/mcp/personalChatBoundary.ts, docs/studio/*.md, apps/ios/README.md, apps/ios/docs/*.md, apps/android/README.md, specweave docs-site/docs/studio/projects.md | Test: vp test run apps/server/src/mcp/personalChatBoundary.test.ts

### T-06 Read guards for personal threads and memory
- AC: AC-08, AC-09 | Files: apps/server/src/mcp/toolkits/orchestrator/handlers.ts, apps/server/src/mcp/toolkits/thread/handlers.ts, apps/server/src/mcp/toolkits/projectMemory/handlers.ts, apps/server/src/mcp/personalChatBoundary.ts | Test: vp test run apps/server/src/mcp

### T-07 Ship PR A: review, merge, release, installed check
- AC: AC-01, AC-02, AC-08, AC-18, AC-19 | Files: (none) | Test: gh pr checks on the PR head, then the released build renames an "Aide" assistant to "Percy"

### T-08 Person identity and the group record (PR B)
- AC: AC-11, AC-12, AC-16 | Files: apps/server/src/project/PersonalGroup.ts, apps/server/src/project/PersonalGroupRoute.ts, apps/server/src/project/PersonalGroup.test.ts, packages/contracts/src/personalGroup.ts | Test: vp test run apps/server/src/project/PersonalGroup.test.ts

### T-09 Shared name, icon, memory and instructions (PR B)
- AC: AC-13, AC-14, AC-15, AC-20 | Files: apps/server/src/project/PersonalGroupSync.ts, apps/server/src/project/PersonalGroupSync.test.ts, apps/server/src/persistence/Migrations/, apps/web/src/components/studio/ProjectMemory.tsx | Test: vp test run apps/server/src/project/PersonalGroupSync.test.ts

### T-10 First-run step, consent card and one pick rule on every client (PR B)
- AC: AC-17, AC-21, AC-22 | Files: apps/web/src/components/onboarding/WelcomeWizard.tsx, apps/web/src/studio/personalAssistant.ts, packages/shared/src/personalAssistant.ts, apps/ios/SWCKit/Sources/SWCSync/ShellSummaries.swift, apps/android/sync/src/main/kotlin/com/specwithcode/sync/ShellSummaries.kt | Test: vp test run apps/web/tests/aide-per-machine packages/shared/src/personalAssistant.test.ts

### T-11 Home machine, one briefing, Google hint, Telegram guard, offline fallback (PR C)
- AC: AC-23, AC-24, AC-25, AC-26 | Files: apps/server/src/project/AideBriefingSetup.ts, apps/server/src/scheduledTasks/ScheduledTaskAdmission.ts, apps/server/src/channels/TelegramChannel.ts, apps/web/src/components/studio/AssistantServices.tsx, apps/ios/SWCKit/Sources/SWCSync/LiveEngine+Sessions.swift | Test: vp test run apps/server/src/project/AideBriefingSetup.test.ts apps/server/src/channels

### T-12 Copied userdata notice, extras cleanup, phone code test, Keychain (PR C)
- AC: AC-10, AC-27, AC-28, AC-29 | Files: apps/server/src/environment/ServerEnvironment.ts, apps/server/src/auth/ServerSecretStore.ts, apps/server/src/fleet/studioFleetHttp.test.ts, apps/web/src/components/studio/shell/StudioSidebar.tsx | Test: vp test run apps/server/src/environment apps/server/src/auth apps/server/src/fleet

### T-13 Verify and close 1269
- AC: AC-20, AC-23 | Files: (none) | Test: specweave verify 1269-percy-default-name-and-opt-in-assistant-link-across-your-machines

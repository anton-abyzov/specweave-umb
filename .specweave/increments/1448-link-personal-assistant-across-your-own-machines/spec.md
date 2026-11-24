# 1448 Link personal assistant across your own machines

Status: **Active, reworked November 24, 2026.** The owner's message of November 24 widened the goal from "link memory between my machines" to "one Percy per SpecWithCode Connect account". The section below is the current design; where it differs from a later section, it wins. Originally approved November 23, 2026; supersedes the unbuilt PR B and PR C of increment `1269-percy-default-name-and-opt-in-assistant-link-across-your-machines` (1269's PR A default name "Percy" and same-machine read guards remain intact).

## Rework, November 24, 2026: one Percy per Connect account

The owner, November 24, 2026: "If I use the one email across multiple machines for SpecWithCode Connect, I must be able to use the same personal assistant. Maybe it needs a separate permission so that you allow both ways of connecting between machines... If this is the same email, it means that I could use the same kind of chats or projects. It should be the one linked account. For example, now I have three different personal assistants, which is weird. I should also have access from my iPhones when I allow it, and there could be repositories attached to it, for example, my tax calculations."

Mockup: `reports/mockup-one-percy.html`.

### What the first build (PR 851) does, and what changes

| Area | PR 851 as reviewed | Now |
|---|---|---|
| Who links | The owner runs a wizard in one window that must reach every seat at once. Nothing links by itself. | A switch on each machine, "Use my Percy on `<machine>`". The servers link themselves and a machine that was off joins when it is back. |
| First merge | The owner reviews every same-name memory file and picks a version. | Automatic and lossless: nothing is picked, nothing is dropped. |
| Undo | A whole-database copy that only a manual restore can use. | "Undo the merge" per machine: Percy's memory and settings go back, nothing else on the machine changes. |
| Chats | Stay on their machine, shown per seat, with a notice on another machine's seat. | One chat list with a machine tag per chat (first release); read-only copies on every joined machine and Continue here (second release). |
| iPhone | Changed `apps/mobile`, which is not distributed. | The shipped Swift app in `apps/ios` shows one Percy. |
| Sync transport | The machine with the lower id drives each pair and needs a grant on the other; a pair with a grant only the other way never syncs. | A grant in either direction is enough. |
| Who runs the merge | "Agents never run it on the live machines." | The owner asked for it on November 24, so an agent may run it with the machine's own command line. Each run saves the copies first. |

Everything else PR 851 built stays: the own-machine sync policy, peer settings sync, the secret scan and "Keep on this machine", the routine runner, attached repository links, the removal and leave signals, the read guards and their tests.

### Decisions of the rework

- **D-11 Percy belongs to the Connect account.** The link id is derived from the account: `logical:percy:` plus the first 32 hex characters of SHA-256 of `percy:` and the Connect user id. Every machine of the account computes the same id, so there is no id to choose or pass around. A machine that is not linked to Connect cannot join.
- **D-12 One switch per machine is the permission.** Server setting `personalAssistantShared`, off by default and never turned on by an update. It holds `machines`, the machines the owner confirmed on this machine. It is changed only by the owner: the RPC `personalLink.setShared` (owner-only list, settings write scope, refused for another machine's key and never an MCP tool) or the local command `specwithcode percy on|off|status|undo`. Turning it on makes this machine's Percy when it has none.
- **D-13 Who may join (the trust boundary).** Two seats link only when all of these hold: both switches are on; each machine lists the other in `machines`, or a seat already linked to this one vouches for it (an addition made on one member reaches the others); an `own`, non-legacy, unrevoked grant exists between the two machines in at least one direction; both report the same Connect user id and so the same link id. The Connect user id a peer sends is its own word; the grant is the authenticated part and the owner's confirmation is the consent. A team grant, a legacy grant, another account, an agent or an MCP client can never cause a join. `workGrantPolicy.projectInGrant` stays `false` for personal projects.
- **D-14 Both directions over one grant.** When the lower-id machine holds no grant on its peer, the other machine drives the pair. Exactly one side drives; a pair with no grant either way syncs through a seat both can reach, and `percy status` names such a pair.
- **D-15 The first link is automatic and lossless.** One seat starts the link ("Start from `<machine>`", default the machine with the most memory files; the owner's choice for his machines is m4). Its name, icon, instructions and repository list become the link's; the name defaults to "Percy" when the seats' names differ. A seat that joins never asks anything: `MEMORY.md` becomes the link's lines followed by its own lines the link lacks; any other file whose name the link already holds with different content is kept as `<name>.from-<machine>.md`, shared, and its line in this seat's `MEMORY.md` is pointed at the new name. Files only one seat has are shared as they are. "Keep on this machine" and secret-flagged files stay local as before. Existing members never rename anything. After the first sync no file holds clash markers.
- **D-16 Undo is per assistant.** Before its first link a seat saves two things: the whole database (as PR 851 does) and a restore point holding only Percy's memory files, flags, name, icon, instructions, repository list and link state. `specwithcode percy undo` (and the button in Settings) turns the switch off, leaves the link, and puts Percy's memory and settings back to the restore point. It first saves the current state as a new restore point, so an undo can itself be undone. The other seats drop this machine and keep their own data. Chats are never touched by a merge or an undo.
- **D-17 Chats, first release.** A linked Percy shows one chat list: every joined machine's chats, each with its machine tag. Opening a chat on another machine reads and answers there, live. A new chat starts on the machine the window sits at. A machine that is off shows as one quiet line ("m1 is offline: its chats appear when it is back"). The notice "this is another machine's assistant" goes for linked seats.
- **D-18 Chats, second release.** Each joined machine keeps a read-only copy of the other seats' Percy chats: title, messages and the assistant's replies as text, without tool output, attachments, provider sessions or files. A copy opens while its machine is off and offers Continue here, which starts a new chat on this machine with the copy as its history. The copy is not a handoff: the chat stays owned by its machine, and Away, hand off, thread move, limit handoff and remote launch keep refusing Percy. Text Percy wrote from mail, calendar or Drive is part of those copies and so rests on every joined machine; the switch's text says so from that release on, and "Keep chats on this machine" on a seat stops its chats from being copied.
- **D-19 iPhone.** The Swift app shows one Percy for linked seats, with the same chat list and machine tags. A phone reaches a machine's Percy only after that machine allowed the phone (the device approval of 1327 and 1447, one code per machine); there is no separate Percy permission for a phone. A new chat from the phone goes to the routine runner when it is online, else the first joined machine that answers. A phone build from before this change keeps working and keeps showing one row per machine.
- **D-20 Not joined is visible.** A machine whose switch is off, that is off, or that runs a version without this change keeps its own assistant as its own row, "Percy on `<machine>` · not joined". Nothing of it is merged until its switch is on. Nobody reports "one Percy" for a machine in that state.
- **D-21 Google data.** Unchanged: Gmail, Calendar and Drive access is per machine and per source ([[decision_personal_data_permission]]). The switch grants no Google access to any machine.

### Rollout

1. Release the first build to every machine (no forced update: each takes it at a quiet moment).
2. On m4: `specwithcode percy on --start --name Percy --with <M5, m1, win>`. On M5 and m1: `specwithcode percy on --with <m4, …>`. Each prints where its copies were saved.
3. Check on each joined machine: `specwithcode percy status` lists the members and "in step"; the sidebar on M5 shows one Percy.
4. win and m3 were unreachable from M5 on November 24. They stay "not joined" until they run the new version and their switch is turned on; the same command joins them.
5. Routines are not merged: three morning briefings still arrive until the owner removes two.

### Proof limits

- The phone's behaviour is proven in the simulator and by tests, not on the owner's iPhone.
- The trust boundary rests on the owner's own grants; a machine the owner wrongly confirmed and that holds an own grant would receive Percy's memory.
- The server cannot ask SpecWithCode Connect which machines belong to its account: the relay lists them only for the user's sign-in token, which a server does not hold. So a peer's Connect user id is its own word and can only refuse; memory goes to a peer only when this machine's owner listed it in the switch or a seat already linked here vouches for it. In the window, Settings pre-ticks only machines the relay lists under the signed-in account.
- A machine that holds this machine's management key and an own grant, and later signs in to another Connect account, can still claim the old account and keep receiving Percy's memory. This adds no reach: that key already opens a window here without a device code and reaches the local command line, which has every scope (final review, November 24, 2026). Removing the machine under Settings > Machines ends both.
- A linked seat whose Connect link cannot be read pauses sync and stays a member; it never leaves or merges again on its own.
- The second release (chat copies) ships after the first; until then a chat is unreadable while its machine is off.

## Problem

Today, every machine in a user's fleet creates a separate, disconnected personal assistant. On Anton's fleet (screenshot evidence from November 23, 2026), the sidebar shows four fragmented entries: `Personal assistant · Set up here` (M5), `Percy` (`win`), `PercyAnton` (`m4`, 3 items), and `PercyM1` (`m1`).

### Current implementation audit (`repositories/anton-abyzov/specwithcode`)

| Area | Current behaviour | Code location |
|---|---|---|
| Creation & managed folder | `createNamedProject` enforces at most one `kind: "personal"` project per machine under `assistantLock`, claims an app-managed folder under `<baseDir>/projects/<slug>`, skips `git init` and SpecWeave, and assigns `PERSONAL_ASSISTANT_PROJECT_ICON`. | `apps/server/src/project/ManagedProjectFolders.ts:920-1105`, `1170-1173` |
| Per-machine uniqueness | `ProjectService.commit` (`PERSONAL_ASSISTANT_LOCK`) and `ProjectCommands` (`PersonalAssistantExistsError`) forbid a second personal project on one machine; `kind` is immutable (`kind_fixed`). | `apps/server/src/project/ProjectService.ts:174-175`, `535-568`; `apps/server/src/orchestration-v2/ProjectCommands.ts:226-235`, `728-735` |
| Memory storage | Memory files live in SQLite (`project_memory` and `project_memory_revisions`), not as Git-tracked files on disk. | `apps/server/src/project/ProjectWorkspaceService.ts:405-516` |
| Attached repositories | Personal projects already support up to 32 `settings.environment.repositories` and 16 `additionalFolders` in both server and UI, while refusing SpecWeave. | `apps/server/src/project/ProjectWorkspaceService.ts:422-424`, `618-630`, `757-758`; `apps/web/src/components/studio/ProjectEnvironment.tsx:280-340`, `502-579` |
| Cross-machine refusal | `PERSONAL_ASSISTANT_PRIVATE_MESSAGE` (October 20 rule) states that a personal assistant's topics, memory and routines never move, copy or sync. `ProjectLink` (`refusePersonal`), `LinkedMemorySync` (`memoryExport`/`memoryMerge`), `LinkedPeerSync`, `LinkedPeerRoute.linkedCopyFor`, and `workGrantPolicy.projectInGrant` all reject `isPersonalAssistantProject`. | `packages/shared/src/personalAssistant.ts:1-53`; `apps/server/src/project/ProjectLink.ts:218-221`, `294`, `555`, `996`, `1076`; `apps/server/src/project/LinkedMemorySync.ts:267`, `475`; `apps/server/src/project/LinkedPeerSync.ts:280`, `1073`; `apps/server/src/project/LinkedPeerRoute.ts:139-151`; `apps/server/src/fleet/workGrantPolicy.ts:251-256` |
| Sidebar rendering | Personal projects have no `logicalProject` and no repository identity. `StudioSidebar` splits them out via `assistantEntries.ts` into separate rows per machine with distinct auto-assigned icons (`useDistinctAssistantIcons`) plus `Set up here` when the local machine lacks one. | `apps/web/src/components/studio/shell/StudioSidebar.tsx:869-885`, `938-945`, `1004-1039`; `apps/web/src/components/studio/shell/assistantEntries.ts:1-54`; `packages/client-runtime/src/state/projectGrouping.ts:136-144` |
| Person memory sync today | None. Increment `1269` (November 12, 2026) designed a separate `PersonalGroupSync` (PR B) and home-machine routing (PR C), but neither shipped. | `.specweave/increments/1269-percy-default-name-and-opt-in-assistant-link-across-your-machines/spec.md` |
| Linked code projects today | Equal coordinators on every machine (no standby/takeover, increment `1390` revised November 19), server-to-server two-way three-way text merge for memory (`LinkedMemorySync` + `LinkedPeerSync` + tombstones), single collapsed sidebar row via `logicalProject`, and informational coordinator messages (`1427`). | `apps/server/src/project/EqualCoordinatorMigration.ts:1-95`; `apps/server/src/project/LinkedMemorySync.ts:1-45`, `165-254`; `apps/server/src/project/linkedMemoryMerge.ts:1-100`; `apps/web/src/sidebarProjectGrouping.ts:101-118` |
| Per-machine Google access | OAuth tokens stay local per machine. Drive currently requests `drive.readonly` only (no write scope). `PersonalDataAccess` gates Gmail, Calendar and Drive per machine and per source; `actsAsOwner` currently passes `grant.kind === "own" || grant.legacy === true`. | `apps/server/src/integrations/google/googleAccountLogic.ts:15-21`; `apps/server/src/personalData/PersonalDataAccess.ts:35`, `61-287`; `apps/server/src/personalData/personalDataGate.ts:17-58` |

## Options Evaluation

| Dimension | (a) Owner-linked Personal Project (Recommended) | (b) Separate per-machine assistants + `PersonalGroupSync` (1269 PR B/C) | (c) Cloud Drive (Google Drive / iCloud / Dropbox) or Git as primary store |
|---|---|---|---|
| **Mental model** | One `Percy` across your own machines (reuses `logicalProject` + equal coordinators + `LinkedMemorySync`), with memory as the shared core and optional attached repos. | Separate assistants per machine linked only by a bespoke `PersonalGroup` sidecar. | External folder in Google Drive (or Git repo) acts as the source of truth; SpecWithCode syncs SQLite memory to/from it. |
| **Privacy & trust boundary** | Strong when enforced by a dedicated human-only join route, `grant.kind === "own"` + equal `cloudUserId` (rejecting `legacy` and `team` grants), `localOnly` file flag, and secret scan. Never leaves the owner's machines. | Strong by construction (zero shared code path with `ProjectLink`), but requires duplicating auth, membership, and peer-sync checks. | Weakest for Google Drive: puts private personal memory (health, taxes, family) on third-party servers. Requires upgrading `drive.readonly` to `drive.file` or restricted `drive` scope (CASA Tier 2+ audit). Git risks committing secrets to remote history. |
| **Offline use** | First-class. Every machine holds a full SQLite copy of memory; `LinkedPeerSync` converges automatically when machines reconnect. | Same offline behavior, once a second sync engine is built and maintained. | Poor without building a full local sync/cache engine anyway. Drive API calls fail offline; local Drive desktop mounts vary wildly by OS and break headless servers. |
| **Conflict handling** | Reuses `LinkedMemorySync` + `linkedMemoryMerge.ts` (content-hash history, 3-way line merge, clash markers, tombstones). | Must wrap or duplicate `LinkedMemorySync` under a separate protocol. | Drive has no 3-way line merge (last-writer-wins overwrites or `(1)` duplicate files). Git merge conflicts block non-technical users. |
| **Per-machine Gmail / Calendar / Drive permissions** | Preserved intact. OAuth tokens and `PersonalDataAccess` stay strictly local per machine. Derived facts written to shared memory obey `localOnly` ("Keep on this machine") and secret scan. | Preserved intact. | Broken as a sync assumption: forces Google sign-in on every machine just to sync Percy, contradicting per-machine Drive permission. |
| **Naming & sidebar UI** | Collapses into one `Percy` row with machine badges (`m4`, `m1`, `win`, `m5`) and a one-click "Use Percy on M5" seat action. | Needs bespoke sidebar grouping on top of `PersonalGroup` outside `logicalProject`. | Does not solve sidebar grouping, naming, or multi-machine coordinator UX on its own. |
| **Attached repositories (e.g. taxes)** | Already supported by `settings.environment.repositories`. Shared metadata lists attached repo URLs; each machine binds its own local checkout path (or clones on demand). | Requires custom metadata sync for attached repos. | Drive cannot host Git repos cleanly. A Git repo is ideal *as an attached repository* (e.g. `taxes-2026`), not as the memory database. |
| **Maintenance & code reuse** | High reuse: `logicalProject`, `LinkedMemorySync`, `LinkedPeerSync`, and `routineOwner` already exist and are tested. Only the join route, owner-only peer predicate, and sidebar grouping change. | High duplication: parallel `PersonalGroup`, `PersonalGroupSync`, membership, and UI grouping (the main reason 1269 PR B/C stalled). | Highest complexity: OAuth scope upgrade, Google verification, Drive API polling/webhooks, custom conflict resolver, plus vendor lock-in. |
| **Migration of `Percy`, `PercyAnton`, `PercyM1`** | Guided owner-approved link + pre-merge diff review (handles no common ancestor), snapshot, and one collapsed `Percy` row. | Same migration burden, on a bespoke group model. | Requires exporting all 3 SQLite stores to Drive, manually resolving clashes, and configuring Drive on all 4 machines. |

### Recommendation

**Adopt Option (a): One owner-linked Personal Project across the owner's own machines**, with a **dedicated human-only, owner-only join route** and **strict boundary preservation**:

- **What Option (a) reuses:** `logicalProject` identity, `LinkedMemorySync` (3-way merge + tombstones), `LinkedPeerSync` (server-to-server background sync), equal coordinators (one active coordinator per machine), `routineOwner` (routines fire on one machine), and collapsed sidebar grouping.
- **What Option (a) deliberately does NOT reuse (rebutting 1269's valid privacy objections):**
  1. Never exposes `ProjectLink.preview`, `ProjectLink.accept`, or `studio_project_link_accept` (agent-callable) to personal projects. Personal linking uses a dedicated, UI-only, owner-only RPC (`personalLink.preview` / `personalLink.join` / `personalLink.leave`) with an allow-listed preview (`assistantName`, `icon`, `memoryFileCount`, `machineLabel` — never workspace roots, fingerprints, or chat snippets).
  2. Never relaxes `workGrantPolicy.ts:256` (`projectInGrant` stays `false` for personal projects so a `projects.kind: "linked"` or `team` grant can never reach Percy). Instead, `LinkedPeerRoute` and `LinkedPeerSync` use a dedicated `isOwnPersonalSyncAllowed(caller, project)` predicate requiring `grant.kind === "own"` **and** equal `cloudUserId` (explicitly rejecting `grant.legacy === true` and `grant.kind === "team"`).
  3. Syncs **memory, instructions, name, icon, and optional attached repo URLs only**. Chats/threads, local workspace files, OAuth refresh tokens, Telegram bot token, and `PersonalDataAccess` stay strictly local per machine. Remote agent launch, Away takeover, thread move, and limit handoff remain disabled for personal assistants.
- **Role of Google Drive & Git:** Reject Google Drive as the primary memory store. Keep Google Drive as a **per-machine connected data source** (`studio_google_drive_*`), and use **attached Git repositories** (`settings.environment.repositories`) for structured personal repos such as tax calculations or an Obsidian vault.

### Explicitly Overturned or Refined Decisions

1. **Overturns October 20 rule (`packages/shared/src/personalAssistant.ts`, `reference_personal_assistant.md`):** Replaces "strictly private to one machine, never linked or synced" with "strictly private to one **owner** across their own verified machines (`grant.kind === 'own'` + matching `cloudUserId`)".
2. **Overturns `decision_personal_assistant_percy.md` (November 12, 2026) and Increment `1269` PR B/C:** Replaces the separate `PersonalGroup` / `PersonalGroupSync` sidecar with `logicalProject` + `LinkedMemorySync` behind a dedicated owner-only join route and peer predicate. Keeps 1269's PR A ("Percy" default name and same-machine read guards) and carries over 1269's `localOnly` flag, secret scan, and pre-merge review rules (AC-11 through AC-15).
3. **Refines `decision_personal_data_permission.md` (November 13, 2026):** Keeps per-machine OAuth token locality and per-machine/per-source `PersonalDataAccess` gates unchanged. Updates the "distinct icons per assistant" rule so **linked seats of one Percy share one icon** (differentiated by machine badges), while only unlinked assistants use distinct icons. Updates "memory is never grantable" to: memory syncs **only** across the owner's own verified machines via `isOwnPersonalSyncAllowed`, never via `team` or `legacy` grants; chats and routines remain non-grantable.
4. **Resolves `decision_person_memory_sync.md` (November 3, 2026):** Resolves the open sync mechanism choice in favor of `LinkedMemorySync` over fleet peer sync (not Google Drive, not a bespoke sync engine).

## Recommended Design & Mockup

### Sidebar & Workspace Mockup

```text
BEFORE (4 separate rows)                  AFTER (1 linked Percy row)
────────────────────────                  ──────────────────────────
+ Personal assistant · Set up here        ★ Percy                [m4][m1][win]
● Percy (win)                               ├ Topics on m4 (3)
● PercyAnton (m4) [3]                       ├ Topics on m1
● PercyM1 (m1)                              ├ Topics on win
                                            └ + Use Percy on M5 (join seat)

When opened on M5 after joining:
────────────────────────────────────────────────────────────────────────────
★ Percy  [M5 ●] [m4] [m1] [win]           [Memory (18 synced, 2 local)] [⚙]
────────────────────────────────────────────────────────────────────────────
Coordinator (M5)                          Memory & Attached Repos (Settings)
• Talks to M5's own coordinator           • Synced across: M5, m4, m1, win
• Local chats stay on M5                  • Local-only toggle per memory file
• Gmail/Drive use M5's own permissions    • Attached repos (optional):
• Routines run on: m4 (Routine owner)       - anton-abyzov/taxes-2026
                                              M5: not cloned [Clone here]
                                              m4: ~/Projects/taxes-2026
```

### Guard Audit Table (`isPersonalAssistantProject` — 126 sites across 45 files)

Every existing guard must be classified explicitly before implementation so joining `logicalProject` never accidentally activates code-project handoff or cross-user access:

| Subsystem | Files | Policy |
|---|---|---|
| Work grants (`projectInGrant`) | `apps/server/src/fleet/workGrantPolicy.ts:251-256`, `apps/server/src/mcp/workGrantAccess.ts` | **Keep `false`** — never expose personal assistant to `projects.kind: "linked"` or `team` grants. |
| Peer memory sync & route | `apps/server/src/project/LinkedMemorySync.ts`, `LinkedPeerSync.ts`, `LinkedPeerRoute.ts` | **New predicate** `isOwnPersonalSyncAllowed(caller, project)` (`grant.kind === "own"` + equal `cloudUserId`, member of `logicalProject`, human-linked only). |
| Link creation & MCP tools | `apps/server/src/project/ProjectLink.ts`, `apps/server/src/mcp/toolkits/project/handlers.ts`, `remoteLaunch.ts`, `migrate.ts` | **Keep refused** — personal projects never use `ProjectLink.preview`/`accept`/`commit` or agent-callable MCP linking/remote launch. Add separate UI-only `personalLink.*` RPCs. |
| Away, Handoff, Thread Move, Limit Handoff | `apps/server/src/away/*`, `apps/server/src/handoff/*`, `apps/server/src/orchestration-v2/ThreadMoveService.ts`, `MachineLimitHandoff.ts` | **Keep refused** — personal assistant chats stay local to their machine. |
| Routines | `apps/server/src/scheduledTasks/*`, `apps/web/src/components/settings/ScheduledTasksSettings.tsx` | **Use `routineOwner`** on `coordinatorBinding` (single routine runner across linked seats, changeable by the user in Settings). |
| Read-only MCP & phone guards (1269 G-14, G-15, G-17) | `apps/server/src/mcp/toolkits/thread/handlers.ts`, `apps/server/src/mcp/toolkits/projectMemory/handlers.ts`, phone token minting | **Harden first** — verify and block cross-project / cross-person reads of personal assistant threads and memory before enabling sync. |
| Sidebar & UI grouping | `apps/web/src/components/studio/shell/assistantEntries.ts`, `StudioSidebar.tsx`, `apps/web/src/studio/personalAssistant.ts`, `CommandPalette.tsx` | **Update** — group linked personal seats into one row with shared icon + machine badges; offer "Use `<name>` on `<this machine>`" when local machine has no seat. |
| Google / Personal data gate | `apps/server/src/personalData/personalDataGate.ts`, `apps/server/src/integrations/google/*` | **Tighten** — keep OAuth tokens local; require `grant.kind === "own"` + equal `cloudUserId` for own-machine personal sync (never `legacy`). |

## Scope

In:
- Owner-only linking of `kind: "personal"` projects via `logicalProject` using a dedicated human-only `personalLink.*` RPC (never agent-callable).
- Two-way memory, instructions, name, icon, and optional attached-repository URL sync across the owner's own machines via `LinkedMemorySync` + `LinkedPeerSync` behind `isOwnPersonalSyncAllowed`.
- Per-file "Keep on this machine" (`localOnly`) flag and automatic secret scan before export.
- Single collapsed sidebar row for linked Percy seats with machine badges, shared icon, and one-click "Use Percy on `<machine>`".
- Routines keep firing once, on the machine where each was made: linking never stops or duplicates one (`routineOwner` decides only a copy a seat rested for another machine). Three Percys that each have a morning briefing still send three until the owner removes the extras.
- Prerequisite hardening of MCP read guards (`thread/handlers.ts`, `projectMemory/handlers.ts`) and phone assistant selection consistency.
- Automatic, lossless, undoable merge of existing separate assistants (`Percy`, `PercyAnton`, `PercyM1`) behind a per-machine switch (rework D-11 to D-16).
- One chat list for a linked Percy across joined machines (D-17), then read-only chat copies and Continue here (D-18).
- One Percy in the Swift iPhone app (D-19).

Out:
- Moving a personal assistant chat between machines (a copy is read-only, D-18), and syncing local workspace files, attachments, provider sessions, OAuth refresh tokens or Telegram bot tokens.
- Remote agent launch into a personal assistant, Away mode, or model-limit handoff for personal assistants.
- Google Drive, iCloud, Dropbox, or Git as the primary memory storage backend.
- Changing `workGrantPolicy.projectInGrant` to admit personal projects into team or general linked-project grants.
- Merging routines, a Percy permission per phone, and linking by Connect account without the owner turning the switch on.

## Acceptance Criteria

- [ ] AC-01: Cross-project and cross-person MCP reads (`thread/handlers.ts`, `projectMemory/handlers.ts`) and phone minting cannot read a personal assistant's threads or memory from another project or another user.
- [ ] AC-02: `isOwnPersonalSyncAllowed` permits peer sync for a `kind: "personal"` project if and only if both machines hold an `own` (non-`legacy`, non-`team`) pairing, both report the same `cloudUserId`, and both are members of the same `logicalProject.id`; `workGrantPolicy.projectInGrant` continues to return `false` for personal projects.
- [ ] AC-03: A personal assistant is linked only by the owner turning its switch on (`personalLink.setShared` or `specwithcode percy on`), and unlinked by `personalLink.leave`, the switch or undo; these and `personalLink.preview` / `personalLink.setRoutineOwner` are owner-only RPCs. No window can ask a seat to join a link directly, and `ProjectLink.preview`/`accept`/`commit` and all agent-callable MCP tools continue to refuse `kind: "personal"`.
- [ ] AC-04: `personalLink.preview` returns only allow-listed metadata (`assistantName`, `icon`, `memoryFileCount`, `machineLabel`, `memoryFileNames`, the seat's own member entry, per-file name and content hash for the clash review, settings revision and memory digest) and never includes `workspaceRoot`, git fingerprints, memory content or chat snippets.
- [ ] AC-05: Linked personal assistant seats sync memory files, instructions, name, and icon two-way via `LinkedMemorySync` and `LinkedPeerSync`, converging offline edits via 3-way merge with clash markers and tombstones.
- [ ] AC-06: Any memory file marked `localOnly` ("Keep on this machine") or flagged by the secret scanner (API keys, OAuth tokens, private keys, `.env`-style secrets) is excluded from export and surfaces a clear badge in the Memory view; raw Gmail/Drive payloads are never auto-copied to shared memory.
- [ ] AC-07: Removing a machine from the fleet or calling `personalLink.leave` immediately stops sync for that machine, removes it from `logicalProject.members` on every remaining seat (the removal travels with the next sync, and a removed seat that still lists the others is told so and unlinks itself), and leaves its local copy intact as an unlinked local-only assistant (never silently wiping local data).
- [ ] AC-08: Every `isPersonalAssistantProject` guard in Away, Handoff, ThreadMoveService, MachineLimitHandoff, and remote launch remains closed for personal projects (verified by automated tests against the guard table).
- [ ] AC-09: Each personal assistant routine fires once per schedule, on the machine where it was made: routines are never copied to the other linked seats (grants and runner staging refuse personal projects), so linking or changing the routine runner never stops or duplicates one. The routine runner set in Settings (`routineOwner` on `coordinatorBinding`) decides only a copy a seat rested for another machine; reassignment disarms the old runner before arming the new one, and the new runner takes such a copy back at its next slot, never a past one-time slot. On a project whose `userdata` was copied to another machine, only the runner fires the shared routines. Settings says each routine runs where it was made and names the machine chosen for routines more than one machine holds, or says none is chosen.
- [ ] AC-10: Attached repository URLs (`settings.environment.repositories`) sync as optional shared metadata across linked seats, while each machine binds its own local checkout path (or offers a one-click "Clone here" action when absent).
- [ ] AC-11: Linked personal assistant seats collapse into one sidebar row with one icon, the link's name and one count that sums the seats', with no machine name on the row. A machine whose switch is off shows "Use my Percy on `<machine>`", which opens the switch. No "Link assistants" wizard is offered.
- [ ] AC-12: Unlinked personal assistants (before migration or after leaving) continue to render with distinct icons so they remain visually distinguishable.
- [ ] AC-13: Merging existing separate assistants (`Percy`, `PercyAnton`, `PercyM1`) happens only on machines whose switch the owner turned on, saves a database copy and a Percy restore point on each machine before any write (a failed copy stops that machine's join and writes nothing), follows D-15 so that every line and every file of every seat still exists afterwards and no file holds clash markers, is idempotent on retry and after a restart mid-join, handles copied `userdata` and stale "extra" rows as before, and leaves a peer on a version without this change unlinked with the reason shown.
- [ ] AC-14: Phone clients resolve the linked personal assistant by `logicalProject.id`: the Swift app (`apps/ios`) shows one Percy row for linked seats and one row per unlinked assistant, lists the linked seats' chats together with machine tags, and starts a new chat on the routine runner when it is online, else on the first joined machine that answers. `apps/mobile` keeps the same rule.
- [ ] AC-15: `personalAssistantShared` is off by default, survives updates unchanged, and is changed only by `personalLink.setShared` or the local command line; a coordinator key, a session without settings write and every MCP tool are refused, and both the UI gate and the server refusal are tested.
- [ ] AC-16: Every machine of one Connect account derives the same link id (D-11); a machine not linked to Connect, or linked to another account, is refused with a reason `percy status` and Settings show.
- [ ] AC-17: Two seats link by themselves, with no window open, once the conditions of D-13 hold, within two sync intervals; a seat that fails any condition stays unlinked and its reason is reported (switch off, not confirmed, no own grant, legacy grant, other account, older version, offline). A machine confirmed on one member becomes known to the other members.
- [ ] AC-18: Memory and shared settings converge between two seats when the grant exists in only one direction, whichever machine has the lower id, and exactly one side merges memory for the pair.
- [ ] AC-19: `specwithcode percy undo` and the Settings button restore that machine's Percy memory files, flags, name, icon, instructions and repository list to the restore point, leave the link, turn the switch off and save the current state first; another seat's data and this machine's chats are unchanged, and a second undo brings the merged state back on this machine. A missing or damaged restore point refuses and changes nothing.
- [ ] AC-20: The linked Percy page lists the chats of every joined seat the window reaches, each with its machine tag, newest first; a chat on another machine opens and is answered there; a new chat starts on the window's own machine; an unreachable seat shows one line naming the machine; the other-machine notice no longer shows for a linked seat.
- [ ] AC-21: An assistant that is not joined (switch off, older version, offline with no link) stays its own sidebar row, named "Percy on `<machine>`" with "not joined", and keeps a distinct icon.
- [ ] AC-22: Settings > General shows the switch for the window's machine, the machines of the account with each one's state and reason, the routine runner, and Undo; a machine the window reaches can be turned on from the same list (through its own session), and one it cannot reach says where to turn it on.
- [ ] AC-23: User-facing text no longer says each machine has its own assistant or that nothing transfers (`packages/shared/src/personalAssistant.ts`, `apps/web/src/studio/personalAssistant.ts`, `apps/ios` strings); the refusals for Away, hand off, thread move and remote launch say a Percy chat stays on its machine.
- [ ] AC-24 (second release): Each joined seat keeps a read-only copy of the other seats' Percy chats as D-18 defines, refreshed within two sync intervals, under the same policy as memory sync; a copy never carries tool output, attachments or provider sessions, never runs a turn, and a seat with "Keep chats on this machine" exports none.
- [ ] AC-25 (second release): A copied chat opens while its machine is unreachable, marked read-only with the time of the copy; Continue here starts a new chat on this machine whose first turn carries the copied conversation, and the original stays on its machine unchanged.
- [ ] AC-26: On the owner's machines after the rollout, every reachable machine on the new version reports the same link id and members, memory in step, and the sidebar on M5 shows one Percy; machines that could not join are listed with their reason.

## Approach

### Ordered implementation sequence

1. **Harden read boundaries first (T-01):** Audit and close G-14/G-15/G-17 in `thread/handlers.ts`, `projectMemory/handlers.ts`, and phone token minting so replication never amplifies an existing leak.
2. **Owner-only sync predicate & secret/localOnly memory controls (T-02, T-03):** Add `isOwnPersonalSyncAllowed` (`grant.kind === "own"` + matching `cloudUserId`, rejecting `legacy` and `team`), add `localOnly` metadata and secret-scan filtering to `LinkedMemorySync` / `ProjectWorkspaceService`, and wire `LinkedPeerRoute` + `LinkedPeerSync` to use `isOwnPersonalSyncAllowed` for linked personal projects while leaving `workGrantPolicy.projectInGrant` untouched.
3. **Human-only `personalLink.*` RPCs & `routineOwner` (T-04, T-05):** Add `personalLink.preview`, `personalLink.join`, `personalLink.leave`, and `personalLink.setRoutineOwner` with allow-listed preview payloads, zero MCP exposure, and version-skew refusal. Keep `ProjectLink.*` refusing personal projects.
4. **Attached repository URL sync with per-machine paths (T-06):** Sync repository remote URLs and labels in `logicalProject` metadata while resolving `localPath` per machine in `ProjectWorkspaceService` and `ProjectEnvironment.tsx`.
5. **Sidebar grouping, shared icon & "Use Percy on `<machine>`" UX (T-07, T-08):** Update `assistantEntries.ts`, `StudioSidebar.tsx`, and phone assistant resolution so linked seats collapse into one row with machine badges and one-click seat creation/join.
6. **Guided migration flow for `Percy`, `PercyAnton`, `PercyM1` (T-09, T-10):** Build the owner-approved migration dialog (pre-merge snapshot, side-by-side clash preview for same-name files with no common ancestor, canonical name/icon picker, copied-`userdata` dedupe, "extra" row cleanup, idempotent commit) and guard-table regression suite.

### Migration Plan for Existing `Percy` (`win`), `PercyAnton` (`m4`), and `PercyM1` (`m1`)

Because `Percy`, `PercyAnton`, and `PercyM1` were created independently on three machines, their memory files share **no common ancestor**. Running a blind first sync would clash every same-name file (especially `MEMORY.md`). Therefore, migration is a **one-time, owner-approved data migration** (never automatic):

1. **Owner approval gate:** Present a "Merge your personal assistants into one Percy" card/dialog listing the discovered seats (`Percy` on `win`, `PercyAnton` on `m4`, `PercyM1` on `m1`) and asking Anton to confirm canonical name (default `Percy`), icon, and routine-owner machine (default `m4`, where active routines and 3 items live).
2. **Pre-merge backup:** Inside its own `personalLink.join`, before any write, each machine copies its whole database with SQLite's online backup into `<state>/backups/personal-link/<operation>.sqlite` (memory lives in `project_memory`, so the copy holds it). A failed copy refuses the join with `snapshot_failed` and writes nothing. The join also refuses with `stale_plan` when the seat's settings revision or memory digest moved since the owner's review.
3. **Pre-sync clash review (no silent overwrite):** Compare memory file names and hashes across all participating seats. Files unique to one machine are marked "Copy to all seats". Same-name files with differing content (such as `MEMORY.md`) are shown in a review list where the user picks *Keep version from <machine>* (the other machines rename their copy to `<name>.from-<machine>.md` and keep it on that machine only) or *Keep both* (the most recently edited copy keeps the name; the others are renamed and sync too). Nothing is deleted on any machine.
4. **Edge-case hygiene:**
   - **Copied `userdata` (1269 G-02):** Detect identical `projectId` across different `environmentId`s and assign a fresh seat `projectId` before joining `logicalProject.members`.
   - **Stale "extra" rows (1269 G-03):** A second personal assistant on one machine is listed as such and stays as it is, not linked (the earliest-created row on each machine is the seat).
   - **Version skew:** Refuse to join any machine running a server version without `personalLink` support, displaying "Update `<machine>` to link Percy".
   - **Idempotence:** Key the migration by `operationId` so retrying after a transient disconnect converges without duplicating files or members.
5. **Add M5 as a seat:** Once `win`, `m4`, and `m1` are linked as one `Percy`, **"Use Percy on M5"** opens the link flow: it sets up M5's seat first, then **Link assistants** joins it to the same `Percy` instead of leaving a 4th disconnected assistant.
6. **Who runs it (replaced November 24, 2026):** see "Rework" above. The switch or `specwithcode percy on` starts it on each machine; the owner asked for the merge of his machines on November 24, so an agent may run that command there. Steps 1 and 3 of this plan (approval dialog, clash review) are replaced by D-12 and D-15.

## Decisions

### Asked
- **O-01 Data migration approval:** Approved one-time snapshot-backed merge of `Percy` (`win`), `PercyAnton` (`m4`), and `PercyM1` (`m1`) into one linked `Percy` with `m4` as routine owner (owner, November 23, 2026).
- **O-02 Overturning prior decisions:** Approved superseding `1269` PR B/C and narrowing the October 20 single-machine rule to owner-verified own machines (owner, November 23, 2026).

- **O-03 One Percy per Connect account (owner, November 24, 2026):** merge Percy, PercyAnton and PercyM1 into one Percy with m4 as routine runner; the same chats on every machine signed in with that account under a permission per machine, both directions; iPhone access once allowed; attached repositories. His request is the consent to the data migration; it must be reversible and backed up. Overturns the October 20 "one assistant per machine" rule and "Agents never run it on the live machines".

### Defaulted (change any before sw-do)
- **D-01 Sync scope (chats: see D-17 and D-18):** Sync memory files (excluding `localOnly` and secret-flagged files), instructions, name, icon, and optional attached repo URLs. Keep chats/threads, local workspace files, OAuth tokens, and Telegram bot tokens strictly local per machine (reversible; matches 1269 D-03/D-07 privacy posture while giving one unified `Percy`).
- **D-02 Primary storage backend:** Fleet peer sync via `LinkedMemorySync` (SQLite + 3-way merge), not Google Drive or Git. Google Drive remains a per-machine connected data source (`drive.readonly`); Git repos attach optionally via `settings.environment.repositories` (reversible).
- **D-03 Routine execution:** Routines stay on the machine where they were made and fire there (review round 2: they never travel between personal seats, so a gate that rested them on non-runner seats would have stopped PercyM1's and Percy (win)'s routines). `routineOwner` on `coordinatorBinding` (default `m4`, changeable in Settings) decides only rested copies and, on a project whose `userdata` was copied to another machine (the same project id on two members, so both seats hold the same routine ids), which seat fires them; on such a project a routine made later on a non-runner seat also rests until that seat is chosen, and a one-time slot a seat rested there is dropped when that seat becomes the runner, because the former runner fired its own copy (review round 3). Making routines travel between seats needs a grant-policy change (an auth change) and is out of scope (reversible).
- **D-04 Identity rule for personal sync:** Require `grant.kind === "own"` AND equal `cloudUserId`; reject `grant.legacy === true` and `grant.kind === "team"` (hard security invariant).
- **D-05 Leaving / removing a machine:** Unlinks the machine from `logicalProject.members` and stops sync, keeping its local copy intact as an unlinked local assistant rather than deleting local memory (reversible, safe default).

- **D-06 Shared-settings conflicts (review round 1):** Name, icon, instructions and repository URLs carry a server-managed `sharedSettingsUpdatedAt` stamp that moves only when one of them changes; the newest stamp wins on every seat, and the newest seat's repository list replaces the others' (each machine keeps its own local folder). Per-machine changes (pause, runner, memory flags) never move it.
- **D-07 Peer identity (review round 1):** The access boundary is the non-legacy `own` grant plus reciprocal seat membership: every personal sync request names the caller's own seat (`forProjectId`) and the receiving seat must list that exact seat. The Connect user id header is self-asserted by an authenticated peer and serves as a consistency check (both machines on one Connect account); it is sent only on personal sync paths.

- **D-08 Leaving a link (review round 2):** A seat that leaves, or removes the last other seat, remembers the old link id and its members (`coordinatorBinding.formerLinks`). A seat still on that link that calls it is told "this seat left" and drops only that member, with a removal tombstone that travels to the rest; "you were removed" keeps meaning "unlink yourself". Joining a link again clears its former-link entry and its tombstones (`relinkedMembers`).
- **D-09 Adding a machine (review round 2):** The link flow reuses an existing link id when any seat already has one, joins the seats already on the link first, and keeps the link's name. Every join, including adding a member, needs the owner's approval, a database copy and the clash resolutions. Clash renames move files without leaving a delete tombstone.

- **D-10 First-link settings (review round 2):** The merge review asks whose instructions and attached repositories the link starts from (default: the first machine listed). That seat stamps its shared settings when it joins; every other seat joins without moving its stamp, so the chosen seat's settings reach every seat instead of the last renamed one. Extending a link: picking a machine already on it keeps the link's settings.

### Deferred (review round 2, low)
- Federation of a linked Percy in `federatedProjectThreads.ts:142`.
- The Connect user id header is self-asserted (D-07); it stays a consistency check.
- The merge dialog nests a dialog role and can be dismissed during a join.
- Runner removal: removing the runner machine leaves no runner until the owner picks one in Settings (Settings says so).
- Preview returns the full member list beyond the AC-04 allow-list (the link flow needs it to find an existing link id).
- With two assistant rows on one machine, the oldest row links and the owner cannot pick another.
- After a removal pass the pair is recorded as synced although no memory merge ran; memory syncs on the next interval.
- A shared setting a seat refuses (for example a title already taken there) is logged and not retried under the same stamp.
- A clash rename on a seat that is already linked can be undone by a sync from an existing peer before the other seats finish joining; the link flow puts renames on joining seats.

### Open
- none

## Tasks

### T-01 Harden personal assistant MCP read guards and phone minting
- AC: AC-01 | Files: `repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/thread/handlers.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/projectMemory/handlers.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/thread/handlers.test.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/projectMemory/handlers.test.ts` | Test: `cd repositories/anton-abyzov/specwithcode/apps/server && ../../node_modules/.bin/vp test run src/mcp/toolkits/thread/handlers.test.ts src/mcp/toolkits/projectMemory/handlers.test.ts src/mcp/personalChatBoundary.test.ts`

### T-02 Add `isOwnPersonalSyncAllowed` predicate and guard-table tests
- AC: AC-02, AC-08 | Files: `repositories/anton-abyzov/specwithcode/apps/server/src/fleet/personalSyncPolicy.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/fleet/personalSyncPolicy.test.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/fleet/workGrantPolicy.ts` | Test: `pnpm --dir repositories/anton-abyzov/specwithcode --filter @specweave-studio/server test -- personalSyncPolicy.test.ts workGrantPolicy`

### T-03 Add `localOnly` flag, secret-scan filter, and own-only personal sync in `LinkedMemorySync` and `LinkedPeerRoute`
- AC: AC-05, AC-06 | Files: `repositories/anton-abyzov/specwithcode/apps/server/src/project/LinkedMemorySync.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/LinkedPeerSync.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/LinkedPeerRoute.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectWorkspaceService.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/LinkedMemorySync.test.ts` | Test: `pnpm --dir repositories/anton-abyzov/specwithcode --filter @specweave-studio/server test -- LinkedMemorySync.test.ts LinkedPeerRoute`

### T-04 Add human-only `personalLink` RPCs (`preview`, `join`, `leave`) with allow-listed preview and version-skew guard
- AC: AC-03, AC-04, AC-07 | Files: `repositories/anton-abyzov/specwithcode/packages/contracts/src/personalLink.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/PersonalLinkService.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/PersonalLinkService.test.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/ws.ts` | Test: `pnpm --dir repositories/anton-abyzov/specwithcode --filter @specweave-studio/server test -- PersonalLinkService.test.ts`

### T-05 Wire `routineOwner` enforcement and reassignment for linked personal assistant routines
- AC: AC-09 | Files: `repositories/anton-abyzov/specwithcode/apps/server/src/scheduledTasks/ScheduledTaskService.ts`, `repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ScheduledTasksSettings.tsx`, `repositories/anton-abyzov/specwithcode/apps/server/src/scheduledTasks/ScheduledTaskService.test.ts` | Test: `pnpm --dir repositories/anton-abyzov/specwithcode --filter @specweave-studio/server test -- ScheduledTaskService.test.ts`

### T-06 Sync optional attached repository URLs with per-machine local path resolution
- AC: AC-10 | Files: `repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectWorkspaceService.ts`, `repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectEnvironment.tsx`, `repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectEnvironment.test.tsx` | Test: `pnpm --dir repositories/anton-abyzov/specwithcode --filter @specweave-studio/web test -- ProjectEnvironment.test.tsx`

### T-07 Collapse linked personal assistant seats in sidebar with shared icon, machine badges, and "Use Percy on `<machine>`"
- AC: AC-11, AC-12 | Files: `repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/assistantEntries.ts`, `repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/StudioSidebar.tsx`, `repositories/anton-abyzov/specwithcode/apps/web/src/studio/personalAssistant.ts`, `repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/assistantEntries.test.ts` | Test: `pnpm --dir repositories/anton-abyzov/specwithcode --filter @specweave-studio/web test -- assistantEntries.test.ts`

### T-08 Add Memory view "Keep on this machine" toggle and secret-excluded badge
- AC: AC-06 | Files: `repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectMemorySection.tsx`, `repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectMemorySection.test.tsx` | Test: `pnpm --dir repositories/anton-abyzov/specwithcode --filter @specweave-studio/web test -- ProjectMemorySection.test.tsx`

### T-09 Build owner-approved migration wizard for existing separate assistants (`Percy`, `PercyAnton`, `PercyM1`)
- AC: AC-13 | Files: `repositories/anton-abyzov/specwithcode/apps/server/src/project/PersonalAssistantMigration.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/PersonalAssistantMigration.test.ts`, `repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/PersonalAssistantMergeDialog.tsx` | Test: `pnpm --dir repositories/anton-abyzov/specwithcode --filter @specweave-studio/server test -- PersonalAssistantMigration.test.ts`

### T-11 Fix review round 1 (GPT-6.2 Sol, `reports/review-gpt-6.2-sol.md`)
- AC: AC-01, AC-02, AC-03, AC-05, AC-06, AC-07, AC-09, AC-10, AC-11, AC-13, AC-14 | Files: `repositories/anton-abyzov/specwithcode/apps/server/src/project/PersonalLinkService.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/personalLinkSnapshot.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/PersonalPeerSync.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/LinkedPeerRoute.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/LinkedPeerSync.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/LinkedMemoryPeers.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ProjectCommands.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/mcp/threadAccess.ts`, `repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/PersonalAssistantLinkFlow.tsx`, `repositories/anton-abyzov/specwithcode/packages/shared/src/personalAssistantMigration.ts` | Test: `cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/project/PersonalLinkService.test.ts src/project/PersonalPeerSync.test.ts src/project/LinkedPeerRoute.personal.test.ts`

### T-10 Unify phone assistant selection by `logicalProject.id`
- AC: AC-14 | Files: `repositories/anton-abyzov/specwithcode/packages/client-runtime/src/state/projectGrouping.ts`, `repositories/anton-abyzov/specwithcode/packages/client-runtime/src/state/projectGrouping.test.ts` | Test: `pnpm --dir repositories/anton-abyzov/specwithcode --filter @specweave-studio/client-runtime test -- projectGrouping.test.ts`

### T-12 Fix review round 2 (ultracode workflow, 38 surviving findings)
- AC: AC-04, AC-05, AC-07, AC-09, AC-10, AC-11, AC-13 | Files: `repositories/anton-abyzov/specwithcode/packages/contracts/src/logicalProject.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/memorySecretScan.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/PersonalLinkService.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/PersonalPeerSync.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/LinkedPeerRoute.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/LinkedPeerSync.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/scheduledTasks/ScheduledTaskService.ts`, `repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/PersonalAssistantLinkFlow.tsx`, `repositories/anton-abyzov/specwithcode/packages/shared/src/personalAssistantMigration.ts` | Test: `cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/project/PersonalLink.threeSeat.test.ts apps/server/src/project/LinkedMemorySync.test.ts`

### T-13 Per-machine switch, account link id and owner-only control
- AC: AC-03, AC-15, AC-16, AC-23 | Files: `repositories/anton-abyzov/specwithcode/packages/contracts/src/personalLink.ts`, `repositories/anton-abyzov/specwithcode/packages/contracts/src/settings.ts`, `repositories/anton-abyzov/specwithcode/packages/shared/src/personalAssistant.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/PersonalShare.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/PersonalShare.test.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/PersonalLinkService.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/auth/RpcAuthorization.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/cli/percy.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/cli/percy.test.ts` | Test: `cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/project/PersonalShare.test.ts apps/server/src/cli/percy.test.ts apps/server/src/auth/RpcAuthorization.personalData.test.ts`

### T-14 Seats link themselves: reconciler, peer paths, either-direction driver
- AC: AC-17, AC-18 | Files: `repositories/anton-abyzov/specwithcode/apps/server/src/project/PersonalShareReconciler.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/PersonalShareReconciler.test.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/LinkedPeerSync.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/LinkedPeerRoute.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/handoff/handoffPeers.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/handoff/handoffRoute.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/handoff/linkedSyncWire.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/fleet/personalSyncPolicy.ts`, `repositories/anton-abyzov/specwithcode/packages/shared/src/linkedPairSync.ts` | Test: `cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/project/PersonalShareReconciler.test.ts apps/server/src/fleet/personalSyncPolicy.test.ts apps/server/src/project/LinkedPeerRoute.personal.test.ts`

### T-15 Automatic lossless first merge and per-assistant undo
- AC: AC-13, AC-19 | Files: `repositories/anton-abyzov/specwithcode/apps/server/src/project/personalAutoMerge.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/personalAutoMerge.test.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/personalRestorePoint.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/personalRestorePoint.test.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/PersonalLinkService.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/PersonalLink.threeSeat.test.ts`, `repositories/anton-abyzov/specwithcode/packages/shared/src/personalAssistantMigration.ts` | Test: `cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/project/personalAutoMerge.test.ts apps/server/src/project/personalRestorePoint.test.ts apps/server/src/project/PersonalLink.threeSeat.test.ts`

### T-16 Web: the switch in Settings, one Percy row, one chat list, no wizard
- AC: AC-11, AC-12, AC-20, AC-21, AC-22, AC-23 | Files: `repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/AideSetting.tsx`, `repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/PercySharedSetting.tsx`, `repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/PercySharedSetting.test.tsx`, `repositories/anton-abyzov/specwithcode/apps/web/src/studio/personalAssistant.ts`, `repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/assistantEntries.ts`, `repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/StudioSidebar.tsx`, `repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx`, `repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/PersonalAssistantLinkFlow.tsx`, `repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/PersonalAssistantMergeDialog.tsx`, `repositories/anton-abyzov/specwithcode/apps/web/tests/one-percy` | Test: `cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/settings/PercySharedSetting.test.tsx src/components/studio/assistantEntries.test.ts src/studio/personalAssistant.linkOffer.test.ts`

### T-17 iPhone: one Percy in the Swift app
- AC: AC-14, AC-23 | Files: `repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCSync/ShellSummaries.swift`, `repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCFeatures/Drawer/DrawerView.swift`, `repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Sources/SWCFeatures/Drawer/SidebarView.swift`, `repositories/anton-abyzov/specwithcode/apps/ios/SWCKit/Tests/SWCSyncTests/ShellSummariesTests.swift` | Test: `cd repositories/anton-abyzov/specwithcode/apps/ios && make test-core`

### T-18 Adversarial review of the rework (Gemini 4 Neon, high effort) and fixes
- AC: AC-03, AC-13, AC-15, AC-17, AC-18, AC-19 | Files: `.specweave/increments/1448-link-personal-assistant-across-your-own-machines/reports/reviews` | Test: `cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/project/PersonalLink.threeSeat.test.ts`

### T-19 Release the first build and join the owner's machines
- AC: AC-26 | Files: `.specweave/increments/1448-link-personal-assistant-across-your-own-machines/reports/rollout.md` | Test: `specwithcode percy status` on each reachable machine, and a headless screenshot of the sidebar on M5

### T-20 Second release: read-only chat copies and Continue here
- AC: AC-24, AC-25 | Files: `repositories/anton-abyzov/specwithcode/apps/server/src/project/PersonalChatCopies.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/project/PersonalChatCopies.test.ts`, `repositories/anton-abyzov/specwithcode/apps/server/src/handoff/linkedSyncWire.ts`, `repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/PersonalChatCopy.tsx`, `repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/PersonalChatCopy.test.tsx` | Test: `cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/project/PersonalChatCopies.test.ts`

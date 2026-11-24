# Personal assistant permissions and distinct icons

## Problem

A personal assistant (Percy) holds a person's own data: Gmail, Calendar, Drive, chats that quote them, memory about the person, routines and a Telegram chat. A code project holds a repository. SpecWithCode treats access to both mostly the same way, and the sidebar draws every assistant with the same violet bell.

Anton, November 13, 2026: "I could connect a machine, and a person could be okay with using the projects totally. But a personal assistant is something that is connected to personal data, and it could be his own email. So we might want to ask for explicit permissions for it, not just like all other regular projects. Maybe when setting up a personal assistant, you should be able to choose the icon. Ideally, it should not be replicating the same." His sidebar showed "PercyM1 (m1)" and "Percy (m4)" with one icon.

Audit of `anton-abyzov/specwithcode` main `277534631` (file references in the Threat model below):

- Agents of another machine are already kept out of the assistant's project, chats, memory and routines (`projectInGrant` refuses a personal project even under an "all projects" grant).
- Google data is gated per project only. A thread another machine started here, in a project the owner gave Gmail, reads the owner's mail as if the owner had started it. No machine is ever named in the permission, and no call is logged.
- Another machine's key (coordinator principal) is accepted on the app's own connection and holds `settings:write`, so by scope it may switch a project's Google access on or re-point the Telegram chat.
- Any paired app or phone session with `orchestration:read` receives the assistant's chats. Hiding another machine's assistant is done in the client only.

## Threat model

Assets, most sensitive first: Google mail, calendar and files; assistant chats (they quote the former); memory about the person; routines and their outputs; the Telegram chat; Google and Telegram tokens.

| # | Who | Path today | Result today | After this increment |
|---|---|---|---|---|
| T1 | Agent of a linked machine, under a work grant | MCP tools on the assistant's project, threads, memory, routines | Refused (`workGrantPolicy.ts:252`, `workGrantAccess.ts`) | Unchanged, covered by a test |
| T2 | Thread a linked machine started in a granted project | `studio_google_*` in a project with Google on | **Reads mail, calendar, files** | Refused unless the owner allowed that machine that source; logged |
| T3 | A linked machine's key on the app connection | `googleAccount*` and `telegramChannel*` writes, `googleAccountStatus` | **Allowed by scope** | Refused: owner only |
| T4 | A linked machine's key on the app connection | Shell and thread streams, memory and routine reads of the assistant | **Allowed by scope** | Open, see Out of scope |
| T5 | Paired app or phone session of another person | Same streams | **Receives the assistant's chats** | Open, see Out of scope |
| T6 | Local MCP client with no thread | `studio_thread_search`, thread reads | **Can read assistant threads** | Open |
| T7 | Whoever holds the paired Telegram chat | Messages drive the assistant and its Google access | By design, one paired chat | Open (documented) |
| T8 | Icons | Two assistants look the same, so a person may type private text into the wrong one | Same bell | Distinct by default |

Rules this increment sets:

1. Personal data is never implied by a machine link, a work grant or a project's own Google switch. It is its own permission, held by the machine that owns the data.
2. The permission names a grantee machine and a source: Gmail, Calendar or Drive. Chats, memory and routines of the assistant stay private to the machine and are not grantable.
3. Default is nothing. A refused call is recorded as a request. Only the owner, in the owning machine's Settings, turns a source on or off; an agent, an MCP tool and another machine's key cannot.
4. Every grant, revoke, refusal and allowed read is written to a log the owner can read in Settings.

## Scope

In:

- Per-machine, per-source personal data permission on the server, with requests and a log.
- Google tools check it for work another machine started.
- Google account and Telegram settings calls refuse another machine's key.
- Settings > Google shows the machines, their three switches, pending requests and the log.
- Icon and colour choice when setting up an assistant, with a distinct suggestion; existing assistants that share the starting bell get distinct icons; rename stays as it is.
- Web and desktop (one bundle). iPhone and Android draw the saved icon already; the suggestion set is limited to icons each draws as a different symbol.

Out (each stays open in project memory `project_open_product_gaps`):

- T4 and T5: hiding the assistant from another person's paired app, phone or machine key on the app connection. It needs a per-session "may see the assistant" flag carried from the pairing link through session renewal, and filtering of every shell and thread stream. Design: default off for new pairing links ("Also show my personal assistant"), existing sessions listed with a switch.
- T6, T7.
- A grant screen in the iPhone app (needs a Mac to build). The server check protects the phone path regardless.
- One Percy with seats across a person's machines (increment 1269). Distinct icons apply between different assistants; seats of one Percy would share its icon.

## Acceptance Criteria

- [ ] AC-01: A thread started by another machine's work calling a Google read tool is refused while that machine has no permission for that source, with a message that names the machine, the source and where the owner allows it.
- [ ] AC-02: After the owner allows that machine one source (for example Gmail), that source's tools work for its threads and the other sources stay refused; turning it off refuses again.
- [ ] AC-03: A thread the owner started, and the assistant's own threads, use Google exactly as before.
- [ ] AC-04: A refused call appears once per machine and source as a pending request; allowing or dismissing it clears it.
- [ ] AC-05: Grant, revoke, refusal and allowed use are each written to the log with time, machine and source; the log is capped and survives a restart.
- [ ] AC-06: Changing or reading these permissions, changing Google account or Telegram settings, and reading Google account status are refused for another machine's key even when it holds the scope.
- [ ] AC-07: An agent of another machine still cannot read or change the assistant's project, threads, memory or routines (existing behaviour, asserted).
- [ ] AC-08: Settings > Google lists each machine that may run work here with Gmail, Calendar and Drive switches, the pending requests with Allow and Dismiss, and the recent log.
- [ ] AC-09: Setting up an assistant shows icon and colour choices; with another assistant listed, the preselected icon differs from it in glyph and colour, and an icon already in use says whose it is.
- [ ] AC-10: The created assistant carries the chosen icon and colour in the sidebar; the first assistant with nothing chosen keeps the bell.
- [ ] AC-11: Two existing assistants that both show the starting bell end with different icons without the user doing anything; the earliest keeps the bell; an icon a person chose is never changed; every client computes the same result.
- [ ] AC-12: Rename still works for an assistant and is unaffected.

## Approach

Repository: `anton-abyzov/specwithcode`, fresh clone at `~/.specwithcode/ministorm/worktrees/assistant-permissions`, branch `feat/assistant-permissions-icons`.

1. `packages/shared/src/assistantIcon.ts`: suggestion set, `suggestAssistantIcon`, `assistantIconChoices`, `distinctAssistantIconPlan` (deterministic: sorted by creation time, machine, id).
2. `packages/contracts/src/personalDataAccess.ts` and `rpc.ts`: sources, status, set-access input, two RPCs.
3. `apps/server/src/personalData/PersonalDataAccess.ts`: state in `<stateDir>/personal-data-access.json`, log in `personal-data-access-log.jsonl`.
4. `apps/server/src/mcp/toolkits/google/handlers.ts`: resolve the caller's work grant; require the source permission for its machine.
5. `apps/server/src/auth/RpcAuthorization.ts`: owner-only set gains Google account, Telegram and the new RPCs.
6. `apps/web/src/components/settings/PersonalDataAccessSection.tsx` under Settings > Google.
7. `apps/web/src/components/studio/AssistantIconChoice.tsx` in the palette's setup step; `useDistinctAssistantIcons` applies the upgrade plan through the normal project update with a fixed command id per project.

Rejected: reusing `AccessRequests` grants (no grantee dimension, and the grantee's own thread could answer its card); a contract change to project create (the chosen icon is applied with the existing project update, so older servers work); server-side icon migration (one server cannot see other machines' assistants).

Risk: owner-only refusals for Google and Telegram settings apply to another machine's key only; the owner's own app and paired devices are unaffected.

## Decisions

### Asked
- none (non-interactive run; Anton's message is the brief)

### Defaulted (change any before sw-do)
- D-01 Grantee is a machine, the unit a work grant already names → machine (a person identity does not exist in the auth model yet).
- D-02 Sources are Gmail, Calendar, Drive; assistant chats, memory and routines are not grantable → private.
- D-03 Requests are answered in the owning machine's Settings, not on a card in the asking thread → Settings (the asking machine can see and answer cards in that thread, so a card would let it approve itself).
- D-04 "Same icon" means same glyph whatever the colour; the suggestion also avoids used colours.
- D-05 The first assistant keeps the bell; only later ones start on another icon.
- D-06 Upgrade changes only assistants still on the untouched starting bell, and only when two collide.

### Open
- T4/T5 session-level visibility (next increment, needs Anton's acceptance on two accounts).

## Tasks

### T-01 Icon suggestion and upgrade plan
- AC: AC-09, AC-11 | Files: packages/shared/src/assistantIcon.ts, packages/shared/src/assistantIcon.test.ts | Test: cd packages/shared && node ../../node_modules/vite-plus/bin/vp test run src/assistantIcon.test.ts

### T-02 Personal data permission store, requests and log
- AC: AC-04, AC-05 | Files: packages/contracts/src/personalDataAccess.ts, apps/server/src/personalData/PersonalDataAccess.ts, apps/server/src/personalData/PersonalDataAccess.test.ts | Test: cd apps/server && node ../../node_modules/vite-plus/bin/vp test run src/personalData/PersonalDataAccess.test.ts

### T-03 Google tools require the permission for another machine's work
- AC: AC-01, AC-02, AC-03, AC-07 | Files: apps/server/src/mcp/toolkits/google/handlers.ts, apps/server/src/personalData/personalDataGate.ts, apps/server/src/personalData/personalDataGate.test.ts | Test: cd apps/server && node ../../node_modules/vite-plus/bin/vp test run src/personalData

### T-04 Owner-only RPCs
- AC: AC-06 | Files: apps/server/src/auth/RpcAuthorization.ts, apps/server/src/auth/RpcAuthorization.test.ts, packages/contracts/src/rpc.ts, apps/server/src/ws.ts | Test: cd apps/server && node ../../node_modules/vite-plus/bin/vp test run src/auth/RpcAuthorization.test.ts

### T-05 Settings section
- AC: AC-08 | Files: apps/web/src/components/settings/PersonalDataAccessSection.tsx, apps/web/src/components/settings/PersonalDataAccessSection.test.tsx, apps/web/src/components/settings/GoogleAccountSettings.tsx | Test: cd apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/settings/PersonalDataAccessSection.test.tsx

### T-06 Icon and colour at setup, distinct icons on upgrade
- AC: AC-09, AC-10, AC-11, AC-12 | Files: apps/web/src/components/studio/AssistantIconChoice.tsx, apps/web/src/components/studio/AssistantIconChoice.test.tsx, apps/web/src/components/CommandPalette.tsx, apps/web/src/hooks/useNewProject.ts, apps/web/src/hooks/useDistinctAssistantIcons.ts | Test: cd apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/studio/AssistantIconChoice.test.tsx

### T-07 Headless before and after screenshots, typecheck, PR, merge, hand SHA to the release owner
- AC: AC-08, AC-09, AC-10 | Files: apps/web/tests/assistant-identity/ | Test: node apps/web/tests/assistant-identity/verify.mjs <report-dir>

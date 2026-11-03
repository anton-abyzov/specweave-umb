# Aide proactive by default: briefing set up, reply approval card sends

## Problem

Aide's proactive briefing (#1046) exists but nobody gets it unless they ask Aide or save it from Routines. When it runs, it saves Gmail drafts and stops: nothing alerts the person, and replying still means opening Gmail and sending each draft by hand. The owner asked (2026-11-03) for Aide to be proactive by default: push alerts, proposed replies to approve.

## Scope

In: the briefing routine is set up automatically for this machine's Aide once Gmail or Calendar is granted to it; the briefing ends with a reply card (one question per draft, Send / Don't send) that shows in the thread, marks it Waiting on you and pushes to the phone; a send tool sends only a draft the person approved on that card, checked by the server. Out: calendar invite answers (needs the calendar.events scope), mail-triggered check-ins between briefings, a rating UI.

## Acceptance Criteria

- [ ] AC-01: When Aide is on and the Google account grants Gmail or Calendar to this machine's personal assistant, one enabled "Proactive briefing" routine (daily 08:00, own thread, `/proactive-briefing`) exists for it, created once per account; an existing briefing is kept, and one the person deleted is not recreated for the same account.
- [ ] AC-02: `studio_google_gmail_propose_send` reads each draft from Gmail and shows one card in the calling thread with a question per draft (recipient, subject, the reply text) and the options Send / Don't send; the thread waits on the person, which alerts them like any question.
- [ ] AC-03: `studio_google_gmail_send_draft` sends a draft only when that card in the same thread was answered Send for that draft; an unanswered card, Don't send, a typed answer, another thread's card or another draft are refused, and nothing is sent.
- [ ] AC-04: The briefing prompt and Aide's instructions use the card: drafts are proposed for sending at the end of the briefing, sent only after Send, and the briefing still never sends, archives or answers invitations on its own.

## Approach

- `apps/server/src/integrations/google/GoogleApi.ts`, `GoogleAccountService.ts`: `gmailDraft` (GET drafts/{id}, format full) and `gmailSendDraft` (POST drafts/send), both under the existing `gmailDrafts` (gmail.compose) service; no new scope. Account state gains optional `briefingSetUp: projectId[]`, reset with a new account.
- `apps/server/src/mcp/toolkits/google/sendApproval.ts` (new): builds the card (request id `gmail-send:<thread>:<hash of draft ids>`, question id `draft:<id>`) through `user_input_request.record`, the same command `ask_user` uses, and checks a resolved answer (also its `update-reopen:` copy) before a send. Tools in `tools.ts`/`handlers.ts`.
- `apps/server/src/project/AideBriefingSetup.ts` (new): a reactor at server start and every 10 minutes; for the machine's assistant with Gmail or Calendar granted and Aide on, creates the routine through `ScheduledTaskService.upsert` unless a briefing exists, then records the project in `briefingSetUp`.
- `packages/shared/src/routineTemplates.ts`, `ProjectWorkspaceService.ts`: prompt text.
- Rejected: a Destructive-annotated send tool relying on provider approval (full-access threads auto-approve, so the person might never see it); recreating the routine on every restart (ignores a deletion).

## Decisions

### Asked
- D-01 Build briefing auto-setup + alert, then reply approval card → yes, autonomously, deploy and verify (owner, 2026-11-03)
### Defaulted (change any before sw-do)
- D-02 Alert = the reply card's Waiting on you state (existing push path), not a new push type → reversible
- D-03 Send reuses gmail.compose (drafts.send); no gmail.send scope → reversible
### Open
- none

## Tasks

### T-01 Gmail draft read and send in the Google service
- AC: AC-03 | Files: apps/server/src/integrations/google/GoogleApi.ts, apps/server/src/integrations/google/GoogleAccountService.ts, apps/server/src/integrations/google/googleAccountLogic.ts, apps/server/src/integrations/google/GoogleAccountService.test.ts | Test: pnpm --filter @specweave-studio/server exec vitest run src/integrations/google

### T-02 Reply approval card and approved-only send tools
- AC: AC-02, AC-03 | Files: apps/server/src/mcp/toolkits/google/sendApproval.ts, apps/server/src/mcp/toolkits/google/tools.ts, apps/server/src/mcp/toolkits/google/handlers.ts, apps/server/src/mcp/toolkits/google/sendApproval.test.ts | Test: pnpm --filter @specweave-studio/server exec vitest run src/mcp/toolkits/google

### T-03 Briefing set up automatically for Aide
- AC: AC-01 | Files: apps/server/src/project/AideBriefingSetup.ts, apps/server/src/project/AideBriefingSetup.test.ts, apps/server/src/server.ts | Test: pnpm --filter @specweave-studio/server exec vitest run src/project/AideBriefingSetup

### T-04 Briefing prompt and Aide instructions use the card
- AC: AC-04 | Files: packages/shared/src/routineTemplates.ts, packages/shared/src/routineTemplates.test.ts, apps/server/src/project/ProjectWorkspaceService.ts | Test: pnpm --filter @specweave-studio/shared exec vitest run src/routineTemplates && pnpm --filter @specweave-studio/server exec vitest run src/project/ProjectWorkspaceService

### T-05 Verify and close 1191
- AC: AC-01, AC-02, AC-03, AC-04 | Files: none | Test: specweave verify 1191

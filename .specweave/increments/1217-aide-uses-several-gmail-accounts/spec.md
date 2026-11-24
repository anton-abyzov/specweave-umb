# Aide uses several Gmail accounts

## Problem

The owner has several Gmail accounts and wants Aide (the personal assistant) to read, brief on and reply from each of them. SpecWithCode's built-in Google sign-in keeps one account per host: one refresh token (`google-refresh-token`) and one `GoogleAccountState`. Signing in with a second account replaces the first and resets every project's switches and the briefing record (`completeSignIn`, `newAccount` branch in `apps/server/src/integrations/google/GoogleAccountService.ts`). The comparison of options (several MCP servers, one multi-account connector, Chrome profiles, IMAP app passwords) is in the doc "Aide across several Gmail accounts"; the owner approved building the multi-account built-in sign-in on 2026-11-03.

## Scope

In: up to ten Google accounts per host, each with its own token, granted services, label and per-project switches; a per-project default account; an optional `account` on the search and list tools (address, label or `all`); account-qualified ids so reads, drafts and sends use the receiving mailbox; the Send card names the sending address; the briefing covers every account; migration of saved one-account state; settings UI; docs and privacy page. Out: per-account OAuth clients, Chrome-profile or IMAP access, Google app verification.

## Acceptance Criteria

- [ ] AC-01: A host that saved one account before the update keeps it as the primary account, with its switches, briefing record and bare ids, after the update and after a restart.
- [ ] AC-02: Signing in with another address adds a second account beside the first (account chooser shown); reconnecting a saved address keeps its switches and label; one account can be disconnected or removed while the others keep working.
- [ ] AC-03: Agents search Gmail, Calendar and Drive in the project's default account, a named account (address or label) or every account (`all`); a name the project may not use returns the accounts it may use; ids carry their account so read, draft and send reach that mailbox with that account's token.
- [ ] AC-04: The reply card shows the address each draft is sent from, and a draft is sent from the mailbox that received the message.
- [ ] AC-05: Settings > Google account lists every account with a label field, Reconnect, Disconnect and Remove, adds another account, switches project access per account and sets a project's default account.
- [ ] AC-06: The briefing prompt covers every account, and adding an account never creates a second briefing.

## Approach

State v2 in `googleAccountLogic.ts` (`accounts[]`, per-account project switches, `defaults`), read from v1 by `readGoogleAccountState`. The primary account keeps the `google-refresh-token` secret and bare ids; added accounts use `google-refresh-token-<id>` with a 12-hex id from the address hash, and ids `<id>:<gmail id>`. `GoogleAccountService` keeps tokens, access tokens and errors per account; status keeps the old top-level fields for the first account and adds `accounts` and `defaults`. RPC: `disconnect` takes `{account?, forget?}`, `setProjectAccess` takes `{account?, makeDefault?}`, new `googleAccount.setLabel`. Rejected: one MCP server per account (duplicated tools, third-party token custody, no Send card), Chrome profiles (UI scraping, full session power), IMAP app passwords (full mailbox access, no Calendar/Drive).

## Decisions

### Asked
- D-01 Which approach → multi-account built-in Google sign-in (owner, 2026-11-03).
### Defaulted (change any before sw-do)
- D-02 Default account is per project; without a choice it is the first account the project may read.
- D-03 A new account starts on for Personal projects only, like the first account.
### Open
- none

## Tasks

### T-01 Multi-account Google sign-in, tools, settings and briefing
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: apps/server/src/integrations/google/GoogleAccountService.ts, apps/server/src/integrations/google/googleAccountLogic.ts, apps/server/src/integrations/google/googleAccountHealth.ts, apps/server/src/mcp/toolkits/google/tools.ts, apps/server/src/mcp/toolkits/google/sendApproval.ts, packages/contracts/src/googleAccount.ts, packages/contracts/src/rpc.ts, apps/web/src/components/settings/GoogleAccountSettings.tsx, packages/shared/src/routineTemplates.ts, scripts/studio-google/verify.mjs, docs/studio/google-account.md | Test: node /private/tmp/claude-501/-Users-antonabyzov-Projects-github-specweave-umb/5a9e42b4-359d-4e46-8c25-b1ea1a579678/scratchpad/swc/scripts/studio-google/verify.mjs /Users/antonabyzov/.specwithcode/m4/evidence/google-multi-account

### T-02 Verify and close 1217
- AC: AC-01 | Files: .specweave/increments/1217-aide-uses-several-gmail-accounts/spec.md | Test: specweave verify 1217-aide-uses-several-gmail-accounts

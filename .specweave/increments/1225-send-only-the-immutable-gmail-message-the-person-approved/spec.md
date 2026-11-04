# Send only the immutable Gmail message the person approved

## Problem
A reply card currently approves a mutable Gmail draft ID and truncated content. Edits after approval can change recipients/body and hidden recipients or attachments are absent from the card. A retry can send twice.

## Scope
In: immutable full raw-MIME snapshots for supported text/plain replies, complete preview, account binding, atomic durable single-use attempts, source-draft retention, mocked regression tests. Out: live Gmail calls, account changes, integration/release before manual auth acceptance, attachment/HTML approval UI. Unsupported or oversized MIME fails closed with explicit Gmail handoff.

## Acceptance Criteria
- [ ] AC-01: Approval binds project, chat, exact account credential identity and complete raw MIME; edited content receives a new card and legacy cards cannot send.
- [ ] AC-02: Cards show full From/To/Cc/Bcc/subject/body without truncation; malformed or unsupported MIME including attachments fails closed.
- [ ] AC-03: Sending posts only the immutable approved raw message, retains the source draft, and atomically consumes the approval before network I/O across concurrent calls/restarts; ambiguous results cannot auto-retry.
- [ ] AC-04: Meaningful mocked service/card tests cover races, mutation, account replacement, duplicate headers, hidden recipients, restart and ambiguous sends; independent review and manual acceptance checklist preserved.

## Approach
Use existing protected ServerSecretStore rather than a new database schema. Hold the account mutation lock while resolving the account/token and performing approval sends. Raw content fingerprints bind every byte plus project/chat/account credentials; store only opaque IDs in cards. Use messages.send, never mutable drafts.send. A durable exclusive attempt marker prevents repeated submissions even after uncertain responses or interruption. Supported text/plain only; refuse anything the card cannot faithfully show. Main integration remains owned by the product review chat.

## Decisions
### Asked
- Dedicated review worktrees and completing remaining fixes authorized by Anton; delegated lane may prepare but must not merge/install auth changes before manual acceptance.
### Defaulted (change any before sw-do)
- Preserve source drafts, clearly disclose retention, require fresh proposal on edits; unsupported attachments/HTML are reviewed in Gmail instead.
### Open
- Manual auth/UI acceptance requires Anton after reviewable implementation.

## Tasks
### T-01 Implement and regress immutable Gmail approval
- AC: AC-01, AC-02, AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/integrations/google/GmailSendApproval.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/integrations/google/GmailSendApproval.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/integrations/google/GoogleAccountService.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/integrations/google/GoogleAccountService.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/mcp/toolkits/google/sendApproval.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/mcp/toolkits/google/sendApproval.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/mcp/toolkits/google/tools.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specwithcode-dev/review-gmail-immutable-approval && PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH node node_modules/vite-plus/bin/vp test run apps/server/src/integrations/google/GmailSendApproval.test.ts apps/server/src/integrations/google/GoogleAccountService.test.ts apps/server/src/mcp/toolkits/google/sendApproval.test.ts
### T-02 Verify and close 1225 after independent review and manual auth acceptance
- AC: AC-04 | Files: reports/gmail-immutable-approval.md | Test: independent exact-head review plus Anton manual auth/UI acceptance; no live sends in automated checks

### T-03 Correct independent-review MIME fidelity and connection disclosure
- AC: AC-01, AC-02, AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/integrations/google/GmailSendApproval.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/integrations/google/GmailSendApproval.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/settings/GoogleAccountSettings.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/google-send-approval/ | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specwithcode-dev/review-gmail-immutable-approval && PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH node node_modules/vite-plus/bin/vp test run apps/server/src/integrations/google/GmailSendApproval.test.ts apps/server/src/integrations/google/GoogleAccountService.test.ts apps/server/src/mcp/toolkits/google/sendApproval.test.ts; additional exact build/headless/lint commands and receipts in gmail-immutable-implementation.md

### T-04 Reject ASCII transfer-byte BOM ambiguity found by re-review
- AC: AC-02, AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/integrations/google/GmailSendApproval.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/integrations/google/GmailSendApproval.test.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specwithcode-dev/review-gmail-immutable-approval && PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH node node_modules/vite-plus/bin/vp test run apps/server/src/integrations/google/GmailSendApproval.test.ts apps/server/src/integrations/google/GoogleAccountService.test.ts apps/server/src/mcp/toolkits/google/sendApproval.test.ts

### T-05 Align headless fixture with real light/dark theme context
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/tests/google-send-approval/main.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/google-send-approval/verify.mjs | Test: owning worktree fixture build and explicit-headless verifier; inspect desktop/narrow dark/light screenshots with production theme surfaces

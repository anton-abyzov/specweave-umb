# Review: 1191 Aide proactive briefing and reply Send card

Fresh-context review of PR #1272 (specwithcode-dev), before merge.

## Findings

1. High, fixed: an agent could answer its own Send card through `studio_pending_request_respond`. That tool now refuses `gmail-send:` ids, including `update-reopen:` copies (`apps/server/src/mcp/toolkits/thread/handlers.ts`, tests in `core.test.ts`).
2. Low, fixed: `proposeSend` reused the closed original card instead of the reopened pending one; it now prefers a pending card in the family.

## Live check (1.0.169, M4)

- Aide on; exactly one "Proactive briefing" routine (daily 08:00, `/proactive-briefing`); the existing one was kept, no duplicate.
- 2026-11-03 13:00Z run succeeded on the new build. It surfaced one email needing the owner's input and saved no draft, so no Send card was due.

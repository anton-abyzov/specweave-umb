# Verify — 1191-aide-proactive-by-default-briefing-set-up-reply-approval-card-sends

PASS · 2026-11-04T09:37:25.493Z · commands from explicit

## Commands

### `gh run view 41596644774 -R anton-abyzov/specwithcode-dev --json conclusion --jq .conclusion | grep -qx success && gh pr view 1272 -R anton-abyzov/specwithcode-dev --json state --jq .state | grep -qx MERGED` → exit 0 (1s)

```
(no output)
```

## Acceptance criteria

4/4 met

| AC | Met | Text |
|---|---|---|
| AC-01 | x (tasks) | When Aide is on and the Google account grants Gmail or Calendar to this machine's personal assistant, one enabled "Proactive briefing" routine (daily 08:00, own thread, `/proactive-briefing`) exists for it, created once per account; an existing briefing is kept, and one the person deleted is not recreated for the same account. |
| AC-02 | x (tasks) | `studio_google_gmail_propose_send` reads each draft from Gmail and shows one card in the calling thread with a question per draft (recipient, subject, the reply text) and the options Send / Don't send; the thread waits on the person, which alerts them like any question. |
| AC-03 | x (tasks) | `studio_google_gmail_send_draft` sends a draft only when that card in the same thread was answered Send for that draft; an unanswered card, Don't send, a typed answer, another thread's card or another draft are refused, and nothing is sent. |
| AC-04 | x (tasks) | The briefing prompt and Aide's instructions use the card: drafts are proposed for sending at the end of the briefing, sent only after Send, and the briefing still never sends, archives or answers invitations on its own. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | claude@antons-macbook-m4max | cd /Users/antonabyzov/.specwithcode/m4/scratch/2026-11-03-a… |  |
| T-02 | done | claude@antons-macbook-m4max | cd /Users/antonabyzov/.specwithcode/m4/scratch/2026-11-03-a… |  |
| T-03 | done | claude@antons-macbook-m4max | cd /Users/antonabyzov/.specwithcode/m4/scratch/2026-11-03-a… |  |
| T-04 | done | claude@antons-macbook-m4max | cd /Users/antonabyzov/.specwithcode/m4/scratch/2026-11-03-a… |  |
| T-05 | done | claude@antons-macbook-m4max | verify --cmd: PR #1272 merged, Checks run 41596644774 succe… |  |

5/5 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open

# Handoff — 0884-subscription-switching 0884 Subscription switching and verified local proxy fleet
agent: codex@antons-macbook-m4max · 2026-10-07T08:18:59.684Z · branch codex/0884-subscription-evidence @ ae0d62d5 · tree: clean · redactions: 0
active claims: none

## Where I left off
Why: Installed implementation verified; waiting for manual UI acceptance, native network consent and subscription sign-ins
Source commit00fafd0ed is in draft PR1980. The identical45b0 bundle is installed on M4, M1 and M3 under GUI501. Companion30/30, installer14/14 and AnyModel532/532 tests passed. Twelve real headless views and native Codex runs passed across all three hosts. Dirty tracked checkpoint/restoration passed. Scoped SpecWeave verification passed all five tasks and mapped all eight ACs; manual acceptance and closure remain pending.

Intent board: .specweave/intents/board.jsonl — 0 open intents (planning state, not verification).

[Open the intent board](../../intents/board.jsonl)
Increment 0884-subscription-switching (active) · tasks 5/5 done · ACs 0/8
Gotcha: M1 login is anton, UID501, home /Users/antonabyzov; admin authenticates separately under UID502. M1 and M3 share one Codex quota identity; M4 differs. Legacy Claude oauth_token identities remain gated even with manual quota/allow-unknown. The actual M4 weekly limit and M1 billing failure are preserved. Do not copy native OAuth credentials or take over other sessions. Old final-named receipts are historical; reviewed45b0 receipts are authoritative.

## Done / Pending
| Task | State | By | Evidence / note |
|---|---|---|---|
| T-01 Recover source context and product evidence | done | codex@antons-macbook-m4max | test -s .specweave/increments/0884-subscription-switching/re |
| T-02 Implement native profile routing, managed execution and restoration | done | codex@antons-macbook-m4max | /Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node --te |
| T-03 Build the private account dashboard | done | codex@antons-macbook-m4max | PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never SWITCH_EVIDENCE_DIR=/Us |
| T-04 Install proxies, companion and isolated T3 nightly; verify real behavior | done | codex@antons-macbook-m4max | /Users/antonabyzov/.local/bin/specweave-switch doctor → exit |
| T-05 Verify fleet and prepare worker bootstrap | done | codex@antons-macbook-m4max | bash -n /Users/antonabyzov/Projects/github/specweave-umb/rep |
5/5 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open

## Decisions
- Keep SpecWeave umbrella name; installed companion SpecWeave Switch. Native CLIs own authentication and execution, portable SpecWeave ledger remains work authority.

## Files touched
Working tree clean.

## Next steps
Read reports/implementation.md and completion-proof.json in this safe evidence checkout. Await explicit UI acceptance under AGENTS.md101 and action-time approval before clicking native Tailscale Grant permissions. Additional native sign-ins and M1 Claude consumer/isolation proof remain. Run closing coverage/review gates before complete; do not merge/release based only on installation.

GitHub unit, E2E, smoke, results and supply-chain checks passed. The automated Claude reviewer failed without producing findings; the hidden error does not establish its cause. Independent source/deployment review passed.

## Resume
1. `specweave pickup` prints the next task with its acceptance criteria, claims and branch state.
2. `specweave task claim <T-id> 0884-subscription-switching` → implement → `specweave task done <T-id> --run "<test>"`.
3. Original transcript (optional): Codex: `codex resume <uuid>`.

---
<!-- Doc format v2 -->
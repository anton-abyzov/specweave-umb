<!-- specweave review: reviewer=gpt-6.2-sol model=gpt-6.2-sol family=openai author=cli depth=standard repo=. base=e3096a417170071fd2fa56d8d6421c90693e1af5 head=46ffba19e0 at=2026-11-24T21:08:57.689Z -->
# 0970 closure review (GPT-6.2 Sol on Codex, high effort, November 24, 2026)

Scope: the closure records and evidence of 0970-phone-fleet-failover (ledger, report t05-two-mac-check.md, verify.json, verify.md). No code changed in this lane. Code citations read at app commit 29d788d8cc51b30ec619acdb626ad31bebc10460.

Round 1 (head 35060d5d50): Verdict fix. (1) High: T-10 marked done before closure. Not changed: SpecWeave's close order is closing task done, verify, review recorded after verify, then specweave complete. (2) Medium: LAN restriction overstated, a peer's mint answer can append a LAN route (phoneLinks.ts:401-402, phoneLinks.test.ts:226-229). Fixed in 46ffba19e0.

Round 2 (head 46ffba19e0):

Verdict: ship

1. Medium, t05-two-mac-check.md:30. The last sentence implied a phone on Connect could learn the LAN route; LiveEngine+Fleet.swift:79 exits before the roster request on Connect. Line 34 should drop "only ... Tailscale". Applied in 9ce7af11b5875b2ec656dc890277765a20cf7d1a (wording only).

Reviewer summary: T-10's ledger entry records the passing verification. The increment correctly remains active pending specweave complete. The receipts match 40 Swift and 23 server tests, disclose the narrowed Swift scope, and show five full-suite issues outside 0970. AC-06 remains Skipped (accepted), and physical hub-off remains untested.

A first attempt on Gemini 4 Neon (Copilot Enterprise, the first-choice reviewer) failed: "You have exceeded your monthly quota". GPT-6.2 Sol is the standing second choice.

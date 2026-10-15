# 0918 release readback and remaining acceptance

Recorded 2026-10-15 by Claude Code.

## Shipped (T-02, AC-04 release part)
- Credit recovery commits d8d0422d5 ("0918: explain paid credits and resolve recovered usage warnings") and 939a796c4 ("0907: Integrate reviewed credit recovery") are ancestors of the SpecWithCode 1.0.19 source F = 1ca53135463163a59b588b2f51880645afd67941. The work first shipped in the 1.0.16 to 1.0.18 line.
- 1.0.19 (PR #190, merge 6c0032077) published 2026-10-14T23:58Z to anton-abyzov/specweave-studio and anton-abyzov/specwithcode (11 assets, digests and anonymous downloads verified). M4 native app and service, M1 and M3 services report installedVersion 1.0.19.
- Tests on F: server 8987/0 failed, desktop 1767/0, web 8106/0, client-runtime 2145/0, contracts 788/0 (`~/Projects/github/.cw-runs/srvfix/full-server.log`, `full-desktop.log`, `~/Projects/github/.cw-runs/webfix/full3.log`).
- Installed M4 1.0.19: the usage-limit card shows "Continue on another machine", "Resume when available" and "Check now". No credits action appears, which is the correct behaviour for that Codex account because it has no funded credit balance.

## Not yet evidenced (increment stays active)
- AC-01 live: a funded, eligible Codex account showing its balance and the explicit "Continue using credits" action in the installed app. Only synthetic-fixture evidence exists (`verification.md`); no funded account was available. Producing it would mean buying credits, which is out of scope without Anton.
- AC-04 manual part: Anton's manual UI acceptance of the credit recovery card, which the AC keeps explicit.
Tracked as T-03 in spec.md.

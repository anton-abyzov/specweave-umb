# 0921 release readback (T-03, AC-04)

Recorded 2026-10-15 by Claude Code.

- Acceptance: Anton accepted the composer UI and authorized merge and deployment on 2026-10-14 ("Looks good. Merge it and deploy"); see ledger note 21:04:57Z.
- Merge: PR #182 merged as 9a98eec6f34433e472e7940aa69a621d4f84e264, an ancestor of the 1.0.19 source F = 1ca53135463163a59b588b2f51880645afd67941.
- Release: SpecWithCode 1.0.19 (PR #190, merge 6c0032077) published 2026-10-14T23:58Z to anton-abyzov/specweave-studio and anton-abyzov/specwithcode, 11 assets, digests and anonymous downloads verified.
- Installed: M4 native app and service, M1 and M3 services report installedVersion 1.0.19; `/Applications/SpecWithCode.app` reads 1.0.19.
- Installed-app check on M4 1.0.19: the composer shows a single "Full access" control; no duplicate provider Allow All.
- Tests on F: server 8987/0 failed, desktop 1767/0, web 8106/0, client-runtime 2145/0, contracts 788/0 (logs `~/Projects/github/.cw-runs/srvfix/full-server.log`, `full-desktop.log`, `~/Projects/github/.cw-runs/webfix/full3.log`). `specweave verify` re-runs the focused ACP permission and composer tests on F in `~/Projects/github/cw-rel119`.

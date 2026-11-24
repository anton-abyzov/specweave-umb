# 0919 release readback and remaining acceptance

Recorded 2026-10-15 by Claude Code.

- PR #177 merge bf4981122034751100218681840b1bbcfaa23ed8 shipped in 1.0.17 (see `deployment.md`) and is an ancestor of the 1.0.19 source F = 1ca53135463163a59b588b2f51880645afd67941. 1.0.19 is installed on the M4 native app and service and on the M1 and M3 services.
- Installed M4 1.0.19 check: the thread panel shows the Resolved group with Reopen.
- Tests on F: web 8106/0 failed, server 8987/0, desktop 1767/0 (`~/Projects/github/.cw-runs/webfix/full3.log`, `~/Projects/github/.cw-runs/srvfix/`).

## Remaining (increment stays active)
- AC-04 manual UI acceptance by Anton. His 2026-10-14 message "Deploy it so I can test" authorised deployment so he could test. It is not acceptance. Tracked as T-04 in spec.md; close with `specweave complete 0919` once Anton accepts Resolve/Reopen, the four state groups and the panel resizer in the installed app.

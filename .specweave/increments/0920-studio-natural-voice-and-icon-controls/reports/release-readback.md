# 0920 release readback and remaining acceptance

Recorded 2026-10-15 by Claude Code.

- Final reviewed voice commits (42e3172d1, 415c0b41b, PR #174) are ancestors of the 1.0.19 source F = 1ca53135463163a59b588b2f51880645afd67941. The voice work first shipped in the 1.0.16 to 1.0.18 line and 1.0.19 is installed on M4 (app and service), M1 and M3 (services). This completes T-04, review and coordinated deployment.
- Tests on F: desktop 1767/0 failed, web 8106/0 (`~/Projects/github/.cw-runs/srvfix/full-desktop.log`, `~/Projects/github/.cw-runs/webfix/full3.log`).

## Remaining (increment stays active)
- AC-03 requires "Anton accepts sound and UI before closure". Anton has not given that acceptance. T-02 stays blocked on it. Close with `specweave complete 0920` after he listens to the natural local voice and optional ElevenLabs voice and accepts the icon controls in the installed app.

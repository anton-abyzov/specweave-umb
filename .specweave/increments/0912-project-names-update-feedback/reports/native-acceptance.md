# 0912 native acceptance (AC-04)

Recorded 2026-10-15 by Claude Code, closing out after the Codex owner ran out of usage.

## Release through the normal updater
- SpecWithCode 1.0.19 (private PR #190, merge 6c0032077; source F = 1ca53135463163a59b588b2f51880645afd67941) was published 2026-10-14T23:58Z to anton-abyzov/specweave-studio and anton-abyzov/specwithcode (11 assets, digests and anonymous downloads verified by the release owner).
- On the M4 native app, the normal "Check for Updates…" path detected 1.0.19 (higher than the installed 1.0.18 candidate) and installed it through "Restart to update". After relaunch the app, the M4 service and the M1 and M3 services report installedVersion 1.0.19. `/Applications/SpecWithCode.app` CFBundleShortVersionString reads 1.0.19 (re-read 2026-10-15).
- The 0912 fixes are ancestors of F: dcb41ebcf "0912: Show manual sidebar update check results" and the sidebar resolved-title change (final reviewed source 2bb52069a). They first shipped in the 1.0.16 to 1.0.18 line and remain in 1.0.19.

## Saved names on the installed app
- Background window capture of the installed 1.0.19 M4 app (no clicks): `screenshots/installed-1.0.19-names-m4.png`.
- The sidebar shows saved project titles, not repository names, including the custom proof checkouts ("jobweave M4 handoff proof", "sw-easychamp product handoff 0907", "EasyChamp handoff test 119", "jobweave product handoff 0907"). The selected sidebar entry "SpecWeave umbrella" matches the header title "SpecWeave umbrella".

## Update feedback
- The native updater gave visible feedback through the full offered → downloaded → "Restart to update" flow on 1.0.19.
- The "no newer update" and handled-error toasts of the sidebar pill are covered by SidebarUpdatePill.test.tsx on F and by the earlier rendered checks (`screenshots/*-update-result.png`, `390-error-result.png`). The sidebar pill's "up to date" toast was not clicked on the live app in this pass, to avoid touching the running workspace.

## Tests on shipped source F
Full suites on F: server 8987 passed / 0 failed, desktop 1767 / 0, web 8106 / 0, client-runtime 2145 / 0, contracts 788 / 0 (logs `~/Projects/github/.cw-runs/srvfix/full-server.log`, `full-desktop.log`, `~/Projects/github/.cw-runs/webfix/full3.log`). `specweave verify` re-runs StudioSidebar and SidebarUpdatePill tests in `~/Projects/github/cw-rel119` (at F) and the installed-version readback.

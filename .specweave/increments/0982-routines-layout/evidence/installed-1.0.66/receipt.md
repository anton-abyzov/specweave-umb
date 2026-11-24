# 0982 installed routines layout receipt (October 21, 2026)

- M4 installed: v1.0.66, sourceCommit b3648d70059f915363e042a1131d7af6c4fce8c0 (~/.specwithcode/m4/installation.json); updater state up-to-date, lastInstall 1.0.66 at 2026-10-21T14:40:45Z.
- PR #542 (515d3d7186) first shipped in v1.0.65 (tag 5b790f2712, release run 39555412711 success); v1.0.65 contains 515d3d7186 (compare: ahead, behind 0); M4 ran 1.0.65 before 1.0.66 (update receipt "before" artifactSourceCommit 5b790f2712).
- Installed client ~/.specwithcode/install/releases/46a2581c3cee7bf6ffeb/client/assets contains "No routines yet", "Manage routines", "sws-routines-list", "Last run failed", "Own thread from the first run"; "Goes to the coordinator" is absent (0 files).
- Live service http://127.0.0.1:8319/ serves index asset index-jTeirTO7.js, the same as the installed client index.html (unauthenticated GET of / only; no session, no routine touched).
- apps/web built at b3648d70059 (worktree ~/.specwithcode/m4/worktrees/routines-layout-verify): all 5 CSS assets byte-identical to the installed client.
- Headless (headless:true, PWDEBUG=0, PLAYWRIGHT_HTML_OPEN=never) fixture checks at b3648d70059 with that CSS: routines-layout-check passed, settings-presentation routines-check passed, 0980 routines-check passed. Fictional fixtures only; actions recorded, never run.
- No live SQLite access, no service restart, no real routine run/enabled/paused/deleted.

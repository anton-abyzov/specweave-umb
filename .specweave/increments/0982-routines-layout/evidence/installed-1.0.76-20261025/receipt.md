# 0982 installed routines acceptance, 1.0.76 (October 25, 2026)

Three kinds of proof, kept apart.

## 1. Live M4 service, read-only: blocked by service load

- Target `http://127.0.0.1:8319`, 1.0.76 (`sourceCommit` `4446ca4295`, which contains #542 `515d3d7186`; `installed-identity.json`). Index asset `assets/index-CBbz81Ew.js`.
- One read-only `scheduledTasks.list` over a `orchestration:read` + `diagnostics:read` pair token returned 111 real routines (90 in this project; counts only in `probe-output.txt`). Nothing was run, enabled, paused, saved or deleted; the token cannot operate.
- The browser check (`routines-readonly-check.mjs`) never rendered a routine row: Settings showed "Environment disconnected – Reconnect Anton's MacBook M4MAX to view its scheduled tasks" and `/` stayed on the splash (not captured). `specweave-studio pair` intermittently returned `NoRunningServerError` while `/` answered in 1.6–7 s. Failure receipts: `live/receipt.json`, `live/failure.png`, `run1/receipt.json`, `run1/failure.png` (both runs ended on the same screen; the two PNGs are byte-identical).
- Not a routines-layout defect and not a user blocker. The service was not restarted and no update was retried (M4 stays on 1.0.76 until the first release containing #720).

## 2. Installed 1.0.76 build, private state, synthetic routines: PASS

- `/Applications/SpecWithCode.app` 1.0.76, its bundled server (`app.asar/apps/server/dist/bin.mjs`) on a free loopback port with `--base-dir` under `~/.local/share/specweave-studio/verification/routines-installed/`, every provider disabled, auto-update off. Same index asset as the live service: `assets/index-CBbz81Ew.js`.
- 62 synthetic routines in one project (11 manual, 21 fixed time, 10 monthly, 10 interval, 10 once; 36 enabled). Enabled ones are manual, once in 2027, or due on a later weekday or month day, so none could fire during the 50-second run.
- Headless Chromium (`headless: true`, `PWDEBUG=0`, `PLAYWRIGHT_HTML_OPEN=never`), owner browser session. Script `routines-private-installed-check.mjs`, receipt `private-run/receipt.json`.

| Check | Result |
|---|---|
| Settings > Routines at 1440 / 900 / 390 px | 62 rows each, no sideways scroll, every row has a state badge, no numeric dates or raw "succeeded/never"; median row 89 / 129 / 133 px |
| Settings search "Routines" + Enter | lands on `/settings/scheduled-tasks` |
| Settings nav entry "Routines" | lands on `/settings/scheduled-tasks` |
| Project Routines pane at 1440 / 390 px | header "On MacBook M4MAX · 25 active · 26 paused · 11 on request", 62 rows, no spills, no "Goes to the coordinator", actions aligned and bordered |
| "New routine" link | `template=new` and the project |
| "Manage routines" | opens Settings > Routines for the project |
| Routine commands sent by the page | none; 13 request tags, all reads, subscriptions, asset URLs or activity pings |
| Routines after the check | unchanged (ids, enabled, last run) |

Screenshots (light and dark): `private-run/settings-routines-1440.png`, `-1440-dark`, `-900`, `-390`, `-390-dark`, `settings-search-routines.png`, `project-routines-pane-1440.png`, `-1440-dark`, `-390`, `-390-dark`, `manage-routines-landing-1440.png`.

Observation, not a failure: a weekly interval reads "Every 10080 min" (`routineCadenceLabel`); "Every 7 days" would read better.

## 3. Fixture proof (October 21)

Unchanged: `../installed-1.0.66/receipt.md` and `../verify-scope.md`. Fictional fixtures at the released source, CSS byte-identical to the installed client.

## Limits

- No live, authenticated rendering of the user's own 111 routines: section 1 is blocked by service load. Sections 2 and 3 prove the installed code and layout, not the live database.
- No real routine was run, enabled, paused, saved or deleted. No `statev2.sqlite*` access, no service restart, no update retry. The private server (spawned PID only) stopped at the end of the run.

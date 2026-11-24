# Verify — 0912-project-names-update-feedback

PASS · 2026-10-15T03:42:07.059Z · commands from explicit

## Commands

### `cd /Users/antonabyzov/Projects/github/cw-rel119 && /Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node node_modules/vite-plus/bin/vp test run apps/web/src/components/studio/shell/StudioSidebar.test.tsx apps/web/src/components/sidebar/SidebarUpdatePill.test.tsx` → exit 0 (2s)

```
note: You are running `vp test` as a Vite+ built-in command. If you meant to run the test npm script, use `vpr test` instead.

[1m[30m[46m RUN [49m[39m[22m [36mv5.0.1 [39m[90m/Users/antonabyzov/Projects/github/cw-rel119[39m

[90mstderr[2m | apps/web/src/components/sidebar/SidebarUpdatePill.test.tsx[2m > [22m[2mmanual sidebar update checks[2m > [22m[2mreports the installed version when no newer release is available
[22m[39mreact-test-renderer is deprecated. See https://react.dev/warnings/react-test-renderer

[90mstderr[2m | apps/web/src/components/sidebar/SidebarUpdatePill.test.tsx[2m > [22m[2mmanual sidebar update checks[2m > [22m[2mreports a handled check failure even when checked is true
[22m[39mreact-test-renderer is deprecated. See https://react.dev/warnings/react-test-renderer

[90mstderr[2m | apps/web/src/components/sidebar/SidebarUpdatePill.test.tsx[2m > [22m[2mmanual sidebar update checks[2m > [22m[2mkeeps rejected checks and bridge failures visible
[22m[39mreact-test-renderer is deprecated. See https://react.dev/warnings/react-test-renderer

[90mstderr[2m | apps/web/src/components/sidebar/SidebarUpdatePill.test.tsx[2m > [22m[2mmanual sidebar update checks[2m > [22m[2mwaits for the matching state event when the RPC finishes before the check event
[22m[39mreact-test-renderer is deprecated. See https://react.dev/warnings/react-test-renderer

[90mstderr[2m | apps/web/src/components/sidebar/SidebarUpdatePill.test.tsx[2m > [22m[2mmanual sidebar update checks[2m > [22m[2mreports a delayed failure and allows another manual check
[22m[39mreact-test-renderer is deprecated. See https://react.dev/warnings/react-test-renderer

[90mstderr[2m | apps/web/src/components/sidebar/SidebarUpdatePill.test.tsx[2m > [22m[2mmanual sidebar update checks[2m > [22m[2mkeeps background checks quiet
[22m[39mreact-test-renderer is deprecated. See https://react.dev/warnings/react-test-renderer

[90mstderr[2m | apps/web/src/components/sidebar/SidebarUpdatePill.test.tsx[2m > [22m[2mmanual sidebar update checks[2m > [22m[2mpreserves the download action after a newer release is offered
[22m[39mreact-test-renderer is deprecated. See https://react.dev/warnings/react-test-renderer

[90mstderr[2m | apps/web/src/components/sidebar/SidebarUpdatePill.test.tsx[2m > [22m[2mmanual sidebar update checks[2m > [22m[2mpreserves the confirmed restart action for a downloaded update
[22m[39mreact-test-renderer is deprecated. See https://react.dev/warnings/react-test-renderer

[90mstderr[2m | apps/web/src/components/sidebar/SidebarUpdatePill.test.tsx[2m > [22m[2mmanual sidebar update checks[2m > [22m[2mdoes not report an automatic download failure as a failed release check
[22m[39mreact-test-renderer is deprecated. See https://react.dev/warnings/react-test-renderer

 [32m✓[39m apps/web/src/components/sidebar/SidebarUpdatePill.test.tsx [2m([22m[2m13 tests[22m[2m)[22m[32m 25[2mms[22m[39m
 [32m✓[39m apps/web/src/components/studio/shell/StudioSidebar.test.tsx [2m([22m[2m33 tests[22m[2m)[22m[33m 408[2mms[22m[39m

[2m Test Files [22m [1m[32m2 passed[39m[22m[90m (2)[39m
[2m      Tests [22m [1m[32m46 passed[39m[22m[90m (46)[39m
[2m   Start at [22m 23:42:04
[2m   Duration [22m 2.11s[2m (transform 38%, import 32%, environment 16%, tests 14%)[22m
```

### `test "$(defaults read /Applications/SpecWithCode.app/Contents/Info CFBundleShortVersionString)" = 1.0.19 && echo installed 1.0.19` → exit 0 (0s)

```
installed 1.0.19
```

## Acceptance criteria

4/4 met

| AC | Met | Text |
|---|---|---|
| AC-01 | x (tasks) | The sidebar uses the same resolved checkout's saved project title as the header, including conflicting custom proof titles, exact remote selections and saved machine selection; grouping identity remains unchanged. |
| AC-02 | x (tasks) | Manual sidebar update checks visibly report no newer update with the installed version, and expose handled check errors; offered/downloaded update actions continue to work. |
| AC-03 | x (tasks) | Focused regressions, production build, independent review and rendered browser checks pass, and all scoped changes are pushed. |
| AC-04 | x (tasks) | A coordinated release higher than the installed candidate is detected through the normal updater, with install/relaunch and actual names/update feedback verified when the release owner yields the live app. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | codex@antons-macbook-m4max | cd repositories/anton-abyzov/specweave-studio && PATH=/User… |  |
| T-02 | done | codex@antons-macbook-m4max | cd repositories/anton-abyzov/specweave-studio && PATH=/User… |  |
| T-03 | done | codex@antons-macbook-m4max | git diff --check → exit 0 log: .specweave/increments/0912-p… |  |
| T-04 | done | cli@antons-macbook-m4max | git diff --check -- .specweave/increments/0912-project-name… |  |

4/4 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open

# Verify — 1023-add-approved-folders-while-project-work-runs

PASS · 2026-10-25T03:18:09.797Z · commands from explicit

## Commands

### `cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-1009-cursor-settings-design-20261024 && /Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node node_modules/vite-plus/bin/vp test run apps/server/src/project/ProjectService.test.ts apps/server/src/project/http.test.ts packages/contracts/src/environmentHttp.test.ts apps/server/src/project/ProjectActionRequests.test.ts apps/server/src/mcp/toolkits/project/route.integration.test.ts apps/server/src/mcp/toolkits/core.test.ts` → exit 0 (7s)

```
note: You are running `vp test` as a Vite+ built-in command. If you meant to run the test npm script, use `vpr test` instead.

 RUN  v5.0.1 /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-1009-cursor-settings-design-20261024

(node:16229) ExperimentalWarning: SQLite is an experimental feature and might change at any time
(Use `node --trace-warnings ...` to show where the warning was created)
(node:16233) ExperimentalWarning: SQLite is an experimental feature and might change at any time
(Use `node --trace-warnings ...` to show where the warning was created)
(node:16231) ExperimentalWarning: SQLite is an experimental feature and might change at any time
(Use `node --trace-warnings ...` to show where the warning was created)
(node:16232) ExperimentalWarning: SQLite is an experimental feature and might change at any time
(Use `node --trace-warnings ...` to show where the warning was created)
(node:16230) ExperimentalWarning: SQLite is an experimental feature and might change at any time
(Use `node --trace-warnings ...` to show where the warning was created)

 Test Files  6 passed (6)
      Tests  83 passed (83)
   Start at  23:18:03
   Duration  6.57s (transform 64%, import 29%, tests 6%)

  Transform  transforming modules took 18.31s · 64% of tracked time, re-done on every run
             persist transforms across runs with fsModuleCache: true
             learn more: https://vitest.dev/guide/improving-performance#caching-between-reruns
```

## Acceptance criteria

6/6 met

| AC | Met | Text |
|---|---|---|
| AC-01 | x (tasks) | While another thread in the project is running, saving Settings > Environment with one added folder succeeds and persists. Removing a folder, changing a repository `localPath` or changing the root while a thread runs is still denied. |
| AC-02 | x (tasks) | An agent can call `studio_project_request` with `action: "add_folder"` and `folder`. The user sees an approval card naming the canonical path, and approving it adds the folder even while other threads run. Declining changes nothing. |
| AC-03 | x (tasks) | Agents still cannot self-grant: `studio_project_update` folder widening is refused with a message naming `add_folder`, and `studio_pending_request_respond` cannot answer an `add_folder` card. |
| AC-04 | x (tasks) | Home, `~/.ssh`-style protected locations, already-approved folders, folders beyond the 16-folder limit, and a folder whose real path changed between request and approval are refused, and nothing changes. |
| AC-05 | x (tasks) | The refusal text for blocked environment changes says removals and changes need stopped work and that adding works while threads run. The orphaned-run notice says SpecWithCode, not Studio. |
| AC-06 | x (tasks) | The installed app on this Mac lets the specweave project approve the app checkout folder, and the 1009 successor launches bound to it. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | claude@antons-macbook-m4max | cd /Users/antonabyzov/.specwithcode/m4/worktrees/fix-additi… |  |
| T-02 | done | claude@antons-macbook-m4max | cd /Users/antonabyzov/.specwithcode/m4/worktrees/fix-additi… |  |
| T-03 | done | codex@antons-macbook-m4max | Installed bundle 1.0.75 includes merged634; project revisio… |  |
| T-04 | done | codex@antons-macbook-m4max | Closure evidence assembled: merged634 successful applicable… |  |

4/4 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open

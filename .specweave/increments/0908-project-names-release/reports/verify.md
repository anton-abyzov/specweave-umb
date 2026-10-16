# Verify — 0908-project-names-release

PASS · 2026-10-13T15:52:08.353Z · commands from explicit

## Commands

### `cd repositories/anton-abyzov/specweave-studio && PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH node node_modules/vite-plus/bin/vp test run packages/client-runtime/src/state/projectGrouping.test.ts apps/web/src/components/studio/shell/StudioSidebar.test.tsx` → exit 0 (4s)

```
note: You are running `vp test` as a Vite+ built-in command. If you meant to run the test npm script, use `vpr test` instead.

 RUN  v5.0.1 /Users/antonabyzov/.codex/worktrees/project-names-release/specweave-umb/repositories/anton-abyzov/specweave-studio


 Test Files  2 passed (2)
      Tests  50 passed (50)
   Start at  11:52:04
   Duration  3.46s (transform 46%, import 26%, environment 16%, tests 11%)

  Transform  transforming modules took 2.28s · 46% of tracked time, re-done on every run
             persist transforms across runs with fsModuleCache: true
             learn more: https://vitest.dev/guide/improving-performance#caching-between-reruns
```

### `git diff --check` → exit 0 (0s)

```
(no output)
```

## Acceptance criteria

4/4 met

| AC | Met | Text |
|---|---|---|
| AC-01 | x (tasks) | A single custom project name survives default-named copies across machines and worktrees; repository identity and fork grouping remain unchanged. |
| AC-02 | x (tasks) | Regression tests, relevant production builds, and a headless rendered check pass for the naming change. |
| AC-03 | x (tasks) | The naming fix and safe pending umbrella records are committed and pushed, with remote readback and exact remaining foreign-worktree boundaries recorded. |
| AC-04 | x (tasks) | A concrete next-release candidate is prepared from latest completed source without colliding with the active 0907 release owner; publication state and outstanding gates are explicit. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | codex-project-names | cd repositories/anton-abyzov/specweave-studio && PATH=/User… |  |
| T-02 | done | codex-project-names | /opt/homebrew/bin/python3.13 /Users/antonabyzov/Projects/re… |  |
| T-03 | done | codex-project-names | git diff --check → exit 0 log: .specweave/increments/0908-p… |  |
| T-04 | done | codex-project-names | git diff --check → exit 0 log: .specweave/increments/0908-p… |  |

4/4 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open

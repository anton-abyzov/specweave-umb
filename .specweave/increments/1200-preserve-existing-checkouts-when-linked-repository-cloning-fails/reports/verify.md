# Verify — 1200-preserve-existing-checkouts-when-linked-repository-cloning-fails

PASS · 2026-11-03T23:57:43.792Z · commands from explicit

## Commands

### `cd "$HOME/.specwithcode/m4/worktrees/specwithcode-dev/recent-features-followup-20261103/apps/server" && test "$(git rev-parse --short=10 HEAD)" = c70a90e702 && node ../../node_modules/vite-plus/bin/vp test run src/project/ProjectRepositoryPresence.test.ts` → exit 0 (2s)

```

 RUN  v5.0.1 /Users/antonabyzov/.specwithcode/m4/worktrees/specwithcode-dev/recent-features-followup-20261103/apps/server

(node:25256) ExperimentalWarning: SQLite is an experimental feature and might change at any time
(Use `node --trace-warnings ...` to show where the warning was created)

 Test Files  1 passed (1)
      Tests  15 passed (15)
   Start at  18:57:41
   Duration  1.94s (transform 68%, import 29%, tests 2%)
```

## Acceptance criteria

2/2 met

| AC | Met | Acceptance | Text |
|---|---|---|---|
| AC-01 | x (tasks) | met | A failed clone cleans up its own partial files and preserves an independently populated destination. |
| AC-02 | x (tasks) | met | Concurrent attempts for the same checkout cannot both clone. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | codex-recent-features-review | cd "$HOME/.specwithcode/m4/worktrees/specwithcode-dev/recen… |  |

1/1 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open

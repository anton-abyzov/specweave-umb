# Verify — 1320-filter-the-project-threads-panel-by-machine-agent-and-pull-request

PASS · 2026-11-03T00:21:56.780Z · commands from explicit

## Commands

### `cd /srv/work/github/specweave-umb/repositories/anton-abyzov/specweave-studio-threads-filter && pnpm exec vp test run apps/web/src/studio/threadPaneFilters.test.ts apps/web/src/studio/threadMachineFilter.test.ts apps/web/src/components/studio/ProjectWorkspace.test.tsx` → exit 0 (9s)

```

 RUN  v5.0.1 /srv/work/github/specweave-umb/repositories/anton-abyzov/specweave-studio-threads-filter


 Test Files  3 passed (3)
      Tests  83 passed (83)
   Start at  19:21:48
   Duration  8.05s (transform 41%, tests 35%, import 19%, environment 5%)

  Transform  transforming modules took 3.29s · 41% of tracked time, re-done on every run
             persist transforms across runs with fsModuleCache: true
             learn more: https://vitest.dev/guide/improving-performance#caching-between-reruns
```

## Acceptance criteria

8/8 met

| AC | Met | Acceptance | Text |
|---|---|---|---|
| AC-01 | x | met | When a project's threads run on more than one machine, the panel shows All and each machine as one-click choices, with this machine first and the rest by name, each machine with its open thread count. The order does not change as counts change. |
| AC-02 | x | met | Choosing a machine narrows every group to threads running there, is remembered per project under the existing storage key, and choosing All undoes it. A filter leaves Resolved folded and paging on. The filter lets go once one machine is left. The Machine section and "On X" pill are gone from the sort menu and header. |
| AC-03 | x | met | A filter menu offers Agent when threads use more than one agent, and Open pull request when any thread has one. The filter button does not render when it has nothing to offer. |
| AC-04 | x | met | An active agent or pull request filter shows as a removable chip in the row, is remembered per project, and machine counts reflect it. |
| AC-05 | x | met | A machine with a thread waiting on the person that the filters keep off the list shows a waiting dot on its choice, except in unattended check projects. The summary line stays project-wide, so a filter cannot silently hide a request. |
| AC-06 | x | met | When filters leave no thread, the panel says so and offers Clear filters. |
| AC-07 | x | met | Stop all and Continue all say that they ignore filters and cover every machine while any filter is on. |
| AC-08 | x | met | The row reads well in light, dark and a narrow pane, and every control has an accessible name and pressed state. Evidence is headless screenshots saved to files. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | claude@ministorm | cd /srv/work/github/specweave-umb/repositories/anton-abyzov… |  |
| T-02 | done | claude@ministorm | cd /srv/work/github/specweave-umb/repositories/anton-abyzov… |  |
| T-03 | done | claude@ministorm | thread-filter-check.mjs and machine-column-check.mjs pass h… |  |
| T-04 | done | claude@ministorm | PR 1234 merged as 9326fd887c; fresh-context review SHIP at … |  |

4/4 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open

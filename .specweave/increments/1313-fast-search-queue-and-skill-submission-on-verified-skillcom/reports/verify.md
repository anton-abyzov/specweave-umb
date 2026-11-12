# Verify — 1313-fast-search-queue-and-skill-submission-on-verified-skillcom

PASS · 2026-11-12T23:06:31.322Z · commands from config testing.commands

## Commands

- Working directory: . (config testing.commands)
### `python3 scripts/fleet-project-sync.py --self-test` → exit 0 (26s)

```
test_absent_and_idempotent (__main__.SafetyTests.test_absent_and_idempotent) ... ok
test_dirty_and_untracked_preserved (__main__.SafetyTests.test_dirty_and_untracked_preserved) ... ok
test_existing_empty_and_atomic_race_preserved (__main__.SafetyTests.test_existing_empty_and_atomic_race_preserved) ... ok
test_final_readback_detects_descendant_and_staging (__main__.SafetyTests.test_final_readback_detects_descendant_and_staging) ... ok
test_incomplete_runtime_and_release_never_pass (__main__.SafetyTests.test_incomplete_runtime_and_release_never_pass) ... ok
test_legacy_fetch_repair_preserves_dirty_or_custom_checkouts (__main__.SafetyTests.test_legacy_fetch_repair_preserves_dirty_or_custom_checkouts) ... ok
test_missing_or_diverged_upstream_is_preserved (__main__.SafetyTests.test_missing_or_diverged_upstream_is_preserved) ... ok
test_new_and_legacy_clones_fetch_and_track_future_feature (__main__.SafetyTests.test_new_and_legacy_clones_fetch_and_track_future_feature) ... ok
test_offline_bundle_and_bad_digest (__main__.SafetyTests.test_offline_bundle_and_bad_digest) ... ok
test_remote_drift_preserves_old_checkout (__main__.SafetyTests.test_remote_drift_preserves_old_checkout) ... ok
test_scoped_transport_preserves_identity_and_rejects_redirects (__main__.SafetyTests.test_scoped_transport_preserves_identity_and_rejects_redirects) ... ok
test_unpushed_commit_preserved (__main__.SafetyTests.test_unpushed_commit_preserved) ... ok
test_unsafe_paths_urls_and_symlinks (__main__.SafetyTests.test_unsafe_paths_urls_and_symlinks) ... ok

----------------------------------------------------------------------
Ran 13 tests in 25.850s

OK
```

- Working directory: . (config testing.commands)
### `python3 -m unittest discover -s tests -p test_handoff_evidence.py` → exit 0 (1s)

```
..............................................
----------------------------------------------------------------------
Ran 46 tests in 1.172s

OK
```

- Working directory: . (config testing.commands)
### `python3 scripts/release/timing.py --self-test` → exit 0 (0s)

```
.................
----------------------------------------------------------------------
Ran 17 tests in 0.290s

OK
recorded
```

- Working directory: repositories/anton-abyzov/vskill (config testing.ownerCommands)
### `npm test` → exit 0 (79s)

```
1. You might have mismatching versions of React and the renderer (such as React DOM)
2. You might be breaking the Rules of Hooks
3. You might have more than one copy of React in the same app
See https://react.dev/link/invalid-hook-call for tips about how to debug and fix this problem.

stderr | src/eval-ui/src/components/__tests__/TopRail.modelselector.test.tsx > T-060 TopRail — model selector wiring > the find-skills slot (Group A) is positioned before the model-selector slot (Group B)
Invalid hook call. Hooks can only be called inside of the body of a function component. This could happen for one of the following reasons:
1. You might have mismatching versions of React and the renderer (such as React DOM)
2. You might be breaking the Rules of Hooks
3. You might have more than one copy of React in the same app
See https://react.dev/link/invalid-hook-call for tips about how to debug and fix this problem.

 ✓ src/eval-ui/src/components/__tests__/TopRail.modelselector.test.tsx (8 tests) 9ms
 ✓ src/eval-ui/src/hooks/__tests__/useContextMenuState.test.ts (14 tests) 14ms
stderr | src/eval-ui/src/__tests__/account/AccountTauriBridge.test.ts > getAccountUserSummary (0836 US-003) > falls back to signed-out shape when the IPC throws
[AccountTauriBridge] account_get_user_summary failed: Error: keychain locked
    at [90m/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/[39msrc/eval-ui/src/__tests__/account/AccountTauriBridge.test.ts:106:13
    at mockCall [90m(file:///Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/[39mnode_modules/[4m@vitest/spy[24m/dist/index.js:96:15[90m)[39m
    at spy [90m(file:///Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/[39mnode_modules/[4mtinyspy[24m/dist/index.js:47:80[90m)[39m
    at invokeTauri [90m(/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/[39msrc/eval-ui/src/contexts/AccountTauriBridge.ts:95:19[90m)[39m
    at getAccountUserSummary [90m(/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/[39msrc/eval-ui/src/contexts/AccountTauriBridge.ts:82:19[90m)[39m
    at [90m/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/[39msrc/eval-ui/src/__tests__/account/AccountTauriBridge.test.ts:110:23
    at [90mfile:///Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/[39mnode_modules/[4m@vitest/runner[24m/dist/chunk-hooks.js:155:11
    at [90mfile:///Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/[39mnode_modules/[4m@vitest/runner[24m/dist/chunk-hooks.js:752:26
    at [90mfile:///Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/[39mnode_modules/[4m@vitest/runner[24m/dist/chunk-hooks.js:1897:20
    at new Promise (<anonymous>)

 ✓ src/eval-ui/src/__tests__/account/AccountTauriBridge.test.ts (8 tests) 11ms
 ✓ src/eval-ui/src/__tests__/StudioTokenBridge.test.ts (9 tests) 8ms
 ✓ src/eval-ui/src/hooks/__tests__/useStudioPreferences.activeAgent.test.ts (4 tests) 6ms
 ✓ src/eval-ui/src/components/__tests__/DetailHeader.copy.test.tsx (4 tests) 7ms
 ✓ src/eval-ui/src/hooks/__tests__/useStudioPreferences-skill-gen.test.ts (9 tests) 14ms
 ✓ src/eval-ui/src/utils/__tests__/toastQueue.test.ts (8 tests) 9ms
 ✓ src/eval-ui/src/components/__tests__/0800-editor-runall.test.tsx (4 tests) 9ms
 ✓ src/eval-ui/src/pages/workspace/__tests__/VersionHistoryPanel.empty-state.test.tsx (5 tests) 4ms
 ✓ src/webmcp/enumerate.e2e.test.ts (6 tests) 73171ms
   ✓ audit-webmcp against a local page (headless Chromium) > enumerates three tools, attributes the third-party one, and never executes a tool  1711ms
   ✓ audit-webmcp against a local page (headless Chromium) > records an error and keeps going when a site cannot be reached  1120ms
   ✓ audit-webmcp against a local page (headless Chromium) > never opens popups the page asks for  1091ms
   ✓ audit-webmcp against a local page (headless Chromium) > detects the Shopify storefront marker  1095ms
   ✓ audit-webmcp against a local page (headless Chromium) > a page stuck in a busy loop is recorded as an error and the batch moves on  16201ms
   ✓ audit-webmcp against a local page (headless Chromium) > relaunches the browser when it has crashed  21700ms
 ✓ src/eval-ui/src/hooks/__tests__/useStudioPreferences.test.ts (5 tests) 4ms
 ✓ src/eval-ui/src/pages/workspace/__tests__/VersionHistoryPanel.local-fallback.test.tsx (3 tests) 4ms
 ✓ src/eval-ui/src/components/__tests__/StudioLayout.test.tsx (4 tests) 4ms

 Test Files  696 passed (696)
      Tests  7814 passed | 2 skipped (7816)
   Start at  18:03:35
   Duration  77.66s (transform 38.12s, setup 0ms, collect 186.01s, tests 468.33s, environment 188.86s, prepare 84.73s)
```

- Working directory: repositories/anton-abyzov/vskill-platform (config testing.ownerCommands)
### `npm test` → exit 0 (98s)

```
 ✓ src/app/__tests__/theme-init.test.ts (5 tests) 19ms
 ✓ src/app/claude-code-skills/__tests__/hub-seo.test.tsx (5 tests) 5ms
 ✓ src/app/check/php2shell/__tests__/page.test.tsx (5 tests) 30ms
 ✓ src/remotion/__tests__/scenes-timeline.test.tsx (124 tests) 23599ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/HookProblem' > renders every sampled frame without throwing or React warnings  1066ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/HookProblem' > never goes blank once its content has appeared  704ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/BrowseGrid' > renders every sampled frame without throwing or React warnings  999ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/BrowseGrid' > never goes blank once its content has appeared  898ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/AuthorCreate' > renders every sampled frame without throwing or React warnings  453ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/AuthorEvals' > renders every sampled frame without throwing or React warnings  1030ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/AuthorEvals' > never goes blank once its content has appeared  781ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/AuthorPublish' > renders every sampled frame without throwing or React warnings  503ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/AuthorPublish' > never goes blank once its content has appeared  304ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/ConsumeInstall' > renders every sampled frame without throwing or React warnings  629ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/ConsumeInstall' > never goes blank once its content has appeared  488ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/ConsumeBugSurface' > never goes blank once its content has appeared  348ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/AuthorEditAndPublish' > renders every sampled frame without throwing or React warnings  512ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/AuthorEditAndPublish' > never goes blank once its content has appeared  426ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/UpdateButton' > renders every sampled frame without throwing or React warnings  675ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/UpdateButton' > never goes blank once its content has appeared  638ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/ConsumeReuseUpdated' > renders every sampled frame without throwing or React warnings  324ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/Outro' > renders every sampled frame without throwing or React warnings  474ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/Outro' > never goes blank once its content has appeared  375ms
   ✓ Remotion scenes render across their whole timeline > 'studio/TestsTabIntro' > renders every sampled frame without throwing or React warnings  480ms
   ✓ Remotion scenes render across their whole timeline > 'studio/TestsTabIntro' > never goes blank once its content has appeared  486ms
   ✓ Remotion scenes render across their whole timeline > 'studio/StudioTestCases' > renders every sampled frame without throwing or React warnings  591ms
   ✓ Remotion scenes render across their whole timeline > 'studio/StudioTestCases' > never goes blank once its content has appeared  635ms
   ✓ Remotion scenes render across their whole timeline > 'studio/StudioBenchmark' > renders every sampled frame without throwing or React warnings  771ms
   ✓ Remotion scenes render across their whole timeline > 'studio/StudioBenchmark' > never goes blank once its content has appeared  349ms
   ✓ Remotion scenes render across their whole timeline > 'studio/StudioMultiModel' > renders every sampled frame without throwing or React warnings  329ms
   ✓ Remotion scenes render across their whole timeline > 'studio/CommandPalette' > renders every sampled frame without throwing or React warnings  348ms
 ✓ scripts/release.test.mjs (14 tests) 94916ms
   ✓ healthy release deploys once, records the commit, keeps the tree clean  26191ms
   ✓ a pg-signature regression after deploy rolls back to the previous version  16027ms
   ✓ a failed queue-health smoke also rolls back  8405ms
   ✓ an untested tree is refused before anything is built or deployed  2745ms
   ✓ dry run lists every refusal and has no side effects  3875ms
   ✓ --sha releases an older main commit from a temporary worktree and removes it  7893ms
   ✓ --keep-workdir retains build evidence and releases its lock on success  7269ms
   ✓ --keep-workdir retains evidence after failure without bypassing the CI gate  1046ms
   ✓ the recorded live commit drives migration and dependency-mix checks  6773ms
   ✓ a deploy that fails after the new version went live is rolled back  4862ms
   ✓ a deploy that fails before going live stops without a rollback  5679ms
   ✓ another deploy during the build stops the release before it migrates or deploys  2499ms
   ✓ push-deploy.sh pushes, then hands release options after -- to release.sh  1606ms

 Test Files  799 passed | 4 skipped (803)
      Tests  9169 passed | 14 skipped (9183)
   Start at  18:04:54
   Duration  96.66s (transform 34.00s, setup 72.54s, collect 151.32s, tests 428.97s, environment 120.68s, prepare 81.65s)
```

## Acceptance criteria

8/8 met

| AC | Met | Acceptance | Text |
|---|---|---|---|
| AC-01 | x (tasks) | met | An uncached production search for a 3 to 6 letter prefix returns in under 1s (Server-Timing enrichment under 100ms), and never runs a substring scan on Submission. |
| AC-02 | x (tasks) | met | The blocklist and rejected KV sets are rebuilt on a schedule, so they cannot expire silently. |
| AC-03 | x (tasks) | met | Typing "higg" in the palette shows results, never an endless skeleton: a slower response still renders, earlier results stay visible while a longer prefix loads, and a failure shows an error with Retry instead of "No results found". |
| AC-04 | x (tasks) | met | `GET /api/v1/submissions?state=active` and `/api/v1/submissions/positions` answer 200 in under 2s on production. |
| AC-05 | x (tasks) | met | `POST /api/v1/submissions` does at most one GitHub repo lookup before saving, and a person's submission is picked up within seconds, not behind crawler jobs. |
| AC-06 | x (tasks) | met | `vskill submit owner/repo` works without `--skill`; `vskill skill publish` either works from a checkout or says what to run; the first push of a new skill sets upstream. |
| AC-07 | x (tasks) | met | A new skill created locally and submitted lands in the production queue and its status page loads. |
| AC-08 | x | met | Remaining UI/UX gaps are listed for the owner, with the quick ones fixed. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | claude@antons-macbook-m4max | npm --prefix repositories/anton-abyzov/vskill-platform test… |  |
| T-02 | done | claude@antons-macbook-m4max | npm --prefix repositories/anton-abyzov/vskill-platform test… |  |
| T-03 | done | claude@antons-macbook-m4max | npm --prefix repositories/anton-abyzov/vskill-platform test… |  |
| T-04 | done | claude@antons-macbook-m4max | npm --prefix repositories/anton-abyzov/vskill-platform test… |  |
| T-05 | done | claude@antons-macbook-m4max | npm --prefix repositories/anton-abyzov/vskill test -- submi… |  |
| T-06 | done | claude@antons-macbook-m4max | npm --prefix repositories/anton-abyzov/vskill-platform test… |  |
| T-07 | done | claude@antons-macbook-m4max | bash scripts/release/release.sh verify platform → exit 0 lo… |  |
| T-08 | claimed | claude@antons-macbook-m4max |  |  |

7/8 done · 0 skipped · 1 claimed · 0 blocked · 0 stale · 0 open

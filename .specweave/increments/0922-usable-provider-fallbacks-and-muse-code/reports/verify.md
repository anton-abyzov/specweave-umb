# Verify — 0922-usable-provider-fallbacks-and-muse-code

PASS · 2026-10-27T13:08:18.998Z · commands from config testing.commands

## Commands

### `npm --prefix repositories/anton-abyzov/specweave run test:unit:fast` → exit 0 (45s)

```
 ✓ tests/unit/sync/pr-linker.test.ts (8 tests) 3ms
 ✓ tests/unit/core/config/hook-config-structure.test.ts (4 tests) 3ms
 ✓ tests/unit/utils/npm-constants.test.ts (5 tests) 3ms
 ✓ tests/unit/core/increment/detect-project-from-cwd.test.ts (10 tests) 4ms
 ✓ tests/unit/sync/format-suffixed-id.test.ts (5 tests) 5ms
 ✓ tests/unit/plugins/ado/ado-client.test.ts (2 tests) 3ms
 ✓ tests/unit/sync/sync-throttle-wiring.test.ts (3 tests) 3ms
 ✓ tests/unit/sync/format-preservation-sync-pr.test.ts (3 tests) 3ms
 ✓ tests/unit/integrations/github/from-repo-project-root.test.ts (4 tests) 3ms
 ✓ tests/unit/core/errors/sync-error.test.ts (5 tests) 3ms
 ✓ tests/unit/dashboard/useUrlState.test.ts (3 tests) 3ms
 ✓ tests/unit/sync/living-docs-sync-distributed.test.ts (3 tests) 3ms
 ✓ tests/unit/core/workflow/workflow-orchestrator.test.ts (3 tests) 3ms
 ✓ tests/unit/core/config-closure-hooks.test.ts (1 test) 3ms
 ✓ tests/unit/cli/helpers/init/claude-install-line.test.ts (2 tests) 2ms
 ✓ tests/unit/core/increment/active-increment-manager-root.test.ts (3 tests) 3ms
 ✓ tests/unit/sync/sync-progress-distributed.test.ts (2 tests) 2ms
 ↓ tests/unit/cli/repair-status-desync.test.ts (20 tests | 20 skipped)
 ✓ tests/unit/adapters/codex-adapter.test.ts (2 tests) 2ms
 ↓ tests/unit/cli/commands/cleanup-cache.test.ts (10 tests | 10 skipped)
 ↓ tests/unit/cli/validate-status-sync.test.ts (14 tests | 14 skipped)
 ↓ tests/unit/increment/duplicate-prevention.test.ts (7 tests | 7 skipped)
 ↓ tests/unit/core/lazy-loading/agent-sdk-integration.test.ts (20 tests | 20 skipped)
 ✓ tests/unit/cli/commands/init-ci-detection.test.ts (7 tests) 3ms
 ✓ tests/unit/review/review.test.ts (20 tests) 44107ms
     ✓ names the author family from the ledger, with claims as the fallback  1297ms
     ✓ carries the ACs, Approach, tasks with Files, and the diff since the base  1519ms
     ✓ keeps the leading space of the first diff stat row, like the rows after it  2424ms
     ✓ --brief prints the brief and runs nothing  1487ms
     ✓ picks Codex for Claude-written code and Claude for OpenAI-written code  1235ms
     ✓ honours --reviewer and review.reviewer, and explains when none fits  1554ms
     ✓ defaults to GPT-6.1-Sol in a read-only Codex sandbox  1846ms
     ✓ parses the verdict line  1573ms
     ✓ runs the reviewer with the brief, writes the report and a ledger note, exit 0 on ship  1549ms
     ✓ exit 3 on fix first and when the answer has no verdict; the close gate notes fix first  2456ms
     ✓ keeps every run's report: the ledger note names the file of that run, review-<reviewer>.md is the latest  2992ms
     ✓ prints the report path relative to where it was run  2677ms
     ✓ warns when the reviewer is the author's own family  2393ms
     ✓ exit 1 when the reviewer fails, times out or none is installed  3289ms
     ✓ a reviewer that exits non-zero is an error even when it prints a verdict  1155ms
     ✓ {out} reaches the command as an environment variable, never as shell text  1023ms
     ✓ a timeout stops the whole process tree and returns promptly  4601ms
     ✓ kills a descendant that ignores SIGTERM and detached from the pipes  4052ms
     ✓ Ctrl-C on specweave review kills the reviewer, even one that ignores SIGTERM  4049ms
     ✓ runReviewer reads {out} when the command writes it, stdout otherwise  934ms

 Test Files  534 passed | 5 skipped (539)
      Tests  10448 passed | 77 skipped (10525)
   Start at  09:05:27
   Duration  44.57s (transform 14.24s, setup 6.31s, import 27.85s, tests 352.97s, environment 32ms)
```

### `npm --prefix repositories/anton-abyzov/vskill test` → exit 0 (71s)

```
   ✓ addCommand source format routing > GitHub URL with .git suffix strips it before routing  1005ms
   ✓ addCommand source format routing > bare GitHub URL still routes to whole-repo discovery  1002ms
   ✓ addCommand source format routing > 3-part format with --copy flag uses installCopy  1003ms
   ✓ addCommand source format routing > 3-part format with --global flag passes global option  1003ms
   ✓ addCommand source format routing > 2-part with --skill fetches same URL as 3-part format  2006ms
   ✓ addCommand source format routing > 3-part format shows repo-not-found error when repo does not exist  1004ms
   ✓ addCommand source format routing > 2-part with --skill shows repo-not-found error when repo does not exist  1001ms
   ✓ addCommand source format routing > 3-part format uses discovery when skill is in plugins/ path  1003ms
   ✓ addCommand source format routing > 3-part format falls back to skills/<skill>/SKILL.md when discovery finds no match  1003ms
   ✓ addCommand source format routing > 3-part format falls back to hardcoded path when discovery returns empty array  1003ms
   ✓ addCommand registry install (no slash in source) > falls back to GitHub install via repoUrl when content is missing  1003ms
   ✓ addCommand registry install (no slash in source) > falls back to GitHub install via author/skillName when repoUrl is absent  1003ms
   ✓ addCommand smart project root resolution > installs skill relative to process.cwd() regardless of findProjectRoot result  1002ms
   ✓ addCommand --agent filter > installs only to the filtered agent when --agent is provided  1002ms
   ✓ addCommand --agent filter > --dry-run on a single skill writes nothing (0894)  1004ms
   ✓ addCommand --agent filter > exits with error when --agent specifies unknown ID  1004ms
   ✓ addCommand nested directory fix (TC-016) > does not create nested agent dir when projectRoot ends with agent base folder  1002ms
   ✓ addCommand nested directory fix (TC-016) > does not create nested agent dir when --cwd and cwd is agent base dir  1002ms
   ✓ addCommand project root consistency > passes project root to ensureLockfile and writeLockfile in discovery flow  1002ms
   ✓ addCommand project root consistency > passes project root to ensureLockfile and writeLockfile in single-skill legacy flow  1002ms
   ✓ addCommand project root consistency > canonical installer and lockfile both use same project root in discovery flow  1005ms
   ✓ addCommand project root consistency > uses ~/.agents/ for lockfile when global scope is selected  1008ms
   ✓ addCommand project root consistency > sets scope field on lockfile entries for global installs  1006ms
   ✓ addCommand project root consistency > sets scope field to 'project' for project-scoped installs  1005ms
   ✓ addCommand error handling in discovery flow > logs error and marks skill as not installed when canonical installer throws  1005ms
   ✓ addCommand flat name identifier guidance > shows resolution hint when registry falls back to GitHub  1003ms
   ✓ addCommand registry fallback auto-selects matching skill > auto-selects matching skill from multi-skill repo (installs 1, not all)  1004ms
   ✓ addCommand registry fallback auto-selects matching skill > aborts in non-TTY when registry name does not match any discovered skill  1004ms
   ✓ addCommand registry fallback auto-selects matching skill > auto-selects with case-insensitive match (registry slug vs directory name)  1004ms
   ✓ addCommand registry fallback auto-selects matching skill > tip message suggests owner/repo format for direct install  1003ms
   ✓ addCommand registry fallback auto-selects matching skill > does not auto-filter when _targetSkill is not set (direct owner/repo)  1005ms
   ✓ detectMarketplaceRepo > TC-003: returns false on network error (graceful fallback)  1003ms
   ✓ detectMarketplaceRepo > returns false when marketplace.json has no plugins  1002ms
   ✓ addCommand marketplace integration > TC-005: falls through to discovery when repo is NOT a marketplace  1002ms
   ✓ resolveViaSearch (flat name search disambiguation) > auto-installs when search returns exactly one non-blocked result  1005ms
   ✓ resolveViaSearch (flat name search disambiguation) > shows interactive prompt for multiple TTY results and installs selected  1006ms
   ✓ resolveViaSearch (flat name search disambiguation) > excludes blocked results from promptChoice options  1005ms
   ✓ resolveViaSearch (flat name search disambiguation) > 2-part owner/repo path does not call searchSkills  1002ms
   ✓ resolveViaSearch (flat name search disambiguation) > 3-part owner/repo/skill path does not call searchSkills  1003ms
   ✓ resolveViaSearch (flat name search disambiguation) > --yes flag auto-picks the exact slug match without prompting  1006ms
   ✓ resolveViaSearch (flat name search disambiguation) > --yes flag on non-TTY auto-picks the exact slug match  1005ms
   ✓ skill versioning (0584) > lockfile entry sha is 64 characters (not 12) for GitHub flat install  1005ms
   ✓ skill versioning (0584) > lockfile entry contains files array with sorted relative paths  1006ms
   ✓ skill versioning (0584) > version defaults to 1.0.0 for first install when no frontmatter version  1008ms
   ✓ private repos never reach verified-skill.com > GitHub installs whose visibility is unknown > send no safety check, security lookup or telemetry  1005ms

 Test Files  688 passed (688)
      Tests  7658 passed | 2 skipped (7660)
   Start at  09:06:12
   Duration  70.15s (transform 11.31s, setup 0ms, collect 40.15s, tests 208.48s, environment 69.10s, prepare 27.59s)
```

### `npm --prefix repositories/anton-abyzov/vskill-platform test` → exit 0 (48s)

```
 ✓ src/app/skills/__tests__/BrowseFilters.nofollow.test.tsx (1 test) 21ms
 ✓ src/app/account/orgs/[tenantId]/__tests__/page.test.tsx (5 tests) 15ms
 ✓ src/app/claude-code-skills/__tests__/hub-counts.test.tsx (2 tests) 16ms
 ✓ src/app/watch/__tests__/seo.test.tsx (3 tests) 13ms
 ✓ src/app/components/__tests__/skill-markdown.test.tsx (4 tests) 13ms
 ✓ src/__tests__/account-page.test.tsx (14 tests) 6ms
 ✓ src/app/__tests__/layout.nav.test.tsx (3 tests) 6ms
 ✓ src/app/submit/__tests__/viewQueueLink.test.tsx (5 tests) 2ms
 ✓ src/app/check/php2shell/__tests__/page.test.tsx (5 tests) 4ms
 ✓ src/app/insights/webmcp-security-2026-10/__tests__/page.test.tsx (9 tests) 9ms
 ✓ src/__tests__/account-repos-parity.test.tsx (4 tests) 6ms
 ✓ src/remotion/__tests__/scenes-timeline.test.tsx (124 tests) 20345ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/HookProblem' > renders every sampled frame without throwing or React warnings  943ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/HookProblem' > never goes blank once its content has appeared  697ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/BrowseGrid' > renders every sampled frame without throwing or React warnings  732ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/BrowseGrid' > is deterministic: the same frame always produces the same markup  335ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/BrowseGrid' > never goes blank once its content has appeared  1062ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/AuthorEvals' > renders every sampled frame without throwing or React warnings  1082ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/AuthorEvals' > never goes blank once its content has appeared  1154ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/AuthorPublish' > renders every sampled frame without throwing or React warnings  399ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/ConsumeInstall' > renders every sampled frame without throwing or React warnings  472ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/ConsumeInstall' > never goes blank once its content has appeared  540ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/ConsumeBugSurface' > renders every sampled frame without throwing or React warnings  372ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/ConsumeBugSurface' > never goes blank once its content has appeared  322ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/AuthorEditAndPublish' > renders every sampled frame without throwing or React warnings  419ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/AuthorEditAndPublish' > never goes blank once its content has appeared  479ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/UpdateButton' > renders every sampled frame without throwing or React warnings  471ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/UpdateButton' > never goes blank once its content has appeared  562ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/Outro' > renders every sampled frame without throwing or React warnings  456ms
   ✓ Remotion scenes render across their whole timeline > 'studio/TestsTabIntro' > renders every sampled frame without throwing or React warnings  385ms
   ✓ Remotion scenes render across their whole timeline > 'studio/TestsTabIntro' > never goes blank once its content has appeared  409ms
 ✓ scripts/release.test.mjs (14 tests) 47496ms
   ✓ healthy release deploys once, records the commit, keeps the tree clean  4419ms
   ✓ a pg-signature regression after deploy rolls back to the previous version  4910ms
   ✓ a failed queue-health smoke also rolls back  3654ms
   ✓ an untested tree is refused before anything is built or deployed  1858ms
   ✓ dry run lists every refusal and has no side effects  2494ms
   ✓ --sha releases an older main commit from a temporary worktree and removes it  6352ms
   ✓ --keep-workdir retains build evidence and releases its lock on success  5794ms
   ✓ --keep-workdir retains evidence after failure without bypassing the CI gate  2232ms
   ✓ the recorded live commit drives migration and dependency-mix checks  7147ms
   ✓ a deploy that fails after the new version went live is rolled back  2411ms
   ✓ a deploy that fails before going live stops without a rollback  2277ms
   ✓ another deploy during the build stops the release before it migrates or deploys  2389ms
   ✓ push-deploy.sh pushes, then hands release options after -- to release.sh  1521ms

 Test Files  766 passed | 4 skipped (770)
      Tests  8828 passed | 14 skipped (8842)
   Start at  09:07:22
   Duration  47.99s (transform 17.76s, setup 30.65s, collect 62.98s, tests 212.55s, environment 103.57s, prepare 40.60s)
```

### `python3 scripts/fleet-project-sync.py --self-test` → exit 0 (8s)

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
Ran 13 tests in 7.744s

OK
```

### `python3 -m unittest discover -s tests -p test_handoff_evidence.py` → exit 0 (0s)

```
..............................................
----------------------------------------------------------------------
Ran 46 tests in 0.296s

OK
```

### `python3 scripts/release/timing.py --self-test` → exit 0 (0s)

```
.................
----------------------------------------------------------------------
Ran 17 tests in 0.081s

OK
recorded
```

## Acceptance criteria

4/4 met

| AC | Met | Text |
|---|---|---|
| AC-01 | x (tasks) | Suggested fallbacks require authenticated, fresh positive usage evidence and a listed model; unknown, denied, stale and exhausted accounts are excluded. |
| AC-02 | x (tasks) | Muse Code is a configurable provider using the official session protocol, with streaming turns, cancellation and approval handling. |
| AC-03 | x (tasks) | Wonder Full appears only when the native account exposes it; API-key access does not imply Full entitlement. Missing CLI/auth have actionable setup guidance. |
| AC-04 | x (tasks) | Focused tests and relevant builds pass; headless UI evidence is saved and credit-recovery integration is reconciled without overwriting its work. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | codex-muse@antons-macbook-m4max | cd /Users/antonabyzov/Projects/github/studio-muse-fallback … |  |
| T-02 | done | codex-muse@antons-macbook-m4max | cd /Users/antonabyzov/Projects/github/studio-muse-fallback … |  |
| T-03 | done | claude@antons-macbook-m4max | PR183 dc0116de is ancestor of specwithcode-dev origin/main … |  |
| T-04 | done | claude@antons-macbook-m4max | Installed 1.0.96+: detection, models, native turn, cancel, … |  |

4/4 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open

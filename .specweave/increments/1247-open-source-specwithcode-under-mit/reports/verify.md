# Verify — 1247-open-source-specwithcode-under-mit

PASS · 2026-11-07T02:40:56.552Z · commands from config testing.commands

## Commands

### `npm --prefix repositories/anton-abyzov/specweave run test:unit:fast` → exit 0 (42s)

```
 ✓ tests/unit/core/increment/recognized-lifecycle-folders.test.ts (4 tests) 4ms
 ✓ tests/unit/core/session/resume-matrix.test.ts (4 tests) 3ms
 ✓ tests/unit/plugins/ado/ado-client.test.ts (2 tests) 3ms
 ✓ tests/unit/core/config/default-config-testing.test.ts (4 tests) 3ms
 ✓ tests/unit/importers/markdown-generator-project.test.ts (5 tests) 2ms
 ✓ tests/unit/sync/pr-linker.test.ts (8 tests) 3ms
 ✓ tests/unit/sync/sync-throttle-wiring.test.ts (3 tests) 3ms
 ✓ tests/unit/utils/npm-constants.test.ts (5 tests) 3ms
 ✓ tests/unit/sync/format-suffixed-id.test.ts (5 tests) 3ms
 ✓ tests/unit/integrations/github/from-repo-project-root.test.ts (4 tests) 2ms
 ✓ tests/unit/sync/format-preservation-sync-pr.test.ts (3 tests) 2ms
 ✓ tests/unit/adapters/codex-adapter.test.ts (2 tests) 2ms
 ✓ tests/unit/cli/helpers/init/claude-install-line.test.ts (2 tests) 2ms
 ✓ tests/unit/core/workflow/workflow-orchestrator.test.ts (3 tests) 2ms
 ✓ tests/unit/sync/sync-progress-distributed.test.ts (2 tests) 2ms
 ✓ tests/unit/sync/living-docs-sync-distributed.test.ts (3 tests) 2ms
 ✓ tests/unit/adapters/generic-instructions.test.ts (1 test) 2ms
 ✓ tests/unit/core/config-closure-hooks.test.ts (1 test) 1ms
 ↓ tests/unit/cli/repair-status-desync.test.ts (20 tests | 20 skipped)
 ↓ tests/unit/increment/duplicate-prevention.test.ts (7 tests | 7 skipped)
 ↓ tests/unit/cli/validate-status-sync.test.ts (14 tests | 14 skipped)
 ↓ tests/unit/cli/commands/cleanup-cache.test.ts (10 tests | 10 skipped)
 ↓ tests/unit/core/lazy-loading/agent-sdk-integration.test.ts (20 tests | 20 skipped)
 ✓ tests/unit/cli/commands/init-ci-detection.test.ts (7 tests) 2ms
 ✓ tests/unit/review/review.test.ts (20 tests) 40904ms
     ✓ names the author family from the ledger, with claims as the fallback  1325ms
     ✓ carries the ACs, Approach, tasks with Files, and the diff since the base  1480ms
     ✓ keeps the leading space of the first diff stat row, like the rows after it  2128ms
     ✓ --brief prints the brief and runs nothing  1530ms
     ✓ picks Codex for Claude-written code and Claude for OpenAI-written code  1215ms
     ✓ honours --reviewer and review.reviewer, and explains when none fits  1246ms
     ✓ defaults to GPT-6.1-Sol in a read-only Codex sandbox  1218ms
     ✓ parses the verdict line  1188ms
     ✓ runs the reviewer with the brief, writes the report and a ledger note, exit 0 on ship  1514ms
     ✓ exit 3 on fix first and when the answer has no verdict; the close gate notes fix first  1697ms
     ✓ keeps every run's report: the ledger note names the file of that run, review-<reviewer>.md is the latest  2368ms
     ✓ prints the report path relative to where it was run  2353ms
     ✓ warns when the reviewer is the author's own family  2169ms
     ✓ exit 1 when the reviewer fails, times out or none is installed  3143ms
     ✓ a reviewer that exits non-zero is an error even when it prints a verdict  1216ms
     ✓ {out} reaches the command as an environment variable, never as shell text  1086ms
     ✓ a timeout stops the whole process tree and returns promptly  4729ms
     ✓ kills a descendant that ignores SIGTERM and detached from the pipes  4061ms
     ✓ Ctrl-C on specweave review kills the reviewer, even one that ignores SIGTERM  4172ms
     ✓ runReviewer reads {out} when the command writes it, stdout otherwise  1065ms

 Test Files  543 passed | 5 skipped (548)
      Tests  10518 passed | 98 skipped (10616)
   Start at  21:38:07
   Duration  41.39s (transform 12.61s, setup 5.02s, import 23.48s, tests 312.30s, environment 30ms)
```

### `npm --prefix repositories/anton-abyzov/vskill test` → exit 0 (71s)

```
   ✓ addCommand source format routing > GitHub URL with .git suffix strips it before routing  1003ms
   ✓ addCommand source format routing > bare GitHub URL still routes to whole-repo discovery  1002ms
   ✓ addCommand source format routing > 3-part format with --copy flag uses installCopy  1006ms
   ✓ addCommand source format routing > 3-part format with --global flag passes global option  1010ms
   ✓ addCommand source format routing > 2-part with --skill fetches same URL as 3-part format  2007ms
   ✓ addCommand source format routing > 3-part format shows repo-not-found error when repo does not exist  1004ms
   ✓ addCommand source format routing > 2-part with --skill shows repo-not-found error when repo does not exist  1004ms
   ✓ addCommand source format routing > 3-part format uses discovery when skill is in plugins/ path  1005ms
   ✓ addCommand source format routing > 3-part format falls back to skills/<skill>/SKILL.md when discovery finds no match  1003ms
   ✓ addCommand source format routing > 3-part format falls back to hardcoded path when discovery returns empty array  1005ms
   ✓ addCommand registry install (no slash in source) > falls back to GitHub install via repoUrl when content is missing  1004ms
   ✓ addCommand registry install (no slash in source) > falls back to GitHub install via author/skillName when repoUrl is absent  1006ms
   ✓ addCommand smart project root resolution > installs skill relative to process.cwd() regardless of findProjectRoot result  1004ms
   ✓ addCommand --agent filter > installs only to the filtered agent when --agent is provided  1008ms
   ✓ addCommand --agent filter > --dry-run on a single skill writes nothing (0894)  1006ms
   ✓ addCommand --agent filter > exits with error when --agent specifies unknown ID  1004ms
   ✓ addCommand nested directory fix (TC-016) > does not create nested agent dir when projectRoot ends with agent base folder  1005ms
   ✓ addCommand nested directory fix (TC-016) > does not create nested agent dir when --cwd and cwd is agent base dir  1006ms
   ✓ addCommand project root consistency > passes project root to ensureLockfile and writeLockfile in discovery flow  1005ms
   ✓ addCommand project root consistency > passes project root to ensureLockfile and writeLockfile in single-skill legacy flow  1007ms
   ✓ addCommand project root consistency > canonical installer and lockfile both use same project root in discovery flow  1007ms
   ✓ addCommand project root consistency > uses ~/.agents/ for lockfile when global scope is selected  1007ms
   ✓ addCommand project root consistency > sets scope field on lockfile entries for global installs  1007ms
   ✓ addCommand project root consistency > sets scope field to 'project' for project-scoped installs  1007ms
   ✓ addCommand error handling in discovery flow > logs error and marks skill as not installed when canonical installer throws  1008ms
   ✓ addCommand flat name identifier guidance > shows resolution hint when registry falls back to GitHub  1007ms
   ✓ addCommand registry fallback auto-selects matching skill > auto-selects matching skill from multi-skill repo (installs 1, not all)  1007ms
   ✓ addCommand registry fallback auto-selects matching skill > aborts in non-TTY when registry name does not match any discovered skill  1008ms
   ✓ addCommand registry fallback auto-selects matching skill > auto-selects with case-insensitive match (registry slug vs directory name)  1008ms
   ✓ addCommand registry fallback auto-selects matching skill > tip message suggests owner/repo format for direct install  1006ms
   ✓ addCommand registry fallback auto-selects matching skill > does not auto-filter when _targetSkill is not set (direct owner/repo)  1006ms
   ✓ detectMarketplaceRepo > TC-003: returns false on network error (graceful fallback)  1004ms
   ✓ detectMarketplaceRepo > returns false when marketplace.json has no plugins  1004ms
   ✓ addCommand marketplace integration > TC-005: falls through to discovery when repo is NOT a marketplace  1003ms
   ✓ resolveViaSearch (flat name search disambiguation) > auto-installs when search returns exactly one non-blocked result  1006ms
   ✓ resolveViaSearch (flat name search disambiguation) > shows interactive prompt for multiple TTY results and installs selected  1009ms
   ✓ resolveViaSearch (flat name search disambiguation) > excludes blocked results from promptChoice options  1012ms
   ✓ resolveViaSearch (flat name search disambiguation) > 2-part owner/repo path does not call searchSkills  1005ms
   ✓ resolveViaSearch (flat name search disambiguation) > 3-part owner/repo/skill path does not call searchSkills  1004ms
   ✓ resolveViaSearch (flat name search disambiguation) > --yes flag auto-picks the exact slug match without prompting  1006ms
   ✓ resolveViaSearch (flat name search disambiguation) > --yes flag on non-TTY auto-picks the exact slug match  1008ms
   ✓ skill versioning (0584) > lockfile entry sha is 64 characters (not 12) for GitHub flat install  1004ms
   ✓ skill versioning (0584) > lockfile entry contains files array with sorted relative paths  1008ms
   ✓ skill versioning (0584) > version defaults to 1.0.0 for first install when no frontmatter version  1008ms
   ✓ private repos never reach verified-skill.com > GitHub installs whose visibility is unknown > send no safety check, security lookup or telemetry  1005ms

 Test Files  693 passed (693)
      Tests  7730 passed | 2 skipped (7732)
   Start at  21:38:49
   Duration  70.26s (transform 9.88s, setup 0ms, collect 35.13s, tests 202.78s, environment 52.70s, prepare 25.58s)
```

### `npm --prefix repositories/anton-abyzov/vskill-platform test` → exit 0 (44s)

```
 ✓ src/app/audits/__tests__/page.test.tsx (1 test) 20ms
 ✓ src/__tests__/account-connect-preflight.test.tsx (5 tests) 14ms
 ✓ src/app/agent-skills/__tests__/page.test.tsx (3 tests) 11ms
 ✓ src/app/studio/find/components/ResultCount.test.tsx (2 tests) 27ms
 ✓ src/app/components/__tests__/DelistedBanner.test.tsx (1 test) 18ms
 ✓ src/app/components/__tests__/LlmReviewPending.test.tsx (1 test) 17ms
 ✓ src/app/studio/find/lib/mock-fetch-gate.test.ts (6 tests) 12ms
 ✓ src/app/watch/__tests__/seo.test.tsx (3 tests) 9ms
 ✓ src/app/account/orgs/[tenantId]/__tests__/page.test.tsx (5 tests) 10ms
 ✓ src/app/claude-code-skills/__tests__/hub-counts.test.tsx (2 tests) 13ms
 ✓ src/app/components/__tests__/skill-markdown.test.tsx (4 tests) 10ms
 ✓ src/app/__tests__/layout.nav.test.tsx (5 tests) 2ms
 ✓ src/__tests__/account-repos-parity.test.tsx (4 tests) 3ms
 ✓ src/app/insights/webmcp-security-2026-10/__tests__/page.test.tsx (9 tests) 4ms
 ✓ src/app/claude-code-skills/__tests__/hub-seo.test.tsx (5 tests) 3ms
 ✓ src/app/submit/__tests__/viewQueueLink.test.tsx (5 tests) 2ms
 ✓ src/app/check/php2shell/__tests__/page.test.tsx (5 tests) 3ms
 ✓ src/remotion/__tests__/scenes-timeline.test.tsx (124 tests) 16398ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/HookProblem' > renders every sampled frame without throwing or React warnings  736ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/HookProblem' > never goes blank once its content has appeared  591ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/BrowseGrid' > renders every sampled frame without throwing or React warnings  704ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/BrowseGrid' > never goes blank once its content has appeared  630ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/AuthorEvals' > renders every sampled frame without throwing or React warnings  641ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/AuthorEvals' > never goes blank once its content has appeared  533ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/AuthorPublish' > renders every sampled frame without throwing or React warnings  313ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/ConsumeInstall' > renders every sampled frame without throwing or React warnings  496ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/AuthorEditAndPublish' > renders every sampled frame without throwing or React warnings  379ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/AuthorEditAndPublish' > never goes blank once its content has appeared  451ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/UpdateButton' > renders every sampled frame without throwing or React warnings  452ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/UpdateButton' > never goes blank once its content has appeared  387ms
   ✓ Remotion scenes render across their whole timeline > 'hackathon/Outro' > renders every sampled frame without throwing or React warnings  331ms
 ✓ scripts/release.test.mjs (14 tests) 43311ms
   ✓ healthy release deploys once, records the commit, keeps the tree clean  4428ms
   ✓ a pg-signature regression after deploy rolls back to the previous version  4610ms
   ✓ a failed queue-health smoke also rolls back  3322ms
   ✓ an untested tree is refused before anything is built or deployed  1738ms
   ✓ dry run lists every refusal and has no side effects  2524ms
   ✓ --sha releases an older main commit from a temporary worktree and removes it  6051ms
   ✓ --keep-workdir retains build evidence and releases its lock on success  4779ms
   ✓ --keep-workdir retains evidence after failure without bypassing the CI gate  1050ms
   ✓ the recorded live commit drives migration and dependency-mix checks  5706ms
   ✓ a deploy that fails after the new version went live is rolled back  2484ms
   ✓ a deploy that fails before going live stops without a rollback  2504ms
   ✓ another deploy during the build stops the release before it migrates or deploys  2432ms
   ✓ push-deploy.sh pushes, then hands release options after -- to release.sh  1639ms

 Test Files  770 passed | 4 skipped (774)
      Tests  8866 passed | 14 skipped (8880)
   Start at  21:40:00
   Duration  43.76s (transform 14.34s, setup 21.34s, collect 47.38s, tests 172.29s, environment 72.10s, prepare 30.08s)
```

### `python3 scripts/fleet-project-sync.py --self-test` → exit 0 (12s)

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
Ran 13 tests in 11.552s

OK
```

### `python3 -m unittest discover -s tests -p test_handoff_evidence.py` → exit 0 (0s)

```
..............................................
----------------------------------------------------------------------
Ran 46 tests in 0.301s

OK
```

### `python3 scripts/release/timing.py --self-test` → exit 0 (0s)

```
.................
----------------------------------------------------------------------
Ran 17 tests in 0.103s

OK
recorded
```

## Acceptance criteria

8/8 met

| AC | Met | Acceptance | Text |
|---|---|---|---|
| AC-01 | x | met | An audit report under this increment's folder lists the gitleaks findings for all commits of `specwithcode-dev` (count by rule, file paths, redacted), the commits that touch any value in the mirror's private scrub list (counts only, never values), sensitive files ever added (`.env`, keys, certificates, databases, user data), and the same checks for `anton-abyzov/specwithcode`, and ends with one recommendation and its evidence. |
| AC-02 | x | met | `LICENSE` at the root of the repository is the MIT License with `Copyright (c) 2026 Anton Abyzov`; GitHub reports the repository license as MIT; the workspace `package.json` files declare `"license": "MIT"`. |
| AC-03 | x | met | `THIRD_PARTY_NOTICES.md` keeps T3 Code's MIT notice verbatim (`Copyright (c) 2026 T3 Tools Inc.`) and every other existing notice; no file still says "no new project-wide license grant", "source available" or "never open source" about SpecWithCode. |
| AC-04 | x | met | No marketing surface (README pitch, specwithcode.com, store copy) says SpecWithCode is built on, based on or a fork of T3 Code; `THIRD_PARTY_NOTICES.md` and `UPSTREAM.md` still state the provenance. |
| AC-05 | x | met | The README opens with a one-line pitch, a demo GIF, download buttons for macOS, Windows and Linux, and a GitHub stars badge; `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, issue templates and a PR template exist; the repository has a description, at least 6 topics and at least 10 open issues labelled `good first issue`, each with the files to change and how to test. |
| AC-06 | x | met | The first-run screen and the About section show a "Star on GitHub" link to the public repository that opens in the system browser; dismissing it on the first-run screen keeps it hidden after a restart; About always shows it. A test covers both. |
| AC-07 | x | met | specwithcode.com shows one "Star on GitHub" link and says "open source (MIT)" wherever it said "source available"; the landing test asserts the new wording. |
| AC-08 | x | met | The development repository is public (after Anton's yes), its default branch builds in CI, and the public URL that has the stars either is that repository or redirects to it. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | claude@antons-macbook-m4max | test -s .specweave/increments/1247-open-source-specwithcode… |  |
| T-02 | done | claude@antons-macbook-m4max | PR #1447 merged as af71feb441: LICENSE MIT, package.json li… |  |
| T-03 | done | claude@antons-macbook-m4max | PR #1447: README hero with demo GIF, badges, download butto… |  |
| T-04 | done | claude@antons-macbook-m4max | PR #1448 merged as b8a709b83a; StarOnGitHub.test.tsx 4 test… |  |
| T-05 | done | claude@antons-macbook-m4max | specweave PR #2257 merged f27ce0e013; Pages deploy success;… |  |
| T-06 | done | claude@antons-macbook-m4max | Public anton-abyzov/specwithcode main 072265ee00 (MIT, 4 st… |  |
| T-07 | done | claude@antons-macbook-m4max | Fresh-context review verdict ship, all 8 ACs met on live ev… |  |

7/7 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open

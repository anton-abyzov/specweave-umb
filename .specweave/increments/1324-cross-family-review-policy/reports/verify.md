# Verify — 1324-cross-family-review-policy

PASS · 2026-11-14T02:59:32.160Z · commands from config testing.commands

## Commands

- Working directory: . (config testing.commands)
### `python3 scripts/fleet-project-sync.py --self-test` → exit 0 (9s)

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
Ran 13 tests in 8.562s

OK
```

- Working directory: . (config testing.commands)
### `python3 -m unittest discover -s tests -p test_handoff_evidence.py` → exit 0 (0s)

```
..............................................
----------------------------------------------------------------------
Ran 46 tests in 0.314s

OK
```

- Working directory: . (config testing.commands)
### `python3 scripts/release/timing.py --self-test` → exit 0 (0s)

```
.................
----------------------------------------------------------------------
Ran 17 tests in 0.078s

OK
recorded
```

- Working directory: repositories/anton-abyzov/specweave (config testing.ownerCommands)
### `npm run test:unit:fast` → exit 0 (43s)

```
 [2m[90m↓[39m[22m tests/unit/cli/validate-status-sync.test.ts [2m([22m[2m14 tests[22m[2m | [22m[33m14 skipped[39m[2m)[22m
 [2m[90m↓[39m[22m tests/unit/increment/duplicate-prevention.test.ts [2m([22m[2m7 tests[22m[2m | [22m[33m7 skipped[39m[2m)[22m
 [2m[90m↓[39m[22m tests/unit/core/lazy-loading/agent-sdk-integration.test.ts [2m([22m[2m20 tests[22m[2m | [22m[33m20 skipped[39m[2m)[22m
 [2m[90m↓[39m[22m tests/unit/cli/commands/cleanup-cache.test.ts [2m([22m[2m10 tests[22m[2m | [22m[33m10 skipped[39m[2m)[22m
 [32m✓[39m tests/unit/cli/commands/init-ci-detection.test.ts [2m([22m[2m7 tests[22m[2m)[22m[32m 2[2mms[22m[39m
 [32m✓[39m tests/unit/review/review-policy-gate.test.ts [2m([22m[2m18 tests[22m[2m)[22m[33m 30183[2mms[22m[39m
     [33m[2m✓[22m[39m round-trips the header and groups task Files by repository, leaving bookkeeping out [33m 1398[2mms[22m[39m
     [33m[2m✓[22m[39m --record stamps a review written elsewhere with model, family, author, repository and commit [33m 1637[2mms[22m[39m
     [33m[2m✓[22m[39m --record refuses without --model, without a verdict line, or with a --head that is not a commit id [33m 1695[2mms[22m[39m
     [33m[2m✓[22m[39m refuses with no review, naming the policy and the next command [33m 1327[2mms[22m[39m
     [33m[2m✓[22m[39m refuses a same-family review and names it [33m 1454[2mms[22m[39m
     [33m[2m✓[22m[39m refuses a fix first verdict and a review older than verification [33m 1538[2mms[22m[39m
     [33m[2m✓[22m[39m passes a squash-merged review and refuses when the reviewed files changed after it [33m 3624[2mms[22m[39m
     [33m[2m✓[22m[39m refuses a reviewed commit the repository does not have [33m 1544[2mms[22m[39m
     [33m[2m✓[22m[39m a cross-family policy takes any other family; without Required nothing changes [33m 1427[2mms[22m[39m
     [33m[2m✓[22m[39m orders by the recorded time, not checkout file times [33m 1741[2mms[22m[39m
     [33m[2m✓[22m[39m a review recorded before verify fails even when its file is newer [33m 1767[2mms[22m[39m
     [33m[2m✓[22m[39m an unclassified family or a Fable author never makes a review cross-family [33m 2042[2mms[22m[39m
     [33m[2m✓[22m[39m a deep policy refuses a standard review; a pinned model matches across provider spellings [33m 2013[2mms[22m[39m
     [33m[2m✓[22m[39m keeps a repository path with spaces and cannot be cut short by a value [33m 1862[2mms[22m[39m
     [33m[2m✓[22m[39m checks wildcard task Files and takes a path starting with a colon literally [33m 2342[2mms[22m[39m
     [33m[2m✓[22m[39m keeps underscores inside a model id and strips only the marks around it [33m 915[2mms[22m[39m
     [33m[2m✓[22m[39m with a required policy, an older same-family fix first does not block a newer matching ship [33m 986[2mms[22m[39m
     [33m[2m✓[22m[39m review.reviewer yields to an increment policy; an explicit --reviewer runs with a warning [33m 872[2mms[22m[39m
 [32m✓[39m tests/unit/review/review.test.ts [2m([22m[2m20 tests[22m[2m)[22m[33m 41631[2mms[22m[39m
     [33m[2m✓[22m[39m names the author family from the ledger, with claims as the fallback [33m 1390[2mms[22m[39m
     [33m[2m✓[22m[39m carries the ACs, Approach, tasks with Files, and the diff since the base [33m 1641[2mms[22m[39m
     [33m[2m✓[22m[39m keeps the leading space of the first diff stat row, like the rows after it [33m 2016[2mms[22m[39m
     [33m[2m✓[22m[39m --brief prints the brief and runs nothing [33m 1547[2mms[22m[39m
     [33m[2m✓[22m[39m picks Codex for Claude-written code and Claude for OpenAI-written code [33m 1270[2mms[22m[39m
     [33m[2m✓[22m[39m honours --reviewer and review.reviewer, and explains when none fits [33m 1248[2mms[22m[39m
     [33m[2m✓[22m[39m defaults to GPT-6.1-Sol in a read-only Codex sandbox [33m 1396[2mms[22m[39m
     [33m[2m✓[22m[39m parses the verdict line [33m 1420[2mms[22m[39m
     [33m[2m✓[22m[39m runs the reviewer with the brief, writes the report and a ledger note, exit 0 on ship [33m 1547[2mms[22m[39m
     [33m[2m✓[22m[39m exit 3 on fix first and when the answer has no verdict; the close gate notes fix first [33m 1607[2mms[22m[39m
     [33m[2m✓[22m[39m keeps every run's report: the ledger note names the file of that run, review-<reviewer>.md is the latest [33m 1937[2mms[22m[39m
     [33m[2m✓[22m[39m prints the report path relative to where it was run [33m 2063[2mms[22m[39m
     [33m[2m✓[22m[39m warns when the reviewer is the author's own family [33m 2259[2mms[22m[39m
     [33m[2m✓[22m[39m exit 1 when the reviewer fails, times out or none is installed [33m 3122[2mms[22m[39m
     [33m[2m✓[22m[39m a reviewer that exits non-zero is an error even when it prints a verdict [33m 2256[2mms[22m[39m
     [33m[2m✓[22m[39m {out} reaches the command as an environment variable, never as shell text [33m 1008[2mms[22m[39m
     [33m[2m✓[22m[39m a timeout stops the whole process tree and returns promptly [33m 4674[2mms[22m[39m
     [33m[2m✓[22m[39m kills a descendant that ignores SIGTERM and detached from the pipes [33m 4046[2mms[22m[39m
     [33m[2m✓[22m[39m Ctrl-C on specweave review kills the reviewer, even one that ignores SIGTERM [33m 4187[2mms[22m[39m
     [33m[2m✓[22m[39m runReviewer reads {out} when the command writes it, stdout otherwise [33m 997[2mms[22m[39m

[2m Test Files [22m [1m[32m548 passed[39m[22m[2m | [22m[33m5 skipped[39m[90m (553)[39m
[2m      Tests [22m [1m[32m10577 passed[39m[22m[2m | [22m[33m98 skipped[39m[90m (10675)[39m
[2m   Start at [22m 21:41:53
[2m   Duration [22m 42.08s[2m (transform 13.54s, setup 5.54s, import 25.85s, tests 341.51s, environment 28ms)[22m
```

- Working directory: repositories/anton-abyzov/specwithcode (config testing.ownerCommands)
### `npm run verify:pr -- --jobs 1 --no-server` → exit 0 (582s)

```

> verify:pr
> bash scripts/studio-verify/pr-gate.sh --jobs 1 --no-server

PR gate: HEAD 6d9593696 against origin/main (merge base 6d9593696); logs in /var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T//studio-pr-gate.rto0rf
Stage 1: 18 jobs, 1 at a time
STAGE 1                                      RESULT     SECS
contrast                                     pass          4
typecheck                                    pass         31
fleet                                        pass        221
apps/chrome-extension                        pass          2
apps/desktop                                 pass         14
apps/marketing                               pass          1
apps/mobile                                  pass         15
apps/web                                     pass        214
infra/relay                                  pass         14
oxlint-plugin-studio                         pass          9
packages/client-runtime                      pass         13
packages/contracts                           pass          4
packages/effect-acp                          pass          3
packages/effect-codex-app-server             pass          1
packages/shared                              pass         10
packages/ssh                                 pass          7
packages/tailscale                           pass          0
scripts                                      pass         18
Stage 2: not run here (--no-server); the server suite runs in jobs of its own
PR gate: stage 1 passed, server passed, 582s
```

- Working directory: repositories/anton-abyzov/specwithcode (config testing.ownerCommands)
### `npm run test:server:sharded -- --shards 6 --out "$(mktemp -d)"` → exit 0 (435s)

```

> test:server:sharded
> node scripts/release/test-sharded.mjs --shards 6 --out /var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/tmp.4D7B8wPVYV

Running the server suite as 6 shards; logs in /var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/tmp.4D7B8wPVYV
SHARD  EXIT  SECONDS  FILES  TESTS  FAILED
1      0       293.5    190    2725        0
2      0       402.3    205    2745        0
3      0       426.7    204    2333        0
4      0       367.4    205    2855        0
5      0       434.7    204    2754        0
6      0       404.2    206    2868        0
Server shards: passed in 434.7s
```

## Acceptance criteria

6/6 met

| AC | Met | Acceptance | Text |
|---|---|---|---|
| AC-01 | x (tasks) | met | `resolveReviewPolicy` reads spec.md `## Review` (`Reviewer: cross-family \| openai \| claude \| google \| xai \| meta \| <model id>`, `Depth: standard \| deep`, `Required: yes \| no`) over `.specweave/config.json` `review.policy` over `review.crossModel` (required, cross-family) over the default (cross-family, standard, not required), and reports which layer set each field. |
| AC-02 | x (tasks) | met | `specweave review` uses the policy's reviewer family or model and depth (deep runs Codex at `xhigh`); its record header carries reviewer, model, family, author, depth, repository and reviewed commit. `specweave review --record <file> --model <id> [--head <sha>]` writes the same record for a review done elsewhere, takes the verdict from the file, and refuses a file with no verdict line. |
| AC-03 | x (tasks) | met | With a required policy, `specweave complete` (and verify's strict-close preview) refuses unless, for every repository that holds task Files, the newest record matching the policy says ship, follows verification, and its reviewed commit has the same content as that repository's HEAD for the task Files; the error names the required family, the newest review found (model, family, commit) and the next command. Without a required policy, behavior is unchanged. |
| AC-04 | x (tasks) | met | `delegate_task` with `taskClass: "review"` or `role: "review"` and no model picks the first available reviewer of another family than the author (the calling thread's model), in the spec policy's family when it names one, from the project's reviewer order; the result's `review` field names the reviewer, the author family and each skipped entry with its reason. When no reviewer of the required family can run, it fails with those reasons and starts nothing. A named model of the author's family runs as asked and the result carries a same-family warning. |
| AC-05 | x (tasks) | met | The plan card shows the newest review record ("Reviewed by GPT-6.1 Sol at 3f9a2c1 · ship", "· fix first") and, when the policy requires a review and none matches, "OpenAI review required"; the server reads it from the increment's reports and spec without a CLI, in all 8 catalogs. |
| AC-06 | x (tasks) | met | sw-review, sw-done, sw-increment and sw-grill-me document `## Review`, recommend `Required: yes` with a deep cross-family reviewer for complex features (auth, payments, migrations, multi-repo, over ~1k lines), and end every review with `specweave review --record`. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | claude@antons-macbook-m4max | cd repositories/anton-abyzov/specweave && npx vitest run te… |  |
| T-02 | done | claude@antons-macbook-m4max | cd repositories/anton-abyzov/specweave && npx vitest run te… |  |
| T-03 | done | claude@antons-macbook-m4max | cd repositories/anton-abyzov/specweave && npx vitest run te… |  |
| T-04 | done | claude@antons-macbook-m4max | cd repositories/anton-abyzov/specweave && grep -q 'Required… |  |
| T-05 | done | claude@antons-macbook-m4max | cd /Users/antonabyzov/.specwithcode/m4/scratch/2026-11-13-r… |  |
| T-06 | done | claude@antons-macbook-m4max | cd /Users/antonabyzov/.specwithcode/m4/scratch/2026-11-13-r… |  |
| T-07 | done | claude@antons-macbook-m4max | specweave verify 1324-cross-family-review-policy at 2026-11… |  |

7/7 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open

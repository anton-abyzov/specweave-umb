# Releasing from the umbrella

One entrypoint covers every product: `scripts/release/release.sh`. It reads `.specweave/release/manifest.json` (repos, tracks, commands, verify checks, policy, known-noise checks) and calls each repo's own one-command release script. The manifest holds paths and env var names only; this repository is public.

## Commands

| Step | Command | Notes |
|---|---|---|
| Audit | `bash scripts/release/release.sh status` | Read-only, about 10 s. Per repo: local branch, behind/ahead, dirty files, open PRs (red ones), latest default-branch CI per workflow, latest tag, unreleased commits, version on the default branch, npm latest, merged worktrees. Per track: live checks against the expected version. JSON on stdout, table on stderr. `--fetch` refreshes local refs first; `--run` shows the current release run. |
| Ship | `bash scripts/release/release.sh ship <track\|vskill\|all> [--dry-run] [--plan] [-- args]` | Runs the track script, then `verify`, then `cleanup --apply` for that track only. `all` runs one pipeline per repo in parallel. `--plan` prints what would run and touches nothing. `--dry-run` passes the track's dry-run flag and refuses a script that has no such option (an older script would take it as an argument and run for real). Exit 2 means shipped but verify is still pending: run `verify`, then `cleanup --apply`. |
| Verify | `bash scripts/release/release.sh verify <track\|all> [--version X]` | Deterministic: npm dist-tag, GitHub release and assets, URLs, updater manifest, Workers deployments, fleet versions, desktop apps, default-branch CI (info only). The studio track's `M4 app`, `M1 app` and `M3 app` checks (kind `desktop_app`) read `/Applications/SpecWithCode.app` on M4 and, over the pinned fleet ssh, on M1 and M3: each fails unless that app is the released version and passes `codesign --verify --deep --strict`, or when the Mac cannot be reached. The studio release's fleet-workers stage updates the M1 and M3 apps after their services; `python3 -B scripts/studio-fleet/fleet_rollout.py --version X.Y.Z --only workers` in the studio checkout retries them. Exit 0 pass, 1 fail, 2 pending. Start an agent only when this fails. |
| Cleanup | `bash scripts/release/release.sh cleanup <track> [--apply]` | Refuses unless verify passes. Removes only clean worktrees, idle for `cleanup.min_idle_minutes` (30), whose branch has no commits outside `origin/<default>` or whose PR merged at the exact tip. Any git error keeps the worktree. Never touches `studio-rel-*`, `studio-release-*`, `relperf-*` or the other protected patterns. Keeps any worktree an open SpecWithCode thread uses, a project root, or a running agent session's folder, and any branch a thread records. It reads them with `specweave-studio db query --base-dir <home>` for each SpecWithCode home that has a database (`specweave-studio worktree owners --json` only adds folders), and reads them again just before each removal. If a read fails, it keeps everything under `~/.specwithcode/worktrees`, `~/.specwithcode/scratch`, `~/.specwithcode/*/worktrees` and `~/.specwithcode/*/scratch`, and every branch. It does the same for a home it could not read. Branches are deleted only with `git branch -d`. Without `--apply` it only lists. |
| Timing | `bash scripts/release/release.sh timing` | `timing.py check`: flags steps slower than 1.5x their baseline median and more than 60 s slower, and caches that missed on the last 3 runs. |

Tracks and their scripts (each script supports `--dry-run`):

| Track | Repo | Release command |
|---|---|---|
| specweave | anton-abyzov/specweave (develop) | `bash scripts/release/release.sh <patch\|minor\|major\|x.y.z>` |
| vskill-npm | anton-abyzov/vskill | `bash scripts/release/release-npm.sh [<v>]` |
| vskill-desktop | anton-abyzov/vskill | `bash scripts/release/release-desktop.sh [<v>]`: tag `desktop-v<next>` on green main, no bump PR |
| platform | anton-abyzov/vskill-platform (private) | `bash scripts/release.sh [--sha X] [--migrate\|--no-migrate]` |
| studio | anton-abyzov/specwithcode-dev, mirror anton-abyzov/specwithcode | `bash scripts/release/release.sh <version> [--resume]` |

## Policy

Merge green PRs, release, deploy, verify and remove fully merged worktrees without asking. Still ask before discarding work that exists nowhere else, and for the manual gates: data migrations (platform `--migrate`), auth changes, payment flows, new UI that needs acceptance. Known-noise checks (`claude-review`, `E2E Live (nightly)`) never block a merge. SpecWithCode fleet: M4 first and wait for its installedVersion, then M1 and M3 together; when the release runs on M4, its install request is queued in normal mode and not waited on.

## Waiting without blocking

Never hold a tool call open longer than 540 s, and never wait on a condition that ignores error output. Use `scripts/release/ci-wait.sh`:

```bash
bash scripts/release/ci-wait.sh pr vskill-platform 131            # PR checks; known noise ignored
bash scripts/release/ci-wait.sh run anton-abyzov/vskill 38918885879
bash scripts/release/ci-wait.sh tag vskill desktop-v1.0.66 desktop-release.yml
bash scripts/release/ci-wait.sh npm vskill 1.2.9
bash scripts/release/ci-wait.sh url https://verified-skill.com/desktop/latest.json '"1.0.66"' --header 'x-manifest-source: r2'
bash scripts/release/ci-wait.sh log tail.log --ok 'queue-health] batch' --ok-count 8 --fail 'socket has been closed|unhandled rejection'
```

Exit 0 is success, 1 is failure (the failing jobs and the last 80 log lines are printed), 2 is still pending: call it again. The default budget is 540 s (`--budget` changes it). GitHub polls send `If-None-Match`, so unchanged answers cost no rate limit. Finished runs are added to the timing log.

For long waits, start the command in the background and watch its output instead of blocking:

1. Run `ci-wait.sh ...` (or `release.sh ship ...`) with `run_in_background`, writing to a log file.
2. Arm a Monitor on that log (and, for a multi-track run, on `.specweave/state/release-run.json`) with an until-condition on the `ci-wait:` result line or an exit code.
3. When a workflow orchestrates the tracks, the parent arms one Monitor right after launching it. It tails the workflow's `journal.jsonl` plus `.specweave/state/release-run.json`. On each result line, or every 10 minutes, it posts one status line per track: phase, what it waits on (run or PR URL), and the ETA from the `timing.py` baseline.

## Timing records and CI lint

`.specweave/metrics/release-timings.jsonl` holds one JSON record per run, job, step, cache result, local suite or release phase.

```bash
python3 scripts/release/timing.py ingest --gh anton-abyzov/vskill 38918885879 --cache-log
python3 scripts/release/timing.py record --repo anton-abyzov/specwithcode-dev --step "server suite" --seconds 1385 --kind suite
python3 scripts/release/timing.py check                      # exit 2 when something regressed
python3 scripts/release/timing.py scan-ci repositories/anton-abyzov/*   # workflow lint
python3 scripts/release/timing.py --self-test
bash scripts/release/release-self-test.sh                     # cleanup rules and desktop_app checks, offline
```

`scan-ci` rules: job without `timeout-minutes`; push/pull_request workflow without `concurrency`; push trigger with no filter, or without the paths filter its pull_request trigger has; dependency installs or Rust builds without a cache; `rust-cache` that is never saved on the default branch under its key; `|| true` after a gating command; `continue-on-error`; third-party actions not pinned to a SHA; vitest without `--maxWorkers` on a 2-vCPU private-repo runner; with `--history`, continue-on-error checks red on most recent PRs. It exits 1 when an error-level rule fires (`--fail-on none|warn|error`).

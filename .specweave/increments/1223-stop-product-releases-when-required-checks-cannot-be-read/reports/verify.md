# Verify — 1223-stop-product-releases-when-required-checks-cannot-be-read

PASS · 2026-11-03T23:42:10.557Z · commands from explicit

## Commands

### `cd "$HOME/.specwithcode/m4/worktrees/specwithcode-dev/recent-features-followup-20261103" && test "$(git rev-parse HEAD)" = 861dc55e00713c05631b16c15d085ffcb86adbc2 && bash scripts/release/release-self-test.sh` → exit 0 (206s)

```
ok   ... backfills a partial clone, and stops before the tests if objects are still missing
ok   ... and stops before the tests when GIT_NO_LAZY_FETCH=1 git show f0b6d13fb273ae3285861878c43b822731926023:pnpm-lock.yaml fails
ok   ... and when the audits no longer pin the probe commit
ok   a --ci rerun removes a release branch that holds only the bump
ok   a --ci rerun keeps a release branch with other work
ok   a --ci rerun refuses a version that is already tagged
ok   a failed required check on the pull request that made main stops before the bump
ok   ... and so does one still running
ok   an earlier release pull request on main skips the gate check
ok   a passed gate on the pull request that made main continues
ok   GitHub pull request lookup failure stops the release
ok   GitHub required check lookup failure stops the release
ok   an explicit empty required-check rollup is accepted
ok   a successful direct-push lookup is accepted
ok   a call whose command is missing or starts with - is refused
ok   no x, q or t call in release.sh glues an option to its command
ok   a refused signature check signs once more and continues
ok   a second refused signature check stops the release
ok   a failed required check on the release PR stops the merge
ok   stage 1 starts contrast first, then the longest jobs by the last run's times
ok   a stage-1 job that fails once runs again, alone, and passes as a FLAKE
ok   two stage-1 jobs that fail once each run again, alone, after the rest, and pass as FLAKEs
ok   a stage-1 job that fails twice fails the stage
ok   ... and --resume runs it first and keeps the earlier retry on record
ok   more failed stage-1 jobs than the cap get no retry
ok   a flake retried among last attempt's failures counts toward the cap: two more failures get no retry
ok   ... and one more failure, two in all, still gets its retry
ok   --no-retry fails a stage on its first failure
ok   a server file that fails once runs again alone and the drafts stay
ok   a server file that fails twice fails the release and drops the drafts
ok   a server run with no failed file named (crash or timeout) gets no retry
ok   server-wait names only the flakes of the server run it waited for
ok   --no-retry restarts a server suite running with retries and keeps one running without
scripts/release/release-self-test.sh: line 1049: 50869 Terminated: 15          bash -c 'sleep 60; :' --internal-server 1.5.12
ok   --no-retry starts the new server suite only once the old one's whole process group is gone
ok   server-wait waits for a suite still running with a three-field server.pid
ok   a desktop app already on the release is kept, not snapshotted or reinstalled
ok   a desktop app that loses the computer-use grants stops the release
ok   a desktop app on the release that fails its signature check is moved aside and installed again
ok   a desktop app with no readable version is moved aside, not snapshotted or probed for grants
ok   the desktop app is unpacked and verified first, then swapped in, and only then the previous one trashed
ok   a failed unpack leaves the installed desktop app in place and never trashes it
ok   the desktop stage waits for the app's own ShipIt and stops while it runs; another app's ShipIt is ignored
ok   timing compare flags a stage over 25% and 10s slower, not a small one
ok   a failed pull request stops the merge stage before it merges
ok   a failed Linux worker update warns after merge and the release still finishes
ok   release_tools.py unit tests
ok   every command the stub runs recorded exists
ok   the repository is unchanged
97 passed, 0 failed
```

## Acceptance criteria

1/1 met

| AC | Met | Acceptance | Text |
|---|---|---|---|
| AC-01 | x (tasks) | met | A GitHub API failure during either lookup stops the release. Successful direct push, release PR, and genuinely empty required checks retain their existing behavior. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | codex@antons-macbook-m4max | 861dc55e00713c05631b16c15d085ffcb86adbc2; bash scripts/rele… |  |

1/1 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open

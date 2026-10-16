# orchestration

## F01 [discovery-gap] real=True safe=True save=450->280 :: Add a single umbrella release entrypoint with a deterministic status audit
FILES: /Users/antonabyzov/Projects/github/specweave-umb/scripts/release/release.sh, /Users/antonabyzov/Projects/github/specweave-umb/AGENTS.md
EVIDENCE: Today's run spent 510s on a 12-agent audit workflow (wf_8996f7ba-384, 14:02:30-14:11:00) to find out what each repo needed to ship. Then it launched a separate ship workflow (wf_da54c895-ff2) whose 4 track prompts re-derived procedures from scratch. /Users/antonabyzov/Projects/github/specweave-umb/scripts has no release tooling. The AGENTS.md Commands table has Build/Test/Lint rows but no Release row.
CHANGE: Create scripts/release/release.sh with these subcommands:
- status: for each repo in .specweave/config.json workspace.repos, report unreleased commits since the last tag, open PRs, CI state on the default branch, the published version versus local package.json, and pending deploys. Print JSON plus a one-line table, all from git log/gh api/npm view with no agents.
- ship <track|all>: call the per-repo one-command scripts (F09, F11, F14, F16).
- verify <track>: run the manifest verify commands.
- cleanup <track>.
- timing: delegate to F04.
Every phase writes progress to .specweave/state/release-run.json. Add a Release row to the AGENTS.md Commands table pointing at it.
RISK: Low. It is additive tooling; status is read-only.
VERIFIER: The audit workflow wf_8996f7ba-384 did take 510s, but its release-status half was done by 14:07:20. The critical path was verify:studio-worktrees (14:06:31 to 14:10:57), which inventoried about 85 worktrees. The audit was also Anton's explicit request, not release overhead. .specweave/config.json workspace.repos lists only specweave, vskill and vskill-platform, so a status loop driven by it would skip specweave-studio (specwithcode-dev), which is the longest track. umbrella scripts/ has no release tooling (only cf-cost-monitor*, fleet-project-sync.py, restore-repos.sh), which confirms the gap.
IMPL: Add /Users/antonabyzov/Projects/github/specweave-umb/scripts/release/release.sh. It reads its repo list from the committed manifest (F02), not workspace.repos. `status` runs, per repo:
- git log <lastTag>..origin/<default> --oneline | wc -l
- gh pr list --state open --json number,statusCheckRollup
- npm view <pkg> version vs package.json
- gh release view --json tagName
- for worktrees: git worktree list --porcelain plus `git cherry origin/<default> <branch>`, to pre-classify merged worktrees. This is what gated the audit's wall clock.
Output is JSON on stdout plus a table. Add a Release row to the AGENTS.md Commands table; it is docs only, since specweave verify reads config testing.commands or package.json, not this table.

## F02 [discovery-gap] real=True safe=True save=300->300 :: Machine-readable release manifest of known paths, policies and verify commands
FILES: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/release/manifest.json, /Users/antonabyzov/Projects/github/specweave-umb/.gitignore
EVIDENCE: The studio agent spent about 356s of critical-path time (982s of tool time) rediscovering paths and building helpers: release dirs ~/Projects/github/studio-rel-<v>*, the mirror checkout ~/Projects/github/specwithcode-public, the fleet key ~/.local/share/specweave/fleet/id_ed25519, service ports 8319/18319/28319, cert and notary key file locations, SDKROOT, and stripping anaconda3 from PATH. It also wrote throwaway /tmp/fleetssh.sh and /tmp/fleet-request.py. The platform and vskill agents rediscovered merge policy (specweave needs --admin), known-noise checks (claude-review) and deploy commands. Memory notes hold stale or contradictory versions of the same facts (see F24).
CHANGE: Add .specweave/release/manifest.json, paths only and never values. Per repo it holds:
- default branch, merge method and whether --admin is needed
- the release command and the verify commands (npm view <pkg> version, curl of the version endpoint, gh release view)
- required checks and known-noise checks (claude-review, e2e-live-nightly)
- build env file locations (cert dir, notary key dir, SDK path, Node version)
- fleet inventory location ($STUDIO_FLEET_HOSTS or ~/.local/share/specweave/fleet/hosts.json), ports and the release dir naming pattern
- policy flags from feedback_git_push_deploy.md: merge, release, deploy and clean worktrees without asking
release.sh reads it, and the memory notes point to it instead of duplicating it. Make sure .specweave/release/ is not caught by .gitignore patterns.
RISK: Low. Secret values must stay out: store file paths and env var names only.
VERIFIER: Discovery was real. The studio agent grepped old transcripts from 14:36:46 to 14:42:11 (about 325s) before it started any work, including `find / -xdev -name '*.jsonl'` (hit the 120s timeout) and `grep -rl make_update_plan`. More grepping until 14:52 overlapped the t-int test run. The prompt did pass the 1.0.35 release note, but that note records outcomes, not commands. Correction: /tmp/fleetssh.sh and /tmp/fleet-request.py were not written today. They existed from 01:04 local, left by an earlier session, and the agent reused them. .specweave/release/ is not gitignored (git check-ignore prints nothing for it).
IMPL: Create /Users/antonabyzov/Projects/github/specweave-umb/.specweave/release/manifest.json, with paths and env var names only. Include a studio entry:
- repo anton-abyzov/specwithcode-dev, mirror anton-abyzov/specwithcode, local path repositories/anton-abyzov/specweave-studio
- release dir pattern ~/Projects/github/studio-rel-<v>, assets ~/Projects/github/studio-release-<v>-assets
- cert dir ~/.config/skill-studio-release/cert and notary key path
- env file (.env in the studio checkout): store var names only
- Node 22.20.0; SDKROOT; strip_path: [anaconda3]
- fleet hosts via scripts/studio-fleet/fleet_hosts.py
- per-host update mode: m1/m3 `install` (force); m4 `normal`, no-wait, because it is the orchestrator host (see missed findings)
Platform: the deploy command must be `npm run db:generate && npm run deploy`, not the triple build. List known_noise_checks: claude-review and E2E Live (nightly).

## F03 [wait-gap] real=True safe=True save=300->100 :: CI-wait helper that blocks efficiently and survives the 600s foreground cap
FILES: /Users/antonabyzov/Projects/github/specweave-umb/scripts/release/ci-wait.sh
EVIDENCE: About 3,800s of today's wall clock was blocked on CI or registries:
- platform PR CI 2281s
- vskill desktop release 966s
- vskill PR CI 362s
- npm-release plus registry poll 357s
- specweave release.yml 281s
- specweave PR CI 174s
Agents waited with ad-hoc `gh pr checks --watch` and sleep loops. Waits were re-issued 8 times after hitting the 600s Bash foreground cap, and each re-issue cost a model round-trip plus re-reading state. Failures showed up only after the full wait, with no failing-job log tail.
CHANGE: Add scripts/release/ci-wait.sh (or .py) with modes:
- pr <repo> <n>
- run <repo> <id>
- tag <repo> <tag> <workflow>
- npm <pkg> <version>
- url <url> <expect-substring>
Behaviour:
- poll gh api with If-None-Match ETags (304s do not count against the rate limit) and 10s->30s backoff
- exit on the first failed required check, without waiting for the rest
- honour the manifest's known-noise ignore list
- on failure, print the failing job names and the `gh run view --log-failed` tail (last 80 lines)
- exit 0 green, 1 red, 2 timeout
- append a timing record (F04)
Document running it via run_in_background or Monitor so agents never hit the 600s cap.
RISK: Low.
VERIFIER: Waits are parallel across tracks, so they don't add up. The listed numbers sum to about 4,400s, not 3,800s. Foreground 600s cap hits: vskill 1, platform 4, studio 4, plus the platform verify agent self-capping at 590s. Re-issue round trips cost only about 5-10s each. vskill-platform unit tests are a single job, so fail-fast on the first red check saves nothing there. The real cost was blindness. From 15:21:33 to 15:31:38 the platform agent blocked on `until [ -s ... ]`, waiting for 8 queue-health batches. Meanwhile tail3.log was filling with 494 unhandled-rejection and 530 socket-closed lines from the bad deploy. The harness Monitor tool exists and was used (14:52:13 and 15:21:13), but agents still also blocked in the foreground.
IMPL: Add /Users/antonabyzov/Projects/github/specweave-umb/scripts/release/ci-wait.sh with these modes:
- pr, run, tag-workflow
- npm: `npm view pkg@ver version --prefer-online` with backoff 5/10/15s
- url
- log <file> --ok <regex> --fail <regex>: exits 1 as soon as the fail regex appears, e.g. 'socket has been closed|unhandled rejection'
Poll `gh api -i` with If-None-Match. On red, print `gh run view <id> --log-failed | tail -80`. Exit codes: 0 green, 1 red, 2 timeout (default 540s, so it never trips the 600s cap). Document it as run_in_background plus Monitor. Rule in the release runbook: no foreground wait whose exit condition ignores error output.

## F04 [scan-gap] real=True safe=True save=None->0 :: Release-timing regression scanner with a per-step baseline and CI workflow lint
FILES: /Users/antonabyzov/Projects/github/specweave-umb/scripts/release/timing.py, /Users/antonabyzov/Projects/github/specweave-umb/.specweave/metrics/release-timings.jsonl
EVIDENCE: Nothing records per-step release durations, so today's regressions were seen only by reading logs afterwards:
- platform unit-tests at 822 and 865s
- the Linux desktop build at 872s (rpm 321s)
- the studio server suite at about 1500s
Workflow problems found by hand that no scanner flags:
- missing timeout-minutes in specweave release.yml and test.yml
- no concurrency in vskill ci.yml
- rust-cache without shared-key or save-if
- continue-on-error checks that stay red (claude-code-review.yml; vskill e2e-live-nightly red across its last 100 runs)
.specweave/metrics/dora-latest.json exists but has no step-level data.
CHANGE: Add scripts/release/timing.py with three subcommands:
- record: append {run_id, repo, step, seconds, kind, sha, at} to .specweave/metrics/release-timings.jsonl. It is called by ci-wait.sh and release.sh, and also ingests `gh run view --json jobs` step timings.
- check: baseline is the median of the last 10 runs per step; flag a step when it exceeds max(1.5x baseline, baseline+60s); exit 2 on flags.
- scan-ci: parse every .github/workflows/*.yml in the workspace repos and flag jobs without timeout-minutes, workflows without concurrency, setup-node/setup-python without cache, Swatinem/rust-cache without shared-key/save-if, continue-on-error jobs red in more than 80% of their last 20 runs, and required checks whose p50 exceeds 300s.
Seed the jsonl with today's measured numbers. Run check at the end of `release.sh ship`.
RISK: Low. It is reporting only.
VERIFIER: No step timing is recorded anywhere, which is accurate; .specweave/metrics has only dora-latest.json and dora-report.md. Two scanner traps:
- specweave claude-code-review.yml uses job-level continue-on-error, so the workflow run concludes success (20 of 20 recent runs) while the claude-review check fails on PRs #2065 and #2069. A red-rate rule must read check-runs, not workflow-run conclusions.
- vskill-platform is PRIVATE, so ubuntu-latest is a 2-vCPU runner where vitest defaults to 1 worker. The scanner should flag that.
IMPL: Add /Users/antonabyzov/Projects/github/specweave-umb/scripts/release/timing.py, with the log at .specweave/metrics/release-timings.jsonl (not ignored). Ingest from `gh run view <id> --json jobs`, with step started/completed times. scan-ci rules:
1. A job without timeout-minutes.
2. A `push:` trigger without `paths` in a workflow whose pull_request trigger has paths (catches sidecar-smoke.yml).
3. Swatinem/rust-cache in a workflow with no main-branch save (catches desktop-release.yml and sidecar-smoke.yml).
4. vitest in a private repo on ubuntu-latest without --maxWorkers.
5. continue-on-error jobs whose check-run is red in more than 80% of the last 20 PRs.
Seed it with today's values:
- platform vitest 821/594/865 (main 788, 859 failed)
- desktop linux 872 (rpm 321), windows 701, macos 544
- studio server 1385 and 1313
- specweave verify-package 177

## F05 [wait-gap] real=True safe=True save=120->150 :: Gate cleanup per track instead of on all tracks
FILES: /Users/antonabyzov/Projects/github/specweave-umb/scripts/release/release.sh
EVIDENCE: The ship workflow used pipeline(TRACKS, ship -> verify) and then a single cleanup agent that waits on every track. specweave finished at 14:48:53 and vskill at 15:06:35, then sat idle until platform (15:55:27) and studio (still running at ~15:57:30) finished. That is about 4000s and 2950s of idle worktrees, branches and stale claims held open.
CHANGE: Make cleanup a per-track phase: ship -> verify -> cleanup <track>, which removes merged worktrees, deletes merged branches and releases claims for that repo only. Run it as the last stage of each track's pipeline. The final cross-track step then only writes the umbrella summary and commits umbrella state, so it takes seconds instead of a full agent run after the slowest track.
RISK: Low. Cleanup must only touch the track's own worktrees, and never studio-rel-*/studio-release-* dirs of another in-flight release.
VERIFIER: Idle finished worktrees are not wall-clock cost. The overall finish is set by studio, which is still running past 16:08 with M4 waiting-for-quiet. The cleanup prompt also deliberately protects the shipping tracks' worktrees and ends in a single umbrella archive commit, which must stay serial. The only real gain is running cleanup for specweave, vskill and vskill-platform while studio is still going, instead of after it. The profiler's current_seconds of 4000 is idle time, not saving.
IMPL: In the workflow script, make the per-track pipeline ship -> verify -> cleanup(track). The cleanup prompt is restricted to that repo's worktrees, only where the PR is MERGED and `git cherry` shows all '-', excluding studio-rel-*/studio-release-* and named in-flight worktrees. A final step commits .specweave/archive/worktree-leftovers-<date>/ to the umbrella once.

## F06 [wait-gap] real=True safe=True save=1000->0 :: Remove the pre-ship permission round-trip by encoding policy
FILES: /Users/antonabyzov/Projects/github/specweave-umb/scripts/release/release.sh, /Users/antonabyzov/Projects/github/specweave-umb/.specweave/release/manifest.json
EVIDENCE: The audit result went to Anton as a question at 14:16:18, he answered at 14:34:28, and the ship started at 14:36:12, so 1090s of human wait plus 104s of relaunch. Memory feedback_git_push_deploy.md and feedback_studio_merge_without_asking.md already say to merge ready PRs, release, deploy and verify without asking.
CHANGE: `release.sh ship all` runs status and continues straight into shipping, reading the policy flags from the manifest (F02) without a confirmation turn. It asks only for items the manifest marks as needing a manual gate: data migrations, auth, payments, per the project's Manual Verification Gates. Those are collected and asked once, at the end.
RISK: Medium. It ships without a human checkpoint, but this matches the owner's recorded policy. Keep the manual-gate list explicit.
VERIFIER: The 1090s was Anton's reply latency (14:16:18 to 14:34:28). The profiler's evidence is wrong on one point: before the question, feedback_git_push_deploy.md only said to deploy after push for specweave, vskill and vskill-platform, and feedback_never_ask_pr_review.md covered merging. Neither covered cutting the studio release, removing about 85 worktrees, or dropping stashes and discarding leftovers. Those are destructive, and CLAUDE.md allows confirming them. The parent closed the gap at 14:34:52 by rewriting feedback_git_push_deploy.md to say never ask, including worktree cleanup. So for Claude sessions the saving is already banked; release.sh adds about 0. The remaining value is cross-tool: Codex sessions don't read ~/.claude memory.
IMPL: Add a 'Release policy' section to /Users/antonabyzov/Projects/github/specweave-umb/AGENTS.md (committed, read by every tool) and a policy block in manifest.json:
- merge green PRs, release, deploy, verify, and remove fully merged worktrees without asking
- still ask before discarding work that exists nowhere else
- still ask for the Manual Verification Gates (data migrations, auth, payments)
Note: `specweave update` rewrites parts of AGENTS.md, so put this under Project notes, which survives.

## F07 [reliability-gap] real=True safe=True save=0->0 :: Progress visibility: per-track status heartbeat
FILES: /Users/antonabyzov/Projects/github/specweave-umb/scripts/release/release.sh, /Users/antonabyzov/Projects/github/specweave-umb/.specweave/state/release-run.json
EVIDENCE: No progress was reported to the user for 38 minutes, until Anton asked "are you stuck?" at 15:14:54 while platform and studio were deep in CI waits and reruns. The workflow journal only gets an entry when a track finishes.
CHANGE: Every release.sh phase transition and every ci-wait.sh poll tick (at most once per 60s) updates .specweave/state/release-run.json with track, phase, started_at, waiting_on (run url or PR) and eta from the F04 baseline. Add `release.sh status --run` to render it. Orchestrator prompts post the rendered status at each phase change.
RISK: Low.
VERIFIER: There were two interrupts, not one: 'are you stuck?' at 15:14:54 (38 min after the parent's last turn at 14:36:58) and 'again stuck? Show me the progress bars' at 15:52:12. The cause is structural. The parent ended its turn with no_reply_needed and wakes only on workflow completion or a user message, and the RULES bar workflow agents from mcp__hearthbot tools. So nothing could post progress, whatever release.sh writes.
IMPL: In the orchestration pattern (the release skill or the workflow-authoring notes), the parent arms a Monitor right after launching the workflow. The Monitor tails <wf dir>/journal.jsonl, plus `stat -f %m agent-*.jsonl` and .specweave/state/release-run.json, which is gitignored and fine for ephemeral state. On each 'result' line, or every 10 minutes, the parent calls update_status with one line per track (phase, waiting_on URL, ETA from the timing.py baseline).

## F08 [slow-step] real=True safe=True save=950->850 :: Shard the studio server test suite locally
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/apps/server/vite.config.ts, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/scripts/release/test-sharded.mjs
EVIDENCE: The studio t-int phase took 1520s, mostly the server suite. apps/server/vite.config.ts sets fileParallelism: false with a WeightedShardSequencer and 120000ms test/hook timeouts. The repo's own CI (.github/workflows/ci.yml test_server) already splits this suite into 6 shards on blacksmith-4vcpu with timeout 10. Actions are disabled on the repo, so the release ran it serially in one process on the Mac.
CHANGE: Add scripts/release/test-sharded.mjs. It spawns N=4 (configurable) parallel `vitest run --shard i/N` processes for apps/server, reusing the existing WeightedShardSequencer. Each process gets its own temp HOME and port base, because fileParallelism:false exists to avoid shared state. It aggregates exit codes and writes a junit or blob report per shard. release-local.mjs (F09) calls it.
RISK: Medium. Tests that bind fixed ports or share ~/.specweave-studio need per-shard isolation, or they flake.
VERIFIER: Confirmed. origin/main apps/server/vite.config.ts sets fileParallelism:false with a comment that parallel files 'introduce load-sensitive flakes'. The suite took 1385.10s on t-int and 1312.85s on t-rel, across 690 files with one worker per file. The Mac has 16 cores (12 performance). Actions are disabled on specwithcode-dev ({"enabled":false}), while ci.yml already uses 6 shards. Risk: running shards concurrently on M4, which also hosts the live studio service and agent sessions, raises load. The serverSettings test 'reloads when a dangling settings link gets its destination' (2s Effect timeout) already failed once in two isolated runs on main. Flakes give false reds, not false greens, so this is safe but needs isolation.
IMPL: Add specweave-studio/scripts/release/test-sharded.mjs. It spawns N=3 (leaving cores for the live service) `vp run --filter specweave-studio test --shard i/3`, the exact CI form. Each shard gets its own TMPDIR and port base. Override HOME only after checking that gitConfig.setup.ts and the pnpm store don't depend on it. Collect exit codes and per-shard logs into <release dir>/t-*/server-i.log. Raise that serverSettings test's timeout from 2s to 10s, or tag it flaky with retry:1. The higher-leverage alternative is re-enabling Actions, where ci.yml already does 6 shards with 10-minute timeouts on Blacksmith; that is Anton's account and cost decision.

## F09 [redundant-work] real=True safe=True save=1400->1000 :: Skip the studio t-rel full re-run with a tree-hash test receipt; bump the version before the first build
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/scripts/release/test-receipt.mjs, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/scripts/release/release-local.mjs
EVIDENCE: t-int tested origin/main plus cherry-picks of #235 and #237. t-rel then re-ran the whole suite (1445s) on origin/main after the #235/#237 merges, #243, a scroll-anchor change, contrast fix 4d2b1c676 and version bump fa43e7c19. The server-side diff between the two trees was negligible, and the changes were web or contrast or version only. The version bump also forced a second signed DMG build (228s after the first 212s).
CHANGE: After a green package test run, write a receipt to <release dir>/receipts/<package>.json containing the git tree hash of the package dir and its workspace deps. On the next phase, re-run only packages whose tree hash changed. A version-only change to package.json files is normalized out of the hash. In release-local.mjs, apply the version bump and any queued fixes before the first signed build, so it is built once.
RISK: Medium. Hash scope must include shared packages and lockfiles, or a real regression could be skipped. Default to re-running when unsure.
VERIFIER: The server part holds. `git diff --stat HEAD origin/main` at 15:12:46 showed changes only in apps/desktop and apps/web, and the bump at 15:13:16 changed only the version line in 4 package.json files. So the t-rel server rerun (1313s) tested the same server tree as t-int. Two corrections:
- The version bump happened before the first signed build (bump 15:13:16, build 15:14:36). The second DMG build at 15:38:50 was caused by the second contrast fix, text-destructive, which the t-rel web suite caught. That was a real defect, so web must always re-run, and receipts would not have avoided the rebuild.
- The t-rel block on the critical path was about 1100s (15:19:19 to 15:37:41), not 1445s, because the first DMG build and helpers overlapped its first 5 minutes.
IMPL: specweave-studio/scripts/release/test-receipt.mjs keys each receipt on sha256 of:
- `git rev-parse HEAD:apps/server`
- the tree hashes of each workspace dependency in apps/server/package.json (packages/contracts, packages/shared and so on)
- HEAD:pnpm-lock.yaml, root vite.config.ts, tsconfig*, scripts/lib
- `node -v`
Strip the package.json 'version' field before hashing, but only for stable-to-stable bumps, because the vite config derives cliBuildChannel from /-(nightly|preview)\./ in the version. Store it at <release dir>/receipts/<pkg>.json. When unsure, rerun.

## F10 [reliability-gap] real=True safe=True save=600->370 :: Studio has no pre-merge gate: add a local CI gate, fix the typecheck command, quarantine the flake
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/scripts/ci/local-gate.mjs, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/.github/workflows/ci.yml, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/docs/studio/releasing.md
EVIDENCE: GitHub Actions is disabled on the specweave-studio repo, so merges to main are ungated and main went red before the release. The release agent ran `npx tsc` instead of the repo's typecheck, which produced a false red (Effect plugin TS377) and cost a diagnosis loop. A serverSettings test flake forced extra reruns. docs/studio/releasing.md documents pieces only, with no end-to-end gate.
CHANGE: Add scripts/ci/local-gate.mjs. It runs the same jobs as ci.yml (repo typecheck script, lint, sharded tests via F08) and writes a merge receipt (tree hash plus results) that the merge step requires. Alternatively, re-enable Actions on a self-hosted runner. Name the exact typecheck command in the manifest and releasing.md so agents never call bare `npx tsc`. Mark the serverSettings flaky test with a retry or quarantine tag, and open an increment to fix it.
RISK: Low to medium. The receipt check is advisory unless it is wired into the merge path.
VERIFIER: Ungated main is real: themeContrastClasses was red on main (it failed in the studio-lockfix worktree, which is main plus the lockfile) since #230, and serverSettings flakes on main. The profiler's typecheck claim is wrong. apps/server's own `typecheck` script is `tsc --noEmit`, the same command run-tests.sh ran. The 51 TS377xxx Effect-plugin diagnostics were waved off in seconds of reasoning ('known pre-existing effect-lint diagnostics'), not in a diagnosis loop. The real cost of the ungated main was the late contrast failure: second DMG build (228s) plus redoing helpers and plan (about 80s) and the fix commit.
IMPL: specweave-studio/scripts/ci/local-gate.mjs runs exactly what ci.yml runs:
- `vp check`
- `vp run knip:check`
- `vpr typecheck`, i.e. root `vp run -r --concurrency-limit 2 typecheck`
- web/desktop/contracts tests
- server via test-sharded.mjs (F08)
It writes a merge receipt keyed by tree hash. The release runbook (docs/studio/releasing.md) requires a green local-gate receipt for HEAD before `gh pr merge`. Quarantining or fixing the serverSettings test is the same as F08.

## F11 [discovery-gap] real=True safe=False save=650->600 :: Studio one-command resumable release script; commit the fleet helpers
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/scripts/release/release-local.mjs, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/fleet_request.py, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/fleet_hosts.py, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/docs/studio/releasing.md
EVIDENCE: The studio track built its procedure by hand:
- env via nvm 22.20.0, SDKROOT pointing at the MacOSX26.2 SDK, anaconda3 stripped from PATH, and CSC_LINK, CSC_KEY_PASSWORD, APPLE_API_KEY, APPLE_API_KEY_ID, APPLE_API_ISSUER and STUDIO_GOOGLE_OAUTH_* sourced from various files
- ad-hoc /tmp/fleetssh.sh and /tmp/fleet-request.py
- a sequence of bundle.mjs, verify-bundle.mjs, update.py, update_request.py, mac-signature.mjs, public-mirror/publish.mjs and mcp-after-restart.mjs
This cost about 356s of critical-path discovery, and the helpers are lost when /tmp is cleaned. Then it blocked about 600s on the fleet update.
CHANGE: Add scripts/release/release-local.mjs <version>. Its phases are recorded in <release dir>/state.json so a rerun resumes:
- preflight: check that each required env file and cert path exists without printing values; set SDKROOT and the Node version from the manifest; strip conda from PATH
- worktree
- test: F08 plus F09
- build signed dmg
- notarize and staple verify
- bundle and verify-bundle
- mirror publish
- fleet
- post-restart verify
Commit fleet_request.py, which takes `--hosts all --version X --mode force --wait --timeout 900`. It reads inventory through fleet_hosts.py and polls each host's update_agent state until it reports applied, or until a rollback, instead of a fixed sleep. Rewrite docs/studio/releasing.md as the end-to-end runbook calling this script.
RISK: Medium. Signing and fleet steps touch production hosts, so keep each phase idempotent and keep the existing snapshot/rollback in update.py.
VERIFIER: Discovery and the lost /tmp helpers are real, but the helpers were pre-existing (01:04), not written today. The repo already has scripts/studio-fleet/update_request.py, fleet_hosts.py, quiescence.py and update.py, so extend those instead of adding fleet_request.py. The 600s fleet wait from 15:47:00 to 15:57:00 was caused by sending a `check` request: normal mode with quietMinutes 10 means waiting-for-quiet. Once `install 1.0.36` was sent at 15:57:12, M1 and M3 reported 1.0.36 within about 16s. M4 then stayed 'waiting-for-quiet ... (3 running tasks)' past 16:07. The running tasks on M4 are most likely this orchestration's own sessions, so `--hosts all --mode force --wait` would either block for good or, once the 15-minute force hold expires, restart the service hosting the release agents mid-run. That part is unsafe as written.
IMPL: specweave-studio/scripts/release/release-local.mjs keeps a resumable <release dir>/state.json across these phases:
- preflight: check file existence only; set SDKROOT; strip anaconda3 from PATH; use nvm 22.20.0
- test (F08/F09)
- signed build
- bundle and verify-bundle
- release on both repos
- mirror publish
- fleet
Fleet phase: add a CLI to update_request.py, `--host <id> --install <ver> --mode force|normal`. Run force plus wait only for hosts that are not the orchestrator. For the host running the release (M4), write a normal-mode install request, do not wait, and report it as 'queued: installs at next quiet'. Rewrite docs/studio/releasing.md as the end-to-end runbook calling this script.

## F12 [slow-step] real=True safe=True save=1400->1350 :: Shard platform unit-tests.yml with merged coverage
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/.github/workflows/unit-tests.yml, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/vitest.config.ts
EVIDENCE: vskill-platform .github/workflows/unit-tests.yml is one job (timeout 25) running `npx vitest run --coverage --reporter=dot --exclude ...`. Today it took 822s, 594s and 865s on 3 PRs, 2281s blocked in total, and it is the dominant wait in the platform track. vitest.config.ts has coverage thresholds of 60 that must still apply to the whole suite.
CHANGE: Use a matrix of shard [1,2,3,4], each running `npx vitest run --shard ${{ matrix.shard }}/4 --coverage --reporter=blob --reporter=dot` and uploading .vitest-reports as an artifact. A final `coverage` job downloads them and runs `npx vitest --merge-reports --coverage`, so the 60% thresholds are enforced on the merged report. Make that final job the required check. Add `concurrency: {group: unit-${{ github.ref }}, cancel-in-progress: true}` and setup-node npm cache.
RISK: Medium. Coverage merge requires the same vitest version across jobs. Shard imbalance can leave one shard slow; tune with a sequencer if needed.
VERIFIER: Durations confirmed: PR 128 821s, PR 129 594s, PR 130 865s; main runs 788s and 859s (failed). unit-tests.yml ALREADY has `concurrency: unit-tests-${{ github.ref }}, cancel-in-progress: true` and setup-node `cache: npm`, so those parts are redundant. Root cause the profiler missed: vskill-platform is PRIVATE, so ubuntu-latest gives 2 vCPU and vitest's run-mode default (CPUs minus 1) gives 1 worker. Wall time is 788s against phase sums of about 652s, i.e. effectively serial. The branch is not protected, so there is no 'required check' to rename. Platform was not on today's overall critical path (studio was), so the saving is per-track.
IMPL: Cheap first step in /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/.github/workflows/unit-tests.yml: add `--maxWorkers=2` to the Vitest step and measure. Then:
- `strategy: {fail-fast: false, matrix: {shard: [1,2,3,4]}}` with `timeout-minutes: 15`
- run `npx vitest run --shard ${{ matrix.shard }}/4 --coverage --reporter=blob --reporter=dot --exclude "src/__tests__/account-repos-parity.test.tsx"`
- upload with actions/upload-artifact@v4 `{name: blob-${{ matrix.shard }}, path: .vitest-reports/, include-hidden-files: true, retention-days: 1}`. The dot directory is skipped without include-hidden-files.
- a `coverage` job with `needs: vitest` and `if: ${{ !cancelled() }}`: checkout, npm ci --ignore-scripts, download-artifact pattern blob-* merge-multiple into .vitest-reports, `npx vitest run --merge-reports --coverage`, so the 60% thresholds apply to the merged report.
Billing: each shard repeats about 50s of setup on a private repo.

## F13 [reliability-gap] real=True safe=False save=1800->600 :: Platform deploy gate: CI-green check, gradual rollout, error-rate watch, auto-rollback, version endpoint
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/scripts/release/deploy.sh, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/package.json, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/src/app/api/v1/version/route.ts, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/.github/dependabot.yml
EVIDENCE: The pg driver upgrade regression reached prod and cost about 1980s of rework: diagnose, fix PR, CI, redeploy, and #130 adding a dependabot pg ignore. There were 4 deploys today. package.json `deploy` runs `npm run clean && npm run build:worker && verify-queue-health-build && npx wrangler deploy && verify-queue-health-deploy`. That deploys 100% immediately, with no check that main CI is green and no automatic rollback. There is no /api/v1/version, so confirming the deployed sha needed manual observation (about 1000s).
CHANGE: Add scripts/release/deploy.sh. It:
1. refuses unless unit-tests.yml is green for HEAD (gh api check-runs), or the local `npx vitest run` exits 0
2. builds once (F14)
3. runs `wrangler versions upload --tag <sha>` and then `wrangler versions deploy <new>@10% <old>@90%`
4. runs `wrangler tail --format json` for 180s, plus a hit on /api/v1/version and a DB-touching health route over Hyperdrive
5. promotes to 100% if the 5xx rate is at most baseline
6. otherwise runs `wrangler rollback` and exits 1
Add /api/v1/version returning {sha, builtAt} from a build-time env. Group pg/hyperdrive-related bumps in dependabot.yml so they get an explicit DB smoke.
RISK: Medium. Gradual deploy changes Durable Object and queue consumer semantics; confirm queue consumers tolerate two live versions.
VERIFIER: The regression is real. Deploy f2843c50 (15:19:04) included dependabot #126 (11 production dependencies, pg 8.16.3 to 8.23). It closed Hyperdrive sockets in the Worker and was rolled back at 15:31:50; #130 pinned pg and was redeployed at about 15:50. But #126 had green CI (vitest 14m04s, e2e 3m43s), so the profiler's 'refuse unless CI green' gate would not have caught it. Unit tests mock Prisma, and the e2e suite runs the Node runtime, not workerd. The roughly 1000s 'observation' was the queue-drain soak the prompt asked for, not checking the deployed SHA. Gradual `wrangler versions deploy` at 10/90 is risky here. The worker has Durable Objects (OpenNext DOQueueHandler and DOShardedTagCache, BucketCachePurge, UpdateHub), a queue consumer and 7 crons. A version split mixes OpenNext cache, tag-cache and asset versions, and DO migrations need a full `wrangler deploy`.
IMPL: vskill-platform/scripts/release/deploy-watch.mjs:
1. Before deploy, read prev=`npx wrangler deployments list --json`[0] and take a 60s baseline of `wrangler tail verified-skill-com --format json`, counting events with outcome!='ok', non-empty exceptions, or logs matching /socket has been closed|unhandled rejection/.
2. Run `npm run db:generate && npm run deploy`.
3. Tail for 180s. If errors per minute exceed max(3x baseline, 5), run `npx wrangler rollback <prev> --message 'auto-rollback' -y` and exit 1.
Add `"deploy:watched": "node scripts/release/deploy-watch.mjs"`. Optionally add /api/v1/version from the version_metadata binding. Also add the CI workerd smoke from the missed findings.

## F14 [redundant-work] real=True safe=False save=200->130 :: Platform deploy builds Next up to three times
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/package.json, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/scripts/push-deploy.sh, /Users/antonabyzov/.claude/projects/-Users-antonabyzov-Projects-github-specweave-umb/memory/project_vskill_platform_deploy.md, /Users/antonabyzov/.claude/projects/-Users-antonabyzov-Projects-github-specweave-umb/memory/feedback_git_push_deploy.md
EVIDENCE: The build script is `npm run build:prepare && next build`, and deploy is `npm run clean && npm run build:worker && ...`. The OpenNext build:worker runs next build itself. Memory project_vskill_platform_deploy.md and feedback_git_push_deploy.md tell agents to run `npm run build && npm run build:worker && npm run deploy`, which is 3 builds, and scripts/push-deploy.sh follows the same pattern. There were 4 deploys today.
CHANGE: Make `npm run deploy` the only documented command (it already cleans and builds once). Update push-deploy.sh to drop its preceding build calls, and fix both memory notes to say `npm run deploy` (or `scripts/release/deploy.sh` once F13 lands).
RISK: Low.
VERIFIER: Each of today's deploys ran Next twice, not three times. deploy1-4.log each show two 'Creating an optimized production build' (compile 7-14s each), because the agent ran `npm run build && npm run deploy`. deploy itself does clean and build:worker, and OpenNext's buildNextjsApp runs `npm run build`. The orchestrator prompt, copied from memory, prescribed three builds: build, then build:worker, then deploy. The profiler is wrong about scripts/push-deploy.sh: it already runs `db:generate`, then `db:migrate`, then `deploy`, a single build that also applies migrations. Changing it as proposed would be a regression. Documenting bare `npm run deploy` is unsafe, because deploy never runs `prisma generate`, so a schema change would ship a stale Prisma client. Separately, push-deploy.sh uses `grep -oP`, which macOS BSD grep rejects ('invalid option -- P'), so INTERNAL_BROADCAST_KEY is never read on the Mac.
IMPL: In vskill-platform/package.json, set `"deploy": "npm run db:generate && npm run clean && npm run build:worker && node scripts/verify-queue-health-build.mjs && npx wrangler deploy && node scripts/verify-queue-health-deploy.mjs"`, so `npm run deploy` stands on its own. Keep push-deploy.sh's db:migrate. Replace its `grep -oP 'INTERNAL_BROADCAST_KEY=\K.*'` with `sed -n 's/^INTERNAL_BROADCAST_KEY=//p'`. In memory, rewrite project_vskill_platform_deploy.md: it still claims deploy = `opennextjs/cloudflare deploy`, which went stale with e635207b on 2026-09-02. Rewrite the feedback_git_push_deploy.md how-to the same way: `npm run deploy` (after the package.json change) or `bash scripts/push-deploy.sh` when migrations changed.

## F15 [wait-gap] real=False safe=True save=700->200 :: Replace platform prod observation sleeps with deterministic checks; rolling drainRate
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/scripts/verify-queue-health-deploy.mjs, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/src/app/api/v1/version/route.ts
EVIDENCE: The platform agent spent about 1000s (net of CI overlap) watching prod after deploys, via sleeps and repeated queue/backlog reads, to decide the state was healthy. The backlog showed about 479.5k RECEIVED, and drainRate was computed over a point-in-time sample, so it needed repeated sampling. verify-queue-health-deploy.mjs already exists but gives a single snapshot.
CHANGE: Have verify-queue-health-deploy.mjs compute drainRate over a rolling window, either 5 minutes of persisted samples or a delta between two reads N seconds apart within one run. Exit 0 when deployed sha == expected (via /api/v1/version), the 5xx rate is under threshold and drainRate > 0. Release agents call it once, with `--window 120`, instead of observing manually.
RISK: Low.
VERIFIER: The evidence is wrong. src/app/api/v1/queue/health/route.ts already returns drainRate.{last1h,last6h} summed from hourly QUEUE_METRICS_KV buckets, which is rolling, not a point-in-time sample. The roughly 10-minute soak was mandated by the orchestrator prompt ('poll /api/v1/queue/health a few times over ~10 minutes'). The open problem was capacity: RECEIVED grew from 478,119 to 479,482 at 400-550 scans an hour, and no observation tool fixes that. verify-queue-health-deploy.mjs checks the contract (schemaVersion 2, ageBasis updatedAt), not health trends. A post-deploy window shorter than an hour needs minute-resolution buckets.
IMPL: If wanted, add per-minute counters to QUEUE_METRICS_KV (with a TTL) and expose drainRate.last10m. Change the orchestrator prompt from 'poll for ~10 minutes' to one call of the F13 deploy-watch, plus one /api/v1/queue/health read showing drainRate.last10m > 0.

## F16 [slow-step] real=True safe=True save=170->170 :: Tauri rpm bundling: cheaper compression on the critical Linux job
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/src-tauri/tauri.conf.json
EVIDENCE: Desktop Release run 38918885879 had a wall clock of 966s. Linux was the critical path at 872s, of which 697s was the Build Tauri app step and rpm bundling about 321s. Windows took 701s and macos 544s. src-tauri/tauri.conf.json targets app, dmg, msi, nsis, deb, rpm and appimage, and linux.rpm sets only depends, so the default xz compression applies.
CHANGE: Set bundle.linux.rpm.compression to {"type":"zstd","level":3} or {"type":"gzip","level":6}. Linux drops to about 550-600s, so Windows (701s) becomes the critical path. The realistic wall-clock saving is about 170s, and more if F17 also speeds up Windows.
RISK: Low. zstd rpm payload needs rpm 4.14+ on install targets (all current Fedora/RHEL/openSUSE); gzip is the universally safe choice.
VERIFIER: The step really is slow. 'Bundling ...x86_64.rpm' ran from 14:56:24 to 15:01:45 (321s), while the deb, at the same 49.19 MiB, bundled in 3s. The profiler's root cause is unverified and probably wrong. The local @tauri-apps/cli 2.12.1 config.schema.json documents bundle.linux.rpm.compression as 'Defaults to Gzip with level 6', not xz, so setting gzip 6 may change nothing. Saving appears only once Linux drops below Windows (701s). GitHub download counts for desktop-v1.0.64 show 0 for every rpm asset (R2 downloads unknown).
IMPL: Measure first. In /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/src-tauri/tauri.conf.json, set `"bundle":{"linux":{"rpm":{...,"compression":{"type":"none"}}}}`, or `{"type":"gzip","level":1}`, and time it on a throwaway desktop-v*-rc tag. If rpm has no users (check R2 logs), drop rpm from the linux matrix `bundles: deb,rpm,appimage` in desktop-release.yml. Signatures are computed after bundling, and the Linux updater uses the AppImage, so neither choice affects updater integrity.

## F17 [slow-step] real=True safe=True save=600->200 :: Rust caches never hit on tag releases and are re-saved uselessly; path-filter cargo CI
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/desktop-release.yml, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/ci.yml
EVIDENCE: Swatinem/rust-cache@v2 in desktop-release.yml (workspaces src-tauri -> target) has no shared-key. The desktop release runs on a tag ref (desktop-v1.0.65), which can only restore caches from itself or the default branch. Its key includes the Cargo.lock hash, and the bump PR #181 changes Cargo.lock every release, so every release builds cold:
- Build Tauri app: 697s linux, 507s windows, 403s macos
- Post Cache Cargo: 40s macos and 37s windows saving caches no later tag can read
In ci.yml, PR #180 changed only .github/workflows/e2e-live-nightly.yml yet ran `cargo check + test src-tauri (windows-latest)` for 532s, the longest check.
CHANGE: In desktop-release.yml, use rust-cache with `shared-key: desktop-${{ matrix.platform }}`, `save-if: false` and `add-job-id-key: false`. Add a main-branch job (in ci.yml, or a small desktop-cache-warm.yml on push to main touching src-tauri/**) that builds `cargo build --release` for each OS with the same shared-key and `save-if: github.ref == 'refs/heads/main'`, so tag builds restore a warm release-profile target. In ci.yml, gate the cargo jobs with a dorny/paths-filter (or `on.pull_request.paths`) on src-tauri/** and Cargo.*, so workflow-only and TS-only PRs skip the 532s Windows cargo job. Add `concurrency: {group: ci-${{ github.ref }}, cancel-in-progress: true}`.
RISK: Low to medium. A warm cache can mask a clean-build failure, so keep a weekly cold build. Path filters need the required-check setup to treat skipped as passing.
VERIFIER: Cold tag builds are confirmed: 'No cache found' on all three OS. Compile times were Linux 4m20s, macOS 5m07s, Windows 7m02s, and Post Cache Cargo saved 40s (macOS) and 37s (Windows) for nothing. The PR #180 claim is wrong. ci.yml has no cargo job. The 'cargo check + test src-tauri (windows-latest)' check comes from sidecar-smoke.yml, whose `push: branches: ['fix/**']` trigger has no paths filter, and PR #180 lived on fix/e2e-live-platform-token. Today #180's wait overlapped #181's legitimate cargo run (8m37s, since it touched src-tauri), so today's saving is 0. The release profile has lto=true and codegen-units=1, so cached dependencies save only part of the compile; the fat-LTO link still runs.
IMPL: In vskill/.github/workflows/sidecar-smoke.yml, add the pull_request path list under `push:` and add `main` to the push branches. Add `concurrency: {group: sidecar-smoke-${{ github.ref }}, cancel-in-progress: ${{ github.event_name == 'pull_request' }}}`. In rust-windows, use rust-cache `save-if: ${{ github.ref == 'refs/heads/main' }}` so PRs restore a warm debug cache.
Add desktop-cache-warm.yml: on push to main with paths src-tauri/** and src-tauri/Cargo.lock, using the same matrix as desktop-release. It builds frontend dist and sidecar prerequisites, then runs `cargo build --release --locked --target ${{ matrix.target }} --manifest-path src-tauri/Cargo.toml`. It needs the same GITHUB_OAUTH_CLIENT_ID env, because the release build.rs refuses the placeholder. Use rust-cache `{workspaces: 'src-tauri -> target', shared-key: desktop-${{ matrix.platform }}, add-job-id-key: false}`.
In desktop-release.yml, use the same shared-key with `save-if: false`. cache-workspace-crates stays false, so the shipped binary is always rebuilt. Add `concurrency` to ci.yml.

## F18 [wait-gap] real=True safe=True save=500->540 :: Drop the desktop version-bump PR round-trip
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/scripts/release/release-desktop.sh, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/desktop-release.yml
EVIDENCE: vskill PR #181 (release-desktop.sh fix plus a version bump in Cargo.toml, Cargo.lock and tauri.conf.json) was open from 14:40:13Z to 14:49:17Z, 544s, before the tag could be pushed and the Desktop Release started at 14:49:25Z. desktop-release.yml derives the version from the tag. release-desktop.sh already supports a direct push to main.
CHANGE: Pick one:
- Have desktop-release.yml stamp the tag version into tauri.conf.json and Cargo.toml inside the job (with `cargo update -p <crate> --offline` for the lock) and stop committing bumps.
- Have release-desktop.sh commit the bump straight to main and tag it in one step (admin push, per policy), skipping PR CI for a version-only diff.
Keep script fixes like today's on a normal PR, separate from the release.
RISK: Low. Stamping in CI means the repo's version lags the released one; the tag stays the source of truth.
VERIFIER: The 544s PR round trip happened, but the proposed fix already exists. desktop-release.yml lines 148-171 already derive the version from the tag and stamp Cargo.toml, tauri.conf.json and Cargo.lock. release-desktop.sh lines 148-157 already commit the bump straight to main and tag it. The agent opened PR #181 by choice, to bundle a release-desktop.sh fix (removing the stale PLATFORM_REPO_REL step) with the bump. Because the bump touches src-tauri/, it also triggered the 8m37s Windows cargo check. The saving is on the vskill track only; it was not on the overall critical path.
IMPL: Add a runbook and manifest rule for vskill desktop: tag `desktop-v<next>` on origin/main HEAD after its ci.yml push run is green, with no bump PR, because CI stamps the version. Ship script fixes as a separate PR in parallel. Optionally drop step 3 (the bump commit) from release-desktop.sh so the repo never needs a version-only commit.

## F19 [redundant-work] real=False safe=True save=250->10 :: vskill npm-release re-runs the full test suite; registry verify done by the agent
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/npm-release.yml
EVIDENCE: npm-release.yml's 'Test the full package' (`npm test -- --maxWorkers=4`) took 157s for a SHA that had already passed ci.yml on main. Afterwards the agent polled the npm registry for 130s by hand. specweave already has scripts/release/verify-package-install.mjs for that verification.
CHANGE: Before testing, query `gh api repos/{repo}/commits/${{ github.sha }}/check-runs`. Skip 'Test the full package' when ci.yml unit-full succeeded for the same SHA, and run it otherwise. Add a post-publish step that runs a port of specweave's verify-package-install.mjs (npm view plus a clean `npx vskill@<v> --version` install, with backoff), so the workflow result is the readiness signal and agents stop polling.
RISK: Low. The skip only applies when there is a green check for the identical SHA.
VERIFIER: The skip condition can't be met at publish time. The tag was pushed 6s after the merge. The ci.yml push run for a5fa1a04 ran 14:36:45 to 14:40:23, while npm-release's 'Test the full package' ran during the same minutes (157s). So there is no green check for that SHA yet, and waiting for one costs the same time. Moving the registry poll into the workflow only moves the wait; the agent still waits for the workflow. The 157s test is a legitimate gate on the published artifact (OIDC provenance is unaffected either way).
IMPL: Keep the test step. Optionally have the agent wait with `ci-wait.sh npm vskill 1.2.8` (F03) instead of a hand-written loop.

## F20 [slow-step] real=True safe=True save=60->10 :: specweave release.yml: create the GitHub Release before or alongside the 177s registry verify; dispatch by input
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave/.github/workflows/release.yml, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave/scripts/release/verify-package-install.mjs
EVIDENCE: In release.yml the publish uses OIDC. Then 'Verify public package' runs scripts/release/verify-package-install.mjs with 40 attempts and delayMs 15000, taking 177s, and only after that does 'Create GitHub Release' run. The total was 281s. The workflow has no timeout-minutes. Agents also had to work out how to supply the version: workflow_dispatch takes version, version_type and dry_run inputs.
CHANGE: Move Create GitHub Release to run right after publish, or as a parallel job needing only publish. In verify-package-install.mjs, change the fixed 15s delay to backoff (5s, 10s, then 15s) so the typical 150-180s propagation is hit closer to when it lands. Add `timeout-minutes: 30` to the job. Record `gh workflow run release.yml -f version=X` in the manifest. Keep a `## [Unreleased]` section in CHANGELOG.md so release notes need no discovery.
RISK: Low. A Release created before the registry verify could exist briefly for a package not yet installable; mark it as a draft until verify passes if that matters.
VERIFIER: Confirmed: 'Verify public package and clean CLI installation' took 177s (40 attempts at a fixed 15000ms) before Create GitHub Release, and release.yml has no timeout-minutes. Saving is trivial. Agents need registry readiness anyway, so creating the GitHub Release earlier doesn't shorten their wait, and backoff only reaches a roughly 150-170s propagation at most about 10s sooner. release.yml already has concurrency.
IMPL: In specweave/.github/workflows/release.yml, add `timeout-minutes: 30` to the release job. In scripts/release/verify-package-install.mjs, waitForRegistryResponse uses a delay of `min(5000*2**attempt, 15000)`. Record `gh workflow run release.yml -R anton-abyzov/specweave --ref develop -f version=X` in the manifest.

## F21 [scan-gap] real=True safe=False save=None->0 :: Missing timeouts and concurrency, and gates that don't gate, across workflows
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave/.github/workflows/release.yml, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave/.github/workflows/test.yml, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave/.github/workflows/deploy-docs.yml, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/ci.yml
EVIDENCE: - specweave release.yml and test.yml (smoke, unit, e2e) have no timeout-minutes, so a hang runs for the 6h default.
- specweave test.yml e2e has continue-on-error, so e2e failures never block.
- vskill ci.yml has no concurrency, so superseded pushes keep consuming runners, including the 532s Windows cargo job.
- specweave deploy-docs.yml has group pages with cancel-in-progress false, so superseded docs deploys queue serially.
CHANGE: Add timeout-minutes per job, about 2x the p95 (release 30, unit 20, e2e 30, smoke 10). Add `concurrency: {group: ${{ github.workflow }}-${{ github.ref }}, cancel-in-progress: ${{ github.event_name == 'pull_request' }}}` to vskill ci.yml and specweave test.yml. Set deploy-docs cancel-in-progress: true, since only the latest docs build matters. Either make e2e blocking or move it to a scheduled job that reports to the timing scanner (F04). The F04 scan-ci check enforces all of this going forward.
RISK: Low. Timeouts that are too tight cause false reds; base them on F04 history.
VERIFIER: Partly right:
- Confirmed: specweave release.yml, test.yml and deploy-docs.yml have no timeout-minutes, test.yml e2e has continue-on-error: true, and vskill ci.yml has no concurrency.
- Wrong: specweave test.yml ALREADY has `concurrency: test-${{ github.ref }}, cancel-in-progress: true`.
- Wrong and unsafe: deploy-docs.yml `group: pages, cancel-in-progress: false` is GitHub's recommended Pages pattern. A concurrency group keeps only one pending run, so docs deploys do not queue serially, and setting it to true can cancel a Pages deployment mid-flight.
IMPL: Add timeout-minutes to specweave release.yml (release 30) and test.yml (smoke 10, unit 20, e2e 30). Add to vskill/.github/workflows/ci.yml: `concurrency: {group: ci-${{ github.ref }}, cancel-in-progress: ${{ github.event_name == 'pull_request' }}}`. Leave deploy-docs.yml unchanged. Make test.yml e2e blocking only after its pass rate is confirmed from check-runs history.

## F22 [reliability-gap] real=True safe=True save=120->90 :: Permanently red non-blocking checks train agents to ignore red
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave/.github/workflows/claude-code-review.yml, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/e2e-live-nightly.yml, /Users/antonabyzov/Projects/github/specweave-umb/.specweave/release/manifest.json
EVIDENCE: specweave .github/workflows/claude-code-review.yml runs with continue-on-error and fails on every PR (credential or quota). vskill e2e-live-nightly has been red across its last 100 runs; PR #180 today was an attempt at that workflow. Each track agent spent triage turns deciding whether these reds mattered before merging.
CHANGE: Fix the review workflow's secret (check it exists without printing it), or disable the workflow. Fix or disable e2e-live-nightly. Until then, list both in the manifest's known_noise_checks so ci-wait.sh (F03) ignores them deterministically. F04 scan-ci flags any continue-on-error job red in more than 80% of its recent runs.
RISK: Low.
VERIFIER: Confirmed. The claude-review check failed on #2065 (32s) and #2069 (42s), while workflow runs show success because of job-level continue-on-error. vskill E2E Live (nightly) failed 30 of 30 recent runs. After #180 it fails on purpose with a clear message: the VSKILL_PLATFORM_TOKEN secret is missing. Creating that PAT is Anton's job; agents may not create credentials. One point the profiler missed: a Claude review bot posting PR comments conflicts with Anton's absolute no-AI-attribution rule for PR review comments, so disabling it beats rotating its token.
IMPL: Run `gh workflow disable claude-code-review.yml -R anton-abyzov/specweave`, or delete the file in a PR. Keep `gh workflow disable e2e-live-nightly.yml -R anton-abyzov/vskill` until Anton adds VSKILL_PLATFORM_TOKEN. Until then, list 'claude-review' and 'E2E Live (nightly)' under known_noise_checks in the manifest.

## F23 [reliability-gap] real=True safe=False save=None->0 :: DMG notarization check cannot fail
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/desktop-release.yml
EVIDENCE: desktop-release.yml verifies the macOS artifact with `spctl ... || true`, so an unsigned or unnotarized DMG passes the release and is only caught by users or the updater.
CHANGE: Replace it with `spctl -a -vvv -t install <dmg>` and `xcrun stapler validate <dmg>` (and spctl on the .app inside), failing the job on a non-zero exit. Keep `|| true` only for informational output.
RISK: Low. It may surface an existing notarization gap as a red release, which is the point.
VERIFIER: The check can't fail, which is accurate. But making the DMG check fatal as proposed would break every release. Today's log shows `Skill Studio_1.0.65_aarch64.dmg: rejected, source=Unnotarized Developer ID`: tauri notarized only the .app (status Accepted at 14:57:44), and the DMG is signed but never notarized or stapled. `spctl -t install` and `stapler validate` on the DMG would both fail every time.
IMPL: Replace the step in vskill/.github/workflows/desktop-release.yml with:
- `set -euo pipefail`
- `APP=$(ls -d src-tauri/target/${{ matrix.target }}/release/bundle/macos/*.app | head -1)`
- `codesign --verify --deep --strict --verbose=2 "$APP"`
- `spctl -a -t exec -vv "$APP"`
- `xcrun stapler validate "$APP"`
- `codesign --verify --verbose=2 "$DMG"`
Then either add `xcrun notarytool submit "$DMG" --keychain-profile vskill --wait && xcrun stapler staple "$DMG"` (about 40-60s, and before any checksum or upload) and make the DMG spctl fatal, or keep the DMG spctl as `|| echo ::warning::`.

## F24 [discovery-gap] real=True safe=True save=120->120 :: Stale and contradictory release notes in memory and docs
FILES: /Users/antonabyzov/.claude/projects/-Users-antonabyzov-Projects-github-specweave-umb/memory/project_vskill_platform_deploy.md, /Users/antonabyzov/.claude/projects/-Users-antonabyzov-Projects-github-specweave-umb/memory/feedback_git_push_deploy.md, /Users/antonabyzov/.claude/projects/-Users-antonabyzov-Projects-github-specweave-umb/memory/project_desktop_release_one_command.md, /Users/antonabyzov/.claude/projects/-Users-antonabyzov-Projects-github-specweave-umb/memory/project_specweave_release_branch_model.md, /Users/antonabyzov/.claude/projects/-Users-antonabyzov-Projects-github-specweave-umb/memory/project_npm_tokens_all_revoked.md, /Users/antonabyzov/Projects/github/specweave-umb/.specweave/docs/internal/delivery/core/release-process.md, /Users/antonabyzov/Projects/github/specweave-umb/.specweave/docs/internal/delivery/core/operations/deployment.md
EVIDENCE: - project_vskill_platform_deploy.md and feedback_git_push_deploy.md prescribe a triple build.
- project_desktop_release_one_command.md is stale and contains literal secret values in a memory file.
- project_specweave_release_branch_model.md still says manual OTP publish, although OIDC trusted publishing is live.
- project_npm_tokens_all_revoked.md says vskill has no CI publish, but npm-release.yml exists.
- .specweave/docs/internal/delivery/core/release-process.md and operations/deployment.md describe an old process.
Agents read these first and then spent turns reconciling them with reality.
CHANGE: Rewrite each memory note to a one-line pointer: 'release procedure: see .specweave/release/manifest.json and scripts/release/release.sh'. Move the literal secrets out of project_desktop_release_one_command.md into the Obsidian credentials folder (per feedback_store_generated_secrets_obsidian.md) and reference the path only. Replace the two docs pages with a short page generated from the manifest.
RISK: Low.
VERIFIER: Confirmed:
- project_desktop_release_one_command.md contains a literal passphrase value (around line 69; verified without printing it).
- project_specweave_release_branch_model.md still says manual OTP publish.
- project_npm_tokens_all_revoked.md says vskill has no CI publish, but npm-release.yml publishes with OIDC.
- project_vskill_platform_deploy.md describes deploy as opennext deploy, stale since 2026-09-02.
Correction: .specweave/docs/internal/delivery/core/operations/deployment.md does not exist. Only release-process.md exists, dated 2026-02-16. These stale notes also leaked into today's orchestrator prompt as the triple-build command.
IMPL: Move the passphrase value into the Obsidian credentials folder, following feedback_store_generated_secrets_obsidian.md, and leave only the path. Rewrite the four memory notes as one-line pointers to .specweave/release/manifest.json and scripts/release/release.sh. The platform pointer must say `npm run db:generate && npm run deploy` (or the F14 package.json change), not bare deploy. Regenerate release-process.md from the manifest.

## F25 [reliability-gap] real=True safe=True save=None->0 :: .gitignore contradicts the committed-memory rule
FILES: /Users/antonabyzov/Projects/github/specweave-umb/.gitignore
EVIDENCE: AGENTS.md says memory in .specweave/memory/ is committed, so every tool and account sees it. The umbrella .gitignore ignores .specweave/memory/ and .specweave/docs/, so release decisions recorded there never reach other sessions or machines.
CHANGE: Remove the .specweave/memory/ ignore (keep ignoring only state or cache paths), or change AGENTS.md if ignoring is intended. Make sure .specweave/release/ (F02) is tracked.
RISK: Low. Check for secret-shaped content in .specweave/memory before un-ignoring it.
VERIFIER: The contradiction is real: .gitignore lines 31 and 35 ignore .specweave/memory/ and .specweave/docs/, while AGENTS.md says memory is committed. Impact on this track is zero, though. The umbrella has no .specweave/memory directory at all, so no release decisions were lost. 17 docs files and .specweave/config.json are force-tracked despite being ignored. .specweave/release/ and .specweave/metrics/ are not ignored.
IMPL: Delete line 31 (.specweave/memory/) from /Users/antonabyzov/Projects/github/specweave-umb/.gitignore. The pre-commit malware and secret scan runs on any later add. Keep .specweave/state/ ignored, since release-run.json is ephemeral there.

## F26 [redundant-work] real=True safe=True save=80->80 :: Replace LLM verify agents with deterministic release.sh verify
FILES: /Users/antonabyzov/Projects/github/specweave-umb/scripts/release/release.sh, /Users/antonabyzov/Projects/github/specweave-umb/.specweave/release/manifest.json
EVIDENCE: Each track's verify stage ran a separate agent (48s and 54s observed) to re-check versions and URLs that are fully specified (npm view, gh release view, a version endpoint, a fleet status query).
CHANGE: `release.sh verify <track>` runs the manifest verify commands and returns JSON pass/fail. The workflow calls it with a plain Bash step and spawns an agent only on failure, for diagnosis.
RISK: Low.
VERIFIER: verify:specweave (48s) and verify:vskill (54s) are right. The profiler missed verify:platform, which ran from 15:56:10 to about 16:17 (about 1300s). Most of that was waiting on main 'unit tests' run 38926914511 for 24e2b23c. Attempt 1 failed at 16:02:54 when publish-db-only.test.ts timed out at 5000ms, and the rerun finished at 16:17:37. A deterministic verify that checks main CI would have waited just as long. Cost goes down, not wall time.
IMPL: `release.sh verify <track>` runs:
- `npm view <pkg> version`
- `gh release view <tag> --json assets`
- `npx wrangler deployments list --json`
- `curl -sI` on the version and health endpoints
- a fleet state.json read
- `gh run list -b main -w 'unit tests' -L1` (report, don't block)
Spawn an agent only when one of these fails.

## F27 [reliability-gap] real=True safe=True save=900->150 :: Serial dependency: studio track started cold and was the critical path
FILES: /Users/antonabyzov/Projects/github/specweave-umb/scripts/release/release.sh, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/scripts/release/release-local.mjs
EVIDENCE: Every track launched at 14:36:12, but studio is the longest: integration, a 1520s suite, a 1445s rerun, two signed builds, mirror and fleet. It also had the most discovery, since it is the only track with no CI. Its preconditions (cherry-pick set, version, env preflight) were not prepared during the 510s audit or the 1090s permission wait, which was idle time on the critical path.
CHANGE: `release.sh status` kicks off non-mutating long poles in the background right away:
- studio preflight
- creating the release worktree from origin/main
- the sharded test run on the candidate tree
The resulting receipts (F09) are then reused by ship. Order tracks by F04 baseline duration and start the longest first.
RISK: Medium. A speculative test run on a tree that later changes is wasted, but F09 receipts make it reusable whenever the tree hash matches.
VERIFIER: Partly right. All tracks already launched together at 14:36:12, so ordering longest-first gains nothing. The studio release tree depended on merging #241, #235 and #237, and both #235 and #237 change apps/server, so a speculative server test run during the audit could not have matched the release tree. With F09 receipts it would have been rerun anyway. This overlaps F06: with no question asked, the idle window disappears. The useful pre-warm is worktree creation and `pnpm install --frozen-lockfile` (39-44s), env preflight and a fleet status read.
IMPL: `release.sh status` kicks off `release-local.mjs preflight --background`: worktree from origin/main, pnpm install, file-existence checks, SDK/Node checks and fleet state reads. It writes results into <release dir>/state.json for ship to reuse. No tests run before the merges are settled.

## MISSED :: Platform agent sat blind in a 600s foreground wait while the bad deploy served all traffic
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/scripts/release/deploy-watch.mjs, /Users/antonabyzov/Projects/github/specweave-umb/scripts/release/ci-wait.sh
EVIDENCE: Deploy f2843c50 was created at 15:19:04. At 15:21:33 the agent blocked for 600s on `until [ -s .../b7cbc2c1d.output ]`, waiting for 8 'queue-health] batch' lines in tail3.log. Meanwhile tail3.log grew to 2,404 lines, with 494 '(error) [worker] unhandled rejection' and 530 'socket has been closed'. Rollback happened only at 15:31:50, so the broken version served 100% of traffic for about 766s.
CHANGE: Every post-deploy wait must exit on error signatures, not only on success counts. Implement the vskill-platform deploy-watch with auto-rollback (F13 corrected) and the umbrella ci-wait.sh `log --fail <regex>` mode (F03). Runbook rule: never foreground-wait on a condition that ignores error output.

## MISSED :: Dependency bump deployed with the incident fix; no CI job runs the Workers runtime against a DB
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/.github/workflows/0826-e2e.yml, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/.github/dependabot.yml
EVIDENCE: Incident fix #129 and the dependabot prod-dependencies group #126 (11 updates, including pg 8.16.3 to 8.23) went out in one deploy at 15:17-15:19, in the middle of the queue-stall incident. #126's green CI dated from 2026-10-13 on an older base and was never re-run. CI can't see Workers plus Hyperdrive driver regressions: unit tests vi.mock @prisma/client, and 0826-e2e.yml runs `npm run build` and Playwright against Node with a postgres:16 service, not workerd. The rework cost about 1,980s: rollback, PR #130, 865s of CI, redeploy.
CHANGE: 1. Orchestrator and runbook: don't merge dependency groups inside incident tracks; deploy them alone through deploy-watch.
2. Add a workerd smoke job to vskill-platform CI: `npm run build:worker`, then `npx wrangler dev --local` with `CLOUDFLARE_HYPERDRIVE_LOCAL_CONNECTION_STRING_HYPERDRIVE=postgresql://vskill@localhost:5432/vskill_test (password: the test postgres service value in 0826-e2e.yml)`, against the same postgres service; curl one DB-backed route and one submission path, and fail on 5xx or 'socket has been closed' in the output.
3. In dependabot.yml, group pg* and @prisma/* separately so they always get this smoke.

## MISSED :: Platform PR CI runs vitest with one worker on a private-repo runner
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/.github/workflows/unit-tests.yml
EVIDENCE: `gh repo view` shows vskill-platform is PRIVATE, so ubuntu-latest is 2 vCPU and vitest defaults to 1 worker. Run 38922647863: Duration 788.04s against per-phase sums (setup 100, environment 214, tests 206, prepare 72, collect 44, transform 18) of about 652s, i.e. effectively serial. That explains the 14-minute unit-tests on every PR and main push.
CHANGE: Quick fix: add `--maxWorkers=2` to the Vitest step in unit-tests.yml (consider `pool: threads`) and measure before sharding (F12). Each PR also pays for a second identical run on push to main after the squash merge. Accept that, or skip the push run when the tree hash equals the PR's tested tree.

## MISSED :: Flaky platform test failed main CI after deploy and forced a 14-minute rerun
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/vitest.config.ts, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill-platform/src/lib/__tests__/publish-db-only.test.ts
EVIDENCE: Main run 38926914511 for 24e2b23c: attempt 1 failed at 16:02:54 after 859s, with 'FAIL src/lib/__tests__/publish-db-only.test.ts > upsert uses hierarchical slug as the unique key: Test timed out in 5000ms'. Attempt 2 passed at 16:17:37. verify:platform spent about 20 minutes in `gh run watch` on it. #130 was already deployed at about 15:50.
CHANGE: Give the DB-flow test suite in vskill-platform a longer timeout (`vi.setConfig({testTimeout: 20000})` in publish-db-only.test.ts, or `testTimeout: 15000` in vitest.config.ts for CI), or add `retry: process.env.CI ? 1 : 0`. Track flaky test files in timing.py.

## MISSED :: Studio test script ran the 22-minute server suite before the 1-minute web suite
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/scripts/release/test-sharded.mjs, /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/docs/studio/releasing.md
EVIDENCE: scratchpad/run-tests.sh runs the packages one after another (contracts, shared, client-runtime, desktop, server, web), then tsc. In t-rel, web.log finished at 11:36:51 local, after server (1312.85s), even though web takes only 58.55s. Web held the real defect (text-destructive contrast). It surfaced about 22 minutes late, after the first signed DMG build (15:14:36), and forced a rebuild at 15:38:50 (228s) plus redoing helpers and plan. In t-int, 163 web failures (the #237 fixture lacked usePrimarySettings) likewise appeared only at 15:10. The agent's first contrast fix (15:13:13) was never re-run against themeContrastClasses.test.ts, an 11s check that would have caught the second bad class.
CHANGE: Release test runner: start the server suite (sharded, F08) in parallel with contracts, shared, client-runtime, desktop and web, plus `vpr typecheck`, so fast suites report in about 1 minute. Runbook rule: after fixing a failing test, re-run that test file before any signed build.

## MISSED :: Fleet update used the wrong request mode, and M4 can't update while it hosts the release
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio/scripts/studio-fleet/update_request.py, /Users/antonabyzov/Projects/github/specweave-umb/.specweave/release/manifest.json
EVIDENCE: At 15:46:54 the agent sent `/tmp/fleet-request.py check` to M1 and M3. Normal mode with quietMinutes 10 left them waiting-for-quiet through a 600s poll that ended at 15:57. After `install 1.0.36` at 15:57:12, both reported serverVersion 1.0.36 within about 16s. M4 then logged 'waiting-for-quiet: Waiting for running tasks, queued messages and open questions to finish (3 running tasks)' until at least 16:07, even after a force request with a 15-minute hold. The running tasks are very likely the orchestration's own sessions on M4's service.
CHANGE: Release procedure: send `install <ver>` (force) to the non-orchestrator hosts and wait about 60s. For the host running the release, write a normal-mode install request and report 'queued' without blocking. Never force-restart the service hosting in-flight release agents. Encode the per-host mode in the manifest and in update_request.py's CLI.

## MISSED :: Workflow-only fix/* pushes run the 8.5-minute Windows cargo job, and its cache is never warm
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/sidecar-smoke.yml
EVIDENCE: sidecar-smoke.yml path-filters pull_request but also has `push: branches: ['fix/**']` with no paths. The push run on fix/e2e-live-platform-token (14:38:16 to 14:47:12) ran 'cargo check + test src-tauri (windows-latest)' for 8m52s on a PR that only touched e2e-live-nightly.yml. Neither workflow runs on main, so rust-cache caches written on PR or fix branches can't be restored by other branches: every PR touching src-tauri builds cold (#181: 8m37s).
CHANGE: In vskill sidecar-smoke.yml, copy the pull_request `paths` list under `push`, add `main` to push branches, and set rust-cache `save-if: ${{ github.ref == 'refs/heads/main' }}`, so PRs restore a main cache (F17 corrected).

## MISSED :: Orchestrator prompts hard-coded stale or slow procedures
FILES: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/release/manifest.json, /Users/antonabyzov/Projects/github/specweave-umb/scripts/release/release.sh
EVIDENCE: The ship-deploy-verify script's prompts told platform to run `npm run db:generate && npm run build && npm run build:worker && npm run deploy` (three Next builds) and to 'poll /api/v1/queue/health a few times over ~10 minutes'. They told studio to do 'release branch + version bump PR, server/web/contracts tests', which forced the redundant second server run, and to 'use the same force/wait approach as 1.0.35' with no commands. They told vskill to 'bump version via a release commit/PR', which produced the 544s #181 round trip even though CI stamps the version from the tag.
CHANGE: Generate track prompts from manifest.json: release, verify and wait commands per repo, plus policy flags. Keep prose in prompts for goals and exceptions only, so fixing a procedure in one place fixes the next run.

## MISSED :: Proposed release status would skip the studio repo
FILES: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/release/manifest.json, /Users/antonabyzov/Projects/github/specweave-umb/.specweave/config.json
EVIDENCE: .specweave/config.json workspace.repos lists only specweave, vskill and vskill-platform. specweave-studio (anton-abyzov/specwithcode-dev plus the public mirror anton-abyzov/specwithcode) is missing, and it was the longest track today (14:36:12 to after 16:08).
CHANGE: List all four products in .specweave/release/manifest.json, including studio's mirror repo and local paths, and have release.sh read only the manifest. Optionally add specweave-studio to workspace.repos too.

## MISSED :: Shipped desktop DMG is unnotarized
FILES: /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/vskill/.github/workflows/desktop-release.yml
EVIDENCE: desktop-release macOS job log, 14:58:29: `Skill Studio_1.0.65_aarch64.dmg: rejected` with `source=Unnotarized Developer ID`. Only 'Skill Studio.app' was notarized (Accepted at 14:57:44). DMG downloads lead in GitHub counts (3 for 1.0.64).
CHANGE: In desktop-release.yml, add `xcrun notarytool submit "$DMG" --keychain-profile vskill --wait && xcrun stapler staple "$DMG"` before the R2/GitHub upload and checksum steps, then make the DMG spctl check fatal (F23 corrected).

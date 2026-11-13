# Verify — 1314-idle-scratch-copies-lose-their-dependency-installs-on-their-own

FAIL · 2026-11-13T19:10:23.508Z · commands from config testing.commands

## Commands

- Working directory: . (config testing.commands)
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
Ran 13 tests in 12.269s

OK
```

- Working directory: . (config testing.commands)
### `python3 -m unittest discover -s tests -p test_handoff_evidence.py` → exit 0 (0s)

```
..............................................
----------------------------------------------------------------------
Ran 46 tests in 0.396s

OK
```

- Working directory: . (config testing.commands)
### `python3 scripts/release/timing.py --self-test` → exit 0 (0s)

```
.................
----------------------------------------------------------------------
Ran 17 tests in 0.133s

OK
recorded
```

- Working directory: repositories/anton-abyzov/specwithcode-dev (config testing.ownerCommands)
### `npm run verify:pr -- --jobs 1 --no-server` → exit 0 (849s)

```

> verify:pr
> bash scripts/studio-verify/pr-gate.sh --jobs 1 --no-server

PR gate: HEAD 773829328c against origin/main (merge base 773829328c); logs in /var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T//studio-pr-gate.gbztEL
Stage 1: 18 jobs, 1 at a time
STAGE 1                                      RESULT     SECS
contrast                                     pass          5
typecheck                                    pass         36
fleet                                        pass        247
apps/chrome-extension                        pass          1
apps/desktop                                 pass         19
apps/marketing                               pass          0
apps/mobile                                  pass         27
apps/web                                     pass        370
infra/relay                                  pass         30
oxlint-plugin-studio                         pass         23
packages/client-runtime                      pass         20
packages/contracts                           pass         10
packages/effect-acp                          pass          5
packages/effect-codex-app-server             pass          1
packages/shared                              pass         18
packages/ssh                                 pass          9
packages/tailscale                           pass          0
scripts                                      pass         27
Stage 2: not run here (--no-server); the server suite runs in jobs of its own
PR gate: stage 1 passed, server passed, 849s
```

- Working directory: repositories/anton-abyzov/specwithcode-dev (config testing.ownerCommands)
### `npm run test:server:sharded -- --shards 6 --out "$(mktemp -d)"` → exit 1 (666s)

```
  src/handoff/handoffIncoming.test.ts > takeover under the source's work grant refuses a takeover whose grant was revoked after the route checked it: AssertionError: expected HandoffRefusal: Minis: git worktree faile… { …(3) } to match object { status: 403, …(2) }
  src/handoff/handoffIncoming.test.ts > takeover and the project's Use worktrees switch off: a folder with uncommitted changes keeps them, and the work gets a worktree: HandoffRefusal: Minis: git worktree failed (128)
  src/handoff/handoffIncoming.test.ts > takeover and the project's Use worktrees switch off: a folder at another commit is left alone: HandoffRefusal: Minis: git worktree failed (128)
  src/handoff/handoffIncoming.test.ts > takeover and the project's Use worktrees switch off: an ignored file in the way is never overwritten: HandoffRefusal: Minis: git worktree failed (128)
  src/handoff/handoffIncoming.test.ts > takeover and the project's Use worktrees switch off: a folder in the middle of a merge is left alone: HandoffRefusal: Minis: git worktree failed (128)
  src/handoff/handoffIncoming.test.ts > takeover and the project's Use worktrees switch off: work for a repository below the project folder keeps its worktree: HandoffRefusal: Minis: git worktree failed (128)
  src/handoff/handoffIncoming.test.ts > takeover and the project's Use worktrees switch on: a clean project folder is not touched: HandoffRefusal: Minis: git worktree failed (128)
  src/project/ProjectStarterSuggestions.test.ts > ProjectStarterSuggestionsService reads an umbrella shaped like specweave-umb, with nested repositories: AssertionError: expected 128 to equal +0
  src/fleet/folderTransfer/portableGit.race.test.ts > Git snapshot while Git keeps changing drops refs, worktrees and ORIG_HEAD that Git deleted after measuring: Error: git worktree add -qb inside /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws4-KlyaEt/vt-Nvqylm/swc-git-race-yJjm91/root/app-wt failed in /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws4-KlyaEt/vt-Nvqylm/swc-git-race-yJjm91/root/app (exit 128): fatal: Use worktrees is 
  src/fleet/folderTransfer/portableGit.race.test.ts > Git snapshot while Git keeps changing survives a repack and prune between measuring and copying: Error: git worktree add -qb inside /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws4-KlyaEt/vt-Nvqylm/swc-git-race-DbhZqa/root/app-wt failed in /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws4-KlyaEt/vt-Nvqylm/swc-git-race-DbhZqa/root/app (exit 128): fatal: Use worktrees is 
  src/fleet/folderTransfer/portableGit.race.test.ts > Git snapshot while Git keeps changing survives a repack that deletes the listed packs while they are copied: Error: git worktree add -qb inside /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws4-KlyaEt/vt-Nvqylm/swc-git-race-ygQp32/root/app-wt failed in /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws4-KlyaEt/vt-Nvqylm/swc-git-race-ygQp32/root/app (exit 128): fatal: Use worktrees is 
  src/fleet/folderTransfer/portableGit.race.test.ts > Git snapshot while Git keeps changing retries a repository whose snapshot keeps failing, then names it: Error: git worktree add -qb inside /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws4-KlyaEt/vt-Nvqylm/swc-git-race-POn431/root/app-wt failed in /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws4-KlyaEt/vt-Nvqylm/swc-git-race-POn431/root/app (exit 128): fatal: Use worktrees is 
  src/fleet/folderTransfer/portableGit.race.test.ts > Git snapshot while Git keeps changing stops promptly when asked during the copy: Error: git worktree add -qb inside /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws4-KlyaEt/vt-Nvqylm/swc-git-race-Kldsam/root/app-wt failed in /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws4-KlyaEt/vt-Nvqylm/swc-git-race-Kldsam/root/app (exit 128): fatal: Use worktrees is 
  src/fleet/folderTransfer/portableGit.race.test.ts > Git snapshot while Git keeps changing stops during the pause before a retry: Error: git worktree add -qb inside /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws4-KlyaEt/vt-Nvqylm/swc-git-race-XVgU9J/root/app-wt failed in /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws4-KlyaEt/vt-Nvqylm/swc-git-race-XVgU9J/root/app (exit 128): fatal: Use worktrees is 
  src/fleet/folderTransfer/portableGit.race.test.ts > Git snapshot while Git keeps changing kills a running Git command when its stop signal fires: Error: git worktree add -qb inside /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws4-KlyaEt/vt-Nvqylm/swc-git-race-xGnAp4/root/app-wt failed in /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws4-KlyaEt/vt-Nvqylm/swc-git-race-xGnAp4/root/app (exit 128): fatal: Use worktrees is 
  src/fleet/folderTransfer/portableGit.race.test.ts > Git snapshot while Git keeps changing copies large packs whole (cloned on macOS) and keeps their permissions: Error: git worktree add -qb inside /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws4-KlyaEt/vt-Nvqylm/swc-git-race-0dp9sZ/root/app-wt failed in /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws4-KlyaEt/vt-Nvqylm/swc-git-race-0dp9sZ/root/app (exit 128): fatal: Use worktrees is 
  src/fleet/folderTransfer/portableGit.race.test.ts > Git snapshot while Git keeps changing reports Git bytes copied: Error: git worktree add -qb inside /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws4-KlyaEt/vt-Nvqylm/swc-git-race-qw4V6D/root/app-wt failed in /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws4-KlyaEt/vt-Nvqylm/swc-git-race-qw4V6D/root/app (exit 128): fatal: Use worktrees is 
  src/fleet/folderTransfer/portableGit.race.test.ts > a repository re-created at a stale worktree path is walked and copied as an ordinary repository: Error: git worktree add -qb inside /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws4-KlyaEt/vt-Nvqylm/swc-git-race-wa618K/root/app-wt failed in /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws4-KlyaEt/vt-Nvqylm/swc-git-race-wa618K/root/app (exit 128): fatal: Use worktrees is 
  src/fleet/folderTransfer/sourceService.test.ts > scan freshness detects added external worktrees and missing registrations: Error: git worktree failed (128)
  src/fleet/repositorySync.test.ts > finds nested repositories, skips linked worktrees, and shares a recent fetch: Error: Command failed: git -c user.name=t -c user.email=t@example.com worktree add --quiet -b side /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-Qan1GI/swc-repo-sync-VdD2cA/linked
  src/fleet/repositorySync.test.ts > lists uncommitted work in a worktree, which a move would leave behind: Error: Command failed: git -c user.name=t -c user.email=t@example.com worktree add --quiet -b worker /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-Qan1GI/swc-repo-sync-u4M8lH/worker
  src/fleet/repositorySync.test.ts > still reads the rest when a worktree's folder is gone: Error: Command failed: git -c user.name=t -c user.email=t@example.com worktree add --quiet -b gone /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-Qan1GI/swc-repo-sync-mV17yK/gone
  src/fleet/repositorySync.test.ts > keeps a clean worktree off the list when the repository has local branches: Error: Command failed: git -c user.name=t -c user.email=t@example.com worktree add --quiet --detach /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-Qan1GI/swc-repo-sync-kpkM2g/tidy
  src/fleet/repositorySync.test.ts > counts a worktree's unpushed branch on its row, not again on the repository's: Error: Command failed: git -c user.name=t -c user.email=t@example.com worktree add --quiet -b worker /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-Qan1GI/swc-repo-sync-n6vq4p/worker
  src/handoff/handoffPlacement.test.ts > reuses a registered checkout across storage changes without touching retained edits: Error: Command failed: git -c user.name=Fixture -c user.email=fixture@example.invalid -C /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-8el6I6/swc-handoff-placement-8ZFtWj/repo worktree add -qb handoff/test /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ
  src/handoff/handoffPlacement.test.ts > rejects ambiguous registered handoff names instead of selecting a checkout: Error: Command failed: git -c user.name=Fixture -c user.email=fixture@example.invalid -C /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-8el6I6/swc-handoff-placement-2LHVap/repo worktree add -qb one /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-8el6I
  src/handoff/handoffPlacement.test.ts > preserves a missing registered checkout as a recovery error: Error: Command failed: git -c user.name=Fixture -c user.email=fixture@example.invalid -C /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-8el6I6/swc-handoff-placement-YTp5dQ/repo worktree add -qb handoff/missing /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owy
  src/fleet/folderTransfer/manifestScope.test.ts > linked worktrees inside the folder skips worktrees of a repository inside the folder and drops their registrations: Error: git worktree add -qb nested /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-zuKwjA/swc-scan-worktrees-JUBWXW/root/b-main/.worktrees/one failed in /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-zuKwjA/swc-scan-worktrees-JUBWXW/root/b-main (exit 
  src/fleet/folderTransfer/manifestScope.test.ts > linked worktrees inside the folder reports clean worktrees as clean and a check that cannot run as unchecked: Error: git worktree add -qb nested /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-zuKwjA/swc-scan-worktrees-8H123Q/root/b-main/.worktrees/one failed in /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-zuKwjA/swc-scan-worktrees-8H123Q/root/b-main (exit 
  src/fleet/folderTransfer/manifestScope.test.ts > linked worktrees inside the folder flags skipped worktrees whose commits are on no branch or mid-rebase as stranded: Error: git worktree add -qb nested /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-zuKwjA/swc-scan-worktrees-oSZ4eg/root/b-main/.worktrees/one failed in /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-zuKwjA/swc-scan-worktrees-oSZ4eg/root/b-main (exit 
  src/fleet/folderTransfer/manifestScope.test.ts > linked worktrees inside the folder gives the stranded check's Git commands one shared deadline: Error: git worktree add -qb nested /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-zuKwjA/swc-scan-worktrees-f09NoH/root/b-main/.worktrees/one failed in /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-zuKwjA/swc-scan-worktrees-f09NoH/root/b-main (exit 
  src/fleet/folderTransfer/manifestScope.test.ts > linked worktrees inside the folder keeps today's handling for a worktree whose main repository is outside the folder: Error: git worktree add -qb nested /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-zuKwjA/swc-scan-worktrees-qnLdY1/root/b-main/.worktrees/one failed in /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-zuKwjA/swc-scan-worktrees-qnLdY1/root/b-main (exit 
  src/fleet/folderTransfer/portableGit.test.ts > portable external linked worktrees copies Git history, both stashes, staged/unstaged work and branch; continues without the main checkout: Error: git worktree add -qb unfinished /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-8w0slS/swc-portable-git-rp47UJ/selected failed in /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-8w0slS/swc-portable-git-rp47UJ/main (exit 128): fatal: Use worktree
  src/fleet/folderTransfer/portableGit.test.ts > portable external linked worktrees inventories excluded worktrees without following their working files: Error: git worktree add -qb unfinished /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-8w0slS/swc-portable-git-wOAK49/selected failed in /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-8w0slS/swc-portable-git-wOAK49/main (exit 128): fatal: Use worktree
  src/fleet/folderTransfer/portableGit.test.ts > portable external linked worktrees keeps sparse-worktree usable after independent copying: Error: git worktree add -qb unfinished /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-8w0slS/swc-portable-git-BV74XY/selected failed in /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-8w0slS/swc-portable-git-BV74XY/main (exit 128): fatal: Use worktree
  src/fleet/folderTransfer/portableGit.test.ts > portable external linked worktrees keeps separate-git-dir usable after independent copying: Error: git worktree add -qb unfinished /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-8w0slS/swc-portable-git-pHMt0y/selected failed in /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-8w0slS/swc-portable-git-pHMt0y/main (exit 128): fatal: Use worktree
  src/fleet/folderTransfer/portableGit.test.ts > portable external linked worktrees refreshes measured external Git state before building the transfer manifest: Error: git worktree add -qb unfinished /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-8w0slS/swc-portable-git-G3YFA5/selected failed in /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-8w0slS/swc-portable-git-G3YFA5/main (exit 128): fatal: Use worktree
  src/fleet/folderTransfer/portableGit.test.ts > portable external linked worktrees skips an internal split-index worktree and keeps its branch coherent (concurrent commits: false): Error: git worktree add -qb unfinished /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-8w0slS/swc-portable-git-QQrVpv/selected failed in /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-8w0slS/swc-portable-git-QQrVpv/main (exit 128): fatal: Use worktree
  src/fleet/folderTransfer/portableGit.test.ts > portable external linked worktrees skips an internal split-index worktree and keeps its branch coherent (concurrent commits: true): Error: git worktree add -qb unfinished /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-8w0slS/swc-portable-git-Z11Pcy/selected failed in /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-8w0slS/swc-portable-git-Z11Pcy/main (exit 128): fatal: Use worktree
  src/fleet/folderTransfer/portableGit.test.ts > portable external linked worktrees refuses active rebase metadata instead of shipping source-machine paths: Error: git worktree add -qb unfinished /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-8w0slS/swc-portable-git-fEucS6/selected failed in /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws5-owyWvQ/vt-8w0slS/swc-portable-git-fEucS6/main (exit 128): fatal: Use worktree
  src/mergedCloneSweep.test.ts > merged clone sweep keeps a clone whose linked worktree holds a commit that is on no remote: Error: Command failed: git -c user.name=Fixture -c user.email=fixture@example.com worktree add --quiet --detach /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws6-A7l80W/vt-dvqJST/clone-sweep-TVPrMp/scratch/2026-11-02-review-10/repo-linked HEAD
  src/mergedCloneSweep.test.ts > merged clone sweep dependency installs of copies that stay leaves a linked worktree, and anything a package manager could not write again: Error: Command failed: git -c user.name=Fixture -c user.email=fixture@example.com worktree add --quiet --detach /private/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws6-A7l80W/vt-dvqJST/clone-sweep-TVPrMp/scratch/2026-11-06-review-32/linked HEAD
  src/git/GitManager.test.ts > GitManager prepares pull request threads in worktree mode on the PR head branch: GitCommandError: Git command failed in GitVcsDriver.createWorktree (/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws6-A7l80W/vt-K4foJ8/studio-git-manager-Een5f4): git worktree add failed: fatal: Use worktrees is off for this project, so this checkout cannot add a worktree. Do not stop for this: 
  src/git/GitManager.test.ts > GitManager launches setup when creating a new PR worktree: GitCommandError: Git command failed in GitVcsDriver.createWorktree (/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws6-A7l80W/vt-K4foJ8/studio-git-manager-UUoGi2): git worktree add failed: fatal: Use worktrees is off for this project, so this checkout cannot add a worktree. Do not stop for this: 
  src/git/GitManager.test.ts > GitManager preserves fork upstream tracking when preparing a worktree PR thread: GitCommandError: Git command failed in GitVcsDriver.createWorktree (/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws6-A7l80W/vt-K4foJ8/studio-git-manager-7cOfcP): git worktree add failed: fatal: Use worktrees is off for this project, so this checkout cannot add a worktree. Do not stop for this: 
  src/git/GitManager.test.ts > GitManager refreshes a reused PR worktree that has no upstream from the pull request ref: GitCommandError: Git command failed in GitVcsDriver.createWorktree (/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws6-A7l80W/vt-K4foJ8/studio-git-manager-0QmS3X): git worktree add failed: fatal: Use worktrees is off for this project, so this checkout cannot add a worktree. Do not stop for this: 
  src/git/GitManager.test.ts > GitManager does not block fork PR worktree prep when the fork head branch collides with root main: GitCommandError: Git command failed in GitVcsDriver.createWorktree (/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws6-A7l80W/vt-K4foJ8/studio-git-manager-QUVbV8): git worktree add failed: fatal: Use worktrees is off for this project, so this checkout cannot add a worktree. Do not stop for this: 
  src/git/GitManager.test.ts > GitManager does not overwrite an existing local main branch when preparing a fork PR worktree: GitCommandError: Git command failed in GitVcsDriver.createWorktree (/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws6-A7l80W/vt-K4foJ8/studio-git-manager-DhVjw0): git worktree add failed: fatal: Use worktrees is off for this project, so this checkout cannot add a worktree. Do not stop for this: 
  src/git/GitManager.test.ts > GitManager does not fail PR worktree prep when setup terminal startup fails: GitCommandError: Git command failed in GitVcsDriver.createWorktree (/var/folders/js/x0hbrvjj2rl7hsgjy5955_r40000gn/T/sws6-A7l80W/vt-K4foJ8/studio-git-manager-DfFSVM): git worktree add failed: fatal: Use worktrees is off for this project, so this checkout cannot add a worktree. Do not stop for this: 
Server shards: shard 1, 2, 3, 4, 5, 6 failed in 665.9s
```

## Acceptance criteria

3/4 met

| AC | Met | Acceptance | Text |
|---|---|---|---|
| AC-01 |   | open | An idle source tree without `.git`, and a kept clone of a registered repository, lose their `node_modules` folders after a day unused, and every other file stays. |
| AC-02 | x (tasks) | met | The installs stay when a thread, agent session, terminal or process uses the copy, when anything outside the installs changed within the day, when the folder is not a package manager's install, and when any of that cannot be read. |
| AC-03 | x (tasks) | met | `specweave-studio clones sweep` lists the installs of each kept copy with the reason, and the released app on the M4 shows the same plan. |
| AC-04 | x (tasks) | met | Agents are told to remove their scratch copy, or its installs, when its pull request merges. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | claude@antons-macbook-m4max | cd ~/.specwithcode/m4/scratch/2026-11-12-scratch-deps-prune… |  |
| T-02 | done | claude@antons-macbook-m4max | grep -q "scratch copy" AGENTS.md && grep -q "Dependency ins… |  |
| T-03 | done | claude@antons-macbook-m4max | specweave-studio clones sweep --base-dir ~/.specwithcode/m4… |  |
| T-04 | claimed | claude@antons-macbook-m4max |  |  |

3/4 done · 0 skipped · 1 claimed · 0 blocked · 0 stale · 0 open

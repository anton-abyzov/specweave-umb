# Campaign cleanup receipt

The two historical unregistered CLI review checkout remnants were archived to `/Volumes/SanDisk APFS/Archive/specwithcode/recent-features-review-20261103/`. No unique source, increment or report content was discarded.

Before archival: read-only scans of project/thread data across root, M4 and dev SQLite databases found no references to either scratch path; process CWD inspection found none. Git listed neither as a worktree. The external volume was verified mounted as APFS.

- `specweave-retired-checkout`: 53,018 entries verified against the pre-move SHA-256/symlink/directory manifest, zero mismatches.
- `specweave-windows-retired-checkout`: 2,107 entries verified, zero mismatches.

The native cross-volume move left three Finder `.DS_Store` metadata files. These were separately moved to the archive's `finder-metadata-after-copy` folder and checksum-verified; only then were the three empty directories removed with nonrecursive rmdir. Both original scratch paths are absent. About 1,238,036,480 allocated bytes (1.24 GB decimal) were retired from internal storage according to the pre-move scan; this is not a measured global free-space delta.

This archival preserves data and does not retry the previously rejected recursive deletion. Jev guard was unavailable (exit4/no key), which the project instructions allow; all other preconditions were checked.

The 1196 review worktree is absent from disk/Git with zero references in three ownership databases. Historical vskill and Windows smoke managed worktrees were removed. The CLI strict-close worktree and umbrella policy-adoption 1224 worktree were subsequently removed after completion, clean-state and ownership/process checks; their owning reports retain the receipts. The strict-close residual payload was moved recoverably to Trash by its owner.

Active product integration/ledger worktrees, Gmail PR1339 and Phase3 stacked PR1341 remain protected while their PRs or work are open. A merged source branch does not authorize deleting a reused checkout that currently hosts another active branch. Cleanup will continue after each campaign checkout is completed/merged, clean, unbound and unused. No open-PR worktree is claimed removed.

Evidence: `retired-checkout-archive-receipt.json`, both `*-archive-manifest.json`, `archive-finder-metadata.py`, and the domain reports. No original source checkout, active owner worktree or unrelated process was removed.


Product follow-through: the completed product review checkout and the subsequent orchestration-coverage checkout were removed after clean-state, binding and process checks. Coverage closure passed321 tests/25 suites at63.20% with the unchanged60% threshold. Private receipts remain on local umbrella branch `codex/november-product-audit-receipts`, latest verified commit7671cd2c4; the public umbrella remote was not used to publish private evidence. Open Gmail1339 and Phase3 stacked1341 worktrees remain retained.

The isolated umbrella verifier-log worktree was removed after [PR #141](https://github.com/anton-abyzov/specweave-umb/pull/141) merged and its merge patch ID matched the reviewed head. The root, M4 and dev ownership databases contained zero references. No process working directory was inside the worktree, and the final worktree was clean. The two isolated SpecWithCode drafts #1347 and #1348 stay available pending owner integration and manual auth acceptance, respectively.

The completed Team Rules Retry CI scratch checkout `review-team-rules-retry-ci` was removed. It was clean and detached at `4e0d5c79c622c46fe55b71743a0093c5fbed4287`. The remote `codex/review-team-rules-retry` still holds that exact commit, and [draft #1336](https://github.com/anton-abyzov/specwithcode-dev/pull/1336) remains held for auth acceptance. Completed CI run 41751821802 passed 19 jobs with one skip. All three ownership databases had zero references and no process was using the checkout. Only regenerable dependencies/hooks and Finder metadata were ignored. The ordinary non-forced Git worktree removal succeeded. Four campaign source worktrees remain for open drafts #1339, #1341, #1347 and #1348.

The isolated Connect-first #1348 checkout was retired on November 4. Before removal it was clean at remote tip `eee098aa96b99a522984b159e07fe2043d0e5d16`, and its complete patch ID matched the squash merge `24a757c9a8d3f771e8ed31006a4af47c3d188d65` on origin/main. All three local project/thread databases had zero path or branch bindings, and no process had files open there. Ordinary `git worktree remove` unregistered the checkout but returned “Directory not empty.” The unregistered residual directory was moved recoverably by same-volume rename to `/Users/antonabyzov/.Trash/connect-first-worker-rollout-merged-1348-20261104-002519`. The original path and Git registration were verified absent. The remote branch, publisher worktrees, and open draft checkouts were preserved.

The isolated Gmail #1339 checkout was removed after the merge and main Checks passed. It was clean at the remote-preserved reviewed head `1962cad03285859037bbc66feb0c5e91043438a3`. All 15 changed blobs matched main's squash merge, and ownership checks found zero path/branch bindings across the three local databases and no open files held by processes. The ordinary non-forced Git worktree removal succeeded. Generated builds and fixtures were regenerable, with independent test and UI evidence retained. The retry scratch checkout had already been removed. The Phase 3 and Ubuntu stacked worktrees and publisher worktrees remain in place.

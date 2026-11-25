<!-- specweave review: reviewer=gpt-6.2-sol model=gpt-6.2-sol family=openai author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=bf2021f9e971e6940da089ff7c971f5c5b1b9a7e head=89c3a889cba265eb0e4ae7b06df0c7eb5792fcf9 at=2026-11-24T18:49:55.247Z -->
# Review: 1469 Folder-copy snapshot capture, round 6
Verdict: fix first
Reviewer context: GPT-6.2-Sol on Codex reviewing Claude Opus 5.5 work in PR #884. Head 89c3a889cba265eb0e4ae7b06df0c7eb5792fcf9, delta a91a90111..89c3a889c.

## [high] apps/server/src/fleet/folderTransfer/sourceCaptureAnchor.ts:90 The link lookup follows symlink parents
The scan sees a real directory `docs` and its link `docs/latest` in the temporary tree. In the restored root, `docs` is itself a symlink to a directory outside the source. If that directory has a `latest` link with the same target text, both lookups follow `docs` and the target comparison passes (sourceSnapshot.ts:335). With only links below `docs`, no regular-file ancestor check runs there. An empty destination gets a real `docs` directory and the nested link (reconcile.ts:654, apply.ts:863). Re-verified by reading. Resolve link parents beneath the pinned root without following symlinks.

## [high] apps/server/src/fleet/folderTransfer/sourceSnapshot.ts:350 A substituted Git classification can skip the secret probe
A scan of the temporary repo can label `settings.json` tracked. If the restored repo has that path untracked and holding a recognized secret, capture opens the correct inode but trusts the tracked class. Tracked files bypass both scan probes and capture eligibility (classify.ts:94, secretContent.ts:176 and :195). The portable Git snapshot refreshes Git metadata while retaining the working-file class (portableGit.ts:851), and a whole copy to an empty destination writes the packed file (reconcile.ts:421 and :645). Re-verified by reading. Bind Git classification as well as the path inventory to the captured tree.

## [medium] apps/server/src/fleet/folderTransfer/sourceSnapshot.ts:334 Cancel waits for the full symlink pass
A link-heavy tree can keep a cancelled build issuing serial lstat/readlink calls until all links have been checked. The pass never calls `input.stop()`, and cancel waits for the build before revoking the grant and cleaning up (sourceService.ts:1668). Re-verified by reading.

The round-five root-level missing or changed link is refused on macOS and Linux. The broader wrong-tree finding remains open above. A file omitted from the scan can also make Mirror move its destination counterpart to backup (reconcile.ts:785). Scan-time mode bits still reach destination chmod (pullWorker.ts:132). No other earlier finding reopened. Windows still skips anchored target checks under D-03, though link-only roots now go through the root identity check.

Static review. Diff whitespace check passed. No tests or builds run. Exact-head PR gates were in progress at readback.

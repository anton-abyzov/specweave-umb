# Ubuntu 22.04 update proof integration

Increment 1189 is held by the owner of SpecWithCode PR #1256 (Anton Abyzov, `fix/linux-update-no-password`, `03845c60f427438eb122b464a19ac18122520971`). Draft #1347 targets that exact branch with one file changed at `ecfe24f5a8db1d46f25eb76c61b7d5e81200532e`. Integration into the owner branch remains with its owner. The isolated worktree stays until the draft closes or merges and a binding check permits removal.

The failed 1.0.178 release proof passed the clean update from 1.0.176. On the first Retry relaunch the journal showed DevTools failing to bind port 9333, before the invalid package was offered or Retry exercised. The process holding the port is unknown. The new app attached to the live service and separately emitted pairing-token errors.

The patch waits for the loopback bind to succeed after the quit and closes the probe before the next launch. Node 22.20 syntax, whitespace, the live-loopback fixture on the exact patch helper, and a normal frozen pnpm install passed. The fixture confirms occupied, released, and available again after the probe closes.

Hosted workflow run 41755689449 uses the exact stacked SHA for its workflow and proof script, with version 1.0.178, dry_run=true, ref pinned to the SHA, and replace=false. Both Ubuntu matrix jobs consume the new Linux x64 artifact from that run. Its version is 1.0.178, but it rebuilds #1256's stack and uses different bytes from the original 1.0.178 release run. The published 1.0.178 release has no desktop .deb or Linux feed, so the standalone published-pair dispatcher cannot test it. The dry run keeps artifacts in GitHub Actions only, with an isolated dry-run concurrency group and no release upload step. No existing publisher or owner run was retried or modified.

Both hosted Ubuntu jobs passed. Ubuntu 22.04 job 126334199449 and Ubuntu 24.04 job 126334199383 each recorded 1.0.176 to 1.0.178 and explicit success of all four phases: update, retry, replaced and signed. The complete job logs are `ubuntu-update-proof-stacked-22.04.log` and `ubuntu-update-proof-stacked-24.04.log`.

The complete dry run finished successfully with all eight jobs green, including the final Check (dry run) job. The private Actions artifact step passed and the upload to both releases was skipped. Full hosted result is retained in `ubuntu-update-proof-stacked-run-41755689449.json`.

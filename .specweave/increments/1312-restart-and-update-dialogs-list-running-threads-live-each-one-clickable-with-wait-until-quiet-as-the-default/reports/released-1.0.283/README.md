# 1312 in the released build (SpecWithCode 1.0.283)

PR 269 merged as `4096042cd1` (squash) and shipped in `v1.0.283` (tag commit `d3cefd6dea`, Release macOS run 43489785102). `request-release.sh --released 4096042cd1` says: released in v1.0.283.

Released bundle: `studio-1.0.283-d3cefd6deacb.tar.gz` from the v1.0.283 GitHub release, SHA256SUMS OK. Its `client/assets` hold "Wait until quiet", "All quiet", "updates when quiet" and "It updates once nothing running there would be cut off"; `ServerUpdateAction` source map holds `serverReachedVersion` (review fix).

Headless fixture at the release commit (`apps/web/tests/restart-work-list/verify.mjs`): 7 of 7 checks pass, screenshots and `receipt.json` here. Unit tests at the release commit (ServerUpdateAction, sidebar, confirmDialog, design token guard): 46 files, 902 tests passed.

Review: round 1 (claude-sonnet-5-5) FIX: the remote Wait until quiet could reinstall or downgrade a machine that had updated itself; fixed in `3ba2eae0d3` (version check before installing, first look before the 15 s sleep, two-way lists focus Later). Round 2 SHIP.

Proof limit: the dialog was not opened in the installed desktop app, which needs a pending update on a busy machine; the fixture renders the released components.

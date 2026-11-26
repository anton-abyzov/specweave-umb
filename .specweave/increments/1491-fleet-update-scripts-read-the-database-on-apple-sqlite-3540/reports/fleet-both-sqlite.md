# 1491 Fleet suite on both SQLite builds

Result: both builds pass. All 85 fleet tests ran in the gated checks copy at `af7db1a2b931a8f1b3c8de3f86a77b8e7b618b71` (PR #961 head, squash-merged as `ff75993a52914b7225d9e3e4a6afee905df5b884`), with the server built.

| Python | SQLite | Result | Time |
|---|---|---|---|
| `/usr/bin/python3` 3.9.6 | 3.54.0 (Apple, macOS 27) | 85 run, 0 failed | 280 s |
| uv CPython 3.12 | 3.53.1 (stock) | 85 run, 0 failed | 194 s |

Skipped acceptance proofs, as in every run of `run-tests.sh`: `test-installed-startup.mjs` and `test-startup.mjs`.

## Runs

1. `f339b57c`: 3.53.1 passed 85/85. 3.54.0 failed `test-protected-tables-after-restart.py` and `test-rehearse-update.py`, both on the tests' own plain `mode=ro` open of a stopped database. Fixed in `9f6e8029` by reading through `live_database.connect`.
2. `9f6e8029`: both builds 85/85. Review round 1 replaced the immutable fallback.
3. `24a12ad6`: both builds 85/85. Review round 2 added the empty-index recheck.
4. `af7db1a2`: both builds 85/85 (this report).

## Evidence

- Final run: `/Users/anton/.specwithcode/m4/scratch/2026-11-26-1491/fleet-run.log`, `/Users/anton/.specwithcode/m4/scratch/2026-11-26-1491/fleet-3.54.0.log`, `/Users/anton/.specwithcode/m4/scratch/2026-11-26-1491/fleet-3.53.1.log`, per-test logs in `/Users/anton/.specwithcode/m4/scratch/2026-11-26-1491/fleet-3.54.0/` and `/Users/anton/.specwithcode/m4/scratch/2026-11-26-1491/fleet-3.53.1/`
- Earlier runs: `/Users/anton/.specwithcode/m4/scratch/2026-11-26-1491/run1/`, `/Users/anton/.specwithcode/m4/scratch/2026-11-26-1491/run2/`, `/Users/anton/.specwithcode/m4/scratch/2026-11-26-1491/run3/`
- Gated script: `/Users/anton/.specwithcode/m4/scratch/2026-11-26-1491/fleet-inner.sh`, run with `specwithcode checks run -- bash fleet-inner.sh`
- PR CI on `af7db1a2`: 28 checks green (`scripts/release/ci-wait.sh`)

## Release

- Released in v1.0.445 (`request-release.sh --released ff75993a52914b7225d9e3e4a6afee905df5b884`), run https://github.com/anton-abyzov/specwithcode/actions/runs/45861125907.
- The shipped `live_database.py` matches the merge commit (sha256 `3a7ae455dc32304645831be2c5bcdbf96cdf5f98e6713950e6a72191ad8c8597`) in both copies: `studio-1.0.445-deployment-helpers-ae13e9d82959.tar.gz` (`scripts/studio-fleet/`) and `SpecWithCode-1.0.445-arm64.zip` (`Contents/Resources/studio-updater/`). Both assets passed `SHA256SUMS`.
- The installed app on M5 is still 1.0.444 and updates at its next quiet moment; nothing was forced.

# 1492 Fleet suite on both SQLite builds

Result: both builds pass. All 85 fleet tests ran in the gated checks copy at `3b79c63913f3f098c70525a1e58823a38b52fe7e` (PR #963 head, squash-merged as `5ddc104e8bf07eefcb677cf2005aadf1d3c65850`), with the server built.

| Python | SQLite | Result | Time |
|---|---|---|---|
| `/usr/bin/python3` 3.9.6 | 3.54.0 (Apple, macOS 27) | 85 run, 0 failed | 341 s |
| uv CPython 3.12 | 3.53.1 (stock) | 85 run, 0 failed | 232 s |

The new tests (`test_a_stopped_service_grant_is_read_on_any_sqlite`, `test_a_stopped_service_grant_stays_authoritative`, `ProtectedRead`) fail on main `733992c8f` under `/usr/bin/python3` with "unable to open database file", and pass on both builds with the fix.

PR CI on `3b79c639`: 26 checks green.

Evidence: `/Users/anton/.specwithcode/m4/scratch/2026-11-26-1492/fleet-run.log`, `/Users/anton/.specwithcode/m4/scratch/2026-11-26-1492/fleet-3.54.0.log`, `/Users/anton/.specwithcode/m4/scratch/2026-11-26-1492/fleet-3.53.1.log`, per-test logs in `/Users/anton/.specwithcode/m4/scratch/2026-11-26-1492/fleet-3.54.0/` and `/Users/anton/.specwithcode/m4/scratch/2026-11-26-1492/fleet-3.53.1/`.

## Release

- Released in v1.0.446 (`request-release.sh --released 5ddc104e8bf07eefcb677cf2005aadf1d3c65850`), run https://github.com/anton-abyzov/specwithcode/actions/runs/45891463592.
- `managed_updates.py` (sha256 `d626e77f…a036`), `rehearse_update.py` (`e7ae2847…95c5`) and `live_database.py` (`3a7ae455…8597`) in `studio-1.0.446-deployment-helpers-3d999838d374.tar.gz` match the merge commit byte for byte; the asset passed `SHA256SUMS`. The app bundle `SpecWithCode-1.0.446-arm64.zip` (`SHA256SUMS` OK) carries the same `managed_updates.py` and `live_database.py` in `Contents/Resources/studio-updater/`.

# Closure evidence for 1481

November 26, 2026, on M5. `specweave verify` stays red in this umbrella worktree for environment reasons: there is no PyYAML, and the app checkout has no installed dependencies. Its `--cmd` overrides were ignored, so it reran the config commands there. The same commands were therefore run by hand. The app's owner commands ran through the heavy-check gate, in the checks copy at merge commit `c283af4dae076d81d8e156712b1b68f06c670146`.

| Command | Result |
|---|---|
| `python3 scripts/fleet-project-sync.py --self-test` | pass, 13 tests |
| `python3 -m unittest discover -s tests -p test_handoff_evidence.py` | pass, 46 tests |
| `python3 scripts/release/timing.py --self-test` (scratch venv with PyYAML 6.0.3) | pass |
| `npm run test:server:sharded -- --shards 6` | pass, 6 shards in 641 s |
| `npm run verify:pr -- --jobs 1 --no-server` | 16 of 18 jobs pass; `scripts` and `fleet` failed (see below) |
| `scripts` job rerun with `ELECTRON_RUN_AS_NODE` unset | pass, 712 tests (the first failure came from that variable leaking from the agent shell) |
| `fleet` job | 79 of 85 pass |

These 6 fleet tests fail with `sqlite3.OperationalError: unable to open database file` or `interrupted`:

- `test-page-continuity.py`
- `test-preflight-disk.py`
- `test-protected-tables-after-restart.py`
- `test-rehearse-update.py`
- `test-room-before-stop.py`
- `test-update-admission.py`

They fail in the same way on the pre-PR base `8dea0b33947728d756497b46285eadee97ea23b3` in the same shell, so they come from the sandboxed agent shell, not from this change. The squash commit touches no file under `scripts/`. PR #929 CI was green on head `76401dac` with 28 checks.

Logs (scratch, outside the repository): `/Users/anton/.specwithcode/m4/scratch/2026-11-25-1481/close-app.log`, `close-rerun.log`, `close-base.log`, `close-timing.log`.

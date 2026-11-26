# Review: 1491 close
Verdict: ship
Reviewed commit: ff75993a52914b7225d9e3e4a6afee905df5b884
Reviewer context: fresh GPT-6-Sol session on Codex reviewing Claude Opus 5.5 work.

## [low] `.specweave/increments/1491-fleet-update-scripts-read-the-database-on-apple-sqlite-3540/spec.md:31` omits the initialized-index branch

The Approach says the fallback opens plain `mode=ro` after creating side files. If a service initializes the new `-shm` before the reader opens, `scripts/studio-fleet/live_database.py:106-107` instead uses `mode=ro&readonly_shm=1`. Fix: describe the empty-index recheck and conditional URI in the Approach. This is documentation drift only; the implementation and test at `scripts/studio-fleet/test-live-database.py:220-232` cover the safe branch.

AC-01: `scripts/studio-fleet/live_database.py:97-107` implements the specified failure-gated fallback: check for missing side files and a holder lock, create empty `-shm` and `-wal` exclusively, recheck whether the index is still empty, then open plain `mode=ro` when this reader owns the empty index. `_open` forces the schema read and sets `query_only`. `scripts/studio-fleet/test-live-database.py:155-249` covers the stopped database, rejected writes, WAL reader locks across a starting service and checkpoint, a second reader, an initialized index, and refusal when a holder has lost both side files. The spec's Rejected options, Risk and Decisions match the shipped behavior; no immutable open shipped.

AC-02: `reports/fleet-both-sqlite.md` records the gated fleet suite at 85/85 on Apple SQLite 3.54.0 and 85/85 on stock SQLite 3.53.1, with the server built. `reports/verify.md` and `reports/verify.json` record strict verify passing at the merged commit. In this review, `/usr/bin/python3 -B test-live-database.py` and the stock Python 3.12 equivalent each passed 12 tests. Both emitted unclosed test fixture stream `ResourceWarning`s but no test failures.

The checkout is at round 3 head `af7db1a2b931a8f1b3c8de3f86a77b8e7b618b71`. Its complete tree and the reviewed squash merge's tree are identical (`d7b17441b49be6baae21c0855e765030feb5aa5c`). The unrestricted diff from `cc2eae1b2` to the merge changes only T-01's nine listed files, so no new merged code sits outside `reports/review-gpt-6-sol-round-3.md`'s review scope.

Advisor edge cases checked: filesystem failures in the fallback can escape as `OSError` despite `connect`'s docstring, but they still fail the read rather than return stale data; no caller-only `sqlite3.Error` recovery was established. If another process creates `-wal` after this reader creates `-shm`, the retry may use `readonly_shm=1` on an empty index and fail until the process initializes it. This is a transient refusal, with no demonstrated corruption or acceptance failure. The size-check-to-open race remains the documented lost-lock risk. These do not block close.

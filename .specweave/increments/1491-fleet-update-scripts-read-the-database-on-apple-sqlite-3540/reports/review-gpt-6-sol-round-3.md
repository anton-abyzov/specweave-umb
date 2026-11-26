# Review: 1491 Fleet database reader, round 3
Verdict: ship
Reviewed commit: af7db1a2b931a8f1b3c8de3f86a77b8e7b618b71
Reviewer context: GPT-6-Sol on Codex, read-only adversarial review of Claude Opus 5.5 work.

No findings. The new index-size check at `scripts/studio-fleet/live_database.py:106` avoids a plain read-only open after another process has initialized the shared index. A second reader uses `readonly_shm=1`, and the first reader holds WAL locks while a writer starts. The remaining stat-to-open race requires a service to initialize and lose its locks between those operations; the same race exists in the previously shipped plain `mode=ro` path when no index exists.

Focused verification: `/usr/bin/python3 -B test-live-database.py` passed 12 tests on SQLite 3.54.0; stock-SQLite Python 3.12 passed the same 12 tests. No whole suite was run in this review.

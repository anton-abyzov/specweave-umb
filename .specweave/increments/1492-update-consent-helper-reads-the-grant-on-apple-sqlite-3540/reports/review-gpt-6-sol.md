# Review: 1492
Verdict: ship
Reviewed commit: 3b79c63913f3f098c70525a1e58823a38b52fe7e
Reviewer context: fresh GPT-6-Sol session on Codex; base `733992c8f`.

## Findings

None.

## Evidence

- `managed_updates.py:100-112` still selects the same `auth_sessions` row by session ID and enforces the same subject, revocation, issue time, expiry, and scopes. `live_database.connect` also sets `query_only=ON`. `managed_updates.py:385-390` maps its `RuntimeError`, `OSError`, and SQLite failures to `unavailable`, so a failed read cannot grant access.
- `installation_descriptor.py:103-115` rejects root and a different effective user. `managedUpdateInstallations.ts:457-468` invokes the helper as the desktop's current user. A stopped database's new side files therefore have the service owner's UID.
- `studio-service-updater.ts:3-20`, `update_request.py:417-420`, `update_agent.py:1398-1413`, and `build-desktop-artifact.ts:4092-4100` include and install `live_database.py` beside `managed_updates.py`. `managedUpdateInstallations.ts:403-419` rejects a helper directory missing any listed sibling, including an older installed updater.
- `rehearse_update.py:279-293` opens the moved clone with a writer before `protected` runs at line 339. Any side files `protected` creates in that private clone belong to that clone and are used by the candidate's normal WAL flow; the before and after reads retain the same table digest logic at lines 115-128.
- `/usr/bin/python3` reports SQLite 3.54.0. `/usr/bin/python3 -B test-managed-updates.py` passed 33 tests; `/usr/bin/python3 -B test-rehearse-update.py ProtectedRead` passed 1 test. The same commands on the stock uv Python 3.12 build, SQLite 3.53.1, also passed 33 and 1 tests. The broader fleet-suite evidence for AC-03 was not present in this review worktree.

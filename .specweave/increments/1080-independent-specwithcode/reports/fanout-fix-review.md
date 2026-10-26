# Fan-out delivery gate fixture review

Verdict: SHIP · fresh-context reviewer · no findings.

Reviewed the uncommitted change to `repositories/anton-abyzov/specweave-studio/apps/server/src/mcp/OrchestratorMcpToolkit.integration.test.ts`. Only two existing statements move: assigning the second delivery gate now immediately precedes dispatch two (line 3949), and deleting the gate now immediately precedes dispatch three (line 3980). Each delivery retains its gate until its completion has been observed.

The adapter publishes running before looking up the mutable gate (lines 282–305); the test's running projection wait (line 3902) does not establish that lookup occurred. Previously the first delivery could select the second gate, while the test waited for first completion before reaching second-gate release. This explains the reproduced stuck first delivery.

Verification commands: `git diff -- apps/server/src/mcp/OrchestratorMcpToolkit.integration.test.ts`, `git diff --check`, and a Python comparison of `git show HEAD:<file>` against the working file. The comparison confirmed identical line multisets and 4396 lines before/after; removing the two moved statements produces byte-identical text. All assertions, deadlines, and other statements remain unchanged. The complete adapter `startTurn` section is identical to HEAD, proving the temporary diagnostic delay is absent.

Read the owner's adjacent logs (no duplicate suite run):

- `fanout-baseline.log`: normal original fixture, 2/2 pass, 11.51s.
- `fanout-forced-red.log`: owner reports a temporary five-second delay before first delivery gate lookup; original ordering fails, 41.79s. Recorded projection exactly shows children 0–6 interrupted, 7–11 running; first delivery running, tasks 0–1 claimed and 2–6 pending.
- `fanout-forced-green.log`: same owner-reported delay with moved statements, 2/2 pass, 17.57s.
- `fanout-fixed.log`: diagnostic removed, normal complete file 2/2 pass, 11.65s.

Independent bounded Effect/Deferred probe also forced preemption before lookup: original ordering selected unresolved second gate; corrected ordering selected already-completed first gate. This supports the integration reproduction without adding assertions or changing deadlines. Windows CI acceptance remains a separate pending check.

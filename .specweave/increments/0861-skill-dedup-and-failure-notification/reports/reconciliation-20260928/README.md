# 0861 production migration reconciliation

Read-only transaction at 2026-09-28T07:02:14Z confirms phaseA, phaseB and registry-alias migrations finished 2026-05-31. `submission_source_natural_key` exists, unique and valid; zero stored duplicate groups. 447,060 submissions; 428,259 fully keyed; 13,898 active unkeyed; 15,112 aliases. The cutover is already applied and should not be rerun.

This does not establish complete natural-identity coverage: 13,898 active unkeyed rows remain. Local migration/dedup/queue verification passed 294 tests with 1 DB-fixture skip; see 0874 recovery receipts. No migration, repair, data write or deployment occurred. The historical 0861 task markers remain stale; the whole increment has not been closed.

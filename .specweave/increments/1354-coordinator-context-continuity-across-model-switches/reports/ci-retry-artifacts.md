# CI retry artifact provenance

Reviewed head: `23657666cdd2c3dcf37722784e08fd36e847edfb`. Run: `44033331395`.

The retry passed all mandatory component jobs. Server 1/3 retry job `133874644360` passed 4,530 tests (1,801 + 2,729), with zero failed tests. Final gate job `133877266300` nevertheless failed because download-artifact selected obsolete artifact `14306417742`, named pr-gate-server-1, instead of successful retry artifact `14306048935` with the same name. Downloaded IDs are in `/srv/specwithcode/minisforum/evidence/1354-context-continuity/ci-final-gate.log`; successful upload and shard table are in `/srv/specwithcode/minisforum/evidence/1354-context-continuity/ci-server-retry.log`.

Both artifacts were downloaded and their shards.json inspected before cleanup. Original failed evidence is preserved in `/srv/specwithcode/minisforum/evidence/1354-context-continuity/server1-attempt1.zip` and `/srv/specwithcode/minisforum/evidence/1354-context-continuity/server1-attempt1.json`. Successful retry evidence is preserved in `/srv/specwithcode/minisforum/evidence/1354-context-continuity/server1-attempt2.zip` and `/srv/specwithcode/minisforum/evidence/1354-context-continuity/server1-attempt2.json`.

Removed only obsolete duplicate artifact 14306417742 through the GitHub API, then requested rerun of the final gate job. No test result was edited, no threshold changed, and no required gate bypassed. Original failed job logs remain on GitHub. Await final required gate success before merge/release.

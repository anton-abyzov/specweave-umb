# Existing hourly sweep observation

Observed October 21, 2026, at 4:00 PM EDT, using a read-only Wrangler tail with no version filter. Worker 0f19d374-3c3d-43ab-9e4e-0facf8dd4172 emitted cron `0 * * * *`, raw scheduledTime `1792612817665`, and outcome `ok`. The sweep reported 500 actual probes, 500 healthy, zero transient results, zero deprecated rows, zero recent skips and no circuit trip. Elapsed sweep time was 24,067 ms.

The bounded observer ran from 3:43:28 to 4:05 PM EDT, captured four scheduled events across Worker replacements, exited zero, and its owned child PID 63793 was confirmed absent. It stored only scheduled-event metadata and allowlisted counters. No cron was manually triggered and no source backfill, acceptance run or configuration change occurred.

Evidence: /Users/antonabyzov/Projects/github/studio-research-notes/disk-audit-2026-10-21-resume/0854-fix/hourly-sweep-current-versions-v2.jsonl

This supplies real hourly execution evidence. It does not prove missing-source deprecation, measured backlog drain, page-to-database latency <=10 seconds, or the absent */10 acceptance receipt. T-018 remains open for its full acceptance scope; zero deprecations cannot satisfy the missing-source/backlog requirement. The previously counted 2,066,558 stale-metrics candidates are not confirmed missing sources.

Verify and close 0854.

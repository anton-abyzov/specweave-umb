# Plan — 0350 Queue Architecture & Performance Overhaul

See detailed plan at: /Users/antonabyzov/.claude/plans/foamy-questing-pearl.md

## Execution Order
1. T-001 + T-002 (together — DB writes + remove blob)
2. T-003 (external scan dispatch fix)
3. T-004 (search repoUrl)
4. T-005 (parallel cron)
5. T-006 (admin routes process.env)
6. T-007 (tests)

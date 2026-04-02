# Implementation Plan: Fix admin installs dashboard

## Overview

Add `machineHash` (static-salt SHA-256 of IP) to `InstallEvent` for cross-day unique machine counting. Update SQL query to use it. Fix default sort.

## Architecture

### Data Model Change

`InstallEvent` gets new nullable column:
```
machineHash String?  /// SHA-256(ip + static salt) — cross-day unique machine ID
```

### Hash Functions

| Function | Salt | Purpose |
|----------|------|---------|
| `hashIp(ip)` | Daily rotating | Daily dedup (existing) |
| `hashMachine(ip)` | Static env var | Cross-day unique counting (new) |

### SQL Change

```sql
-- Before
COUNT(DISTINCT ie."ipHash")::int AS unique_machines
-- After
COUNT(DISTINCT COALESCE(ie."machineHash", ie."ipHash"))::int AS unique_machines
```

## Files to Modify

1. `prisma/schema.prisma` — add field + index
2. `src/lib/install-tracker.ts` — add `hashMachine()`, update `InstallMeta`, update upsert
3. `src/app/api/v1/skills/installs/route.ts` — pass machineHash in meta
4. `src/app/api/v1/skills/[owner]/[repo]/[skill]/installs/route.ts` — pass machineHash in meta
5. `src/app/api/v1/admin/install-stats/route.ts` — COALESCE in SQL
6. `src/app/admin/installs/page.tsx` — default sort = lastInstallAt

## Testing Strategy

- Unit tests for `hashMachine()` function
- Unit tests for install tracker storing machineHash
- Verify admin stats query shape

# Plan — 0349 Persistent Verification Reports

## Architecture

```
Submission Pipeline (unchanged)
    │
    ├─ createSubmission() ──→ KV sub:{id}  (7-day TTL, hot-path)
    │                     ──→ DB Submission  (permanent, best-effort)  ← NEW
    │
    ├─ updateState()      ──→ KV sub:{id} + hist:{id}
    │                     ──→ DB Submission.state + SubmissionStateEvent  ← NEW
    │
    ├─ storeScanResult()  ──→ KV scan:{id}  (7-day TTL, hot-path)
    │                     ──→ DB ScanResult  (permanent, best-effort)  ← NEW
    │
    └─ getSubmissionFull() ─→ KV first (hot-path)
                           ─→ DB fallback if KV expired  ← NEW

New API:
    GET /api/v1/packages/:owner/:repo/:skillName/history
    GET /api/v1/packages/:owner/:repo/:skillName/latest
```

## Execution Order

1. **Schema migration** — Add `dependencyRisk`, `scriptScanSummary`, `commitSha` to ScanResult. Add `@@index([repositoryId, skillName])` to Submission.
2. **createSubmission() dual-write** — DB create alongside KV write.
3. **createSubmissionsBatch() dual-write** — Batch DB create.
4. **updateState() dual-write** — DB state update + SubmissionStateEvent creation.
5. **storeScanResult() dual-write** — DB ScanResult creation.
6. **getSubmissionFull() DB fallback** — Query DB when KV returns null.
7. **Package history endpoint** — New route with paginated queries.
8. **Latest report endpoint** — Shortcut route.

## Files

| File | Change |
|------|--------|
| `prisma/schema.prisma` | Add 3 fields to ScanResult + 1 index on Submission |
| `src/lib/submission-store.ts` | Dual-write + DB fallback (core changes) |
| `src/app/api/v1/packages/[owner]/[repo]/[skillName]/history/route.ts` | New |
| `src/app/api/v1/packages/[owner]/[repo]/[skillName]/latest/route.ts` | New |

## Risk Mitigation

- All DB writes are best-effort with `.catch()` — pipeline latency unaffected
- DB timeout via existing `$extends` interceptor (8s) prevents Neon cold-start hangs
- KV remains authoritative for in-flight submissions; DB is durable backup
- No changes to `process-submission.ts` — we modify only the store layer

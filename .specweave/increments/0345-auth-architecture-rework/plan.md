# 0345 — Auth Architecture Rework Plan

## Implementation Order

1. T-001 (JWT enrichment) — foundation for everything else
2. T-002 (server-auth helper) — depends on T-001's exported `getJwtSecret`
3. T-003 (root layout) — depends on T-002
4. T-004 (AuthProvider) — depends on T-003
5. T-005 (optimize /me) — depends on T-001
6. T-006 (refresh endpoint) — depends on T-001
7. T-007 (blocklist fix) — independent
8. T-008 (auth UI) — depends on T-003/T-004
9. T-009 (tests + build) — final verification

## Key Architectural Decisions

- **No middleware.ts**: JWT_SECRET may not be available via `process.env` in Cloudflare middleware context. Server-side auth in layout achieves the same goal without this risk.
- **Backward compat via optional fields**: Old JWTs without `avatarUrl` still work — `getServerAuth()` returns `null` for missing fields, `/me` falls back to DB, refresh self-heals.
- **Silent refresh only when server says null**: Only triggers when access token is verified as invalid server-side AND a refresh cookie exists.

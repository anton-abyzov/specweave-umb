# Backend Memory

<!-- Project-specific learnings for this skill -->

## Learnings

- **2026-02-24**: Cloudflare Workers: Secrets only available on env handler parameter, not process.env. Always pass env through utility functions—process.env is empty even with nodejs_compat.
- **2026-02-24**: Cloudflare Workers: Module-level I/O object caching (e.g., PrismaClient, database adapters) violates request isolation—cached objects retain I/O context from previous requests, causing 'Cannot perform I/O on behalf of a different request' errors. Create fresh I/O objects per request, not at module scope.
- **2026-02-24**: Cloudflare Workers: getCloudflareContext() calls require `{ async: true }` parameter—without it, context resolution fails intermittently during concurrent requests, causing edge KV paths to silently fail and cascade to slower Postgres fallback

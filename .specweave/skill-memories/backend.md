# Backend Memory

<!-- Project-specific learnings for this skill -->

## Learnings

- **2026-03-24**: Cloudflare Workers: Secrets only available on env handler parameter, not process.env. Always pass env through utility functions—process.env is empty even with nodejs_compat.
- **2026-03-24**: Cloudflare Workers: Module-level I/O object caching (e.g., PrismaClient, database adapters) violates request isolation—cached objects retain I/O context from previous requests, causing 'Cannot perform I/O on behalf of a different request' errors. Create fresh I/O objects per request, not at module scope.
- **2026-03-24**: Cloudflare Workers: getCloudflareContext() calls require `{ async: true }` parameter—without it, context resolution fails intermittently during concurrent requests, causing edge KV paths to silently fail and cascade to slower Postgres fallback
- **2026-03-24**: External API validation functions should fail-closed (return false on timeouts, rate limits, non-404 errors) rather than fail-open, to prevent invalid state from propagating into the database queue
- **2026-03-24**: Cloudflare Workers: Fire-and-forget database operations with silent .catch(() => {}) handlers become invisible in production—log all failures to console.error() even in best-effort async writes to detect outages
- **2026-03-24**: HTTP error retry discrimination: retry on transient errors (5xx, 429, network timeouts), treat permanent errors (404 for file existence checks) as non-retryable to avoid wasted cycles
- **2026-03-24**: Cloudflare Workers + OpenNext: next/link RSC payload requests fail. Architecture: Use <a> tags for forward navigation (full-page load), history.back() for back navigation with document.referrer checks (instant, no server round-trip), router.push() for overlay-based nav only
- **2026-03-24**: Cloudflare Workers with cost constraints: prioritize Gemini 2.0 Flash (free tier) → Claude (if ANTHROPIC_API_KEY set) → Ollama/self-hosted (if 8GB+ available) → Workers AI (emergency). Implement via `createAiRouter(env)` adapter pattern to avoid provider lock-in. Gemini free tier: 15 RPM limit, 1M tokens/day—sufficient for typical workloads with caching.

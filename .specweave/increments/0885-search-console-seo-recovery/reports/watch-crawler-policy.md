# Watch crawler rendering proof

The deployed watch-crawler-shed worker intentionally returns HTTP 429 with body busy for generic HeadlessChrome and curl user agents. The response includes x-ec-shed: headless and retry-after: 3600 and executes before origin fetch. Waiting does not change this policy.

Authenticated GitOps develop at 081e2ac9, committed 2026-10-07T14:10:35Z, retains identical worker blob 9e93f4cc. SEARCH_BOT permits Googlebot and Google-InspectionTool; robots/sitemap paths bypass shedding. The production Cloudflare worker version 81bb6145-68a4-4218-b78a-3032b4a3dc39 was deployed October 4. No edge policy was altered.

Explicitly headless Chromium using the allowed Google-InspectionTool user agent returned 200 on the exact deployed Watch release, with one complete SportsEvent, self canonical and no overflow at 390px. This is simulated crawler rendering, not actual authenticated Google URL Inspection. Generic automation 429 receipts and raw HTML/search-agent success remain separate evidence.

# Backend Memory

<!-- Project-specific learnings for this skill -->

## Learnings

- **2026-02-23**: Cloudflare Workers: Secrets only available on env handler parameter, not process.env. Always pass env through utility functions—process.env is empty even with nodejs_compat.

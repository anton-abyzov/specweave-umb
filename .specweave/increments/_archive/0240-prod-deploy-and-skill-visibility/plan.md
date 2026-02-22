# Plan — 0240: Production Deploy & Skill Visibility

## Summary

Production shows 15 skills because deployment is manual and the site is running stale code. Fix: deploy now + add CI/CD.

## Execution Order

1. **T-001**: Deploy current code (`npm run deploy`)
2. **T-004**: Verify production shows 89 skills
3. **T-002**: Test KV published skill visibility end-to-end
4. **T-003**: Add GitHub Actions deploy workflow

## Risk

- Cloudflare API token may need to be configured as GitHub secret
- OpenNext build might fail if env vars are missing during build
- KV published skills merge is best-effort (try/catch) so failures are silent

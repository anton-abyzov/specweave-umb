# Lighthouse CI configuration — Track E §8.5

**Owner:** ci-pipeline-agent (this is the spec, not the workflow file).

This document specifies the Lighthouse gate per AC-US21-01..05 + NFR-14.

## Pages to audit

Per spec:

```
https://verified-skill.com/
https://verified-skill.com/desktop
https://verified-skill.com/ai-studio
https://verified-skill.com/skill-studio
https://verified-skill.com/press
```

## Profile

- **Mobile** (per AC-US21-02 — mobile profile is harder than desktop and a deploy-blocker)
- Lighthouse 12+
- Throttling: simulated 4G

## Score thresholds (NFR-14)

All four categories must score ≥ 90 on every page:

| Category | Threshold | Action if below |
|----------|-----------|-----------------|
| Performance | ≥ 90 | block PR / deploy |
| SEO | ≥ 90 | block PR / deploy |
| Accessibility | ≥ 90 | block PR / deploy |
| Best Practices | ≥ 90 | block PR / deploy |

## Workflow file (for ci-pipeline-agent)

`.github/workflows/lighthouse.yml` — referenced by plan §8.5. Should run:
- On every PR that touches `src/app/desktop/**`, `src/app/ai-studio/**`,
  `src/app/skill-studio/**`, `src/app/press/**`, `src/app/layout.tsx`,
  `src/app/sitemap.ts`, `src/app/robots.ts`, or any file in
  `src/app/components/home/`.
- On every push to `main`.
- Daily cron at 04:00 UTC against production for regression detection (AC-US29-04).

## Known caveats

- The 5 marketing pages currently render with placeholder OG SVGs. Once ci-pipeline-agent
  generates real Remotion-rendered PNGs, the SEO score will improve due to the
  og:image link being a 1200×630 PNG (search engines and Lighthouse both prefer raster).
- /desktop has 3 download cards with anchor `<a>` tags pointing to URLs that may not
  exist yet (the actual /desktop/v{N}/... URLs only exist after the desktop-release.yml
  workflow uploads to R2). For Lighthouse audits, this is "broken link" warning, not
  failure. Configure Lighthouse to skip URL existence checks until ci pipeline lands.

## Manual verification (one-time, before first PR)

If the agent who shipped these pages cannot boot the full vskill-platform locally
(it requires Cloudflare Worker bindings + Prisma D1), document a one-time manual
audit run by ci-pipeline-agent or the user:

```
cd repositories/anton-abyzov/vskill-platform
npm run dev   # boots local server on :3000
# In another shell:
npx lighthouse http://localhost:3000/ --form-factor=mobile --output=html
npx lighthouse http://localhost:3000/desktop --form-factor=mobile --output=html
npx lighthouse http://localhost:3000/ai-studio --form-factor=mobile --output=html
npx lighthouse http://localhost:3000/skill-studio --form-factor=mobile --output=html
npx lighthouse http://localhost:3000/press --form-factor=mobile --output=html
```

Document the resulting scores in the PR description before merging.

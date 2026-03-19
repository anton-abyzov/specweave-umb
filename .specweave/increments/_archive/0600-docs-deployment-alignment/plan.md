---
increment: 0600-docs-deployment-alignment
---

# Plan: Fix docs deployment alignment

## Root Cause Analysis

Two separate documentation systems exist but are conflated:
1. **spec-weave.com** — Docusaurus site at `repositories/anton-abyzov/specweave/docs-site/`
2. **verified-skill.com** — vskill platform (Next.js), NOT the docs site

The umbrella CLAUDE.md and living docs reference `verified-skill.com` for docs URLs, causing confusion and 404s.

## Architecture Decisions

- No structural changes — fix references and config only
- Living docs and deployed docs remain separate systems (by design)
- Redirects added via existing `plugin-client-redirects` in docusaurus.config.ts

## Implementation Approach

1. Fix umbrella CLAUDE.md domain reference
2. Bulk replace `verified-skill.com/docs/` → `spec-weave.com/docs/` in living docs (preserve platform refs)
3. Investigate and fix homepage Docusaurus config error
4. Add two redirects to docusaurus.config.ts
5. Audit sidebar entries via `npm run build`
6. Push to deploy

## Key Files

- `CLAUDE.md` (umbrella root)
- `repositories/anton-abyzov/specweave/docs-site/docusaurus.config.ts`
- `repositories/anton-abyzov/specweave/docs-site/sidebars.ts`
- `.specweave/docs/public/**` (living docs bulk replace)

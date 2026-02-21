# 0267: Plan — Skills Docs URL Restructure

## Approach

File move + redirect + link update. Zero content changes.

## Steps

1. Move 6 markdown files from `docs/guides/` to `docs/skills/`
2. Add redirects in `docusaurus.config.ts` for all moved files
3. Update `sidebars.ts` — change all `guides/xxx` references to `skills/xxx`
4. Grep for internal links (`/docs/guides/extensible-skills`, etc.) across all docs and update
5. Run `npm run build` to verify zero broken links
6. Verify existing redirect chain (`programmable-skills` -> `extensible-skills`) still works

## Risks

- **Low**: Broken external links — mitigated by redirects
- **Low**: SEO impact — redirects preserve ranking

## Dependencies

None.

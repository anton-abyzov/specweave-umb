# 0941 verified-skill.com nested pages inherit a parent canonical

## Problem
Bing Webmaster Tools (October 19, 2026) flagged verified-skill.com: "Large number of pages pointing to the same canonical URL". A live crawl of the 6,048 sitemap URLs found every one self-canonical, but routes nested under a layout that calls `publicMetadata()` inherit that layout's canonical, because Next.js merges layout metadata into child pages that set none:

- every `/submit/<submission id>` (thousands, linked from /queue) declares `https://verified-skill.com/submit`
- every `/studio/find/<owner>/<repo>/<skill>` declares `https://verified-skill.com/studio/find`
- `/report/my-reports` declares `/report`, `/settings/integrations` declares `/settings`, `/e2e/studio-mock` declares `/e2e`

Filtered catalog variants (`/skills?category=x` → `/skills`, noindex) and ignored params (`/publishers/x?page=2`) are intentional and stay.

## Scope
In: canonical metadata for the nested routes above, a structural guard against the inheritance, deploy, live HTML readback. Out: new SEO work, sitemap changes, Bing resubmission (owner dashboard step).

## Acceptance Criteria
- [ ] AC-01: `/submit/<id>`, `/studio/find/<owner>/<repo>/<skill>`, `/report/my-reports`, `/settings/integrations` and `/e2e/studio-mock` each render exactly one canonical equal to their own path, and keep `noindex, follow`.
- [ ] AC-02: A unit test fails when any `page.tsx` under `src/app` would inherit a canonical from a layout in an ancestor directory.
- [ ] AC-03: Production serves the fix: the live HTML of two distinct `/submit/<id>` pages and two distinct `/studio/find/...` pages shows distinct self canonicals, while sitemap pages, `/skills?category=testing`, `/?ref=x` and the http/www 308 redirects are unchanged.

## Approach
Each affected nested segment gets its own `layout.tsx` (the pages are client components and cannot export metadata) calling `publicMetadata()` with its own path; dynamic segments use `generateMetadata({ params })`. The server-rendered studio find detail page adds the canonical in its existing `generateMetadata`. `src/lib/__tests__/canonical-inheritance.test.ts` walks `src/app`, finds the nearest canonical-setting file for every page (page or layout in its own directory, else the closest ancestor layout) and fails when that file sits in an ancestor directory. Release with `npm run release` after unit-tests.yml passes on main.

## Decisions
### Defaulted (change any before sw-do)
- D-01 Studio find detail canonical → its own URL, not `/skills/...`; the page is noindex, and a cross-page canonical plus noindex sends mixed signals (reversible).
- D-02 Fix per segment with layouts instead of dropping canonicals from section layouts; the section entry pages are client components that rely on the layout for metadata (reversible).
### Open
- Bing alert clearing depends on Bing recrawling; only the owner can request it in Webmaster Tools.

## Tasks

### T-01 Self canonicals for nested routes
- AC: AC-01, AC-02 | Files: vskill-platform/src/app/submit/[id]/layout.tsx, vskill-platform/src/app/studio/find/[owner]/[repo]/[skill]/page.tsx, vskill-platform/src/app/report/my-reports/layout.tsx, vskill-platform/src/app/settings/integrations/layout.tsx, vskill-platform/src/app/e2e/studio-mock/layout.tsx, vskill-platform/src/lib/__tests__/canonical-inheritance.test.ts | Test: cd repositories/anton-abyzov/vskill-platform && npx vitest run src/lib/__tests__/canonical-inheritance.test.ts src/lib/__tests__/public-seo.test.ts

### T-02 Release and verify live HTML
- AC: AC-03 | Files: none (release) | Test: bash /tmp/vs-canon/live-verify.sh

Verify and close 0941.

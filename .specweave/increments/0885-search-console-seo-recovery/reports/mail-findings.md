# Mailbox and SEO findings — 2026-10-07

Authenticated gws profile and Gmail users.getProfile both identify admin@easychamp.com. All 88 messages matching `in:anywhere from:sc-noreply@google.com` were fetched and decoded with complete pagination. A broader Google/indexing/schema/performance query returned 58 messages, consistent with the sender inventory. Raw MIME/content stays in a private temporary folder; committed inventory keeps only notice metadata and issue names.

## Current notices

- verified-skill.com, October 7: robots exclusions, soft 404, 404, alternate canonical, missing selected canonical; submitted sitemap additionally contains noindex URLs. September 28: no thumbnail URL for video indexing.
- spec-weave.com, October 7: redirect, 404, noindex, alternate canonical and robots exclusions. Submitted sitemap specifically flags alternate canonical and blocked URLs.
- easychamp.com, October 4–6: invalid Video uploadDate/timezone, invalid Event location, and missing Event image. Image validation failed after 48 pages passed; restarted validation reports 2,415 pages. Other Event validations report missing description (2,444), eventStatus/image (2,443), organizer (2,329), location (2,353), startDate (1,279), performer (1,474), address (196), and organizer URL (one). Organizer URL was validated fixed on October 6. These figures are mailbox snapshots, not fresh Search Console totals.

## Search intent evidence

September EasyChamp email reports 596 web clicks / 14.7K impressions: /pro-clubs 187 clicks, homepage 116, /ko 83. Leading queries include easychamp (46), the Korean phrase for football simulation site (29), and pro clubs tracker fc 26 (27). Public metadata and internal links should serve those existing page intents, with localized pages retaining their own canonicals. No invented ranking/traffic guarantees or keyword stuffing.

## Reconciliation

Latest authenticated EasyChamp project context: claude-project-sync 8e5cfe07470d86f9eb9afb7ee5b07ea900bb2583, committed 2026-10-07T12:24:21Z. Active B2B/design checkout owners are preserved. Supported public repos are ec-landing/ec-arena-ui/ec-uikit; deprecated web/webengine/mobile repositories remain untouched.

Current stable SpecWeave installed and registry versions both 3.0.3. Live sitemap audit on spec-weave.com checked all 96 submitted pages: canonical URLs match; /search/ directly conflicts with robots. A transient glossary 503 passed on unchanged repeat. Blog tag exclusions and retained redirect aliases are intentional.

Verified Skills live/source audit confirms missing route canonicals, missing /og/default.png, submitted excluded publishers and redirect URLs, and an indexable unfinished video with unavailable assets. Shared templates and listing data queries need public-only eligibility checks; source and public deployment evidence are separate gates.

EasyChamp latest source already contains Event image/location fixes; three public match samples have complete SportsEvent data and accessible generated images. Three competition samples honestly emit WebPage when date/location are unavailable. Remaining Video date/schema gaps survive through the shared UIKit builder and Help tutorial schema.

Historical sportchamp.ru notices are retained as historical evidence. Removed-page 404s, private noindex routes, correct canonical alternatives and redirects are expected when excluded from submitted sitemaps. Older EasyChamp INP/mobile notices require current measurements before attributing them to today's supported frontend.

Google revalidation is asynchronous. Source tests and public readback can prove released fixes; they cannot prove Google's final index/rich-result decision. Existing gws authorization lacks the Search Console scope, so no claim of authenticated URL Inspection or final validation is made.

## Primary references

- [Google canonical consolidation](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)
- [Google crawl and soft 404 guidance](https://developers.google.com/search/docs/crawling-indexing/troubleshoot-crawling-errors)
- [Google video structured data](https://developers.google.com/search/docs/appearance/structured-data/video)

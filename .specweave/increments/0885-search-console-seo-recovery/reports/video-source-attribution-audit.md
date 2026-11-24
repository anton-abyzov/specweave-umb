# VideoObject publication source audit — 2026-10-07

Every supported VideoObject emitter and date mapping was searched in ec-landing, ec-arena-ui, and ec-uikit, including literal schema types and helper calls.

| Surface | Source | Current behavior |
| --- | --- | --- |
| Landing Help, `src/app/help/structured.ts` | 14 precise publication instants from the corresponding official YouTube player uploadDate fields; ledger display day kept separately | Normalize verified instants to UTC; omit invalid, future, unknown, or day-only timestamps; keep articles and players |
| Landing blog, `src/lib/blog-seo.ts` | Curated EFA film's original YouTube player uploadDate at `https://www.youtube.com/watch?v=v8fTZX6F-ZU`: `2026-09-14T10:55:33-07:00` | Use that verified per-video timestamp; remove fallback to unrelated blog publication date; unknown films remain playable without schema |
| Arena news, `src/lib/news-jsonld.ts` | DTO contains embedded video URLs but only article `date/created/updated` | Emit NewsArticle and preserve players; no VideoObject until actual per-video publication metadata exists |
| Arena fixture facade, `src/lib/broadcast-fixture-video.ts` and `src/app/fixture/[id]/page.tsx` | DTO `createdAt` is the added link-row time, mapped from `created/addedAtUtc`; match kickoff is unrelated | Keep facade, source links, thumbnails, and goal seeks; unknown video publication means no VideoObject or nested Clips |
| Arena player subject, `src/lib/video-subject-jsonld.ts` and `src/app/match/[id]/video/[subject]/page.tsx` | Analysis DTO has no video-publication timestamp | Keep playback and breadcrumb list; do not supply kickoff; omit VideoObject |
| Arena generic `src/lib/seo-jsonld-broadcast.ts` | Caller must supply actual video publication timestamp | Shared strict normalization, rejects date-only/unknown-zone/calendar rollover/future; no implicit date substitution |
| UIKit `src/public-site/videoSchema.ts` | Caller must supply verified video first-publication timestamp | Shared strict DateTime validation; requires real thumbnail/name/provider and timestamp. Comment explicitly rejects article, kickoff, and added-link proxies |

The EFA's former curated `2026-09-14T17:54:52+00:00` differed from its official video publication timestamp and is replaced by the verified source value, normalized to `2026-09-14T17:55:33.000Z`. The existing source association between its content-hash filename and YouTube ID is retained.

Source receipts: `youtube-help-publication-times.json`, `youtube-efa-video-publication.json` in this audit directory. No publication times are inferred from file mtime, server timezone, fixture kickoff, announcement timestamps, or upload-link creation.

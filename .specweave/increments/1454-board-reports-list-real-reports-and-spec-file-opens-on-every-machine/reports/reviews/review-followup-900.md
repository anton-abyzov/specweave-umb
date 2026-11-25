# Follow-up review: PR 900

November 24, 2026. A second review of #847 (Claude Opus 5.5 on M4, four finders with refuters) read an early commit. Its server findings (review grouping, folder cap, copy provenance) had already been fixed by GPT-6.2 Sol rounds 1 to 7. Four viewer findings still applied to main and went into PR 900.

| Finding | Response |
|---|---|
| Arrow keys on a video's controls switched files. | Fixed: keys from a media element are left to it. |
| Videos a browser cannot play showed a dead player. | Fixed: only mp4, m4v, webm, ogv and mov open in the player; others keep the preview card; a failed video says so. |
| An open page or PDF reloads when its signed URL is re-minted. | Not changed. Keeping the first URL let a page outlive its one-hour token (Sol, PR 900 round 1), so the reload stays as before. |
| `Reviews/` listed twice on case-insensitive disks. | No change needed on main: only an exact `reviews` folder is read as reviews, so `Reviews/` is listed once and grouped under Reviews. |

GPT-6.2 Sol, PR 900 round 1 at `e51880932`: fix first (the expiry above, and a video error that survived URL renewal). Round 2 at `cafc0f45e`: Verdict: ship. Merged as `110aa4417` with 27 checks green.

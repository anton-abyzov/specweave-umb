# 0924 live verification (AC-05)

Recorded 2026-10-15T03:35Z by Claude Code. All browser runs headless Chromium (Playwright), against production.

## Merge and deploy
- PR #2053 merged 2026-10-15T00:24:53Z as 8d5194715e704dfbfe24590f9d6f0611e7da1d88.
- deploy-docs.yml run for 8d5194715: success (https://github.com/anton-abyzov/specweave/actions/runs/38659889293). Two later deploy-docs runs on develop also succeeded.

## Live readback (`live-check.mjs`, results in `live/live-check.json`)
| Viewport | Theme | Status | Canonical | Hero "Your agents." | "Same work, two meters" | Horizontal overflow | Page errors |
|---|---|---|---|---|---|---|---|
| 1440 | light | 200 | https://spec-weave.com/code/ | yes | yes | none | 0 |
| 375 | light | 200 | https://spec-weave.com/code/ | yes | yes | none | 0 |
| 1440 | dark | 200 | https://spec-weave.com/code/ | yes | yes | none | 0 |
| 375 | dark | 200 | https://spec-weave.com/code/ | yes | yes | none | 0 |

- `/studio/` returns 200 and lands on `/code/`.
- Screenshots: `live/{light,dark}-{1440,375}-top.png` (first viewport) and `live/{light,dark}-{1440,375}-full.jpg` (full page). Inspected: hero, CTA and cloud qualification, recorded app capture, consistent light and dark theming.

## Scroll stops, reduced motion, no-JS (`~/Projects/github/.cw-runs/l2/tools/shoot.mjs` against production)
- 8 scroll stops (0, 10, 25, 40, 55, 70, 85, 100%) at 1440 and 375, light and dark: `live/stops/*-0NN.jpg`, `live/stops/report.json`; no console or page errors, scrollWidth equals viewport width.
- Reduced motion (stops 0 and 30%): `live/stops/*-reduced.jpg`, `report-reduced.json`; no errors.
- No-JS full page: `live/stops/*-full-nojs.jpg`, `report-nojs.json`; no errors, full content rendered.

## Fresh review findings re-checked live (`live-review-findings.mjs`, `live/review-findings.json`)
The independent review (`~/Projects/research/0924-landing-redesign/review.md`, verdict ship, no critical or high findings) raised two items. Both are resolved in production:
- [medium] Reduced-motion workflow navigation: computed `scroll-behavior` is `auto` under reduced motion, and clicking step 3 jumps instantly (y 0 → 1991 immediately, unchanged at 100 ms and 1.3 s).
- [low] No-JS workflow buttons: the four workflow step buttons are not rendered/visible without JavaScript.
- Observation (not a review finding): without JavaScript the plan-calculator buttons ($20/$100/$200) and video chapter buttons stay visible but inert; their content is still readable.

## Build and SEO
Production build with verify-seo (104 indexable URLs) and the code-landing guard test passed before merge (`~/Projects/github/.cw-runs/l2/`); production canonical readback above confirms `/code/`.

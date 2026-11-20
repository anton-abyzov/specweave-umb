# SpecWithCode icon: prompt-and-lines mark on every platform

## Problem

Anton chose a new SpecWithCode icon on November 15, 2026: a white prompt chevron whose cursor is two solid text lines, on an indigo tile that runs from `#6E7DFF` (top) to `#4A58E8` (bottom). Today every surface still shows the old page-and-prompt mark on a flat `#5B6CFF` tile. The existing export script covers most assets but not the native iOS app, the Chrome extension, the in-app wordmark, the Android activity mark, the docs site or the store avatars, so a master change today leaves old icons behind.

Evidence and inventory: `.specweave/reports/threads/2026-11-15-specwithcode-icon-concepts-1a02cc-d6d0e5.md` in the specweave repository. Chosen masters: `/srv/work/specwithcode-icon-concepts/final/` on linux-mini.

## Scope

In: new vector masters, the tile gradient, every tracked icon asset in the app repository `repositories/anton-abyzov/specwithcode`, the SpecWithCode icon files on the docs site in `repositories/anton-abyzov/specweave`, one command that regenerates all of them, and an avatar pack for stores and social pages.

Out: uploading avatars to GitHub, YouTube, LinkedIn, X, the Chrome Web Store and the App Store (manual, needs Anton's approval per post or listing); a new wordmark typeface; dev and nightly variant artwork beyond swapping the mark.

## Acceptance Criteria

- [ ] AC-01: `assets/brand/specwithcode-mark.svg` and `assets/brand/specwithcode-mark-silhouette.svg` hold the prompt-and-lines mark, and no tracked file outside `assets/brand` still contains the old page path data (`M29 10H60L78 28`).
- [ ] AC-02: One command (`vp run brand:rollout`) regenerates every tracked icon: macOS, Linux and iOS 1024 PNGs, Windows ICOs, favicons, apple-touch icons, web manifest icons, the three Icon Composer projects, Android launcher, splash, monochrome and notification art, `apps/ios` `AppIcon.icon` and `Brand.xcassets` logo, Chrome extension icons at 16, 32, 48 and 128, `StudioWordmark.tsx` on web and mobile, the widget mark and `agent_activity_mark.xml`. Running it twice produces no diff.
- [ ] AC-03: The tile gradient is defined once and the flat `#5B6CFF` tile colour no longer appears as an icon background in `apps/android`, `apps/chrome-extension` or `apps/mobile/app.config.ts`.
- [ ] AC-04: The mark is legible at 16px: the Windows ICO and `favicon-16x16.png` show the chevron and both lines as separate shapes, checked on light and dark backgrounds.
- [ ] AC-05: The macOS and iOS builds show the new icon with Liquid Glass from the Icon Composer project, in Default, Dark and Tinted appearances, checked on the M4 and on an iPhone or simulator.
- [ ] AC-06: The docs site shows the new icon (`docs-site/static/img/studio/specwithcode-icon.png`, `scripts/brand/specwithcode-logo.svg`) and its Open Graph image no longer shows the old mark.
- [ ] AC-07: `dist/brand/avatars/` holds square and round avatars at the sizes GitHub, YouTube, LinkedIn, X, the Chrome Web Store and the App Store need.

## Approach

1. Replace the two masters with the chosen mark (a 1024-unit box, three round-capped strokes: chevron `M288 366L454 512L288 658` at 92, lines `M544 548H756` and `M544 672H692` at 84). The silhouette master equals the mark, because the mark is already one colour.
2. `scripts/export-studio-icons.py`: the mark fills about 55 percent of the tile instead of the page inset; the tile becomes the vertical gradient; `ICON_COMPOSER` layers get the mark as `text.svg` and the gradient as the fill.
3. Extend the export to the uncovered surfaces listed in AC-02 and add the `brand:rollout` script that also runs `icons:export:android`.
4. On the Mac, run `vp run icons:export` (needs Icon Composer `ictool`) for the Liquid Glass renders.
5. Docs site: update `scripts/brand/specwithcode-logo.svg`, rerun `scripts/brand/export-icons.py`, regenerate the Open Graph image.
6. Avatar pack.

Rejected: translucent lines (opacity 0.8 and 0.5). They cannot be shown in one-colour contexts (Android monochrome and notification icons, tinted mode, the tray) and soften the 16px ICO; solid lines render the same everywhere.

Risks: the mark shares the prompt idea with Codex and terminals; the full tile and the two lines keep it apart. The retired-icon guard and the brand audit may flag new files. Installed apps keep the old dock icon until they update.

## Decisions

### Asked
- D-01 Which icon → prompt chevron with two text lines on soft vertical indigo (Anton, November 15, 2026).
- D-02 Heavier translucent lines or solid lines → Anton left it to the safer option; solid lines chosen for the reasons under Rejected.
### Defaulted (change any before sw-do)
- D-03 Dark appearance → same mark on a deeper indigo tile, tuned in Icon Composer (reversible).
- D-04 Dev and nightly variants → keep their backgrounds, swap the mark (reversible).
- D-05 16px drawing → same two lines, no simplified variant, unless AC-04 fails (reversible).
### Open
- none

## Tasks

### T-01 New masters and tile gradient in the export script
- AC: AC-01, AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/assets/brand/specwithcode-mark.svg, repositories/anton-abyzov/specwithcode/assets/brand/specwithcode-mark-silhouette.svg, repositories/anton-abyzov/specwithcode/scripts/export-studio-icons.py, repositories/anton-abyzov/specwithcode/assets/README.md | Test: python3 scripts/export-studio-icons.py && git grep -n "M29 10H60L78 28" -- . ':!assets/brand' ; test $? -eq 1

### T-02 Cover the missing surfaces and add brand:rollout
- AC: AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode/package.json, repositories/anton-abyzov/specwithcode/scripts/export-studio-icons.py, repositories/anton-abyzov/specwithcode/apps/ios/App/AppIcon.icon, repositories/anton-abyzov/specwithcode/apps/chrome-extension/icons, repositories/anton-abyzov/specwithcode/apps/web/src/components/StudioWordmark.tsx, repositories/anton-abyzov/specwithcode/apps/mobile/src/components/StudioWordmark.tsx | Test: vp run brand:rollout && vp run brand:rollout && git diff --exit-code

### T-03 Liquid Glass export on the Mac and device check
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/assets/prod/app-icon.icon, repositories/anton-abyzov/specwithcode/assets/dev/app-icon.icon, repositories/anton-abyzov/specwithcode/assets/nightly/app-icon.icon | Test: vp run icons:export on the M4, then screenshots of the dock and an iPhone home screen in Default, Dark and Tinted

### T-04 Docs site icon and Open Graph image
- AC: AC-06 | Files: repositories/anton-abyzov/specweave/scripts/brand/specwithcode-logo.svg, repositories/anton-abyzov/specweave/docs-site/static/img/studio/specwithcode-icon.png, repositories/anton-abyzov/specweave/docs-site/static/img/studio/og-specwithcode.jpg | Test: python3 scripts/brand/export-icons.py && npm run build --prefix docs-site

### T-05 Avatar pack
- AC: AC-07 | Files: repositories/anton-abyzov/specwithcode/scripts/export-studio-icons.py | Test: vp run brand:rollout && ls dist/brand/avatars

### T-06 Verify and close
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07 | Files: .specweave/increments/1353-specwithcode-icon-prompt-and-lines-mark-on-every-platform/spec.md | Test: specweave verify 1353-specwithcode-icon-prompt-and-lines-mark-on-every-platform

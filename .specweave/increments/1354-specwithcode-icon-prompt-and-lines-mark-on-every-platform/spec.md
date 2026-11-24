# SpecWithCode icon: prompt and lines mark on every platform

## Problem

On November 15, 2026 Anton chose a new SpecWithCode app icon: a white prompt chevron whose cursor is two solid white text lines, on an indigo tile that runs vertically from `#6E7DFF` (top) to `#4A58E8` (bottom). No glow, blur or translucent lines, because one-colour contexts (Android monochrome, iOS tinted, the tray) cannot show opacity levels.

The app repository (anton-abyzov/specwithcode) still ships the page-and-prompt mark on a flat `#5B6CFF` tile. `scripts/export-studio-icons.py` writes most icons, but several consumers are hand-copied and fall out of step on every change: the iOS `AppIcon.icon` and `specwithcode-logo.imageset`, the Chrome extension icons and store promo sources, both `StudioWordmark.tsx` components, the Android notification vector, the DMG backgrounds and the tile colour in Android, the Chrome popup and the Expo config. The docs site in the specweave repository carries its own copy.

The brief was written as increment 1353, but 1353 was already taken by the Linux memory-limit increment and no icon spec existed, so this increment carries it as 1354.

## Scope

In: new masters, every icon and mark in the app repository, the Icon Composer projects (prod, dev, nightly, `apps/ios`), an avatar pack in `dist/brand/avatars/`, one rollout command, the 16px check, and the docs-site brand files in the specweave repository (separate PR to `develop`).

Out: uploading avatars or changing any store or social listing (each needs Anton's approval). Cutting a release. The app's accent colour `#5B6CFF` in UI themes and design-system fixtures (it is the UI accent, not the icon tile).

## Acceptance Criteria

- [x] AC-01: `assets/brand/specwithcode-mark.svg` and `specwithcode-mark-silhouette.svg` hold the chosen mark (1024-unit box, chevron and two lines) as filled paths in solid white, matching the stroke design pixel for pixel at 1024px.
- [x] AC-02: Every tiled icon uses the vertical gradient `#6E7DFF` to `#4A58E8`, and the mark fills about 55 percent of the tile.
- [x] AC-03: The consumers that were hand-copied (iOS `AppIcon.icon` and `specwithcode-logo.imageset`, Chrome extension icons and promo sources, both `StudioWordmark.tsx`, `agent_activity_mark.xml`, DMG backgrounds, the tile colour in Android `colors.xml`, `popup.css` and `app.config.ts`) are written by the rollout, and no tracked file outside history still carries the old mark path `M29 10H60L78 28`.
- [x] AC-04: The four Icon Composer projects carry the mark layer and gradient fill with Default, Dark and Tinted appearances; dev and nightly keep their backgrounds; `ictool` exports all three renditions.
- [x] AC-05: `vp run brand:rollout` regenerates everything above plus `dist/brand/avatars/` (square and round, sizes for GitHub, YouTube, LinkedIn, X, Chrome Web Store and App Store); a second run gives no diff; `assets/README.md` documents it.
- [x] AC-06: At 16px (`favicon-16x16.png` and the 16px Windows ICO frame) the chevron and both lines are separate shapes on light and dark backgrounds, or a simplified 16px drawing with one line is used and reported.
- [x] AC-07: The retired-icon guard and the brand audit pass without widening any allow list.
- [x] AC-08: The docs site (specweave repository) carries the new `scripts/brand/specwithcode-logo.svg`, `export-icons.py`, `docs-site/static/img/studio/specwithcode-icon.png` and `og-specwithcode.jpg` in a PR to `develop`.

## Approach

The masters are the source; `vp run brand:rollout` runs `scripts/export-studio-icons.py` (every PNG, ICO, WebP and SVG, the consumers that used to be hand-copied, the Icon Composer projects and the avatar pack) and then `scripts/export-android-icons.ts` (the Expo Android artwork). The strokes are outlined to filled paths in the masters because Android vector drawables, the notification icon and Icon Composer's tinted mode read fills most reliably. Composer exports with `ictool` give the Dark and Tinted screenshots.

## Decisions

### Asked
- none (brief from Anton, November 15, 2026)
### Defaulted
- D-01 Increment number 1354, because 1353 was already taken.
- D-02 The UI accent `#5B6CFF` stays in themes and design-system fixtures; only icon tiles change.

## Tasks

### T-01 New masters and the gradient tile in the export script
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/assets/brand, repositories/anton-abyzov/specwithcode/scripts/export-studio-icons.py | Test: test -s .specweave/increments/1354-specwithcode-icon-prompt-and-lines-mark-on-every-platform/reports/master-check.md

### T-02 Hand-copied consumers written by the rollout
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode/scripts/export-studio-icons.py, repositories/anton-abyzov/specwithcode/scripts/export-android-icons.ts, repositories/anton-abyzov/specwithcode/apps | Test: test -s .specweave/increments/1354-specwithcode-icon-prompt-and-lines-mark-on-every-platform/reports/rollout.md

### T-03 Icon Composer projects with Default, Dark and Tinted
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode/assets, repositories/anton-abyzov/specwithcode/apps/ios/App/AppIcon.icon | Test: test -s .specweave/increments/1354-specwithcode-icon-prompt-and-lines-mark-on-every-platform/reports/appearances.md

### T-04 One command, avatar pack, idempotence, README
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/package.json, repositories/anton-abyzov/specwithcode/assets/README.md | Test: test -s .specweave/increments/1354-specwithcode-icon-prompt-and-lines-mark-on-every-platform/reports/rollout.md

### T-05 16px check
- AC: AC-06 | Files: .specweave/increments/1354-specwithcode-icon-prompt-and-lines-mark-on-every-platform/reports | Test: test -s .specweave/increments/1354-specwithcode-icon-prompt-and-lines-mark-on-every-platform/reports/16px.md

### T-06 Guards and audits
- AC: AC-07 | Files: repositories/anton-abyzov/specwithcode/scripts/studio-brand-audit.mjs, repositories/anton-abyzov/specwithcode/scripts/studio-toolchain/preservation-audit.mjs | Test: test -s .specweave/increments/1354-specwithcode-icon-prompt-and-lines-mark-on-every-platform/reports/rollout.md

### T-07 Docs site PR
- AC: AC-08 | Files: repositories/anton-abyzov/specweave/scripts/brand, repositories/anton-abyzov/specweave/docs-site/static/img/studio | Test: test -s .specweave/increments/1354-specwithcode-icon-prompt-and-lines-mark-on-every-platform/reports/docs-site.md

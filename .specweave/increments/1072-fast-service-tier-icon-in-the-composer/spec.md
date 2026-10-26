# Fast service tier icon in the composer

## Problem

On October 25, Anton picked Codex's Fast service tier ("2x speed, increased usage"). The composer's reasoning control then read "Medium Fast", showing only the effort bars and the word. Nothing in the control or its menu marks that a faster, costlier tier is on. The screenshot is `/Users/antonabyzov/.specwithcode/m4/userdata/attachments/project-coordinator-1332065e-795b-4f98-91c4-f114917e53f6-493054b5-69e3-4328-aeb6-afafeda6db98.png`.

The app already has a speed glyph: `TraitsSpeedIcon` in `apps/web/src/components/chat/TraitsSpeed.tsx` draws a filled bolt for Fast and a double bolt for Ultrafast. Only the subagent tooltip uses it.

## Scope

In:

- The reasoning control in the composer (wide and narrow).
- The reasoning menu rows, including the composer's "More composer controls" menu.
- Claude's Fast mode on/off rows.

Out:

- Tier, model and billing semantics: the selected value, its saved form and what it costs.
- Settings pages.
- Kie-generated artwork, because an established vector glyph exists.

## Acceptance Criteria

- [ ] AC-01: With Fast (or Ultrafast) selected, the composer's reasoning control shows the bolt (double bolt) beside the effort bars, in place of the word. The bolt is neutral (foreground), never the amber of the fallback mark.
- [ ] AC-02: The control's tooltip and accessible name read "Medium effort · Fast service tier" (Claude: "· Fast mode"). With Standard they read "Medium effort".
- [ ] AC-03: In the reasoning menu, the Fast and Ultrafast rows carry the bolt, and Standard keeps the same text alignment as the effort rows. This holds in the narrow composer's "More composer controls" menu too. Rows are named once, with no duplicate "mode on" text.
- [ ] AC-04: Switching Standard and Fast updates the control and menu, verified headless at 360, 520 and 900 px in light and dark, next to a fallback mark.
- [ ] AC-05: Merged, released, and visible in the installed desktop app.

## Approach

- `TraitsPicker.tsx`: `buildTraitsTriggerParts` returns `speed` and drops the speed word from `details`. `traitsTriggerDescription` builds the tooltip and accessible name. The trigger renders `TraitsSpeedIcon`, and menu rows render it for faster tiers.
- `TraitsSpeed.tsx`: `TraitsSpeedIcon` takes `className` and `announce`.
- Fixture: `apps/web/tests/fallback-composer` `?tier=fast|standard`, and runner `fast-tier.mjs`.

Rejected alternatives:

- A generated raster icon: blurry at 12 to 16 px, and the bolt is the established speed mark.
- An amber bolt: it would read as the fallback mark.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Reuse the lucide bolt (`ZapIcon`) and the existing `UltrafastIcon` instead of Kie generation.
- D-02: Show the bolt in place of the word "Fast" in the control. The words stay in the tooltip and accessible name.
### Open
- none

## Tasks

### T-01 Bolt in the reasoning control and menu
- AC: AC-01, AC-02, AC-03 | Files: apps/web/src/components/chat/TraitsPicker.tsx, apps/web/src/components/chat/TraitsSpeed.tsx, apps/web/src/components/chat/TraitsPicker.test.ts | Test: cd apps/web && vp test run src/components/chat/TraitsPicker.test.ts

### T-02 Headless Standard/Fast matrix
- AC: AC-04 | Files: apps/web/tests/fallback-composer/main.tsx, apps/web/tests/fallback-composer/fast-tier.mjs | Test: node apps/web/tests/fallback-composer/fast-tier.mjs /Users/antonabyzov/.specwithcode/m4/evidence/fast-tier-glyph

### T-03 Merge, release, verify installed
- AC: AC-05 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/fast-tier-glyph | Test: CI green, release published, installed app readback and screenshot

### T-04 Verify and close 1072
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: .specweave/increments/1072-fast-service-tier-icon-in-the-composer | Test: specweave verify and a fresh-context review

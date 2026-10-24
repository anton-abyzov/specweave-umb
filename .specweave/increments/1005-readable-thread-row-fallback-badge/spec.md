# Readable thread row fallback badge

## Problem

On the Threads home ("Welcome back.") a thread running on a usage-limit fallback shows `Codex · GPT-… ( • ● Fallback for Opus 5.5 )`: the model name is cut to "GPT-…", a stray separator dot sits inside the fallback pill, and the pill's border is clipped top and bottom. The machine name on the next row is cut to "MacBo…". Evidence: `/Users/antonabyzov/.specwithcode/m4/userdata/attachments/project-coordinator-1332065e-795b-4f98-91c4-f114917e53f6-1e66f77a-89e5-4964-a26d-f87e93250350.png`.

Cause (specwithcode-dev `apps/web`): `ThreadModelBadge` renders the composer's bordered `ModelStateTag` pill (20px tall, `shrink-0`, up to 176px) inside `.sws-thread-meta`, an 18px, `overflow: hidden` line whose `> * + *::before` rule injects the separator dot as the pill's first flex child. Because the pill never shrinks, the model name (shrink 9999) gives way first.

The composer has the same fault (second report, `/Users/antonabyzov/.specwithcode/m4/userdata/attachments/project-coordinator-1332065e-795b-4f98-91c4-f114917e53f6-943e5a8a-0ce7-4680-a49b-1e2d805f9c95.png`): the "Continuing on Codex · GPT-6.1-Sol" banner and an amber "Fallback for Opus 5.5" pill say the same fact twice, and the pill wins the toolbar while the model chip is crushed to "C…". The pill sits outside what the resting-controls measurement counts.

## Scope

In: one fallback language for every surface that names a thread's model: worker composer (ChatComposer, ProviderModelPicker and its menu), the limit pairing banner, the coordinator composer (CoordinatorModelPicker, CoordinatorAccessPicker), thread rows (ThreadsPane), the thread header chip and overview rows (StudioOverview); light and dark; 360/520/900 px. Out: iOS (its rows show no fallback tag), the usage-limit recovery card (a stopped thread, not a fallback). Design: `/Users/antonabyzov/.specwithcode/m4/evidence/thread-row-fallback-badge/design/final-spec.md` (winner of four judged proposals).

## Acceptance Criteria

- [ ] AC-01: In a thread row, the fallback indicator renders as an inline glyph (no pill border, no separator dot inside it; glyph only since 1025), its full meaning stays in a tooltip and accessible name, and the model name is never truncated while the machine name or fallback label can still give way.
- [ ] AC-02: Below a narrow row width the fallback collapses to its icon alone; the provider mark, model, plan, PR and machine chips never overlap at 360px, 520px and 900px pane widths in light and dark themes.
- [ ] AC-03: The thread header and overview rows use the same suffix inside the model unit; the header chip is focusable and shows the tooltip.
- [ ] AC-04: In the worker and coordinator composers the fallback is a suffix inside the model trigger (the amber detour glyph alone since 1025; words in its tooltip and accessible name), the model name never collapses below 7 characters before effort/access labels and the usage number give way, and nothing in the toolbar overlaps at 360/520/900 px.
- [ ] AC-05: Each fact is said once: the "Continuing on" banner is gone; a one-line banner appears only when switching back is possible ("Opus 5.5 has room again." + Switch back); the picker menu opens with a status header that explains the fallback and offers the way back.
- [ ] AC-06: Fix merged to main, released, and the installed desktop app shows the readable row and composer.

## Approach

Superseded by the design spec named in Scope: `ModelStateTag` becomes the suffix (glyph, full, short, sr-only) and `ModelStateTip` the shared three-line tooltip; hosts place it inside the model unit and choose width tiers. Original row-only approach, kept for history:

`ModelStateTag` gains `variant: "pill" | "inline"`; inline renders `.sws-model-state` (icon + `.sws-model-state-label`) styled in `shell.css`. `ThreadModelBadge` takes `stateVariant` (default inline); `ProjectThreadHeader` passes `pill`. In `.sws-thread-meta` the state shrinks after the machine (shrink 100 vs 1000, min width keeps the icon) and before the model; `.sws-thread-text` becomes an inline-size container so a container query hides the label under 460px. Rejected: wrapping the meta line to two rows (the CSS contract keeps rows one height); dropping the tag (loses the fallback fact).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Icon-plus-text suffix inside the model unit, icon-only when narrow, tooltip carries the pick and reason; chosen by a four-proposal, three-judge design panel (one-surface won).
- D-02 Keep the banner only when switching back is possible (judges rejected deleting it outright).
### Open
- none

## Tasks

### T-01 Inline fallback state in thread rows
- AC: AC-01, AC-02, AC-03 | Files: apps/web/src/components/chat/ModelStateTag.tsx, apps/web/src/components/studio/shell/ModelBadge.tsx, apps/web/src/components/studio/shell/ProjectThreadHeader.tsx, apps/web/src/components/studio/shell/shell.css, apps/web/src/components/chat/ModelStateTag.test.tsx, apps/web/src/components/studio/shell/Tip.tsx, apps/web/src/components/studio/shell/ThreadsPane.tsx, apps/web/src/components/studio/shell/StudioSidebar.tsx, apps/web/src/components/studio/StudioOverview.tsx, apps/web/src/components/studio/shell/panes.css, apps/web/src/components/studio/PlanProgressChip.tsx, apps/web/src/components/studio/shell/ModelBadge.test.tsx, apps/web/src/components/studio/shell/StudioSidebar.test.tsx, apps/web/tests/thread-row-meta | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/thread-row-fallback-badge/apps/web && npx vitest run src/components/chat/ModelStateTag.test.tsx

### T-05 Composer, banner and picker header
- AC: AC-04, AC-05 | Files: apps/web/src/components/chat/ProviderModelPicker.tsx, apps/web/src/components/chat/ModelPickerContent.tsx, apps/web/src/components/chat/ChatComposer.tsx, apps/web/src/components/chat/UsageLimitRecoveryBanner.tsx, apps/web/src/components/ChatView.tsx, apps/web/src/components/chat/UsageLimitRecoveryBanner.test.tsx, apps/web/src/components/chat/ModelPickerContent.test.tsx, apps/web/src/components/chat/ProviderModelPicker.test.tsx, apps/web/tests/fallback-composer | Test: node apps/web/tests/fallback-composer/verify.mjs and focused vitest files

### T-06 Coordinator composer
- AC: AC-04, AC-05 | Files: apps/web/src/components/studio/shell/CoordinatorModelPicker.tsx, apps/web/src/components/studio/CoordinatorAccessPicker.tsx, apps/web/src/components/studio/shell/CoordinatorModelPicker.test.tsx, apps/web/src/components/studio/CoordinatorAccessPicker.test.tsx, apps/web/src/components/studio/shell/shell.css (.sws-model-fallback and data-off-pick rules only) | Test: npx vitest run src/components/studio/shell/CoordinatorModelPicker.test.tsx

### T-02 Headless before/after screenshots
- AC: AC-02, AC-04 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/thread-row-fallback-badge | Test: headless Playwright fixtures (thread-row-meta, fallback-composer) at 360/520/900px, light and dark

### T-03 Merge, release, verify installed
- AC: AC-06 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/thread-row-fallback-badge | Test: CI green, release published, installed app version readback and screenshot

### T-04 Verify and close 1005
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1005-readable-thread-row-fallback-badge | Test: specweave verify and fresh-context review

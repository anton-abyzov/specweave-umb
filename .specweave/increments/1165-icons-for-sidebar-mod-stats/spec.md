# Icons for sidebar mod stats

## Problem

The sidebar footer shows mod stats as gray text pills ("8 blocked · 19 stale claims", "6 need verify"). They take two rows at narrow widths, their tooltip only names the mod, they cannot be clicked, and `$.ui.status` accepts text only.

## Scope

In: an optional stats form of `$.ui.status`, one attention chip with a popover, crafted glyphs, and the four example mods that report counts. Out: mods that report plain text (focus-timer, the user's parallel-meter and stall-watch), which keep their pill; a new mod permission.

## Acceptance Criteria

- [ ] AC-01: `$.ui.status([{ glyph, count, label, detail, onPress }])` is checked by the host: unknown glyphs, non-positive counts and missing labels are dropped, text is bounded, and an all-zero list clears the status.
- [ ] AC-02: One chip replaces the count pills and shows the most severe glyph and the total. With nothing to report no chip renders.
- [ ] AC-03: The chip opens a popover with one row per stat: crafted glyph, label, right-aligned count, and a tooltip that explains the stat and names its mod.
- [ ] AC-04: Pressing a row closes the popover and opens that stat's list: blocked, stale claims, need verify, ready to close, trace gaps, waiting.
- [ ] AC-05: Glyphs use the 16px grid and currentColor, and no brain, lock or thinking icon appears; `retiredIcons.guard.test.ts` passes.
- [ ] AC-06: Chip and popover read cleanly in light and dark at the narrowest sidebar width, with no clipping or horizontal overflow, proven by headless screenshots.
- [ ] AC-07: Text-only mods still render their pill, and a press from a replaced status cannot reach a newer stat's handler.
- [ ] AC-08: The merged change ships in a release and is checked on the installed M4 app.

## Approach

Protocol: extend the `ui.status` message with `stats`; handlers stay in the worker and the host only receives numbers, matching pane buttons. Rendering: `ModStatGlyph.tsx` plus `ModStatusItems` in `apps/web/src/mods`. Mods: `examples/mods/{increment-standup,ready-to-close,ac-trace-lint,review-queue}`.

Rejected: letting mods ship SVG, because the host renders nothing from a mod except checked text. Rejected: a separate `$.ui.stats`, because a new mod on an older host would throw instead of going quiet.

## Decisions

### Asked
- D-01 Popover or plain icons? -> Coordinator default: one chip plus a popover, unless a measured reason favours plain icons. The user noted that Claude's chip appears only in a thread with a PR, so this chip also appears only while something needs attention.
### Defaulted (change any before sw-do)
- D-02 Tone comes from the glyph, chosen by the host, so a mod cannot make a stat look alarming.
### Open
- none

## Tasks

### T-01 Stats protocol and sandbox
- AC: AC-01, AC-07 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/mods/protocol.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/mods/sandbox.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/mods/modsStore.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/mods/ModsHost.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/mods/protocol.test.ts | Test: vitest apps/web/src/mods

### T-02 Chip, popover and glyphs
- AC: AC-02, AC-03, AC-04, AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/mods/ModStatGlyph.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/mods/ModPanes.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/mod-status | Test: headless fixture screenshots

### T-03 Example mods, docs and verify script
- AC: AC-04, AC-07 | Files: repositories/anton-abyzov/specwithcode-dev/examples/mods, repositories/anton-abyzov/specwithcode-dev/docs/studio/mods.md, repositories/anton-abyzov/specwithcode-dev/scripts/studio-mods/verify.mjs | Test: node scripts/studio-mods/verify.mjs

### T-04 Merge, release and installed check
- AC: AC-08 | Files: none | Test: installed M4 headless check

### T-05 Verify and close 1165
- AC: AC-08 | Files: none | Test: specweave verify

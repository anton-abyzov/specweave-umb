# Every clickable action looks clickable: copy dialog buttons and an app-wide sweep of bare-text actions

## Problem

Anton, November 16, 2026, on the "Send specweave to Anton M5MAX PROLED" copy dialog at 53%: "Check all places where users should understand that this is a clickable button. On the left, you see there is a gap. Think about improving it."

In that dialog "Stop copy" is a `ghost` Button: no border and no fill until hover, so it reads as a caption, and its transparent padding leaves a 12 px gap between the dialog's content edge and the text. "Change (stops this copy)" in the "Your choices" card is a `link` Button with no underline at rest. Beside them "Run in background" is an `outline` Button and reads as a button.

The same pattern is used across `apps/web`: a structural scan of origin/main `01acc4d9b5` found 343 labelled Buttons on a quiet variant (`ghost`, `ghost-muted`, `ghost-destructive`, `link`) or `InlineButton`, and 433 labelled raw `<button>` elements with no resting border, fill or underline. Many are fine (list rows, tabs, toolbar items), but the standalone ones give no sign they can be clicked.

## Scope

In: the web app (`apps/web`, which is also the desktop window). The copy dialog's leading actions and its "Change" link; a written rule for when a quiet variant is allowed; shared primitives changed once (`InlineButton`, the `link` variant); every standalone bare-text action found by the audit moved to a shared variant; a guard so new ones fail a test; headless before/after screenshots in light and dark.

Out: the Expo mobile app, the native iOS and Android apps, the marketing site and the Chrome extension (separate UI systems); icon-only buttons; list, tree and menu rows, tabs and pressed-state toggles, toolbar items with an icon, disclosure toggles with a chevron; any new colour, spacing or radius token.

## Acceptance Criteria

- [ ] AC-01: In the copy dialog footer "Stop copy" and "Stop handoff" are `destructive-outline` Buttons (border, destructive text), their left border sits on the dialog's content edge, and they keep the far-left place. The other leading actions ("Undo…", "Keep here") are `outline`.
- [ ] AC-02: "Change (stops this copy)" and "Change (stops the handoff)" in the "Your choices" card are bordered `outline` Buttons of the same size, and still stop the copy and open the setup.
- [ ] AC-03: The button rule is written next to the variants in `apps/web/src/components/ui/button.tsx`: a standalone labelled action has a resting border or fill; quiet variants are for icon-only buttons and for items whose container already shows they are clickable; an action inside a sentence is an underlined `InlineButton`.
- [ ] AC-04: `InlineButton` (default, muted and destructive tones) and the `link` Button variant are underlined at rest, changed once in `button.tsx`.
- [ ] AC-05: Every place the audit confirms as a standalone bare-text action (`reports/audit.md`, by surface: dialog footers, cards, settings rows, banners, popovers) uses a shared variant with a resting border, fill or underline. No site gets hand-written border or background classes for this.
- [ ] AC-06: A guard test fails when a new labelled, icon-less Button uses a quiet variant outside the recorded exceptions, and its message names the rule.
- [ ] AC-07: Headless before/after screenshots of the copy dialog at the copying stage in light and dark are in `reports/`, plus after shots of at least three other fixed surfaces; `themeContrastClasses.test.ts` and the touched suites pass.

## Approach

1. Scan (`scan.mjs`, TypeScript AST) lists every candidate; agents classify each one against the rule, a second pass tries to refute each flag. The confirmed list is `reports/audit.md`.
2. `button.tsx`: the rule as a comment; resting underline for `InlineButton` and `link`.
3. Copy dialog: `HandoffCopyFooter.tsx`, `HandoffCopyDone.tsx`, `HandoffSourceChanges.tsx`, `HandoffCopyGuide.tsx`, comment in `HandoffCopyActions.tsx`.
4. Sweep the confirmed sites: `ghost`/`ghost-muted`/`link` to `outline`, destructive ones to `destructive-outline`, sentence actions to `InlineButton`; raw `<button>` text actions to `Button` or `InlineButton`.
5. Guard test `apps/web/src/quietLabelledButtons.guard.test.ts`.

Rejected: restyling `ghost` itself (it carries about 220 icon-only buttons and every toolbar); a new variant (`outline`, `secondary` and `destructive-outline` already cover the three cases, so a fourth look would add inconsistency); per-site classes.

Risk: denser borders in tight rows. Each surface keeps its current size (`xs`, `sm`), and rows where the container already signals clickability stay quiet.

## Review

- Reviewer: openai (gpt-6.1-sol)
- Depth: deep
- Required: yes

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 "Stop copy" is `destructive-outline` (bordered, destructive text), not a filled destructive button: stopping a copy before Apply changes nothing on the destination, so it must not outweigh "Run in background" → default
- D-02 No new Button variant: existing `outline`, `secondary`, `destructive-outline` are the shared answer → default
- D-03 Inline sentence actions get a resting underline rather than a border → default
- D-04 Mobile, iOS, Android, marketing and the extension are out of this increment → default
### Open
- none

## Tasks

### T-01 Audit: classify every candidate and confirm the list
- AC: AC-05 | Files: .specweave/increments/1361-every-clickable-action-looks-clickable-copy-dialog-buttons-and-an-app-wide-sweep-of-bare-text-actions/reports/audit.md | Test: test -s .specweave/increments/1361-every-clickable-action-looks-clickable-copy-dialog-buttons-and-an-app-wide-sweep-of-bare-text-actions/reports/audit.md

### T-02 Shared primitives and the rule
- AC: AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/ui/button.tsx | Test: cd ~/.specwithcode/m4/verify/specwithcode/apps/web && specweave-studio checks run -- node ../../node_modules/vite-plus/bin/vp test run src/themeContrastClasses.test.ts src/components/ui

### T-03 Copy dialog buttons
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffCopyFooter.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffCopyDone.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffSourceChanges.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffCopyGuide.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffCopyActions.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/HandoffFolderCopy.wizard.test.tsx | Test: cd ~/.specwithcode/m4/verify/specwithcode/apps/web && specweave-studio checks run -- node ../../node_modules/vite-plus/bin/vp test run src/components/studio/HandoffFolderCopy.wizard.test.tsx src/components/studio/HandoffCopyFooter.test.tsx src/components/studio/HandoffFolderCopy.test.tsx src/components/studio/HandoffFolderCopy.cancel.test.tsx

### T-04 App-wide sweep of the confirmed sites
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/web/src | Test: cd ~/.specwithcode/m4/verify/specwithcode/apps/web && specweave-studio checks run -- node ../../node_modules/vite-plus/bin/vp test run src

### T-05 Guard test
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/quietLabelledButtons.guard.test.ts | Test: cd ~/.specwithcode/m4/verify/specwithcode/apps/web && specweave-studio checks run -- node ../../node_modules/vite-plus/bin/vp test run src/quietLabelledButtons.guard.test.ts

### T-06 Before/after screenshots, light and dark
- AC: AC-07 | Files: .specweave/increments/1361-every-clickable-action-looks-clickable-copy-dialog-buttons-and-an-app-wide-sweep-of-bare-text-actions/reports | Test: ls .specweave/increments/1361-every-clickable-action-looks-clickable-copy-dialog-buttons-and-an-app-wide-sweep-of-bare-text-actions/reports/copy-dialog-before-after.png

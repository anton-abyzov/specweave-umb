# 1016 Fix blurry pasted snapshots

## Problem
A pasted window snapshot card appears blurry. The card alone cannot prove degraded provider input. SpecWithCode's native macOS capture currently scales Retina PNG pixels to window bounds measured in points before attaching, discarding text detail.

## Scope
In: trace native capture, clipboard paste, composer preview, attachment preparation and provider delivery; fix confirmed premature capture loss; preserve source pixels and verify text with retained before/after artifacts.
Out: sharpening, paid provider calls, unrelated capture redesign, independent release.

Expanded user scope: selected-element/window preview annotations must retain the user comment, DOM context and a correctly located screenshot at non-default browser zoom.

## Acceptance Criteria
- [ ] AC-01: Native macOS snapshots preserve Retina PNG pixels and bytes when within the capture safety bound, independent of window point dimensions.
- [ ] AC-02: Oversized capture behavior stays bounded, preserves aspect ratio and never upscales; focused capture tests pass.
- [ ] AC-03: Evidence distinguishes thumbnail styling, capture output, pasted attachment transformations and provider delivery, with readable before/after text artifacts and explicit installed-proof limits.
- [ ] AC-05: Preview annotation crops target the selected content at 75%, 100% and 150% zoom; comment and DOM context survive capture and provider-payload construction.
- [ ] AC-04: Focused checks and fresh review pass; the release owner receives the ready result without an independent release.

- [ ] AC-06: Retained installed-artifact evidence and a real provider image handoff prove the delivered crop is readable, with byte hashes and explicit runtime boundaries.
- [ ] AC-07: The live installed desktop snapshot shortcut and selected-element annotation at 150% zoom have actual outcome evidence.

- [ ] AC-08: A snapshot from a project pane or Settings retains the exact prior scoped thread or draft, never creates an unrelated scratch chat, and does not override a newer user navigation.
- [ ] AC-09: Capturing the app itself does not request application activation or a cross-display capture animation; external-window capture behavior remains intact.

## Approach
Inspect the capture and delivery code before altering it. Isolate app changes from other owners. Change the native macOS capture budget to operate on image pixels rather than window points, retain a conservative maximum pixel envelope, and test Retina and oversized captures. Generate deterministic text imagery headlessly and exercise the actual capture transform with Electron NativeImage. Trace upload and adapters to identify later transformations. Change preview or paste behavior only if evidence shows a separate defect.

## Decisions
### Defaulted
- D-01: Preserve lossless captured pixels before applying existing provider byte limits; do not sharpen degraded imagery.
- D-02: Keep work in an isolated app worktree; preserve shared dirty files and sessions.
### Open
- None.

## Tasks
### T-01 Trace and fix native capture loss
- AC: AC-01, AC-02 | Files: apps/desktop/src/snapShot/MacSnapShot.ts, apps/desktop/src/snapShot/MacSnapShot.test.ts, apps/desktop/src/snapShot/DesktopSnapShot.ts | Test: node node_modules/vite-plus/bin/vp test run apps/desktop/src/snapShot/MacSnapShot.test.ts apps/desktop/src/snapShot/DesktopSnapShot.test.ts

### T-02 Verify visual and delivery evidence
- AC: AC-03 | Files: apps/desktop/tests/snapshot-quality/check.mjs, apps/desktop/tests/snapshot-quality/electron.cjs, docs/studio/snapshot-quality.md | Test: node apps/desktop/tests/snapshot-quality/check.mjs

### T-03 Fix zoomed preview annotation capture
- AC: AC-05 | Files: apps/desktop/src/preview/AnnotationCapture.ts, apps/desktop/src/preview/AnnotationCapture.test.ts, apps/desktop/src/preview/Manager.ts, apps/desktop/tests/snapshot-quality/check.mjs, apps/desktop/tests/snapshot-quality/electron.cjs, docs/studio/snapshot-quality.md | Test: node node_modules/vite-plus/bin/vp test run apps/desktop/src/preview/AnnotationCapture.test.ts apps/desktop/src/preview/Manager.test.ts apps/web/src/lib/previewAnnotation.test.ts apps/web/src/lib/composerContextRecords.test.ts

### T-04 Verify and close 1016
- AC: AC-04 | Files: docs/studio/snapshot-quality.md | Test: specweave verify 1016


### T-05 Verify installed artifacts and live-provider image handoff
- AC: AC-06 | Files: .github/workflows/snapshot-receipts.yml, .specweave/increments/1016-fix-blurry-pasted-snapshots/evidence/installed-20261025 | Test: python3 .specweave/increments/1016-fix-blurry-pasted-snapshots/evidence/installed-20261025/check.py

### T-06 Obtain live installed native acceptance
- AC: AC-07 | Files: .specweave/increments/1016-fix-blurry-pasted-snapshots/evidence/installed-20261025/acceptance.md | Test: live desktop snapshot shortcut and selected-element annotation at 150% zoom, user-operated or explicitly authorized native interaction

### T-08 Preserve snapshot conversation and self-capture focus
- AC: AC-08, AC-09 | Files: apps/web/src/components/desktop/SnapShotCoordinator.tsx, apps/web/src/components/desktop/SnapShotCoordinator.test.ts, apps/web/src/components/desktop/snapShotTarget.ts, apps/web/src/components/desktop/snapShotTarget.test.ts, apps/web/src/components/sidebar/mainAppLocation.ts, apps/desktop/src/snapShot/DesktopSnapShot.ts, apps/desktop/src/snapShot/DesktopSnapShot.test.ts, docs/studio/snapshot-quality.md | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/desktop/SnapShotCoordinator.test.ts apps/web/src/components/desktop/snapShotTarget.test.ts apps/desktop/src/snapShot/DesktopSnapShot.test.ts

User follow-up October 26, 2026: the physical both-Shift shortcut works, with native PNG attachments. Capturing from Settings can lose project/thread context or change the active app/desktop. Trace this separately from pixel quality; preserve exact scoped project-pane destinations and existing user draft contents. Native input remains stopped outside a newly coordinated slot.

### T-09 Preserve snapshot source metadata through durable draft restore
- AC: AC-05, AC-08 | Files: packages/contracts/src/composerDraft.ts, apps/server/src/composerDrafts/draftFiles.ts, apps/server/src/composerDrafts/draftFiles.test.ts, apps/web/src/lib/durableComposerDrafts.ts, apps/web/src/lib/durableComposerDrafts.test.ts, apps/web/src/lib/durableComposerDraftBindings.ts, apps/web/src/components/desktop/SnapShotCoordinator.tsx, apps/web/src/components/desktop/SnapShotCoordinator.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/composerDrafts/draftFiles.test.ts apps/web/src/lib/durableComposerDrafts.test.ts apps/web/src/components/desktop/SnapShotCoordinator.test.ts

Fresh review of the first T-08 candidate found that coordinator durability omitted snapshot source metadata. Keep app/window identity, accessibility text/tree and pixel coordinates through journal and host save/restore before acknowledging the native capture. Existing source-less drafts remain readable. No live database access or migration is required.

### T-07 Verify and close 1016
- AC: AC-04, AC-06, AC-07 | Files: .specweave/increments/1016-fix-blurry-pasted-snapshots/reports | Test: specweave verify 1016

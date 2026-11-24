# Verify embedded browser and recover cancelled live previews

## Problem

The user wants a live browser that navigates and scrolls inside or above the macOS app. Existing preview paths need evidence of what actually works, not a bug-free promise. The web/server picture-in-picture startup awaits media playback and metadata without cancellation checks, allowing a closed or replaced startup to continue and potentially leaving promises/resources unsettled.

## Scope

In: inspect shipped T3 v0.1.2 browser, scrolling and floating preview with retained REA evidence; compare our existing paths; reproduce lifecycle failures; fix warranted web/server pop-out initialization bugs; validate navigation/scroll/live-display behavior and failure handling headlessly.

Out: native screenshot/annotation capture, clipboard/paste, image fidelity, desktop Manager capture sections, browser-profile/account changes, service restarts, releases, hosted deployment, iOS redesign. Snapshot increment 1016 owns its listed capture files; release increment 1015 owns PR #628 and dispatch.

## Acceptance Criteria

- [ ] AC-01: Shipped evidence explains interactive embedded tabs, navigation/scroll and always-on-top display, with observed/inferred/unknown distinctions and a clean-room behavior specification before implementation.
- [ ] AC-02: A regression reproduces closing/replacing a pending server pop-out; cancelled or superseded startup cannot enter picture-in-picture or affect its replacement, and all owned media resources are cleaned.
- [ ] AC-03: Playback/metadata/PiP failures reject without hanging; expired startup and retry failures are bounded and reported. No live-display success is claimed from saved state alone.
- [ ] AC-04: Focused tests, production web build, headless navigation/scroll/frame/failure checks and fresh-context review validate the scoped change. OS-floating-window acceptance is distinguished from headless evidence.

## Approach

Use `/Users/antonabyzov/.specwithcode/m4/worktrees/browser-live-1018` on `fix/browser-live-lifecycle`. Reuse retained REA parent `ev_bb0adcdc55b2aa4b89e93c9df6a6745c717371507e864997d9f2e3a08951b99e`; avoid repeat whole-app analysis. Implement from behavior, not copied code. Preserve sandbox/profile/control boundaries.

## Decisions

### Asked
- D-01: User authorized research and warranted fixes, not headed automation or a bug-free guarantee.
- D-02: Snapshot owner confirmed exact disjoint scope. This task will not edit desktop capture files, Manager.ts, annotation paths or ChatComposer.
### Defaulted
- D-03: Keep existing interactive embedded preview and view-only always-on-top pop-out rather than building a duplicate browser.
### Open
- none

## Tasks

### T-01 Inspect shipped browser and specify independent behavior
- AC: AC-01 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/browser-live-1018/docs/research/embedded-browser-1018.md | Test: inspect retained REA module evidence and source-bound locations

### T-02 Reproduce and repair pending live-preview lifecycle
- AC: AC-02, AC-03 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/browser-live-1018/apps/web/src/browser/serverPictureInPicture.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/browser-live-1018/apps/web/src/browser/serverPictureInPicture.test.ts | Test: focused lifecycle regressions and client-runtime preview stream tests

### T-03 Verify and close 1018
- AC: AC-04 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/browser-live-1018/apps/web/tests/browser-live/, /Users/antonabyzov/.specwithcode/m4/worktrees/browser-live-1018/docs/research/embedded-browser-1018.md | Test: headless navigation/scroll/frame/failure checks, production build, fresh review, specweave verify and complete

# Reviewer order shows the family rule and readable routes

## Problem

The owner testing Settings > Models > Adversarial review on November 14, 2026 could not tell from the reviewer order that Claude-written work (Fable 5.2, Opus 5.5) is never reviewed by a Claude model: Claude Opus 5.5 sits at #1 with nothing saying it is skipped for Claude work. Rows carried a chip of stacked, unlabeled provider icons ("+4", "+2", "+1") that reads as noise. Claude showed "Usage unknown" with no reason and no way to fix it.

Code read on specwithcode `main` 8f11ba70:

- `resolveReviewer` (`packages/shared/src/adversarialReview.ts:263`) already skips the author's family first, whatever the entry's availability; Fable and Opus are both `claude` (`modelVendor.ts:10`). Tests cover Claude through Copilot.
- Since #414 the Models page shows a Review track card (`ModelTracksSettings.tsx`), but Project settings > Adversarial review still renders the old list (`AdversarialReviewSettings.tsx` + `FallbackOrderList.tsx` `ModelOrderList`) with the icon chip. Two lists for one setting.
- The icon chip lists `reviewerOrderGroups` alternates: the same model on other enabled sources, tried right after the row. The track card already shows the same sources as text.
- The Review card says "Ready" for a source whose usage reading is stale, while `resolveReviewer` treats it as "usage unknown" and only picks it when nothing else is ready, so a row can lose to a lower row with no visible reason.
- The "fallback order" link passes `?machine=`, which `/settings/models` ignores (it reads `environmentId`); "app-wide reviewer order" links to `#adversarial-review-order`, which no longer exists on the Models page.

## Scope

In: Review card shows each row's family, which work a row is skipped for, and a "who reviews" preview computed by `resolveReviewer`; Project settings uses the same Review card (icon chip removed); "Usage unknown" with its reason and a Check now action; link fixes. Out: changing the selection rule itself; an iOS review-settings screen (iOS has none; desktop renders web).

## Acceptance Criteria

- [ ] AC-01: Each Review row names its model family; a row whose family wrote the work here (the Daily and Hard models) carries "Skipped for <Family> work".
- [ ] AC-02: Under the Review list, one line per author family in Daily and Hard says which model reviews that work now ("Work by Opus 5.5 or Fable 5.2 → muse-wonder-full-1.0 reviews"), computed by `resolveReviewer`, or says no reviewer can run and why.
- [ ] AC-03: Project settings > Adversarial review shows the same Review card as the Models page (project-scoped), with no stacked-icon chip anywhere; other sources of a model read as text.
- [ ] AC-04: A Review source whose usage is unknown shows "Usage unknown" with the reason (no recent reading, last check failed, sign-in cannot report usage, refused turn, reset passed) and a Check now action that re-reads providers.
- [ ] AC-05: `resolveReviewer` keeps skipping same-family entries when the author is Fable 5.2 and Claude Opus 5.5 is #1 (test), and the settings links ("fallback order", "app-wide reviewer order") land on existing targets.

## Approach

1. `packages/shared/src/providerFallback.ts`: export `usageUnknownReason(provider, nowMs, model)`, the reasons behind `hasUsableFallbackCapacity` returning false for a signed-in source that can take a turn.
2. `packages/shared/src/modelTrackRules.ts`: `describeReviewRule({ providers, reviewers, authors, ... })` returns per-author-family preview lines via `resolveReviewer`; review `TrackSource` gains `usage` reason.
3. `apps/web/src/components/settings/ModelTracksSettings.tsx`: family chip, skipped badge, preview lines, Usage unknown chip with reason + Check now; export the Review card for project scope.
4. `AdversarialReviewSettings.tsx`: project scope renders auto switch, depth and the Review card; drop `ModelOrderList` steps with alternates; fix links. Remove the alternates chip from `FallbackOrderList.tsx`.
5. Tests: shared (Fable author with Opus #1, preview lines, usage reasons), web component tests.

Rejected: keeping the icon chip with a tooltip (the track card already lists sources as text; two lists for one setting is the inconsistency).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Icon chip → removed; sources show as text in the shared Review card.
- D-02 Author families previewed → the families of the effective Daily and Hard models on this machine or project.
- D-03 "Usage unknown" → Review card only, where it changes which row reviews.
### Open
- none

## Tasks

### T-01 Shared rules: usage-unknown reason and review preview
- AC: AC-02, AC-04, AC-05 | Files: [repositories/anton-abyzov/specwithcode/packages/shared/src/providerFallback.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/modelTrackRules.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/modelTrackRules.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/adversarialReview.test.ts] | Test: `vp test run packages/shared/src/modelTrackRules.test.ts packages/shared/src/adversarialReview.test.ts`

### T-02 Review card shows family, skipped rows, preview and usage reason
- AC: AC-01, AC-02, AC-04 | Files: [repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ModelTracksSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ModelTracksSettings.test.tsx] | Test: `vp test run apps/web/src/components/settings/ModelTracksSettings.test.tsx`

### T-03 Project settings uses the Review card; icon chip removed; links fixed
- AC: AC-03, AC-05 | Files: [repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/AdversarialReviewSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/FallbackOrderList.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/AdversarialReviewSettings.test.tsx] | Test: `vp test run apps/web/src/components/settings/AdversarialReviewSettings.test.tsx`

### T-04 Merge the reviewed implementation
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/web/tests/picker-calm/fixture.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/picker-calm/verify-settings.mjs | Test: GitHub PR #437 checks and exact-head adversarial review

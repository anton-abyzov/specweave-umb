# 1459 Quick visual guides for SpecWeave, artifacts and multiple machines

## Problem
The first-run flow gets users to a workspace. The optional sample project teaches a first feature, while everyday instructions for the Board, artifact editors and linked machines are scattered across prior sessions and docs.

## Scope
Add a repeatable Quick guides dialog on Overview. Cover the three workflows with short, illustrated cards. Preserve all setup transitions and the existing sample guide.

## Acceptance Criteria
- [ ] AC-01: Overview users can open, switch between and close three optional guide cards with the mouse or keyboard. An existing workspace can reopen them.
- [ ] AC-02: The SpecWeave card shows how an increment moves from plan through Board tracking to test evidence and review. Artifacts shows where to open files and how supported editors save changes. Multiple machines shows which machine handles each join action, plus distinct controls for Sync and Hand off.
- [ ] AC-03: The existing first-run contract still passes. The web app builds, and headless evidence includes each card and a narrow layout.
- [ ] AC-04: The shipped/planned split and ranked guide topics cite the release, prior sessions and project decisions. A different model family reviews the app commit. Record the merged product PR and its checked head.

## Approach
Use the existing Overview masthead controls, shared Dialog and Tabs primitives, Lucide symbols and theme tokens. Render a three-step illustrated list for each topic. Keep it read-only and offline-capable, with no server, persistence or wizard dependencies. Add the entry point to the welcome guide and changelog.

## Decisions
### Defaulted
- Use a persistent Overview entry so existing users can revisit the cards after setup. The sample project exercise keeps its own entry point.
- Use static illustrations and existing theme tokens so the cards work with reduced motion and in narrow windows.

### Open
- None.

## Review
Require an Anthropic model for independent review of the app PR. Use the signed-in Claude Agent provider. Gemini 4 Neon and OpenAI are excluded for this task.

## Release
After the product and umbrella PRs merge, request the normal app release and report its run.

## Tasks

### T-01 Add and verify the Quick guides
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/StudioOverview.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/StudioOverview.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/QuickGuides.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/de.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/es.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/fr.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ja.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ko.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/pt.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ru.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/zh.ts, repositories/anton-abyzov/specwithcode/docs/user/welcome-wizard.md, repositories/anton-abyzov/specwithcode/CHANGELOG.md | Test: pnpm --dir repositories/anton-abyzov/specwithcode/apps/web exec vp test run src/components/studio/StudioOverview.test.tsx src/components/onboarding/WelcomeWizard.contract.test.tsx

### T-02 Record findings, review and product merge
- AC: AC-04 | Files: none | Test: test -s .specweave/increments/1459-quick-visual-guides-for-specweave-artifacts-and-multiple-machines/reports/onboarding-status.md

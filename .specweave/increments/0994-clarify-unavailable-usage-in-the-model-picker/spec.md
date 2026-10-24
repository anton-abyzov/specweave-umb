# 0994 Clarify unavailable usage in the model picker

## Problem

The Grok composer displays bare `Unknown` beside the model. This means unreadable quota telemetry but looks like an unknown provider. The official Grok logo and provider name already resolve correctly.

## Scope

In: reason-specific composer usage copy, headless Grok identity and selection checks, reviewed PR merge. Out: provider probes, billing, admission and releases.

## Acceptance Criteria

- [ ] AC-01: The composer names missing usage by its reason instead of bare `Unknown`; detailed accessible copy stays available.
- [ ] AC-02: Grok retains its official logo and name in the composer and rail; missing usage does not prevent manual selection.
- [ ] AC-03: Focused tests, web build, headless desktop/mobile checks and fresh-context review pass; the PR merges with all checks passing.

## Approach

Pass existing formatted availability text into the trigger meter and reuse its short explanation for unknown quota. Add fictional Grok probe-failure and empty-window scenarios. Preserve quota transitions.

## Decisions

### Defaulted

- Retain the official bundled Grok mark. The screenshot already identifies the provider correctly.
- Reuse existing usage copy across the trigger and picker.

### Open

- None.

## Tasks

### T-01 Explain unavailable usage and cover Grok in the picker fixture

- AC: AC-01, AC-02 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/grok-usage-label/apps/web/src/components/chat/ModelUsage.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/grok-usage-label/apps/web/src/components/chat/ProviderModelPicker.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/grok-usage-label/apps/web/tests/picker-usage/main.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/grok-usage-label/apps/web/tests/picker-usage/verify.mjs, /Users/antonabyzov/.specwithcode/m4/worktrees/grok-usage-label/apps/web/src/studio/modelAvailability.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/grok-usage-label && node node_modules/vite-plus/bin/vp test run apps/web/src/studio/modelAvailability.test.ts apps/web/src/components/ProviderLogo.test.ts apps/web/src/components/chat/ProviderInstanceIcon.test.ts

### T-02 Verify, review and merge the fix

- AC: AC-03 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0994-clarify-unavailable-usage-in-the-model-picker/reports | Test: gh pr view 604 --repo anton-abyzov/specwithcode-dev --json state,mergeCommit,statusCheckRollup

Verify and close 0994.

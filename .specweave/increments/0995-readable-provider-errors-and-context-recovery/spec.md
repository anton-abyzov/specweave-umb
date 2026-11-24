# 0995 Readable provider errors and context recovery

## Problem
SpecWithCode displays nested JSON provider failures verbatim in banners and timeline rows. Gemini context overflow is unreadable and offers no useful recovery.

## Scope
In: bounded explicit error-message decoding, safe server redaction, existing stored errors, context-limit presentation and guarded recovery, focused and headless checks, reviewed PR and merge. Out: changing provider quota classification, provider turns, releases, installed-app acceptance.

## Acceptance Criteria
- [ ] AC-01: Nested and repeatedly encoded provider JSON becomes readable prose before server redaction and truncation; curated cause boundaries and quota classification remain intact.
- [ ] AC-02: Banner and inline timeline show clean titles and messages for stored errors; only a live context-limit failure offers supported guarded compaction and a same-project new thread.
- [ ] AC-03: Focused regressions and light/dark headless UI checks pass, the PR passes checks and merges.

## Approach
Normalize recognized error/message/response/data envelopes with depth and size limits in the existing shared error module. Normalize explicit server messages only, before credential redaction. Preserve raw comparison semantics by comparing normalized messages when matching session and turn failures. Reuse semantic alerts and buttons, the guarded composer compact callback, provider capability discovery and existing new-thread handler. Keep historical/recovered failures quiet. Use isolated fixtures and no live stores or provider requests.

## Decisions
### Asked
- None. The user authorized implementation, PR checks and merge.
### Defaulted
- Context overflow stays separate from usage quotas; unsupported compaction is hidden.
- Source merge is the acceptance boundary; no app release or service restart.
### Open
- None.

## Tasks

### T-01 Decode nested messages at safe boundaries
- AC: AC-01 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/provider-error-presentation/packages/shared/src/orchestrationV2ThreadError.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/provider-error-presentation/packages/shared/src/providerErrorMessage.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/provider-error-presentation/apps/server/src/orchestration-v2/ProviderFailure.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/provider-error-presentation/apps/server/src/orchestration-v2/ProviderFailure.test.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/provider-error-presentation && node node_modules/vite-plus/bin/vp test run packages/shared/src/providerErrorMessage.test.ts packages/shared/src/orchestrationV2ThreadError.test.ts apps/server/src/orchestration-v2/ProviderFailure.test.ts apps/server/src/orchestration-v2/UserFacingErrors.test.ts

### T-02 Present context limits and wire guarded recovery
- AC: AC-02 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/provider-error-presentation/apps/web/src/components/chat/ContextLimitRecovery.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/provider-error-presentation/apps/web/src/components/chat/ThreadErrorBanner.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/provider-error-presentation/apps/web/src/components/chat/FailureDetail.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/provider-error-presentation/apps/web/src/components/chat/MessagesTimeline.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/provider-error-presentation/apps/web/src/session-logic.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/provider-error-presentation/apps/web/src/components/ChatView.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/provider-error-presentation/apps/web/src/components/chat/ThreadErrorBanner.test.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/provider-error-presentation/apps/web/src/session-logic.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/provider-error-presentation/docs/internals/providers.md | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/provider-error-presentation && node node_modules/vite-plus/bin/vp test run apps/web/src/components/chat/ThreadErrorBanner.test.tsx apps/web/src/session-logic.test.ts apps/web/src/components/chat/MessagesTimeline.test.tsx apps/web/src/components/chat/ContextWindowMeter.logic.test.ts

### T-03 Build an isolated UI regression fixture
- AC: AC-02, AC-03 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/provider-error-presentation/apps/web/tests/provider-errors/index.html, /Users/antonabyzov/.specwithcode/m4/worktrees/provider-error-presentation/apps/web/tests/provider-errors/main.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/provider-error-presentation/apps/web/tests/provider-errors/fixture.css, /Users/antonabyzov/.specwithcode/m4/worktrees/provider-error-presentation/apps/web/tests/provider-errors/vite.config.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/provider-error-presentation && node node_modules/vite-plus/bin/vp build --config apps/web/tests/provider-errors/vite.config.ts

### T-05 Clean provider retry inspector
- AC: AC-02 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/provider-error-presentation/apps/web/src/components/chat/V2ItemInspector.tsx | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/provider-error-presentation && node node_modules/vite-plus/bin/vp test run apps/web/src/components/chat/MessagesTimeline.test.tsx

### T-06 Address independent review edge cases
- AC: AC-01, AC-02 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/provider-error-presentation/packages/shared/src/orchestrationV2ThreadError.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/provider-error-presentation/packages/shared/src/providerErrorMessage.test.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/provider-error-presentation && node node_modules/vite-plus/bin/vp test run packages/shared/src/providerErrorMessage.test.ts packages/shared/src/orchestrationV2ThreadError.test.ts apps/server/src/orchestration-v2/ProviderFailure.test.ts apps/server/src/orchestration-v2/UserFacingErrors.test.ts

### T-07 Fix the shared-test module import
- AC: AC-03 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/provider-error-presentation/packages/shared/src/providerErrorMessage.test.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/provider-error-presentation && node node_modules/typescript/bin/tsc --noEmit --project packages/shared/tsconfig.json

### T-04 Verify and close 0995
- AC: AC-03 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0995-readable-provider-errors-and-context-recovery/reports | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/provider-error-presentation && git diff --check

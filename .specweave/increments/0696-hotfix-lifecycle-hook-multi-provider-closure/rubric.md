---
increment: 0696-hotfix-lifecycle-hook-multi-provider-closure
title: "Hotfix: LifecycleHookDispatcher multi-provider closure (JIRA + ADO)"
generated: "2026-04-22"
source: hand-authored
version: "1.0"
status: active
---

# Quality Rubric — 0696

## Gates

1. **Unit tests green** — `npx vitest run tests/unit/sync/sync-coordinator.externallinks-closure.test.ts tests/unit/core/hooks/lifecycle-hook-dispatcher.closure-0696.test.ts` exits 0. All 10 tests pass.
2. **No regression** — `npx vitest run tests/unit/sync/sync-coordinator.test.ts tests/unit/sync/sync-coordinator-closure.test.ts tests/unit/sync/sync-coordinator-messages.test.ts tests/unit/core/hooks/lifecycle-hook-dispatcher.test.ts` exits 0 (69 pre-existing tests).
3. **TypeScript compiles** — `npx tsc -p tsconfig.json` exits 0 with no errors.
4. **Minimum-diff discipline** — only `src/sync/sync-coordinator.ts` and `src/core/hooks/LifecycleHookDispatcher.ts` touched in production; two new test files added.

## Smoke / dogfood assertion

JIRA epic auto-closure on `specweave complete` verified in live smoke test:
- Closing increment 0696 via `specweave complete 0696-hotfix-lifecycle-hook-multi-provider-closure --yes` MUST transition:
  - JIRA epic `SWE2E-904` to `Done` (via the `LifecycleHookDispatcher.onIncrementDone` hook, not `sync-living-docs`)
  - ADO Feature `#1743` to `Closed` (via the hook)
- Stdout MUST include `✅ JIRA SWE2E-904 transitioned to Done` and `✅ ADO #1743 transitioned to <Closed|Done>`.
- `.specweave/logs/hooks.log` MUST receive any closure errors if they occur.

## Non-gates (informational)

- Code comment at `LifecycleHookDispatcher.ts:252` updated to describe the four-source fallback.
- CHANGELOG entry at `1.0.581` describes the fix.

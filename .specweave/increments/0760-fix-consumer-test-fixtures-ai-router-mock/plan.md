# Implementation Plan: Fix stale consumer.test.ts message routing fixtures

## Overview

Single-file test fixture fix, mirror of 0758. Add a hoisted `vi.mock("@/lib/ai/ai-router", ...)` block alongside the existing 6 module mocks in `consumer.test.ts`. No production code change.

## Decision

```ts
// Hoisted helper — alongside other vi.hoisted() declarations (~line 9)
const mockCreateAiRouter = vi.hoisted(() => vi.fn(() => ({})));

// Module mock — alongside other vi.mock() calls (~line 27)
vi.mock("@/lib/ai/ai-router", () => ({
  createAiRouter: mockCreateAiRouter,
}));
```

## Why this approach

- Same pattern used for the other 6 mocked modules in this test file (`../process-submission`, `../metrics-store`, `../scan-log-store`, `../search-index-consumer`, `../../worker-context`, `../../submission-store`).
- Empty object return is safe: `processSubmission` is itself mocked (line 11), so the AI client value passed in is never inspected by real code during these tests.
- No production change. The eager `createAiRouter(env)` call at `consumer.ts:169` is correct for the Cloudflare Worker runtime where AI bindings are present.

## Files modified

- `repositories/anton-abyzov/vskill-platform/src/lib/queue/__tests__/consumer.test.ts`

## Files NOT modified

- `repositories/anton-abyzov/vskill-platform/src/lib/queue/consumer.ts` (production)
- `repositories/anton-abyzov/vskill-platform/src/lib/ai/ai-router.ts` (production)

## Architecture impact

None. No ADR. No API change. No data model change.

## Testing Strategy

1. `npx vitest run src/lib/queue/__tests__/consumer.test.ts` — expect 5 → 0 failures.
2. `npx vitest run src/lib/queue/__tests__/` — expect no neighbor regressions (process-submission.test.ts already green from 0758).
3. `git diff repositories/anton-abyzov/vskill-platform/src/lib/queue/consumer.ts` — expect empty.

## Technical Challenges

None. Single mock block, established pattern from 0758.

# Implementation Plan: Fix stale process-submission.test.ts ai-router mock

## Overview

Single-file test fixture fix. Add a hoisted `vi.mock("@/lib/ai/ai-router", ...)` block alongside the existing 12+ module mocks in `process-submission.test.ts`. No production code change.

## Decision

Mirror the existing mocking pattern used at lines 36–128 of the test file:

```ts
// Hoisted helper — alongside other vi.hoisted() declarations (~line 34)
const mockCreateAiRouter = vi.hoisted(() => vi.fn(() => ({})));

// Module mock — alongside other vi.mock() calls (~line 105)
vi.mock("@/lib/ai/ai-router", () => ({
  createAiRouter: mockCreateAiRouter,
}));
```

## Why this approach

- Consistent with how every other module that `process-submission.ts` imports is mocked in this test file (`@/lib/event-bus`, `@/lib/submission-store`, `@/lib/scanner`, `@/lib/scanner/tier1`, `@/lib/scanner/tier2`, `@/lib/scanner/dependency-analyzer`, etc.).
- Hoisted helper is the established pattern in this file — keeps the mock object addressable from `beforeEach` / individual tests if a future case wants to inspect or override its return value.
- Empty object return is safe: `runTier2Scan` is itself mocked at line 62 (`vi.mock("@/lib/scanner/tier2", ...)`), so the AI client value passed into it is never inspected by real code during tests.
- No production code change. The dynamic import at `process-submission.ts:521` is correct for the Cloudflare Worker runtime where bindings are lazily resolved.

## Files modified

- `repositories/anton-abyzov/vskill-platform/src/lib/queue/__tests__/process-submission.test.ts`

## Files NOT modified

- `repositories/anton-abyzov/vskill-platform/src/lib/queue/process-submission.ts` (production)

## Architecture impact

None. No ADR. No API change. No data model change.

## Testing Strategy

Direct verification:
1. Run the targeted file: `npx vitest run src/lib/queue/__tests__/process-submission.test.ts` — expect 14 → 0 failures.
2. Run the full queue suite to confirm no neighbor regressions: `npx vitest run src/lib/queue/__tests__/`.
3. Confirm production file is byte-for-byte unchanged: `git diff repositories/anton-abyzov/vskill-platform/src/lib/queue/process-submission.ts` — expect empty.

## Technical Challenges

None. Single mock block, established pattern.

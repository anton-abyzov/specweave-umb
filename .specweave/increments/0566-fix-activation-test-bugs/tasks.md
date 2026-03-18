---
increment: 0566-fix-activation-test-bugs
generated: 2026-03-18
test_mode: TDD
---

# Tasks: Fix Skill Studio Activation Test Bugs

## US-001: Surface Error Payloads from SSE Done Events

### T-001: Add ACTIVATION_ERROR reducer tests for error-in-done scenarios
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] Completed
**Test Plan**:
- Given `workspaceReducer.test.ts` with existing activation tests
- When `ACTIVATION_ERROR` action is dispatched with an error message
- Then `activationRunning` is `false`, `activationError` equals the message, and no history entry is produced

Specific test cases to add in `workspaceReducer.test.ts` under a new describe block `"ACTIVATION_ERROR from done event"`:
1. `ACTIVATION_ERROR` sets `activationRunning: false` and `activationError` to the error string
2. `ACTIVATION_ERROR` does not clear `activationResults` (partial results preserved)
3. State transition: `ACTIVATION_START` → `ACTIVATION_RESULT` × 2 → `ACTIVATION_ERROR` leaves partial results intact and sets error
4. `ACTIVATION_START` clears prior `activationError`

Run: `npx vitest run src/eval-ui/src/pages/workspace/workspaceReducer.test.ts`

---

### T-002: Fix WorkspaceContext SSE `done` handler to check error field (activation test)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03
**Status**: [x] Completed
**Test Plan**:
- Given `WorkspaceContext.tsx` SSE done handler for activation test (line 530 area)
- When the `done` event's `evt.data` contains `{ error: "LLM call failed" }`
- Then the handler dispatches `ACTIVATION_ERROR` with that message, clears the timeout, and does NOT dispatch `ACTIVATION_DONE` or append a history entry

Implementation: in the `evt.event === "done"` branch, check for error before casting to `ActivationSummary`:
```typescript
const raw = evt.data as { error?: string } & ActivationSummary & { description?: string };
if (raw.error) {
  if (activationTimeoutRef.current) {
    clearTimeout(activationTimeoutRef.current);
    activationTimeoutRef.current = null;
  }
  dispatch({ type: "ACTIVATION_ERROR", error: raw.error });
} else {
  // existing ACTIVATION_DONE + history append logic unchanged
}
```

File: `src/eval-ui/src/pages/workspace/WorkspaceContext.tsx`

Verification: Tests from T-001 pass. Run `npx vitest run`.

---

### T-003: Add reducer test for GENERATE_PROMPTS_ERROR from SSE done error field
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04
**Status**: [x] Completed
**Test Plan**:
- Given `workspaceReducer.test.ts` AI Prompt Generation section
- When `GENERATE_PROMPTS_START` → `GENERATE_PROMPTS_ERROR` is dispatched in sequence
- Then `generatingPrompts` is `false` and `generatingPromptsError` equals the error string

Add under a new describe block `"GENERATE_PROMPTS flow with error-in-done"`:
1. Chain `GENERATE_PROMPTS_START` → `GENERATE_PROMPTS_ERROR` — verifies both fields settle correctly
2. A second run after first clears error: `GENERATE_PROMPTS_ERROR` → `GENERATE_PROMPTS_START` → check `generatingPromptsError` is `null`

Run: `npx vitest run src/eval-ui/src/pages/workspace/workspaceReducer.test.ts`

---

### T-004: Fix WorkspaceContext to throw on error field in prompt generation SSE `done` event
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04
**Status**: [x] Completed
**Test Plan**:
- Given `WorkspaceContext.tsx` `generateActivationPrompts` SSE reader (line 653 area)
- When the `done` event's parsed data is `{ error: "generation failed" }` (no `prompts` field)
- Then the handler throws `new Error("generation failed")`, which is caught by the outer `catch` block and dispatches `GENERATE_PROMPTS_ERROR`

Change in the `if (currentEvent === "done")` branch (line 654):
```typescript
if (currentEvent === "done") {
  if (data.error) throw new Error(data.error);
  finalPrompts = data.prompts || [];
}
```

File: `src/eval-ui/src/pages/workspace/WorkspaceContext.tsx`

Verification: Tests from T-003 pass. Run `npx vitest run`.

---

## US-002: Emit Progress Events During Phase 1 Auto-Classification

### T-005: Add onProgress callback tests to activation-tester.test.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03
**Status**: [x] Completed
**Test Plan**:
- Given `activation-tester.test.ts` auto-classification section
- When `testActivation` is called with 2 auto-prompts, a valid `meta`, and a `vi.fn()` `onProgress` callback
- Then `onProgress` is called exactly 2 times during Phase 1 with `("classifying", 1, 2)` and `("classifying", 2, 2)`

Test cases to add in a new describe block `"testActivation — onProgress callback"`:
1. `onProgress` called once per auto-prompt (2 auto → 2 calls with correct index/total)
2. `onProgress` NOT called when all prompts have explicit expected values (0 auto prompts)
3. `onProgress` called only for auto prompts in a mixed array (1 auto + 1 manual → 1 call)
4. Calling without `onProgress` (undefined) does not throw — backward compatible

Run: `npx vitest run src/eval/__tests__/activation-tester.test.ts`

---

### T-006: Add onProgress parameter to testActivation and resolvePrompts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03
**Status**: [x] Completed
**Test Plan**:
- Given `activation-tester.ts` `resolvePrompts` and `testActivation` functions
- When `testActivation` is called with an `onProgress` callback and prompts containing `expected: "auto"`
- Then `onProgress` is called once after each `classifyExpectation` resolves, with correct `(phase, index, total)` values

Implementation:
1. Update `resolvePrompts` signature to accept `onProgress?: (phase: string, index: number, total: number) => void`
2. Before the loop, count auto-only prompts: `const autoTotal = prompts.filter(p => p.expected === "auto" && meta).length`
3. Maintain an `autoIndex` counter; after each `classifyExpectation` call: `onProgress?.("classifying", ++autoIndex, autoTotal)`
4. Update `testActivation` signature: add `onProgress` as 6th optional parameter
5. Pass `onProgress` to `resolvePrompts`

New `testActivation` signature:
```typescript
export async function testActivation(
  skillDescription: string,
  prompts: ActivationPrompt[],
  client: LlmClient,
  onResult?: (result: ActivationResult) => void,
  meta?: SkillMeta,
  onProgress?: (phase: string, index: number, total: number) => void,
): Promise<ActivationSummary>
```

File: `src/eval/activation-tester.ts`

Run: `npx vitest run src/eval/__tests__/activation-tester.test.ts`

---

### T-007: Wire onProgress to SSE classifying events in activation-test route
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02
**Status**: [x] Completed
**Test Plan**:
- Given `api-routes.ts` activation-test route, `testActivation` call at line 1246
- When `testActivation` invokes `onProgress("classifying", 2, 5)`
- Then the route emits `sendSSE(res, "classifying", { index: 2, total: 5 })` to the SSE stream

Implementation: add `onProgress` as 6th argument to the existing `testActivation` call:
```typescript
const summary = await testActivation(
  description, body.prompts, client,
  (result) => { if (!aborted) sendSSE(res, "prompt_result", result); },
  meta,
  (phase, index, total) => { if (!aborted) sendSSE(res, phase, { index, total }); },
);
```

File: `src/eval-server/api-routes.ts`

Verification: Run existing api-routes tests and activation-tester tests. `npx vitest run`.

---

## US-003: Show Inline Hint When Generate Button Is Disabled

### T-008: Create ActivationPanel component tests for disabled-reason hint
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02
**Status**: [x] Completed
**Test Plan**:
- Given a new test file `src/eval-ui/src/pages/workspace/ActivationPanel.test.tsx`
- When `ActivationPanel` is rendered with `WorkspaceContext` providing `cleanDescription = ""`
- Then the text "Add a description to your skill's frontmatter to enable prompt generation." is present in the DOM

- When `ActivationPanel` is rendered with a non-empty `cleanDescription`
- Then the hint text is absent from the DOM

Setup: Use Vitest + `@testing-library/react`. Wrap with a minimal `WorkspaceContext.Provider` that supplies the required state (empty evals, not running, etc.). Mock `fetch` and SSE hooks.

Run: `npx vitest run src/eval-ui/src/pages/workspace/ActivationPanel.test.tsx`

---

### T-009: Render inline disabled-reason hint in ActivationPanel when no description
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02
**Status**: [x] Completed
**Test Plan**:
- Given `ActivationPanel.tsx` button area for "Generate Test Prompts"
- When `!cleanDescription` is `true` and `activationRunning` is `false`
- Then a hint `<div>` with accessible text renders below the button row

Implementation: add after the Generate button's enclosing `</div>` (around line 124):
```tsx
{!cleanDescription && !activationRunning && (
  <div
    className="text-[11px] mt-1"
    style={{ color: "var(--text-tertiary)" }}
    aria-live="polite"
  >
    Add a description to your skill's frontmatter to enable prompt generation.
  </div>
)}
```

File: `src/eval-ui/src/pages/workspace/ActivationPanel.tsx`

Verification: Tests from T-008 pass. Visual check: open a skill without frontmatter description.

---

## US-004: Unify Description Fallback Across Activation Endpoints

### T-010: Create extractDescription helper tests
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [x] Completed
**Test Plan**:
- Given a new test file `src/eval-server/__tests__/activation-description.test.ts`
- When `extractDescription` is called with various SKILL.md content strings
- Then it returns the correct description per extraction rules

Test cases:
1. `description: "My skill desc"` in frontmatter → returns `"My skill desc"`
2. Frontmatter present but no `description` field → returns first 500 chars of body (no frontmatter)
3. No frontmatter at all → returns first 500 chars of the full content
4. Empty string input → returns `""`
5. Body longer than 500 chars → returns exactly 500-char slice
6. Frontmatter only, empty body → returns `""`

Note: `extractDescription` is a local function in `api-routes.ts`. Export it for testing or extract it to a shared utility module (e.g., `src/eval-server/skill-utils.ts`) so it can be imported in the test.

Run: `npx vitest run src/eval-server/__tests__/activation-description.test.ts`

---

### T-011: Add extractDescription helper and apply to both activation endpoints
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [x] Completed
**Test Plan**:
- Given `api-routes.ts` with `/activation-test` (line 1232) and `/activation-prompts` (line 1301) each using different description extraction logic
- When `extractDescription` is added as a local function and applied to both endpoints
- Then `/activation-prompts` no longer returns 400 when frontmatter has no description field; it falls back to body content

Implementation:
1. Add local function before the route handlers:
```typescript
function extractDescription(skillContent: string): string {
  const fmMatch = skillContent.match(/^---[\s\S]*?description:\s*"([^"]+)"[\s\S]*?---/);
  if (fmMatch) return fmMatch[1];
  const body = skillContent.replace(/^---[\s\S]*?---\s*/, "").trim();
  return body.slice(0, 500);
}
```
2. Replace line 1232–1233 in `/activation-test` with: `const description = extractDescription(skillContent);`
3. In `/activation-prompts`, replace lines 1301–1307 (the descMatch + empty check + 400 return) with: `const description = extractDescription(skillContent);`
4. The 404 guard for missing SKILL.md (line 1296) remains unchanged

File: `src/eval-server/api-routes.ts`

Run: `npx vitest run src/eval-server/__tests__/activation-description.test.ts`

---

## US-005: Emit Heartbeat During Prompt Generation

### T-012: Add heartbeat integration test for activation-prompts route
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02
**Status**: [x] Completed
**Test Plan**:
- Given a test in `src/eval-server/__tests__/activation-prompts-heartbeat.test.ts`
- When the `/activation-prompts` route processes a request and `vi.useFakeTimers()` advances by 3100ms during the awaited generate call
- Then `sendSSE` (or the SSE write stream) records at least one `"progress"` event before the `"done"` event

Setup approach:
- Mock `client.generate` to return a promise that only resolves after fake timers advance
- Spy on `sendSSE` from `sse-helpers.ts` via `vi.mock`
- Assert call order: progress before done

Alternative simpler approach if direct route testing is complex: test that `withHeartbeat` emits progress events on a 3s interval using fake timers — this directly verifies the utility used in T-013.

Run: `npx vitest run src/eval-server/__tests__/activation-prompts-heartbeat.test.ts`

---

### T-013: Wrap client.generate with withHeartbeat in activation-prompts endpoint
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02
**Status**: [x] Completed
**Test Plan**:
- Given `api-routes.ts` activation-prompts route at line 1326
- When `client.generate` completes normally in under 3 seconds
- Then no heartbeat event is emitted (timer cleared before first interval fires), and the `done` event is sent normally

- When `client.generate` takes more than 3 seconds
- Then at least one `progress` event is emitted before `done`

Implementation: replace line 1326 with:
```typescript
const { text } = await withHeartbeat(
  res,
  undefined,
  "generating",
  "Generating test prompts...",
  () => client.generate(systemPrompt, userPrompt),
);
```

Ensure `withHeartbeat` is imported from `"./sse-helpers.js"`. Check existing imports at top of `api-routes.ts`.

Note: `initSSE` is already called at line 1309 before this block.

File: `src/eval-server/api-routes.ts`

Verification: Test from T-012 passes. Run `npx vitest run`.

---

## Acceptance Criteria Coverage Matrix

| AC ID | Covered By |
|---|---|
| AC-US1-01 | T-001, T-002 |
| AC-US1-02 | T-001, T-002 |
| AC-US1-03 | T-001, T-002 |
| AC-US1-04 | T-003, T-004 |
| AC-US2-01 | T-005, T-006, T-007 |
| AC-US2-02 | T-007 |
| AC-US2-03 | T-005, T-006 |
| AC-US3-01 | T-008, T-009 |
| AC-US3-02 | T-008, T-009 |
| AC-US4-01 | T-010, T-011 |
| AC-US4-02 | T-010, T-011 |
| AC-US5-01 | T-012, T-013 |
| AC-US5-02 | T-012, T-013 |

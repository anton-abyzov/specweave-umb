# Implementation Plan: Port ## Test Cases parser to vskill (+writer)

## Overview

A self-contained vskill CLI feature: one new module (parser+serializer+upserter), two new server routes, and UI wiring in ActivationPanel + WorkspaceContext. No new dependencies. Pure regex + filesystem write. Runs entirely in-process; no network calls beyond the existing eval-server.

## Architecture

### Components

| File | Role | Type |
|---|---|---|
| `repositories/anton-abyzov/vskill/src/eval/test-case-parser.ts` | Parser, serializer, upsert helper | NEW |
| `repositories/anton-abyzov/vskill/src/eval/__tests__/test-case-parser.test.ts` | Vitest unit tests for parser/serializer/upsert | NEW |
| `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts` | + GET `/test-cases`, + PUT `/test-cases` routes | EXTEND |
| `repositories/anton-abyzov/vskill/src/eval-server/__tests__/test-cases-routes.test.ts` | Route integration tests | NEW |
| `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/ActivationPanel.tsx` | Initial-load fetch, source badge, Save button | EXTEND |
| `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/WorkspaceContext.tsx` | `activationPromptsSource` state, `SET_PROMPTS_SOURCE` action | EXTEND |
| `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/workspaceTypes.ts` | Type for `activationPromptsSource` | EXTEND |

### Data Model

```ts
// src/eval/test-case-parser.ts
export type TestCaseExpected = "should_activate" | "should_not_activate" | "auto";
export interface ParsedTestCase {
  prompt: string;
  expected: TestCaseExpected;
}
```

### API Contracts

**GET `/api/skills/:plugin/:skill/test-cases`**
- Response 200: `{ prompts: ParsedTestCase[], source: "skill-md" | null }`
- Response 404: `{ error: "skill not found" }` (existing resolveSkillDir error path)

**PUT `/api/skills/:plugin/:skill/test-cases`**
- Body: `{ prompts: ParsedTestCase[] }`
- Response 200: `{ ok: true, count: number }`
- Behavior: if `prompts.length === 0`, the `## Test Cases` block is REMOVED from SKILL.md (clean state). Otherwise, replaced or appended.

## Technology Stack

- **Language**: TypeScript (NodeNext, `.js` import extensions per vskill convention).
- **Test framework**: Vitest with existing API-route test helpers (look at neighboring `__tests__/version-routes.test.ts` pattern but only for non-failing tests; many existing route tests are flaky pre-existing).
- **UI**: React + existing CSS variables. Green pill uses `var(--green-muted)` / `var(--green)`.

**Architecture Decisions**:
- **Dedicated route over generic `/file` PUT** — the generic file-write endpoint at `api-routes.ts:2469` exists, but pushing the upsert logic client-side would force the UI to read the full file, parse, edit, write — racy and complex. A dedicated route encapsulates the section-replace logic server-side where filesystem is authoritative.
- **`auto` as a serializable Expected value** — the platform parser only knows "should activate" / "should not activate" (binary). vskill needs to round-trip `auto` prompts too (no-prefix textarea lines). Adding `auto` as a third value keeps the serialized format human-editable while preserving the existing scoring semantics from increment 0775.
- **Empty-prompts removes the section** — chose remove over write-empty-block because (a) it keeps SKILL.md clean for skills that no longer want fixtures, (b) re-running PUT with empty prompts is an explicit "clear" gesture, not an accidental save.

## Implementation Phases

### Phase 1: TDD RED — failing tests
12 vitest cases:
- 8 in `__tests__/test-case-parser.test.ts` (parse, serialize, upsert, round-trip, edge cases).
- 4 in `__tests__/test-cases-routes.test.ts` (GET happy + empty, PUT writes + preserves frontmatter).

Run: `npx vitest run src/eval/__tests__/test-case-parser.test.ts src/eval-server/__tests__/test-cases-routes.test.ts` — expect 12 fails.

### Phase 2: TDD GREEN — implement parser module
Implement `parseTestCases`, `serializeTestCases`, `upsertTestCasesIntoSkillMd`. Run vitest → 8 pass.

### Phase 3: Server routes
Add GET + PUT to `api-routes.ts`. Run vitest → 4 pass. Total 12/12 GREEN.

### Phase 4: UI wiring
- ActivationPanel: useEffect for initial load, source badge, Save button + handler.
- WorkspaceContext: `activationPromptsSource` state slice, `SET_PROMPTS_SOURCE` action, source flip on AI-generation, on edit, on save.
- workspaceTypes.ts: extend `WorkspaceState` and `WorkspaceAction` types.

### Phase 5: Build + smoke test
`npm run build:eval-ui` → clean. Then studio smoke test on greet-anton SKILL.md (manually add a `## Test Cases` block, verify load, edit, save, reload, frontmatter integrity).

## Testing Strategy

- **Unit (vitest)**: 8 parser/serializer/upsert tests — pure functions, no IO mocking needed.
- **Integration (vitest)**: 4 route tests — set up a temp skillDir with fixture SKILL.md, exercise the route via the existing test harness pattern.
- **E2E (manual smoke)**: studio Trigger tab on greet-anton — load, badge, edit, save, reload, file-content diff to confirm frontmatter+body preservation.
- **Coverage target**: 95% on the new parser module, 90% on the route handlers.

## Technical Challenges

### Challenge 1: Existing `__tests__/version-routes.test.ts` and similar route tests are pre-existing failures
**Solution**: Don't model new route tests on those flaky patterns. Look at a stable test like `__tests__/skill-updates-route.test.ts` for the harness pattern, but use a fresh fixture-based approach: write a temp SKILL.md to a temp dir, instantiate the route handler with that root, exercise it directly.
**Risk**: New tests inherit flakiness. Mitigation: keep new tests pure-function-based where possible; only test the route's request/response wiring, not the underlying parser (which is unit-tested separately).

### Challenge 2: Section-replace regex must be greedy enough to consume the whole block but not adjacent sections
**Solution**: Use the same `(?=\n## |\n---|\n$|$)` lookahead the platform's parser uses. The replace regex captures the heading and body but the lookahead stops at the next section boundary.
**Risk**: A user-authored `## Test Cases` block followed by a `## Test Cases (advanced)` block would have ambiguous boundaries. Mitigation: the lookahead `\n## ` (with trailing space) catches that; "Test Cases (advanced)" is a different heading.

### Challenge 3: Round-trip preservation when prompt strings contain double-quotes
**Solution**: The platform's parser uses `[^"]+` (no internal quotes allowed). For the writer, escape double-quotes in prompt strings as `\"` OR reject prompts with double-quotes at the API layer.
**Decision**: Reject at the API layer — return 400 with a clear error. Quote-escaping in markdown bodies is fragile and not what the parser regex expects. Authors with quote-heavy prompts can use single quotes, smart quotes, or rephrase.

### Challenge 4: Backward compat — what if 0775's `verdict` field consumers don't expect this new flow?
**Solution**: This increment doesn't touch `activation-tester.ts` or `ActivationResult`/`ActivationSummary`. The new parser feeds `ActivationPrompt[]` (the input type), not the result types. 0775's verdict logic is preserved unchanged.

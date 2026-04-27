# Implementation Plan: Studio: redirect to skill detail after Create Skill

## Overview

Two-file fix in `repositories/anton-abyzov/vskill/src/eval-ui/`. The bug is a wiring mismatch: `CreateSkillPage` uses `react-router`'s `useNavigate()` to "redirect" after a successful create, but the Studio shell's main-content slot is driven by hand-rolled hash predicates (`useIsCreateRoute`, `useIsUpdatesRoute` in `useHashRoute.ts`). The unrecognized `#/skills/<plugin>/<skill>` hash falls through to `<RightPanel>` which reads `state.selectedSkill` — and nothing has updated that. The shipped, working pattern from `<CreateSkillModal>` (App.tsx:743-761) reuses `StudioContext.revealSkill`, which both updates context state AND writes `window.location.hash`. We adopt that pattern verbatim in `CreateSkillPage`.

No new abstractions, no new routes, no new context fields. Pure state-wiring fix.

## Architecture

### Components touched
- **`CreateSkillPage` (page)** — `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/CreateSkillPage.tsx`
  - Imports `useStudio` from `../StudioContext`
  - Pulls `{ refreshSkills, revealSkill }` from context
  - Replaces `onCreated: (plugin, skill) => navigate(\`/skills/${plugin}/${skill}\`)` with the modal pattern: `refreshSkills(); setTimeout(() => revealSkill(plugin, skill), 500);`
  - Drops `useNavigate` import only if it becomes unused after the change.

### Components reused (no change)
- **`StudioContext.revealSkill`** (StudioContext.tsx:291-321) — dispatches `REVEAL_SKILL` action AND writes `window.location.hash = '/skills/{plugin}/{skill}'`. Already handles standalone skills (empty plugin) safely (lines 297-313).
- **`StudioContext.refreshSkills`** — exposed via `useStudio()`; already debounced internally.
- **`useCreateSkill.handleCreate`** (useCreateSkill.ts:621-669) — already invokes `onCreated(result.plugin, result.skill)` on both success (line 646) and 409-recovery (line 662) paths. Contract is correct; only the page-level wiring was wrong.
- **`useHashRoute`** (useHashRoute.ts) — unchanged. The lack of a `#/skills/...` predicate is intentional: `revealSkill` writes the hash for sidebar deep-linking, not for routing.
- **Backend `POST /api/skills/create`** (skill-create-routes.ts:1214-1383) — response shape `{ ok, plugin, skill, dir, … }` already exposes everything we need.

### Data model
None. No new types, no schema changes.

### API contracts
None changed.

## Technology Stack

- **Language/Framework**: TypeScript + React (existing vskill Studio UI)
- **Test stack**: Vitest + jsdom + react-dom/client `act` (matches the established pattern in `useCreateSkill-409.test.ts` and `useCreateSkill.flush.test.ts`)
- **No new dependencies.**

**Architecture decisions**:
- **Reuse the modal pattern instead of adding a `#/skills/...` route handler** — the studio's "right panel" is selection-driven, not URL-driven; adding URL-driven detail routing would be a much larger refactor (sidebar selection, deep-linking, scroll-to-row would all need to read from URL instead of `state.selectedSkill`). Out of scope.
- **Keep the 500 ms `setTimeout` from the modal pattern** — `refreshSkills` is async; `revealSkill`'s matcher reads from the latest `state.skills` via `skillsRef` (StudioContext.tsx:289-290) and bails when the new row hasn't landed yet. The 500 ms delay matches what `CreateSkillModal` ships with and has proven sufficient in production.
- **Drop `useNavigate` if unused** — avoid dead imports per CLAUDE.md "no half-finished implementations". Keep it only if it's used elsewhere in the page (e.g., for cancel/back).

## Implementation Phases

### Phase 1: Code change (single file)
- Edit `CreateSkillPage.tsx`:
  - Add `import { useStudio } from "../StudioContext";`
  - In the component body, after `const navigate = useNavigate();` (line 82), add `const { refreshSkills, revealSkill } = useStudio();`
  - Replace the `onCreated` callback at line 260 with the modal pattern.
  - Audit `navigate(...)` references in the file; remove `useNavigate` import if no other call site exists.

### Phase 2: Test
- Add `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/__tests__/CreateSkillPage.redirect.test.tsx` mirroring the rendering/mocking style in `useCreateSkill-409.test.ts`:
  - Stub `api.createSkill` to resolve with `{ ok: true, plugin, skill, dir, … }`
  - Mock `../../StudioContext` to expose spy functions for `refreshSkills` + `revealSkill` (and a no-op `state` shape sufficient for the page)
  - Mock peripheral context (`useConfig`) and `react-router-dom` `HashRouter` so `useNavigate` doesn't blow up at mount
  - Use `vi.useFakeTimers()` + `vi.advanceTimersByTime(500)` to flush the setTimeout
  - Assert: `refreshSkills` called once; `revealSkill` called once with the returned `(plugin, skill)`; both plugin-scoped and standalone (`plugin: ""`) cases covered.

### Phase 3: Verification
- Run the new test in isolation, then the broader `src/eval-ui` suite, to confirm no regressions.
- Manual smoke per spec.md success criteria: click Create Skill, observe immediate redirect to detail view + sidebar reveal.

## Testing Strategy

- **Unit (Vitest, jsdom)**: New `CreateSkillPage.redirect.test.tsx` for AC-US1-01..05 + AC-US2-01..02 (single test file, multiple `it` blocks for each AC).
- **Regression**: Existing suites — `CreateSkillPage.{picker,prefill,targetAgents}.test.tsx` and all `useCreateSkill*.test.ts` — must continue to pass unchanged.
- **E2E**: Out of scope (see spec.md).
- **Manual smoke**: One pass through both layouts (plugin-scoped + standalone) on the local studio at `localhost:3109`.

## Technical Challenges

### Challenge 1: Spying on `revealSkill` without a real `<StudioProvider>`
**Solution**: `vi.mock("../../StudioContext", () => ({ useStudio: () => ({ refreshSkills: spy1, revealSkill: spy2, state: { … minimal stub … } }) }))`. Mirrors the `vi.mock("../../api", …)` pattern already used in `useCreateSkill-409.test.ts`.
**Risk**: The page may read additional context fields (e.g., `state.selectedSkill`, `state.skills`). Mitigation: stub a minimal-but-complete `state` shape — read the page top-down to enumerate fields it actually consumes.

### Challenge 2: `useNavigate` requires router context at mount
**Solution**: Either (a) keep `useNavigate` in the page and wrap test render in `<HashRouter>` (matches the prod App.tsx wrapping in main.tsx:57), or (b) if `useNavigate` is unused after the fix, drop the import and skip the wrapper. We prefer (b) for cleanliness.
**Risk**: If `useNavigate` is used elsewhere in `CreateSkillPage` (e.g., a Cancel button), dropping the import breaks the build. Mitigation: grep before deleting; default to keeping the import + `<HashRouter>` test wrapper if any other call site exists.

### Challenge 3: Fake timers interacting with React 18 batching
**Solution**: Wrap state-affecting calls (handleCreate invocation, advanceTimersByTime) in `await act(async () => { … })`, identical to the patterns in `useCreateSkill.flush.test.ts`.
**Risk**: Low — the flush pattern is well-established in this codebase.

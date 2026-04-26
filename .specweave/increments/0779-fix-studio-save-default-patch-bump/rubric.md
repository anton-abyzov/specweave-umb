---
increment: 0779-fix-studio-save-default-patch-bump
title: "Studio Save default patch bump"
generated: "2026-04-26"
source: spec.md + plan.md
version: "1.0"
status: active
---

# Quality Contract

## Functional correctness

- Clicking Save when editor frontmatter version equals last-saved version persists content with the patch incremented by one (e.g. 1.0.2 → 1.0.3). [Evaluator: sw:grill] [Result: [x] PASS — computeSavePayload.ts:45-58 bumps patch when fromVersion === toVersion; verified by computeSavePayload.test.ts AC-US1-01 case.]
- Clicking Save when the editor declares a strictly higher version than last-saved persists the editor's version verbatim — no double-bump. [Evaluator: sw:grill] [Result: [x] PASS — equality gate at computeSavePayload.ts:45 only fires for equal versions; manual minor/patch/major cases all return content unchanged. Verified by computeSavePayload.test.ts AC-US2-02, AC-US2-03, and the manual-major case.]
- The `studio:content-saved` event still fires after a successful save (existing behavior preserved). [Evaluator: sw:grill] [Result: [x] PASS — EditorPanel.tsx:166-170 dispatches the CustomEvent post-await with detail.version = effectiveVersion.]
- The Save button remains disabled when `isDirty` is false. [Evaluator: sw:grill] [Result: [x] PASS — EditorPanel.tsx:483 `disabled={!isDirty || saving}` unchanged.]

## Test coverage

- Three vitest cases exist covering: auto-bump on equal versions, respect manual +minor, respect manual +patch. [Evaluator: sw:grill] [Result: [x] PASS — computeSavePayload.test.ts has 6 cases (3 ACs + manual-major + 2 null-safety paths). saveContent contract pinned by WorkspaceContext.saveContent.test.tsx (2 cases). Helper-level rather than render-level, but the full chain is covered piecewise. See finding F-G02 about the deviation from the AC text wording.]
- All new tests pass; existing EditorPanel and WorkspaceContext tests stay green. [Evaluator: sw:grill] [Result: [x] PASS — 8/8 0779 tests green; 7 pre-existing failures in `useSkillUpdates.real-sse*` and `UpdateBell` ToastProvider context are unrelated (verified by stashing 0779 changes — they fail on baseline too).]

## Non-regression

- `handleBump` continues to work standalone (manual button clicks still bump the textarea). [Evaluator: sw:grill] [Result: [x] PASS — EditorPanel.tsx:177-190 unchanged in shape; uses bumpVersion + setFrontmatterVersion + dispatch SET_CONTENT.]
- The `apply-improvement` backend route is unchanged. [Evaluator: sw:grill] [Result: [x] PASS — change is frontend-only (computeSavePayload.ts new file + EditorPanel.tsx + WorkspaceContext.tsx saveContent signature).]
- The `isDirty` and `saving` guards on the Save button are unchanged. [Evaluator: sw:grill] [Result: [x] PASS — EditorPanel.tsx:483 disabled prop preserved verbatim.]
- Publish flow is untouched. [Evaluator: sw:grill] [Result: [x] PASS — PublishButton wiring at EditorPanel.tsx:489-495 untouched.]

## Code quality

- The version parse-and-rewrite logic is shared between `handleSave` (via `computeSavePayload`) and `handleBump` (direct `bumpVersion` + `setFrontmatterVersion` calls) — both lean on the same primitives, no duplication of bump rules. [Evaluator: sw:grill] [Result: [x] PASS — computeSavePayload internally calls bumpVersion + setFrontmatterVersion. handleBump calls them directly. Same primitives, no duplication.]
- `computeSavePayload` is a pure function (no React state, no DOM access) — trivially unit-testable. [Evaluator: sw:grill] [Result: [x] PASS — file imports only bumpVersion + setFrontmatterVersion; no React/DOM imports; no closures over component state.]
- `saveContent` accepts an optional `contentOverride: string` to support the auto-bump path without forcing a React re-render between dispatch and save. [Evaluator: sw:grill] [Result: [x] PASS — WorkspaceContext.tsx:228 signature is `(contentOverride?: string)`; line 230 selects override or current state.]

## Documentation

- spec.md, plan.md, tasks.md, rubric.md complete and consistent. [Evaluator: sw:grill] [Result: [x] PASS — all four artifacts exist and describe the same behavior. Tasks.md mentions a `EditorPanel.handleSave.test.tsx` file path that the implementation pivoted away from (helper-level test instead) — minor doc drift, see F-G02.]
- No external docs updated — the user-visible behavior change (Save bumps patch by default) is intuitive and matches user expectation; no changelog entry required beyond commit message. [Evaluator: sw:grill] [Result: [x] PASS — bug-fix scope, no public API change.]

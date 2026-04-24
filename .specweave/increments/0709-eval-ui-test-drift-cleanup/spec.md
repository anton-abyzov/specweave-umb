---
increment: 0709-eval-ui-test-drift-cleanup
title: "eval-ui test-drift cleanup"
type: chore
priority: P2
status: active
created: 2026-04-24
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: eval-ui test-drift cleanup

## Overview

Test-only hygiene increment for vskill. Two unrelated test failures that have
been red on `main` are blocking the `sw:done` closure gates for any increment
touching `src/eval-ui/**`. Both are drift from earlier polish work where the
production code was updated intentionally but the tests were never caught up.
Production code is correct. Tests must catch up. No runtime behavior changes.

## Context

Surfaced during cross-cutting triage while shipping a Skill Studio UX polish
(AgentScopePicker — no Set-Up button, tooltips on Remote badge + Not-detected
rows). The `npx vitest run src/eval-ui` sweep was red on baseline `main`,
independent of the UX polish work. The two failures:

1. **Breadcrumb vocabulary drift (0700 polish).** 0700 intentionally renamed
   the `TopRail` breadcrumb origin labels from `OWN` / `INSTALLED` to
   `Skills` / `Project` to match the Sidebar group headers (see
   `src/eval-ui/src/components/TopRail.tsx:49-58`). Four tests still assert
   the pre-0700 vocabulary and now fail. The production code change is
   deliberately commented: *"Use Anthropic-aligned vocabulary to match the
   Sidebar group headers. Keeps the top and side in sync so the user never
   sees conflicting labels for the same skill."*
2. **Stale inline snapshot for `PluginTreeGroup` (0698 T-010).** The
   component's markup intentionally changed (added flex wrapper with
   `padding-right:6px`, chevron width bumped `12px → 16px`, font-size
   `10px → 14px`, added `font-weight:700`, fallback color switched to
   `var(--color-ink, var(--text-primary))`). The snapshot was never
   re-recorded.

Neither failure breaks user-visible behavior — the suite is just red on a
state of the world that shipped fine.

## Scope

### In scope

- Align 4 breadcrumb-label assertions with the post-0700 vocabulary.
- Re-record the `PluginTreeGroup` inline snapshot.
- Update stale test names / `it()` descriptors so future readers see the
  current vocabulary (no more "OWN" in test titles).

### Out of scope

- Any behavior change in `TopRail.tsx` or `PluginTreeGroup.tsx` — production
  code is correct. If the product direction later decides 0700 was wrong,
  that is its own increment.
- Cleanup already owned elsewhere:
  - Raw color literals in `CreateSkillPage.tsx` → **0704 T-013a** (done).
  - Provider-tooltip precedence in `CreateSkillPage.tsx` → **0704 T-013b**
    (done).

## User Stories

### US-001: Breadcrumb tests match current vocabulary
**Project**: vskill

**As an** engineer running `npx vitest run src/eval-ui`
**I want** the breadcrumb tests to assert the `Skills` / `Project` labels
**So that** the suite reflects the actual post-0700 UI contract and
`sw:done` closure gates stop false-positiving on this surface.

**Acceptance Criteria**:
- [x] **AC-US1-01**: `TopRail.test.tsx > renders breadcrumb OWN › plugin › skill when a source skill is selected` passes, with the assertion updated to `toContain("Skills")` instead of `toContain("Own")`.
- [x] **AC-US1-02**: `TopRail.test.tsx > renders breadcrumb INSTALLED when an installed skill is selected` passes, with `toContain("Project")` instead of `toContain("Installed")`.
- [x] **AC-US1-03**: `TopRail.modelselector.test.tsx > T-059 TopRail — breadcrumb navigation > OWN segment is a button-like element with an onClick handler` passes, asserting against the `Skills` segment label.
- [x] **AC-US1-04**: `qa-interactions.test.tsx > QA: TopRail breadcrumb shape` passes, asserting `"Skills"` instead of `"Own"`.
- [x] **AC-US1-05**: The three test files' `it()` / `describe()` descriptors and inline comments referring to `OWN` / `INSTALLED` are refreshed to `Skills` / `Project` where they describe the current behavior (stale descriptors were misleading enough to cause the drift in the first place).

### US-002: PluginTreeGroup snapshot reflects current DOM
**Project**: vskill

**As an** engineer running `npx vitest run src/eval-ui/src/__tests__/PluginTreeGroup.test.tsx`
**I want** the snapshot to match the current rendered markup
**So that** the test gates real regressions instead of triggering on
intentional 0698 styling changes.

**Acceptance Criteria**:
- [x] **AC-US2-01**: `PluginTreeGroup (0698 T-010) > matches snapshot for a typical AVAILABLE > Plugins subtree` passes without `-u` after the snapshot is re-recorded.
- [x] **AC-US2-02**: The re-recorded snapshot includes the wrapping `<div style="display:flex;align-items:center;padding-right:6px">` and the updated chevron styling (`width:16px`, `font-size:14px`, `font-weight:700`, `color:var(--color-ink, var(--text-primary))`).

## Verification

- `npx vitest run src/eval-ui/src/components/__tests__/TopRail.test.tsx src/eval-ui/src/components/__tests__/TopRail.modelselector.test.tsx src/eval-ui/src/components/__tests__/qa-interactions.test.tsx src/eval-ui/src/__tests__/PluginTreeGroup.test.tsx` → all green.
- `npx vitest run src/eval-ui` — confirms the cleanup introduced no new failures on adjacent tests.

## Risk

Very low. Test-only edits on a well-owned surface. The only way to regress
real behavior is to re-record the snapshot while the component is
incorrectly rendering — mitigated by reading `PluginTreeGroup.tsx` and the
0698 T-010 implementation comments first to confirm the current DOM matches
the declared design intent before accepting the new snapshot.

# Implementation Plan: eval-ui test-drift cleanup

## Architecture

This is a **test-only** cleanup. No architectural decisions. No ADRs needed.

The production surfaces `TopRail.tsx` and `PluginTreeGroup.tsx` are the
source of truth for the visible UI contract. Their current implementation
is correct (per 0700 and 0698 deliberate polish). The tests drifted and now
need to catch up.

## Files Touched

| File | Change Type | Owning AC |
|------|-------------|-----------|
| `src/eval-ui/src/components/__tests__/TopRail.test.tsx` | 2 assertion updates + descriptor refresh | AC-US1-01, AC-US1-02, AC-US1-05 |
| `src/eval-ui/src/components/__tests__/TopRail.modelselector.test.tsx` | 1 assertion update + descriptor refresh | AC-US1-03, AC-US1-05 |
| `src/eval-ui/src/components/__tests__/qa-interactions.test.tsx` | 1 assertion update + descriptor refresh | AC-US1-04, AC-US1-05 |
| `src/eval-ui/src/__tests__/PluginTreeGroup.test.tsx` | Re-record inline snapshot | AC-US2-01, AC-US2-02 |

**Files NOT touched**: `TopRail.tsx`, `PluginTreeGroup.tsx`, any other
production source. If this increment touches production code it has scoped
wrong and must stop.

## Approach

### US-001 — Breadcrumb vocabulary (4 assertions)

For each of the 4 failing tests:

1. Read current production value from `TopRail.tsx:49-58`:
   - `"installed"` → `"Project"`
   - else (source/own) → `"Skills"`
2. Replace `toContain("Own")` → `toContain("Skills")`,
   `toContain("Installed")` → `toContain("Project")`.
3. Refresh the `it()` descriptor / leading comment to describe current
   vocabulary (e.g. `"renders breadcrumb Skills › plugin › skill when a
   source skill is selected"`). Stale descriptors caused this drift.

### US-002 — PluginTreeGroup snapshot

1. Read `PluginTreeGroup.tsx` and the 0698 T-010 implementation comments to
   confirm the current DOM matches the declared design intent:
   - Flex wrapper `<div style="display:flex;align-items:center;padding-right:6px">` around the expand/collapse `<button>`.
   - Chevron `<span>` with `width:16px`, `font-size:14px`, `font-weight:700`,
     `color:var(--color-ink, var(--text-primary))`, `flex:1` on the
     enclosing button.
2. Run `npx vitest run src/eval-ui/src/__tests__/PluginTreeGroup.test.tsx -u`
   to accept the new inline snapshot.
3. Inspect the resulting diff — verify nothing else changed unexpectedly
   before keeping the edit.

## Verification

- **Phase 1** (after US-001 edits): `npx vitest run src/eval-ui/src/components/__tests__/TopRail.test.tsx src/eval-ui/src/components/__tests__/TopRail.modelselector.test.tsx src/eval-ui/src/components/__tests__/qa-interactions.test.tsx` → green.
- **Phase 2** (after US-002 snapshot re-record): `npx vitest run src/eval-ui/src/__tests__/PluginTreeGroup.test.tsx` → green without `-u`.
- **Phase 3** (full regression): `npx vitest run src/eval-ui` → no new reds introduced.

## Risk + Mitigation

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Re-record snapshot while component is actually wrong | Low | Read production + 0698 T-010 comments before accepting snapshot. Visually diff snapshot before save. |
| Descriptor refresh introduces typo in `it()` string | Very low | Lint + vitest name changes are safe; vitest still runs by index. |
| Cleanup touches production code accidentally | Very low | Plan explicitly forbids it. Any diff outside `__tests__/` fails review. |

## Out-of-Scope Follow-ups

- Consider adding a `strings.ts` source-of-truth for UI vocabulary so the
  next rename doesn't cascade through individual test files. Out of scope
  here — separate increment.

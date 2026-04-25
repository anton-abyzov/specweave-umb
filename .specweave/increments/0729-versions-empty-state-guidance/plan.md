# Implementation Plan: Versions tab empty-state guidance

## Overview

Front-end-only change in `src/eval-ui/src/pages/workspace/VersionHistoryPanel.tsx`. Replace the single empty-state branch (line 175-183) with two branches keyed off `skill.origin`. Extract the URL builder to a pure helper for unit-testability.

## Architecture

### Components touched

| File | Change |
|---|---|
| `src/eval-ui/src/pages/workspace/VersionHistoryPanel.tsx` | Replace single empty branch with two `data-testid`-distinguished branches: source vs installed |
| `src/eval-ui/src/utils/submit-url.ts` (NEW) | Pure helper `buildSubmitUrl(repoUrl?: string): string` |
| `src/eval-ui/src/utils/__tests__/submit-url.test.ts` (NEW) | Unit tests for the URL builder |
| `src/eval-ui/src/pages/workspace/__tests__/VersionHistoryPanel.empty-state.test.tsx` (NEW) | Component tests for the two empty-state branches |

### Data flow

```
WorkspaceContext.state.skill (SkillInfo from /api/skills)
  ├─ skill.origin: "source" | "plugin" | "global"
  └─ skill.homepage | skill.repoUrl (optional, may be null)

VersionHistoryPanel
  ├─ versions empty + origin === "source"  → LocalEmptyState (CTA)
  ├─ versions empty + origin !== "source"  → InstalledEmptyState (legacy msg)
  └─ versions present                       → existing timeline (unchanged)
```

### Why a helper

Tests can exercise URL construction without mounting React. The component test asserts that the helper output is rendered into `href`, not the exact URL shape.

## Test Strategy

Strict TDD: RED tests first.

1. `src/eval-ui/src/utils/__tests__/submit-url.test.ts`
   - No repoUrl → `https://verified-skill.com/submit`
   - With repoUrl → `https://verified-skill.com/submit?repo=<encoded>`
   - Special chars → properly encoded

2. `src/eval-ui/src/pages/workspace/__tests__/VersionHistoryPanel.empty-state.test.tsx`
   - AC-US1-01: source + empty → renders `versions-empty-state-local` + CTA
   - AC-US1-02: installed + empty → renders `versions-empty-state-installed` + no CTA
   - AC-US1-03: CTA href matches `buildSubmitUrl()`, has `target="_blank"`, `rel="noopener noreferrer"`
   - AC-US1-04: stable `data-testid` selectors

## Risks

| Risk | Mitigation |
|---|---|
| `skill.origin` undefined for legacy shapes | Defensive: undefined → not-source → installed branch (legacy msg) |
| `repoUrl` includes credentials | URL-encode; only `https://github.com/...` patterns honoured |
| Existing snapshot tests | Other test files mock the panel as `() => null` — my changes are insulated |

## ADRs

No new ADRs — pure UI change within existing component contract.

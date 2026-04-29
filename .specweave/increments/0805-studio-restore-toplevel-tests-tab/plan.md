---
increment: 0805-studio-restore-toplevel-tests-tab
status: planned
---

# Plan — Restore top-level Tests tab

## Architecture

One-file change: add `"tests"` to `TAB_DESCRIPTORS` in `src/eval-ui/src/components/RightPanel.tsx`, render `<TestsPanel />` (non-embedded) in the Tests tab content branch, and remove the 0792 legacy `?tab=tests` → `?tab=run&mode=benchmark` redirect.

## File Targets

| File | Change |
|------|--------|
| `src/eval-ui/src/components/RightPanel.tsx` | (1) Insert `{ id: "tests", label: "Tests" }` into TAB_DESCRIPTORS between Edit and Run. (2) Add `import { TestsPanel } from "../pages/workspace/TestsPanel"`. (3) Add Tests tab content branch rendering `<TestsPanel />`. (4) Remove `?tab=tests` legacy redirect block (lines ~92-109). |
| `e2e/qa-click-audit.spec.ts` (and any other 0792-era spec) | Migrate any "exactly 4 tabs" assertion to "exactly 5 tabs" — fix locator counts |

## Test Strategy

- **Unit**: Add a small RightPanel test asserting TAB_DESCRIPTORS contains `tests` in correct order and that TestsPanel mounts on `?tab=tests`.
- **Playwright**: Add `e2e/0805-tests-tab.spec.ts` asserting (a) 5 tabs visible, (b) Tests tab clickable, (c) TestsPanel content renders. Migrate 0792 specs as needed.

## Release Strategy

Bundle into the same vskill 1.0.x patch as 0800 (single release, two increments). Sequence:
1. Build `dist/eval-ui/`
2. `npm version patch --no-git-tag-version`
3. Commit with message referencing both 0800 + 0805
4. `npm publish`
5. Verify `npx vskill@latest studio`
6. `git push origin main`

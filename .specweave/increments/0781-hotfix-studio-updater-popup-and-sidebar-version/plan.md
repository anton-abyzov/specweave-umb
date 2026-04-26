# Plan — 0781 hotfix

## Files touched

| Path | Change |
|---|---|
| `vskill/src/eval-ui/src/version-resolver.ts` | Extend `ResolveSkillVersionInput` with optional `installedCurrentVersion` + `preferInstalled`. When `preferInstalled` is true and `installedCurrentVersion` is a valid semver, return it with `versionSource: "registry"` ahead of the frontmatter check. |
| `vskill/src/eval-ui/src/api.ts` | In both call sites (`normalizeSkillInfo` line 317 + `mergeUpdatesIntoSkills` line 1316), pass `preferInstalled: info.origin === "installed"` and `installedCurrentVersion: info.currentVersion ?? null`. |
| `vskill/src/eval-ui/src/components/UpdateDropdown.tsx` | Width 320 → 440. Remove the `platformDegraded` / `platformReason` banner block + props. Drop the `useStudio()` hook line that's no longer used (it stays — `onSkillUpdated` is still used). |
| `vskill/src/eval-ui/src/components/UpdateBell.tsx` | Stop passing `platformDegraded` / `platformReason` to `UpdateDropdown`. Keep the bell's own degraded styling (icon colour, tooltip, ariaLabel). |
| `vskill/src/eval-ui/src/pages/workspace/VersionHistoryPanel.tsx` | Add a `formatDiffSummary` helper. When the trimmed lowercase form is `"0 files"` or `"no file changes"` (or `"no files"`), render "Metadata-only release — no file changes". Apply at line 396 render site. |
| `vskill/src/eval-ui/src/components/__tests__/UpdateDropdown-degraded-banner.test.tsx` | **Delete** — banner removed from this component. The bell-level degraded styling has its own tests (`UpdateBell-degraded.test.tsx`) which remain unchanged. |

## New tests (RED → GREEN)

| Test file | What it asserts |
|---|---|
| `vskill/src/eval-ui/src/__tests__/version-resolver.installed.test.ts` | New cases for `preferInstalled` flag — installed wins over frontmatter when set; falls through to existing chain when unset or when `installedCurrentVersion` invalid. |
| `vskill/src/eval-ui/src/components/__tests__/SkillRow.installedVersion.test.tsx` | Renders a SkillRow with `origin: "installed"`, `version: "1.0.3"`, `currentVersion: "1.0.2"` → badge text is `1.0.2`. With `origin: "own"` same inputs → badge is `1.0.3`. |
| `vskill/src/eval-ui/src/components/__tests__/UpdateDropdown.width.test.tsx` | Renders the dropdown, asserts the root element has `width >= 440`. Renders a long skill name + assert the inline Update button's `textContent` is exactly `"Update"` (not truncated by ellipsis style). |
| `vskill/src/eval-ui/src/components/__tests__/UpdateDropdown.no-banner.test.tsx` | Replaces the deleted degraded-banner test. Asserts that `[data-testid='update-dropdown-platform-degraded-banner']` is NEVER rendered, regardless of any external degraded state. |
| `vskill/src/eval-ui/src/pages/workspace/__tests__/VersionHistoryPanel.diffSummary.test.tsx` | (or unit-test the helper directly) — `formatDiffSummary("0 files") === "Metadata-only release — no file changes"`, `formatDiffSummary("0 Files") === ...`, `formatDiffSummary("Synced SKILL.md") === "Synced SKILL.md"`, `formatDiffSummary(null) === ""`. |

## Validation

```bash
cd repositories/anton-abyzov/vskill
npx vitest run src/eval-ui/src/__tests__/version-resolver.installed.test.ts \
                src/eval-ui/src/components/__tests__/SkillRow.installedVersion.test.tsx \
                src/eval-ui/src/components/__tests__/UpdateDropdown.width.test.tsx \
                src/eval-ui/src/components/__tests__/UpdateDropdown.no-banner.test.tsx
npx vitest run src/eval-ui          # full eval-ui suite to catch regressions
npm run typecheck
```

## Rollback

Pure UI; revert by reverting the commit. No DB/migration/lockfile changes.

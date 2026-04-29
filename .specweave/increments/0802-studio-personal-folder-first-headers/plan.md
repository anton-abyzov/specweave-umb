# Plan: 0802 — Personal section folder-first headers

## Strategy

Mirror the project-scope labeling rule onto personal-scope, then add a small "tool sublabel" caption shared by both. Keep changes surgical: scanner derivation, type field, one render branch.

## Files Touched

1. **`repositories/anton-abyzov/vskill/src/eval/skill-scanner.ts`**
   - Helper: `pluginLabelForGlobal(globalSkillsDir, agentId): { plugin: string, pluginDisplay: string }`.
     - Compute `parent = path.basename(path.dirname(globalSkillsDir))`.
     - If `parent` starts with `.` and length ≥ 2 → use `parent` as `plugin`.
     - Else → fall back to `agentId`.
     - `pluginDisplay = agent.displayName`.
   - Patch `scanSkillsTriScope` global branch to emit `plugin: derivedFolder, pluginDisplay: agent.displayName`.
   - Helper: `displayForLocalPluginFolder(folderName): string | undefined`.
     - Strips leading `.` and looks up via `agentIdForLocalPrefix(folderName)`.
     - Returns the registry's `displayName` when found.
   - Patch `enrichWithScopeAndSymlink` (or the immediate emission paths) to set `pluginDisplay` on project skills whose folder maps to an agent prefix.

2. **`repositories/anton-abyzov/vskill/src/eval/skill-scanner.ts` types** (nearby `SkillInfo`)
   - Add `pluginDisplay?: string`.

3. **`repositories/anton-abyzov/vskill/src/eval-ui/src/types.ts`**
   - Mirror `pluginDisplay?: string` on the UI's `SkillInfo` type.

4. **`repositories/anton-abyzov/vskill/src/eval-ui/src/components/PluginGroup.tsx`**
   - In the header div, render an additional caption span when `skills[0].pluginDisplay` is non-empty AND not exactly equal (case-fold) to the plugin label minus leading dot.
   - Caption styling: fontSize 9, color `var(--text-tertiary, #999)`, marginLeft 6.

5. **Tests**
   - `repositories/anton-abyzov/vskill/src/eval/skill-scanner.test.ts` — add 3 cases (`.claude` global, `.cursor` global, Amp `~/.config/agents` fallback).
   - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/PluginGroup.test.tsx` — add sublabel render + omission cases.
   - Update any fixture that hard-codes `plugin: "claude-code"` to `plugin: ".claude"` or to the new contract.

## TDD Order

1. **RED-A**: scanner test asserts `.claude` + `Claude Code` for a fixture home.
2. **GREEN-A**: implement `pluginLabelForGlobal` + emission.
3. **RED-B**: scanner test asserts Amp fallback (`amp` + `Amp`).
4. **GREEN-B**: extend helper with fallback branch.
5. **RED-C**: scanner test asserts project `.claude/skills/*` carries `pluginDisplay: "Claude Code"`.
6. **GREEN-C**: enrich project skills via `displayForLocalPluginFolder`.
7. **RED-D**: PluginGroup test asserts caption renders + omits.
8. **GREEN-D**: render caption in PluginGroup.
9. **REFACTOR**: collapse the two label-derivation helpers into a small module if duplication appears; tighten types.

## Verification

- `npx vitest run src/eval/skill-scanner.test.ts src/eval-ui/src/components/__tests__/PluginGroup.test.tsx` (workspace).
- `npm run build && npm run build:ui` (or whatever vskill's bundle script is) to refresh studio's served bundle.
- Self-install + run vskill studio, screenshot the sidebar.
- `npx playwright test` if any Studio E2E exists for the sidebar; otherwise N/A.

## Rollback

Single commit revert. Field is optional; older bundles ignore it.

## Risks

- A test fixture elsewhere may assert the old `claude-code` label and start failing — addressed in AC-US3-04.
- If `agentIdForLocalPrefix` already strips the leading dot, the helper must too; quick read of that fn confirms shape.

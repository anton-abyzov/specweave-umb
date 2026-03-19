---
increment: 0593-fix-refresh-plugins-tool-detection
title: "Fix refresh-plugins to detect project AI tool"
status: planned
---

# Tasks

## T-001: Add getSkillsDirectory() to IAdapter interface and AdapterBase
**User Story**: US-002 | **Satisfies ACs**: AC-US1-01, AC-US2-01 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US2-01

Add `getSkillsDirectory(): string` to `IAdapter` in `src/adapters/adapter-interface.ts`, and provide a default implementation in `AdapterBase` (`src/adapters/adapter-base.ts`) returning `.claude/skills` as the fallback. This is the foundation all other tasks build on.

**Test Plan**: Given `AdapterBase` is extended → When `getSkillsDirectory()` is called → Then returns `.claude/skills`. Given a concrete adapter overrides the method → When called → Then returns the adapter-specific path.

---

## T-002: Implement getSkillsDirectory() on all 17 adapter implementations
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**AC**: AC-US1-01

Add `getSkillsDirectory()` to every concrete adapter class returning its tool-specific directory. Adapters and their paths (from plan.md D-1 table):

| Adapter dir | Skills dir |
|---|---|
| cursor | `.cursor/skills` |
| windsurf | `.windsurf/skills` |
| cline | `.cline/skills` |
| copilot | `.github/skills` |
| opencode | `.opencode/skills` |
| codex | `.codex/skills` |
| gemini | `.gemini` |
| antigravity | `.agent/skills` |
| jetbrains | `.junie/skills` |
| amazonq | `.amazonq/skills` |
| continue | `.continue/skills` |
| aider | `.aider/skills` |
| trae | `.trae/skills` |
| zed | `.zed/skills` |
| tabnine | `.tabnine/skills` |
| kimi | `.kimi/skills` |
| generic | `.agents/skills` |

**Test Plan**: Given any concrete adapter instance → When `getSkillsDirectory()` is called → Then returns the expected tool-specific path from the table above.

---

## T-003: Add targetSkillsDir option to copyPluginSkillsToProject()
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed
**AC**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04

In `src/utils/plugin-copier.ts`, add optional `targetSkillsDir?: string` field to `CopyPluginOptions`. When provided, use `join(projectRoot, targetSkillsDir, skillName, 'SKILL.md')` as the destination instead of the hardcoded `.claude/skills` path. Hook file copying to `.claude/hooks/` must only happen when `targetSkillsDir` is unset or equals `.claude/skills`.

**Test Plan**: Given `copyPluginSkillsToProject()` is called with `targetSkillsDir: '.cursor/skills'` → When a plugin with skills is processed → Then files are written to `{projectRoot}/.cursor/skills/{skillName}/SKILL.md`. Given no `targetSkillsDir` → Then behavior matches current (`.claude/skills/`). Given `targetSkillsDir` is non-Claude → Then hook files are NOT copied.

---

## T-004: Implement resolveActiveAdapter() helper in refresh-plugins.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-02, AC-US1-03

Add `resolveActiveAdapter(projectRoot: string): ResolvedAdapter` function to `src/cli/commands/refresh-plugins.ts` with the interface:

```typescript
interface ResolvedAdapter {
  name: string;
  method: 'native-cli' | 'file-copy';
  skillsDir: string;
}
```

Resolution order (from plan.md D-3 and D-5):
1. Read `config.adapters.default` from `.specweave/config.json` via `fs.readFileSync` + `JSON.parse` (sync, no ConfigManager import).
2. If adapter is explicitly set and NOT `claude` and IS in known adapter mapping → load via `AdapterLoader`, call `getSkillsDirectory()`, return `{ name, method: 'file-copy', skillsDir }`.
3. If adapter NOT in known mapping → log warning and fall through to Claude detection.
4. If adapter is `claude` or unset → call `detectClaudeCli()`:
   - CLI available + plugin commands work → `{ name: 'claude', method: 'native-cli', skillsDir: '' }`
   - Otherwise → `{ name: 'claude', method: 'file-copy', skillsDir: '.claude/skills' }`

**Test Plan**: Given config has `adapters.default: 'cursor'` → When `resolveActiveAdapter()` is called → Then returns `{ name: 'cursor', method: 'file-copy', skillsDir: '.cursor/skills' }`. Given config has `adapters.default: 'claude'` and CLI available → Then returns `{ name: 'claude', method: 'native-cli', skillsDir: '' }`. Given config missing → Then falls back to Claude CLI detection. Given unknown adapter name → Then logs warning and falls back to Claude detection.

---

## T-005: Update refreshPluginsCommand() to use resolveActiveAdapter()
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-04, AC-US1-05 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-02, AC-US1-04, AC-US1-05

Replace the `detectClaudeCli()` call at the top of `refreshPluginsCommand()` in `src/cli/commands/refresh-plugins.ts` with `resolveActiveAdapter(projectRoot)`. Update downstream logic:

- Use `resolved.method === 'native-cli'` instead of `useNativeCli` flag.
- Pass `resolved.skillsDir` as `targetSkillsDir` to `copyPluginSkillsToProject()` when adapter is not `claude`.
- Update the mode display message to show `resolved.name` and `resolved.skillsDir` instead of always printing "Claude CLI" or ".claude/skills/" (AC-US1-04).
- Gate `enablePluginsInSettings()`, `cleanupStalePlugins()`, and `migrateUserLevelPlugins()` behind `resolved.name === 'claude'` check (AC-US1-05).

**Test Plan**: Given resolved adapter is `cursor` → When `refreshPluginsCommand()` runs → Then mode display shows cursor, `enablePluginsInSettings` is NOT called, skills are written to `.cursor/skills/`. Given resolved adapter is `claude` native → Then existing native-CLI path executes unchanged. Given resolved adapter is `claude` file-copy → Then `.claude/skills/` path executes unchanged.

---

## T-006: Write unit tests for resolveActiveAdapter()
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-02, AC-US1-03

Create `tests/unit/refresh-plugins-adapter.test.ts`. Cover:

1. Config `adapters.default: 'cursor'` → returns cursor skills dir via file-copy method
2. Config `adapters.default: 'opencode'` → returns `.opencode/skills` via file-copy method
3. Config `adapters.default: 'claude'` + CLI available → returns native-cli method
4. Config `adapters.default: 'claude'` + CLI unavailable → returns file-copy to `.claude/skills`
5. Config missing (no `.specweave/config.json`) → falls back to Claude CLI detection
6. Unknown adapter name in config → logs warning, falls back to Claude detection

Use `vi.mock()` and `vi.hoisted()` to stub `detectClaudeCli` and filesystem reads.

**Test Plan**: Given mocked config scenarios → When `resolveActiveAdapter()` is called → Then returned `ResolvedAdapter` matches expected shape for each scenario.

---

## T-007: Write unit tests for copyPluginSkillsToProject() with custom targetSkillsDir
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed
**AC**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04

Create `tests/unit/plugin-copier-target-dir.test.ts`. Cover:

1. With `targetSkillsDir: '.cursor/skills'` writes to `{projectRoot}/.cursor/skills/{skillName}/SKILL.md`
2. All subdirectories of the target are preserved correctly
3. Without `targetSkillsDir`, output path is `{projectRoot}/.claude/skills/{skillName}/SKILL.md` (regression guard)
4. Hook files are NOT copied when `targetSkillsDir` is a non-Claude path
5. Hook files ARE copied when `targetSkillsDir` is unset or `.claude/skills`

Use `vi.mock()` and `vi.hoisted()` to stub the filesystem.

**Test Plan**: Given mocked plugin source with skills → When function is called with each scenario → Then file writes go to the expected target paths.

---

## T-008: Run tests and verify no regression on Claude path
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-02

Run the full test suite (`npx vitest run`) from within `repositories/anton-abyzov/specweave/` and confirm all pre-existing tests pass alongside the new tests added in T-006 and T-007. Fix any regressions before marking this task complete.

**Test Plan**: Given the full vitest suite runs → When all tests complete → Then no previously-passing test fails and new tests all pass with 90%+ coverage on modified files.

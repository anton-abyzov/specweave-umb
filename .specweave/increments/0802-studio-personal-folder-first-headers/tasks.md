# Tasks: 0802 — Personal section folder-first headers

## TDD RED → GREEN → REFACTOR

### T-001: Scanner RED — personal `.claude` label test
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US2-01 | **Status**: [x] completed
**Test**: Given a fixture home `tmp/home` with `.claude/skills/foo/SKILL.md` → When `scanSkillsTriScope(root, { agentId: "claude-code", home: tmp/home })` runs → Then the global skill emits `plugin === ".claude"` AND `pluginDisplay === "Claude Code"`.

### T-002: Scanner GREEN — `pluginLabelForGlobal` helper + emit
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US2-01 | **Status**: [x] completed
**Test**: T-001 turns green.

### T-003: Scanner RED — Cursor / Codex symmetry
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test**: Given fixture homes for Cursor (`.cursor/skills/foo`) and Codex (`.codex/skills/bar`) → When scanned with the matching agentId → Then `plugin` is `.cursor` / `.codex` and `pluginDisplay` matches each agent's `displayName`.

### T-004: Scanner GREEN — symmetry passes
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test**: T-003 turns green via the same helper.

### T-005: Scanner RED — Amp fallback (`~/.config/agents/skills`)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test**: Given fixture home with `.config/agents/skills/foo/SKILL.md` → When scanned with `agentId: "amp"` → Then `plugin === "amp"` (NOT `agents`) and `pluginDisplay === "Amp"`.

### T-006: Scanner GREEN — fallback branch
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test**: T-005 turns green.

### T-007: Scanner RED — project `.claude/skills/*` carries `pluginDisplay`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**Test**: Given a project root with `.claude/skills/baz/SKILL.md` → When `scanSkills(root)` runs → Then the emitted skill has `plugin === ".claude"` AND `pluginDisplay === "Claude Code"`.

### T-008: Scanner GREEN — project enrichment
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**Test**: T-007 turns green via `displayForLocalPluginFolder` lookup.

### T-009: Type plumbing — add `pluginDisplay?: string`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test**: Compiles in `src/eval/skill-scanner.ts` SkillInfo + `src/eval-ui/src/types.ts` SkillInfo; no eslint errors.

### T-010: PluginGroup RED — sublabel render contract
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-04 | **Status**: [x] completed
**Test**: Given a SkillInfo with `pluginDisplay: "Claude Code"` and another with no `pluginDisplay` → When PluginGroup is rendered → Then the first shows a caption matching `Claude Code` AND the second shows no caption.

### T-011: PluginGroup GREEN — caption render
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-04 | **Status**: [x] completed
**Test**: T-010 turns green; existing PluginGroup tests still green.

### T-012: Fixture cleanup — update tests asserting `plugin: "claude-code"`
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [x] completed
**Test**: Search vskill workspace for `plugin: "claude-code"` test fixtures; update each to the new contract OR confirm they exercise legitimately-different code paths.

### T-013: Build + verify in studio
**User Story**: US-001, US-002 | **Satisfies ACs**: all | **Status**: [x] completed
**Test**: `npm run build` (vskill) succeeds → run `vskill studio` → sidebar shows `.CLAUDE (n)` under PERSONAL with `Claude Code` caption.

### T-014: Commit, push, publish, deploy
**User Story**: US-001, US-002 | **Satisfies ACs**: all | **Status**: [x] completed
**Test**: `npm publish` (or project's release script) succeeds; `vskill@latest` carries the change.

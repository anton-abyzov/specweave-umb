# Tasks: 0694 CLI coverage — Warp + Amazon Q + Copilot CLI split + isRemoteOnly

**Test Mode**: TDD (RED → GREEN → REFACTOR per task)

---

### T-001: Add `isRemoteOnly?: boolean` to AgentDefinition interface
**User Story**: US-004 | **AC**: AC-US4-01 | **Status**: [x] completed
**Test Plan**: Given the `AgentDefinition` type → When a fixture sets `isRemoteOnly: true` → Then TypeScript compilation passes and `Object.keys(fixture).includes('isRemoteOnly')` is true.

### T-002: Add `LEGACY_AGENT_IDS` alias map and update `getAgent()`
**User Story**: US-001 | **AC**: AC-US1-04 | **Status**: [x] completed
**Test Plan**: Given `LEGACY_AGENT_IDS = { 'github-copilot': 'github-copilot-ext' }` → When `getAgent('github-copilot')` is called → Then it returns the same object as `getAgent('github-copilot-ext')` (not undefined).

### T-003: Rename `github-copilot` → `github-copilot-ext` (VS Code extension)
**User Story**: US-001 | **AC**: AC-US1-02 | **Status**: [x] completed
**Test Plan**: Given the registry → When inspecting the entry with `localSkillsDir: '.github/copilot/skills'` → Then `id === 'github-copilot-ext'` and `displayName === 'GitHub Copilot (VS Code)'`.

### T-004: Add `copilot-cli` standalone entry (verify path via WebFetch)
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-03 | **Status**: [x] completed
**Test Plan**: Given the registry → When `getAgent('copilot-cli')` is called → Then it returns `{ id: 'copilot-cli', displayName: 'GitHub Copilot CLI', localSkillsDir: '.copilot/skills', globalSkillsDir: '~/.copilot/skills', detectInstalled: 'which copilot', parentCompany: 'GitHub (Microsoft)' }`.

### T-005: Add `warp` entry (verify path via WebFetch on docs.warp.dev/agent-platform)
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test Plan**: Given the registry → When `getAgent('warp')` is called → Then it returns an entry with `displayName: 'Warp'`, `parentCompany: 'Warp'`, `detectInstalled: 'which warp'`, and a verified or `// VERIFY`-tagged skills dir.

### T-006: Add `amazon-q-cli` entry (verify path via WebFetch on aws/amazon-q-developer-cli)
**User Story**: US-003 | **AC**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Test Plan**: Given the registry → When `getAgent('amazon-q-cli')` is called → Then it returns an entry with `displayName: 'Amazon Q CLI'`, `parentCompany: 'AWS'`, `detectInstalled: 'which q'`, and verified skills dir.

### T-007: Add `zed` entry (parity with specweave/adapters/registry.yaml)
**User Story**: US-005 | **AC**: AC-US5-01, AC-US5-02 | **Status**: [x] completed
**Test Plan**: Given the registry → When `getAgent('zed')` is called → Then it returns `{ id: 'zed', displayName: 'Zed', localSkillsDir: '.zed/skills', detectInstalled: 'which zed', parentCompany: 'Zed Industries' }`.

### T-008: Mark Devin / bolt-new / v0 / replit with `isRemoteOnly: true`
**User Story**: US-004 | **AC**: AC-US4-02 | **Status**: [x] completed
**Test Plan**: Given the registry → When filtering for `isRemoteOnly === true` → Then the result has exactly 4 entries with ids `devin`, `bolt-new`, `v0`, `replit`.

### T-009: Add `getInstallableAgents()` helper
**User Story**: US-004 | **AC**: AC-US4-03 | **Status**: [x] completed
**Test Plan**: Given the registry has 53 entries (49 original + 4 new) and 4 are `isRemoteOnly` → When `getInstallableAgents()` is called → Then the result has 49 entries and none have `isRemoteOnly === true`.

### T-010: Reject install on remote-only agent with typed error
**User Story**: US-004 | **AC**: AC-US4-05 | **Status**: [x] completed
**Test Plan**: Given user invokes `vskill add` against `devin` → When the add command runs → Then it throws/returns an error containing "remote-only" and exits non-zero without writing files.

### T-011: AgentScopePicker renders "Remote" badge for `isRemoteOnly` agents
**User Story**: US-004 | **AC**: AC-US4-04 | **Status**: [x] completed
**Test Plan**: Given a `PickerAgentEntry` with `isRemoteOnly: true` → When `AgentScopePicker` renders → Then a "Remote" badge is in the DOM and the install/active button is hidden or disabled.

### T-012: Integration round-trip — load → resolve install path for all 4 new agents
**User Story**: US-001, US-002, US-003, US-005 | **AC**: AC-US1-03, AC-US2-03, AC-US3-03, AC-US5-01 | **Status**: [x] completed
**Test Plan**: Given the registry → When iterating `['copilot-cli', 'warp', 'amazon-q-cli', 'zed']` and calling the install path resolver in dry-run → Then each returns an absolute path under the agent's expected globalSkillsDir.

### T-013: Detection — simulate `copilot|warp|q` on PATH, assert detection includes them
**User Story**: US-001, US-002, US-003 | **AC**: AC-US1-01, AC-US2-01, AC-US3-01 | **Status**: [x] completed
**Test Plan**: Given `child_process.exec` is mocked so `which copilot`, `which warp`, `which q` succeed → When `detectInstalledAgents()` runs → Then the result includes `copilot-cli`, `warp`, `amazon-q-cli`.

### T-014: Update `vskill-platform/src/lib/agent-branding.ts` featured list (NO-OP unless promoting new agents)
**User Story**: US-001, US-002, US-003 | **AC**: — | **Status**: [x] completed
**Test Plan**: Given the current featured list → When inspecting `agent-branding.ts` → Then either the file is unchanged (deliberate NO-OP, recorded in commit message) OR new agents are added with verified branding metadata. Test asserts the file still parses and exports the expected shape.
**Resolution**: Deliberate NO-OP. The 4 new agents (copilot-cli, warp, amazon-q-cli, zed) are not promoted to the homepage featured 10. FEATURED_AGENTS retains "GitHub Copilot" — note: this string is a marketing display label, not a registry id, so the registry rename to `github-copilot-ext` does not require updating it. Existing tests (`agent-branding.test.ts`) assert shape only and continue to pass.

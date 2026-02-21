# Tasks: 0264 Fix Plugin Scope & Ban Official Plugins

### T-001: Create increment metadata files
**Status**: [x] completed
**Satisfies ACs**: AC-01 (infrastructure)

### T-002: Remove OFFICIAL_PLUGINS from llm-plugin-detector.ts
**Status**: [x] completed
**Satisfies ACs**: AC-02, AC-03, AC-08
**Test**: Given a user prompt mentioning "gitlab" → When LLM detection runs → Then no official plugins returned
- Remove `OFFICIAL_PLUGINS` const (lines 194-216)
- Update `ALL_VALID_PLUGINS = SPECWEAVE_PLUGINS`
- Remove `isOfficialPlugin()`, `OfficialPlugin` type
- Simplify `getPluginMarketplace()` — always returns `'specweave'`
- Remove entire "OFFICIAL PLUGINS" section from `buildDetectionPrompt()`
- Remove `isOfficial` check from `installPluginViaCli()`

### T-003: Fix install_plugin_direct scope (user → project)
**Status**: [x] completed
**Satisfies ACs**: AC-01, AC-07
**Test**: Given plugin auto-detection triggers → When install_plugin_direct runs → Then files land in `.claude/commands/` not `~/.claude/commands/`
- Line 514: change `${HOME}/.claude/commands/${plugin}` → `${SW_PROJECT_ROOT}/.claude/commands/${plugin}`
- Add vskill detection and try `node $VSKILL_BIN install ...` first
- Fall back to direct copy only if vskill not found (with fixed project scope)

### T-004: Remove claude-plugins-official auto-install branch from hook
**Status**: [x] completed
**Satisfies ACs**: AC-04
**Test**: Given detected plugin is not sw-*, → When hook processes it → Then no claude plugin install is called
- Remove the else branch for "NON-SW PLUGINS" (~line 1302-1350 in user-prompt-submit.sh)

### T-005: Fix scope guard to clean up *@claude-plugins-official
**Status**: [x] completed
**Satisfies ACs**: AC-05
**Test**: Given gitlab@claude-plugins-official is in user or project settings → When scope guard runs → Then it is uninstalled and NOT reinstalled
- Update POLLUTED_PLUGINS jq query to match `*@claude-plugins-official` in addition to `sw-*@specweave`
- For official plugin entries: uninstall only, no reinstall
- Also scan and clean project `.claude/settings.json`

### T-006: State cleanup — remove user-level plugin entries
**Status**: [x] completed
**Satisfies ACs**: AC-06
**Test**: Given current state → When cleanup runs → Then ~/.claude/settings.json has no sw-github/sw-jira
- Remove `sw-github@specweave` and `sw-jira@specweave` from `~/.claude/settings.json`
- Verify `.claude/settings.json` no longer has `gitlab@claude-plugins-official` (already done)

### T-007: Update tests
**Status**: [x] completed
**Satisfies ACs**: AC-08
- Remove official plugin assertions from llm-plugin-detector tests
- Add test: gitlab never returned in detection results
- Update integration test mocks that reference OFFICIAL_PLUGINS

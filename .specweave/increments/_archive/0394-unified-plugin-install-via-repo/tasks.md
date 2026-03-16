# Tasks: Unified Plugin Installation via --repo

## Tasks

### T-001: Rewrite install_plugin_via_vskill() to use --repo
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-02

**Description**: Replace the `install_plugin_via_vskill()` function in `user-prompt-submit.sh` (lines 488-522) to use `npx vskill install --repo anton-abyzov/specweave --plugin <name> --agent claude-code --force --yes` instead of `--plugin-dir ~/.claude/plugins/marketplaces/specweave`. Remove the marketplace directory existence check and the fallback to local vskill binary.

**Test Plan**:
- **Given** the `~/.claude/plugins/marketplaces/specweave` directory does not exist
- **When** `install_plugin_via_vskill "sw-github"` is called
- **Then** it runs `npx vskill install --repo anton-abyzov/specweave --plugin sw-github --agent claude-code --force --yes`
- **And** returns 0 on success (output contains "installed")

### T-002: Route docs plugin through specweave repo
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**AC**: AC-US2-03

**Description**: Remove `docs` from the `VSKILL_REPO_PLUGINS` list (line ~527). Add `docs` to the sw-* plugin detection condition at line ~1294 so it routes through `install_plugin_via_vskill()` (which uses `--repo anton-abyzov/specweave`). The condition should be: `if [[ "$plugin" == sw-* ]] || [[ "$plugin" == "sw" ]] || [[ "$plugin" == "docs" ]]; then`.

**Test Plan**:
- **Given** LLM detection returns `docs` as a needed plugin
- **When** the plugin installation branch is entered
- **Then** `install_plugin_via_vskill "docs"` is called (not `install_vskill_repo_plugin`)
- **And** it installs from `--repo anton-abyzov/specweave`

### T-003: Remove stale plugins from VSKILL_REPO_PLUGINS
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**AC**: AC-US2-01, AC-US2-02

**Description**: Remove `k8s`, `cost`, and `docs` from the `VSKILL_REPO_PLUGINS` variable at line ~527. The resulting list should be: `"frontend backend testing mobile infra payments ml kafka confluent security skills blockchain"`.

**Test Plan**:
- **Given** the `VSKILL_REPO_PLUGINS` variable in `user-prompt-submit.sh`
- **When** checking for `k8s`, `cost`, or `docs`
- **Then** `is_vskill_repo_plugin "k8s"` returns 1 (not found)
- **And** `is_vskill_repo_plugin "cost"` returns 1 (not found)
- **And** `is_vskill_repo_plugin "docs"` returns 1 (not found)
- **And** `is_vskill_repo_plugin "frontend"` still returns 0 (found)

### T-004: Update suggest-only mode install command
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] completed
**AC**: AC-US2-04

**Description**: Update the suggest-only mode message at line ~1266 to use `--repo` syntax instead of `--plugin-dir`. Change from:
`npx vskill add ~/.claude/plugins/marketplaces/specweave --plugin <plugin> --plugin-dir ~/.claude/plugins/marketplaces/specweave --force`
To:
`npx vskill install --repo anton-abyzov/specweave --plugin <plugin> --force`

**Test Plan**:
- **Given** `PLUGIN_SUGGEST_ONLY` is true
- **When** plugins are detected for suggestion
- **Then** the output message references `--repo anton-abyzov/specweave`
- **And** does not reference `~/.claude/plugins/marketplaces/specweave`

### T-005: Update startup-health-check.sh
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**AC**: AC-US3-01, AC-US3-02

**Description**: Review and update `startup-health-check.sh` to remove references to `~/.claude/plugins/marketplaces/specweave`. The `SPECWEAVE_DIR` variable at line ~16 and `PLUGINS_SUBDIR` at line ~17 may be used for health checks that are no longer valid. Remove or update these references.

**Test Plan**:
- **Given** `~/.claude/plugins/marketplaces/specweave` does not exist
- **When** `startup-health-check.sh` runs
- **Then** it does not log warnings about missing marketplace directory
- **And** completes without errors

### T-006: Verify scope guard still works
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**AC**: AC-US1-03

**Description**: Verify that the scope guard migration code (lines ~297-304) correctly uses the updated `install_plugin_via_vskill()`. Since it already calls the function by name, the rewrite in T-001 should automatically fix this path. Verify by reading the code after T-001 changes.

**Test Plan**:
- **Given** a sw-* plugin is detected at user scope
- **When** the scope guard runs
- **Then** it calls `install_plugin_via_vskill` which now uses `--repo anton-abyzov/specweave`
- **And** the plugin is reinstalled at project scope

### T-007: Smoke test end-to-end plugin installation
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**AC**: AC-US1-04

**Description**: Run a manual smoke test to verify the updated `install_plugin_via_vskill()` works end-to-end by invoking `npx vskill install --repo anton-abyzov/specweave --plugin sw-github --agent claude-code --force --yes` and confirming it succeeds.

**Test Plan**:
- **Given** npx and vskill are available
- **When** `npx vskill install --repo anton-abyzov/specweave --plugin sw-github --agent claude-code --force --yes` is run
- **Then** the command succeeds with output containing "Installed"
- **And** the sw-github plugin files appear in `~/.claude/commands/sw-github/`

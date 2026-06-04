# Tasks: 0872 refresh-plugins force-sync

### T-001: RED — unit test for syncNativePluginContent
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**AC**: AC-US2-01
**Test Plan**: Given a temp HOME with installed_plugins.json pointing to a stale installPath, a fake specweaveRoot (marketplace.json source=./plugins/specweave + plugins/specweave/{hooks/hooks.json v-new, .claude-plugin/plugin.json vNew}), When syncNativePluginContent runs, Then the installPath gets the current files, a wiped installPath is recreated, and the record version becomes vNew. (Fails RED — function absent.)

### T-002: GREEN — implement syncNativePluginContent
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-04 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-02, AC-US1-04
**Test Plan**: Function copies source→each installPath (recursive, recreate-if-missing) + fixHookPermissions + updates version/lastUpdated; no-op on missing/malformed installed_plugins.json or absent source; never throws. T-001 passes.

### T-003: Wire into refresh-plugins native path
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**AC**: AC-US1-03
**Test Plan**: Given native-cli refresh, When the install loop completes, Then syncNativePluginContent runs per installed plugin and logs `↻ <name>: content synced` on refresh; file-copy/adapter paths unaffected.

### T-004: VERIFY — build + real refresh restores deleted cache file
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**AC**: AC-US2-02
**Test Plan**: Given `npm run build`, When I delete a file from the real cache installPath and run `specweave refresh-plugins`, Then the file is restored and the installPath plugin.json version == global package version. Full unit suite green.

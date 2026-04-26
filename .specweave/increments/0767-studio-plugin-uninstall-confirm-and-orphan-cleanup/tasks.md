# 0767 — Tasks

### T-001: Orphan-cleanup helper (RED)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-04 | **Status**: [x] completed
**Test Plan**: Vitest unit tests in `src/eval-server/plugin-orphan-cleanup.test.ts`.
- Given a tmp cacheRoot with `<mp1>/skill-creator/`, `<mp2>/skill-creator/`, and `<mp1>/other/`
  - When `listOrphanCacheDirs("skill-creator", cacheRoot)`
  - Then it returns the two skill-creator dirs and ignores `other`.
- Given a path-traversal attempt (`name = "../../etc"`)
  - When listing
  - Then it returns []  (resolve check fails).
- Given two dirs returned by `listOrphanCacheDirs`
  - When `removeOrphanCacheDirs([...])`
  - Then both directories are gone, returns `{ removed: 2, failed: [] }`.

### T-002: Orphan-cleanup helper (GREEN)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-04 | **Status**: [x] completed
**Test**: T-001 tests pass.

### T-003: Uninstall route fallback (RED)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Test Plan**: integration test mocking `runClaudePlugin`.
- Given runClaudePlugin returns `{ code: 1, stderr: 'Plugin "x" not found in installed plugins' }` AND tmp cacheRoot has `<mp>/x/`
  - When POST `/api/plugins/x/uninstall`
  - Then response is `{ ok: true, fallback: "orphan-cache-removed", removed: [path] }` and the dir is gone.
- Given same stderr but cacheRoot has no `<mp>/x/` dir
  - When POST `/api/plugins/x/uninstall`
  - Then response is `{ ok: false, code: "claude-cli-failed", error: ... }`.

### T-004: Uninstall route fallback (GREEN)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Test**: T-003 tests pass.

### T-005: PluginActionMenu ConfirmDialog (RED)
**User Story**: US-001, US-002, US-004 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US2-01, AC-US4-01 | **Status**: [x] completed
**Test Plan**: RTL component test in `src/eval-ui/src/components/PluginActionMenu.test.tsx`.
- Given menu open
  - When user clicks "Uninstall"
  - Then ConfirmDialog appears with title "Uninstall <name>?" and destructive variant.
- Given dialog open
  - When user clicks "Cancel"
  - Then dialog closes, no fetch call.
- Given dialog open
  - When user clicks "Uninstall" confirm + fetch resolves ok:true
  - Then a `studio:toast` CustomEvent fires with severity "success" and message "Uninstalled <name>".
- Given fetch resolves ok:false
  - Then `studio:toast` fires with severity "error" carrying the error string.

### T-006: PluginActionMenu ConfirmDialog (GREEN)
**User Story**: US-001, US-002, US-004 | **Satisfies ACs**: AC-US1-01..04, AC-US2-01, AC-US4-01 | **Status**: [x] completed
**Test**: T-005 tests pass.

### T-007: Build + manual verification
**User Story**: US-002, US-003 | **Satisfies ACs**: AC-US2-02, AC-US3-02 | **Status**: [x] completed
**Test**: Build vskill bundle, run `vskill studio` locally, in browser:
- Confirm `skill-creator` plugin shows in sidebar (cached orphan).
- Click `... > Uninstall` → ConfirmDialog appears (beautiful, modal).
- Click Confirm → toast "Uninstalled skill-creator" appears, sidebar refreshes, `skill-creator` is gone.
- `~/.claude/plugins/cache/claude-plugins-official/skill-creator/` no longer exists on disk.

### T-008: MarketplaceDrawer also routed through ConfirmDialog
**User Story**: US-001, US-002, US-004 | **Satisfies ACs**: AC-US1-01..04, AC-US2-01, AC-US4-01 | **Status**: [x] completed
**Test**: Audit revealed a second `window.confirm` for plugin uninstall in `App.tsx` MarketplaceDrawer onUninstall callback. Replaced with the same `<ConfirmDialog>` (destructive variant) gated by a Promise-resolver state pattern; success/failure routed through the existing `useToast()` toast bridge with the same `Removed orphaned <plugin>` / `Uninstalled <plugin>` distinction. Bundle re-built; both occurrences of "Removed orphaned" + "This removes the … plugin" present in dist/eval-ui (sidebar + marketplace surfaces).

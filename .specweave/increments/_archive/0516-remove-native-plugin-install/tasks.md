---
increment: 0516-remove-native-plugin-install
completed_tasks: 3
total_tasks: 3
---

# Tasks: Remove native Claude Code plugin install from vskill

### T-001: RED — Delete claude-cli module and verify compile errors
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test**: Given claude-cli.ts is deleted → When tsc compiles → Then add.ts import errors appear

- [x] Delete `src/utils/claude-cli.ts`
- [x] Delete `src/utils/claude-cli.test.ts`
- [x] Run `npx tsc --noEmit` — confirm import errors in add.ts

---

### T-002: GREEN — Remove all native install code from add.ts and add.test.ts
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US2-01, AC-US2-02, AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test**: Given native code removed → When `npx vitest run` → Then all tests pass

- [x] Remove claude-cli import from add.ts
- [x] Remove `hasClaude` variable (uninstall path)
- [x] Remove `uninstallNativePlugin()` call
- [x] Remove Step 1 native install block (marketplace registration loop)
- [x] Remove `tryNativeClaudeInstall()` function
- [x] Remove `claudeNativeSuccess` branch — set `extractionAgents = selectedAgents`
- [x] Remove `hasClaude && marketplaceRegistered` Claude manage hint
- [x] Remove `gitUrl` extraction (only used by native install)
- [x] Remove misleading `--plugin-dir` native hint
- [x] Remove `vi.mock("../utils/claude-cli.js")` block from add.test.ts
- [x] Remove native install test blocks from add.test.ts
- [x] Run `npx vitest run` — all tests pass (1177/1177)

---

### T-003: Build and verify
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed
**Test**: Given refactor complete → When `npm run build` → Then no TypeScript errors

- [x] Run `npm run build` — no errors
- [x] Verify no references to `claude-cli` remain: `grep -r "claude-cli" src/`

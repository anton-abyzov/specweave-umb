# Tasks: Remove node_modules Specweave Dependency

## Task Notation

- `[ ]`: Not started
- `[x]`: Completed
- `[~]`: In progress

---

## US-001: Replace hardcoded node_modules paths with dynamic resolution

### T-001: Fix scheduler-startup.sh — source resolve-package.sh and repair inline node -e path
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01
**Status**: [x] Completed
**Test**: Given `scheduler-startup.sh` is executed — When the session-sync-executor `node -e` block runs — Then the executor path is resolved via `find_specweave_script "dist/src/core/scheduler/session-sync-executor.js"` (correct `/src/` segment present) and no `node_modules/specweave` reference remains in the file

---

### T-002: Fix ac-sync-dispatcher.sh — replace node_modules candidate with find_specweave_script
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03
**Status**: [x] Completed
**Test**: Given `ac-sync-dispatcher.sh` is inspected — When grepped for `node_modules/specweave` — Then zero matches are found, and the ac-progress-sync path resolves via `find_specweave_script` sourced from `"$HANDLER_DIR/../../lib/resolve-package.sh"`

---

### T-003: Fix universal-auto-create-dispatcher.sh — replace both node_modules candidates
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05
**Status**: [x] Completed
**Test**: Given `universal-auto-create-dispatcher.sh` is inspected — When grepped for `node_modules/specweave` — Then zero matches are found, and both the GitHub handler path and auto-create module path resolve via `find_specweave_script` calls

---

### T-004: Fix dispatcher.mjs — remove node_modules/specweave candidate from findHooksDir()
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04
**Status**: [x] Completed
**Test**: Given `dispatcher.mjs` is inspected — When grepped for `node_modules/specweave` — Then zero matches are found, and `findHooksDir()` candidate list retains only non-node_modules entries

---

### T-005: Verify AC-US1-02 pre-satisfied (post-task-completion.sh)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02
**Status**: [x] Completed
**Test**: Given the plugin source tree is grepped for `node_modules/specweave` in any file matching `*post*task*` or containing `DETECT_CLI` — When the grep runs — Then zero matches are returned, confirming the file was already refactored away

---

## US-002: Remove specweave from umbrella package.json

### T-006: Remove specweave dependency from umbrella package.json and run npm install
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] Completed
**Test**: Given the umbrella `package.json` has `specweave` removed from all dependency sections — When `npm install` completes — Then `node_modules/specweave` does not exist, and running `specweave --version` resolves to the global install

---

## Verification

### T-007: Full grep sweep — confirm zero node_modules/specweave refs in non-archive plugin source
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-03, AC-US1-04, AC-US1-05, AC-US2-01
**Status**: [x] Completed
**Test**: Given all tasks T-001 through T-006 are complete — When `grep -r "node_modules/specweave" repositories/anton-abyzov/specweave/plugins/specweave/hooks/ --include="*.sh" --include="*.mjs"` runs (excluding `_archive/`) — Then exit code is 1 (no matches found)

# Tasks: SpecWeave Doctor Command - Installation Health Scanner

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Core Checker Implementation

### US-001: Ghost Slash Command Detection (P1)

#### T-001: Implement ghost command detection

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04

**Description**: Create `InstallationHealthChecker` class in `src/core/doctor/checkers/installation-health-checker.ts` with `checkGhostCommands()` method. Scan `~/.claude/commands/` recursively for PLUGIN.md, README.md, FRESHNESS.md files. Report each as a warning with full path and plugin name. With `--fix`, delete them.

**Implementation Details**:
- Create new file `src/core/doctor/checkers/installation-health-checker.ts`
- Implement `HealthChecker` interface with `category = 'Installation Health'`
- Constructor accepts optional `commandsDir` and `cacheDir` overrides for testing
- `checkGhostCommands()`: walk `commandsDir` recursively, match files where `shouldSkipFromCommands()` returns true, report each, delete if `fix=true`
- Import `shouldSkipFromCommands` from `../../utils/plugin-copier.js`

**Test Plan**:
- **File**: `tests/unit/core/doctor/checkers/installation-health-checker.test.ts`
- **Tests**:
  - **TC-001**: Ghost detection - clean directory
    - Given a temp commands dir with only SKILL.md files
    - When checkGhostCommands runs
    - Then status is 'pass' with message "no ghost commands"
  - **TC-002**: Ghost detection - PLUGIN.md present
    - Given a temp commands dir with `sw/PLUGIN.md`
    - When checkGhostCommands runs
    - Then status is 'warn' with details listing the file
  - **TC-003**: Ghost detection - README.md nested
    - Given a temp commands dir with `sw/knowledge-base/README.md`
    - When checkGhostCommands runs
    - Then status is 'warn'
  - **TC-004**: Ghost fix mode
    - Given ghost files exist and fix=true
    - When checkGhostCommands runs
    - Then ghost files are deleted and summary is in fixSuggestion

**Dependencies**: None
**Status**: [x] Completed

---

### US-002: Stale Cache Directory Detection (P1)

#### T-002: Implement stale cache directory detection

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [x] completed
**AC**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05

**Description**: Add `checkStaleCacheDirs()` method to `InstallationHealthChecker`. Scan `~/.claude/plugins/cache/` for `temp_local_*` dirs and dirs not referenced in `installed_plugins.json`. Report path and age. With `--fix`, remove only temp_local dirs.

**Implementation Details**:
- Read `~/.claude/plugins/installed_plugins.json` to get referenced cache paths
- List directories in `~/.claude/plugins/cache/` recursively (1 level: marketplace dirs, then plugin dirs)
- Detect `temp_local_*` directories as orphaned
- Compare all cache subdirectories against `installed_plugins.json` entries
- Report unreferenced dirs as warnings (NOT auto-deleted for safety)
- With `--fix`, only remove `temp_local_*` dirs

**Test Plan**:
- **File**: `tests/unit/core/doctor/checkers/installation-health-checker.test.ts`
- **Tests**:
  - **TC-005**: Stale cache - clean state
    - Given cache dir matches installed_plugins.json
    - When checkStaleCacheDirs runs
    - Then status is 'pass'
  - **TC-006**: Stale cache - temp_local present
    - Given cache dir has `temp_local_123_abc/`
    - When checkStaleCacheDirs runs
    - Then status is 'warn' with details about temp dir
  - **TC-007**: Stale cache - fix removes temp_local
    - Given temp_local dir exists and fix=true
    - When checkStaleCacheDirs runs
    - Then temp_local dir is removed
  - **TC-008**: Stale cache - unreferenced dir not auto-deleted
    - Given unreferenced cache dir exists and fix=true
    - When checkStaleCacheDirs runs
    - Then dir still exists (only reported)

**Dependencies**: T-001 (shares the class file)
**Status**: [x] Completed

---

### US-003: Cache-Lockfile Hash Integrity (P1)

#### T-003: Implement lockfile hash integrity check

**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04 | **Status**: [x] completed
**AC**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04

**Description**: Add `checkLockfileIntegrity()` method. Read `vskill.lock` from project root, compute hash of each skill in `~/.claude/commands/<name>/` using `computePluginHash()`, compare with lockfile SHA. Report mismatches as warnings, missing skills as failures.

**Implementation Details**:
- Import `readLockfile`, `computePluginHash` from `../../utils/plugin-copier.js`
- Read lockfile from `projectRoot`
- For each skill entry, compute hash of `commandsDir/<skillName>/`
- Compare with stored SHA
- Report mismatch as warn, missing dir as fail
- With `--fix`, suggest `specweave refresh-plugins` (do not auto-run)

**Test Plan**:
- **File**: `tests/unit/core/doctor/checkers/installation-health-checker.test.ts`
- **Tests**:
  - **TC-009**: Lockfile integrity - matching hashes
    - Given lockfile SHA matches computed hash
    - When checkLockfileIntegrity runs
    - Then status is 'pass'
  - **TC-010**: Lockfile integrity - hash mismatch
    - Given lockfile SHA differs from computed hash
    - When checkLockfileIntegrity runs
    - Then status is 'warn' with both values shown
  - **TC-011**: Lockfile integrity - missing skill directory
    - Given lockfile has skill entry but commands dir is empty
    - When checkLockfileIntegrity runs
    - Then status is 'fail'
  - **TC-012**: Lockfile integrity - no lockfile
    - Given no vskill.lock exists
    - When checkLockfileIntegrity runs
    - Then status is 'skip'

**Dependencies**: T-001 (shares the class file)
**Status**: [x] Completed

---

## Phase 2: Enhancement + Skill

### US-004: Command Namespace Pollution Detection (P2)

#### T-004: Implement namespace pollution detection

**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [x] completed
**AC**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04

**Description**: Add `checkNamespacePollution()` method. Scan `~/.claude/commands/` for `.md` files inside internal directories that `shouldSkipFromCommands()` would filter. Report with the inferred Claude Code command name. With `--fix`, delete them.

**Implementation Details**:
- Walk `commandsDir` recursively, collect all `.md` files
- For each, compute relative path from plugin root, check `shouldSkipFromCommands()`
- If it would be filtered, it's pollution
- Derive the would-be command name (path without .md, colons for separators)
- With `--fix`, delete the file

**Test Plan**:
- **File**: `tests/unit/core/doctor/checkers/installation-health-checker.test.ts`
- **Tests**:
  - **TC-013**: Namespace pollution - clean
    - Given commands dir has only proper SKILL.md and command .md files
    - When checkNamespacePollution runs
    - Then status is 'pass'
  - **TC-014**: Namespace pollution - lib/ contains .md
    - Given `sw/lib/utils.md` exists in commands dir
    - When checkNamespacePollution runs
    - Then status is 'warn' with the would-be command name
  - **TC-015**: Namespace pollution - fix removes files
    - Given pollution files exist and fix=true
    - When checkNamespacePollution runs
    - Then pollution files are deleted

**Dependencies**: T-001 (shares the class file)
**Status**: [x] Completed

---

### US-005: /sw:doctor Skill (P2)

#### T-005: Create /sw:doctor skill SKILL.md

**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04 | **Status**: [x] completed
**AC**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04

**Description**: Create `plugins/specweave/skills/doctor/SKILL.md` with instructions that invoke `specweave doctor` and present results. Support `--fix` pass-through. Handle missing CLI gracefully.

**Implementation Details**:
- Create `plugins/specweave/skills/doctor/SKILL.md` with proper frontmatter
- Skill should run `specweave doctor --verbose` by default
- If user passes `--fix`, add `--fix` flag
- Parse output and present in readable format
- If specweave not found, suggest `npm install -g specweave`

**Dependencies**: T-001 through T-004 (checker must exist for useful output)
**Status**: [x] Completed

---

## Phase 3: Wiring & Integration

#### T-006: Wire InstallationHealthChecker into doctor pipeline

**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: All | **Status**: [x] completed
**AC**: AC-US1-01, AC-US2-01, AC-US3-01, AC-US4-01

**Description**: Add `InstallationHealthChecker` to the checkers array in `doctor.ts`, update `determineFix()`, and re-export from `index.ts`.

**Implementation Details**:
- In `doctor.ts`: import and add `new InstallationHealthChecker()` to checkers array
- In `doctor.ts`: extend `determineFix()` to check for `Installation Health` category issues and suggest `specweave refresh-plugins`
- In `index.ts`: add `export { InstallationHealthChecker } from './checkers/installation-health-checker.js'`

**Test Plan**:
- **File**: `tests/unit/core/doctor/checkers/installation-health-checker.test.ts`
- **Tests**:
  - **TC-016**: Full check() method
    - Given a temp environment with mixed issues
    - When check() runs
    - Then CategoryResult includes checks from all 4 methods
  - **TC-017**: determineFix includes installation health
    - Given installation health issues in report
    - When determineFix runs
    - Then returns "specweave refresh-plugins"

**Dependencies**: T-001 through T-004
**Status**: [x] Completed

---

## Phase 4: Verification

#### T-007: Verify all acceptance criteria

**User Story**: All | **Satisfies ACs**: All | **Status**: [x] completed

**Description**: Run full test suite, verify all ACs, run `specweave doctor` on the real project to validate real-world detection.

**Test Plan**:
- Run `npm run test:unit` for all new tests
- Run `specweave doctor --verbose` on the specweave-umb repo
- Run `specweave doctor --fix` on a disposable test installation
- Verify no false positives on a clean install
- Verify idempotency (run --fix twice, same result)

**Dependencies**: T-001 through T-006
**Status**: [x] Completed

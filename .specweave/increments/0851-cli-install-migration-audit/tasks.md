# Tasks: CLI Install And Migration Audit

### T-001: Baseline Pack Install And Empty Init
**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [x] completed

**Test Plan** (BDD):
- Given a clean temp directory and an isolated npm prefix -> When the local package is packed and installed -> Then `specweave --version`, `specweave --help`, and `specweave init --help` work from the installed binary.
- Given an empty temp folder -> When `specweave init . --quick --adapter generic` runs from the installed binary -> Then `.specweave/`, `repositories/`, config, instruction files, and git state are valid.

### T-002: Baseline Existing Folder And Migration Helpers
**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed

**Test Plan** (BDD):
- Given a temp folder with source files -> When quick init runs -> Then existing files remain in place and the workspace is usable.
- Given a temp local git repo with `.git`, a regular file, and a symlink -> When copy-local helper runs -> Then regular files copy to `repositories/{org}/{repo}/`, `.git` and symlinks are skipped, and errors are deterministic.
- Given a temp non-empty workspace -> When restructure helper runs -> Then only safe entries move and protected entries remain.

### T-003: Baseline Repository Registration
**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-04
**Status**: [x] completed

**Test Plan** (BDD):
- Given a current workspace-schema config and a temp local git repo -> When `specweave get <path>` runs -> Then the repo is registered under workspace repos and repeated runs are idempotent.
- Given a remote-style source and `--no-init` -> When the clone path is exercised with a fixture or mocked clone -> Then target path is `repositories/{owner}/{repo}/` and child init is skipped.

### T-004: Baseline Config Migration And Command Drift
**User Story**: US-001, US-003
**Satisfies ACs**: AC-US1-03, AC-US3-03
**Status**: [x] completed

**Test Plan** (BDD):
- Given a legacy `umbrella`/`multiProject` config fixture -> When a read command runs twice -> Then migration persists once and the second run is quiet.
- Given documented command references and generated next steps -> When CLI help is inspected -> Then references map to real commands or supported aliases.

### T-005: Fix Install, Init, And Help Failures
**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed

**Test Plan** (BDD):
- Given the failures from T-001 and T-004 -> When the package is rebuilt and reinstalled from a fresh tarball -> Then the install/init/help matrix passes.

### T-006: Fix Copy, Restructure, And Get Registration
**User Story**: US-002, US-003
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US3-01, AC-US3-02, AC-US3-04
**Status**: [x] completed

**Test Plan** (BDD):
- Given the failures from T-002 and T-003 -> When the helper and command fixes are applied -> Then the local temp workflows pass without touching real repositories.

### T-007: Fix Config Migration Noise And Planning Artifact Drift
**User Story**: US-003, US-004
**Satisfies ACs**: AC-US3-03, AC-US4-04
**Status**: [x] completed

**Test Plan** (BDD):
- Given a legacy config and an increment created by the CLI -> When migration and increment creation run -> Then migration persists once and generated artifacts obey the project folder rules.

### T-008: Write Test Report
**User Story**: US-004
**Satisfies ACs**: AC-US4-01
**Status**: [x] completed

**Test Plan** (BDD):
- Given all baseline and final verification runs -> When results are gathered -> Then `reports/test-report.md` lists commands, temp paths, failures, fixes, and final status.

### T-009: Full Verification
**User Story**: US-004
**Satisfies ACs**: AC-US4-02
**Status**: [x] completed

**Test Plan** (BDD):
- Given fixes are implemented -> When targeted Vitest suites, `npm run build`, smoke tests, and pack-install matrix run -> Then all blocking checks pass or documented pre-existing failures remain clearly isolated.

### T-010: Push, Deploy Or Publish, And Latest Verification
**User Story**: US-004
**Satisfies ACs**: AC-US4-03, AC-US4-04
**Status**: [ ] pending

**Test Plan** (BDD):
- Given local verification is green -> When the branch is pushed and the configured deploy/publish path runs -> Then a fresh isolated install of the newest published/deployed SpecWeave version verifies the install/init/get workflow.

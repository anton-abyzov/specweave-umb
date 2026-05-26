# 0853 — Tasks

### T-001: Define shared types + registry
**User Story**: US-001, US-002 | **AC**: AC-US1-02, AC-US2-01 | **Status**: [x] completed
**Test Plan**: Given an empty registry, when I call `registerUnit(...)` with two units, then `listUnits().length === 2` and `buildManifest()` returns both ids.
- Files: `scripts/verify-types.mjs`, `scripts/registry.mjs`.

### T-002: Build the runner
**User Story**: US-001, US-004 | **AC**: AC-US1-01, AC-US4-01, AC-US4-02 | **Status**: [x] completed
**Test Plan**: Given a unit whose `act()` throws, when `runFixture` runs, then verdict === "BLOCKED" and `blockedReason` contains the stack. Given a unit with a failing invariant, verdict === "FAIL".
- Files: `scripts/runner.mjs`, `scripts/verifiers/{schema,invariants,filesystem}.mjs`.

### T-003: Build U-INSTALL unit (happy + probe fixtures)
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-03 | **Status**: [x] completed
**Test Plan**: Given the local `fixtures/tiny-skill-source/` plugin, when `vskill install file://.../tiny-skill-source` runs in a tmp `CLAUDE_HOME`, then the install surface lists 1 installed skill with a matching frontmatter name. Probe: install twice — second run reports `idempotent: true` (or matching surface).
- Files: `scripts/units/install.verify.mjs`, `fixtures/tiny-skill-source/**`.

### T-004: Build U-SKILL-NEW unit (happy + probe fixtures)
**User Story**: US-001 | **AC**: AC-US1-01 | **Status**: [x] completed
**Test Plan**: Given a stub LLM (or direct template write — see plan.md risk table), when `vskill skill new` runs, then the emit surface lists 1 SKILL.md with frontmatter `name` matching the prompt slug. Probe: re-emit with same prompt — divergence report is empty.
- Files: `scripts/units/skill-new.verify.mjs`.

### T-005: CLI entry — run-verify.mjs
**User Story**: US-001, US-003 | **AC**: AC-US1-01, AC-US1-02, AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test Plan**: When `node scripts/run-verify.mjs` runs, then exits 0, prints a grid, writes `reports/verify-result.json`, writes `.specweave/state/verify-current.json` atomically (via tmp+rename).
- Files: `scripts/run-verify.mjs`.

### T-006: CI matrix entry — matrix.test.mjs
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test Plan**: Given a unit without any `probe: true` fixture, when `node --test matrix.test.mjs` runs, then test fails with message `"Unit X has no probe fixtures — only happy path is covered."`.
- Files: `scripts/matrix.test.mjs`.

### T-007: Run the harness end-to-end, capture real artifacts
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test Plan**: Execute T-005, paste the actual grid output + the relevant JSON keys + the produced file paths into `reports/run-log.md`.
- Files: `reports/run-log.md`, `reports/verify-result.json`.

### T-008: (optional, only if T-001..T-007 pass cleanly) Document the pattern as ADR
**User Story**: — | **Status**: [x] completed
**Test Plan**: Manual review — does another developer read this and understand how to add a third unit?
- Files: `.specweave/docs/internal/architecture/adr/0853-verify-runtime-pattern.md`.

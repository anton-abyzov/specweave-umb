# Make TDD fully optional

## Problem

The user asked on October 24, 2026 whether SpecWeave forces TDD and said it must be completely optional.

Audit of `specweave` 3.1.9 (`develop` at `511ff2cf1`): `DEFAULT_CONFIG` and `init` already write no test mode or coverage target, and no hook blocks on test order. The leftovers still imply a test policy nobody chose:

- `src/core/increment/metadata-manager.ts:945-953` writes `testMode: "test-after"` and `coverageTarget: 80` into every increment's `metadata.json` on read.
- `src/core/increment/completion-validator.ts:222` defaults a missing `testMode` to `TDD`, then falls back to that metadata `coverageTarget` (80) and warns "Test coverage below target" at close when a coverage report exists, although `testing.coverage` is unset. The docs say coverage is "not set" unless the user sets it.
- `src/core/rubric/rubric-generator.ts:45` adds an R-D01 "coverage >= 90%" criterion to every generated rubric.
- The packaged editor schema `src/core/schemas/specweave-config.schema.json` still describes "TDD mode", ships `tddEnforcement` (default `warn`, "strict blocks GREEN without RED") and other removed 1.x keys, and rejects the real 2.0 keys `testing.mode`, `testing.commands`, `testing.coverage`.
- `skills/sw-do/SKILL.md:28` says "Don't write tests first", which forbids TDD for users who want it instead of leaving the order to them.
- `enforceTestFirst` in `src/core/auto/` is read and never used.

## Scope

In: remove the implied defaults above, make coverage and test order apply only when the user opts in (`testing.mode`, `testing.coverage`, the task, or project conventions), align the schema with the 2.0 config, neutral skill wording, docs line. Out: `specweave verify` and task `Test` commands (normal verification stays), the opt-in `specweave auto` TDD/requireTests criterion, rewriting existing increments' metadata.

## Acceptance Criteria

- [ ] AC-01: Reading or creating an increment no longer writes `testMode` or `coverageTarget` into `metadata.json`.
- [ ] AC-02: Closing an increment with no `testing.coverage` configured never warns about coverage, even when a coverage report exists and old metadata carries `coverageTarget: 80`; with `testing.coverage.unit` set, a shortfall still warns as before.
- [ ] AC-03: A generated rubric has no coverage criterion unless a coverage target is configured.
- [ ] AC-04: The packaged config schema accepts `testing.mode`, `testing.commands` and `testing.coverage`, and no longer declares `tddEnforcement` or other removed testing keys.
- [ ] AC-05: Generated skills and docs state test-first order is optional (used only when the user, `testing.mode: TDD` or project conventions ask), and the dead `enforceTestFirst` option is gone.

## Approach

Stop the metadata auto-correct from inventing `testMode`/`coverageTarget`. In the completion validator, take the coverage target only from `testing.coverage.unit` (the documented opt-in) and the mode from `testing.mode`, then `metadata.testMode`, else `test-after`; never default to TDD. `generate-rubric` passes the configured target; the generator omits R-D01 without one. Replace the schema's testing block with the 2.0 shape. Reword sw-do step 4 and regenerate plugin skills. Rejected: keeping metadata `coverageTarget` as a fallback, because the auto-correct already stamped 80 into existing increments and that value can't be told apart from a user choice.

## Decisions

### Asked
- D-01 Should TDD be enforced by default → no, completely optional (user, October 24, 2026)
### Defaulted (change any before sw-do)
- D-02 Existing increments keep their stamped `coverageTarget`; it is ignored instead of rewritten (reversible).
### Open
- none

## Tasks

### T-01 Stop stamping test defaults into metadata
- AC: AC-01 | Files: src/core/increment/metadata-manager.ts, tests/unit/core/increment/metadata-no-test-defaults.test.ts | Test: cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave && npx vitest run tests/unit/core/increment/metadata-no-test-defaults.test.ts

### T-02 Coverage check only on configured target, no TDD default
- AC: AC-02 | Files: src/core/increment/completion-validator.ts, tests/unit/core/increment/completion-validator-coverage.test.ts, tests/unit/increment/completion-validator.test.ts | Test: cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave && npx vitest run tests/unit/core/increment/completion-validator-coverage.test.ts tests/unit/increment/completion-validator.test.ts

### T-03 Rubric coverage criterion only when configured
- AC: AC-03 | Files: src/core/rubric/rubric-generator.ts, src/core/rubric/rubric-generator-parity.test.ts, src/cli/commands/generate-rubric.ts, tests/unit/core/rubric/rubric-generator.test.ts | Test: cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave && npx vitest run tests/unit/core/rubric src/core/rubric

### T-04 Align config schema testing block with 2.0
- AC: AC-04 | Files: src/core/schemas/specweave-config.schema.json, tests/unit/workspace-adoption/schema.test.ts | Test: cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave && npx vitest run tests/unit/workspace-adoption/schema.test.ts

### T-05 Neutral skill and docs wording, drop enforceTestFirst
- AC: AC-05 | Files: skills/sw-do/SKILL.md, plugins/specweave/skills, src/core/auto/types.ts, src/core/auto/config.ts, docs-site/docs/reference/configuration.md, tests/unit/config-test-mode.test.ts (deleted: it simulated a TDD default and tested no product code) | Test: cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave && npm run generate:skills && ! grep -rn "Don't write tests first\|enforceTestFirst" skills plugins/specweave/skills src

### T-06 Verify and close 1062
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: .specweave/increments/1062-make-tdd-fully-optional | Test: cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave && npx tsc --noEmit -p . && npm run test:unit

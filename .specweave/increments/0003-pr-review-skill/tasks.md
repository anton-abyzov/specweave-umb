---
increment: 0003-pr-review-skill
title: "Enhanced Multi-Dimensional PR Review Skill"
status: active
by_user_story:
  US-001: [T-001]
  US-002: [T-002]
  US-003: [T-003, T-004]
---

# Tasks: Enhanced Multi-Dimensional PR Review Skill

**Base directory**: `repositories/Colibri-Group-AI/claude-skills-registry`

---

## User Story: US-001 - Multi-Dimensional PR Review

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Tasks**: 1 total, 1 completed

### T-001: Create skills/pr-review/SKILL.md with all 7 dimensions

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** a new `skills/pr-review/SKILL.md` file
- **When** the file is read and reviewed for structure
- **Then** it contains frontmatter, all 7 dimension sections, a dimension applicability matrix, confidence scoring rules (suppress <80, Important 80-89, Critical 90-100), and the output format template

**Test Cases**:
1. **Manual content check**: `skills/pr-review/SKILL.md`
   - Verify 7 section headers present: Code Quality, Type Design, Error Handling, Test Coverage, Comment Analysis, Code Simplification, Infrastructure & Security
   - Verify confidence threshold rules (80/90 boundaries) appear in the scoring section
   - Verify applicability matrix table covers `.ts`, `.test.ts`, `.tf`, `Dockerfile`, `.md` rows
   - Verify output template includes per-dimension score table and Critical/Important finding groups
   - **Coverage Target**: 100% of ACs (all 4 AC-US1-xx items verified by inspection)

2. **Line count check**:
   - File must be under 800 lines (per spec constraint)
   - Each dimension section must be present and delimited

**Implementation**:
1. Create directory `skills/pr-review/` and `skills/pr-review/evals/`
2. Write `skills/pr-review/SKILL.md` following the internal structure from plan.md:
   - Lines 1-15: Frontmatter (name, description, triggers, tools)
   - Lines 16-40: Role definition and activation rules
   - Lines 41-60: PR identifier parsing
   - Lines 61-80: Size assessment and depth tier selection (4 tiers: <200, 200-500, 500-1500, >1500)
   - Lines 81-100: Dimension applicability matrix table (CQ, TD, EH, TC, CA, CS, IS)
   - Lines 101-115: Confidence scoring framework (Critical 90-100, Important 80-89, suppress <80)
   - Lines 116-135: Data gathering steps (gh CLI commands)
   - Lines 136-215: Dimension 1 - Code Quality
   - Lines 216-295: Dimension 2 - Type Design
   - Lines 296-375: Dimension 3 - Error Handling
   - Lines 376-450: Dimension 4 - Test Coverage
   - Lines 451-510: Dimension 5 - Comment Analysis
   - Lines 511-575: Dimension 6 - Code Simplification
   - Lines 576-680: Dimension 7 - Infrastructure & Security
   - Lines 681-730: Output format template
   - Lines 731-770: Edge cases and special handling
   - Lines 771-800: Verdict framework and composite scoring
3. Verify file line count is under 800

---

## User Story: US-002 - Colibri Stack-Specific Review Patterns

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Tasks**: 1 total, 1 completed

### T-002: Embed Colibri-specific patterns in SKILL.md dimensions

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed

**Test Plan**:
- **Given** the completed `skills/pr-review/SKILL.md`
- **When** each dimension section is read for Colibri-specific content
- **Then** Infra & Security covers AWS/Docker/Terraform/Keycloak patterns, Error Handling covers Pino/Helmet/Zod/OpenTelemetry, and Test Coverage covers Vitest/.test.ts/TypeScript strict conventions

**Test Cases**:
1. **Manual content check**: `skills/pr-review/SKILL.md`
   - AC-US2-01: Infra & Security dimension contains: "Secrets Manager", "least-privilege IAM", "ECS task role", "multi-stage", "non-root USER", "state locking", "hardcoded ARNs", "JWKS", "realm-scoped"
   - AC-US2-02: Error Handling and Code Quality sections contain: "Pino", "Helmet", "Zod", "OpenTelemetry"
   - AC-US2-03: Test Coverage and Type Design sections contain: "Vitest", ".test.ts", "strict mode", "consistent-type-imports"
   - **Coverage Target**: 100% of Colibri pattern keywords verified present

**Implementation**:
1. This task is delivered as part of T-001 (SKILL.md authoring) -- the Colibri patterns are embedded within dimension sections during SKILL.md creation
2. After T-001 is complete, grep SKILL.md for each required keyword to confirm AC-US2-xx coverage:
   - `grep -i "secrets manager\|least-privilege\|ecs task\|multi-stage\|non-root\|state locking\|hardcoded arn\|jwks\|realm-scoped" SKILL.md`
   - `grep -i "pino\|helmet\|zod\|opentelemetry" SKILL.md`
   - `grep -i "vitest\|\.test\.ts\|strict mode\|consistent-type-imports" SKILL.md`
3. Mark complete once all patterns confirmed present

---

## User Story: US-003 - Clean Migration from github-pr-review to pr-review

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Tasks**: 2 total, 2 completed

### T-003: Create evals/evals.json with 12 test cases

**User Story**: US-003
**Satisfies ACs**: AC-US3-03
**Status**: [x] completed

**Test Plan**:
- **Given** `skills/pr-review/evals/evals.json` is created
- **When** test cases are counted and categorized
- **Then** there are exactly 12 cases: 8 positive (one per dimension plus multi-dimension) and 4 negative (binary diff, empty diff, docs-only, confidence-below-threshold)

**Test Cases**:
1. **Manual count check**: `skills/pr-review/evals/evals.json`
   - Count total cases: must be >= 12
   - Count positive cases (type "positive"): must be >= 8
   - Count negative cases (type "negative"): must be >= 4
   - Each positive case maps to a distinct dimension trigger
   - Negative cases cover: binary-only diff, empty diff, docs-only (README), style-only findings
   - Verify JSON validity: `jq . evals.json` exits 0
   - **Coverage Target**: 100% (all 12 case types per AC-US3-03)

**Implementation**:
1. Create `skills/pr-review/evals/evals.json` matching the eval file structure used elsewhere in the registry
2. Write 8 positive cases:
   - Case 1: TS file with long functions, no error handling → Code Quality fires
   - Case 2: TS file with `any` types, missing generics → Type Design fires
   - Case 3: Express route without try-catch → Error Handling fires
   - Case 4: New module with zero test files → Test Coverage fires
   - Case 5: Docs-only PR → Comment Analysis fires (only dimension)
   - Case 6: Deeply nested conditionals → Code Simplification fires
   - Case 7: Terraform with hardcoded ARNs → Infrastructure & Security fires
   - Case 8: Full-stack PR (code + tests + infra) → multi-dimension, 4+ dimensions fire
3. Write 4 negative cases:
   - Case 9: Binary file changes only → zero code dimensions fire, output "No actionable code changes"
   - Case 10: Empty diff → skill outputs appropriate no-changes message
   - Case 11: README.md only → only Comment Analysis fires, no code dimensions
   - Case 12: Style-only nits (function naming, whitespace) → all findings score <80, output empty after suppression
4. Verify JSON is valid: `jq . evals.json`

### T-004: Delete github-pr-review directory and update all cross-references

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02
**Status**: [x] completed

**Test Plan**:
- **Given** the migration tasks are executed
- **When** the `skills/` directory is listed and all registry files are searched for "github-pr-review"
- **Then** `skills/github-pr-review/` does not exist and zero matches for "github-pr-review" are found in the entire repository

**Test Cases**:
1. **Directory check**:
   - `ls skills/github-pr-review/` → must return "No such file or directory"
   - `ls skills/pr-review/SKILL.md` → must exist
   - **Coverage Target**: 100% (AC-US3-01 binary pass/fail)

2. **Zero-reference grep**:
   - `grep -r "github-pr-review" . --include="*.md" --include="*.json" --include="*.sh" --include="*.bat"` → must return 0 matches
   - All 10 known cross-reference files updated: README.md, CHANGELOG.md, QUICKSTART.md, install.sh, install.bat, skills/professionalize/evals/evals.json, skills/prd-questions/evals/evals.json, skills/github-repo-review/evals/evals.json
   - **Coverage Target**: 100% (AC-US3-02 verified by zero-match grep)

**Implementation**:
1. Delete `skills/github-pr-review/` directory entirely (`rm -rf skills/github-pr-review/`)
2. Update `README.md`: replace all "github-pr-review" references with "pr-review"
3. Update `CHANGELOG.md`: add migration entry noting rename from github-pr-review to pr-review
4. Update `QUICKSTART.md`: replace skill name references
5. Update `install.sh`: replace directory references
6. Update `install.bat`: replace directory references
7. Update `skills/professionalize/evals/evals.json`: fix cross-skill references
8. Update `skills/prd-questions/evals/evals.json`: fix cross-skill references
9. Update `skills/github-repo-review/evals/evals.json`: fix cross-skill references
10. Run verification: `grep -r "github-pr-review" . --include="*.md" --include="*.json" --include="*.sh" --include="*.bat"` → confirm zero matches

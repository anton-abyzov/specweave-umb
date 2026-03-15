# Architecture Plan: Enhanced Multi-Dimensional PR Review Skill

## Context

This increment replaces `skills/github-pr-review/SKILL.md` (623 lines, flat monolithic reviewer) with `skills/pr-review/SKILL.md` (~800 lines, 7-dimension structured reviewer). The deliverable is a single SKILL.md file plus eval cases and cross-reference updates -- not a traditional software system.

## Decision 1: Sequential Dimension Framework (Not Agents)

**Decision**: Structure the 7 review dimensions as sequential sections within a single SKILL.md, forming a mental checklist the LLM walks through. No sub-agents, no parallel processing, no external orchestration.

**Rationale**: Claude Code skills are prompt documents, not executable code. The LLM reads the entire SKILL.md into context and follows its instructions linearly. A "multi-agent" design would require tool orchestration infrastructure that does not exist in the skill format. Sequential sections give the LLM a clear walkthrough order and allow early dimensions (Code Quality) to inform later ones (Code Simplification).

**Dimension execution order** (dependency-aware):
1. Code Quality -- foundational, informs all others
2. Type Design -- caught early, shapes error handling analysis
3. Error Handling -- depends on type awareness
4. Test Coverage -- needs code quality + error handling context
5. Comment Analysis -- assesses documentation of above findings
6. Code Simplification -- holistic, needs full picture
7. Infrastructure & Security -- independent but benefits from full context

**Section structure per dimension** (~80-100 lines each):
```
## Dimension N: [Name]
### What This Dimension Checks
### Scoring Rubric (0-100)
### File Type Triggers (from applicability matrix)
### Patterns to Flag
### Colibri-Specific Patterns (conditional)
### Output Template
```

## Decision 2: Dimension Applicability Matrix

**Decision**: Embed a lookup table at the top of the review flow that maps file extensions and change patterns to active dimensions. The LLM consults this before running each dimension.

**Design**:
```
| File Pattern          | CQ | TD | EH | TC | CA | CS | IS |
|-----------------------|----|----|----|----|----|----|----|
| *.ts, *.js            | Y  | Y  | Y  | -  | Y  | Y  | -  |
| *.test.ts, *.test.js  | Y  | -  | -  | Y  | Y  | -  | -  |
| *.tf, *.hcl           | -  | -  | -  | -  | Y  | -  | Y  |
| Dockerfile, *.yml     | -  | -  | -  | -  | Y  | -  | Y  |
| *.md, *.json (config) | -  | -  | -  | -  | Y  | -  | -  |
| *.css, *.scss          | -  | -  | -  | -  | Y  | Y  | -  |
```

**Key**: CQ=Code Quality, TD=Type Design, EH=Error Handling, TC=Test Coverage, CA=Comment Analysis, CS=Code Simplification, IS=Infrastructure & Security.

**Rule**: A dimension activates if ANY changed file matches its trigger. `-` means dimension is skipped entirely for that file type but may still fire from another file in the same PR.

**Edge case**: PR with only non-code files (images, docs) -- only Comment Analysis activates. If no dimension produces findings, output "No actionable code changes to review."

## Decision 3: Confidence Scoring Integration

**Decision**: Each finding carries a confidence score (0-100). The skill instructs the LLM to self-assess confidence based on explicit criteria, then filters output.

**Scoring criteria embedded in skill**:
- **90-100 (Critical)**: Pattern is unambiguous (e.g., hardcoded secret, missing error handler on async call, SQL injection). Show with `CRITICAL` label.
- **80-89 (Important)**: High likelihood of issue but context-dependent (e.g., missing test for new function, overly broad type). Show with `IMPORTANT` label.
- **0-79**: Suppressed from output entirely. Not shown to the developer.

**Implementation in SKILL.md**: Each dimension's "Patterns to Flag" section includes confidence guidance:
```
- Hardcoded AWS credentials -> confidence: 95 (unambiguous security violation)
- Function longer than 50 lines -> confidence: 70 (style preference, SUPPRESS)
- Missing error boundary in React component -> confidence: 82 (important but context-dependent)
```

**Threshold is hardcoded at 80**: No configuration knob. This keeps the skill self-contained and avoids the LLM needing to parse external config.

## Decision 4: Output Format Design

**Decision**: Structured markdown output with per-dimension scores, severity-grouped findings, and a composite summary. Written to `pr-review-{repo}-{pr}.md`.

**Output structure**:
```markdown
# PR Review: [Title]
**PR**: #N | **Author**: X | **Dimensions**: N/7 active

## Dimension Scores
| Dimension            | Score | Findings |
|----------------------|-------|----------|
| Code Quality         | 85    | 2        |
| Type Design          | 92    | 1        |
| ...                  | ...   | ...      |
| **Composite**        | **87**| **total**|

## Critical Findings (confidence >= 90)
### [DIM-CQ-001] Missing null check in parseUser()
...

## Important Findings (confidence 80-89)
### [DIM-EH-001] Unhandled promise rejection in fetchData()
...

## Dimension Summaries
### Code Quality (85/100)
One-line summary of this dimension's assessment.
...

## Verdict
**Recommendation**: Approve | Request Changes | Needs Discussion
```

**Finding IDs**: `DIM-{dimension abbreviation}-{sequence}` (e.g., `DIM-IS-003` for the 3rd Infrastructure & Security finding). Enables referencing specific findings in PR comments.

## Decision 5: Size-Adaptive Depth Strategy

**Decision**: Scale review depth based on PR size, measured by total changed lines (additions + deletions).

| PR Size       | Lines Changed | Depth Strategy |
|---------------|---------------|----------------|
| Small         | < 200         | Line-by-line analysis, all dimensions at full depth |
| Medium        | 200-500       | Function-level analysis, full dimensions |
| Large         | 500-1500      | File-level analysis, focus on high-risk dimensions |
| Extra-Large   | > 1500        | Architecture-level only, top 3 dimensions by risk, suggest splitting |

**Implementation**: The SKILL.md includes a "Size Assessment" step early in the flow. The LLM counts changed lines from `gh pr view --json additions,deletions`, then selects the depth tier. Each dimension section includes conditional instructions: "For Large+ PRs, skip pattern X and focus on pattern Y."

**Change from existing skill**: Current skill uses 4 tiers (< 100, 100-500, 500-1000, > 1000). New thresholds are shifted up because the dimension-based approach naturally filters noise, making deeper analysis practical on slightly larger PRs.

## Decision 6: Colibri Patterns as Conditional Sections

**Decision**: Embed Colibri-specific patterns inside each relevant dimension, gated by tech-stack detection from the PR diff content. Not a separate "Colibri mode" toggle.

**Detection heuristic** (instructed in SKILL.md):
```
IF diff contains any of: package.json with "express", "pino", "@hapi",
   Dockerfile, *.tf files, keycloak references, aws-sdk imports,
   vitest.config, .env with AWS_ prefixes
THEN activate Colibri-specific patterns within each dimension
```

**Colibri patterns per dimension**:

| Dimension | Colibri-Specific Checks |
|-----------|------------------------|
| Code Quality | Pino structured logging (no console.log), Helmet middleware, Zod validation |
| Type Design | TypeScript strict mode, consistent-type-imports, no `any` escape hatches |
| Error Handling | Express error middleware chain, async handler wrapping, Pino error serialization |
| Test Coverage | Vitest with `.test.ts` convention, vi.mock() patterns, coverage thresholds |
| Comment Analysis | (no Colibri-specific additions) |
| Code Simplification | (no Colibri-specific additions) |
| Infrastructure & Security | AWS Secrets Manager over env vars, least-privilege IAM, ECS task role separation, Docker multi-stage + non-root USER, Terraform state locking + no hardcoded ARNs, Keycloak JWKS validation + realm-scoped client checks |

**Rationale for conditional embedding over separate config**: The skill must be a single self-contained SKILL.md. Colibri patterns are woven into the dimension text with "If Colibri stack detected:" prefixes. For non-Colibri repos, these sections are simply skipped by the LLM.

## File Layout (Post-Migration)

```
skills/
  pr-review/                    # NEW directory
    SKILL.md                    # ~800 lines, 7-dimension reviewer
    evals/
      evals.json                # 12+ test cases (8 positive, 4 negative)
  github-pr-review/             # DELETED entirely
```

**Cross-reference update targets** (10 files found referencing "github-pr-review"):
1. `README.md` -- skill listing and description
2. `CHANGELOG.md` -- add migration entry
3. `QUICKSTART.md` -- update skill name
4. `install.sh` -- update skill directory reference
5. `install.bat` -- update skill directory reference
6. `skills/professionalize/evals/evals.json` -- cross-skill reference
7. `skills/prd-questions/evals/evals.json` -- cross-skill reference
8. `skills/github-repo-review/evals/evals.json` -- cross-skill reference
9. `skills/github-pr-review/evals/evals.json` -- replaced by new evals
10. `skills/github-pr-review/SKILL.md` -- replaced by new SKILL.md

## SKILL.md Internal Structure (~800 lines target)

```
Lines 1-15:     Frontmatter (name, description, triggers, tools)
Lines 16-40:    Role definition and activation rules
Lines 41-60:    PR identifier parsing (preserved from existing)
Lines 61-80:    Size assessment and depth tier selection
Lines 81-100:   Dimension applicability matrix (table)
Lines 101-115:  Confidence scoring framework
Lines 116-135:  Data gathering steps (gh CLI commands)
Lines 136-215:  Dimension 1: Code Quality
Lines 216-295:  Dimension 2: Type Design
Lines 296-375:  Dimension 3: Error Handling
Lines 376-450:  Dimension 4: Test Coverage
Lines 451-510:  Dimension 5: Comment Analysis
Lines 511-575:  Dimension 6: Code Simplification
Lines 576-680:  Dimension 7: Infrastructure & Security (largest, Colibri-heavy)
Lines 681-730:  Output format template
Lines 731-770:  Edge cases and special handling
Lines 771-800:  Verdict framework and composite scoring
```

## Eval Test Case Design (12 cases)

**Positive cases (8)**:
1. Code Quality dimension -- TS file with long functions, no error handling
2. Type Design dimension -- TS file with `any` types, missing generics
3. Error Handling dimension -- Express route without try-catch
4. Test Coverage dimension -- new module with zero test files
5. Comment Analysis dimension -- docs-only PR
6. Code Simplification dimension -- deeply nested conditionals
7. Infrastructure & Security dimension -- Terraform with hardcoded ARNs
8. Multi-dimension case -- full-stack PR touching code, tests, infra

**Negative cases (4)**:
9. Irrelevant diff -- binary file changes only
10. Empty diff -- PR with no file changes
11. Non-code file -- only README.md changes (only Comment Analysis should fire)
12. Confidence-below-threshold -- style-only findings that should be suppressed

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| SKILL.md exceeds 800 lines | Each dimension budgeted at ~80 lines; Infra & Security gets 105. Monitor during implementation. |
| LLM ignores confidence thresholds | Embed concrete examples per dimension showing which patterns score below 80 and must be suppressed. |
| Colibri detection false positives | Use conjunction: require 2+ signals (e.g., pino + express, not just express alone) before activating Colibri patterns. |
| Cross-reference update misses a file | Exhaustive grep already identified 10 files. Verification task runs grep post-migration to confirm zero matches. |

## Implementation Sequence

1. **Write SKILL.md** -- the core deliverable (addresses US-001, US-002)
2. **Write evals.json** -- 12 test cases (addresses AC-US3-03)
3. **Delete old directory** -- remove `skills/github-pr-review/` (addresses AC-US3-01)
4. **Update cross-references** -- all 10 files (addresses AC-US3-02)
5. **Verification** -- grep for zero remaining "github-pr-review" references

## No Domain Skill Delegation Needed

This increment produces markdown files (SKILL.md, evals.json, registry docs). There is no frontend, backend, or infrastructure code to implement. No domain-specific architect skills (frontend:architect, backend:*) are applicable.

---
increment: 0003-pr-review-skill
title: Enhanced Multi-Dimensional PR Review Skill
status: completed
priority: P1
type: feature
created: 2026-03-13T00:00:00.000Z
---

# Enhanced Multi-Dimensional PR Review Skill

## Problem Statement

The current `github-pr-review` skill in the claude-skills-registry is a monolithic 623-line single-pass reviewer that produces flat, undifferentiated feedback. It lacks structured scoring, dimension-specific analysis, and Colibri stack awareness. Developers receive noisy reviews where minor style nits sit alongside critical security findings, making it hard to prioritize action items.

## Goals

- Replace the monolithic reviewer with a 7-dimension structured review that scores and filters findings by confidence
- Embed Colibri-specific patterns (AWS, Express, Keycloak, Pino, Vitest) so reviews reflect the actual stack
- Clean-migrate from `github-pr-review` to `pr-review` with all cross-references updated

## User Stories

### US-001: Multi-Dimensional PR Review (P0)
**Project**: claude-skills-registry
**As a** developer requesting a PR review
**I want** structured feedback across 7 review dimensions with confidence scoring
**So that** I can focus on high-impact findings and skip noise

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a SKILL.md file, when reviewed for content, then it contains all 7 review dimensions (Code Quality, Test Coverage, Error Handling, Type Design, Comment Analysis, Code Simplification, Infrastructure & Security) each with its own scoring framework
- [x] **AC-US1-02**: Given a review finding, when its confidence score is below 80, then the finding is suppressed from output; when 80-89 it appears as "Important"; when 90-100 it appears as "Critical"
- [x] **AC-US1-03**: Given a PR diff, when the skill selects applicable dimensions, then it uses a dimension applicability matrix that maps file types and change patterns to relevant dimensions (e.g., .tf files trigger Infrastructure, .test.ts files trigger Test Coverage)
- [x] **AC-US1-04**: Given a completed review, when the output is rendered, then each applicable dimension has a numeric score (0-100), severity-grouped findings (Critical then Important), and a one-line summary

---

### US-002: Colibri Stack-Specific Review Patterns (P1)
**Project**: claude-skills-registry
**As a** developer working on Colibri services
**I want** the reviewer to understand our AWS/Express/Keycloak stack conventions
**So that** reviews catch stack-specific anti-patterns instead of giving generic advice

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given the Infrastructure & Security dimension definition, when reviewed for coverage, then it includes patterns for AWS (Secrets Manager over env vars, least-privilege IAM, ECS task role separation), Docker (multi-stage builds, non-root USER), Terraform (state locking, no hardcoded ARNs), and Keycloak (JWKS validation, realm-scoped client checks)
- [x] **AC-US2-02**: Given the Error Handling and Code Quality dimension definitions, when reviewed for backend patterns, then they reference Pino structured logging, Helmet middleware, Zod schema validation, and OpenTelemetry span conventions
- [x] **AC-US2-03**: Given the Test Coverage and Type Design dimension definitions, when reviewed for frontend patterns, then they reference Vitest with `.test.ts` file convention, TypeScript strict mode, and `consistent-type-imports` ESLint rule

---

### US-003: Clean Migration from github-pr-review to pr-review (P0)
**Project**: claude-skills-registry
**As a** registry maintainer
**I want** a clean migration that removes the old skill directory and updates all references
**So that** the registry has no stale pointers or broken cross-references

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given the migration is complete, when the `skills/` directory is listed, then `skills/github-pr-review/` does not exist and `skills/pr-review/SKILL.md` exists with the new content
- [x] **AC-US3-02**: Given the migration is complete, when all registry files are searched for "github-pr-review", then zero matches are found; all references in README.md, CHANGELOG.md, install scripts, QUICKSTART.md, and cross-skill eval files point to "pr-review"
- [x] **AC-US3-03**: Given the evals directory for pr-review, when eval test cases are counted, then there are at least 12 cases: 8 positive cases (one per dimension plus a multi-dimension case) and 4 negative cases (irrelevant diff, empty diff, non-code file, confidence-below-threshold)

## Out of Scope

- Automated CI integration (GitHub Actions workflow for review triggering)
- Web UI or dashboard for review results
- Review memory across PRs (learning from past reviews)
- Multi-repo PR review in a single pass
- Custom dimension authoring by end users

## Technical Notes

### Dependencies
- `gh` CLI for PR diff fetching (preserved from existing skill)
- Claude Code skill system (`~/.claude/skills/` installation path)

### Constraints
- SKILL.md must remain a single file (Claude Code skill format requirement)
- Skill must work offline against local diffs when `gh` is unavailable
- No external API calls beyond `gh` CLI

### Architecture Decisions
- Single SKILL.md file containing all 7 dimensions rather than modular includes (skill format constraint)
- Confidence threshold hardcoded at 80 (not configurable) to keep the skill self-contained
- Dimension applicability matrix embedded in the skill rather than external config

## Non-Functional Requirements

- **Performance**: Skill file loads in a single read; no multi-file resolution needed
- **Compatibility**: Works with any GitHub-hosted repo accessible via `gh` CLI; also works with local `git diff` output
- **Maintainability**: Each dimension is a clearly delimited section in SKILL.md so individual dimensions can be updated independently
- **Security**: Skill never stores or transmits PR content beyond the current Claude Code session

## Edge Cases

- PR with only non-code files (e.g., docs, images): Dimension matrix selects zero code dimensions; skill outputs "No code changes to review" with Comment Analysis as the only applicable dimension
- PR exceeding 2000 lines: Skill applies size-adaptive depth (summary mode for large PRs, line-by-line for small)
- PR touching only test files: Only Test Coverage and Code Quality dimensions activate
- PR with no test changes alongside code changes: Test Coverage dimension flags missing test coverage with high confidence

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| SKILL.md exceeds practical token limit for Claude context | 0.3 | 7 | 2.1 | Keep each dimension concise; target under 800 lines total |
| Confidence scoring too aggressive, suppressing valid findings | 0.4 | 5 | 2.0 | Calibrate with 12 eval test cases; adjust threshold if >20% false negatives |
| Cross-reference update misses an obscure file | 0.2 | 3 | 0.6 | Use grep-based exhaustive search for "github-pr-review" across entire repo |

## Success Metrics

- All 12 eval test cases pass (8 positive, 4 negative)
- Zero references to "github-pr-review" remain in the registry
- SKILL.md stays under 800 lines

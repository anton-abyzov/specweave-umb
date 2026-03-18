# Tasks: Fix Skills Are Structured Expertise docs page

## Phase 1: Implementation

### T-001: Fix skills-as-structured-expertise.md accuracy
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [x] completed

**Description**: Update `repositories/anton-abyzov/specweave/docs-site/docs/overview/skills-as-structured-expertise.md` to fix all inaccuracies.

**Implementation Details**:
- Replace "100+ Skills" heading with accurate language (44 core skills + marketplace/community plugins)
- Remove stale skill references: `/backend:nodejs`, `backend:python`, `backend:go`, `/testing:qa`, `/sw:security`, `/backend:database-optimizer`, `/sw:code-review`
- Replace with accurate core skill list: `/sw:pm`, `/sw:architect`, `/sw:code-reviewer`, `/sw:grill`, `/sw:tdd-cycle`, `/sw:release-expert`
- Fix `/sw:architect` description — it is general-purpose system design, not frontend-specific
- Remove or replace dead link to `../skills/skill-development-guidelines`
- Add clear distinction between core skills (shipped with SpecWeave) and domain plugins (installed via vskill marketplace)

**Test Plan**:
- Given the updated docs page → When a user reads it → Then: heading reflects 44 core skills, no stale skill references exist, architect is described as general-purpose, dead link is gone, core vs plugin distinction is clear

**Dependencies**: None

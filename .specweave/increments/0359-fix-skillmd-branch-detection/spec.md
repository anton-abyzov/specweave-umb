# 0359 — Fix false-positive SKILL.md rejection (branch detection gap)

## Problem

`fetchRepoFiles()`, `checkSkillMdExists()`, `fetchSkillContent()`, and `discoverSkills()` hardcode `["main", "master"]` for branch detection. `discoverSkillsEnhanced()` properly uses `detectBranch()` (GitHub API). This causes false-positive REJECTED submissions when repos use non-standard default branches.

## User Stories

### US-001: Correct branch detection for all scanner functions
As a skill submitter, I want the SKILL.md check to detect my repo's actual default branch so my submissions aren't falsely rejected.

**Acceptance Criteria:**
- [x] AC-US1-01: `checkSkillMdExists` uses `detectBranch()` instead of hardcoded branches
- [x] AC-US1-02: `fetchRepoFiles` uses `detectBranch()` instead of hardcoded branches
- [x] AC-US1-03: `fetchSkillContent` uses `detectBranch()` instead of hardcoded branches
- [x] AC-US1-04: `discoverSkills` uses `detectBranch()` instead of hardcoded branches
- [x] AC-US1-05: `detectBranch` is exported for testing
- [x] AC-US1-06: Fail-open behavior preserved in `checkSkillMdExists`

### US-002: Path-aware rejection message
As a skill submitter, I want the rejection message to show the actual path checked, not always "repo root."

**Acceptance Criteria:**
- [x] AC-US2-01: Error message includes skillPath when present
- [x] AC-US2-02: Error message says "repo root" only when checking root SKILL.md

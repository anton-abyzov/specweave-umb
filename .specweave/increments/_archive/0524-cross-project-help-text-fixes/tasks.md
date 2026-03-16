---
increment: 0524-cross-project-help-text-fixes
---

# Tasks: Cross-Project Help Text Fixes

## US-001: Clarify specweave validate-jira help description

### T-001: Update validate-jira help text in source and compiled output
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01
**Status**: [x] Completed
**Test**: Given I run `specweave validate-jira --help` → When I read the command description → Then it reads "Validate Jira connection, project, and issue-type configuration; create missing issue types if needed"

**Files**:
- `repositories/anton-abyzov/specweave/src/cli/commands/validate-jira.ts` line 36
- `repositories/anton-abyzov/specweave/bin/specweave.js` line 714

**Change**: Replace `Validate Jira configuration and create missing resources` with `Validate Jira connection, project, and issue-type configuration; create missing issue types if needed` in both files.

---

## US-002: Clarify vskill init command description

### T-002: Update vskill init command description
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01
**Status**: [x] Completed
**Test**: Given I run `vskill init --help` → When I read the command description → Then it reads "Detect installed AI agents and optionally update the lockfile"

**File**: `repositories/anton-abyzov/vskill/src/index.ts` line 45

**Change**: Replace `Show detected AI agents and update lockfile (optional)` with `Detect installed AI agents and optionally update the lockfile`.

---

## US-003: Improve vskill-platform 404 page help text

### T-003: Update 404 page description paragraph
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01
**Status**: [x] Completed
**Test**: Given I visit a non-existent URL on verified-skill.com → When the 404 page renders → Then the description reads "This URL doesn't match any page. Check the address for typos, or use the links below to navigate."

**File**: `repositories/anton-abyzov/vskill-platform/src/app/not-found.tsx` line 50

**Change**: Replace `This URL doesn't match any page. It may have been moved or removed.` with `This URL doesn't match any page. Check the address for typos, or use the links below to navigate.`

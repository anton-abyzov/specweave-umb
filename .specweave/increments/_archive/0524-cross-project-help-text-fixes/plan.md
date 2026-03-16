---
increment: 0524-cross-project-help-text-fixes
status: approved
---

# Architecture Plan: Cross-Project Help Text Fixes

## Overview

Three independent string replacements across three repos. No logic changes, no new dependencies, no architectural impact.

## Changes

### 1. specweave -- validate-jira help text (AC-US1-01)

**Files** (both must match):
- `repositories/anton-abyzov/specweave/src/cli/commands/validate-jira.ts` (line 36)
- `repositories/anton-abyzov/specweave/bin/specweave.js` (line 714) -- compiled output

**Old**: `Validate Jira configuration and create missing resources`
**New**: `Validate Jira connection, project, and issue-type configuration; create missing issue types if needed`

### 2. vskill -- init command description (AC-US2-01)

**File**: `repositories/anton-abyzov/vskill/src/index.ts` (line 45)

**Old**: `Show detected AI agents and update lockfile (optional)`
**New**: `Detect installed AI agents and optionally update the lockfile`

### 3. vskill-platform -- 404 page copy (AC-US3-01)

**File**: `repositories/anton-abyzov/vskill-platform/src/app/not-found.tsx` (line 50)

**Old**: `This URL doesn't match any page. It may have been moved or removed.`
**New**: `This URL doesn't match any page. Check the address for typos, or use the links below to navigate.`

## Risks

- If specweave has CLI snapshot tests, they will need updating after the description change. No snapshots were found during search, so risk is low.
- The compiled `bin/specweave.js` must be updated alongside the TypeScript source to stay in sync.

## Decisions

- No ADRs needed -- pure copy edits with zero architectural impact.
- No domain skill delegation needed -- changes are simple string replacements.

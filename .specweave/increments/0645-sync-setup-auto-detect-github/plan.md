# Plan: Auto-detect GitHub owner/repo in sync-setup

## Changes

### 1. Add `authenticatedOwner` + `projectPath` to MappingWizardOptions (`project-mapping-wizard.ts`)
New optional fields on the options interface.

### 2. Auto-detect in promptMappingTarget (`project-mapping-wizard.ts`)
For GitHub provider: try git remote parsing first, then fall back to authenticatedOwner + repo name. Show single confirmation "Map to owner/repo?" instead of 3 separate prompts.

### 3. Pass context from sync-setup.ts
Read sync profile owner from updated config after `setupIssueTracker()` completes. Pass to wizard along with project path for git remote detection.

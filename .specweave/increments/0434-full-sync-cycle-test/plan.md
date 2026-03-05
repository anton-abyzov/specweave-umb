---
increment: 0434-full-sync-cycle-test
title: "Full Sync Cycle E2E Test"
---

# Plan

## Approach

1. Create the increment with user stories targeting different child repos
2. Run sync-progress to push to GitHub/JIRA/ADO
3. Verify external items are created with correct routing
4. Mark ACs as complete and re-sync to verify progress updates
5. Verify close flow with completion comments

## Architecture

Uses existing sync infrastructure:
- `resolveSyncTarget()` for per-repo routing
- `github-feature-sync.ts` for GitHub issue management
- `living-docs-sync.ts` for JIRA/ADO sync
- `ac-progress-sync.ts` for AC checkbox updates

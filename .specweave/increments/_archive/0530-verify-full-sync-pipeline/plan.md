# Plan: FS-530 Verify Full Sync Pipeline

## Key Investigation: AC Comments Per Platform

### GitHub: Has comments (via addComment option in update-ac-status.ts)
### ADO: Has comments (ado-ac-checkbox-sync.ts posts progress update comment)
### JIRA: MISSING comments — jira-ac-checkbox-sync.ts only updates description checkboxes, never posts comments

## Implementation
1. Add comment posting to jira-ac-checkbox-sync.ts (use JIRA REST API v3 comment endpoint)
2. Run full pipeline test with this increment
3. Measure API call counts before/after

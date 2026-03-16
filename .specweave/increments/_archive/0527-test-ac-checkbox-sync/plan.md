# Plan: FS-527 Test AC Checkbox Sync

## Approach

Verification-only increment. No code changes — all implementation shipped in v1.0.458.
Run sync twice (first to create living docs, second to sync to external tools) and visually confirm.

## Steps

1. Run `specweave sync-living-docs FS-527` (creates FEATURE.md + us-*.md)
2. Run `specweave sync-living-docs FS-527` again (syncs to JIRA / ADO / GitHub)
3. Verify JIRA Epic → Story hierarchy + native checkboxes
4. Verify ADO Epic → Issue hierarchy
5. Verify GitHub Milestone → Issue linkage

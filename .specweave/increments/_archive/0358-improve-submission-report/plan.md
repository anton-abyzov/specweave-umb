# Plan — 0358 Improve Submission Report

## Approach
Single-file change to `src/app/submit/[id]/page.tsx`. The API already sends `file` and `commitSha` — just wire them to the UI.

## Steps
1. Fix client types: add `file` to ScanFinding, `commitSha` to scanResult
2. Import `buildGitHubPermalink` from existing utility
3. Add `groupFindings()` helper (group by patternId+file)
4. Replace findings render block with grouped+linked version
5. Build and verify

# Tasks — 0358 Improve Submission Report

### T-001: Fix client types and add import
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test**: Given the page.tsx types → When `file` and `commitSha` are added → Then TypeScript compiles without errors

- Add `file?: string` to `ScanFinding` interface
- Add `commitSha?: string` to `SubmissionResponse.scanResult`
- Import `buildGitHubPermalink` from `@/lib/scanner/github-permalink`

### T-002: Add groupFindings helper
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test**: Given findings with same patternId+file → When grouped → Then one entry with multiple lineNumbers

- Add `GroupedFinding` interface
- Add `groupFindings()` function that groups by `patternId::file`
- Sort line numbers ascending within each group

### T-003: Replace findings render block
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test**: Given grouped findings → When rendered → Then each group shows file path, pattern name, and clickable line chips with GitHub permalinks

- Iterate grouped findings instead of raw
- Parse repoUrl for owner/repo
- Build permalink per line number
- Show file path in header row
- Render line numbers as clickable chips (link or span fallback)
- Keep total raw count in FINDINGS header

### T-004: Build and verify
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-03, AC-US2-03 | **Status**: [x] completed
**Test**: Given changes → When `npm run build` → Then no errors

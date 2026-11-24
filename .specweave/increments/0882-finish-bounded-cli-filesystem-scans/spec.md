---
status: completed
---
# Finish bounded CLI filesystem scans

**Project**: specweave

## Problem
PR #1951 fixes cwd fallback scans in living-docs, save and gc. Its original Claude session is 7598cec3-ada6-4d25-a594-8fa5259a5436. Remaining LSP entry points scan arbitrary cwd, LSP detection follows symlinks, and dashboard accepts a global bare .specweave directory.

## Scope
Finish these small remaining guards, preserve valid project operation, verify original PR and new fixes, update PR #1951. No release, merge, global installation, or unrelated CI redesign.

## Acceptance Criteria
- [x] AC-01 All LSP CLI actions stop outside a SpecWeave project before scanning or initialization; nested cwd resolves nearest project; quiet warmup remains quiet.
- [x] AC-02 Language scans and server detection skip symlinked containers, directories and project files while detecting real files and Swift project directories.
- [x] AC-03 Dashboard refuses bare .specweave without starting or registering a server; valid project uses effective root.
- [x] AC-04 Original and new regression tests, build, lints and bounded black-box CLI checks pass; changes pushed to PR #1951 with precise CI status.

## Approach
Reuse findProjectRoot for LSP and findEffectiveRoot for dashboard. Use Dirent/lstat for LSP filesystem checks. Tests use synthetic directories and mocked server availability; no browser launches. Work in isolated 0882-codex worktree based on PR head. Keep PR #1950 independent; test both together in temporary integration checkout if needed. Preserve all existing tests.

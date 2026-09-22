---
status: completed
---
# 0876 — Release bounded portable hooks
## Problem
Published 2.0.0 hook manifests use ignored args fields in Codex. PreCompact synchronous Git blocks timeout timers and temporarily changes real index. Local repair must ship upstream.
## Scope
Portable command strings; supervised hook worker; isolated bounded Git capture; regression tests; patch release. Excludes unrelated unpublished 2.0.1 cleanup commit.
### US-001 Reliable hooks
**Project**: default
## Acceptance Criteria
- [x] AC-01: Hook manifest executes launcher on Codex; hung worker terminates before host limit.
- [x] AC-02: Handoff never mutates real index and Git calls have bounded total runtime.
- [x] AC-03: Tests/build/preflight pass and patch tarball, source commit and tag are published.
## Approach
Isolated worktree from origin/develop. Port supervisor into package; retain original launcher as worker. Move index isolation into shared Git capture with deadline. Regression first, then source edits, independent review, release 2.0.2. Existing local unpublished cleanup stays untouched.

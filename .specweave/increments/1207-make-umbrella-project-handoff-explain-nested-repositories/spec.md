# 1207 Make umbrella project handoff explain nested repositories

## Problem
The handoff sharing screen checks only the root repository identity. An umbrella without its own remote is described as having nothing to clone, even when nested repositories have origins. The existing folder transfer supports cloning repositories and copying local additions, but the entry point hides this capability.

## Scope
In: bounded source-side nested repository discovery, accurate umbrella handoff explanation and routing to the existing mixed Git/file review, focused tests and headless visual evidence, PR merge and release coordination, explanation of the origin warning.
Out: performing a real OlySense handoff, changing credentials, replacing the transfer engine, taking over another release dispatcher.

## Acceptance Criteria
- [ ] AC-01: A root without a remote lists discovered nested repositories with origins and distinguishes repositories requiring file copy. Unknown or incomplete discovery never claims there is nothing to clone.
- [ ] AC-02: The umbrella entry point opens the existing review that can clone repositories and copy local changes; it does not tell users to commit non-Git files or imply uncommitted files must stay behind.
- [ ] AC-03: Single-repository cloning, explicit secrets selection, destination checks and existing-copy protection remain intact.
- [ ] AC-04: Focused checks, production builds and headless visual verification pass; a fresh review approves the exact PR head, and merge and release evidence are recorded separately.

## Approach
Extend the existing FolderCopyScopes response with optional, bounded repository-origin classifications and populate the project root's existing repository list. Reuse source-side discovery rather than relying on cached root identity or guessing from names. Show an umbrella-specific entry in HandoffShare, routing to HandoffFolderCopy's existing clone/copy review. Keep root clone behavior unchanged. Trace repositorySync's unreachable warning without changing M3 credentials or files.

## Decisions
### Defaulted
- Use the existing mixed transfer review rather than introduce a second clone implementation.
- An origin is a clone candidate, not proof the destination can access it; the existing destination preview decides availability.
- Release remains with the current dispatcher until explicitly yielded.
### Open
- None.

## Tasks
### T-01 Discover and explain nested repository transfer
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/folderCopy.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/fleet/folderCopyScope.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/fleet/folderCopyScope.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/HandoffShare.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/HandoffShare.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/HandoffShareRepositories.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/HandoffCopyScope.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/ProjectMachineHandoff.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/ProjectMachineHandoff.test.tsx | Test: focused web and server suites

### T-02 Verify behavior, review, merge and release
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/tests/handoff-share/**, README.md, CHANGELOG.md, repositories/anton-abyzov/specwithcode-dev/docs/user/add-a-machine.md, reports/** | Test: production web/server builds, headless fixture, exact-head review and release receipt

### T-03 Verify and close 1207
- AC: AC-01, AC-02, AC-03, AC-04 | Files: reports/** | Test: specweave verify 1207 and specweave complete 1207

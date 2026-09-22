# Deploy bounded CLI scan fixes

**Project**: specweave

## Problem
PRs #1950 and #1951 contain verified fixes but remain unmerged and absent from stable npm. Stable npm 2.2.3 is based on tag a8b4fd0d4, while develop remains 2.2.2. Releasing from develop directly would drop deployed Jev features.

## Scope
Merge release PR #1954 containing the two scoped fix PR heads, ship the fixes in the coordinated stable 2.3.0 release preserving the existing stable release, verify the downloaded registry artifact, and push scoped umbrella evidence. Preserve unrelated dirty changes and the locally installed 2.3 RC.

## Acceptance Criteria
- [ ] AC-01 Both fix PRs merged with exact-head protection; respect branch policy and the authorized release process.
- [x] AC-02 Version 2.2.4 contains stable 2.2.3 and both fix branches; combined build, unit tests, lint, and packaged CLI regressions pass.
- [ ] AC-03 npm latest and GitHub release resolve to coordinated stable 2.3.0; downloaded registry artifact passes bounded-scan and refresh-plugins regressions.
- [ ] AC-04 Source and scoped evidence pushed; merge SHAs, publication receipts, and remaining external check status recorded.

## Approach
Isolated release worktree from stable v2.2.3. Merge fix branches and preserve changelog entries; bump patch using repository version-stamping machinery. Test before publish, then install registry package in an isolated prefix and rerun CLI checks. GitHub branch protection requires one approval and has rejected ordinary merge; admin authorization is pending. Do not replace the user's globally installed 2.3 RC with the stable patch.

Current release candidate: fe9db936dae5f865ddc92a5146c6dac423c0882d. PR #1952 was independently squash-merged as 5728b69a0 during preparation; tree parity with its original head was verified before reconciling ancestry without changing candidate files.

Release coordination: task 01a0c712-f935-7de2-8285-15fc93773bae owns PR #1953 and stable 2.3.0 publication. It is integrating these fixes. Do not publish competing 2.2.4 or overwrite the newer global installation; independently verify the downloaded 2.3.0 package.

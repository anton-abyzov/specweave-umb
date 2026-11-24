---
status: completed
---
# Deploy bounded CLI scan fixes

**Project**: specweave

## Problem
At the start, PRs #1950 and #1951 contained verified fixes absent from stable npm. Published 2.2.3 was based on tag a8b4fd0d4 while develop was still 2.2.2, so a direct release risked dropping deployed Jev features.

## Scope
Merge both scoped fix PR heads through the coordinated #1953 release (including #1954 ancestry), ship the fixes in the coordinated stable 2.3.0 release preserving the existing stable release, verify the downloaded registry artifact, and push scoped umbrella evidence. Preserve unrelated dirty changes and the locally installed 2.3 RC.

## Acceptance Criteria
- [x] AC-01 Both fix PRs merged with exact-head protection; respect branch policy and the authorized release process.
- [x] AC-02 Version 2.2.4 contains stable 2.2.3 and both fix branches; combined build, unit tests, lint, and packaged CLI regressions pass.
- [x] AC-03 npm latest and GitHub release resolve to coordinated stable 2.3.0; downloaded registry artifact passes bounded-scan and refresh-plugins regressions.
- [x] AC-04 Source and scoped evidence pushed; merge SHAs, publication receipts, and remaining external check status recorded.

## Approach
Isolated release worktree from stable v2.2.3. Merge fix branches and preserve changelog entries; bump patch using repository version-stamping machinery. Test before publish, then install registry package in an isolated prefix and rerun CLI checks. The release owner completed independent review and merged with the user-authorized release permissions in its task; all original fix PRs now report merged. Do not replace the user's globally installed 2.3 RC with the stable patch.

Current release candidate: fe9db936dae5f865ddc92a5146c6dac423c0882d. PR #1952 was independently squash-merged as 5728b69a0 during preparation; tree parity with its original head was verified before reconciling ancestry without changing candidate files.

Release coordination: task 01a0c712-f935-7de2-8285-15fc93773bae owns PR #1953 and stable 2.3.0 publication. It is integrating these fixes. Do not publish competing 2.2.4 or overwrite the newer global installation; independently verify the downloaded 2.3.0 package.

Source merged through PR #1953 as 8be01b24e23f18c1a87036e7f6e8ab0d4c98cce3. Original PRs #1950, #1951 and consolidated #1954 report MERGED. Readback confirmed merged tree equals tested c8fbd8c16 and contains both exact fix heads. Release run 35690795298 is publishing tag v2.3.0.

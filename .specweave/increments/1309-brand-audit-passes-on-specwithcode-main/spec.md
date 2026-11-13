# Brand audit passes on specwithcode main

## Problem

`node scripts/studio-brand-audit.mjs` exits 1 on specwithcode main at `be371b1d87` with 7 of 21 checks failed. The 1297 thread hit it closing T-21, and the 1303 close checks wait on it.

The audit runs only in the on-demand `ci.yml`, never on pull requests, so nothing stopped the drift. It already failed 7 of 21 at `072265ee00`, the first public commit that carries the script. The changes behind each failure were made in the private history (`dev/main`):

| Check | Cause | Commit | Stale side |
|---|---|---|---|
| upstream MIT provenance retained exactly | A "Linux voice" section was added after the inherited license, and the check compares everything from "MIT License" to the end of the file | `c47c0f1399` (#1270, November 3) | check |
| project terms remain separate from inherited notices | The project was released under MIT; the check still requires no `LICENSE` and `UNLICENSED` | `af71feb441` (#1447, November 6) | check |
| reference trees and fixtures preserved | 5 inherited assertion helpers gained Studio assertions; 8 Codex transcripts carry the public repository's origin URL; 53 Studio-owned fixture files are unlisted and one listed file changed | `88ec8e9e3d` (#654), `eb3c87ab68`, `27707679f7` (October 25); public snapshots `b71edc5054`, `839602c74d` | manifest and check |
| self update only from an owned feed | The refused-feed digests moved from `DesktopUpdates.ts` to `updateFeedGate.ts` | `fdcc652ec4` (October 29) | check |
| no upstream name outside the documented references | The Ghostty notice cites a commit, no longer the branch named after upstream, so two allowances are unused | public snapshot `b71edc5054` | check |
| no publishable key outside tests | SpecWithCode's own Connect key is in the iOS and Android clients; Swift `Tests/` and `src/testing/` are not seen as tests | `5668c3ab41` (October 20), `e5e80d6870` (#1418), public `1c1906f94a` (#190) | check |
| pinned registry, patch and payload bytes preserved | The LegendList patch was replaced under a reviewed lock change; two Expo 57 patches were ported to Expo 58 | `c43122baf0` (#959, October 27), `a3906b9ff6` (#306, October 17) | check |

## Scope

In: make the audit pass on main without loosening what it protects (inherited license text, notices, reference trees, inherited fixture and patch bytes, upstream names, keys); unit tests for each rule that changes; PR, review, merge; hand the shared checkout back.

Out: any change to `LICENSE`, `THIRD_PARTY_NOTICES.md` or `UPSTREAM.md` text. The license field of generated manifests is T-05, in its own PR (D-01). Running the audit on every pull request (recommended follow-up).

## Acceptance Criteria

- [ ] AC-01: `node scripts/studio-brand-audit.mjs` exits 0 with no failed check in the shared checkout at the PR head, and again at `origin/main` after the merge.
- [ ] AC-02: The audit still fails, proven by unit tests, when: the inherited license text in `THIRD_PARTY_NOTICES.md` is altered, missing or duplicated; `LICENSE` is missing, is not the MIT text or carries the inherited copyright; an inherited fixture changes without a pinned reviewed hash; an inherited patch changes or disappears without a reviewed lock change; a publishable key outside a test is not for an owned host, or any key is for an upstream host.
- [ ] AC-03: Studio-owned fixture files are scanned for upstream names like any other owned file.
- [ ] AC-04: The PR changes no byte of `LICENSE`, `THIRD_PARTY_NOTICES.md` or `UPSTREAM.md`, and its description says for each of the seven checks whether the check or the code was stale.
- [ ] AC-05: The shared checkout is back on detached `origin/main` with a clean status, and the "Onboarding and new-project-from-folder UX" thread is told main passes.
- [ ] AC-06: Generated manifests state the license Anton chose, or stay untouched if he says so.

## Approach

All paths are under `repositories/anton-abyzov/specwithcode-dev/`.

1. `scripts/studio-toolchain/source-terms-rules.mjs` (new): pure rules with tests. `assertInheritedNoticeRetained` requires the upstream license text exactly once in the notices, byte for byte, followed by the end of the file or a new `## ` section. `assertProjectLicense` requires `LICENSE` to be the same MIT body under the owner's copyright line and no inherited copyright. `publishableKeyFinding` and `isTestPath` hold the key rule.
2. `scripts/studio-brand-audit.mjs`: use those rules; the project-terms check asserts MIT in every workspace manifest and that notices still reach each bundle; the update check reads `updateFeedGate.ts` and that `DesktopUpdates.ts` calls it; drop the two unused Ghostty allowances; a key outside a test passes only for an owned Clerk host (`clerk.spec-weave.com`); `Tests` and `testing` count as test directories; a fixture path is an upstream reference file only when upstream has that path.
3. `scripts/studio-toolchain/fixture-preservation-audit.mjs`: inherited fixtures stay pinned (upstream bytes or a reviewed hash). The 13 changed entries are re-pinned after reading each diff: 8 transcripts differ only in the origin URL, 5 helpers add or adjust Studio assertions (new reason `studio-test-assertion`, closed path list). A fixture with no upstream counterpart is Studio's own and is no longer hash-pinned; `owned-fixture-files.json` goes away. `.repos` stays closed: any added file fails.
4. `scripts/studio-toolchain/preservation-audit.mjs`: an inherited patch must equal upstream unless a reviewed `replace` lock change pins its new hash, or it is in the closed list of patches ported to a new package version whose successor is a reviewed patch.

Rejected: listing all 53 owned fixtures in the pinned manifest. Each entry needs the full SHA of the commit that added the file, which a squash-merged PR cannot know, so the list cannot be kept current and the audit would fail again on the next new fixture. Reverting the five helper changes would remove assertions that guard shipped behavior.

Risk: scanning owned fixtures for upstream names may surface real leftovers; fix them in the file, never by allowance.

## Decisions

### Answered
- D-01 License field of the generated npm, runtime and desktop manifests, the Linux metainfo and two podspecs (`UNLICENSED` / `LicenseRef-proprietary` after the MIT release) → asked November 12, 2026; answered by Anton on November 13, 2026: "go, let's avoid those contradictions, so go ahead and update it all." Every license marker becomes MIT to match `LICENSE`, plus the desktop copyright string and the workspace manifests that had no license field; the brand audit asserts it. Shipped in its own PR (anton-abyzov/specwithcode#330), not the audit-fix PR. Third-party notices, `THIRD_PARTY_NOTICES.md`, `UPSTREAM.md` and the Apache-2.0 Chrome extension stay as they are. Anton also asked for the npm package `specwithcode` to show MIT on its next published version.

### Defaulted (change any before sw-do)
- D-02 Studio-owned fixture files → not hash-pinned, scanned for upstream names instead (reversible).
- D-03 Owned Connect publishable key in client source → allowed by decoded host, since publishable keys are public by design (reversible).
- D-04 Audit on every pull request → not in this increment; recommended next.

### Open
- none

## Notes

- November 13, 2026: T-06 is blocked in agent shells. `specweave verify` runs the server shards, and 37 tests that create linked git checkouts in temp repos fail there because the session's git guard refuses them while Use worktrees is off. The same shards passed in PR #330's CI. Close by running verify outside an agent shell (or after the guard stops applying to temp test repos), then `specweave task done T-06` and `specweave complete`. Review: `reports/review-claude-sonnet-5-5.md` (local); release evidence: `~/.specwithcode/m4/evidence/1309-mit-license/1.0.283/README.md`.

## Tasks

### T-01 Source terms, update feed, names and keys checks
- AC: AC-01, AC-02, AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/scripts/studio-brand-audit.mjs, repositories/anton-abyzov/specwithcode-dev/scripts/studio-toolchain/source-terms-rules.mjs, repositories/anton-abyzov/specwithcode-dev/scripts/studio-toolchain/source-terms-rules.test.mjs | Test: cd repositories/anton-abyzov/specwithcode-dev && node --test scripts/studio-toolchain/source-terms-rules.test.mjs

### T-02 Fixture preservation: re-pin reviewed fixtures, owned fixtures scanned
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode-dev/scripts/studio-toolchain/fixture-preservation-audit.mjs, repositories/anton-abyzov/specwithcode-dev/scripts/studio-toolchain/fixture-preservation-audit.test.mjs, repositories/anton-abyzov/specwithcode-dev/scripts/studio-toolchain/reviewed-fixture-migrations.json, repositories/anton-abyzov/specwithcode-dev/scripts/studio-toolchain/owned-fixture-files.json | Test: cd repositories/anton-abyzov/specwithcode-dev && node --test scripts/studio-toolchain/fixture-preservation-audit.test.mjs

### T-03 Patch preservation honors reviewed replacements and ports
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode-dev/scripts/studio-toolchain/preservation-audit.mjs, repositories/anton-abyzov/specwithcode-dev/scripts/studio-toolchain/preservation-audit.test.mjs | Test: cd repositories/anton-abyzov/specwithcode-dev && node --test scripts/studio-toolchain/preservation-audit.test.mjs && node scripts/studio-brand-audit.mjs

### T-04 PR, review, merge, hand the checkout back, tell the onboarding thread
- AC: AC-01, AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode-dev/AGENTS.md | Test: cd repositories/anton-abyzov/specwithcode-dev && git fetch origin main && test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" && test -z "$(git status --porcelain)" && node scripts/studio-brand-audit.mjs

### T-05 License field of generated manifests, per Anton's answer
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode-dev/scripts/studio-fleet/npm-package.mjs, repositories/anton-abyzov/specwithcode-dev/scripts/studio-fleet/npm-package.test.mjs, repositories/anton-abyzov/specwithcode-dev/scripts/studio-fleet/runtime-package.mjs, repositories/anton-abyzov/specwithcode-dev/scripts/studio-fleet/runtime-package.test.mjs, repositories/anton-abyzov/specwithcode-dev/scripts/build-desktop-artifact.ts, repositories/anton-abyzov/specwithcode-dev/apps/desktop/resources/linux/com.specweave.studio.metainfo.xml, repositories/anton-abyzov/specwithcode-dev/apps/mobile/modules/studio-review-diff/StudioReviewDiffNative.podspec, repositories/anton-abyzov/specwithcode-dev/apps/mobile/modules/studio-terminal/StudioTerminalNative.podspec, repositories/anton-abyzov/specwithcode-dev/scripts/studio-brand-audit.mjs, repositories/anton-abyzov/specwithcode-dev/scripts/build-desktop-artifact.test.ts, repositories/anton-abyzov/specwithcode-dev/infra/relay/package.json, repositories/anton-abyzov/specwithcode-dev/oxlint-plugin-studio/package.json, repositories/anton-abyzov/specwithcode-dev/scripts/package.json | Test: bash .specweave/increments/1309-brand-audit-passes-on-specwithcode-main/t05-mit-check.sh

### T-06 Verify and close 1309
- AC: AC-01 | Files: .specweave/increments/1309-brand-audit-passes-on-specwithcode-main/spec.md | Test: specweave verify 1309-brand-audit-passes-on-specwithcode-main

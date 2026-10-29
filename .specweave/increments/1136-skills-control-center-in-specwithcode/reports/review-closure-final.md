# Review: 1136 closure fixes

Verdict: ship · risk: low · 15 changed files · no remaining findings
Reviewer context: fresh child session; did not implement the fixes. Reviewed fix commit `c3c6520a25e2f08f7f21a51215f27951f854a351` and final HEAD `914455629b6a134d019e1cec4a7f9d8d07c52bd5` in `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/1136-closure-fixes`. Date: 2026-10-29.

This report supersedes the fix-first verdict for the three findings in `review-closure.md`, which remains intact as the initial evidence. The verdict covers source correctness of the fixes; release, CI and installed acceptance remain separate gates.

## Finding resolution

1. **Plugin Undo after rediscovery — resolved.** `apps/server/src/provider/Drivers/ClaudeSkills.ts` retains explicitly disabled installed plugin skills with `enabled: false`, so they remain addressable by the existing action resolver. `ProjectSkillsToggles.test.ts` now performs disable, rediscovery, preview and enable, checking the resulting effective state. The settings UI offers Turn on for disabled Claude plugins. Enabled copies are ordered before explicitly disabled copies sharing a namespace; the new `ClaudeSkills.test.ts` fixture deliberately gives the disabled marketplace the earlier alphabetical name and confirms the enabled source wins.
2. **Unsupported Claude per-skill plugin switch — resolved.** `ProjectSkillsToggles.ts` refuses `scope: plugin` before writing settings for both preview and apply. `ProjectSkillActions.logic.ts` disables that UI switch with a whole-plugin reason. Regression coverage checks refusal, no CLI call, no refresh/write and absent settings changes; the settings fixture checks the disabled switch and available whole-plugin control.
3. **Registry drift after version preview — resolved.** `projectSkills.ts` carries a validated `expected.targetVersion`. `ProjectSkillsActions.ts` compares the apply-time registry choice with that preview version before invoking install, rejecting either missing expected version or changed latest version as stale. The changing-registry fixture confirms no install or after-write hook occurs on refusal. Existing update fixtures now pass the preview expectation and still test pinned and unpinned behavior.

README, changelog and the AGENTS command guidance accurately describe these behaviors. No additional correctness or security finding survived reinspection of the final committed diff.

## Verification examined

- `fix-server-coverage.log`: five files, 82 tests passed. Scoped V8 coverage for `ProjectSkillsActions.ts` and `ProjectSkillsToggles.ts`: 93% lines, 81.96% branches, 87.75% functions, 92.15% statements. These numbers do not represent whole-repository coverage or Claude discovery coverage.
- `fix-web-tests.log`: two settings suites, 27 tests passed.
- `fix-contracts-tests.log`: one suite, seven tests passed, including exact preview-version preservation and invalid-version rejection.
- `closure-ui.json`: headless controls check passed in light/dark; unsupported per-skill switches are disabled and whole-plugin actions select the correct enable/disable value. The receipt explicitly records no live settings writes.

These are actual retained outputs read by this reviewer, not tests re-executed by the reviewer. The focused tests use isolated fixtures and stand-in CLI operations; they do not prove installed native CLI behavior on every machine. The final test-only commit copies explicit name, path, plugin scope and enabled state from rediscovery instead of spreading optional properties; it preserves the tested behavior and fixes exactOptionalPropertyTypes. `fix-typecheck-server.log` records the server typecheck gate passing with zero new diagnostics (87 baseline diagnostics remain; the raw compiler exits 1). The original typecheck log records the other 14 packages passing. `fix-production-build.log` records the production build completing; the parent observed exit 0. These are baseline-aware typecheck and build passes, not claims of a diagnostic-free repository. Release staging and CI remained pending at this final review update. No live provider turn, account mutation, browser session or source edit was performed by this reviewer.

## Final platform-scope review

Fresh reviewer rechecked the recorded Windows failures after CI completed. No evidence of a new defect introduced by #995: failures are in unchanged paths or existing vskill discovery before the added drift assertion. Proceed with the macOS release once required CI passes. Closure scope is the accepted macOS skills control center; Windows launcher compatibility remains with active PR #991 and its existing owner. Do not claim all-platform completion or Windows acceptance. The POSIX file-mode assertion also provides no Windows ACL assurance. Canonical candidate 095714ab3657 has 18 passing prechecks and 13,309 passing server tests, with 32 pending.

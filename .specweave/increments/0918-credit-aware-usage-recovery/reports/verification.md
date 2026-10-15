# 0918 verification

Product commit: d8d0422d5 (codex/credit-recovery), based on origin/main 4d6e30488.
Product checkout: /Users/antonabyzov/Projects/github/studio-credit-recovery.

305 focused tests pass across seven suites. Web production build passes; server production build passes and bundles dist/client. Headless Chrome fixture checks pass in 21 cases (18 baseline width/theme/status cases plus credit callback and separate resolved-state checks at 320/768/1440). The fixtures use production components with synthetic account data, not a live paid turn or installed-app acceptance.

Scoped coverage of CreditRecoveryAction and usageWarningResolution: 95% statements, 84.31% branches, 100% functions and lines. This is focused unit coverage, not repository-wide integration/E2E coverage. Fresh-context review approved after reproducing and fixing the navigation-during-paid-retry race and historical-warning reactivation; actual callback regressions cover route/model/account/denial/permission/freshness changes.

Full web typecheck remains red on pre-existing Effect diagnostics: fs imports in tests, ProjectPlan.test crypto use, ProjectWorkspace.test fs/path, and newThreadWorkspaceDefault unknown error/type assertions. No new recovery code type errors remain. No claim of clean global typecheck.

Evidence: product .artifacts/credit-recovery/*.log, .artifacts/credit-coverage/, .artifacts/usage-limit-recovery/evidence/{receipt.json,credit-recovery-*.png,resolved-warning-*.png}.

Release: Anton explicitly approved coordinating with Improve SpecWithCode release output and Fix GitHub Copilot links. Existing release owner retains PR172 and 1.0.14 source/install ownership; verified commit delivered for integration. No independent release/version bump/install. Packaging currently needs storage: SanDisk free5.9GiB versus8GiB guard; user asked to free10GiB or name another volume. Manual UI acceptance and deployed readback remain outstanding.

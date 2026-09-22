# Lifecycle pointer contract correction — T28

Final documentation-head CI 34817251213 exposed an outdated assertion in tests/e2e/lifecycle/closure-2.0.e2e.ts. The handoff command successfully wrote its intended file and its new relative pointer. The test then resolved that pointer against the test-runner checkout, producing ENOENT for that unrelated directory.

The failure was reproduced locally using the CI environment and the built published runtime: lifecycle-pointer-red.log. The test now requires a relative pointer, resolves it from the fixture project root, and retains the exact canonical handoff destination assertion. It adds a portability guarantee; it does not remove a case, relax a limit, or alter implementation.

The complete lifecycle file passes all eight CLI end-to-end cases: lifecycle-pointer-green.log. Node22, CI=true, GITHUB_ACTIONS=true, explicit E2E configuration. No browser needed. Runtime/package contents are unchanged; this is a test contract update after the2.1.0 release.

The separate old LSP speed comparison failed because its measured ratio exceeded a wall-clock threshold. That unrelated benchmark failure remains visible; it was not removed, skipped or weakened.

Independent review: skills_audit approved commit59fd2c4d5 without authoring code. All existing file/content/destination assertions remain; no findings.

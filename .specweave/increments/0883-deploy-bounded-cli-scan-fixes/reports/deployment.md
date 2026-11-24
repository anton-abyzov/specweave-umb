# Stable deployment verified

SpecWeave 2.3.0 published to npm latest and GitHub stable release: https://github.com/anton-abyzov/specweave/releases/tag/v2.3.0. Release workflow https://github.com/anton-abyzov/specweave/actions/runs/35690795298 completed successfully.

Source merge: 8be01b24e23f18c1a87036e7f6e8ab0d4c98cce3 through PR #1953. Original fix PRs #1950 and #1951, and consolidated candidate #1954, all report MERGED. Verified source tree equals tested c8fbd8c16 and includes both exact fix heads. The planned 2.2.4 candidate was superseded by this coordinated 2.3.0 release; no competing older npm publication occurred.

Independent registry verification at 2026-09-22T05:36:13Z: npm latest 2.3.0; downloaded tarball SHA-512 matches registry integrity; isolated installation reports version 2.3.0; complete bounded-scans harness passed against installed package. refresh-plugins rejects a bare .specweave directory with exit 1 in 64 ms, and quiet mode returns exit 1 silently in 59 ms. See registry-receipt.json and task-T-02.log. The initial public check correctly failed while npm still reported 2.2.3 during propagation; completion was recorded only after the public artifact passed.

CI: 16,858 unit tests passed, 159 pre-existing skips; full coverage lines 69.52%, branches 61.96%, functions 71.41%, statements 68.94%, all above 60%. Documentation build and 685 links passed. Independent live guide readback confirmed the deployed SpecWeave 2.3 page and project init command.

Known limitation: the pre-existing nonblocking comparative LSP benchmark failed on retry (49.36 ms vs 45.81 ms threshold); 88 other E2E tests passed. No assertion was weakened or skipped to change this outcome. External Claude review still failed before model execution; the release owner obtained an independent review and used the user's authorized release permissions for the protected merge.

Umbrella release owner is integrating final scoped evidence through PR #93. The release task installed stable 2.3.0 globally. Independent readback of specweave --version and npm ls -g specweave confirms 2.3.0. A separate task verified four installed refresh-plugins cases in ~60 ms, silent quiet mode, no project writes, and preservation of local and symlink-target locks; installed-global-refresh.json preserves its receipt.

Closure: specweave verify 0883 passed with 4/4 ACs and 2/2 tasks. specweave complete 0883 --yes exited 0 and set completed through the CLI. GitHub milestone 263 created; ADO 2456 transitioned to Done. Jira returned 404 Site temporarily unavailable, so tracker sync remains unavailable independently of the successful deployment.

Global CLI proof also includes successful refresh-plugins from the real umbrella and nested repository (930 ms / 583 ms, active sw 2.3.0). Jira sync was retried once and remained unavailable; this does not change the completed increment or published package.

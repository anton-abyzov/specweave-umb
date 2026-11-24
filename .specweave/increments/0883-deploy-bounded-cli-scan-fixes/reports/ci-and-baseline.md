# Combined candidate CI and baseline comparison

Candidate: fe9db936dae5f865ddc92a5146c6dac423c0882d.

GitHub Test & Validate run https://github.com/anton-abyzov/specweave/actions/runs/35688195434 passed on its unchanged retry. Unit: 746 files passed, 16,801 tests passed, 159 existing environment-dependent skips. E2E: 12 files passed, 89 tests passed, 106 existing skips. Smoke and results also passed. First attempt had a 10-second source scan timeout and a comparative LSP timing failure. No tests or assertions were modified.

Additional local E2E: 134 passed, nine failed, 52 skipped. All nine failures occur in optional tests against the adjacent vskill checkout. Checked out develop 5728b69a08ca41f10c10f2143f3751a907434e61 in an isolated worktree sharing the same sibling vskill; its exact same nine test titles fail (28 passed, two skipped in that file). Programmatically compared sorted failed test titles: identical. Source test and skill index implementation diff from develop is empty. These are pre-existing cross-repository expectations, not scan regressions.

Failures:

- tests/e2e/plugin-activation/skill-matching.test.ts > Plugin Activation E2E Tests > T-006: Kubernetes Plugin Activation > should activate infrastructure skills for "deploy to EKS with GitOps"
- tests/e2e/plugin-activation/skill-matching.test.ts > Plugin Activation E2E Tests > T-010: Additional Domain Activation > Database > should activate database skills for "PostgreSQL performance"
- tests/e2e/plugin-activation/skill-matching.test.ts > Plugin Activation E2E Tests > T-010: Additional Domain Activation > Database > should activate database skills for "database performance"
- tests/e2e/plugin-activation/skill-matching.test.ts > Plugin Activation E2E Tests > T-010: Additional Domain Activation > Infrastructure/DevOps > should activate devops skills for "Terraform AWS"
- tests/e2e/plugin-activation/skill-matching.test.ts > Plugin Activation E2E Tests > T-010: Additional Domain Activation > Infrastructure/DevOps > should activate devops skills for "containerization"
- tests/e2e/plugin-activation/skill-matching.test.ts > Plugin Activation E2E Tests > T-010: Additional Domain Activation > Security > should activate security skills for "authentication implementation"
- tests/e2e/plugin-activation/skill-matching.test.ts > Plugin Activation E2E Tests > T-010: Additional Domain Activation > Security > should activate security skills for "security vulnerabilities"
- tests/e2e/plugin-activation/skill-matching.test.ts > Plugin Activation E2E Tests > T-010: Additional Domain Activation > Testing > should activate testing skills for "E2E Playwright tests"
- tests/e2e/plugin-activation/skill-matching.test.ts > Plugin Activation E2E Tests > T-010: Additional Domain Activation > Testing > should activate testing skills for "TDD workflow"

---
increment: 0844-vskill-private-repo-install
title: "vskill: private-repo install support"
generated: 2026-05-10
source: increment-skill-single-agent
version: "1.0"
status: ready
---

# Quality Contract — vskill Private-repo Install

Per-increment quality bar that `sw:grill`, `sw:judge-llm`, and PM closure
gates use to decide whether the increment ships. Every criterion must be
either MET or explicitly WAIVED with a reason in the closure report.

## Functional

| ID | Criterion | Verification |
|----|-----------|--------------|
| F-1 | `vskill install --repo anton-abyzov/anton-personal-skills --all --dry-run` succeeds and lists `resume-tuner` | E2E test `tests/integration/private-repo-install.test.ts` (gated by `VSKILL_E2E=1`) |
| F-2 | A real install (no `--dry-run`) symlinks `skills/resume-tuner` into `~/.claude/skills/` | Manual canary run after the E2E (since real installs mutate the home dir) |
| F-3 | Public-repo install behaviour unchanged | Existing test suite green + manual public canary |
| F-4 | Single-plugin install (`--plugin foo`) works on private repos too | Unit test parameterised across both flows |
| F-5 | Differentiated exit codes (2 / 3 / 4 / 5) per US-002 | Unit tests for each path in `tests/unit/private-repo-install.test.ts` |

## Security

| ID | Criterion | Verification |
|----|-----------|--------------|
| S-1 | No raw token text appears in any log line, audit entry, or stderr | grep over a captured stdout/stderr stream from a successful install: `grep -E "ghp_|gho_|github_pat_|ghs_" stdout.log` returns 0 matches |
| S-2 | `installed-skills.json` records `token_fingerprint_hash` exactly 12 hex chars (sha256[:12]) | Unit test on `recordInstall` |
| S-3 | `~/.vskill/installed-skills.json` mode is `0600` after first write | Unit test reads `fs.statSync(...).mode & 0o777` and asserts `0o600` |
| S-4 | SSRF allow-list unchanged (`api.github.com`, `raw.githubusercontent.com`) — no new hosts allowed | Diff check against `src/lib/github-fetch.ts` ALLOWED_HOSTS in code review |
| S-5 | `VSKILL_GITHUB_APP_TOKEN` is never written to keychain or `.env` files | Code review + unit test that intercepts `setGitHubToken` calls |
| S-6 | Pre-install vskill scan still runs against every fetched SKILL.md before symlinking | No change to existing scan call site; verified by reading the diff |
| S-7 | SAML SSO preflight: when 403 with `X-Github-Sso` header, the SSO URL is shown in the error message verbatim | Unit test with mocked 403 response |

## Performance

| ID | Criterion | Verification |
|----|-----------|--------------|
| P-1 | Install issues at most 2 + N API calls (N = number of skills installed) | Mock-call counter in unit tests |
| P-2 | No call exceeds 1 MB request body | n/a — only GETs |
| P-3 | Existing retry-on-429/5xx behaviour preserved | Unit test injects 429s and asserts the retry loop fires |

## Code quality

| ID | Criterion | Verification |
|----|-----------|--------------|
| Q-1 | New helpers have ≥ 90% line coverage | `npx vitest run --coverage` shows new files at ≥ 90% |
| Q-2 | No file exceeds the project's 1500-line limit (per umbrella CLAUDE.md) | `wc -l src/**/*.ts \| awk '$1 > 1500'` returns empty |
| Q-3 | TypeScript strict mode passes (no new `any`) | `npm run typecheck` green |
| Q-4 | ESLint passes with no new warnings | `npm run lint` green |
| Q-5 | All public exports from new modules have JSDoc with at least the param + return tags | Code review |

## Documentation

| ID | Criterion | Verification |
|----|-----------|--------------|
| D-1 | `docs/private-repos.md` exists, walks through the canary repo end-to-end | Manual review against the doc rubric in spec.md AC-US4-01..04 |
| D-2 | The new ADR `ADR-vskill-private-repo-fetch-strategy.md` is committed and linked from `plan.md` | File exists; `grep -l ADR-vskill-private-repo-fetch-strategy plan.md` non-empty |
| D-3 | `README.md` mentions `vskill install --repo OWNER/PRIVATE-REPO` works (one sentence) | Manual review |

## Auditability

| ID | Criterion | Verification |
|----|-----------|--------------|
| A-1 | Every successful install records all 7 audit fields (`repo`, `branch`, `commit_sha`, `marketplace_hash`, `token_fingerprint_hash`, `installed_at`, `actor`) | Unit + integration tests assert presence and shape |
| A-2 | Audit entries are never overwritten — only appended | Unit test runs `recordInstall` 3× and asserts file has 3 entries |
| A-3 | Concurrent installs serialize correctly (no lost entries) | Unit test that races two `recordInstall` calls under the lock |

## Closure gates (mandatory before `sw:done`)

- `sw:code-reviewer` — zero critical/high findings; medium findings either
  fixed or explicitly waived in the closure report.
- `simplify` — runs and any flagged duplications either resolved or waived.
- `sw:grill` — written to `reports/grill-report.json`; no blocker findings.
- `sw:judge-llm` — written to `reports/judge-llm-report.json`; verdict ≥ 7/10.
- All tasks in `tasks.md` marked `[x]` with each Test Plan satisfied.
- `npx vitest run` and `npx playwright test` (if any e2e) green.

## Waiver policy

A criterion may be marked WAIVED only with an explicit one-line reason in the
closure report and the umbrella maintainer's approval. Default: zero waivers.

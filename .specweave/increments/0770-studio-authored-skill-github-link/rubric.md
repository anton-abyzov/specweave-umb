---
increment: 0770-studio-authored-skill-github-link
title: "Studio header — clickable GitHub link for locally-authored skills"
generated: 2026-04-26
source: hand-authored
version: "1.0"
status: active
---

# Quality Contract

## Acceptance Criteria

All ACs from spec.md must be satisfied with passing automated tests OR explicit manual verification:

- **AC-US1-01..04** — covered by integration tests TC-016, TC-017, TC-024, TC-025 in `authored-source-link.test.ts` + manual verification T-009 (steps 4–6).
- **AC-US2-01..03** — covered by tests TC-018, TC-019, TC-026 + lockfile-precedence test TC-024 + manual verification T-009 (step 7).
- **AC-US3-01..03** — covered by tests TC-021 (memoization), TC-022 (no-throw), TC-023 (bounded child_process count).

## Coverage Targets

- Unit (`parseGithubRemote`, `walkUpForGitRoot`): ≥ 95 % statements, ≥ 90 % branches.
- Integration (`detectAuthoredSourceLink`, modified `resolveSourceLink`): every branch hit at least once (lockfile-wins, authored-fall-through-success, authored-fall-through-no-git, authored-fall-through-non-github, untracked-skill-md fallback, cache-hit, error-path).
- Regression: existing `skill-metadata-source-link.test.ts` (6 cases) passes byte-identically.

## Code Quality Gates

- `npx vitest run src/eval-server/__tests__/` — 0 failures, 0 unintended skips.
- `npx tsc --noEmit` — 0 errors in `vskill` package.
- No `any` types in the new helpers; explicit return types on all new functions.
- No new ESLint warnings introduced.
- New helpers placed in `api-routes.ts` next to `resolveSourceLink` (cohesion); not split into a new module unless reuse appears.

## Behavioral Gates

- **TestLab/greet-anton**: studio header renders `↗` anchor that opens `https://github.com/anton-abyzov/greet-anton/blob/HEAD/SKILL.md` (or actual ls-files path). Verified manually in T-009.
- **Skill in non-git directory**: copy-chip renders, no link, no console error. Verified in T-009 step 7.
- **Skill in git repo with non-github remote** (gitlab/bitbucket): copy-chip renders, no link, no error.
- **Already-installed skill (lockfile present)**: existing 0737/0743 link still resolves to lockfile-recorded URL — NOT to the local git remote (regression check, T-009 step 8).
- **Skill in repo with untracked SKILL.md**: link still renders, points to filesystem-relative path that will resolve once committed and pushed.

## Performance Gates

- Cold detection (first call for a skill dir) ≤ 100 ms p95 on developer machine, including 2 git shell-outs (with 1500 ms timeout cap).
- Warm detection (cache hit) ≤ 1 ms (Map.get only).
- No additional `/api/skills` request latency for skills outside any git repo (short-circuits at `walkUpForGitRoot` with no shell-out).
- Initial `/api/skills` response time for a workspace of 20 skills increases by ≤ 1 s in the worst case (20 × 100 ms cold).

## Security Gates

- All `git` invocations use `execFileSync` with argv form (literal array). No `execSync`, no shell interpolation.
- All `cwd` values are derived from `skill.dir` (a controlled path produced by `scanSkills`) — never from user-supplied request bodies.
- `stdio` set to `["ignore", "pipe", "ignore"]` to silence stderr — prevents leaking workspace paths into logs.
- All git invocations wrapped in `try/catch` returning `{null, null}` — `buildSkillMetadata` never crashes due to git.
- 1500 ms `timeout` on every `execFileSync` call — prevents hung subprocesses from blocking studio responses.
- No new secrets, env vars, or credentials introduced.

## Documentation Gates

- Inline JSDoc on `parseGithubRemote`, `walkUpForGitRoot`, `detectAuthoredSourceLink` describing inputs, outputs, and fallback behavior.
- Inline comment on the new fall-through line in `resolveSourceLink` linking to increment ID `0770`.
- No README/architecture docs require updates — feature is internal to eval-server.

## Closure Gates (sw:done)

- `code-review-report.json` — 0 critical, 0 high, 0 medium findings.
- `/simplify` — no actionable simplifications outstanding (or all addressed).
- `grill-report.json` — produced.
- `judge-llm-report.json` — produced (or waived with consent denial).
- `sw:validate` — 0 rule violations.
- All 10 ACs across US-001/US-002/US-003 marked `[x]` in spec.md.
- All 9 tasks (T-001 through T-009) marked `[x]` in tasks.md.
- Closer agent verifies via `git status` that ALL implementation diff (api-routes.ts + new test file) is committed — not just the closer's own diff (per memory `feedback_closure_git_status_check.md`).
- Closer agent installs `vskill` at the candidate version and runs the studio for T-009 manual verification — does NOT ask the user to restart their session (per memory `feedback_self_install_vskill.md`).

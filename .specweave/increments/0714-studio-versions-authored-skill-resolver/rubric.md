---
increment: 0714-studio-versions-authored-skill-resolver
title: "Studio Versions: resolve owner/repo for authored skills"
generated: 2026-04-24
source: hand-authored
version: "1.0"
status: active
---

# Quality Contract

## Acceptance Criteria

All ACs from spec.md must be satisfied with passing automated tests OR explicit manual verification:

- AC-US1-01..04 — unit tests T-01..T-03, T-07 GREEN.
- AC-US2-01..02 — integration tests T-08; resolver call sites verified to be unchanged in number.
- AC-US3-01..03 — pre-existing test suite still green; T-03a explicitly covers lockfile path; T-03d covers bare-name fallback.

## Coverage Targets

- Unit (new module `skill-name-resolver.ts`): ≥ 95 % statements, ≥ 90 % branches.
- Integration (`/api/skills/.../versions*` proxy paths): every resolver branch (lockfile / authored / fallback) hit at least once.
- E2E (Studio Versions tab): manual verification recorded for `appstore` and `obsidian-brain` skills (T-09).

## Code Quality Gates

- `npx vitest run` — 0 failures, 0 skipped tests added.
- `npx tsc --noEmit` — 0 errors.
- ESLint (existing config) — 0 new warnings.
- No `any` types in the new module; explicit return types on all exported functions.
- New helpers exported via the module's index for testability (no test-only re-exports).

## Behavioral Gates

- For `appstore` (authored, has 2 platform versions), Studio Versions tab renders both 1.0.0 and 1.0.1 with timestamps from platform.
- For `obsidian-brain` (authored, has 6 platform versions), Studio Versions tab renders the full list, newest first.
- For a lockfile-installed skill (any pre-existing entry), no behavior change observed (regression check).
- For an authored skill in a directory with no git remote, Versions tab shows the existing "No version history available" empty state — no error toast.

## Performance Gates

- Cold resolve (first call for a skill name) ≤ 100 ms p95 on the developer machine, including the git shell-out.
- Warm resolve ≤ 1 ms p95 (Map lookup only).
- No additional outbound platform requests vs current behavior — same number of calls, just to the correct path.

## Security Gates

- All shell invocations use `execFile` with argv form. No `exec`, no shell interpolation.
- The plugin path passed to `git -C` is verified to resolve under the eval-server's repo root before invocation.
- No new secrets, env vars, or credentials handled.

## Documentation Gates

- Inline JSDoc on the three new exported functions describing the contract and fallback behavior.
- Increment closure notes record the manual verification screenshots / log lines for `appstore` and `obsidian-brain`.

## Closure Gates (sw:done)

- [x] PASS — `code-review-report.json` — 0 critical, 0 high, 0 medium, 2 low, 1 info findings. Re-review on 2026-04-24 confirms previously-flagged S1 (path-traversal boundary) is mitigated and L1 (proxy-contract test) is satisfied.
- `simplify` — no actionable simplifications outstanding.
- `grill-report.json` — produced.
- `judge-llm-report.json` — produced (or waived with consent denial).
- `sw:validate` — 0 rule violations.
- All 9 ACs marked `[x]` in spec.md.

## Security Gates Status (post-review)

- [x] PASS — Plugin-path boundary check is implemented: `findAuthoredSkillDir` at skill-name-resolver.ts:99 verifies `skillDir.startsWith(pluginsRootPrefix)` before returning, plus skill-name traversal rejection at lines 77-78 and plugin-name traversal rejection at lines 94-96. Test TC-02e exercises path-traversal skill names.

Evaluator: sw:code-reviewer | Date: 2026-04-24

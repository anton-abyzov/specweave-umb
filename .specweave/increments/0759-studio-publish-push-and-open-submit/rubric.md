---
increment: 0759-studio-publish-push-and-open-submit
title: "Studio: Publish (push + open pre-filled submit page)"
generated: "2026-04-26"
source: pm-derived
version: "1.0"
status: active
---

# Quality Rubric: 0759-studio-publish-push-and-open-submit

Auto-derived from spec.md acceptance criteria. Three-tier inheritance: P0 (blocking) → P1 (required) → P2 (advisory).

---

## P0 — Blocking Gates (must pass before merge)

These ACs represent correctness, security, and data-safety requirements.

| Gate | AC | Verification |
|---|---|---|
| No shell-string injection in git spawn | AC-US2-03 | Code review: `child_process.spawn` uses argv array, not `exec`/shell string |
| Workspace path validated before git exec | AC-US2-06 | Unit test: path outside allowlist is rejected before spawn |
| Browser NOT opened on push failure | AC-US3-05 | Unit test: error path → `window.open` never called |
| `window.open` uses `noopener,noreferrer` | AC-US3-01 | Code review: exact window features string present |
| Platform does NOT auto-submit | AC-US4-05 | E2E: page load with `?repo=` → form not submitted automatically |

---

## P1 — Required (all ACs must pass for closure)

### US-001: Publish button visibility
| AC | Check |
|---|---|
| AC-US1-01 | Render test: Publish button present when `hasRemote: true` |
| AC-US1-02 | Render test: Publish button absent (not in DOM) when `hasRemote: false` |
| AC-US1-03 | Interaction test: button disabled and shows loading while request in-flight |
| AC-US1-04 | Hook test: `useGitRemote` stores `{ remoteUrl, branch, hasRemote }` from GET /git-remote response |
| AC-US1-05 | Test: GET /git-remote failure → `hasRemote` defaults false → no button rendered |

### US-002: eval-server routes
| AC | Check |
|---|---|
| AC-US2-01 | Integration test: GET /git-remote with valid remote → `{ remoteUrl, branch, hasRemote: true }` |
| AC-US2-02 | Integration test: GET /git-remote with no remote → `{ remoteUrl: null, hasRemote: false }` HTTP 200 |
| AC-US2-03 | Unit test: POST /git-publish on exit 0 → `{ success: true, commitSha, branch, remoteUrl, stdout, stderr }` |
| AC-US2-04 | Unit test: POST /git-publish on non-zero exit → HTTP 500 `{ success: false, stderr }` |
| AC-US2-05 | Unit test: subprocess timeout (mock delay > GIT_PUBLISH_TIMEOUT_MS) → HTTP 500 `{ success: false, stderr: "timeout" }` |

### US-003: Success flow
| AC | Check |
|---|---|
| AC-US3-01 | Unit test: success response → `window.open` called once with correct URL |
| AC-US3-02 | Unit test: SSH URL `git@github.com:owner/repo.git` → normalized to `https://github.com/owner/repo` |
| AC-US3-03 | Unit test: HTTPS URL `https://github.com/owner/repo.git` → normalized to `https://github.com/owner/repo` |
| AC-US3-04 | Render/interaction test: success toast shows short SHA (7 chars), branch name, "Opening…" text |

### US-004: Platform pre-fill
| AC | Check |
|---|---|
| AC-US4-01 | Test: `?repo=https://github.com/owner/repo` → input value equals that URL on mount |
| AC-US4-02 | Test: no `?repo=` param → input empty |
| AC-US4-03 | Test: malformed `?repo=` → input empty, no error element rendered |
| AC-US4-04 | Test: pre-filled input can be edited (not read-only) |

---

## P2 — Advisory (tracked, non-blocking)

| Advisory | Rationale |
|---|---|
| `GIT_PUBLISH_TIMEOUT_MS` env var honored | Configurable timeout tested with non-default value |
| "Everything up-to-date" push treated as success | git push exits 0 → browser still opens |
| Concurrent Publish clicks blocked | Button disabled while in-flight — only one request possible |
| Zero new external npm dependencies | Verified by `npm ls` diff before/after |
| Unit coverage ≥ 90% for URL normalizer, subprocess wrapper, query-param pre-fill | Vitest coverage report |

---

## Closure Checklist

- [x] All P0 gates pass — all 5 P0 gates verified by `sw:grill` (no shell injection, factory-bound root, no window.open on failure, noopener,noreferrer literal, no platform auto-submit)
- [x] All P1 ACs verified (unit + integration + E2E) — 21/21 ACs covered, 19 PASS + 2 PASS_WITH_NIT (AC-US2-06 drift, AC-US3-04 toast literal)
- [x] Playwright E2E: e2e/0759-studio-publish.spec.ts — stubs both endpoints, asserts popup URL contains canonical https://github.com/owner/test-repo
- [x] No regression on existing Save button behavior — Publish button is additive (rendered after Save, gated on hasRemote)
- [x] No regression on existing /submit page when `?repo=` is absent — repoPrefill returns null on missing param, useEffect skips setRepoUrl, input remains empty (existing behavior)
- [x] `sw:grill` report generated — reports/grill-report.json (verdict PASS, shipReadiness READY, 0 critical, 0 high, 1 medium, 3 low)
- [x] `sw:code-reviewer` (re-run 2026-04-26 v5 post-judge-llm) — 0 CRITICAL, 0 HIGH, 1 MEDIUM (F-001 stale rubric closure-note — non-blocking documentation hygiene), 3 LOW, 1 INFO. All 21 ACs verified by tests. All 5 P0 gates pass. Spec FR-002 + AC-US2-06 are mutually consistent with factory-bound root design. Closure NOT blocked. See reports/code-review-report.json.
- [x] `sw:judge-llm` — verdict APPROVED, score 91/100. Ultrathink in-session (no ANTHROPIC_API_KEY). All security properties verified: argv-only spawn, factory-bound root, loopback+CSRF guards, noopener+noreferrer, platform no-auto-submit. Error surfacing (body.error) verified correct. One LOW finding (req.socket?.remoteAddress defensive null check) fixed. See reports/judge-llm-report.json.

## Evaluator Results (sw:grill)

| Gate | Evaluator | Result |
|---|---|---|
| No shell-string injection in git spawn | sw:grill | [x] PASS — argv arrays only, verified by test git-routes.test.ts:157-173 (GET) and 261-278 (POST) |
| Workspace path validated before git exec | sw:grill | [x] PASS — root bound at registerGitRoutes(router, root) factory time; no per-request path; loopback IP + Origin CSRF guards; tests at git-routes.test.ts:175-193, 280-302 |
| Browser NOT opened on push failure | sw:grill | [x] PASS — verified by PublishButton.test.tsx:122-143 |
| `window.open` uses `noopener,noreferrer` | sw:grill | [x] PASS — PublishButton.tsx:42 hardcoded literal; PublishButton.test.tsx:88-89 substring check |
| Platform does NOT auto-submit | sw:grill | [x] PASS — submit/page.tsx useEffect only setRepoUrl; no fetch on mount; repoPrefill is pure |
| AC-US2-06 (workspace path validation) | sw:grill | [x] PASS — factory-bound root design eliminates path traversal architecturally; spec wording drift surfaced as F-G001 (medium, no behavior bug) |
| AC-US3-04 (success toast format) | sw:grill | [x] PASS — short SHA (7 chars), branch, 'opening' all present. Spec literal '…' (ellipsis) absent — surfaced as F-G003 (low, cosmetic) |

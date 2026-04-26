---
increment: 0738-vskill-platform-auth-refresh-401-fix
title: "vskill-platform: fix intermittent 401 on /api/v1/auth/user/refresh"
generated: "2026-04-25"
source: hand-authored
version: "1.0"
status: active
---

# Quality Contract

## Acceptance gate (must all be GREEN to close)

| ID | Criterion | Verification |
|---|---|---|
| Q-01 | All tasks T-001..T-013 marked `[x] completed` in `tasks.md` | `grep -c '\[x\] completed' tasks.md` = 13 |
| Q-02 | All ACs in `spec.md` flipped to `[x]` | `grep -c '\[x\] \*\*AC-' spec.md` = 12 |
| Q-03 | `npx vitest run` returns exit 0 in `repositories/anton-abyzov/vskill-platform` | CI log |
| Q-04 | Concurrent-refresh unit test (T-001) asserts both responses 200 | Inspect test source |
| Q-05 | Grace-window expiry unit test (T-002) asserts 401 with replay-detection body | Inspect test source |
| Q-06 | `route.ts` retry loop on lines 96-120 (transient DB errors) preserved | Diff review |
| Q-07 | `auth-fetch.ts` no longer declares its own `refreshPromise` | `grep -c 'let refreshPromise' src/lib/auth-fetch.ts` = 0 |
| Q-08 | `AuthProvider.tsx` no longer declares `refreshingRef` | `grep -c 'refreshingRef' src/app/components/AuthProvider.tsx` = 0 |
| Q-09 | `auth-cookies.ts` uses `sameSite: "lax"` exclusively | `grep -c 'sameSite: "strict"' src/lib/auth-cookies.ts` = 0 |
| Q-10 | `middleware.ts` Origin allowlist unchanged | Diff review (no modifications expected) |
| Q-11 | `sw:code-reviewer` report shows zero critical/high/medium findings on the auth surface | [x] PASS — 0 critical, 0 high, 0 medium. F-001/F-004/F-005 resolved; F-006 collapsed; F-002 deferred per spec Out of Scope; F-003 accepted with trade-off documented. Re-review 2026-04-25 — see `reports/code-review-report.json`. |
| Q-12 | `sw:grill` `grill-report.json` written | [x] PASS — re-grill 2026-04-25T23:15Z: verdict=PASS / shipReadiness=READY. All 4 prior HIGH findings resolved (F-G01 id-equality short-circuit removed → unconditional setUser; F-G02 vacuous cold-load E2E removed and AC-US3-02 reframed to unit-asserted+manual; F-G03 consumer now guards on `success && refreshedUser`; F-G07 race E2E uses two independent APIRequestContexts). F-G04/F-G05 accepted with threat-model language in spec.md "Known limitations". 12/12 ACs PASS. 19/19 unit tests GREEN. 4 medium follow-up findings remain (F-G06/F-G08/F-G09/F-G11) — all pre-existing or defense-in-depth, none blockers. See `reports/grill-report.json`. |

## Quality bar (correctness)

- **Correctness**: server returns 200 for any concurrent refresh within the 10 s grace window; 401 outside it. Replay-detection signal preserved for legitimately stale tokens.
- **Determinism**: tests use `vi.useFakeTimers` for the 500 ms client TTL and the 10 s server window — no flakiness from real time.
- **Idempotency**: a duplicate refresh fires exactly one network call within a 500 ms client window; both retrieved by separate components if needed.
- **Backward compat**: existing `Strict` cookies continue to work for their TTL; no forced re-login on rollout.

## Quality bar (security)

- CSRF defense: `middleware.ts` Origin allowlist remains the active defense. `Lax` is the OWASP default for auth cookies.
- Replay defense: 10 s window is short enough that an attacker without the cookie plaintext cannot trigger the path; the OLD token is already deleted by the legitimate winner.
- No new env vars, no JWT secret changes, no new external dependencies.

## Quality bar (performance)

- Server: +1 indexed `findFirst` (uses `UserRefreshToken.userId` index) only on `count===0` race path. Negligible overhead.
- Client: removes a redundant network round-trip whenever AuthProvider mount/visibility races `authFetch` 401-retry. Net throughput improves.

## Definition of done

1. All gates Q-01..Q-12 GREEN.
2. `sw:code-reviewer` findings zero (or resolved) at critical/high/medium.
3. `simplify` pass run and any duplications collapsed.
4. `sw:grill` report written; objections addressed.
5. `sw:judge-llm` report written (or waived per consent).
6. Increment status flipped to `closed` via `sw:done`.

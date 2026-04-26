---
increment: 0746-studio-diff-proxy-502-masking
title: Studio diff proxy masks every non-2xx as 502 Platform API unavailable
type: bug
priority: P2
status: completed
created: 2026-04-26T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Stop the studio diff proxy from masking every non-2xx as `502 Platform API unavailable`

## Overview

`vskill/src/eval-server/api-routes.ts:1908-1921` proxies `GET /api/skills/:plugin/:skill/versions/diff` to the platform. When the platform replies with a legitimate `400` (`Version 'X' not found`) or `404` (`Skill not found`), the proxy silently drops the upstream status + body and emits the hardcoded:

```ts
sendJson(res, { error: "Platform API unavailable" }, 502, req);
```

Concrete repro from production:
- `GET /api/skills/greet-anton/greet-anton/versions/diff?from=1.0.1&to=1.0.2`
- Platform direct: `400 {"error":"Version '1.0.1' not found"}` — the installed v1.0.1 was never published upstream (only v1.0.2 is registered)
- Studio proxy: `502 {"error":"Platform API unavailable"}` — wrong status, wrong message, hides the real reason

The user sees a 502 in the network panel, assumes the platform is down, and the diff viewer renders nothing.

The sibling proxy at `/versions` (line 1861) already handles non-2xx correctly — it gracefully degrades to an empty envelope. The diff proxy is the outlier.

## User Stories

### US-001: Real upstream errors reach the studio (P2)
**Project**: vskill (CLI / eval-server)

**As a** Skill Studio user
**I want** the diff endpoint to return the platform's real status code and error message
**So that** I can tell whether the request failed because of bad input ("version not published") versus a genuine platform outage

**Acceptance Criteria**:
- [x] **AC-US1-01**: When the upstream platform returns `400 {error}`, the studio proxy returns `400` with the same body — NOT `502 Platform API unavailable`.
- [x] **AC-US1-02**: When the upstream returns `404 {error}`, the proxy returns `404` with the same body.
- [x] **AC-US1-03**: When the upstream returns any non-2xx with a non-JSON body, the proxy returns the same status with `{error: "Upstream returned <status>"}` as the body.
- [x] **AC-US1-04**: When the upstream is unreachable (fetch throws / timeout), the proxy continues to return `502 {error: "Platform API unavailable"}` — that is the correct semantic for genuine network failures.
- [x] **AC-US1-05**: 2xx happy path is unchanged — same body, same headers, same 200 status.

### US-002: TDD coverage gates the fix (P1)
**Project**: vskill

**As a** maintainer
**I want** every behavior change preceded by a failing test
**So that** the bug stays fixed

**Acceptance Criteria**:
- [x] **AC-US2-01**: Existing tests in `vskill/src/eval-server/__tests__/version-routes.test.ts` continue to pass unchanged.
- [x] **AC-US2-02**: New tests cover AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 — each fails before the proxy fix and passes after.

## Functional Requirements

### FR-001: Pass-through on non-2xx
The diff proxy MUST forward the upstream `resp.status` and parsed body verbatim on non-2xx, with a safe fallback envelope when the upstream body cannot be parsed as JSON.

### FR-002: Fetch failure stays as 502
When `fetch()` itself throws (DNS failure, timeout, connection refused), the proxy MUST keep returning `502 Platform API unavailable`. That is the only case where "platform unavailable" is true.

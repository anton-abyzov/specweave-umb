# 0855 — Tasks

### T-001: RED — extend router-token-gate.test.ts with query-param-token gate cases
**AC**: AC-US1-01, AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06
**Test**: Given the eval-server tokenGate -> When GET /api/v1/skills/stream carries a valid ?studioToken -> Then it passes, the token is stripped from req.url, and is never logged; wrong/missing token and POST/non-stream paths are still 401.
**Status**: [x] completed

### T-002: RED — new integration test sse-stream-token-gate.test.ts (real eval-server)
**AC**: AC-US1-03, AC-US2-01, AC-US2-02
**Test**: Given a running eval-server -> When an SSE request opens /api/v1/skills/stream?studioToken=<valid> -> Then it returns 200 with content-type text/event-stream (NOT 401); without/with wrong token returns 401.
**Status**: [x] completed

### T-003: GREEN — router.ts tokenGate query-param-token exemption + strip + no-log
**AC**: AC-US1-01, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06
**Test**: Given the new test suites -> When tokenGate runs -> Then valid query token on a known GET stream path passes, studioToken is deleted from req.url before return, and no log line contains the token.
**Status**: [x] completed

### T-004: GREEN — StudioTokenBridge getStudioTokenForUrl() getter
**AC**: AC-US1-02
**Test**: Given the injected token script in the DOM -> When getStudioTokenForUrl() is called -> Then it returns the cached/DOM token synchronously for EventSource URL building.
**Status**: [x] completed

### T-005: GREEN — useSkillUpdates appends ?studioToken to the EventSource URL
**AC**: AC-US1-02
**Test**: Given a resolved studio token -> When the notification EventSource URL is built -> Then it includes &studioToken=<token>; when no token is present the URL is unchanged.
**Status**: [x] completed

### T-006: REFACTOR + scoped test run
**AC**: AC-US1-01, AC-US1-03, AC-US2-01..06
**Test**: Given all changes -> When `npx vitest run src/eval-server` is run -> Then the token-gate and SSE suites pass with no regressions in the eval-server scope.
**Status**: [x] completed

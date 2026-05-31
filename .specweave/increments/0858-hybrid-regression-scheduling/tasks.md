# 0858 — Tasks

### T-001: GitHub Actions twice-daily golden-path workflow
**AC**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: Given the workflow file → When parsed → Then it has a `schedule` cron `0 6,18 * * *` + `workflow_dispatch`, and steps run `npm run build`, `npm run build:eval-ui`, `npm run verify`, `npm run verify:matrix`.
- Created `.github/workflows/golden-path-nightly.yml`; YAML validated; cron + 9 steps confirmed.

### T-002: No-secret core lane + optional gated lanes
**AC**: AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Test**: Given no secrets → When the workflow runs → Then the stub lane + loud-skip gate run unconditionally; the anthropic lane runs only `if env.ANTHROPIC_API_KEY != ''` (continue-on-error) and the Slack step only `if failure() && env.SLACK_WEBHOOK_URL != ''`.
- Secrets mapped to job-level env (secrets context unavailable in `if:`); both optional steps gated on env.

### T-003: Mac-local scheduled task for the local-model leg
**AC**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test**: Given `mcp__scheduled-tasks` → When `vskill-regression-daily` fires → Then it runs `npm run verify` in the vskill repo on the real claude-cli default + a local model, asserting provider availability first.
- Created via `mcp__scheduled-tasks` on Anton's Mac, twice-daily local time.

### T-004: Verify the workflow's exact commands pass locally
**AC**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test**: Given the vskill repo → When `npm run build && npm run build:eval-ui && npm run verify && npm run verify:matrix` runs → Then verify is Overall: PASS and matrix is 4/4.
- Confirmed locally this session (Overall: PASS, 12/12 units; matrix 4/4).

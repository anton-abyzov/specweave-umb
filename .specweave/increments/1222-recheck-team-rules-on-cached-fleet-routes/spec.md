# 1222 Recheck Team Rules on cached fleet routes

## Problem

After Connect is disabled, a fleet caller can reuse a cached Connect route.

## Acceptance Criteria

- [ ] AC-01 Tightening Connect policy prevents issuing further authorization on the cached Connect route and allows discovery of another eligible route.

## Approach

Recheck route policy at the authorization boundary and refresh a remembered route when Connect is disabled. Verify with mock fleet hosts.

## Tasks

### T-01 Honor current Connect policy for cached calls

- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/fleet/fleetTransport.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/fleet/fleetTransport.teamRules.test.ts | Test: cd "$HOME/.specwithcode/m4/worktrees/specwithcode-dev/recent-features-followup-20261103/apps/server" && node ../../node_modules/vite-plus/bin/vp test run src/fleet/fleetTransport.teamRules.test.ts --maxWorkers=1

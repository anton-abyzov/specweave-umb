# 1221 Recognize configured SpecWeave projects before the first increment

## Problem

A checkout with a valid SpecWeave config but no increments directory skips launch guidance.

## Acceptance Criteria

- [ ] AC-01 Launches in a config-only checkout honor the configured increment policy and planning guidance.

## Approach

Recognize the existing regular config marker alongside the existing directory check.

## Tasks

### T-01 Recognize config-only checkouts

- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/launchIncrement.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/launchIncrement.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/ThreadIncrementProgress.ts | Test: cd "repositories/anton-abyzov/specwithcode-dev/apps/server" && node ../../node_modules/vite-plus/bin/vp test run src/project/launchIncrement.test.ts --maxWorkers=1

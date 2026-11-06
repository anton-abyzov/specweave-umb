# 1218 Share the final result of concurrent file transfer retries

## Problem

Overlapping retries of the final chunk can both publish the staged file. One reports failure even though the correct file was saved.

## Scope

Receiving an already authorized file offer and retrying its last chunk.

## Acceptance Criteria

- [ ] AC-01 Concurrent identical final requests share the same result and publish the file once.

## Approach

Set the finalization promise before awaiting the final write, so retries join it. Once accepted, the final request owns publication. Keep the staged file and handle cleanup on finalization failure.

## Tasks

### T-01 Reserve finalization before writing the final chunk

- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/fleet/fileTransfer/offers.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/fleet/fileTransfer/files.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/fleet/fileTransfer/files.test.ts | Test: cd "repositories/anton-abyzov/specwithcode-dev/apps/server" && node ../../node_modules/vite-plus/bin/vp test run src/fleet/fileTransfer/files.test.ts --maxWorkers=1

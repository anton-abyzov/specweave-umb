# 1198 Keep folder copy previews scoped to their source machine

## Problem

Completing a copy can cancel an unrelated preview when two source machines use the same project ID. A supersession racing a person’s approval can also cancel the just-approved transfer.

## Scope

Match superseded folder copy previews by source machine as well as project and destination. Serialize automatic closure with approval.

## Acceptance Criteria

- [ ] AC-01 A later copy from another source machine leaves the existing preview available.

- [ ] AC-02 Approval and automatic cancellation cannot both commit the same preview.

## Approach

Include the source environment in the existing supersession predicate. Guard and persist the preview cancellation under the same operation lock as approval. Test matching project and destination fields and a concurrent approval.

## Tasks

### T-01 Scope supersession by source environment

- AC: AC-01 , AC-02 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/fleet/folderTransfer/destinationService.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/fleet/folderTransfer/destinationService.superseded.test.ts | Test: cd "repositories/anton-abyzov/specwithcode-dev/apps/server" && node ../../node_modules/vite-plus/bin/vp test run src/fleet/folderTransfer/destinationService.superseded.test.ts

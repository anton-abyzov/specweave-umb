# 1220 Isolate overlapping Chrome uploads by transfer

## Problem

Two uploads to the same browser tab share a buffer and can attach each other's bytes.

## Scope

Buffer ownership and cleanup in the existing upload command.

## Acceptance Criteria

- [ ] AC-01 Simultaneous uploads in one page cannot read or clear each other's buffered bytes.

## Approach

Allocate a unique buffer key per operation and use it for append, finalization and failure cleanup. Exercise interleaving with a simulated DOM.

## Tasks

### T-01 Isolate upload buffers

- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/browserExtension/chromeTools.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/browserExtension/pageScripts.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/browserExtension/chromeTools.test.ts | Test: cd "repositories/anton-abyzov/specwithcode-dev/apps/server" && node ../../node_modules/vite-plus/bin/vp test run src/browserExtension/chromeTools.test.ts --maxWorkers=1

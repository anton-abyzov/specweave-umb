# 1203 Keep undelivered relay notes visible after unrelated direct messages

## Problem

A later direct user message can hide an old undelivered relay note merely by repeating its words.

## Scope

Keep the historical relay display. Exclude direct user messages from its delivery inference.

## Acceptance Criteria

- [ ] AC-01 A later directly typed message containing the same words leaves the note visible.
- [ ] AC-02 A message sent by an agent or forwarded by a thread can still satisfy the legacy inference.

## Approach

Use the recorded creator and sender before applying the existing text heuristic. Retain conservative history coverage behavior.

## Tasks

### T-01 Exclude direct messages from relay inference

- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/projectCoordinatorMessageDisplay.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/studio/projectCoordinatorMessageDisplay.test.ts | Test: cd "repositories/anton-abyzov/specwithcode-dev/apps/web" && node ../../node_modules/vite-plus/bin/vp test run src/studio/projectCoordinatorMessageDisplay.test.ts

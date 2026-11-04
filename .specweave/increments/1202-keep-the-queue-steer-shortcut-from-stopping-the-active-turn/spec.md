# 1202 Keep the queue steer shortcut from stopping the active turn

## Problem

The keyboard command described as steering into the current turn can stop it when the oldest queued row uses a different model.

## Scope

Keep the shortcut limited to rows that offer Steer now. Retain the explicit Run now button for model-changing rows.

## Acceptance Criteria

- [ ] AC-01 The shortcut cannot promote a Run now row or skip ahead of it.
- [ ] AC-02 The shortcut still steers the oldest eligible same-model row.

## Approach

Use the queue row's existing picked-model marker to decline the keyboard action. Exercise the imperative shortcut and the existing explicit button through the DOM test.

## Tasks

### T-01 Guard the Steer shortcut

- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/QueuedRunsControl.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/QueuedRunsControl.dom.test.tsx | Test: cd "repositories/anton-abyzov/specwithcode-dev/apps/web" && node ../../node_modules/vite-plus/bin/vp test run src/components/chat/QueuedRunsControl.dom.test.tsx

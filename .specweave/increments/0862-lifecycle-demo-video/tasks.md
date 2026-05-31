# 0862 — Tasks

### T-001: `anton-grid` demo skill fixture (v1.0.0)
**AC**: AC-US1-01 | **Status**: [x] completed
**Test**: An authored `anton-grid` skill exists under e2e/fixtures with version 1.0.0, exposing the editor (Edit tab) + Publish button in the studio.

### T-002: Playwright video-demo spec (continuous lifecycle + captions)
**AC**: AC-US1-01..03, AC-US2-01 | **Status**: [x] completed
**Test**: One continuous test drives select → bump version → in-app submit (no popup) → My Queue RECEIVED → injected APPROVED → bell → update-locally, with a per-step caption overlay and `video:'on'`, producing a `.webm`.

### T-003: Run + produce the recording
**AC**: AC-US1-01..03 | **Status**: [x] completed
**Test**: Running the spec yields a `.webm` of the full flow with no error states.

### T-004: ffmpeg post-process → mp4 + title card
**AC**: AC-US1-04 | **Status**: [x] completed
**Test**: A script converts the `.webm` → h264 `.mp4` with an intro title card; the final mp4 is delivered.

### T-005: Fix any UI bug hit during recording
**AC**: AC-US2-01 | **Status**: [x] completed
**Test**: If a step is broken, the minimal product fix lands (and deploys/publishes if needed) so the recorded flow is clean.

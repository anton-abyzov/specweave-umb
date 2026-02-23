# Tasks: 0329-homepage-video-first-redesign

## Phase 1: Asset Setup

### T-001: Copy video to docs-site static
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given video at video/out/ -> When copied to docs-site/static/video/ -> Then file exists and is accessible

### T-002: Generate video poster image
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given video file -> When ffmpeg extracts first frame -> Then poster.jpg exists

## Phase 2: Homepage Rewrite

### T-003: Rewrite index.tsx with 5 sections
**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: AC-US1-01 through AC-US4-02 | **Status**: [x] completed
**Test**: Given new TSX -> When rendered -> Then 5 sections visible: VideoHero, Workflow, Capabilities, Trust, CTA

### T-004: Rewrite index.module.css with new design
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01 through AC-US5-04 | **Status**: [x] completed
**Test**: Given new CSS -> When page loads -> Then dark hero, whitespace, responsive layout, dark mode all work

## Phase 3: Verification

### T-005: Build verification
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test**: Given rewritten files -> When npm run build -> Then build succeeds with no errors

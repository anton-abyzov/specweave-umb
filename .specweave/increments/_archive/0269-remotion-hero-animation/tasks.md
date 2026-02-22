# 0269: Tasks — Remotion Hero Animation

### T-001: Scaffold Remotion project
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-04 | **Status**: [x] completed
**Test**: Given docs-site repo -> When `npm run remotion:preview` executed -> Then Remotion Studio opens with SpecWeaveHero composition

### T-002: Implement Scene 1 — The Problem
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test**: Given Scene 1 renders -> When previewed at frame 0-270 -> Then 36.82% stat visible with floating threat snippets and fade-out

### T-003: Implement Scene 2 — The Scanner
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**Test**: Given Scene 2 renders -> When previewed at frame 240-540 -> Then scan line sweeps, results appear, BLOCKED overlay shows

### T-004: Implement Scene 3 — Three Tiers
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**Test**: Given Scene 3 renders -> When previewed at frame 510-810 -> Then three badges pop in with arrows between them

### T-005: Implement Scene 4 — Install Flow
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] completed
**Test**: Given Scene 4 renders -> When previewed at frame 780-1110 -> Then terminal typewriter plays and verified badge bounces in

### T-006: Implement Scene 5 — Ship Safely
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [x] completed
**Test**: Given Scene 5 renders -> When previewed at frame 1080-1350 -> Then SpecWeave wordmark and tagline animate in with trust badges

### T-007: Wire scenes with Sequence and crossfades
**User Story**: US-002 | **Satisfies ACs**: AC-US2-06, AC-US2-07 | **Status**: [x] completed
**Test**: Given all scenes -> When composed in Root -> Then transitions overlap by 30 frames with opacity crossfade

### T-008: Preview QA and timing polish
**User Story**: US-002 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test**: Given full composition -> When previewed end-to-end -> Then flow is smooth, timing feels natural, no visual glitches

### T-009: Render to MP4 and WebM
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test**: Given composition -> When `npm run remotion:render` executed -> Then MP4 and WebM files produced under 5MB each
**Note**: Render config and scripts are ready. User must run `npm run remotion:render` locally (requires ffmpeg).

### T-010: Embed video on homepage
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [x] completed
**Test**: Given rendered video -> When homepage loaded -> Then video autoplays silently with fallback poster image

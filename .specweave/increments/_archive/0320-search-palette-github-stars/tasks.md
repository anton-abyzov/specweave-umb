# 0320 — Tasks

## Tasks

### T-001: Write test for search API returning githubStars
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given a search query matching a skill → When GET /api/v1/skills/search?q=name → Then response.results[].githubStars is a number
**Details**: Create `src/app/api/v1/skills/search/__tests__/route.test.ts`. Mock `getSkills` to return a skill with `githubStars: 3240`. Assert the response includes `githubStars` field.

### T-002: Add githubStars to search API response
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given T-001 test exists → When route.ts maps `githubStars: s.githubStars` → Then T-001 passes
**Details**: Add `githubStars: s.githubStars` to the results mapping in `src/app/api/v1/skills/search/route.ts`.

### T-003: Write test for star count formatting
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test**: Given formatStarCount function → When called with 0 → Then returns "" | When 500 → Then "500" | When 3240 → Then "3.2k" | When 15800 → Then "15.8k"
**Details**: Unit test for the formatting helper. Can be in SearchPalette test file or a shared test.

### T-004: Write test for SearchPalette rendering stars
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Test**: Given SearchPalette with skill results → When githubStars > 0 → Then star icon and count visible | When githubStars = 0 → Then no star display
**Details**: Create `src/app/components/__tests__/SearchPalette.test.tsx`. Render component, mock fetch to return results with and without stars.

### T-005: Add githubStars to SearchPalette interface and display
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Test**: Given T-003 and T-004 tests → When SearchPalette changes implemented → Then all tests pass
**Details**:
- Add `githubStars: number` to `SearchResult` interface
- Add `formatStarCount` helper
- Add star SVG icon + formatted count in result row between repo URL and tier badge
- Thread `githubStars` through `allItems` mapping
- Conditionally render only when `githubStars > 0`

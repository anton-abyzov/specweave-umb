# 0267: Tasks — Skills Docs URL Restructure

### T-001: Move extensible-skills.md to docs/skills/
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given `docs/guides/extensible-skills.md` exists -> When moved to `docs/skills/extensible-skills.md` -> Then file exists at new location and old location is empty

### T-002: Move skills-related guides to docs/skills/
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [x] completed
**Test**: Given 5 skill guides in `docs/guides/` -> When moved to `docs/skills/` -> Then all 5 exist at new paths

### T-003: Add redirects for all moved files
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-02, AC-US1-05, AC-US2-06 | **Status**: [x] completed
**Test**: Given redirect config in `docusaurus.config.ts` -> When visiting old URL -> Then redirected to new URL

### T-004: Update sidebars.ts paths
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-03, AC-US2-07 | **Status**: [x] completed
**Test**: Given sidebars.ts references `guides/extensible-skills` -> When updated -> Then references `skills/extensible-skills`

### T-005: Update all internal cross-references
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test**: Given internal links pointing to old paths -> When grep finds and updates all -> Then zero references to old paths remain

### T-006: Build verification
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test**: Given all files moved and links updated -> When `npm run build` runs -> Then zero broken link warnings for moved pages

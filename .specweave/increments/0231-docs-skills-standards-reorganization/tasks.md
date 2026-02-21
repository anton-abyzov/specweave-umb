# Tasks: Skills Documentation Reorganization

### T-001: Create Extensible Skills pillar directory and move files
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test**: Given skills docs → When extensible/ dir created and files moved → Then extensible-skills.md, claude-skills-deep-dive.md, self-improving-skills.md, skill-development-guidelines.md exist under skills/extensible/

### T-002: Create Verified Skills pillar directory and move files
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test**: Given skills docs → When verified/ dir created and files moved → Then verified-skills.md, secure-skill-factory-standard.md, skills-ecosystem-security.md exist under skills/verified/

### T-003: Create Extensible Skills hub index page
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test**: Given extensible/ dir → When index.md created → Then it has overview text and links to all 4 extensible docs

### T-004: Create Verified Skills hub index page
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**Test**: Given verified/ dir → When index.md created → Then it has overview text, trust tier summary, and links to all 3 verified docs

### T-005: Update main Skills index page
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test**: Given skills/index.md → When updated → Then links point to pillar hub pages

### T-006: Update sidebars.ts with new doc IDs
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed
**Test**: Given sidebars.ts → When skillsSidebar updated → Then doc IDs match new file paths

### T-007: Add redirects for moved pages
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03 | **Status**: [x] completed
**Test**: Given docusaurus.config.ts → When redirects added → Then old URLs redirect to new locations

### T-008: Update cross-references in all moved files
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [x] completed
**Test**: Given moved files → When cross-references updated → Then all internal links use new paths

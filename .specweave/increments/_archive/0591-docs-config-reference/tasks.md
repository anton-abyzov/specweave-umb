---
increment: 0591-docs-config-reference
---

# Tasks: Configuration Reference Documentation Page

## Phase 1: Research & Content Gathering

### T-001: Audit source types for config.json properties
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**AC**: AC-US1-03
**Test**: Given `src/core/config/types.ts` exists → When all top-level sections of `SpecWeaveConfig` are enumerated → Then every section listed in AC-US1-03 is accounted for with property name, type, and default value

### T-002: Audit source types for metadata.json properties
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**AC**: AC-US1-04
**Test**: Given `src/core/types/increment-metadata.ts` exists → When all fields of `IncrementMetadataV2` are enumerated → Then every field listed in AC-US1-04 is accounted for with type and purpose

### T-003: Collect all SPECWEAVE_* environment variables from source
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed
**AC**: AC-US1-05
**Test**: Given the specweave source repo → When `process.env.SPECWEAVE_*` usages are grepped → Then all env vars listed in AC-US1-05 are found plus any additional ones

---

## Phase 2: Create Documentation Page

### T-004: Create configuration.md with frontmatter and introduction
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**AC**: AC-US1-01
**Test**: Given the docs-site → When `docs/reference/configuration.md` is created with valid Docusaurus frontmatter → Then the file exists at the correct path and the introduction explains what config.json is, where it lives, and how to edit it

### T-005: Add Disableable Features quick-reference table
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed
**AC**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Test**: Given the configuration.md page → When the "Quick Reference: Disableable Features" section is rendered → Then a table with columns Feature/Config Path/Value to Disable/Default appears after the introduction and documents all 20 features listed in AC-US2-03, with a note about living docs tradeoffs

### T-006: Document config.json Core & Project sections
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-06, AC-US1-07 | **Status**: [x] completed
**AC**: AC-US1-03, AC-US1-06, AC-US1-07
**Test**: Given the config.json reference section → When Core (`version`, `language`) and `project` sections are documented → Then each has a property table (name/type/default/description), valid enum values listed, and a JSON usage example

### T-007: Document config.json Testing, Limits, and Planning sections
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-06, AC-US1-07 | **Status**: [x] completed
**AC**: AC-US1-03, AC-US1-06, AC-US1-07
**Test**: Given the config.json reference section → When `testing`, `grill`, `limits`, `planning`, `incrementAssist` sections are documented → Then each has property tables with types/defaults and JSON examples, and enum values (tddEnforcement, defaultTestMode) are listed

### T-008: Document config.json Sync & Integrations sections
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-06 | **Status**: [x] completed
**AC**: AC-US1-03, AC-US1-06
**Test**: Given the config.json reference section → When `sync` (enabled, direction, autoSync, profiles, github, jira, ado, orchestration), `hooks`, and `issueTracker` are documented → Then property tables cover all sub-properties with defaults and a realistic JSON example is included

### T-009: Document config.json Living Docs, Docs, and API Docs sections
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-06 | **Status**: [x] completed
**AC**: AC-US1-03, AC-US1-06
**Test**: Given the config.json reference section → When `livingDocs`, `documentation`, and `apiDocs` sections are documented → Then copyBasedSync and threeLayerSync sub-properties appear with enabled/disabled examples

### T-010: Document config.json CI/CD, Repository, and Umbrella sections
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-06 | **Status**: [x] completed
**AC**: AC-US1-03, AC-US1-06
**Test**: Given the config.json reference section → When `cicd`, `repository`, and `umbrella` sections are documented → Then pushStrategy enum values are listed and umbrella childRepos structure is shown with an example

### T-011: Document config.json AI & Automation and Advanced sections
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-06, AC-US1-07 | **Status**: [x] completed
**AC**: AC-US1-03, AC-US1-06, AC-US1-07
**Test**: Given the config.json reference section → When `auto`, `reflect`, `contextBudget`, `skillGen`, `adapters`, `archiving`, `deduplication`, `statusLine`, `pluginAutoLoad`, `translation`, `multiProject`, `projectMappings` are documented → Then all top-level keys from AC-US1-03 Advanced list are covered with property tables

### T-012: Document metadata.json reference
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, AC-US1-07 | **Status**: [x] completed
**AC**: AC-US1-04, AC-US1-07
**Test**: Given the metadata.json reference section → When all fields from `IncrementMetadataV2` are documented across Core/Lifecycle/External/Multi-project/CI-CD categories → Then every field listed in AC-US1-04 appears with type and description, and IncrementStatus + IncrementType enum values are listed

### T-013: Document environment variables reference
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed
**AC**: AC-US1-05
**Test**: Given the environment variables section → When all SPECWEAVE_* vars and credential vars are documented → Then every variable listed in AC-US1-05 appears with purpose and example value, and a security note warns against hardcoding credentials

---

## Phase 3: Integration

### T-014: Add configuration.md to sidebars.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**AC**: AC-US1-02
**Test**: Given `sidebars.ts` in docs-site → When `{type: 'doc', id: 'reference/configuration', label: 'Configuration Reference'}` is added after the Skills & Cost category → Then the sidebar renders configuration.md under the Reference section

### T-015: Update reference/index.md Quick Navigation
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**AC**: AC-US1-01
**Test**: Given `reference/index.md` → When a "Configuration Reference" entry is added to the Quick Navigation section linking to `./configuration` → Then users can reach the page from the Reference overview

---

## Phase 4: Verification

### T-016: Build docs-site and verify no broken links or MDX errors
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-02
**Test**: Given the docs-site with the new configuration.md → When `npm run build` is executed in the docs-site directory → Then the build completes with zero errors, no broken internal links, and the new page is included in the output

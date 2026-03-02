# FS-408: GitHub Sync Smoke Test 4 - AC Markers Section

## Overview
Fourth smoke test: validates that the `<!-- specweave:ac-start --><!-- specweave:ac-end -->` markers section in the GitHub issue body is populated with AC checkboxes during auto-create, and that AC sync correctly updates checkboxes.

## User Stories

### US-001: Validate AC Markers Section Population
**As a** SpecWeave user
**I want** the structured AC markers section in the GitHub issue body to contain AC checkboxes
**So that** external tooling can parse AC progress from the structured section

#### Acceptance Criteria
- [x] AC-US1-01: GitHub issue body contains AC checkboxes inside the specweave:ac-start/end markers
- [x] AC-US1-02: After marking ACs complete, the checkboxes in the markers section show [x]

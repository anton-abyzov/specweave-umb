# Tasks: Update umbrella project documentation

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## User Story: US-001 - Update Umbrella Documentation

**Linked ACs**: AC-US1-01, AC-US1-02
**Tasks**: 2 total, 2 completed

### T-001: Document distributed vs centralized sync modes in README

**User Story**: US-001
**Satisfies ACs**: AC-US1-01
**Status**: [x] completed

**Test Plan**:
- **Given** the umbrella README
- **When** a user reads the sync section
- **Then** it describes distributed vs centralized sync modes

**Implementation**:
1. Add sync modes section to README explaining distributed and centralized modes
2. Include configuration examples for each mode

### T-002: Document umbrella.projectName configuration

**User Story**: US-001
**Satisfies ACs**: AC-US1-02
**Status**: [x] completed

**Test Plan**:
- **Given** the umbrella project config
- **When** umbrella.projectName is set
- **Then** living docs route to a distinct umbrella folder

**Implementation**:
1. Add projectName configuration section to README
2. Explain how living docs routing works with umbrella projects

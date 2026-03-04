---
increment: 0417J-update-cli-help-umbrella
total_tasks: 2
completed_tasks: 2
by_user_story:
  US-001: [T-001, T-002]
---

# Tasks: Update CLI Help Text for Umbrella Commands

## User Story: US-001 - Update migrate-to-umbrella Help Text

**Linked ACs**: AC-US1-01, AC-US1-02
**Tasks**: 2 total, 0 completed

---

### T-001: Verify --consolidate flag in help output

**User Story**: US-001
**Satisfies ACs**: AC-US1-01
**Status**: [x] completed

**Test Plan**:
- **Given** the `bin/specweave.js` CLI command registration
- **When** `specweave migrate-to-umbrella --help` is run
- **Then** the output includes `--consolidate` with description text

**Implementation**:
1. Run `specweave migrate-to-umbrella --help` and verify `--consolidate` appears
2. If description is unclear, update the `.option()` text in `bin/specweave.js`

---

### T-002: Add sync strategy mode documentation to help text

**User Story**: US-001
**Satisfies ACs**: AC-US1-02
**Status**: [x] completed

**Test Plan**:
- **Given** the CLI command description for `migrate-to-umbrella`
- **When** a user reads the help output
- **Then** it mentions distributed vs centralized sync modes

**Implementation**:
1. Update the `.description()` text in `bin/specweave.js` to mention sync strategy modes
2. Verify with `specweave migrate-to-umbrella --help`

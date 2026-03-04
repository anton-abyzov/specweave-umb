---
increment: 0419G-vskill-version-flag
total_tasks: 1
completed_tasks: 1
by_user_story:
  US-001: [T-001]
---

# Tasks: Add --version flag to vskill CLI

## User Story: US-001 - Version Flag Support

**Linked ACs**: AC-US1-01, AC-US1-02
**Tasks**: 1 total, 1 completed

---

### T-001: Add --version flag to CLI

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [x] completed

**Test Plan**:
- **Given** the vskill CLI entry point
- **When** `vskill --version` is executed
- **Then** it outputs only the version string from package.json (e.g., `0.2.20`)

**Implementation**:
1. Read version from package.json in CLI entry point
2. Add `--version` flag handling
3. Verify output format

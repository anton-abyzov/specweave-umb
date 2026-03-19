# Tasks for 0614: Fix update command skill routing

### T-001: Write failing tests for canonical skill routing in update command
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test Plan**:
- Given: A project with OpenCode detected as the agent
- When: `specweave update` installs/updates a skill
- Then: The skill is written to canonical `.agents/skills/` dir AND symlinked from `.opencode/skills/`, NOT directly written to both `.claude/skills/` and `.agents/skills/`
- Given: A project with Claude Code detected
- When: `specweave update` installs/updates a skill
- Then: Claude Code gets a direct copy with full frontmatter (not symlinked)
- Given: A project with both OpenCode and Claude Code detected
- When: `specweave update` installs/updates a skill
- Then: OpenCode gets symlink to canonical, Claude gets direct copy

### T-002: Replace inline file-writing loop with canonical installer calls
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test Plan**:
- Given: The update command at update.ts lines 191-226
- When: The inline loop is replaced with `installSymlink()` calls
- Then: All existing tests pass AND new tests from T-001 pass
- Then: `installSymlink()` handles canonical dir, symlinks, and content stripping automatically

### T-003: Verify ghost file cleanup works with canonical approach
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test Plan**:
- Given: An update that removes files from a skill
- When: Ghost file cleanup runs
- Then: Cleanup works correctly in the canonical dir AND symlinked dirs

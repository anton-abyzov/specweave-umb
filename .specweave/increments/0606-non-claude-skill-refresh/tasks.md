# Tasks

## Phase 1: Core Implementation

### T-001: Add normalizeFrontmatter() to plugin-copier.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed

**Test Plan**:
- Given a SKILL.md without `name:` field, When copied to non-Claude dir, Then output has `name:` derived from directory name
- Given a SKILL.md without `description:` field, When copied to non-Claude dir, Then output has `description:` extracted from body
- Given a SKILL.md with Claude-specific fields (hooks, model, etc.), When copied to non-Claude dir, Then those fields are stripped
- Given a non-SKILL.md file (agents/pm.md), When copied to non-Claude dir, Then file is copied unchanged

### T-002: Default vskill update to --all
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed

**Test Plan**:
- Given `vskill update` called with no args and no flags, When lockfile has 2 installed skills, Then both skills are updated

### T-003: Export findCoreSkillsDir() from sync.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed

**Test Plan**:
- Given specweave plugin cache exists, When `findCoreSkillsDir()` is called, Then returns path to skills directory

### T-004: Add fetchLocal() to source-fetcher.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [x] completed

**Test Plan**:
- Given a lockfile entry with `source: "local:specweave"`, When `fetchFromSource()` is called, Then it returns file map from specweave plugin cache
- Given plugin cache has same SHA as lockfile, When update runs, Then skill is skipped
- Given plugin cache has different SHA, When update runs, Then skill is re-installed with ensureFrontmatter() and lockfile updated

## Phase 2: Documentation

### T-005: Update specweave.com documentation
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed

**Test Plan**:
- Given docs-site/docs/reference/commands.md, When reading refresh-plugins section, Then frontmatter normalization is documented

### T-006: Update verified-skill.com documentation
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [x] completed

**Test Plan**:
- Given vskill docs, When reading update command section, Then default behavior change and local:specweave support are documented

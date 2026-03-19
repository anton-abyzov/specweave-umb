---
increment: 0565-vskill-frontmatter-compliance
title: Fix vskill SKILL.md frontmatter for Agent Skills standard compliance
type: feature
priority: P1
status: completed
created: 2026-03-18T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Fix vskill SKILL.md frontmatter for Agent Skills standard compliance

## Problem Statement

`vskill install` writes SKILL.md files without `name` and `description` frontmatter fields. The Agent Skills open standard (agentskills.io), adopted by 30+ tools, requires both fields. Skills installed by vskill are therefore broken in OpenCode, GitHub Copilot, and Codex CLI (Group A tools) which enforce the standard strictly.

## Goals

- All SKILL.md files written by vskill always contain valid `name` and `description` frontmatter
- Existing skills with author-set frontmatter are never corrupted
- Name values conform to agentskills.io format: lowercase alphanumeric + hyphens, 1-64 chars

## User Stories

### US-001: Frontmatter injection during skill installation (P1)
**Project**: vskill

**As a** developer installing skills via vskill
**I want** the installed SKILL.md to always contain valid `name` and `description` frontmatter
**So that** my skills work in all AI tools that follow the Agent Skills standard

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a SKILL.md with no frontmatter block, when `ensureFrontmatter(content, "my-skill")` is called, then the returned content starts with a YAML frontmatter block containing `name: my-skill`
- [x] **AC-US1-02**: Given a SKILL.md with frontmatter missing `name`, when `ensureFrontmatter(content, "my-skill")` is called, then `name: my-skill` is injected into the existing frontmatter
- [x] **AC-US1-03**: Given a SKILL.md with frontmatter missing `description`, when `ensureFrontmatter(content, "my-skill")` is called, then `description` is injected using text extracted from the first non-empty paragraph of the body
- [x] **AC-US1-04**: Given a SKILL.md where both `name` and `description` already exist, when `ensureFrontmatter` is called, then the content is returned unchanged
- [x] **AC-US1-05**: Given a SKILL.md with an existing `name` that differs from the skillName parameter, when `ensureFrontmatter` is called, then the existing `name` is preserved (author intent)

---

### US-002: Write-site integration across install and update paths (P1)
**Project**: vskill

**As a** developer installing or updating skills
**I want** frontmatter injection applied at every SKILL.md write location
**So that** no code path can produce a non-compliant file

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given any call to `installSymlink()`, when SKILL.md is written to the canonical directory, then `ensureFrontmatter` is applied to the content before writing
- [x] **AC-US2-02**: Given any call to `installSymlink()`, when SKILL.md is written to a copy-fallback agent directory, then `ensureFrontmatter` is applied to the content before writing
- [x] **AC-US2-03**: Given any call to `installSymlink()`, when SKILL.md is written to a symlink-failure fallback directory, then `ensureFrontmatter` is applied to the content before writing
- [x] **AC-US2-04**: Given any call to `installCopy()`, when SKILL.md is written, then `ensureFrontmatter` is applied to the content before writing
- [x] **AC-US2-05**: Given the `updateCommand` writing SKILL.md directly (bypassing canonical.ts), when SKILL.md is written, then `ensureFrontmatter` is applied to the content before writing

---

### US-003: Skill name validation (P1)
**Project**: vskill

**As a** skill author
**I want** skill names validated against the agentskills.io standard
**So that** invalid names are caught early instead of causing silent failures in consuming tools

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given a valid skill name (lowercase alphanumeric and hyphens, 1-64 chars), when `validateSkillNameStrict(name)` is called, then it returns true
- [x] **AC-US3-02**: Given a name with uppercase letters, when `validateSkillNameStrict(name)` is called, then it returns false
- [x] **AC-US3-03**: Given a name with underscores or spaces, when `validateSkillNameStrict(name)` is called, then it returns false
- [x] **AC-US3-04**: Given an empty string or a name exceeding 64 characters, when `validateSkillNameStrict(name)` is called, then it returns false
- [x] **AC-US3-05**: Given a name starting or ending with a hyphen, when `validateSkillNameStrict(name)` is called, then it returns false

## Out of Scope

- Modifying the existing `parseFrontmatter.ts` in eval-ui (reference only, not the same module)
- Enforcing `name` must match directory name (standard says "must match" but we preserve author intent)
- Adding frontmatter fields beyond `name` and `description` (e.g., `version`, `tags`)
- Retroactively patching already-installed SKILL.md files (only affects new install/update operations)

## Non-Functional Requirements

- **Compatibility**: Must work with all existing SKILL.md files without data loss -- existing frontmatter fields must be preserved
- **Testing**: TDD required -- all tests written before implementation, 90% coverage target

## Edge Cases

- SKILL.md with no frontmatter at all: create new frontmatter block with both fields
- SKILL.md with empty body (no paragraphs): set description to the skill name humanized (e.g., "my-skill" becomes "my skill")
- SKILL.md with CRLF line endings: handle correctly without corrupting content
- Frontmatter with extra/unknown fields: preserve all existing fields untouched
- Content that starts with `---` but has malformed YAML: treat as no-frontmatter case, prepend new block

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Existing valid SKILL.md corrupted by injection | 0.2 | 8 | 1.6 | AC-US1-04 and AC-US1-05 guard against this; TDD tests cover preservation |
| update.ts write path missed | 0.3 | 6 | 1.8 | AC-US2-05 explicitly covers the bypass path |

## Technical Notes

- `canonical.ts` has 4 `writeFileSync` calls in `installSymlink()` (line 114 canonical, line 128 copy-fallback, line 141 symlink-failure-fallback) plus 1 in `installCopy()` (line 168)
- `update.ts` line 170-174 writes directly via `writeFileSync`, bypassing canonical.ts entirely
- The existing `parseFrontmatter.ts` in eval-ui can serve as reference for parsing logic but the new utility should be self-contained in the installer module
- `ensureFrontmatter` should be a pure function (string in, string out) for easy testing

## Success Metrics

- 100% of SKILL.md files produced by `vskill install` and `vskill update` contain both `name` and `description` frontmatter
- Zero regressions in existing install/update test suite
- Skills installed by vskill load successfully in OpenCode, GitHub Copilot, and Codex CLI

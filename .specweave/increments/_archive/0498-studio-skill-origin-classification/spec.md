---
increment: 0498-studio-skill-origin-classification
title: Studio Skill Origin Classification (Consumed vs Editable)
type: feature
priority: P1
status: completed
created: 2026-03-11T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio Skill Origin Classification (Consumed vs Editable)

## Problem Statement

When `npx vskill studio` scans for skills, it discovers ALL SKILL.md files including those inside agent config directories (`.claude/skills/`, `.cursor/skills/`, `.windsurf/skills/`, etc.). These are installed copies meant for consumption by AI agents, not the user's source skills for editing and development. Currently there is no visual distinction -- users cannot tell which skills they should be working on versus which are just installed copies.

## Goals

- Classify every scanned skill as either "source" (editable) or "installed" (consumed)
- Visually separate source and installed skills in the studio sidebar
- Prevent accidental editing/benchmarking of installed copies
- Leverage the existing AGENTS_REGISTRY for detection rather than hardcoding agent directories

## User Stories

### US-001: Origin Classification in Scanner
**Project**: vskill
**As a** skill developer
**I want** the skill scanner to classify each discovered skill as "source" or "installed"
**So that** downstream consumers (UI, CLI) know which skills are editable vs consumed copies

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a skill whose `dir` relative to `root` starts with any `localSkillsDir` prefix from `AGENTS_REGISTRY` (e.g., `.claude/`, `.cursor/`, `.amp/`), when the scanner returns results, then that skill has `origin: "installed"`
- [x] **AC-US1-02**: Given a skill whose `dir` relative to `root` starts with any hardcoded extra prefix (`.specweave/`, `.vscode/`, `.idea/`, `.zed/`, `.devcontainer/`, `.github/`, `.agents/`, `.agent/`), when the scanner returns results, then that skill has `origin: "installed"`
- [x] **AC-US1-03**: Given a skill whose `dir` relative path contains `plugins/cache/`, when the scanner returns results, then that skill has `origin: "installed"`
- [x] **AC-US1-04**: Given a skill that does not match any installed pattern, when the scanner returns results, then that skill has `origin: "source"`
- [x] **AC-US1-05**: Given a skill that exists as both a source copy and an installed copy, when the scanner returns results, then both copies appear in the list with their respective origin values

---

### US-002: Sidebar Split into Source and Installed Sections
**Project**: vskill
**As a** skill developer
**I want** the studio sidebar to display "Your Skills" at the top and "Installed" below
**So that** I can immediately identify which skills I should be editing

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given the sidebar loads skills, when skills have mixed origins, then source skills appear under a "Your Skills" section header and installed skills appear under an "Installed" section header
- [x] **AC-US2-02**: Given all skills are source skills, when the sidebar renders, then only the "Your Skills" section is shown (no empty "Installed" section)
- [x] **AC-US2-03**: Given all skills are installed skills, when the sidebar renders, then only the "Installed" section is shown (no empty "Your Skills" section)
- [x] **AC-US2-04**: Given the search filter is active, when filtering skills, then the origin-based grouping is preserved within filtered results

---

### US-003: Visual De-emphasis of Installed Skills
**Project**: vskill
**As a** skill developer
**I want** installed skills to appear visually dimmed with a distinguishing icon
**So that** I can quickly scan past them and focus on my editable skills

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given a skill card for an installed skill, when rendered in the sidebar, then the card text has opacity 0.7
- [x] **AC-US3-02**: Given a skill card for an installed skill, when rendered in the sidebar, then a lock SVG icon is displayed before the skill name
- [x] **AC-US3-03**: Given a skill card for a source skill, when rendered in the sidebar, then no lock icon is shown and text has opacity 1.0

---

### US-004: Read-Only Mode for Installed Skills
**Project**: vskill
**As a** skill developer
**I want** installed skills to open in a read-only view when selected
**So that** I do not accidentally modify or benchmark consumed copies

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given an installed skill is selected, when the detail panel renders, then the SKILL.md content is shown in read-only mode
- [x] **AC-US4-02**: Given an installed skill is selected, when the detail panel renders, then benchmark run buttons have the `disabled` attribute
- [x] **AC-US4-03**: Given an installed skill is selected, when the detail panel renders, then eval editing controls (Add Test Case, edit, delete) are hidden from the DOM
- [x] **AC-US4-04**: Given a source skill is selected, when the detail panel renders, then all editing and benchmarking controls remain fully functional

---

### US-005: Info Banner Explaining Origin Distinction
**Project**: vskill
**As a** skill developer
**I want** an informational banner in the sidebar explaining the Your Skills vs Installed distinction
**So that** I understand why some skills are separated and what the grouping means

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given the sidebar contains both source and installed skills, when the "Installed" section is expanded, then an info banner is displayed at the top of the installed section explaining the distinction
- [x] **AC-US5-02**: Given the user dismisses the info banner, when the sidebar re-renders in the same session, then the banner remains hidden
- [x] **AC-US5-03**: Given the info banner is shown, when rendered, then the banner text contains "installed copies" and "Edit skills in your project root"

## Non-Functional Requirements

- **Performance**: Origin classification adds < 1ms per skill to scanner runtime (pure string prefix matching, no I/O)
- **Compatibility**: Path normalization works on Windows (`\` separators), macOS, and Linux (`/` separators) via `path.relative()` + forward-slash normalization
- **Accessibility**: All interactive elements (collapse toggle, dismiss button, disabled buttons) are keyboard-navigable and have appropriate ARIA attributes or tooltips
- **Security**: No user-controlled input reaches `path.relative()` unsanitized — scanner root is always the resolved working directory

## Edge Cases

- **Empty relative path** (`root === skillDir`, Layout 4 self-layout): Returns `"source"` — the skill IS the project root
- **Symlinked directories**: `path.relative()` resolves symlinks to their target path; classification uses the resolved path
- **Case sensitivity**: Path prefix matching is case-sensitive (`.claude/` does not match `.Claude/`); this is correct on Linux, and macOS/Windows filesystems normalize case anyway
- **Windows path separators**: Relative path is normalized to forward slashes before prefix matching
- **No skills found**: Both sidebar sections hidden; "No skills match your search" empty state shown
- **AGENTS_REGISTRY changes**: Prefix set is computed per `scanSkills()` call from the live registry; new agents are picked up automatically
- **Very long paths**: No path length limit enforced; `path.relative()` handles arbitrarily deep nesting

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| False positive: source skill classified as installed due to overly broad prefix matching | 0.2 | 6 | 1.2 (LOW) | Top-level segment extraction (`.claude/` not `.claude/skills/`) is intentionally broad; out-of-scope paths are rare |
| False negative: installed skill in unknown agent dir not classified | 0.3 | 3 | 0.9 (LOW) | Hardcoded extras cover non-registry dirs; new agents added to AGENTS_REGISTRY automatically |
| UI regression: existing skill interactions break for source skills | 0.1 | 8 | 0.8 (LOW) | Source skills have `isReadOnly=false`, all controls unchanged; full Vitest regression suite |
| Read-only bypass: user finds way to trigger mutations on installed skills | 0.2 | 4 | 0.8 (LOW) | Defense in depth: UI disables + context-level `if (isReadOnly) return` guards on all 6 mutating functions |

## Out of Scope

- Filtering installed skills out of scanner results entirely (they are still returned)
- Editing the installed skill path or redirecting to source location
- Origin classification in the standalone `SkillListPage` route (sidebar only for this increment)
- Origin-aware behavior in CLI commands (e.g., `vskill eval run`)
- Syncing or linking installed copies back to their source skill

## Technical Notes

### Dependencies
- `AGENTS_REGISTRY` from `src/agents/agents-registry.ts` -- provides `localSkillsDir` for all 49+ known agents
- `SkillInfo` interface in `src/eval/skill-scanner.ts` -- needs `origin` field added
- `SkillInfo` mirror in `src/eval-ui/src/types.ts` -- needs matching `origin` field

### Architecture Decisions
- Origin detection uses path prefix matching, not file content analysis
- The `localSkillsDir` values from AGENTS_REGISTRY are extracted as directory prefixes (e.g., `.claude/skills` yields `.claude/` as the prefix to match, since any path starting with `.claude/` is agent-owned)
- Extra hardcoded prefixes cover non-agent config directories that also contain installed/consumed skills
- `plugins/cache/` is matched anywhere in the relative path (contains-check, not prefix-check)

## Success Metrics

- Source vs installed distinction is correct for 100% of scanned skills in test scenarios
- No regressions in existing scanner behavior (all existing tests pass)
- Installed skills cannot trigger benchmark runs from the UI

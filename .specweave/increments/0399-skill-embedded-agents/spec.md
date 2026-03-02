# FS-399: Skill-Embedded Agents & Token Isolation

**Status**: in-progress | **Created**: 2026-03-02 | **Type**: enhancement

## Problem

SpecWeave skills have inline agent bloat (team-lead: 310 lines of agent templates), non-interactive skills waste main context tokens (no `context: fork`), and vskill blocks `agents/` subdirectory distribution.

## User Stories

### US-001: Extract Team-Lead Agents to Reusable Files
**Project**: specweave

**As a** skill author, **I want** domain agent definitions as `agents/*.md` files inside team-lead skill, **so that** agent prompts are maintainable, inspectable, and distributable via vskill.

**Acceptance Criteria**:
- [x] **AC-US1-01**: 5 agent .md files in `plugins/specweave/skills/team-lead/agents/`
- [x] **AC-US1-02**: team-lead SKILL.md Section 4 replaced with reference table + "Read agents/{name}.md"
- [x] **AC-US1-03**: team-lead SKILL.md reduced by ~250 lines (927→653)
- [ ] **AC-US1-04**: spawned agents receive identical prompt content (behavioral equivalence)

### US-002: Token Isolation for Non-Interactive Skills
**Project**: specweave

**As a** user running `/sw:increment`, **I want** architect and test-aware-planner to run in isolated context, **so that** skill instructions don't consume main conversation tokens.

**Acceptance Criteria**:
- [x] **AC-US2-01**: `architect/SKILL.md` has `context: fork` and `model: opus`
- [x] **AC-US2-02**: `test-aware-planner/SKILL.md` has `context: fork` and `model: opus`
- [x] **AC-US2-03**: `grill/SKILL.md` has `context: fork` and `model: opus`
- [ ] **AC-US2-04**: `/sw:increment` produces equivalent quality output

### US-003: vskill Installer Supports agents/ Subdirectory
**Project**: vskill

**As a** skill distributor, **I want** `vskill install` to copy `agents/*.md` alongside SKILL.md, **so that** skill-embedded agents survive distribution.

**Acceptance Criteria**:
- [x] **AC-US3-01**: `shouldSkipFromCommands` allows `skills/{name}/agents/*.md`
- [x] **AC-US3-02**: `installSymlink` COPY_FALLBACK copies agents/ from canonical
- [x] **AC-US3-03**: `installCopy` copies agents/ alongside SKILL.md
- [x] **AC-US3-04**: Skills without agents/ install correctly (9/9 canonical tests pass)

## Out of Scope
- Root `.claude/agents/` definitions (not needed — skill-embedded is distributable via vskill)
- Declarative agent trigger rules in config.json (current heuristic in /sw:do works)
- CLAUDE.md/AGENTS.md template changes (sub-agent usage understood by default)
- vskill CLI execution changes

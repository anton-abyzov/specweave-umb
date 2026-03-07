---
increment: 0415-brainstorm-skill
title: "sw:brainstorm - Multi-Perspective Ideation Skill"
type: feature
priority: P1
status: active
created: 2026-03-03
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: sw:brainstorm - Multi-Perspective Ideation Skill

## Problem Statement

Developers and product owners currently jump straight from a rough idea to `sw:increment`, skipping structured ideation. The existing `docs:spec-driven-brainstorming` skill in the specweave-docs plugin is limited to basic product discovery (story mapping, MoSCoW/RICE) and lacks cognitive frameworks, parallel exploration, depth controls, and native increment handoff. Teams miss alternative approaches because they never systematically diverge before converging on a plan.

## Goals

- Provide a 5-phase structured ideation flow (Frame, Diverge, Evaluate, Deepen, Output) as a first-class core skill
- Support 5 selectable cognitive lenses (Default, Six Thinking Hats, SCAMPER, TRIZ, Adjacent Possible) for multi-perspective exploration
- Offer 3 depth modes (quick, standard, deep) to match available time and complexity
- Enable parallel subagent dispatch in deep mode so lens facets run concurrently
- Produce persistent, linkable brainstorm documents that feed directly into the increment workflow
- Replace the existing `docs:spec-driven-brainstorming` skill with a more capable core alternative

## User Stories

### US-001: Multi-Perspective Brainstorming Before Implementation (P1)
**Project**: specweave
**As a** developer starting a new feature
**I want** to brainstorm approaches from multiple perspectives before committing to an implementation plan
**So that** I make better architectural decisions

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given the core specweave plugin, when the skill is registered, then a `skills/brainstorm/SKILL.md` file exists with frontmatter containing `context: fork` and `model: opus`
- [x] **AC-US1-02**: Given a user invokes `sw:brainstorm "topic"`, when the skill starts, then it executes a 5-phase flow in order: Frame (problem definition), Diverge (idea generation), Evaluate (scoring/ranking), Deepen (drill into top ideas), Output (structured document)
- [x] **AC-US1-03**: Given the skill supports 3 depth modes, when a user specifies `--depth quick`, then only Phase 1 (Frame) and Phase 3 (Evaluate) execute; when `--depth standard` (default), then Phases 1-3 and 5 execute; when `--depth deep`, then all 5 phases execute
- [x] **AC-US1-04**: Given the brainstorm session completes, when the Output phase runs, then it produces a DOT-notation process flow graph embedded in the output document showing the phases executed and decisions made
- [x] **AC-US1-05**: Given each phase has a token budget, when a phase executes, then Frame uses at most 500 tokens, Diverge at most 800 tokens, Evaluate at most 600 tokens, Deepen at most 1000 tokens, and Output at most 400 tokens

### US-002: Structured Ideation with Cognitive Frameworks (P1)
**Project**: specweave
**As a** product owner exploring a new product idea
**I want** structured ideation with cognitive frameworks (Six Thinking Hats, SCAMPER, TRIZ)
**So that** I consider angles I might miss on my own

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given the brainstorm skill, when the user selects a lens, then exactly 5 lenses are available: Default (unstructured divergent thinking), Six Thinking Hats (White/Red/Black/Yellow/Green/Blue facets), SCAMPER (Substitute/Combine/Adapt/Modify/Put-to-other-uses/Eliminate/Reverse), TRIZ (Inventive Principles, Contradiction Matrix, Ideal Final Result), and Adjacent Possible (analogies from adjacent domains)
- [x] **AC-US2-02**: Given the user selects `--lens six-hats` and `--depth deep`, when the Diverge phase runs, then each of the 6 hat facets (White, Red, Black, Yellow, Green, Blue) is dispatched as a parallel subagent, and results are collected and merged before proceeding to Evaluate
- [x] **AC-US2-03**: Given the user selects `--lens scamper` and `--depth deep`, when the Diverge phase runs, then each of the 7 SCAMPER operators is dispatched as a parallel subagent
- [x] **AC-US2-04**: Given a lens is selected with `--depth quick` or `--depth standard`, when the Diverge phase runs (standard only), then the lens facets execute sequentially in a single agent context rather than as parallel subagents
- [x] **AC-US2-05**: Given no `--lens` flag is provided, when the skill starts, then the Default lens is used automatically

### US-003: Persistent Brainstorm Documents with Increment Handoff (P1)
**Project**: specweave
**As a** team lead
**I want** brainstorm sessions to produce persistent, linkable documents that feed into the increment workflow
**So that** decision rationale is preserved

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given a brainstorm session completes, when the Output phase finishes, then a markdown document is saved to `.specweave/docs/brainstorms/{timestamp}-{slug}.md` containing: topic, lens used, depth mode, all phase outputs, the DOT process graph, and a ranked list of ideas with scores
- [x] **AC-US3-02**: Given the brainstorm session is interrupted (context limit, user abort, crash), when the session resumes, then a state file at `.specweave/state/brainstorm-{session-id}.json` tracks completed phases and partial results, allowing the skill to resume from the last completed phase
- [x] **AC-US3-03**: Given a brainstorm document exists and the user says "proceed to increment" or similar, when the handoff triggers, then `sw:increment` is invoked with the brainstorm document path as context, and the increment's spec.md references the brainstorm doc in a `## Background` section
- [x] **AC-US3-04**: Given the skill is added to the core specweave plugin, when the `specweave` PLUGIN.md skill table is read, then `brainstorm` appears as a listed skill with its description
- [x] **AC-US3-05**: Given the `specweave-docs` plugin currently lists `spec-driven-brainstorming`, when this increment is complete, then `specweave-docs/PLUGIN.md` marks `spec-driven-brainstorming` as deprecated with a note directing users to `sw:brainstorm`
- [x] **AC-US3-06**: Given the source code references the old brainstorming skill, when this increment is complete, then `src/core/lazy-loading/llm-plugin-detector.ts` updates the `docs:` skill group to remove or replace `docs:brainstorming` with `sw:brainstorm`, `src/adapters/claude-md-generator.ts` updates the framework skills list and trigger description to reference `brainstorm` instead of `spec-driven-brainstorming`, and `src/utils/generate-skills-index.ts` continues to detect the brainstorm skill name correctly
- [x] **AC-US3-07**: Given the CLAUDE.md template at `src/templates/CLAUDE.md.template`, when this increment is complete, then the auto-detection opt-out phrase "Just brainstorm first" is updated or a note is added clarifying that `sw:brainstorm` is the dedicated skill for brainstorming (distinct from the opt-out phrase)
- [x] **AC-US3-08**: Given the public documentation site, when this increment is complete, then `docs-site/docs/reference/skills.md` lists `sw:brainstorm` with usage examples, and `docs-site/docs/workflows/planning.md` references brainstorming as an optional pre-increment step
- [x] **AC-US3-09**: Given the brainstorm skill, when auto-activation keywords are detected in user input (e.g., "brainstorm", "explore ideas", "think through", "what if", "ideate", "diverge"), then the skill is suggested or auto-invoked per the plugin auto-load configuration

## Out of Scope

- Visual/graphical brainstorm UIs (web dashboard, mind maps) -- this is CLI/text only
- Real-time collaborative brainstorming with multiple human participants
- Integration with external brainstorming tools (Miro, FigJam, etc.)
- Custom user-defined lenses (future increment)
- Brainstorm history search or analytics across multiple sessions
- Changes to the `specweave-docs` plugin skills other than the deprecation notice

## Technical Notes

### File Targets (New)
- `plugins/specweave/skills/brainstorm/SKILL.md` -- skill definition with phases, lenses, depth modes
- `.specweave/docs/brainstorms/` -- persistent output directory (created on first use)
- `.specweave/state/brainstorm-*.json` -- session state files for resumability

### File Targets (Modified)
- `plugins/specweave/PLUGIN.md` -- add brainstorm to skill table
- `plugins/specweave-docs/PLUGIN.md` -- deprecation notice on spec-driven-brainstorming
- `src/core/lazy-loading/llm-plugin-detector.ts` -- update docs: group reference
- `src/adapters/claude-md-generator.ts` -- update framework skills list and trigger map
- `src/utils/generate-skills-index.ts` -- verify brainstorm detection (may need no change)
- `src/templates/CLAUDE.md.template` -- clarify brainstorm opt-out vs skill invocation
- `docs-site/docs/reference/skills.md` -- add sw:brainstorm documentation
- `docs-site/docs/workflows/planning.md` -- add brainstorm as pre-increment step

### Architecture
- SKILL.md uses `context: fork` (runs in isolated agent context) and `model: opus` (needs strong reasoning for cognitive frameworks)
- Deep mode subagent dispatch uses the existing SpecWeave subagent infrastructure (same pattern as team-build/team-lead skills)
- State file JSON schema: `{ sessionId, topic, lens, depth, startedAt, phases: { frame: {status, output}, diverge: {status, output, facets: []}, ... } }`

### Constraints
- No new npm dependencies
- Token budgets are advisory targets, not hard enforcement (the skill instructions guide the model)
- Backward compatibility: existing `docs:brainstorming` invocations should still work but emit a deprecation warning directing to `sw:brainstorm`

## Dependencies

- SpecWeave core plugin (`plugins/specweave/`) -- host for the new skill
- Subagent infrastructure -- for deep mode parallel facet dispatch
- `sw:increment` skill -- for native handoff integration

## Success Metrics

- Brainstorm skill is discoverable via auto-activation keywords and direct invocation
- All 3 depth modes produce valid output documents in `.specweave/docs/brainstorms/`
- Deep mode successfully dispatches lens facets as parallel subagents
- Session resumability works after interruption (state file round-trip)
- Handoff to `sw:increment` carries brainstorm context into spec.md
- Old `docs:spec-driven-brainstorming` shows deprecation notice
- All 3 source .ts files and CLAUDE.md template are updated
- Public docs (skills.md, planning.md) reference the new skill

---
increment: 0548-skill-gen-autoinstall-dedup-docs
title: 'Skill-Gen: Auto-Install Skill-Creator, Deduplication, and Documentation Update'
type: feature
priority: P1
status: completed
created: 2026-03-16T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skill-Gen: Auto-Install Skill-Creator, Deduplication, and Documentation Update

## Problem Statement

Skill-gen currently requires manual installation of Anthropic's skill-creator plugin before `/sw:skill-gen` can work. Developers must know about this dependency and install it separately, creating friction on first use. Additionally, pattern detection has no awareness of rules the developer has already documented -- it suggests patterns that duplicate existing CLAUDE.md rules or `.cursorrules` content. Finally, the docs still describe the old keyword-matching approach rather than the current LLM-based detection.

## Goals

- Zero-friction first run: `specweave init` ensures skill-creator is available without manual steps
- Eliminate duplicate suggestions: pattern detection checks existing rules before proposing new skills
- Accurate documentation: docs reflect the LLM-based architecture, seed mode, and prerequisites

## User Stories

### US-001: Auto-Install Skill-Creator Locally (P0)
**Project**: specweave
**As a** developer running specweave init
**I want** Anthropic's skill-creator auto-installed into .claude/skills/skill-creator/
**So that** /sw:skill-gen works out of the box without separate plugin installation

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given specweave init runs on a project, when .claude/skills/skill-creator/SKILL.md does not exist, then skill-creator is installed locally via `claude install-skill` CLI targeting the GitHub URL
- [x] **AC-US1-02**: Given skill-creator already exists at .claude/skills/skill-creator/SKILL.md, when init runs, then installation is skipped silently
- [x] **AC-US1-03**: Given the `claude install-skill` command fails (network error, CLI missing), when init runs, then a warning is logged but init continues without blocking
- [x] **AC-US1-04**: Given specweave update-instructions runs, when .claude/skills/skill-creator/ is missing, then it installs skill-creator (same behavior as init)
- [x] **AC-US1-05**: Given /sw:skill-gen runs, when looking for skill-creator, then it checks .claude/skills/skill-creator/SKILL.md first (local), then falls back to ~/.claude/plugins/cache/claude-plugins-official/skill-creator/*/SKILL.md (global)

---

### US-002: Deduplication Awareness in Pattern Detection (P1)
**Project**: specweave
**As a** developer using skill-gen
**I want** pattern detection to check my existing rules before suggesting patterns
**So that** I don't get suggestions for patterns I've already documented

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given existing rule files (.claude/skills/**/*.md, CLAUDE.md, .cursorrules, .cursor/rules/*.mdc, .github/copilot-instructions.md), when signal-collector builds the LLM prompt, then existing rules content is included as dedup context
- [x] **AC-US2-02**: Given existing rules cover "always use Zod for validation", when the LLM analyzes living docs, then it does NOT return a "zod-validation" pattern as a suggestion
- [x] **AC-US2-03**: Given no rule files exist in the project, when signal-collector builds the prompt, then the prompt works normally without the dedup section
- [x] **AC-US2-04**: Given a skill with slug "error-handling" already exists at .claude/skills/error-handling/SKILL.md, when /sw:skill-gen tries to generate the same slug, then it warns and skips generation
- [x] **AC-US2-05**: Given rule files contain sensitive content, when included in the LLM prompt, then content is truncated to a reasonable size (max 10K tokens of rules context) to avoid overwhelming the pattern detection

---

### US-003: Documentation Update for LLM Pivot (P1)
**Project**: specweave
**As a** developer reading SpecWeave docs
**I want** accurate documentation explaining LLM-based skill-gen
**So that** I understand how pattern detection works, how to use --seed mode, and what prerequisites are needed

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given docs-site/docs/skills/extensible/skill-generation.md, when rewritten, then it explains LLM-based detection (not keyword matching), dynamic categories, file-based confidence scoring
- [x] **AC-US3-02**: Given the docs page, when --seed mode is documented, then it includes a command example and explains it solves the cold start problem
- [x] **AC-US3-03**: Given the docs page, when a walkthrough example is included, then it shows a concrete Express+React+Zod project going through the full flow (init -> seed -> detect -> suggest -> generate -> eval)
- [x] **AC-US3-04**: Given the docs page, when prerequisites are listed, then it covers: living docs enabled, LLM config in config.json, skill-creator auto-installed
- [x] **AC-US3-05**: Given README.md, when the skill-gen section is updated, then it has a compelling 3-4 sentence description linking to the full docs

## Out of Scope

- Merging skill-gen with skill-memories
- Pattern preview UI
- Cross-tool skill distribution
- Changing skill-creator itself

## Non-Functional Requirements

- **Performance**: Auto-install adds no more than 5 seconds to init when skill-creator is already present (skip check is O(1) file existence)
- **Security**: Rule file content sent to LLM is read-only; no user credentials or .env files are included in dedup context
- **Compatibility**: `claude install-skill` detection works on macOS, Linux, and Windows (where Claude Code CLI is available)
- **Reliability**: Install failure is non-blocking -- init always completes successfully regardless of network state

## Edge Cases

- **claude CLI not installed**: `which claude` returns empty -- log warning, skip install, init succeeds
- **Permissions on .claude/skills/**: Directory not writable -- log warning, skip, init succeeds
- **Massive rule files**: A project with 50+ rule files totaling 200K tokens -- truncation caps at 10K tokens, oldest/largest files prioritized by recency
- **Symlinked skill-creator**: .claude/skills/skill-creator is a symlink to another location -- treat as existing, skip install
- **Empty CLAUDE.md**: File exists but is 0 bytes -- treated as "no rules exist" for dedup purposes
- **Concurrent init runs**: Two terminals run `specweave init` simultaneously -- file-existence check is idempotent, no corruption risk

## Technical Notes

### Dependencies
- Claude Code CLI (`claude install-skill` subcommand)
- Anthropic's skill-creator GitHub repository URL
- Existing signal-collector module (`src/core/skill-gen/signal-collector.ts`)

### Constraints
- LLM prompt size has a practical ceiling; dedup context must be bounded (10K tokens max)
- `claude install-skill` is an external binary -- its behavior and exit codes may change across versions

### Architecture Decisions
- Local-first resolution: check .claude/skills/ before global plugin cache to respect project-level overrides
- Non-blocking install: network-dependent steps must never prevent init from completing
- Dedup via prompt injection: existing rules are appended to the LLM prompt as context rather than implementing client-side filtering

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| `claude install-skill` CLI interface changes | 0.3 | 5 | 1.5 | Version-check the CLI; wrap in try/catch with descriptive warning |
| Dedup prompt bloat slows LLM response | 0.2 | 4 | 0.8 | Hard cap at 10K tokens; monitor prompt size in tests |
| Docs become stale if skill-gen evolves further | 0.4 | 3 | 1.2 | Link docs to source; add "last verified" date |
| skill-creator GitHub URL changes or goes private | 0.1 | 7 | 0.7 | Make URL configurable in config.json |

## Success Metrics

- Init-to-first-skill-gen requires zero manual plugin installation steps
- Pattern suggestions contain zero duplicates of existing documented rules (verified via eval cases)
- Docs page accurately describes the current LLM-based architecture with working examples

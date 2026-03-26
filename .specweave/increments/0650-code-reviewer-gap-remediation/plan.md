# Implementation Plan: Code Reviewer Gap Remediation

## Overview

All changes are markdown template edits — no TypeScript, no runtime changes. The SKILL.md orchestrator gets 3 new sections (gate check, finding validation, PR context fetching) and an updated routing table. Six existing agent templates gain "DO NOT FLAG" and "PR CONTEXT" sections. Two new agent templates are created following the established pattern.

## Architecture

### File Map

| File | Change Type | Gap(s) Addressed |
|------|-------------|------------------|
| `plugins/specweave/skills/code-reviewer/SKILL.md` | Edit | All 6 gaps |
| `plugins/specweave/skills/team-lead/agents/reviewer-logic.md` | Edit | #4 (DO NOT FLAG), #6 (PR context) |
| `plugins/specweave/skills/team-lead/agents/reviewer-security.md` | Edit | #4, #6 |
| `plugins/specweave/skills/team-lead/agents/reviewer-performance.md` | Edit | #4, #6 |
| `plugins/specweave/skills/code-reviewer/agents/reviewer-silent-failures.md` | Edit | #4, #6 |
| `plugins/specweave/skills/code-reviewer/agents/reviewer-types.md` | Edit | #4, #6 |
| `plugins/specweave/skills/code-reviewer/agents/reviewer-spec-compliance.md` | Edit | #4, #6 |
| `plugins/specweave/skills/code-reviewer/agents/reviewer-comments.md` | **New** | #4, #5, #6 |
| `plugins/specweave/skills/code-reviewer/agents/reviewer-tests.md` | **New** | #4, #5, #6 |

### SKILL.md Orchestrator Changes

**New Section 0.5: Gate Check** (between Scope Detection and Smart Reviewer Routing)
- For PR scope only: query `gh pr view --json isDraft,state,additions,deletions`
- Skip with message if: isDraft=true, state=CLOSED/MERGED, or additions+deletions < 5
- Document `--force` flag to bypass
- Non-PR scopes (--changes, --increment, path) skip gate check entirely

**New Section 1.5: PR Context Fetching** (between Smart Reviewer Routing and Team Creation)
- For PR scope: fetch `gh pr view --json title,body`
- Store as `PR_TITLE` and `PR_BODY` variables
- Pass to all agent templates via `[PR_TITLE]` and `[PR_BODY]` placeholders
- For non-PR scopes: set both to "N/A — not a PR review"

**Updated Section 1: Smart Reviewer Routing**
- Add reviewer-comments and reviewer-tests to the routing table
- Update model assignments: opus for logic/security, sonnet for all others
- Add routing rules: comments triggers on any code files; tests triggers when test files or testable source present

**New Section 3.5: Finding Validation** (between Result Aggregation and Report Generation)
- After collecting all findings, filter for CRITICAL and HIGH severity
- Spawn one haiku-model validator per finding via Task()
- Validator receives: finding text, code snippet, instructions to confirm/reject/downgrade
- Collect validator verdicts; exclude rejected findings, adjust severity on downgrades
- Pass validated findings to report generation

**Updated Section 2: Team Creation and Agent Spawning**
- Add `[PR_TITLE]` and `[PR_BODY]` to placeholder replacement list

## Architecture Decisions

### ADR-1: Haiku for validation, not sonnet
Validation is a binary confirm/reject/downgrade task — it does not require deep reasoning. Haiku is sufficient and keeps costs proportional. Each CRITICAL/HIGH finding gets its own validator for independence (no cross-contamination between findings).

### ADR-2: DO NOT FLAG in templates, not in orchestrator
Suppression rules belong in agent templates because they are domain-specific. Centralizing them in the orchestrator would create coupling and require the orchestrator to understand each domain's nuances. Agents are the domain experts.

### ADR-3: PR context as placeholder, not as a separate message
Passing PR context in the initial prompt (via placeholder substitution) is simpler than sending a follow-up message. Agents get context from the start, reducing back-and-forth.

### ADR-4: Gate check applies to PR scope only
Non-PR scopes (file paths, --changes, --increment) represent deliberate intent to review. Only PR-triggered reviews need gate checking because PRs have lifecycle states (draft, closed) that may make review premature.

## Implementation Phases

### Phase 1: Orchestrator Updates (SKILL.md)
- Add gate check section
- Update routing table with new reviewers and model tiering
- Add PR context fetching
- Add finding validation section

### Phase 2: Existing Agent Template Updates
- Add DO NOT FLAG sections to all 6 existing templates
- Add PR CONTEXT placeholders to all 6 existing templates

### Phase 3: New Agent Templates
- Create reviewer-comments.md
- Create reviewer-tests.md
- Both include DO NOT FLAG and PR CONTEXT from the start

## Testing Strategy

All changes are markdown — no unit tests apply. Verification is structural:
- Each task's BDD test plan checks the presence and correctness of specific markdown sections
- Validation is done by reading the modified files and confirming content matches ACs
- Given/When/Then format captures what to check in each file

## Technical Challenges

### Challenge 1: Template Consistency
All 8 agent templates must follow the same output format, communication protocol, and rules.
**Solution**: New templates are modeled directly on existing ones (reviewer-silent-failures.md as the reference pattern). DO NOT FLAG and PR CONTEXT sections use a consistent format across all 8.

### Challenge 2: Finding Validation Ordering
Validation must happen after aggregation but before report generation.
**Solution**: SKILL.md sections are numbered explicitly (3 = Aggregation, 3.5 = Validation, 4 = Report). The orchestrator follows sequential section order.

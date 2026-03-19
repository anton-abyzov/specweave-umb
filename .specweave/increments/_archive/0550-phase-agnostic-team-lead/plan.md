# Plan: Phase-Agnostic Team Lead and Standalone Code Reviewer

## Architecture Overview

This increment restructures two SpecWeave skill orchestration surfaces: the team-lead skill (markdown-only redesign of its orchestration logic) and a new code-reviewer skill (standalone skill with its own agents directory). All deliverables are markdown (.md) and shell (.sh) files. No TypeScript or JavaScript code changes.

```
plugins/specweave/
├── skills/
│   ├── team-lead/
│   │   ├── SKILL.md            ← Redesigned: Section 0 now has 6 modes
│   │   └── agents/
│   │       ├── pm.md           ← existing (referenced by plan mode)
│   │       ├── architect.md    ← existing (referenced by plan mode)
│   │       ├── researcher.md   ← existing (referenced by research mode)
│   │       ├── brainstorm-*.md ← existing (referenced by brainstorm mode)
│   │       ├── reviewer-logic.md      ← existing (shared with code-reviewer)
│   │       ├── reviewer-security.md   ← existing (shared with code-reviewer)
│   │       ├── reviewer-performance.md ← existing (shared with code-reviewer)
│   │       └── testing.md     ← existing (referenced by test mode)
│   └── code-reviewer/
│       ├── SKILL.md            ← NEW: standalone orchestrator
│       └── agents/
│           ├── reviewer-silent-failures.md  ← NEW
│           ├── reviewer-types.md            ← NEW
│           └── reviewer-spec-compliance.md  ← NEW
├── hooks/v2/guards/
│   └── increment-existence-guard.sh  ← UPDATED: research-*, plan-*, test-* prefixes
└── PLUGIN.md                         ← VERIFIED: code-reviewer already registered at line 82
```

---

## Decision 1: Mode Detection Architecture in Team-Lead (Section 0 Redesign)

### Problem

The team-lead SKILL.md previously operated as an implementation-only orchestrator. Sections 0 through 7 assumed the user wanted domain implementation agents (frontend, backend, database, etc.). Users who invoked team-lead for brainstorming, planning, research, or review had to either work around this assumption or invoke separate skills manually.

### Decision

Redesign Section 0 of SKILL.md as a mode-detection router with 6 modes, each terminating at its own subsection (0a-0e) or falling through to Section 1 (implementation). This is a prompt-engineering change, not a runtime code change.

### Mode Detection Priority Chain

```
User Request
    |
    v
1. Explicit --mode flag? ──yes──> Use specified mode
    |no
    v
2. team_name prefix?     ──yes──> Infer mode from prefix
   review-*, brainstorm-*,         (review, brainstorm, research,
   research-*, plan-*, test-*       plan, test)
    |no
    v
3. Intent keywords?      ──yes──> Match against keyword table
    |no
    v
4. Default: IMPLEMENTATION mode
```

### Mode Configuration Matrix

| Mode | Increment Required? | Agent Templates | Team Prefix | Terminates At |
|------|-------------------|-----------------|-------------|---------------|
| BRAINSTORM | No | brainstorm-advocate, brainstorm-critic, brainstorm-pragmatist | brainstorm-* | Section 0a |
| PLANNING | Creates one if absent | pm, architect (+ optional security) | plan-* | Section 0b |
| IMPLEMENTATION | Yes (enforced by guard) | backend, frontend, database, testing, security | impl-* | Section 1+ |
| REVIEW | No (delegates to code-reviewer) | N/A (delegates) | review-* | Section 0c |
| RESEARCH | No | researcher (1-3 instances) | research-* | Section 0d |
| TESTING | Yes | testing (split by layer: unit, e2e) | test-* | Section 0e |

### Why 6 Modes (Not Fewer)

**Alternative considered**: Collapse to 3 modes (plan, implement, review) as in ADR-0013. Rejected because:
- Research and brainstorm have fundamentally different agent compositions and no increment requirement
- Testing needs the increment (for AC coverage) but uses different agents than implementation
- Collapsing modes would force users to work around the abstraction ("I want to research but the system thinks I want to implement")

**Alternative considered**: Let each mode be a separate skill. Rejected because:
- Team-lead is the recognized entry point for "parallel agent work"
- Users already say "team-lead, research this" or "team-lead, brainstorm approaches"
- Splitting into 6 skills would fragment discoverability
- The code-reviewer extraction (Decision 2) is the exception that proves the rule: review needs its own sophisticated orchestration logic (6 reviewer types, routing, deduplication)

### Backward Compatibility

Implementation mode (the default) is unchanged. If no keywords match and no prefix is used, team-lead behaves identically to its pre-increment behavior. The mode detection inserts a decision point *before* the existing flow, never altering it.

### Relationship to ADR-0013 (Phase Detection)

ADR-0013 describes a runtime TypeScript PhaseDetector with weighted scoring for model selection (Sonnet vs Haiku). This increment operates at a different level: it is prompt-level mode routing within a skill's SKILL.md, not runtime code. The two systems are complementary:
- ADR-0013's PhaseDetector selects the model after mode is determined
- This increment's mode detection selects the orchestration pattern before agents are spawned

---

## Decision 2: Code-Reviewer as Standalone Skill

### Problem

Code review capabilities were embedded inside team-lead's review mode as a simple delegation. But code review needs its own orchestration logic: scope detection (PR vs changes vs increment vs project), smart reviewer routing (not all 6 reviewers for every review), deduplication of cross-reviewer findings, structured report generation, and cross-repo umbrella support. This complexity doesn't belong inline in team-lead's SKILL.md.

### Decision

Create a standalone `/sw:code-reviewer` skill at `plugins/specweave/skills/code-reviewer/` with its own SKILL.md, agents directory, and orchestration logic. Team-lead's review mode (Section 0c) delegates to this skill via `Skill({ skill: "sw:code-reviewer" })`.

### Reviewer Composition

The 6 reviewers split across two directories:

**From team-lead/agents/ (shared, pre-existing)**:
- `reviewer-logic.md` -- bugs, edge cases, error handling
- `reviewer-security.md` -- OWASP, auth, secrets, injection
- `reviewer-performance.md` -- N+1, memory, blocking ops

**From code-reviewer/agents/ (new, owned by code-reviewer)**:
- `reviewer-silent-failures.md` -- empty catches, swallowed errors, missing .catch()
- `reviewer-types.md` -- type quality, invariants, unsafe assertions
- `reviewer-spec-compliance.md` -- AC verification, scope creep detection

### Why Split Ownership

The first three reviewers (logic, security, performance) pre-exist in team-lead and are also used during implementation-mode grill checks. Duplicating them would violate DRY. The code-reviewer reads them from team-lead's agents/ directory at spawn time.

The last three reviewers (silent failures, types, spec compliance) are review-specific. They have no implementation-mode use case. They live in code-reviewer's own agents/ directory.

### Smart Routing

Not all 6 reviewers fire on every review. The SKILL.md defines routing rules:

```
ALWAYS:           reviewer-logic, reviewer-security
IF *.ts/*.tsx:    reviewer-types
IF *.ts/*.js:     reviewer-silent-failures
IF db/api files:  reviewer-performance
IF increment:     reviewer-spec-compliance
```

This prevents unnecessary agent spawns for small reviews (e.g., a markdown-only change gets only logic + security).

### Cross-Repo Mode

For umbrella projects, the code-reviewer detects `repositories/*/*` directories with uncommitted changes and spawns per-repo reviewer sets. After per-repo reviews complete, a cross-repo integration check catches API contract mismatches, shared type drift, and dependency version conflicts. The merged report has sections per repo plus a cross-repo issues section.

### PLUGIN.md Registration

The code-reviewer skill was already registered in PLUGIN.md at line 82 during a prior increment. This increment only verifies the entry exists; no PLUGIN.md modification is needed.

---

## Decision 3: Planning Mode Agent Composition (Section 0b)

### Problem

Planning previously required invoking `/sw:pm` then `/sw:architect` sequentially. Users had to manually chain these skills. Team-lead's planning mode should orchestrate both automatically.

### Decision

Planning mode (Section 0b) runs PM and Architect agents with a phased dependency:

```
Phase 1 (sequential):
  PM agent writes spec.md
  Wait for PLAN_READY signal

Phase 2 (parallel):
  Architect agent writes plan.md
  Security reviewer flags design issues
  Both run simultaneously
```

### Why Not Fully Parallel

The Architect needs the spec.md (user stories, ACs, constraints) to produce a meaningful plan.md. Running PM and Architect in parallel would force the Architect to guess at requirements. The phased model ensures the Architect has real input.

**Alternative considered**: Fully parallel PM + Architect. Rejected because:
- Architect without spec produces speculative plans that need rework
- PM's spec.md contains acceptance criteria that constrain architectural decisions
- The phased model adds a few minutes of latency but eliminates a rework cycle

**Alternative considered**: Sequential PM then Architect (no parallelism). Rejected because:
- Security review is independent of architecture and can run alongside
- Even with just two parallel agents in Phase 2, we save wall-clock time vs pure sequential

### Placeholder Protocol

Agent templates use bracketed placeholders that the orchestrator replaces before spawning:
- `[INCREMENT_ID]` -- the 4-digit increment number
- `[MASTER_INCREMENT_PATH]` -- path to increment directory
- `[FEATURE_DESCRIPTION]` -- the user's natural language request
- `[REVIEW_TARGET]` -- scope description for reviewers
- `[PR_NUMBER]` -- PR number for PR-scoped reviews
- `[INCREMENT_PATH]` -- increment path for spec-compliance reviewer
- `[BRAINSTORM_QUESTION]` -- the brainstorm topic
- `[RESEARCH_TOPIC]`, `[RESEARCH_SCOPE]` -- research parameters

---

## Decision 4: Guard Script Update for New Prefixes

### Problem

The `increment-existence-guard.sh` enforced spec-first for all TeamCreate calls. Non-implementation modes (brainstorm, review, analysis) were already exempted via prefix matching. But `research-*`, `plan-*`, and `test-*` prefixes were not in the guard's allowlist, which would block team creation for these new modes.

### Decision

Add `research-*`, `plan-*`, and `test-*` to the existing pipe-delimited case statement at line 65 of the guard script. Also add these prefixes to the description keywords list and the error message's ALTERNATIVE section.

### Changes

Guard script case statement (line 65):
```bash
# Before:
review-*|brainstorm-*|analysis-*|audit-*|explore-*|ideate-*)

# After:
review-*|brainstorm-*|analysis-*|audit-*|explore-*|ideate-*|research-*|plan-*)
```

Note: `test-*` prefix is handled separately -- testing mode requires an increment (like implementation mode) and should pass through to the spec check. The guard correctly allows `test-*` teams to proceed only when a valid spec.md exists.

### Description keywords additions

Added to the NON_IMPL_KEYWORDS array: `"research"`, `"planning"`.

### Error message update

Added research-* and plan-* to the ALTERNATIVE section in the block message so users see these as available non-implementation prefixes.

---

## Decision 5: Agent Template Conventions

### Problem

Agent templates across team-lead and code-reviewer needed consistent conventions for placeholders, output signaling, and communication protocol. Without conventions, each template would use different patterns, making the orchestrator's job harder.

### Conventions Established

**1. Placeholder format**: Uppercase words in square brackets: `[PLACEHOLDER_NAME]`. The orchestrator replaces these before passing the template content to `Task()`.

**2. Completion signaling**: Each agent type uses a domain-specific completion keyword in its SendMessage to the orchestrator:
- Implementation agents: `COMPLETION:`
- Reviewer agents: `REVIEW_COMPLETE:`
- Research agents: `RESEARCH_COMPLETE:`
- Brainstorm agents: `PERSPECTIVE_COMPLETE:`
- PM agent: `PLAN_READY:` (Phase 1 completion in planning mode)

**3. SendMessage protocol**: All agents communicate via:
```typescript
SendMessage({
  type: "message",
  recipient: "team-lead",  // always target the orchestrator
  content: "SIGNAL: description of results",
  summary: "Brief one-line summary"
})
```

**4. Orchestrator identity**: Both team-lead and code-reviewer SKILL.md files declare an "Orchestrator Identity" section at the top stating they must never use Edit/Bash to do work themselves. This prevents the orchestrator from bypassing its agents.

**5. bypassPermissions mode**: All agent spawns use `mode: "bypassPermissions"` in the Task() call. Reviewers and researchers cannot handle interactive trust-folder permission prompts.

**6. Read-only agents**: Reviewer and researcher agents are explicitly marked as read-only analysts. They use Read and Bash (for git/gh commands) but never Edit or Write. This is stated in the RULES section of each template.

---

## Component Boundaries

### team-lead/SKILL.md Owns

- Mode detection logic (Section 0)
- Brainstorm orchestration (Section 0a)
- Planning orchestration with phased PM/Architect (Section 0b)
- Review delegation to code-reviewer (Section 0c)
- Research orchestration (Section 0d)
- Testing orchestration (Section 0e)
- Implementation orchestration (Sections 1-7, unchanged)
- Pre-flight cleanup of stale teams (Section -1)
- Increment activation for implementation/testing modes

### code-reviewer/SKILL.md Owns

- Scope detection (PR, changes, increment, project, cross-repo)
- Smart reviewer routing based on file types
- Team creation with review-* prefix
- Agent spawning for 6 reviewer types (3 shared from team-lead, 3 own)
- Result aggregation with deduplication and severity ranking
- Report generation (markdown + JSON)
- Cross-repo umbrella detection and per-repo review
- Cleanup and follow-up recommendations

### increment-existence-guard.sh Owns

- Mode detection from team_name prefix and description keywords
- Spec-first enforcement for implementation teams only
- Bypass for non-implementation modes
- Environment variable override (SPECWEAVE_NO_INCREMENT)

---

## Risk Mitigations

| Risk | Mitigation |
|------|------------|
| Mode detection misclassifies intent | Default to implement (backward compatible); --mode flag for override |
| SKILL.md exceeds 1500-line limit | Each mode section is self-contained and terminates with STOP; progressive disclosure keeps modes concise |
| Guard script changes break existing team creation | Only additive changes (new prefixes to existing case statement); existing prefixes untouched |
| Reviewer agent from team-lead/agents/ path changes | Code-reviewer references by relative path from plugin root; if team-lead moves agents, a single path update fixes it |
| Planning mode PM/Architect phase creates bottleneck | Phase 1 (PM only) is fast; Phase 2 runs parallel; total latency is PM time + max(Architect, Security) |

---

## Files Modified

| File | Change Type | User Story |
|------|------------|------------|
| `skills/team-lead/SKILL.md` | Modified (Section 0 redesign) | US-001, US-003 |
| `skills/code-reviewer/SKILL.md` | New file | US-002, US-004 |
| `skills/code-reviewer/agents/reviewer-silent-failures.md` | New file | US-002 |
| `skills/code-reviewer/agents/reviewer-types.md` | New file | US-002 |
| `skills/code-reviewer/agents/reviewer-spec-compliance.md` | New file | US-002 |
| `hooks/v2/guards/increment-existence-guard.sh` | Modified (prefix additions) | US-001 |

All paths relative to `repositories/anton-abyzov/specweave/plugins/specweave/`.

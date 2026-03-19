# Tasks: Phase-Agnostic Team Lead and Standalone Code Reviewer

## US-001: Mode Detection in Team Lead

### T-001: Redesign team-lead SKILL.md Section 0 with 6-mode detection router
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [x] Completed
**Test**: Given team-lead SKILL.md contains a Section 0 mode detection router → When a user invokes team-lead with "plan the checkout feature" → Then SKILL.md routes to Section 0b (plan mode) and spawns PM + Architect agents instead of domain implementation agents

### T-002: Add mode detection for research intent with researcher agent routing
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02
**Status**: [x] Completed
**Test**: Given team-lead SKILL.md Section 0d contains research mode definition → When a user invokes team-lead with "research how auth works in this codebase" → Then SKILL.md detects research mode keyword and spawns 1-3 researcher agents without requiring an increment

### T-003: Add mode detection for test intent with testing agent routing
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03
**Status**: [x] Completed
**Test**: Given team-lead SKILL.md Section 0e contains test mode definition → When a user invokes team-lead with "test the payment flow" → Then SKILL.md detects test mode and spawns testing-focused agents using the test-* team prefix

### T-004: Preserve backward compatibility with default implementation mode
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04
**Status**: [x] Completed
**Test**: Given team-lead SKILL.md mode detection chain exhausts all keyword matches → When a user invokes team-lead without any mode-specific keywords or prefixes → Then SKILL.md falls through to Section 1+ (implementation mode) with identical behavior to pre-increment team-lead

### T-005: Document mode configuration matrix in SKILL.md
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05
**Status**: [x] Completed
**Test**: Given team-lead SKILL.md Section 0 is updated → When a developer reads the mode detection section → Then each mode lists its trigger keywords, required agent templates, team prefix, and whether an increment is required

---

## US-002: Standalone Code Reviewer Skill

### T-006: Create code-reviewer SKILL.md with frontmatter, orchestration logic, and smart reviewer routing
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03, AC-US2-04
**Status**: [x] Completed
**Test**: Given the code-reviewer skill directory exists at plugins/specweave/skills/code-reviewer/ → When SKILL.md is created with valid frontmatter and routing logic → Then it contains description, hooks, usage instructions, and routing rules that conditionally spawn reviewer agents based on file types changed

### T-007: Create reviewer-silent-failures.md agent template
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03
**Status**: [x] Completed
**Test**: Given code-reviewer/agents/reviewer-silent-failures.md is created → When code-reviewer SKILL.md spawns this agent → Then the agent analyzes code for empty catch blocks, swallowed errors, and missing .catch() chains and signals REVIEW_COMPLETE on completion

### T-008: Create reviewer-types.md agent template
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03
**Status**: [x] Completed
**Test**: Given code-reviewer/agents/reviewer-types.md is created → When code-reviewer SKILL.md spawns this agent on *.ts or *.tsx files → Then the agent analyzes type quality, invariants, and unsafe assertions and signals REVIEW_COMPLETE on completion

### T-009: Create reviewer-spec-compliance.md agent template
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03
**Status**: [x] Completed
**Test**: Given code-reviewer/agents/reviewer-spec-compliance.md is created → When code-reviewer SKILL.md spawns this agent when an increment is in scope → Then the agent verifies AC coverage, detects scope creep, and signals REVIEW_COMPLETE on completion

### T-010: Verify PLUGIN.md code-reviewer registration without duplication
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04
**Status**: [x] Completed
**Test**: Given PLUGIN.md already contains a code-reviewer entry at line 82 → When the increment is complete → Then PLUGIN.md still has exactly one code-reviewer entry (no duplicate was added) and the skill is invocable via /sw:code-reviewer

---

## US-003: Planning Mode Agent Composition

### T-011: Implement phased PM + Architect planning orchestration in team-lead Section 0b
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] Completed
**Test**: Given team-lead SKILL.md Section 0b is defined with a two-phase planning model → When team-lead detects plan mode → Then Phase 1 spawns the PM agent (agents/pm.md) to write spec.md, waits for PLAN_READY signal, then Phase 2 spawns Architect agent (agents/architect.md) in parallel with optional security review using the plan-* team prefix

---

## US-004: Cross-Repo Code Review

### T-012: Add umbrella project detection logic to code-reviewer SKILL.md
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-03
**Status**: [x] Completed
**Test**: Given code-reviewer SKILL.md contains umbrella detection logic → When /sw:code-reviewer is invoked in an umbrella project with repositories/*/* directories → Then the skill scans for child repos with uncommitted changes and passes the list of child repo paths to reviewer agent prompts

### T-013: Add cross-repo concern detection to reviewer agent templates
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02
**Status**: [x] Completed
**Test**: Given reviewer agents receive child repo paths in umbrella mode → When a reviewer detects a cross-repo concern such as a frontend call to a backend API endpoint that changed → Then the agent flags it in its REVIEW_COMPLETE output with a cross-repo concern label

---

## Guard and Infrastructure

### T-014: Update increment-existence-guard.sh to allow research-* and plan-* prefixes
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [x] Completed
**Test**: Given increment-existence-guard.sh case statement at line 65 is updated → When TeamCreate is called with team name "research-auth-analysis" or "plan-checkout-feature" → Then the guard bypasses spec-first enforcement and allows the team creation without blocking

### T-015: Verify updated guard preserves enforcement for implementation-mode teams
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04
**Status**: [x] Completed
**Test**: Given increment-existence-guard.sh has research-* and plan-* added to the allowlist → When TeamCreate is called with team name "impl-checkout-feature" without a valid spec.md → Then the guard still blocks the call with the spec-first error message and the new prefixes appear in the ALTERNATIVE section

### T-016: Run specweave refresh-plugins --force and verify all files appear in cache
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-04
**Status**: [x] Completed
**Test**: Given all new skill files are written to plugins/specweave/ → When `specweave refresh-plugins --force` is executed → Then the command completes without error and all new files (code-reviewer/SKILL.md, agent templates, team-lead SKILL.md updates, guard script) appear in the plugin cache

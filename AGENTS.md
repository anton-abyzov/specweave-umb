<!-- SW:META template="agents" version="1.0.443" sections="rules,orchestration,principles,commands,nonclaudetools,syncworkflow,contextloading,structure,agents,skills,taskformat,usformat,workflows,troubleshooting,docs" -->

<!-- SW:SECTION:rules version="1.0.443" -->
## Essential Rules

```
1. NEVER pollute project root with .md files
2. Increment IDs unique (0001-9999)
3. ONLY 4 files in increment root: metadata.json, spec.md, plan.md, tasks.md
4. ALL reports/scripts/logs → increment subfolders (NEVER at root!)
5. metadata.json MUST exist BEFORE spec.md can be created
6. tasks.md + spec.md = SOURCE OF TRUTH (update after every task!)
7. EVERY User Story MUST have **Project**: field
8. For 2-level structures: EVERY US also needs **Board**: field
```

### Increment Folder Structure

```
.specweave/increments/0001-feature/
├── metadata.json                  # REQUIRED - create FIRST
├── spec.md                        # WHAT & WHY
├── plan.md                        # HOW (optional)
├── tasks.md                       # Task checklist
├── reports/                       # ALL other .md files go here!
├── scripts/                       # Helper scripts
└── logs/                          # Execution logs
    └── 2026-01-04/
```
<!-- SW:END:rules -->

<!-- SW:SECTION:orchestration version="1.0.443" -->
## Workflow Orchestration

### 1. Plan Before Code (MANDATORY)

BEFORE implementing ANY task — create an increment FIRST:
1. Create increment: spec.md (WHAT/WHY) + plan.md (HOW) + tasks.md (checklist)
2. Get user approval before implementing
3. If something goes sideways → STOP and re-plan

**No exceptions for "simple" tasks** — "simple", "quick", "basic" still require an increment. The only exception: user explicitly says "don't create an increment."

**Setup/config actions are NOT implementation** — "connect github", "setup sync", "import issues" → use the matching setup command directly, not the increment workflow.

See **Task Format** and **User Story Format** sections for templates.

### 2. Verify Before Done

Never mark a task complete without proving it works:
- Code compiles/builds successfully
- Run tests after every task: `npx vitest run` + `npx playwright test`
- Review code quality before committing — check for duplication, readability issues, and inefficiencies (Claude Code: `/simplify`; other tools: manual review or linter)
- `/sw:grill` writes `grill-report.json` — CLI blocks closure without it
- `/sw:judge-llm` writes `judge-llm-report.json` — WAIVED if consent denied
- Acceptance criteria actually satisfied

### 2b. Auto-Closure (MANDATORY)

When ALL tasks are complete, IMMEDIATELY run `/sw:done` — do NOT stop to ask for user confirmation. Quality gates (grill, judge-llm, PM validation) ARE the review. If gates fail, the increment stays open. User can re-open if they disagree with closure.

### 4. Large-Scale Changes

For codebase-wide migrations or bulk refactors:
- **Claude Code**: Use `/batch` — decomposes work into parallel agents with worktree isolation, each producing its own PR
- **Other tools**: Break work into isolated branches (one per unit), implement each independently, review and merge separately
- Always get approval on the decomposition plan before executing

### 3. Dependencies First

Satisfy dependencies BEFORE dependent operations.

```
Bad:  node script.js → Error → npm run build
Good: npm run build → node script.js → Success
```
<!-- SW:END:orchestration -->

<!-- SW:SECTION:principles version="1.0.443" -->
## Core Principles (Quality)

### Simplicity First
- Write the simplest code that solves the problem
- Avoid over-engineering and premature optimization
- One function = one responsibility
- If you can delete code and tests still pass, delete it
- **Match tooling to complexity** — simple tasks (calculator, todo) need 0 domain plugins and vanilla code. Don't load heavyweight frameworks, design systems, or i18n for trivial features

### No Laziness
- Don't leave TODO comments for "later"
- Don't skip error handling because "it probably won't fail"
- Don't copy-paste without understanding
- Test edge cases, not just happy paths

### Minimal Impact
- Change only what's necessary for the task
- Don't refactor adjacent code unless asked
- Keep PRs focused and reviewable
- Preserve existing patterns unless improving them is the task

### Demand Elegance (Balanced)
- Code should be readable by humans first
- Names should reveal intent
- BUT: Don't over-abstract for hypothetical futures
- Pragmatic > Perfect

### DRY (Don't Repeat Yourself)
- Flag repetitions aggressively — duplicated logic, config, or patterns
- Extract shared code into reusable functions/modules
- If you see the same block twice, refactor before adding a third
- Applies to code, config, tests, and documentation alike

### Plan Review Before Code
- Review the full plan thoroughly before writing any code
- Verify plan covers all ACs and edge cases before implementation
- If the plan has gaps, fix the plan first — don't discover them mid-coding
- Re-read the plan between tasks to stay aligned

### Test Before Ship
- Tests pass at every step — unit after each task, E2E before close, no exceptions
- `/sw:test-aware-planner` generates BDD test plans during design — verify they exist before `/sw:do`
- TDD cycle: `/sw:tdd-red` → `/sw:tdd-green` → `/sw:tdd-refactor`
- E2E with Playwright CLI (`npx playwright test`) is a blocking closure gate
<!-- SW:END:principles -->

<!-- SW:SECTION:commands version="1.0.443" -->
## Commands Reference

| Command | Purpose |
|---------|---------|
| `/sw:increment "name"` | Plan new feature (PM-led) |
| `/sw:do` | Execute tasks from active increment |
| `/sw:done 0001` | Close increment (validates gates) |
| `/sw:progress` | Show task completion status |
| `/sw:validate 0001` | Quality check before closing |
| `/sw:progress-sync` | Sync tasks.md with reality |
| `/sw:sync-docs update` | Sync to living docs |
| `/sw-github:sync 0001` | Sync increment to GitHub issue |
| `/sw-jira:sync 0001` | Sync to Jira |
| `/sw-ado:sync 0001` | Sync to Azure DevOps |
| `/sw:sync-setup` | Connect GitHub/Jira/ADO integration |
| `/sw:import` | Import issues from external tools |
<!-- SW:END:commands -->

<!-- SW:SECTION:nonclaudetools version="1.0.443" -->
## Non-Claude Tools (Cursor, Copilot, etc.)

Claude Code has automatic hooks and orchestration. Other tools must do these manually.

### Capability Comparison

| Capability | Claude Code | Non-Claude Tools |
|------------|-------------|------------------|
| **Plan Mode** | `EnterPlanMode` → `/sw:increment` | Manual: Create spec.md + plan.md + tasks.md |
| **Subagents** | `Task` tool for parallel work | Split into multiple chat sessions |
| **Verification** | PostToolUse hooks auto-validate | Manual: Run tests, check ACs |
| **Code quality** | `/simplify` (3 parallel review agents) | Manual: lint, review for duplication/readability/perf |
| **Batch migration** | `/batch` (worktree-isolated parallel agents) | Manual: one branch per unit, implement separately |
| **Hooks** | Auto-run on events | YOU must mimic (see below) |
| **Task sync** | Automatic AC updates | Manual: Edit tasks.md + spec.md |
| **Skills** | Auto-activate on keywords | Read SKILL.md, follow manually |

### Manual Hook Checklist

**After EVERY task completion:**
1. Update tasks.md: `[ ] pending` → `[x] completed`
2. Update spec.md ACs if satisfied: `[ ] AC` → `[x] AC`
3. Review code quality: check for duplication, readability, performance issues (Claude Code: `/simplify`)
4. Run `/sw:progress-sync`
5. Run `/sw-github:sync <id>` (if GitHub configured)

**After all ACs for a User Story are done:**
- Run `/sw:sync-docs update`

**After increment completion:**
1. `/sw:validate <id>`
2. `/sw:sync-docs update`
3. `/sw-github:close-issue <id>`

**Session start:**
1. `specweave jobs` (check background jobs)
2. `/sw:progress` (check current state)
3. `/sw:do` (continue work)

**Background jobs**: Monitor with `specweave jobs` (clone-repos, import-issues, living-docs-builder, sync-external).
<!-- SW:END:nonclaudetools -->

<!-- SW:SECTION:syncworkflow version="1.0.443" -->
## Sync Workflow

### Source of Truth

| Level | Location | Update Method |
|-------|----------|---------------|
| **Source** | tasks.md + spec.md | Edit directly |
| **Derived** | .specweave/docs/internal/specs/ | `/sw:sync-docs update` |
| **Mirror** | GitHub/Jira/ADO | `/sw-github:sync`, `/sw-jira:sync`, `/sw-ado:sync` |

**Update order**: ALWAYS tasks.md/spec.md FIRST → progress-sync → sync-docs → external tools

### Sync Commands

| Command | When to Run |
|---------|-------------|
| `/sw:progress-sync` | After editing tasks.md |
| `/sw:sync-docs update` | After US complete |
| `/sw-github:sync <id>` | After each task |
| `/sw-github:close-issue <id>` | On increment done |
| `/sw-jira:sync <id>` | After each task |
| `/sw-ado:sync <id>` | After each task |
<!-- SW:END:syncworkflow -->

<!-- SW:SECTION:contextloading version="1.0.443" -->
## Context Loading

### Efficient Context Management

```
Read only what's needed for the current task:
- Active increment: spec.md, tasks.md (always)
- Supporting docs: only when referenced in tasks
- Living docs: load per-US when implementing
```

### Token-Efficient Approach

1. Start with increment's `tasks.md` - contains current task list
2. Reference `spec.md` for acceptance criteria
3. Load living docs only when needed for context
4. Avoid loading entire documentation trees
<!-- SW:END:contextloading -->

<!-- SW:SECTION:structure version="1.0.443" -->
## Project Structure

```
.specweave/
├── increments/           # Feature increments (0001-9999)
│   └── 0001-feature/
│       ├── metadata.json # Increment metadata - REQUIRED
│       ├── spec.md       # WHAT & WHY (user stories, ACs)
│       ├── plan.md       # HOW (architecture, APIs) - optional
│       └── tasks.md      # Task checklist with test plans
├── docs/internal/
│   ├── strategy/         # PRD, business requirements
│   ├── specs/            # Living docs (extracted user stories)
│   │   └── {project}/    # Per-project specs
│   ├── architecture/     # HLD, ADRs, technical design
│   └── delivery/         # CI/CD, deployment guides
└── state/                # Runtime state (active increment, caches)
```

### Multi-Repo Structure

**In umbrella projects with `repositories/` folder, each repo has its own `.specweave/`:**

```
umbrella-project/
├── .specweave/config.json          # Umbrella config ONLY
├── repositories/
│   ├── org/frontend/
│   │   └── .specweave/increments/  # Frontend increments HERE
│   ├── org/backend/
│   │   └── .specweave/increments/  # Backend increments HERE
│   └── org/shared/
│       └── .specweave/increments/  # Shared increments HERE
```

**Rules**: Each repo manages its own increments. Never create agent increments in the umbrella root.
<!-- SW:END:structure -->

<!-- SW:SECTION:agents version="1.0.443" -->
## Agents (Roles)

{AGENTS_SECTION}

**Usage**: Adopt role perspective when working on related tasks.
<!-- SW:END:agents -->

<!-- SW:SECTION:skills version="1.0.443" -->
## Skills (Capabilities)

{SKILLS_SECTION}

**Claude Code**: Skills auto-activate based on keywords in your prompt.

**Non-Claude Tools**: Skills don't auto-activate. Manually load them:
1. Find: `ls plugins/specweave*/skills/`
2. Read: `cat plugins/specweave/skills/<name>/SKILL.md`
3. Follow the workflow instructions inside
4. Run `specweave context projects` BEFORE creating any increment
<!-- SW:END:skills -->

<!-- SW:SECTION:taskformat version="1.0.443" -->
## Task Format

```markdown
### T-001: Task Title
**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [ ] pending / [x] completed

**Test Plan** (BDD):
- Given [context] → When [action] → Then [result]
```
<!-- SW:END:taskformat -->

<!-- SW:SECTION:usformat version="1.0.443" -->
## User Story Format (CRITICAL for spec.md)

**MANDATORY: Every User Story MUST have `**Project**:` field!**

```markdown
### US-001: Feature Name
**Project**: my-app          # ← MANDATORY! Get from: specweave context projects
**Board**: digital-ops       # ← MANDATORY for 2-level structures ONLY

**As a** user
**I want** [goal]
**So that** [benefit]

**Acceptance Criteria**:
- [ ] **AC-US1-01**: [Criterion 1]
- [ ] **AC-US1-02**: [Criterion 2]
```

**How to get Project/Board values:**
```bash
# Run BEFORE creating any increment:
specweave context projects

# 1-level output (single project):
# {"level":1,"projects":[{"id":"my-app"}]}
# → Use: **Project**: my-app

# 2-level output (multi-project with boards):
# {"level":2,"projects":[...],"boardsByProject":{"corp":[{"id":"digital-ops"}]}}
# → Use: **Project**: corp AND **Board**: digital-ops
```
<!-- SW:END:usformat -->

<!-- SW:SECTION:workflows version="1.0.443" -->
## Workflows

### Creating Increment
1. Run `specweave context projects` → store project IDs
2. `mkdir -p .specweave/increments/XXXX-feature`
3. Create `metadata.json` (MUST be FIRST)
4. Create `spec.md` — every US needs `**Project**:` field (see User Story Format)
5. Create `tasks.md` (task checklist with BDD tests)
6. Optional: `plan.md` for complex features
7. **Verify** tasks.md has `**Test Plan**:` for every task with testable ACs
8. **Verify** E2E scenarios exist for user-facing user stories — re-run `/sw:test-aware-planner` if missing

### Completing Tasks
1. Implement the task
2. Run unit tests: `npx vitest run`
3. Run E2E tests (if task touches UI/API): `npx playwright test`
4. Only mark task `[x]` after tests pass
5. Review code quality before committing (Claude Code: `/simplify`; other tools: lint + manual review)
6. Update tasks.md: `[ ] pending` → `[x] completed`
7. Update spec.md: check off satisfied ACs
8. Sync to external trackers if enabled
9. If 3 consecutive test failures: STOP, re-plan, ask user

### Closing Increment (AUTO — do NOT stop to ask)
1. Full test suite: `npx vitest run`
2. Full E2E: `npx playwright test`
3. `/sw:grill <id>` — writes `grill-report.json` (CLI requires it)
4. `/sw:done <id>` — validates report files + PM 3 gates (tasks, tests, docs) + syncs to GitHub/Jira/ADO

**CRITICAL**: When all tasks are done, IMMEDIATELY chain to closure. Quality gates (grill, judge-llm, PM validation) ARE the review. Never stop to ask "should I close?" — just close it. If a gate fails, the increment stays open. User can re-open if they disagree.
<!-- SW:END:workflows -->

<!-- SW:SECTION:troubleshooting version="1.0.443" -->
## Troubleshooting

| Issue | Fix |
|-------|-----|
| Commands not working (non-Claude) | Read `plugins/specweave/commands/<name>.md`, follow manually |
| GitHub/Jira not updating | `/sw:progress-sync` → `/sw:sync-docs update` → `/sw-github:sync <id>` |
| .md files in project root | `mv *.md .specweave/increments/<current>/reports/` |
| Progress % wrong | Update tasks.md manually or `/sw:progress-sync` |
| Tool crashes on start | Load only active increment's spec.md + tasks.md, not entire docs/ |
| Missing **Project**: field | `specweave context projects`, add `**Project**:` to every US |
| Skills not activating (non-Claude) | Expected — read SKILL.md from `plugins/specweave*/skills/` |
<!-- SW:END:troubleshooting -->

<!-- SW:SECTION:docs version="1.0.443" -->
## Documentation

| Resource | Purpose |
|----------|---------|
| CLAUDE.md | Quick reference (Claude Code) |
| AGENTS.md | This file (all AI tools) |
| verified-skill.com | Official documentation |
| .specweave/docs/ | Project-specific docs |
<!-- SW:END:docs -->

---
<!-- ↓ ORIGINAL ↓ -->

# ./sw-col

**Framework**: SpecWeave - Specification-First Development
**Standard**: [agents.md](https://agents.md/) for universal AI compatibility

---

## Section Index (Use Ctrl+F to Navigate)

| Section | Search For | Purpose |
|---------|------------|---------|
| Rules | `#essential-rules` | Critical rules, file organization |
| Commands | `#commands` | All SpecWeave commands |
| **Hooks** | `#non-claude-tools` | **CRITICAL: Hook behavior to mimic** |
| Sync | `#sync-workflow` | When/how to sync |
| Context | `#context-loading` | Token savings (70%+) |
| Troubleshoot | `#troubleshooting` | Common issues |

---

## Quick Start

**Initial Increment**: `0001-project-setup` (`.specweave/increments/0001-project-setup/`)

1. **Start Fresh**: Delete it, run `/sw:increment "your-feature"`
2. **Customize**: Edit spec.md in the increment folder

---

## Essential Rules {#essential-rules}

```
1. NEVER pollute project root with .md files
2. Increment IDs unique (0001-9999)
3. ONLY 4 files in increment root: metadata.json, spec.md, plan.md, tasks.md
4. All reports/scripts/logs → increment subfolders
5. metadata.json MUST exist BEFORE spec.md can be created
6. tasks.md + spec.md = SOURCE OF TRUTH (update after every task!)
```

**File Organization**:
```
.specweave/increments/0001-feature/
├── metadata.json                  # REQUIRED - create FIRST
├── spec.md, plan.md, tasks.md    # Core increment docs
├── reports/                       # SESSION-*.md, analysis, etc.
├── scripts/                       # Helper scripts
└── logs/                          # Execution logs
```

---

## Commands Reference {#commands}

### Core Commands

| Command | Purpose |
|---------|---------|
| `/sw:increment "name"` | Plan new feature (PM-led) |
| `/sw:do` | Execute tasks from active increment |
| `/sw:done 0001` | Close increment (validates gates) |
| `/sw:progress` | Show task completion status |
| `/sw:validate 0001` | Quality check before closing |
| `/sw:sync-tasks` | Sync tasks.md with reality |
| `/sw:sync-docs update` | Sync to living docs |

### Plugin Commands (when installed)

| Command | Purpose |
|---------|---------|
| `/sw-github:sync 0001` | Sync increment to GitHub issue |
| `/sw-jira:sync 0001` | Sync to Jira |
| `/sw-ado:sync 0001` | Sync to Azure DevOps |

---

## Non-Claude Tools (Cursor, Copilot, etc.) {#non-claude-tools}

**CRITICAL**: Claude Code has automatic hooks. Other tools DO NOT.

### Latest Features (v0.28+)

SpecWeave v0.28+ introduces powerful automation that **works differently** in non-Claude tools:

| Feature | Claude Code | Non-Claude Tools |
|---------|-------------|------------------|
| **Living Docs Builder** | Auto-runs after init | Use `specweave jobs --follow` to monitor |
| **Bidirectional Sync** | Pull sync on session start | Run `/sw:sync-pull` manually |
| **Background Jobs** | Automatic with hooks | Monitor with `specweave jobs` CLI |
| **EDA Hooks** | Auto-detect task completion | Manually update tasks.md + spec.md |

### Background Jobs Workflow (NEW in v0.28)

SpecWeave now runs heavy operations as **background jobs**:

```bash
# Monitor all jobs
specweave jobs

# Follow a specific job
specweave jobs --follow <job-id>

# View job logs
specweave jobs --logs <job-id>

# Pause/resume long-running jobs
specweave jobs --kill <job-id>    # Pauses gracefully
specweave jobs --resume <job-id>  # Resumes from checkpoint
```

**Job Types**:
- `clone-repos` - Clone multiple repositories (ADO/GitHub)
- `import-issues` - Import work items from external tools
- `living-docs-builder` - Generate documentation from codebase (NEW!)
- `sync-external` - Bidirectional sync with external tools

**Job Dependencies**: The `living-docs-builder` waits for `clone-repos` and `import-issues` to complete before starting. This is automatic - just monitor with `specweave jobs`.

### Code-First Approach (MANDATORY for Non-Claude Tools)

> **Engineering insight**: [Anthropic research](https://www.anthropic.com/engineering/code-execution-with-mcp) shows code execution achieves **98% token reduction** vs MCP tool calls.
>
> **For non-Claude tools, this is even MORE important** - MCP support varies, but `npx` works everywhere!

**Rule**: Always prefer direct code execution over MCP:

```bash
# ❌ DON'T: Use Playwright MCP for testing
# ✅ DO: Write Playwright tests and run with npx
npx playwright test

# ❌ DON'T: Use Kafka MCP for messaging
# ✅ DO: Write kafkajs code
import { Kafka } from 'kafkajs';
const kafka = new Kafka({ brokers: ['localhost:9092'] });

# ❌ DON'T: Chain multiple MCP tool calls
# ✅ DO: Write a script that does all the work
npx ts-node scripts/process-data.ts
```

**Why code is better**:
| Aspect | MCP | Code (`npx`) |
|--------|-----|--------------|
| Token cost | High (tool defs + data duplication) | Low (only results) |
| Reusability | Ephemeral | Committed to git |
| CI/CD | Usually can't run | Native execution |
| Debugging | Limited | Full stack traces |
| Works with | Tools with MCP support | ANY tool |

**Pattern for non-Claude tools**:
```
1. AI writes code (test, script, automation)
2. You run: npx <command>
3. AI analyzes output
4. Repeat
```

This gives you the SAME experience as Claude Code with MCP, but deterministic and reusable!

### What's Different

| Feature | Claude Code | Cursor/Copilot |
|---------|-------------|----------------|
| Commands | Slash syntax works | Manual workflow |
| Hooks | Auto-run on events | **YOU must mimic** |
| Task sync | Automatic | Manual |
| GitHub/Jira sync | Automatic | Manual |
| Living docs | Auto-updated | Manual |

### Hook Behavior You Must Mimic

**Claude Code hooks do these automatically. YOU must do them manually:**

#### 1. After EVERY Task Completion
```bash
# Claude hook: PostTaskCompletion
# You must run these commands:

# Step 1: Update tasks.md (source of truth)
# Change: **Status**: [ ] pending → **Status**: [x] completed

# Step 2: Update spec.md ACs (if task satisfies any)
# Change: - [ ] AC-US1-01 → - [x] AC-US1-01

# Step 3: Sync to external tools (if configured)
/sw:sync-tasks
/sw-github:sync <increment-id>   # If GitHub enabled
/sw-jira:sync <increment-id>     # If Jira enabled
```

#### 2. After User Story Completion (all ACs satisfied)
```bash
# Claude hook: PostUserStoryCompletion
# When ALL acceptance criteria for a user story are [x] checked:

# Step 1: Sync to living docs
/sw:sync-docs update

# Step 2: Update GitHub/Jira issue status
/sw-github:sync <increment-id>
```

#### 3. After Increment Completion
```bash
# Claude hook: PostIncrementDone
# When running /sw:done:

# Step 1: Validate all tasks complete
/sw:validate <increment-id>

# Step 2: Sync living docs
/sw:sync-docs update

# Step 3: Close external issues
/sw-github:close-issue <increment-id>
```

#### 4. After Writing to spec.md or tasks.md
```bash
# Claude hook: PostToolUse (Write/Edit to spec/tasks files)
# After any edit to spec.md or tasks.md:

# Sync status line cache
/sw:sync-tasks

# If external tools configured, sync progress
/sw-github:sync <increment-id>
```

#### 5. Bidirectional Sync - PULL from External Tools (NEW in v0.28)
```bash
# Claude hook: SessionStart (runs automatically)
# For non-Claude tools, run manually to catch external changes:

# Pull changes from external tools (status, priority, assignee)
/sw:sync-pull

# This does:
# 1. Query ADO/JIRA/GitHub for items changed since last sync
# 2. Pull status/priority/assignee updates to living docs
# 3. Use timestamp-based conflict resolution (latest wins)
# 4. Log all changes with full audit trail

# When to run:
# - Start of each work session (catch overnight changes)
# - Before starting work on a linked increment
# - After PM updates status in external tool
```

#### 6. After Init on Brownfield Project (NEW in v0.28)
```bash
# SpecWeave automatically launches living-docs-builder job after init
# For non-Claude tools, monitor it manually:

# Check job status
specweave jobs

# Follow the living-docs-builder progress
specweave jobs --follow <job-id>

# The job runs in 6 phases:
# 1. waiting - Waits for clone/import jobs to complete
# 2. discovery - Scans codebase structure (no LLM, fast)
# 3. foundation - Generates overview.md, tech-stack.md (1-2 hours)
# 4. integration - Matches work items to discovered modules
# 5. deep-dive - Analyzes modules one at a time with checkpoints
# 6. suggestions - Generates SUGGESTIONS.md with next steps

# Output locations:
# - .specweave/docs/internal/architecture/overview.md
# - .specweave/docs/internal/architecture/tech-stack.md
# - .specweave/docs/internal/strategy/modules-skeleton.md
# - .specweave/docs/internal/SUGGESTIONS.md
```

### How to Check if External Tools Configured

```bash
# Check increment metadata for external tool config
cat .specweave/increments/<id>/metadata.json

# Look for these fields:
# "github": { "issue": 123 }     → GitHub enabled
# "jira": { "issue": "PROJ-123" } → Jira enabled
# "ado": { "item": 456 }          → Azure DevOps enabled
```

### Manual Command Execution

In non-Claude tools, commands are markdown workflows:

```bash
# Find and read command file
cat plugins/specweave/commands/increment.md
# Follow the workflow steps manually
```

### Quick Reference: After EVERY Task

```
┌─────────────────────────────────────────────────────────────┐
│ AFTER COMPLETING ANY TASK (MANDATORY FOR NON-CLAUDE TOOLS)  │
├─────────────────────────────────────────────────────────────┤
│ 1. Update tasks.md: [ ] → [x]                               │
│ 2. Update spec.md ACs if satisfied: [ ] → [x]               │
│ 3. Run: /sw:sync-tasks                               │
│ 4. Run: /sw-github:sync <id>  (if GitHub configured) │
│ 5. If all ACs for US done: /sw:sync-docs update      │
└─────────────────────────────────────────────────────────────┘
```

### Quick Reference: Session Start Routine (NEW in v0.28)

```
┌─────────────────────────────────────────────────────────────┐
│ START OF EVERY SESSION (FOR NON-CLAUDE TOOLS)               │
├─────────────────────────────────────────────────────────────┤
│ 1. Pull external changes: /sw:sync-pull              │
│ 2. Check job status:      specweave jobs                    │
│ 3. Check progress:        /sw:progress               │
│ 4. Continue work:         /sw:do                     │
└─────────────────────────────────────────────────────────────┘
```

**Without these manual steps, your work won't be tracked!**

---

## Sync Workflow {#sync-workflow}

### Source of Truth Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│ SOURCE OF TRUTH (edit here first!)                          │
│ ├── tasks.md: Task completion status                        │
│ └── spec.md: Acceptance criteria checkboxes                 │
├─────────────────────────────────────────────────────────────┤
│ DERIVED (auto-updated via sync commands)                    │
│ └── .specweave/docs/internal/specs/: Living documentation   │
├─────────────────────────────────────────────────────────────┤
│ MIRROR (synced to external tools)                           │
│ ├── GitHub Issues: Task checklist, AC progress              │
│ ├── Jira Stories: Status, story points, completion          │
│ └── Azure DevOps: Work item state, task list                │
└─────────────────────────────────────────────────────────────┘
```

**Update Order**: ALWAYS tasks.md/spec.md FIRST → sync-tasks → sync-docs → external tools

### Sync Commands Reference

| Command | What It Does | When to Run |
|---------|--------------|-------------|
| `/sw:sync-tasks` | Recalculates progress from tasks.md | After editing tasks.md |
| `/sw:sync-docs update` | Updates living docs from increment | After US complete |
| `/sw-github:sync <id>` | Syncs progress to GitHub issue | After each task |
| `/sw-github:close-issue <id>` | Closes GitHub issue | On increment done |
| `/sw-jira:sync <id>` | Syncs progress to Jira story | After each task |
| `/sw-ado:sync <id>` | Syncs to Azure DevOps work item | After each task |

### Complete Sync Flow (Non-Claude Tools)

```
TASK COMPLETED
     │
     ▼
┌─────────────────────────────┐
│ 1. Edit tasks.md            │
│    [ ] pending → [x] done   │
└─────────────────────────────┘
     │
     ▼
┌─────────────────────────────┐
│ 2. Edit spec.md ACs         │
│    [ ] AC → [x] AC          │
└─────────────────────────────┘
     │
     ▼
┌─────────────────────────────┐
│ 3. /sw:sync-tasks    │
│    Updates progress cache   │
└─────────────────────────────┘
     │
     ▼
┌─────────────────────────────┐
│ 4. /sw-github:sync   │
│    Updates GitHub issue     │
└─────────────────────────────┘
     │
     ▼ (if all ACs for US done)
┌─────────────────────────────┐
│ 5. /sw:sync-docs     │
│    Updates living docs      │
└─────────────────────────────┘
```

### Claude Code Hooks (Automatic)

| Hook | Trigger | What It Does |
|------|---------|--------------|
| `UserPromptSubmit` | Every prompt | WIP limits, discipline checks |
| `PostToolUse` | File write/edit | Detects task completion, syncs |
| `PostTaskCompletion` | Task done | Updates GitHub/Jira progress |
| `PostIncrementDone` | Increment closed | Closes issues, syncs all docs |

**Non-Claude tools**: NO HOOKS EXIST. See "Hook Behavior You Must Mimic" section above.

---

## Context Loading {#context-loading}

### Efficient Context Management

```
Read only what's needed for the current task:
- Active increment: spec.md, tasks.md (always)
- Supporting docs: only when referenced in tasks
- Living docs: load per-US when implementing
```

### Token-Efficient Approach

1. Start with increment's `tasks.md` - contains current task list
2. Reference `spec.md` for acceptance criteria
3. Load living docs only when needed for context
4. Avoid loading entire documentation trees

---

## Project Structure

```
.specweave/
├── increments/           # Feature increments (0001-9999)
│   └── 0001-feature/
│       ├── metadata.json # Increment metadata - REQUIRED
│       ├── spec.md       # WHAT & WHY (user stories, ACs)
│       ├── plan.md       # HOW (architecture, APIs) - optional
│       └── tasks.md      # Task checklist with test plans
├── docs/internal/
│   ├── strategy/         # PRD, business requirements
│   ├── specs/            # Living docs (extracted user stories)
│   │   └── {project}/    # Per-project specs
│   ├── architecture/     # HLD, ADRs, technical design
│   └── delivery/         # CI/CD, deployment guides
└── state/                # Runtime state (active increment, caches)
```

---

## Agents (Roles)



**Usage**: Adopt role perspective when working on related tasks.

---

## Skills (Capabilities)



**Usage for Claude Code**: Skills auto-activate based on keywords in your prompt.

**Usage for Non-Claude Tools (Cursor, Copilot, etc.)**:
Skills don't auto-activate. You must manually load them:

```bash
# Step 1: Find relevant skill
ls plugins/specweave*/skills/

# Step 2: Read the skill file
cat plugins/specweave/skills/increment-planner/SKILL.md

# Step 3: Tell AI to follow the skill's workflow
"Follow the increment-planner skill workflow to create my feature"

# Step 4: AI reads skill content and follows instructions
```

**Skill Simulation Pattern**:
```
Non-Claude AI Tools simulate skills by:
1. Reading SKILL.md files from plugins/ folder
2. Following the workflow instructions inside
3. Using the patterns and templates provided
4. Running `npx` commands instead of MCP tools (code-first!)
```

**Example** - Creating increment with Cursor:
```
User: "Create an increment for user authentication"
AI: [Reads plugins/specweave/skills/increment-planner/SKILL.md]
AI: [Follows PM workflow: research → spec → plan → tasks]
AI: [Creates .specweave/increments/0001-auth/spec.md, plan.md, tasks.md]
```

---

## Task Format

```markdown
### T-001: Task Title
**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [ ] pending / [x] completed

**Test Plan** (BDD):
- Given [context] → When [action] → Then [result]
```

---

## Workflows

### Creating Increment
1. `mkdir -p .specweave/increments/0001-feature`
2. Create `metadata.json` (increment metadata) - **MUST be FIRST**
3. Create `spec.md` (WHAT/WHY, user stories, ACs)
4. Create `tasks.md` (task checklist with tests)
5. Optional: Create `plan.md` (HOW, architecture) for complex features

### Completing Tasks
1. Implement the task
2. Update `tasks.md`: `[ ] pending` → `[x] completed`
3. Update `spec.md`: Check off satisfied ACs
4. Sync to external trackers if enabled

### Closing Increment
1. Run `/sw:done 0001`
2. PM validates 3 gates (tasks, tests, docs)
3. Living docs synced automatically
4. GitHub issue closed (if enabled)

---

## Plugin Commands

| Command | Plugin |
|---------|--------|
| `/sw-github:sync` | GitHub sync |
| `/sw-jira:sync` | Jira sync |
| `/sw-ado:sync` | Azure DevOps |

---

## Troubleshooting {#troubleshooting}

### Commands Not Working

**Non-Claude tools**: Commands are markdown workflows, not slash syntax.

```bash
# Find and read the command file
ls plugins/specweave/commands/
cat plugins/specweave/commands/increment.md
# Follow the workflow steps manually
```

### Sync Issues

**Symptoms**: GitHub/Jira not updating, living docs stale

**Solution** (run after EVERY task in non-Claude tools):
```bash
/sw:sync-tasks                  # Update tasks.md
/sw:sync-docs update            # Sync living docs
/sw-github:sync <increment-id>  # Sync to GitHub
```

### Root Folder Polluted

**Symptoms**: `git status` shows .md files in project root

**Fix**:
```bash
CURRENT=$(ls -t .specweave/increments/ | head -1)
mv *.md .specweave/increments/$CURRENT/reports/
```

### Tasks Out of Sync

**Symptoms**: Progress shows wrong completion %

**Fix**: Update tasks.md manually:
```markdown
**Status**: [ ] pending  →  **Status**: [x] completed
```

Or run: `/sw:sync-tasks`

### Context Explosion / Crashes

**Symptoms**: Tool crashes 10-50s after start

**Causes**: Loading too many files at once

**Fix**:
1. Load only the active increment's spec.md and tasks.md
2. Reference living docs only when needed for specific tasks
3. Never load entire `.specweave/docs/` folder at once

### Skills/Agents Not Activating

**Non-Claude tools**: Skills don't auto-activate. This is EXPECTED.

**Manual activation (Cursor, Copilot, Windsurf, etc.)**:
```bash
# 1. Find skills in plugins folder (NOT .claude/)
ls plugins/specweave*/skills/

# 2. Read the skill file
cat plugins/specweave/skills/e2e-playwright/SKILL.md

# 3. Tell AI to follow it
"Read the e2e-playwright skill and write tests for my login page"

# 4. AI writes code, YOU run it (code-first!)
npx playwright test
```

**Remember**: Non-Claude tools get SAME functionality by:
- Reading skill files manually
- Following the workflows inside
- Running `npx` instead of MCP tools (better anyway!)

---

## Documentation

| Resource | Purpose |
|----------|---------|
| CLAUDE.md | Quick reference (Claude Code) |
| AGENTS.md | This file (non-Claude tools) |
| spec-weave.com | Official documentation |
| .specweave/docs/ | Project-specific docs |

---

**Generated by SpecWeave** - Specification-first AI development
**Compatible with**: Claude Code, Cursor, Copilot, Gemini CLI, ChatGPT, and more
**Last Updated**: 2025-12-15

<!-- SW:META template="claude" version="1.0.442" sections="hook-priority,header,claude-code-concepts,lsp,start,autodetect,metarule,rules,workflow,save-nested-repos,reflect,context,structure,taskformat,secrets,syncing,testing,tdd,api,limits,troubleshooting,lazyloading,principles,linking,mcp,auto,docs,non-claude" -->

<!-- SW:SECTION:hook-priority version="1.0.442" -->
## Hook Instructions Override Everything

`<system-reminder>` hook output = **BLOCKING PRECONDITIONS**.

| Hook Message | Action |
|---|---|
| **"RESTART REQUIRED"** | ALL tools blocked → STOP, wait for restart |
| **"SKILL FIRST"** | Call shown skill FIRST → chain domain skills → implement |

**"SKILL FIRST" is mandatory** — "simple", "quick", "basic" are NOT opt-out phrases. The ONLY exception: user explicitly says "don't create an increment" or similar. Perceived simplicity never overrides hook instructions.

**Setup actions are NOT implementation** — "connect github", "setup sync", "import issues" → route to the matching setup skill (`sw:sync-setup`, `sw:import`, `sw:progress-sync`), NOT `/sw:increment`.
<!-- SW:END:hook-priority -->

<!-- SW:SECTION:header version="1.0.442" -->
**Framework**: SpecWeave | **Truth**: `spec.md` + `tasks.md`
<!-- SW:END:header -->

<!-- SW:SECTION:claude-code-concepts version="1.0.442" -->
## Skills & Plugins

**Invoke**: `/skill-name` | auto-trigger by keywords | `Skill({ skill: "name" })`
**Parallel work**: Append "use subagents" to requests

**Key skills**: `sw:pm`, `sw:architect`, `sw:grill`, `sw:tdd-cycle`, `frontend:*`, `backend:*`, `testing:*`

**Skill chaining** — skills are NOT "one and done":
1. **Planning**: `sw:pm` (specs) → `sw:architect` (design)
2. **Implementation**: Invoke domain skill per tech (React → `frontend:architect`, .NET → `backend:dotnet`, Stripe → `payments:payment-core`, etc.)
3. **Closure**: `sw:grill` runs automatically via `/sw:done`

**Complexity gate** — before chaining domain skills:
1. **Tech stack specified?** → Chain ONLY the matching skill. If unspecified, ASK or default to minimal (vanilla JS/HTML, simple Express)
2. **Complexity triage** → Simple (calculator, todo) = 0 domain plugins. Medium (auth, dashboard) = 1-2. Complex (SaaS) = full chain
3. **Sanity check** → Would a senior engineer use this tool for this task? If obviously not, don't invoke it
4. **Never** load all available plugins for a domain — pick ONE per domain based on the actual tech stack

If auto-activation fails, invoke explicitly: `Skill({ skill: "name" })`
<!-- SW:END:claude-code-concepts -->

<!-- SW:SECTION:lsp version="1.0.442" -->
## LSP (Code Intelligence)

**Native LSP broken in v2.1.0+.** Use: `specweave lsp refs|def|hover src/file.ts SymbolName`
<!-- SW:END:lsp -->

<!-- SW:SECTION:start version="1.0.442" -->
## Getting Started

Your first increment starts at `0001`. Just describe what you want to build:

`/sw:increment "your-feature"`
<!-- SW:END:start -->

<!-- SW:SECTION:autodetect version="1.0.442" -->
## Auto-Detection

SpecWeave auto-detects product descriptions and routes to `/sw:increment`:

**Signals** (5+ = auto-route): Project name | Features list (3+) | Tech stack | Timeline/MVP | Problem statement | Business model

**Opt-out phrases**: "Don't plan yet" | "Quick discussion" | "Let's explore ideas"

**Brainstorm routing**: "Just brainstorm first" | "brainstorm" | "ideate" | "what are our options" → routes to `/sw:brainstorm`

**NOT opt-out phrases**: "simple" | "quick" | "basic" | "small" — these still require `/sw:increment`

**Setup/config requests bypass auto-detection** → route directly to the matching skill (e.g., `sw:sync-setup`, `sw:import`)
<!-- SW:END:autodetect -->

<!-- SW:SECTION:metarule version="1.0.442" -->
## Workflow Orchestration

### 1. Plan Mode Default (MANDATORY)
- **ALWAYS enter plan mode** for ANY non-trivial task (3+ steps or architectural decisions)
- Call `EnterPlanMode` BEFORE writing specs, plans, or task breakdowns
- Do NOT start implementation until the plan is reviewed and approved
- If something goes sideways, **STOP and re-plan** -- do not keep pushing
- Write detailed specs upfront to reduce ambiguity
- `/sw:increment` REQUIRES plan mode -- never skip it

### 2. Subagent Strategy (Context Economy)
- **Protect main context** — the main agent's context window is precious; delegate anything that produces large output
- **Research via subagents** — when the user provides URLs, links, or references external docs, spawn a subagent to fetch and summarize instead of loading raw content into main context
- **Codebase exploration** — use Explore subagents for broad searches; only bring concise findings back to main context
- **One task per subagent** — focused execution produces better results and cleaner summaries
- **Parallel research** — launch multiple subagents concurrently when investigating independent questions
- **Summarize, don't relay** — subagent results should be distilled to actionable insights before acting on them in main context
- Append "use subagents" to requests for safe parallelization
- In team mode, sub-agents submit plans for team lead review before implementing

### 3. Verification Before Done
- Never mark a task complete without proving it works
- Run tests after every task: `npx vitest run` + `npx playwright test`
- Run `/simplify` before committing — catches duplication, readability issues, and inefficiencies via 3 parallel review agents
- `/sw:grill` writes `grill-report.json` — CLI blocks closure without it
- `/sw:judge-llm` writes `judge-llm-report.json` — WAIVED if consent denied
- Ask yourself: **"Would a staff engineer approve this?"**

### 5. Auto-Closure After Implementation (MANDATORY)
- When `/sw:do` completes all tasks, IMMEDIATELY invoke `/sw:done` — do NOT stop to ask for review
- The quality gates inside `/sw:done` (grill, judge-llm, PM validation) ARE the review — no user confirmation needed
- `/sw:done` handles: grill report, judge-llm, PM gates, closure, sync to GitHub/Jira/ADO
- If a gate fails, the increment stays open automatically — no risk of premature closure
- If the user disagrees, they can re-open the increment
- **Anti-pattern**: "All tasks complete. Should I close?" — NEVER ask this. Just close it.

### 4. Think-Before-Act (Dependencies)
**Satisfy dependencies BEFORE dependent operations.**
```
Bad:  node script.js → Error → npm run build
Good: npm run build → node script.js → Success
```
<!-- SW:END:metarule -->

<!-- SW:SECTION:rules version="1.0.442" -->
## Rules

1. **Files** → `.specweave/increments/####-name/` (see Structure section for details)
2. **Update immediately**: `Edit("tasks.md", "[ ] pending", "[x] completed")` + `Edit("spec.md", "[ ] AC-", "[x] AC-")`
3. **Unique IDs**: Check ALL folders (active, archive, abandoned):
   ```bash
   find .specweave/increments -maxdepth 2 -type d -name "[0-9]*" | grep -oE '[0-9]{4}E?' | sort -u | tail -5
   ```
4. **Emergency**: "emergency mode" → 1 edit, 50 lines max, no agents
5. **Initialization guard**: `.specweave/` folders MUST ONLY exist where `specweave init` was run
6. **Plugin refresh**: Use `specweave refresh-plugins` CLI (not `scripts/refresh-marketplace.sh`)
7. **Numbered folder collisions**: Before creating `docs/NN-*` folders, CHECK existing prefixes
8. **Multi-repo**: ALL repos MUST be at `repositories/{org}/{repo-name}/` — NEVER directly under `repositories/`
<!-- SW:END:rules -->

<!-- SW:SECTION:workflow version="1.0.442" -->
## Workflow

`/sw:increment "X"` → `/sw:do` → `/sw:progress` → `/sw:done 0001`

| Cmd | Action |
|-----|--------|
| `/sw:increment` | Plan feature |
| `/sw:do` | Execute tasks |
| `/sw:auto` | Autonomous execution |
| `/sw:auto-status` | Check auto session |
| `/sw:cancel-auto` | EMERGENCY ONLY manual cancel |
| `/sw:validate` | Quality check |
| `/sw:done` | Close |
| `/sw:progress-sync` | Sync progress to all external tools |
| `/sw-github:push` | Push progress to GitHub |
| `/sw:sync-setup` | Connect GitHub/Jira/ADO integration |
| `/sw:import` | Import issues from external tools |

**Natural language**: "Let's build X" → `/sw:increment` | "What's status?" → `/sw:progress` | "We're done" → `/sw:done` | "Ship while sleeping" → `/sw:auto`

**Large-scale changes**: For codebase-wide migrations or bulk refactors, use `/batch` — decomposes work into parallel agents with worktree isolation, each producing its own PR. Example: `/batch migrate from Solid to React`
<!-- SW:END:workflow -->

<!-- SW:SECTION:save-nested-repos version="1.0.442" -->
## Nested Repos

Before git operations, scan: `for d in repositories packages services apps libs workspace; do [ -d "$d" ] && find "$d" -maxdepth 2 -name ".git" -type d; done`
<!-- SW:END:save-nested-repos -->

<!-- SW:SECTION:reflect version="1.0.442" -->
## Skill Memories

SpecWeave learns from corrections. Learnings saved here automatically. Edit or delete as needed.

**Disable**: Set `"reflect": { "enabled": false }` in `.specweave/config.json`
<!-- SW:END:reflect -->

## Skill Memories

<!-- Auto-captured by SpecWeave reflect. Edit or delete as needed. -->

### Team Lead
- **2026-03-03**: Agents in team contexts should NOT run /sw:done or /sw:grill themselves — team-lead handles centralized closure to prevent context overflow and enable parallel work
- **2026-03-03**: Team-lead MUST activate master increment (set metadata.json status to "active") BEFORE spawning agents. `specweave complete` silently exits on "planned" status — agents don't manage lifecycle transitions. Closure must retry on failure (max 2) rather than skip.

<!-- SW:SECTION:context version="1.0.442" -->
## Context

**Before implementing**: Check ADRs at `.specweave/docs/internal/architecture/adr/`

**Load context**: `/sw:docs <topic>` loads relevant living docs into conversation
<!-- SW:END:context -->

<!-- SW:SECTION:structure version="1.0.442" -->
## Structure

```
.specweave/
├── increments/####-name/     # metadata.json, spec.md, plan.md, tasks.md
├── docs/internal/specs/      # Living docs
└── config.json
```

**Increment root**: ONLY `metadata.json`, `spec.md`, `plan.md`, `tasks.md`

**Everything else → subfolders**: `reports/` | `logs/` | `scripts/` | `backups/`
<!-- SW:END:structure -->

<!-- SW:SECTION:taskformat version="1.0.442" -->
## Task Format

```markdown
### T-001: Title
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given [X] → When [Y] → Then [Z]
```
<!-- SW:END:taskformat -->

<!-- SW:SECTION:secrets version="1.0.442" -->
## Secrets

Before CLI tools, check existing config (`grep -q` only — never display values).
<!-- SW:END:secrets -->

<!-- SW:SECTION:syncing version="1.0.442" -->
## External Sync

Primary: `/sw:progress-sync`. Individual: `/sw-github:push`, `/sw-github:close`. Mapping: Feature→Milestone | Story→Issue | Task→Checkbox.
<!-- SW:END:syncing -->

<!-- SW:SECTION:testing version="1.0.442" -->
## Testing Pipeline (MANDATORY)

**Testing is a pipeline step, not an afterthought.**

### During Design (`/sw:increment`)
- `/sw:test-aware-planner` generates tasks.md with BDD test plans (Given/When/Then) for every AC
- Every task MUST have a `**Test Plan**:` block before implementation begins
- E2E test scenarios MUST be specified for user-facing features

### During Implementation (`/sw:do`)
- TDD cycle: `/sw:tdd-red` → `/sw:tdd-green` → `/sw:tdd-refactor`
- Run tests after EVERY task: `npx vitest run` (unit) + `npx playwright test` (E2E when applicable)
- Never mark a task `[x]` until its tests pass

### Before Closing (`/sw:done`)
- `/sw:grill` writes `grill-report.json` — CLI blocks closure without it
- `/sw:judge-llm` writes `judge-llm-report.json` — WAIVED if consent denied
- `/sw:validate` — 130+ rule checks
- E2E: `npx playwright test` (blocking gate)

### Test Stack
- Unit/Integration: Vitest (`.test.ts`), ESM mocking with `vi.hoisted()` + `vi.mock()`
- E2E: Playwright CLI (`npx playwright test`)
- Coverage targets: unit 95%, integration 90%, e2e 100% of AC scenarios
<!-- SW:END:testing -->

<!-- SW:SECTION:tdd version="1.0.442" -->
## TDD

When `testing.defaultTestMode: "TDD"` in config.json: RED→GREEN→REFACTOR. Use `/sw:tdd-cycle`. Enforcement via `testing.tddEnforcement` (strict|warn|off).
<!-- SW:END:tdd -->

<!-- SW:SECTION:api version="1.0.442" -->
<!-- API: Enable `apiDocs` in config.json. Commands: /sw:api-docs -->
<!-- SW:END:api -->

<!-- SW:SECTION:limits version="1.0.442" -->
## Limits

**Max 1500 lines/file** — extract before adding
<!-- SW:END:limits -->

<!-- SW:SECTION:troubleshooting version="1.0.442" -->
## Troubleshooting

| Issue | Fix |
|-------|-----|
| Skills missing | Restart Claude Code |
| Plugins outdated | `specweave refresh-plugins` |
| Out of sync | `/sw:sync-progress` |
| Session stuck | `rm -f .specweave/state/*.lock` + restart |
| npm E401 on update | `npm i -g specweave --registry https://registry.npmjs.org --userconfig /dev/null` |
<!-- SW:END:troubleshooting -->

<!-- SW:SECTION:lazyloading version="1.0.442" -->
## Plugin Auto-Loading

Plugins load automatically. Manual: `vskill install --repo anton-abyzov/vskill --plugin frontend`. Disable: `export SPECWEAVE_DISABLE_AUTO_LOAD=1`
<!-- SW:END:lazyloading -->

<!-- SW:SECTION:principles version="1.0.442" -->
## Principles

1. **Spec-first**: `/sw:increment` before coding — mandatory for ALL implementation requests, no exceptions unless user explicitly opts out
2. **Docs = truth**: Specs guide implementation
3. **Simplicity First**: Minimal code, minimal impact
4. **No Laziness**: Root causes, senior standards
5. **DRY**: Don't Repeat Yourself — flag and eliminate repetitions aggressively
6. **Plan Review**: Review the plan thoroughly before making any code changes
7. **Test before ship**: Tests pass at every step — unit after each task, E2E before close, no exceptions
<!-- SW:END:principles -->

<!-- SW:SECTION:linking version="1.0.442" -->
## Bidirectional Linking

Tasks ↔ User Stories auto-linked via AC-IDs: `AC-US1-01` → `US-001`

Task format: `**AC**: AC-US1-01, AC-US1-02` (CRITICAL for linking)
<!-- SW:END:linking -->

<!-- SW:SECTION:mcp version="1.0.442" -->
## External Services

CLI tools first (`gh`, `wrangler`, `supabase`) → MCP for complex integrations.
<!-- SW:END:mcp -->

<!-- SW:SECTION:auto version="1.0.442" -->
## Auto Mode

`/sw:auto` (start) | `/sw:auto-status` (check) | `/sw:cancel-auto` (emergency)

Pattern: IMPLEMENT → TEST → FAIL? → FIX → PASS → NEXT. STOP & ASK if spec conflicts or ambiguity.
<!-- SW:END:auto -->

<!-- SW:SECTION:docs version="1.0.442" -->
## Docs

[verified-skill.com](https://verified-skill.com)
<!-- SW:END:docs -->

---
<!-- ↓ PROJECT-SPECIFIC (non-duplicate additions) ↓ -->

## Project Structure

- **Umbrella repo**: specweave-umb with repos under `repositories/anton-abyzov/`

## Manual Verification Gates

Ask user to manually verify: new UI flows, auth changes, payment flows, data migrations.

<!-- SW:SECTION:non-claude version="1.0.442" -->
## Using SpecWeave with Other AI Tools

See **AGENTS.md** for Cursor, Copilot, Windsurf, Aider instructions.
<!-- SW:END:non-claude -->

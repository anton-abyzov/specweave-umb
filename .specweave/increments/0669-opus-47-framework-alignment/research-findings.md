# Research Findings — Opus 4.7 Framework Alignment

Consolidated research from the 3-agent research team (blog-analyst, skill-auditor, stale-detector) executed on 2026-04-16. This document is the **input** to the spec.md and plan.md produced by PM and Architect agents.

---

## 1. Opus 4.7 — What Changed (blog-analyst)

### Novel mechanisms in 4.7
1. **Adaptive thinking** — replaces fixed Extended Thinking budgets. Thinking is now optional per-step; fixed `thinking.budget_tokens` is **not supported in 4.7**.
2. **xhigh effort level** — new level between `high` and `max`, described as "best setting for most coding and agentic uses".
3. **Auto mode** (Shift+Tab, Claude Code Max) — native unsupervised execution path.
4. **Effort toggling mid-task** — user can change effort level during a session.
5. **Reduced default verbosity** — 4.7 is less chatty than 4.6 by default.
6. **Reduced default tool-use** — model calls tools less often; requires explicit "when and why" guidance in skills.
7. **Reduced default subagent spawning** — "more judicious about when to delegate… Do not spawn a subagent for work you can complete directly in a single response."
8. **Updated tokenizer** — may affect prompt tuning migrated from 4.6.
9. **`max` effort caution** — "diminishing returns and more prone to overthinking."
10. **Prompt-driven thinking control** — "Think carefully and step-by-step, this problem is harder than it looks" / "Prioritize responding quickly rather than thinking deeply."

### Anti-patterns explicitly warned against
- A1. Spawning subagents for work completable directly in one response
- A2. Routine use of `max` effort
- A3. Fixed Extended Thinking prompting (not supported)
- A4. Tool-use without explicit when/why conditions
- A5. Multi-turn progressive ambiguous prompting (spec-first fixes this)
- A6. Negative instructions for voice/length

### SpecWeave current violations
- **VIOLATED A1**: `sw:team-lead` SKILL.md: "Even if the work seems simple enough to do directly — spawn agents anyway."
- **VIOLATED A3**: `sw:judge-llm` description: "Uses extended thinking and Opus model."
- **PARTIALLY VIOLATES A2**: `sw:grill` uses `model: opus` with no effort cap; `sw:judge-llm` is "ultrathink by default".
- **PARTIALLY VIOLATES A4**: Skills describe *what* tools to call but not *when/why*.

---

## 2. Skill-by-Skill Findings (skill-auditor)

### Top-15 prioritized changes

| # | Skill | Change | Win |
|---|-------|--------|-----|
| 1 | `sw:increment` | Default single-agent planner; gate 3-agent fan-out behind `--parallel` or US count ≥10 | 2× faster planning |
| 2 | `sw:team-lead` | Raise 15-task cap to 40; retire `--simple` mode coupling | Fewer forced splits |
| 3 | All skills | Prompt-cache CLAUDE.md + config.json | ~60% input-token cut |
| 4 | `sw:grill` | Add adaptive-thinking prompt hint (no fixed budget) | Catches more defects |
| 5 | `sw:judge-llm` | Prompt-cache rubric + spec + diff context | ~70% cost cut |
| 6 | `sw:code-reviewer` | Collapse 8 reviewers + 10 validators → 3 reviewers + inline self-critique | 6× fewer agents |
| 7 | TDD trio | Merge `tdd-red`+`tdd-green`+`tdd-refactor` → `tdd-cycle` | 3 skills → 1 |
| 8 | `sw:pm`/`sw:architect` | Retire `skill-chain-XXXX.json` state-marker files | -20 lines per skill |
| 9 | `sw:done` | Prompt-cache increment files read across 5+ steps | ~50% closure cost cut |
| 10 | All skills | Add `quality.thinkingBudget` in config.json | Centralized control |
| 11 | team-lead agent templates | Extract shared protocol to `_protocol.md` | -40% per template |
| 12 | `sw:auto` | Retire `--simple` flag | Higher quality outcomes |
| 13 | `sw:team-merge` | Run closure inline for ≤5 increments | 4× fewer subagent spawns |
| 14 | `sw:grill` | Lower confidence threshold default 70 → 50 | Catch more real issues |
| 15 | `sw:do` | Default-on per-task review for P1 tasks | Earlier drift detection |

### Legacy compromises to retire (14 total)
1. 15-task cap per agent (`team-lead/SKILL.md:624-639`)
2. `--simple` mode (`auto/SKILL.md:47-57`)
3. Mandatory PM+Architect+Planner fan-out (`increment/SKILL.md:270-358`)
4. `sw-closer` subagent during closure (`done/SKILL.md:19`, `team-merge/SKILL.md:81-92`)
5. State-marker files `skill-chain-XXXX.json` (`pm/SKILL.md:18-34`, `architect/SKILL.md:9-24`)
6. Grill confidence threshold ≥70 (`grill/SKILL.md:156-173`)
7. Interview state markers for PreToolUse guard (`pm/SKILL.md:79-96`)
8. Heartbeat stuck-detection thresholds (`team-lead/SKILL.md:928-979`) — keep but raise
9. 3-iteration fix-loop cap on code-review (`done/SKILL.md:58-67`) — raise to 5
10. Independent-finding-validator spawning 10 haiku agents (`code-reviewer/SKILL.md:310-344`)
11. Active-phase forbidden-list (no closure skills loaded) (`team-lead/SKILL.md:863-888`)
12. Separate `sw:tdd-red`/`tdd-green`/`tdd-refactor` skills
13. Task-by-task model switching (haiku/sonnet/opus hints) (`do/SKILL.md:158`)
14. Hardcoded token budgets 400/500/600 (`pm/SKILL.md:163-168`, `brainstorm/SKILL.md:508-524`) — raise 3×

### Cross-cutting opportunities
- **Prompt caching** on CLAUDE.md + config.json + spec.md — universally applicable
- **`quality.thinkingBudget` config knob** — per-skill thinking hints
- **`cache.staticContextFiles` list in config.json** — explicit cache-prefix declaration
- **`/sw:preview` dry-run mode** — for `sw:done`, `sw:increment`, `sw:team-lead`
- **Shared agent protocol file** — `agents/_protocol.md` referenced by all team-lead templates

---

## 3. Stale / Redundant Skills (stale-detector)

### Complete recommendation breakdown
- **DEPRECATE (7)**: `sw:github-sync`, `sw:jira-sync`, `sw:ado-sync`, `sw:tdd-red`, `sw:tdd-green`, `sw:tdd-refactor`, `sw:github-issue-standard` (→ move to docs)
- **MERGE (9 → 3)**: `github-multi-project` + `ado-multi-project` → `sw:multi-project`; 2 resource-validators → keep but simplify; `team-build` presets → fold into `team-lead --preset`
- **SIMPLIFY (11)**: `sw:plan` (regenerate-only), `sw:close-all` (~40 lines), `sw:image`, `sw:validate` (drop Gate 2), `sw:judge-llm` (opt-in flag on grill), validators, `sw:brainstorm`, `sw:do`, `sw:auto`, `sw:help`, `sw:sync-docs`

### Dead code confirmed
- **Orphaned agent templates**: `team-lead/agents/reviewer-logic.md`, `team-lead/agents/reviewer-performance.md` — REVIEW mode in `team-lead/SKILL.md:93` delegates to `sw:code-reviewer`; these two templates are never referenced. Either wire into REVIEW mode or delete.

### Skills covered by Claude Code natives
- Built-in plan mode duplicates some ceremony in `sw:increment`
- Built-in TodoWrite/TaskCreate could replace `skill-chain-*.json` state coordination
- Built-in Agent/Task tool subsumes TDD trio Task()-wrappers
- Native `review` skill is less capable than `sw:code-reviewer` (KEEP) but closer to `sw:pr-review` (EVALUATE)
- `/simplify` (native) already delegated-to in `sw:done` step 3 — good pattern

### Net result
**Skill index shrinks 47 → ~38 core skills** if DEPRECATE + MERGE recommendations execute. No user-facing workflow change.

---

## 4. Scoring & Priority Framework

The PM agent will translate findings into user stories, and the Architect will design an execution plan. Priority tiers are suggested:

**P0 (blockers to ship before Opus 4.7 default-on):**
- Drop fixed "extended thinking" language from `sw:judge-llm` (broken in 4.7)
- Fix `sw:team-lead` "always spawn agents" anti-pattern
- Raise 15-task cap (was 4.5-era context mitigation)

**P1 (high-impact, low-risk wins):**
- Deprecate TDD trio → `tdd-cycle`
- Deprecate 3 `*-sync` guidance stubs
- Delete 2 orphan agent templates
- Prompt caching on CLAUDE.md + config.json

**P2 (quality improvements):**
- Collapse `code-reviewer` fan-out (18 → 3)
- Retire `--simple` mode
- State-marker file cleanup in pm/architect
- Shared agent protocol file

**P3 (consolidation / UX):**
- Merge multi-project skills
- Move `github-issue-standard` to docs
- Simplify `close-all`, `image`, `validate`
- `/sw:preview` dry-run mode

**P4 (requires telemetry / future):**
- Evaluate `sw:remotion` usage
- Evaluate fold `team-build` → `team-lead --preset`
- Evaluate fold `sw:plan` → `sw:increment --regen`

---

## 5. Known Risks (from audit)

- Collapsing 3-agent planning fan-out may surprise users who rely on tmux-visible parallelism. Mitigation: preserve `--parallel` flag.
- Raising task cap to 40 may hide genuinely hung agents. Mitigation: keep heartbeat stuck detection; tune thresholds.
- Retiring `--simple` may slow auto-mode on very large specs (>50K tokens). Mitigation: auto-fall-back when spec large.
- Collapsing code-reviewer agents may miss security edge cases. Mitigation: keep dedicated Opus security reviewer, merge only sonnet-tier.
- Dropping state-marker files requires guard rewrite. Mitigation: rewrite guard first, then remove markers.

---

## 6. Out-of-Scope (deferred)

- The 20 non-priority skills not yet audited (`sw:lsp`, `sw:qa`, `sw:npm`, `sw:release-*`, `sw:ado-*`, `sw:jira-*`, `sw:docs-*`, `sw:umbrella`, `sw:discrepancies`) — expected to show similar patterns; recommend follow-up increment.
- MCP-related changes (blog does not discuss MCP specifics).
- Memory/auto-memory redesign (blog notes improved context-carry but no API changes).

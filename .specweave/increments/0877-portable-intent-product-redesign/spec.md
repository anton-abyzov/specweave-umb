---
status: completed
---
# 0877 — Portable intent, live progress, and focused skills

## Problem
SpecWeave's purpose is to preserve requested outcomes and verified progress when people change agents, models, or tools. The current dashboard cannot read the 2.0 task ledger reliably, while marketing still promotes removed skill counts and orchestration. vskill cleanup can mistake global plugins for stale project installs. Broad skill triggers and unconditional hooks increase friction without demonstrating value.

## Scope
Research both supplied OpenAI articles and current harness/product documentation. Redesign the local dashboard around work intent with optional linked increments, evidence, and execution history. Redesign SpecWeave and Verified Skills entry points with progressive navigation. Audit and reversibly uninstall obsolete personal/project skills. Fix scoped vskill cleanup. Reassess hooks and tracker integrations, implement verified improvements, build, test headlessly, release and install eligible packages, deploy sites, and deliver an evidence-backed report.

## Acceptance Criteria
- [x] AC-01: Research report distinguishes sourced facts from product hypotheses and records business value, rejected alternatives, integrations strategy, and kill criteria.
- [x] AC-02: Dashboard reads current ledger tasks and plain acceptance criteria, refreshes on authoritative file changes, and shows accurate completion/evidence.
- [x] AC-03: Work board supports persistent intent items with optional increment links, clear summaries, state movement by drag/drop and accessible controls, plus honest harness/model/effort execution history.
- [x] AC-04: SpecWeave website presents portable intent and verified progress through a responsive, layered design with useful generated graphics and working navigation.
- [x] AC-05: Verified Skills website presents scoped expertise, provenance, security evidence, and measured usefulness honestly through a responsive, layered design.
- [x] AC-06: vskill cleanup and removal respect scope, preserve unrelated global installations, and include regression coverage.
- [x] AC-07: Personal/project skill inventory, reversible removals, retained expertise, and recovery manifest are documented; unnecessary hooks are removed or made optional without losing supported handoffs.
- [x] AC-08: Relevant builds, tests, lint, coverage and headless E2E pass; failures outside scope are recorded accurately; review findings resolved; release/install/deploy evidence is recorded.

## Approach
User explicitly authorizes autonomous implementation, testing, installation and releases; this authorizes routine plan/design decisions. One worktree per code lane, preserving existing dirty checkouts. Base SpecWeave on published v2.0.3, vskill and platform on fetched main. Shared board state is deterministic local data, not periodic model inference; unknown telemetry remains unknown and observed use is not a causal quality ranking. Existing specs/ledger remain evidence sources; small intents do not require a new increment. Integrations stay opt-in under a dedicated integration surface, with explicit conflict and authority rules rather than blanket removal. Inspect relevant architecture and current implementation before changes. Use frontend-design, product audit, brainstorm, deep-research, Kie.ai, and SpecWeave ledger workflows. Kie visuals decorate explanatory surfaces, never substitute for real dashboard data. Primary audience: developers and small teams who switch coding tools. Enterprise connectors are an optional extension.

## Open questions
Paid demand and calibrated completion predictions require real adoption data; state these as hypotheses, not shipped guarantees.
